"""Build-time inputs: storm tracks (IBTrACS), infrastructure (OpenStreetMap) and cyclone shelters (OSDMA).

Downloads are cached under ``settings.cache_dir`` so repeated builds are fast and polite to upstream services.
"""

from __future__ import annotations

import io
import json
import logging
import re
import time
from typing import Any

import httpx
import pandas as pd

from shadowcast_geo.config import (
    IBTRACS_NI_CSV,
    NM_TO_KM,
    OSDMA_SHELTERS_URL,
    OSM_KINDS,
    OVERPASS_URLS,
    ROAD_HIGHWAYS,
    WIND_BANDS_KT,
    Region,
    Settings,
)
from shadowcast_geo.hazard import QUADRANTS, radii_to_km

logger = logging.getLogger(__name__)

RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})
ASSET_COLUMNS = ["asset_id", "kind", "name", "source", "lat", "lon"]
_OSDMA_SHELTERS = re.compile(r"var shelters1\s*=\s*(\[.*?\]);", re.DOTALL)


def download(client: httpx.Client, settings: Settings, cache_name: str, urls: tuple[str, ...], **request: Any) -> bytes:
    """Download a resource once, trying alternative URLs in order with retries, and cache it on disk.

    Transport errors and 429/5xx responses are retried with exponential backoff; a 404 moves straight to the next URL.

    Args:
        client: HTTP client.
        settings: Settings providing the cache directory and retry policy.
        cache_name: File name under the cache directory.
        urls: Candidate URLs (mirrors or alternative names) tried in order.
        **request: Extra ``client.request`` arguments (``method``, ``params``, ``data``); ``method`` defaults to GET.

    Returns:
        bytes: The response body (from cache when present).

    Raises:
        httpx.HTTPError: When every URL fails (the last error is raised).
    """
    cached = settings.cache_dir / cache_name
    if cached.exists():
        return cached.read_bytes()
    method = request.pop("method", "GET")
    error: httpx.HTTPError | None = None
    for url in urls:
        for attempt in range(1, settings.max_attempts + 1):
            try:
                response = client.request(method, url, **request)
                if response.status_code == 404:  # not at this URL: try the next alternative without retrying
                    error = httpx.HTTPStatusError("not found", request=response.request, response=response)
                    break
                if response.status_code not in RETRYABLE_STATUS:
                    body = response.raise_for_status().content
                    cached.parent.mkdir(parents=True, exist_ok=True)
                    cached.write_bytes(body)
                    return body
                error = httpx.HTTPStatusError(
                    f"retryable status {response.status_code}", request=response.request, response=response
                )
            except httpx.TransportError as exc:
                error = exc
            if attempt < settings.max_attempts:
                delay = settings.retry_backoff_s * 2 ** (attempt - 1)
                logger.warning("retrying %s in %.0fs (attempt %d)", url, delay, attempt)
                time.sleep(delay)
        logger.warning("giving up on %s: %s", url, error)
    assert error is not None  # urls is never empty
    raise error


def load_best_track(client: httpx.Client, settings: Settings, storm: str, season: int) -> list[dict[str, Any]]:
    """Load a storm's IBTrACS best track (JTWC intensity, RMW and quadrant wind radii) as JSON-ready fixes.

    Args:
        client: HTTP client.
        settings: Settings (cache, retries).
        storm: IBTrACS storm name, e.g. ``"FANI"``.
        season: Storm season.

    Returns:
        list[dict[str, Any]]: Fixes with ``time`` (ISO 8601 UTC), ``lat``, ``lon``, ``vmax_kt``, ``rmw_km`` and
        ``r34_km``/``r50_km``/``r64_km`` (NE, SE, SW, NW; ``None`` where missing). Fixes without intensity are dropped.

    Raises:
        ValueError: If the storm is not in the archive.
    """
    raw = download(client, settings, "ibtracs_NI.csv", (IBTRACS_NI_CSV,))
    frame = pd.read_csv(io.BytesIO(raw), skiprows=[1], low_memory=False)
    track = frame[(frame["NAME"] == storm) & (frame["SEASON"] == season)].copy()
    if track.empty:
        raise ValueError(f"storm {storm} {season} not found in IBTrACS")
    radius_columns = [f"USA_R{band}_{q}" for band in WIND_BANDS_KT for q in QUADRANTS]
    for column in ["LAT", "LON", "USA_WIND", "USA_RMW", *radius_columns]:
        track[column] = pd.to_numeric(track[column], errors="coerce")
    track = track.dropna(subset=["USA_WIND", "USA_RMW"])
    return [
        {
            "time": pd.Timestamp(row["ISO_TIME"]).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "lat": float(row["LAT"]),
            "lon": float(row["LON"]),
            "vmax_kt": float(row["USA_WIND"]),
            "rmw_km": round(float(row["USA_RMW"]) * NM_TO_KM, 1),
            **{
                f"r{band}_km": radii_to_km([float(row[f"USA_R{band}_{q}"]) for q in QUADRANTS])
                for band in WIND_BANDS_KT
            },
        }
        for row in track.to_dict("records")
    ]


