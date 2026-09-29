"""Deterministic cyclone hazard: parametric wind field, wind-radius bands and closest approach per asset.

Pure numpy so the same code runs in the offline build and in request handlers. Arrays are shaped
``(n_assets, n_fixes)`` whenever an asset/track-fix pairing is involved.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import numpy as np
from numpy.typing import NDArray

from shadowcast_geo.config import (
    DENSIFY_STEP_MINUTES,
    EARTH_RADIUS_KM,
    GALE_KT,
    HOLLAND_B,
    KT_PER_MS,
    MM_PER_H_PER_IN_PER_DAY,
    NM_TO_KM,
    RCLIPER,
    WIND_BANDS_KT,
)

FloatArray = NDArray[np.float64]
QUADRANTS = ("NE", "SE", "SW", "NW")


@dataclass(frozen=True)
class Track:
    """A storm track: one row per fix, with intensity and quadrant wind radii.

    Attributes:
        times: Fix times as ``datetime64[s]`` (UTC).
        lat: Latitude of the storm centre (degrees).
        lon: Longitude of the storm centre (degrees).
        vmax_kt: Maximum sustained wind (knots).
        rmw_km: Radius of maximum wind (km).
        radii_km: Wind-radius per band (34/50/64 kt) as ``(4, n_fixes)`` arrays in NE, SE, SW, NW order; NaN where
            the band does not exist.
    """

    times: NDArray[np.datetime64]
    lat: FloatArray
    lon: FloatArray
    vmax_kt: FloatArray
    rmw_km: FloatArray
    radii_km: dict[int, FloatArray]

    @classmethod
    def from_records(cls, fixes: list[dict[str, Any]]) -> Track:
        """Build a track from JSON-style fix records (the ``track.json`` artifact format).

        Args:
            fixes: Records with ``time`` (ISO 8601), ``lat``, ``lon``, ``vmax_kt``, ``rmw_km`` and ``r{band}_km`` (a
                4-item list in NE, SE, SW, NW order, items may be null).

        Returns:
            Track: The parsed track.
        """
        return cls(
            times=np.array([np.datetime64(fix["time"].replace("Z", ""), "s") for fix in fixes]),
            lat=np.array([fix["lat"] for fix in fixes], dtype=float),
            lon=np.array([fix["lon"] for fix in fixes], dtype=float),
            vmax_kt=np.array([fix["vmax_kt"] for fix in fixes], dtype=float),
            rmw_km=np.array([fix["rmw_km"] for fix in fixes], dtype=float),
            radii_km={
                band: np.array(
                    [[np.nan if r is None else r for r in fix[f"r{band}_km"]] for fix in fixes], dtype=float
                ).T
                for band in WIND_BANDS_KT
            },
        )

    def densify(self, step_minutes: int = DENSIFY_STEP_MINUTES) -> Track:
        """Interpolate the track linearly to a finer time step.

        Best tracks are 3-hourly while a cyclone moves ~50 km in that time, more than the radius of maximum wind; at
        coarse fixes an asset near the track can sit in the calm eye at one fix and outside the eyewall at the next,
        so the peak wind it experiences is never sampled. Densifying samples the eyewall at every asset.

        Args:
            step_minutes: Output time step.

        Returns:
            Track: A track with fixes every ``step_minutes`` spanning the same period (NaN intervals stay NaN).
        """
        seconds = self.times.astype(np.int64).astype(float)
        grid = np.arange(seconds[0], seconds[-1] + 1.0, step_minutes * 60.0)
        radii_km: dict[int, FloatArray] = {}
        for band, radii in self.radii_km.items():
            quadrants: list[FloatArray] = [np.interp(grid, seconds, radii[q]) for q in range(radii.shape[0])]
            radii_km[band] = np.vstack(quadrants)
        return Track(
            times=grid.astype(np.int64).astype("datetime64[s]"),
            lat=np.interp(grid, seconds, self.lat),
            lon=np.interp(grid, seconds, self.lon),
            vmax_kt=np.interp(grid, seconds, self.vmax_kt),
            rmw_km=np.interp(grid, seconds, self.rmw_km),
            radii_km=radii_km,
        )


def geodesics(
    lat: FloatArray, lon: FloatArray, track_lat: FloatArray, track_lon: FloatArray
) -> tuple[FloatArray, FloatArray]:
    """Great-circle distance and bearing from each track position to each asset.

    Args:
        lat: Asset latitudes, shape ``(n_assets,)``.
        lon: Asset longitudes, shape ``(n_assets,)``.
        track_lat: Storm-centre latitudes, shape ``(n_fixes,)``.
        track_lon: Storm-centre longitudes, shape ``(n_fixes,)``.

    Returns:
        tuple[FloatArray, FloatArray]: Distance in km and bearing from the storm centre in degrees (0 = north),
        both shaped ``(n_assets, n_fixes)``.
    """
    plat, plon = np.radians(lat)[:, None], np.radians(lon)[:, None]
    tlat, tlon = np.radians(track_lat)[None, :], np.radians(track_lon)[None, :]
    dlat, dlon = plat - tlat, plon - tlon
    hav = np.sin(dlat / 2) ** 2 + np.cos(tlat) * np.cos(plat) * np.sin(dlon / 2) ** 2
    distance = 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(hav))
    bearing = np.degrees(
        np.arctan2(
            np.sin(dlon) * np.cos(plat), np.cos(tlat) * np.sin(plat) - np.sin(tlat) * np.cos(plat) * np.cos(dlon)
        )
    )
    return distance, (bearing + 360.0) % 360.0


def holland_wind(distance_km: FloatArray, vmax_kt: FloatArray, rmw_km: FloatArray) -> FloatArray:
    """Holland (1980) gradient-wind profile: ``V = Vmax * sqrt((Rm/r)^B * exp(1 - (Rm/r)^B))``.

    Args:
        distance_km: Distance from the storm centre, shape ``(n_assets, n_fixes)``.
        vmax_kt: Maximum sustained wind per fix, shape ``(n_fixes,)``.
        rmw_km: Radius of maximum wind per fix, shape ``(n_fixes,)``.

    Returns:
        FloatArray: Wind speed in knots, same shape as ``distance_km`` (NaN where intensity or RMW is missing).
    """
    x = (rmw_km[None, :] / np.maximum(distance_km, 1.0)) ** HOLLAND_B
    return vmax_kt[None, :] * np.sqrt(x * np.exp(1.0 - x))


def rcliper_rain(distance_km: FloatArray, vmax_kt: FloatArray) -> FloatArray:
    """R-CLIPER symmetric rain rate: linear from the centre to ``rm``, then exponential decay (Tuleya et al. 2007).

    ``T(r) = T0 + (Tm - T0) r / rm`` inside ``rm`` and ``Tm exp(-(r - rm) / re)`` beyond, where each parameter is
    linear in the normalised intensity ``U = 1 + (Vmax - 35) / 33`` (knots).

    Args:
        distance_km: Distance from the storm centre, shape ``(n_assets, n_fixes)``.
        vmax_kt: Maximum sustained wind per fix, shape ``(n_fixes,)``.

    Returns:
        FloatArray: Rain rate in mm/h, same shape as ``distance_km`` (0 where intensity is missing).
    """
    u = (1.0 + (np.nan_to_num(vmax_kt) - 35.0) / 33.0)[None, :]
    t0, tm, rm, re = (a + b * u for a, b in (RCLIPER[k] for k in ("t0", "tm", "rm", "re")))
    rate = np.where(distance_km < rm, t0 + (tm - t0) * distance_km / rm, tm * np.exp(-(distance_km - rm) / re))
    return np.maximum(rate, 0.0) * MM_PER_H_PER_IN_PER_DAY


def willoughby_rmw_km(vmax_kt: FloatArray, lat: FloatArray) -> FloatArray:
    """Radius of maximum wind estimated from intensity and latitude (Willoughby, Darling & Rahn 2006, eq. 7a).

    ``Rmax = 46.4 * exp(-0.0155 * Vmax + 0.0169 * |lat|)`` with ``Vmax`` in m/s and ``Rmax`` in km. Used for forecast
    tracks (e.g. the ECMWF ensemble) that report position and intensity but not RMW.

    Args:
        vmax_kt: Maximum sustained wind in knots.
        lat: Latitude of the storm centre in degrees.

    Returns:
        FloatArray: Radius of maximum wind in km.
    """
    return 46.4 * np.exp(-0.0155 * vmax_kt / KT_PER_MS + 0.0169 * np.abs(lat))


def exposure(lat: FloatArray, lon: FloatArray, track: Track) -> dict[str, NDArray[Any]]:
    """Peak modelled wind, closest approach and first entry into each wind-radius band for every asset.

    For each fix, the asset's bearing from the storm centre selects the quadrant radius; the asset is inside a band
    when its distance is within that radius.

    Args:
        lat: Asset latitudes, shape ``(n_assets,)``.
        lon: Asset longitudes, shape ``(n_assets,)``.
        track: The storm track.

    Returns:
        dict[str, NDArray[Any]]: ``peak_wind_kt``, ``peak_time``, ``min_dist_km``, ``closest_time``, ``band_kt``
        (strongest band entered, 0 if none), ``band_entry`` (first time inside that band), ``gale_arrival`` (first
        time the modelled wind reaches ``GALE_KT``) and ``rain_mm`` (storm-total R-CLIPER rain); missing times are
        NaT. Times are resolved on the densified track
        (see :meth:`Track.densify`).
    """
    track = track.densify()
    distance, bearing = geodesics(lat, lon, track.lat, track.lon)
    wind = holland_wind(distance, track.vmax_kt, track.rmw_km)
    filled = np.where(np.isnan(wind), -np.inf, wind)
    valid = np.isfinite(filled).any(axis=1)
    peak_index = filled.argmax(axis=1)
    not_a_time = np.datetime64("NaT", "s")
    gale = filled >= GALE_KT
    quadrant = (bearing // 90).astype(int)
    fix_index = np.arange(track.times.size)[None, :]
    band_kt = np.zeros(lat.size, dtype=int)
    band_entry = np.full(lat.size, not_a_time, dtype="datetime64[s]")
    for band in WIND_BANDS_KT:  # weakest first, so stronger bands overwrite
        inside = distance <= track.radii_km[band][quadrant, fix_index]  # NaN radius compares False
        hit = inside.any(axis=1)
        band_kt[hit] = band
        band_entry[hit] = track.times[inside[hit].argmax(axis=1)]
    return {
        "peak_wind_kt": np.where(valid, filled.max(axis=1), np.nan),
        "peak_time": np.where(valid, track.times[peak_index], not_a_time),
        "min_dist_km": distance.min(axis=1),
        "closest_time": track.times[distance.argmin(axis=1)],
        "band_kt": band_kt,
        "band_entry": band_entry,
        "gale_arrival": np.where(gale.any(axis=1), track.times[gale.argmax(axis=1)], not_a_time),
        "rain_mm": rcliper_rain(distance, track.vmax_kt).sum(axis=1) * DENSIFY_STEP_MINUTES / 60.0,
    }


def wind_timeline(lat: float, lon: float, track: Track) -> tuple[NDArray[np.datetime64], FloatArray]:
    """Modelled wind at one asset through the storm's life, on the densified track.

    Args:
        lat: Asset latitude.
        lon: Asset longitude.
        track: The storm track.

    Returns:
        tuple[NDArray[np.datetime64], FloatArray]: Times and wind in knots, both shaped ``(n_dense_fixes,)``.
    """
    dense = track.densify()
    distance, _ = geodesics(np.array([lat]), np.array([lon]), dense.lat, dense.lon)
    return dense.times, holland_wind(distance, dense.vmax_kt, dense.rmw_km)[0]


def track_position(track: Track, when: datetime) -> dict[str, float] | None:
    """Storm centre and intensity at an arbitrary moment, interpolated linearly between fixes.

    Args:
        track: The storm track.
        when: Moment to evaluate (timezone-aware or naive UTC).

    Returns:
        dict[str, float] | None: ``lat``, ``lon``, ``vmax_kt`` and ``rmw_km``, or ``None`` outside the track's span.
    """
    naive_utc = when.astimezone(UTC).replace(tzinfo=None) if when.tzinfo else when
    seconds = track.times.astype(np.int64).astype(float)
    t = float(np.datetime64(naive_utc, "s").astype(np.int64))
    if t < seconds[0] or t > seconds[-1]:
        return None
    values = (track.lat, track.lon, track.vmax_kt, track.rmw_km)
    return {
        key: float(np.interp(t, seconds, v)) for key, v in zip(("lat", "lon", "vmax_kt", "rmw_km"), values, strict=True)
    }


def wind_at(lat: FloatArray, lon: FloatArray, track: Track, when: datetime) -> FloatArray:
    """Modelled wind at every asset at an arbitrary moment.

    Args:
        lat: Asset latitudes, shape ``(n_assets,)``.
        lon: Asset longitudes, shape ``(n_assets,)``.
        track: The storm track.
        when: Moment to evaluate (timezone-aware or naive UTC).

    Returns:
        FloatArray: Wind in knots per asset; zeros when ``when`` is outside the track's time span.
    """
    centre = track_position(track, when)
    if centre is None:
        return np.zeros(lat.size)
    distance, _ = geodesics(lat, lon, np.array([centre["lat"]]), np.array([centre["lon"]]))
    return np.nan_to_num(holland_wind(distance, np.array([centre["vmax_kt"]]), np.array([centre["rmw_km"]]))[:, 0])


def radii_to_km(radii_nm: list[float | None]) -> list[float | None]:
    """Convert a 4-quadrant wind-radius list from nautical miles to km, preserving missing values.

    Args:
        radii_nm: Radii in NE, SE, SW, NW order; ``None`` or NaN where missing.

    Returns:
        list[float | None]: Radii in km rounded to 0.1, with ``None`` for missing quadrants.
    """
    return [None if r is None or np.isnan(r) else round(r * NM_TO_KM, 1) for r in radii_nm]
