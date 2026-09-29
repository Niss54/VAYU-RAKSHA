"""Upstream feed sources.

Each source is a coroutine that downloads one public feed and returns the artifacts to archive. Sources share a
single HTTP client and a semaphore so the whole run stays within a bounded number of concurrent requests.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Literal, overload

import httpx
from defusedxml import ElementTree

from shadowcast_archiver.config import (
    COASTAL_POINTS,
    GDACS_API,
    IBTRACS_ACTIVE_CSV,
    NORTH_INDIAN_BASIN,
    OPEN_METEO_ENSEMBLE,
    SACHET_COASTAL_SLUGS,
    SACHET_NATIONAL_SLUG,
    SACHET_RSS,
    WEATHERNEXT2_MODEL,
    WEATHERNEXT2_VARIABLES,
    Settings,
)

logger = logging.getLogger(__name__)

JSON = "application/json"
XML = "application/xml"
CSV = "text/csv"
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})


@dataclass(frozen=True)
class Artifact:
    """One file to archive.

    Attributes:
        name: Path relative to the source's run folder, e.g. ``"cap/1790410360067012.xml"``.
        body: Raw bytes exactly as served upstream (or a JSON envelope we build around them).
        content_type: MIME type stored with the object.
    """

    name: str
    body: bytes
    content_type: str


@dataclass(frozen=True)
class FetchContext:
    """Shared state for one archiver run.

    Attributes:
        client: HTTP client reused by every source.
        settings: Run configuration (timeouts, retries, horizons).
        run_at: UTC timestamp identifying this run.
        semaphore: Bounds concurrent upstream requests across all sources.
    """

    client: httpx.AsyncClient
    settings: Settings
    run_at: datetime
    semaphore: asyncio.Semaphore


Source = Callable[[FetchContext], Awaitable[list[Artifact]]]


@overload
async def fetch(
    ctx: FetchContext, url: str, *, params: dict[str, Any] | None = None, allow_missing: Literal[False] = False
) -> httpx.Response: ...


@overload
async def fetch(
    ctx: FetchContext, url: str, *, params: dict[str, Any] | None = None, allow_missing: Literal[True]
) -> httpx.Response | None: ...


async def fetch(
    ctx: FetchContext,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    allow_missing: bool = False,
) -> httpx.Response | None:
    """GET a URL with bounded concurrency, the client timeout and exponential-backoff retries.

    Retries on transport errors and on 429/5xx responses; other 4xx responses fail immediately.

    Args:
        ctx: Run context holding the client, settings and semaphore.
        url: Absolute URL to request.
        params: Optional query parameters.
        allow_missing: Return ``None`` instead of raising when the server answers 404.

    Returns:
        httpx.Response | None: The successful response, or ``None`` for an allowed 404.

    Raises:
        httpx.HTTPError: When the final attempt fails or a non-retryable error status is returned.
    """
    attempts = ctx.settings.max_attempts
    for attempt in range(1, attempts + 1):
        try:
            async with ctx.semaphore:
                response = await ctx.client.get(url, params=params)
        except httpx.TransportError:
            if attempt == attempts:
                raise
        else:
            if response.status_code == 404 and allow_missing:
                return None
            if response.status_code not in RETRYABLE_STATUS or attempt == attempts:
                return response.raise_for_status()
        delay = ctx.settings.retry_backoff_s * 2 ** (attempt - 1)
        logger.warning("retrying %s in %.1fs (attempt %d/%d)", url, delay, attempt, attempts)
        await asyncio.sleep(delay)
    raise AssertionError("unreachable: the final attempt always returns or raises")  # pragma: no cover


async def gdacs_cyclones(ctx: FetchContext) -> list[Artifact]:
    """Archive GDACS tropical-cyclone events in the North Indian Ocean: listing, event details and geometry.

    Geometry holds the observed track, forecast points, wind buffers and cone as GeoJSON.

    Args:
        ctx: Run context.

    Returns:
        list[Artifact]: ``events.json`` plus ``{eventid}-{episodeid}/details.json`` and ``geometry.json`` per event.
    """
    since = ctx.run_at - timedelta(days=ctx.settings.gdacs_lookback_days)
    listing = await fetch(
        ctx,
        f"{GDACS_API}/events/geteventlist/SEARCH",
        params={"eventlist": "TC", "fromDate": since.date().isoformat(), "toDate": ctx.run_at.date().isoformat()},
        allow_missing=True,
    )
    lon_min, lat_min, lon_max, lat_max = NORTH_INDIAN_BASIN
    listed: list[dict[str, Any]] = listing.json().get("features", []) if listing else []
    features = [
        feature
        for feature in listed
        if lon_min <= feature["geometry"]["coordinates"][0] <= lon_max
        and lat_min <= feature["geometry"]["coordinates"][1] <= lat_max
    ]
    artifacts = [
        Artifact("events.json", json.dumps({"type": "FeatureCollection", "features": features}).encode(), JSON)
    ]

    async def event_files(properties: dict[str, Any]) -> list[Artifact]:
        event = {"eventtype": "TC", "eventid": properties["eventid"]}
        details, geometry = await asyncio.gather(
            fetch(ctx, f"{GDACS_API}/events/geteventdata", params=event),
            fetch(ctx, f"{GDACS_API}/polygons/getgeometry", params={**event, "episodeid": properties["episodeid"]}),
        )
        folder = f"{properties['eventid']}-{properties['episodeid']}"
        return [
            Artifact(f"{folder}/details.json", details.content, JSON),
            Artifact(f"{folder}/geometry.json", geometry.content, JSON),
        ]

    for files in await asyncio.gather(*(event_files(feature["properties"]) for feature in features)):
        artifacts.extend(files)
    return artifacts


async def sachet_alerts(ctx: FetchContext) -> list[Artifact]:
    """Archive NDMA SACHET CAP 1.2 RSS feeds plus every CAP alert document linked from the coastal feeds.

    CAP documents carry the multilingual (e.g. Odia, Telugu) alert text and the alert area polygon. Missing state
    feeds are logged and skipped so one renamed feed never fails the run.

    Args:
        ctx: Run context.

    Returns:
        list[Artifact]: ``rss/{slug}.xml`` for each available feed and ``cap/{identifier}.xml`` per unique alert.
    """
    slugs = (SACHET_NATIONAL_SLUG, *SACHET_COASTAL_SLUGS)
    feeds = await asyncio.gather(*(fetch(ctx, SACHET_RSS.format(slug=slug), allow_missing=True) for slug in slugs))
    artifacts: list[Artifact] = []
    cap_links: dict[str, str] = {}
    for slug, feed in zip(slugs, feeds, strict=True):
        if feed is None:
            logger.warning("SACHET feed %r not found; skipping", slug)
            continue
        artifacts.append(Artifact(f"rss/{slug}.xml", feed.content, XML))
        if slug == SACHET_NATIONAL_SLUG:
            continue
        for item in ElementTree.fromstring(feed.content).iter("item"):
            identifier, link = (item.findtext("guid") or "").strip(), (item.findtext("link") or "").strip()
            if identifier.isdigit() and link:
                cap_links[identifier] = link
    documents = await asyncio.gather(*(fetch(ctx, link) for link in cap_links.values()))
    artifacts.extend(
        Artifact(f"cap/{identifier}.xml", document.content, XML)
        for identifier, document in zip(cap_links, documents, strict=True)
    )
    return artifacts


async def ibtracs_active(ctx: FetchContext) -> list[Artifact]:
    """Archive IBTrACS' provisional file of currently active storms across all basins.

    Args:
        ctx: Run context.

    Returns:
        list[Artifact]: A single ``ibtracs_active.csv``.
    """
    response = await fetch(ctx, IBTRACS_ACTIVE_CSV)
    return [Artifact("ibtracs_active.csv", response.content, CSV)]


async def weathernext2_ensemble(ctx: FetchContext) -> list[Artifact]:
    """Archive Google WeatherNext 2's 64-member ensemble at coastal district HQs via Open-Meteo.

    Open-Meteo serves only the latest run, so snapshots are the only way to replay as-issued ensembles later.

    Args:
        ctx: Run context.

    Returns:
        list[Artifact]: A single ``weathernext2_ensemble.json`` holding the sampled points and the raw forecasts.
    """
    names, lats, lons = zip(*COASTAL_POINTS, strict=True)
    response = await fetch(
        ctx,
        OPEN_METEO_ENSEMBLE,
        params={
            "latitude": ",".join(map(str, lats)),
            "longitude": ",".join(map(str, lons)),
            "hourly": ",".join(WEATHERNEXT2_VARIABLES),
            "models": WEATHERNEXT2_MODEL,
            "forecast_days": ctx.settings.forecast_days,
            "wind_speed_unit": "kn",
            "timezone": "UTC",
        },
    )
    points = [{"name": name, "lat": lat, "lon": lon} for name, lat, lon in zip(names, lats, lons, strict=True)]
    body = json.dumps({"model": WEATHERNEXT2_MODEL, "points": points, "forecasts": response.json()}).encode()
    return [Artifact("weathernext2_ensemble.json", body, JSON)]


SOURCES: dict[str, Source] = {
    "gdacs": gdacs_cyclones,
    "sachet": sachet_alerts,
    "ibtracs": ibtracs_active,
    "weathernext2": weathernext2_ensemble,
}
