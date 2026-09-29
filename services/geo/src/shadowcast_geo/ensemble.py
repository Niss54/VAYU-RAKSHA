"""As-issued ECMWF ensemble cyclone forecasts: download, decode, storm selection and probabilistic impact.

ECMWF publishes a tropical-cyclone track BUFR file per ensemble run (52 members: 50 perturbed, control, high-res).
Each message is one storm; each subset is one member with 6-hourly centre positions, MSLP and maximum 10 m wind.
Running the deterministic hazard per member and aggregating turns a forecast into impact *probabilities* per asset,
with the forecast's own uncertainty folded in, at the lead time forecasters actually had.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import eccodes
import httpx
import numpy as np
from numpy.typing import NDArray

from shadowcast_geo.calibration import OutageModel
from shadowcast_geo.config import (
    ECMWF_OPEN_DATA,
    ECMWF_TRACK_STEPS,
    ENSEMBLE_MATCH_KM,
    EXTREME_RAIN_MM,
    GALE_KT,
    KT_PER_MS,
    Settings,
)
from shadowcast_geo.hazard import Track, exposure, geodesics, willoughby_rmw_km
from shadowcast_geo.inputs import download

FloatArray = NDArray[np.float64]
NO_RADII: list[float | None] = [None, None, None, None]


@dataclass(frozen=True)
class StormForecast:
    """One storm's ensemble forecast from a single ECMWF run.

    Attributes:
        storm_id: ECMWF storm identifier (e.g. ``"70B"`` for an unnamed Bay of Bengal system).
        issued: Forecast base time (UTC).
        members: Member number -> fix records in the ``track.json`` format (radii unknown, RMW estimated).
    """

    storm_id: str
    issued: datetime
    members: dict[int, list[dict[str, Any]]]


def track_file_urls(issued: datetime) -> tuple[str, ...]:
    """Candidate URLs of the ensemble track file for a base time (file naming changed over the years).

    Args:
        issued: Forecast base time (UTC; 00 or 12 for the ensemble).

    Returns:
        tuple[str, ...]: URLs to try in order.
    """
    day, stamp = issued.strftime("%Y%m%d"), issued.strftime("%Y%m%d%H0000")
    return tuple(
        f"{ECMWF_OPEN_DATA}/{day}/{issued:%H}z/ifs/0p25/enfo/{stamp}-{step}h-enfo-tf.bufr" for step in ECMWF_TRACK_STEPS
    )


def load_ensemble(client: httpx.Client, settings: Settings, issued: datetime) -> list[StormForecast]:
    """Download (once, cached) and decode every storm in the ensemble track file for one run.

    Args:
        client: HTTP client.
        settings: Settings (cache, retries).
        issued: Forecast base time (UTC).

    Returns:
        list[StormForecast]: One entry per storm tracked in that run, worldwide.
    """
    cache_name = f"ecmwf_enfo_tf_{issued:%Y%m%d%H}.bufr"
    download(client, settings, cache_name, track_file_urls(issued))
    forecasts: list[StormForecast] = []
    with (settings.cache_dir / cache_name).open("rb") as handle:
        while (message := eccodes.codes_bufr_new_from_file(handle)) is not None:
            try:
                eccodes.codes_set(message, "unpack", 1)
                forecasts.append(_decode_message(message))
            finally:
                eccodes.codes_release(message)
    return forecasts


def _bufr_array(message: Any, key: str) -> FloatArray:
    """Read a BUFR key as a float array (ecCodes returns untyped scalars, lists or arrays).

    Args:
        message: An unpacked ecCodes BUFR handle.
        key: ecCodes key, e.g. ``"#3#latitude"``.

    Returns:
        FloatArray: At least one-dimensional values with missing values replaced by NaN.

    Raises:
        eccodes.CodesInternalError: If the key does not exist in the message.
    """
    raw = np.atleast_1d(np.asarray(cast("Any", eccodes.codes_get_array(message, key)), dtype=float))
    return np.where(raw == eccodes.CODES_MISSING_DOUBLE, np.nan, raw)


def _decode_message(message: Any) -> StormForecast:
    """Decode one storm message into per-member fix records.

    Key layout follows ECMWF's tropical-cyclone BUFR template: the perturbed analysis centre is ``#2#latitude`` with
    wind ``#1#windSpeedAt10M``; forecast period ``i`` has its centre at ``#(2i+2)#latitude`` and wind
    ``#(i+1)#windSpeedAt10M``. Values may be compressed to a single element when equal across members.

    Args:
        message: An unpacked ecCodes BUFR handle.

    Returns:
        StormForecast: The storm's members, keeping only fixes with a valid position and wind.
    """
    members = _bufr_array(message, "ensembleMemberNumber").astype(int)
    base = [int(cast("Any", eccodes.codes_get(message, key))) for key in ("year", "month", "day", "hour")]
    issued = datetime(base[0], base[1], base[2], base[3], tzinfo=UTC)
    hours = [0.0]
    keys: list[tuple[str, str, str]] = [("#2#latitude", "#2#longitude", "#1#windSpeedAt10M")]  # lat, lon, wind
    period = 1
    while True:
        try:
            offset = float(_bufr_array(message, f"#{period}#timePeriod")[0])
        except eccodes.CodesInternalError:
            break
        hours.append(offset)
        keys.append((f"#{2 * period + 2}#latitude", f"#{2 * period + 2}#longitude", f"#{period + 1}#windSpeedAt10M"))
        period += 1

    def stacked(field: int) -> FloatArray:  # (periods, members)
        return np.vstack([np.broadcast_to(_bufr_array(message, key[field]), members.shape) for key in keys])

    lats, lons, vmax = stacked(0), stacked(1), stacked(2) * KT_PER_MS
    rmw = willoughby_rmw_km(vmax, lats)
    tracks: dict[int, list[dict[str, Any]]] = {}
    for column, member in enumerate(members.tolist()):
        fixes = [
            {
                "time": (issued + timedelta(hours=hours[row])).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "lat": round(float(lats[row, column]), 2),
                "lon": round(float(lons[row, column]), 2),
                "vmax_kt": round(float(vmax[row, column]), 1),
                "rmw_km": round(float(rmw[row, column]), 1),
                "r34_km": NO_RADII,
                "r50_km": NO_RADII,
                "r64_km": NO_RADII,
            }
            for row in range(len(hours))
            if np.isfinite([lats[row, column], lons[row, column], vmax[row, column]]).all()
        ]
        if len(fixes) >= 2:
            tracks[int(member)] = fixes
    storm_id = str(cast("Any", eccodes.codes_get(message, "stormIdentifier"))).strip()
    return StormForecast(storm_id, issued, tracks)


def select_storm(forecasts: list[StormForecast], target: tuple[float, float]) -> StormForecast:
    """Pick the storm most ensemble members bring near a target point (e.g. the observed landfall).

    Early in a cyclone's life the ensemble can split genesis between neighbouring vortices, each tracked as its own
    storm, and a single outlier member can pass close to the target. Ranking by member agreement is robust to that:
    the storm with the most members passing within ``ENSEMBLE_MATCH_KM`` wins, ties broken by median distance.

    Args:
        forecasts: Storms decoded from one run.
        target: ``(lat, lon)`` of interest.

    Returns:
        StormForecast: The best-matching storm.

    Raises:
        ValueError: If no storm has any member track.
    """
    candidates = [f for f in forecasts if f.members]
    if not candidates:
        raise ValueError("no storm with member tracks in this ensemble run")

    def agreement(forecast: StormForecast) -> tuple[int, float]:
        closest = [
            float(
                geodesics(
                    np.array([target[0]]),
                    np.array([target[1]]),
                    np.array([f["lat"] for f in fixes], dtype=float),
                    np.array([f["lon"] for f in fixes], dtype=float),
                )[0].min()
            )
            for fixes in forecast.members.values()
        ]
        return sum(d <= ENSEMBLE_MATCH_KM for d in closest), -float(np.median(closest))

    return max(candidates, key=agreement)


def ensemble_impact(
    lat: FloatArray, lon: FloatArray, storm: StormForecast, model: OutageModel
) -> tuple[dict[str, NDArray[Any]], FloatArray]:
    """Run the hazard for every member and aggregate impact probabilities per asset.

    Args:
        lat: Asset latitudes, shape ``(n_assets,)``.
        lon: Asset longitudes, shape ``(n_assets,)``.
        storm: The ensemble forecast.
        model: Calibrated outage model applied to each member's peak wind.

    Returns:
        tuple[dict[str, NDArray[Any]], FloatArray]: Per asset: ``p_outage`` (member mean), ``p34`` and ``p64``
        (share of members reaching gale / hurricane force), ``wind_p10``/``peak_wind_kt``/``wind_p90`` (peak-wind
        percentiles), ``min_dist_km`` (median closest approach), the median ``closest_time``, ``peak_time`` and
        ``gale_arrival`` (over members where defined; NaT otherwise), ``rain_mm`` (member median storm rain) and
        ``p_rain`` (share of members bringing at least ``EXTREME_RAIN_MM``); and every member's peak wind per
        asset, shaped ``(n_members, n_assets)``, for district-level scoring.
    """
    results = [exposure(lat, lon, Track.from_records(fixes)) for fixes in storm.members.values()]
    peak = np.vstack([r["peak_wind_kt"] for r in results])  # (members, assets)
    reached = np.nan_to_num(peak, nan=0.0)  # a member that never reaches an asset contributes calm (0 kt)
    p10, p50, p90 = np.percentile(reached, [10, 50, 90], axis=0)
    rain = np.vstack([r["rain_mm"] for r in results])
    impact = {
        "p_outage": model.predict(peak).mean(axis=0),
        "p34": (reached >= GALE_KT).mean(axis=0),
        "p64": (reached >= 64.0).mean(axis=0),
        "wind_p10": p10,
        "peak_wind_kt": p50,
        "wind_p90": p90,
        "min_dist_km": np.median(np.vstack([r["min_dist_km"] for r in results]), axis=0),
        "closest_time": _median_time(np.vstack([r["closest_time"] for r in results])),
        "peak_time": _median_time(np.vstack([r["peak_time"] for r in results])),
        "gale_arrival": _median_time(np.vstack([r["gale_arrival"] for r in results])),
        "rain_mm": np.median(rain, axis=0),
        "p_rain": (rain >= EXTREME_RAIN_MM).mean(axis=0),
    }
    return impact, peak


def _median_time(times: NDArray[np.datetime64]) -> NDArray[np.datetime64]:
    """Median over axis 0 of a ``datetime64[s]`` array, ignoring NaT (all-NaT columns stay NaT).

    Args:
        times: Array shaped ``(members, assets)``.

    Returns:
        NDArray[np.datetime64]: Median time per asset.
    """
    seconds = np.where(np.isnat(times), np.nan, times.astype("datetime64[s]").astype(np.int64).astype(float))
    has_value = ~np.isnan(seconds).all(axis=0)
    median = np.nanmedian(np.where(has_value, seconds, 0.0), axis=0)
    return np.where(has_value, median.astype(np.int64).astype("datetime64[s]"), np.datetime64("NaT", "s"))
