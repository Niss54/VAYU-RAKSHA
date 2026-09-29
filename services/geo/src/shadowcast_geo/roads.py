"""Arterial roads through the storm: where they are likely cut, when they close, and which sites lose their access.

Every motorway, trunk and primary road from OpenStreetMap is sampled every ``ROAD_SAMPLE_KM``. Each sample carries the
same hazard as the assets: peak wind (and when the 64-kt radius arrives), storm-surge water and storm rain. Following
IMD's damage classes, a road is **cut** where surge floods it or winds reach ``ROAD_CUT_KT`` (extremely severe:
"disruption of rail/road link at several places"), and **at risk** from ``ROAD_RISK_KT`` or under extreme rain on low
ground. Travel on it becomes unsafe when the first of its samples enters the 64-kt radius: the deadline for moving
people along it. Each shelter and hospital is linked to its nearest arterial road, so evacuation and resupply know when
their route goes.

No routing is attempted: a cut arterial road means the site must be reached, or left, before it closes.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from shadowcast_geo.config import (
    ACCESS_RADIUS_KM,
    EARTH_RADIUS_KM,
    EXTREME_RAIN_MM,
    FLOOD_DEPTH_M,
    LOW_LYING_M,
    ROAD_CUT_KT,
    ROAD_RISK_KT,
    ROAD_SAMPLE_KM,
)
from shadowcast_geo.hazard import geodesics

ACCESS_CHUNK = 256  # assets per distance-matrix block, bounding memory


def sample_roads(roads: list[dict[str, Any]]) -> pd.DataFrame:
    """Points every ``ROAD_SAMPLE_KM`` along each road, always including its first and last vertex.

    Args:
        roads: Roads with ``coords`` as ``[[lat, lon], ...]``.

    Returns:
        pd.DataFrame: ``road`` (index into ``roads``), ``lat`` and ``lon`` per sample.
    """
    rows: list[tuple[int, float, float]] = []
    for index, road in enumerate(roads):
        coords = np.asarray(road["coords"], dtype=float)
        lat, lon = coords[:, 0], coords[:, 1]
        step_km = np.hypot(np.diff(lat), np.diff(lon) * np.cos(np.radians(lat[:-1]))) * np.pi * EARTH_RADIUS_KM / 180
        along = np.concatenate([[0.0], np.cumsum(step_km)])
        stations = np.unique(np.append(np.arange(0.0, along[-1], ROAD_SAMPLE_KM), along[-1]))
        rows.extend(
            (index, a, b) for a, b in zip(np.interp(stations, along, lat), np.interp(stations, along, lon), strict=True)
        )
    return pd.DataFrame(rows, columns=["road", "lat", "lon"])


def road_status(roads: list[dict[str, Any]], samples: pd.DataFrame) -> list[dict[str, Any]]:
    """Status of each road from the hazard at its samples.

    Args:
        roads: Roads with ``road_id``, ``name``, ``ref``, ``highway`` and ``coords``.
        samples: One row per sample with ``road``, ``peak_wind_kt``, ``band_kt``, ``band_entry``, ``flood_m``,
            ``rain_mm`` and ``elevation_m``.

    Returns:
        list[dict[str, Any]]: Per road: identity, ``path`` (``[lon, lat]`` pairs), ``length_km``, the worst
        ``peak_wind_kt``, ``flood_m`` and ``rain_mm``, ``status`` (``cut``, ``at risk`` or ``open``), ``causes`` and
        ``closes_at`` (first entry into the 64-kt radius, ``None`` if never).
    """
    road = samples["road"].to_numpy(dtype=int)
    count = len(roads)

    def worst(values: NDArray[np.float64], combine: np.ufunc, fill: float) -> NDArray[np.float64]:
        out = np.full(count, fill)
        combine.at(out, road, values)
        return out

    wind = worst(np.nan_to_num(samples["peak_wind_kt"].to_numpy(dtype=float)), np.fmax, 0.0)
    flood = worst(np.nan_to_num(samples["flood_m"].to_numpy(dtype=float)), np.fmax, 0.0)
    rain = worst(np.nan_to_num(samples["rain_mm"].to_numpy(dtype=float)), np.fmax, 0.0)
    wet_sample = (samples["rain_mm"].to_numpy(dtype=float) >= EXTREME_RAIN_MM) & (
        samples["elevation_m"].to_numpy(dtype=float) < LOW_LYING_M
    )
    wet = worst(wet_sample.astype(float), np.fmax, 0.0) > 0
    entry = pd.to_datetime(samples["band_entry"]).to_numpy(dtype="datetime64[s]").astype(np.int64).astype(float)
    entry[(samples["band_kt"].to_numpy() != 64) | np.isnat(pd.to_datetime(samples["band_entry"]).to_numpy())] = np.inf
    closes = worst(entry, np.fmin, np.inf)
    sampled = np.bincount(road, minlength=count)

    results: list[dict[str, Any]] = []
    for i, source in enumerate(roads):
        flooded, felled = bool(flood[i] >= FLOOD_DEPTH_M), bool(wind[i] >= ROAD_CUT_KT)
        causes = [c for c, hit in (("surge", flooded), ("hurricane winds", felled), ("extreme rain", wet[i])) if hit]
        status = "cut" if flooded or felled else "at risk" if causes or wind[i] >= ROAD_RISK_KT else "open"
        closing = None if not np.isfinite(closes[i]) else np.datetime64(int(closes[i]), "s")
        results.append(
            {
                "road_id": source["road_id"],
                "name": source["name"],
                "ref": source["ref"],
                "highway": source["highway"],
                "path": [[round(lon, 4), round(lat, 4)] for lat, lon in source["coords"]],
                "length_km": round(float(max(sampled[i] - 1, 1) * ROAD_SAMPLE_KM), 1),
                "peak_wind_kt": round(float(wind[i]), 1),
                "flood_m": round(float(flood[i]), 2),
                "rain_mm": round(float(rain[i])),
                "status": status,
                "causes": causes,
                "closes_at": None if closing is None else f"{np.datetime_as_string(closing, unit='s')}Z",
            }
        )
    return results


def nearest_access(
    lat: NDArray[np.float64], lon: NDArray[np.float64], samples: pd.DataFrame, statuses: list[dict[str, Any]]
) -> pd.DataFrame:
    """Each site's nearest arterial road within ``ACCESS_RADIUS_KM`` and when that road closes.

    Args:
        lat: Site latitudes.
        lon: Site longitudes.
        samples: Road samples (``road``, ``lat``, ``lon``).
        statuses: Road statuses from :func:`road_status`, in road order.

    Returns:
        pd.DataFrame: ``road_km`` (NaN beyond the radius), ``access_road`` (name or ref) and ``access_closes`` per
        site, in input order.
    """
    nearest = np.empty(lat.size, dtype=int)
    road_km = np.empty(lat.size)
    for start in range(0, lat.size, ACCESS_CHUNK):
        distance, _ = geodesics(
            lat[start : start + ACCESS_CHUNK],
            lon[start : start + ACCESS_CHUNK],
            samples["lat"].to_numpy(dtype=float),
            samples["lon"].to_numpy(dtype=float),
        )
        nearest[start : start + ACCESS_CHUNK] = distance.argmin(axis=1)
        road_km[start : start + ACCESS_CHUNK] = distance.min(axis=1)
    road_of = samples["road"].to_numpy(dtype=int)[nearest]
    access: list[dict[str, Any] | None] = [
        statuses[int(r)] if km <= ACCESS_RADIUS_KM else None
        for r, km in zip(road_of.tolist(), road_km.tolist(), strict=True)
    ]
    return pd.DataFrame(
        {
            "road_km": np.where(road_km <= ACCESS_RADIUS_KM, road_km, np.nan),
            "access_road": [None if s is None else s["name"] or s["ref"] or "Unnamed road" for s in access],
            "access_closes": pd.to_datetime(
                pd.Series([None if s is None else s["closes_at"] for s in access], dtype=object), utc=True
            ).dt.tz_localize(None),
        }
    )