def fetch_osm_assets(client: httpx.Client, settings: Settings, region: Region) -> pd.DataFrame:
    """Critical infrastructure points in a region from OpenStreetMap (Overpass API).

    Args:
        client: HTTP client.
        settings: Settings (cache, retries).
        region: Study area.

    Returns:
        pd.DataFrame: Columns ``asset_id``, ``kind``, ``name``, ``source``, ``lat``, ``lon``.
    """
    bbox = ",".join(map(str, region.bbox))
    selectors = "".join(f'nwr["{key}"="{value}"]({bbox});' for key, value in OSM_KINDS)
    query = f"[out:json][timeout:300];({selectors});out tags center;"
    body = download(client, settings, f"osm_{region.id}.json", OVERPASS_URLS, method="POST", data={"data": query})
    rows: list[dict[str, Any]] = []
    for element in json.loads(body)["elements"]:
        tags: dict[str, str] = element.get("tags", {})
        kind = next((k for (key, value), k in OSM_KINDS.items() if tags.get(key) == value), None)
        point = element.get("center") or element
        if kind and "lat" in point:
            rows.append(
                {
                    "asset_id": f"osm:{element['type']}/{element['id']}",
                    "kind": kind,
                    "name": tags.get("name") or tags.get("name:en"),
                    "source": "OpenStreetMap",
                    "lat": float(point["lat"]),
                    "lon": float(point["lon"]),
                }
            )
    return pd.DataFrame(rows, columns=ASSET_COLUMNS)


def fetch_osm_roads(client: httpx.Client, settings: Settings, region: Region) -> list[dict[str, Any]]:
    """Arterial roads (motorway, trunk and primary) in a region from OpenStreetMap, with their geometry.

    Args:
        client: HTTP client.
        settings: Settings (cache, retries).
        region: Study area.

    Returns:
        list[dict[str, Any]]: ``road_id``, ``name``, ``ref``, ``highway`` and ``coords`` (``[[lat, lon], ...]``) per
        OSM way with at least two vertices.
    """
    bbox = ",".join(map(str, region.bbox))
    classes = "|".join(ROAD_HIGHWAYS)
    query = f'[out:json][timeout:300];way["highway"~"^({classes})$"]({bbox});out tags geom;'
    body = download(client, settings, f"osm_roads_{region.id}.json", OVERPASS_URLS, method="POST", data={"data": query})
    return [
        {
            "road_id": f"osm:way/{way['id']}",
            "name": way.get("tags", {}).get("name") or way.get("tags", {}).get("name:en"),
            "ref": way.get("tags", {}).get("ref"),
            "highway": way.get("tags", {}).get("highway"),
            "coords": [[point["lat"], point["lon"]] for point in way["geometry"]],
        }
        for way in json.loads(body)["elements"]
        if len(way.get("geometry", [])) >= 2
    ]


def fetch_osdma_shelters(client: httpx.Client, settings: Settings, region: Region) -> pd.DataFrame:
    """Official multipurpose cyclone/flood shelters from the OSDMA shelter map, one request per district.

    The OSDMA page embeds its shelter registry as a JavaScript array; entries with coordinates outside the region
    (including 0/0 placeholders) are dropped.

    Args:
        client: HTTP client.
        settings: Settings (cache, retries).
        region: Study area; its ``osdma_districts`` list which districts to fetch.

    Returns:
        pd.DataFrame: Columns ``asset_id``, ``kind``, ``name``, ``source``, ``lat``, ``lon``.
    """
    south, west, north, east = region.bbox
    rows: list[dict[str, Any]] = []
    for district in region.osdma_districts:
        page = download(
            client, settings, f"osdma_{district.lower()}.html", (OSDMA_SHELTERS_URL,), params={"district": district}
        ).decode("utf-8", errors="replace")
        match = _OSDMA_SHELTERS.search(page)
        if not match:
            logger.warning("no shelter registry found for OSDMA district %s", district)
            continue
        for shelter in json.loads(re.sub(r",\s*\]$", "]", match.group(1))):
            lat, lon = float(shelter["lat"] or 0), float(shelter["lon"] or 0)
            if south <= lat <= north and west <= lon <= east:
                rows.append(
                    {
                        "asset_id": f"osdma:{district}:{lat:.5f},{lon:.5f}",
                        "kind": "cyclone_shelter",
                        "name": f"{str(shelter['name']).title()} shelter ({str(shelter['village']).title()})",
                        "source": f"OSDMA ({shelter['shelter']})",
                        "lat": lat,
                        "lon": lon,
                    }
                )
    return pd.DataFrame(rows, columns=ASSET_COLUMNS)


def load_assets(client: httpx.Client, settings: Settings, region: Region) -> pd.DataFrame:
    """All assets in a region: OSDMA shelters (where available) plus OSM infrastructure, de-duplicated by id.

    Args:
        client: HTTP client.
        settings: Settings (cache, retries).
        region: Study area.

    Returns:
        pd.DataFrame: Columns ``asset_id``, ``kind``, ``name``, ``source``, ``lat``, ``lon``.
    """
    frames = [fetch_osdma_shelters(client, settings, region), fetch_osm_assets(client, settings, region)]
    non_empty = [frame for frame in frames if not frame.empty]
    if not non_empty:
        return pd.DataFrame(columns=ASSET_COLUMNS)
    return pd.concat(non_empty, ignore_index=True).drop_duplicates("asset_id").reset_index(drop=True)
