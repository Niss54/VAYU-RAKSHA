"""Parametric storm surge: wind setup over the continental shelf plus the inverse barometer, carried inland.

Each open-coast cell of a bathymetry grid gets a transect running offshore, normal to the coast, out to the shelf
edge. The steady one-dimensional wind-setup equation ``d(eta)/dx = tau / (rho g (h + eta))`` (Dean & Dalrymple 1991) is
integrated shoreward along it, using the onshore stress of the Holland wind field and Garratt's (1977) drag
coefficient, capped for hurricane winds. The inverse-barometer rise comes from the Holland pressure profile, with the
pressure deficit taken from Holland's wind-pressure relation so wind and pressure stay consistent. Inland, the peak
coastal level decays with distance and floods wherever it stays above the ground.

This is a screening model, not a hydrodynamic simulation: no astronomical tide, waves, rivers or alongshore flow.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from shadowcast_geo.config import (
    COAST_NORMAL_CELLS,
    DRAG_MAX,
    EARTH_RADIUS_KM,
    GRAVITY,
    HOLLAND_B,
    INFLOW_DEG,
    KT_PER_MS,
    MIN_WATER_DEPTH_M,
    RHO_AIR,
    RHO_SEA,
    SHELF_DEPTH_M,
    SURGE_DECAY_M_PER_KM,
    SURGE_REACH_KM,
    SURGE_TIME_CHUNK,
    TEN_MINUTE_FACTOR,
    TRANSECT_MAX_KM,
    TRANSECT_STEP_KM,
)
from shadowcast_geo.hazard import Track, geodesics, holland_wind

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class Grid:
    """A regular latitude/longitude raster, north-up.

    Attributes:
        cells: Cell values, shape ``(rows, cols)``; row 0 is the northern edge.
        north: Latitude of the northern edge (degrees).
        west: Longitude of the western edge (degrees).
        cell_deg: Cell size (degrees, both axes).
    """

    cells: FloatArray
    north: float
    west: float
    cell_deg: float

    def sample(self, lat: FloatArray, lon: FloatArray) -> FloatArray:
        """Nearest-cell values at arbitrary points.

        Args:
            lat: Latitudes, any shape.
            lon: Longitudes, same shape.

        Returns:
            FloatArray: Values at the points; NaN outside the grid.
        """
        row = np.floor((self.north - lat) / self.cell_deg)
        col = np.floor((lon - self.west) / self.cell_deg)
        rows, cols = self.cells.shape
        inside = (row >= 0) & (row < rows) & (col >= 0) & (col < cols)
        r, c = np.where(inside, row, 0).astype(int), np.where(inside, col, 0).astype(int)
        return np.where(inside, self.cells[r, c], np.nan)


@dataclass(frozen=True)
class Coast:
    """Open-coast points with their offshore transects.

    Attributes:
        lat: Coast-point latitudes, shape ``(n,)``.
        lon: Coast-point longitudes, shape ``(n,)``.
        seaward_deg: Bearing pointing offshore, normal to the coast (degrees, 0 = north).
        depth_m: Water depth along each transect every ``TRANSECT_STEP_KM`` from the coast outward, shape
            ``(n, steps)``; NaN beyond the shelf edge.
    """

    lat: FloatArray
    lon: FloatArray
    seaward_deg: FloatArray
    depth_m: FloatArray

    def transect_points(self) -> tuple[FloatArray, FloatArray]:
        """Latitude and longitude of every transect sample (great-circle destination points).

        Returns:
            tuple[FloatArray, FloatArray]: Both shaped like ``depth_m``.
        """
        return destination(self.lat, self.lon, self.seaward_deg, self.depth_m.shape[1])


def destination(lat: FloatArray, lon: FloatArray, bearing_deg: FloatArray, steps: int) -> tuple[FloatArray, FloatArray]:
    """Points every ``TRANSECT_STEP_KM`` along a bearing from each start point.

    Args:
        lat: Start latitudes, shape ``(n,)``.
        lon: Start longitudes, shape ``(n,)``.
        bearing_deg: Bearing per start point.
        steps: Number of samples, the first at the start point.

    Returns:
        tuple[FloatArray, FloatArray]: Latitudes and longitudes shaped ``(n, steps)``.
    """
    angular = (np.arange(steps) * TRANSECT_STEP_KM / EARTH_RADIUS_KM)[None, :]
    phi, lam, theta = np.radians(lat)[:, None], np.radians(lon)[:, None], np.radians(bearing_deg)[:, None]
    phi2 = np.arcsin(np.sin(phi) * np.cos(angular) + np.cos(phi) * np.sin(angular) * np.cos(theta))
    lam2 = lam + np.arctan2(np.sin(theta) * np.sin(angular) * np.cos(phi), np.cos(angular) - np.sin(phi) * np.sin(phi2))
    return np.degrees(phi2), np.degrees(lam2)


def coast_from_grid(relief: Grid, bbox: tuple[float, float, float, float]) -> Coast:
    """Find the open coast in a relief grid and cut an offshore transect from every coast cell.

    A coast cell is a sea cell (relief below 0) touching land. Its offshore direction is the gradient of the smoothed
    sea mask. Only transects that reach the shelf edge (``SHELF_DEPTH_M``) before meeting land are kept, so lagoons,
    estuaries and gaps between islands do not count as open coast.

    Args:
        relief: Elevation grid in metres, negative below sea level, covering the region plus a seaward margin.
        bbox: ``(south, west, north, east)`` of the region; coast cells outside it are ignored.

    Returns:
        Coast: The open-coast points and their depth profiles.
    """
    sea = relief.cells < 0
    land = np.pad(~sea, 1, constant_values=False)
    touches_land = land[:-2, 1:-1] | land[2:, 1:-1] | land[1:-1, :-2] | land[1:-1, 2:]
    rows, cols = np.nonzero(sea & touches_land)
    lat = (relief.north - (rows + 0.5) * relief.cell_deg).astype(np.float64)
    lon = (relief.west + (cols + 0.5) * relief.cell_deg).astype(np.float64)
    south, west, north, east = bbox
    inside = (lat >= south) & (lat <= north) & (lon >= west) & (lon <= east)
    rows, cols, lat, lon = rows[inside], cols[inside], lat[inside], lon[inside]

    # Box-mean of the sea mask (summed-area table), then its gradient: rows run south, columns east.
    k = COAST_NORMAL_CELLS
    table = np.pad(np.pad(sea.astype(float), k // 2, mode="edge").cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    smooth = (table[k:, k:] - table[:-k, k:] - table[k:, :-k] + table[:-k, :-k]) / (k * k)
    d_row, d_col = (np.asarray(g, dtype=np.float64) for g in np.gradient(smooth))
    seaward = np.degrees(np.arctan2(d_col[rows, cols], -d_row[rows, cols])) % 360.0

    steps = int(TRANSECT_MAX_KM / TRANSECT_STEP_KM) + 1
    t_lat, t_lon = destination(lat, lon, seaward, steps)
    depth = -relief.sample(t_lat, t_lon)
    stop = ~((depth > 0) & (depth < SHELF_DEPTH_M))  # land, shelf edge or off the grid (NaN compares False)
    first = stop.argmax(axis=1)
    keep = stop.any(axis=1) & (np.nan_to_num(depth[np.arange(first.size), first], nan=-1.0) >= SHELF_DEPTH_M)
    depth = np.where(np.arange(steps)[None, :] >= first[:, None], np.nan, depth)[keep]
    return Coast(lat=lat[keep], lon=lon[keep], seaward_deg=seaward[keep], depth_m=depth)


def wind_setup(depth_m: FloatArray, stress_pa: FloatArray) -> FloatArray:
    """Integrate the steady 1D wind-setup equation shoreward along each transect.

    Args:
        depth_m: Still-water depth per transect sample, shape ``(n, steps)``, from the coast outward; NaN beyond the
            shelf edge, where the level is held at zero.
        stress_pa: Onshore wind stress per sample and time, shape ``(n, steps, times)``; negative when offshore.

    Returns:
        FloatArray: Setup at the coast in metres, shape ``(n, times)`` (negative for setdown).
    """
    eta = np.zeros((depth_m.shape[0], stress_pa.shape[2]))
    step_m = TRANSECT_STEP_KM * 1000.0
    for i in range(depth_m.shape[1] - 1, -1, -1):
        h = depth_m[:, i, None]
        total = np.maximum(h + eta, MIN_WATER_DEPTH_M)
        eta = np.where(np.isfinite(h), eta + step_m * stress_pa[:, i, :] / (RHO_SEA * GRAVITY * total), eta)
    return eta


def coastal_surge(coast: Coast, track: Track) -> dict[str, NDArray[Any]]:
    """Peak storm-surge level at every coast point over the storm's life.

    Args:
        coast: Open-coast points and transects.
        track: The storm track (densified internally, as for the wind hazard).

    Returns:
        dict[str, NDArray[Any]]: ``peak_m`` (wind setup plus inverse barometer, metres above still water),
        ``setup_m`` and ``barometer_m`` at that moment, and ``peak_time``; NaT/NaN when the storm never comes within
        ``SURGE_REACH_KM``.
    """
    dense = track.densify()
    n, steps = coast.depth_m.shape
    t_lat, t_lon = coast.transect_points()
    distance_to_coast, _ = geodesics(coast.lat, coast.lon, dense.lat, dense.lon)
    active = np.flatnonzero((distance_to_coast.min(axis=0) <= SURGE_REACH_KM) & np.isfinite(dense.vmax_kt))
    vmax_ms = dense.vmax_kt / KT_PER_MS
    deficit_pa = RHO_AIR * np.e * vmax_ms**2 / HOLLAND_B  # Holland (1980): Vmax^2 = B * dp / (rho * e)
    landward = np.radians(coast.seaward_deg + 180.0)[:, None, None]

    peak = np.full(n, -np.inf)
    setup_at_peak, barometer_at_peak = np.full(n, np.nan), np.full(n, np.nan)
    peak_time = np.full(n, np.datetime64("NaT", "s"), dtype="datetime64[s]")
    for start in range(0, active.size, SURGE_TIME_CHUNK):
        fixes = active[start : start + SURGE_TIME_CHUNK]
        distance, bearing = geodesics(t_lat.ravel(), t_lon.ravel(), dense.lat[fixes], dense.lon[fixes])
        speed = np.nan_to_num(holland_wind(distance, dense.vmax_kt[fixes], dense.rmw_km[fixes])) / KT_PER_MS
        speed *= TEN_MINUTE_FACTOR
        blow_to = np.radians(bearing - 90.0 - INFLOW_DEG)  # counter-clockwise, spiralling in (northern hemisphere)
        drag = np.minimum((0.75 + 0.067 * speed) * 1e-3, DRAG_MAX)  # Garratt (1977)
        onshore = (RHO_AIR * drag * speed**2).reshape(n, steps, -1) * np.cos(blow_to.reshape(n, steps, -1) - landward)
        setup = wind_setup(coast.depth_m, onshore)
        x = (dense.rmw_km[fixes][None, :] / np.maximum(distance.reshape(n, steps, -1)[:, 0, :], 1.0)) ** HOLLAND_B
        barometer = deficit_pa[fixes][None, :] * (1.0 - np.exp(-x)) / (RHO_SEA * GRAVITY)
        level = setup + barometer
        best = level.argmax(axis=1)
        higher = level[np.arange(n), best] > peak
        peak = np.where(higher, level[np.arange(n), best], peak)
        setup_at_peak = np.where(higher, setup[np.arange(n), best], setup_at_peak)
        barometer_at_peak = np.where(higher, barometer[np.arange(n), best], barometer_at_peak)
        peak_time = np.where(higher, dense.times[fixes][best], peak_time)
    return {
        "peak_m": np.where(np.isfinite(peak), peak, np.nan),
        "setup_m": setup_at_peak,
        "barometer_m": barometer_at_peak,
        "peak_time": peak_time,
    }


def inundation(
    lat: FloatArray,
    lon: FloatArray,
    elevation_m: FloatArray,
    *,
    coast_lat: FloatArray,
    coast_lon: FloatArray,
    peak_m: FloatArray,
) -> dict[str, FloatArray]:
    """Carry each asset's nearest coastal surge inland and compare it with the ground.

    Args:
        lat: Asset latitudes, shape ``(n_assets,)``.
        lon: Asset longitudes.
        elevation_m: Ground elevation per asset (metres above sea level; NaN if unknown).
        coast_lat: Open-coast point latitudes.
        coast_lon: Open-coast point longitudes.
        peak_m: Peak surge per coast point (see :func:`coastal_surge`).

    Returns:
        dict[str, FloatArray]: ``coast_km`` (distance to the nearest open coast), ``surge_m`` (peak surge there) and
        ``flood_m`` (modelled water depth at the asset after decaying ``SURGE_DECAY_M_PER_KM`` inland; 0 when dry, NaN
        without elevation).
    """
    distance, _ = geodesics(lat, lon, coast_lat, coast_lon)
    nearest = distance.argmin(axis=1)
    coast_km = distance[np.arange(lat.size), nearest]
    surge_m = np.nan_to_num(peak_m[nearest])
    level = surge_m - SURGE_DECAY_M_PER_KM * coast_km
    return {"coast_km": coast_km, "surge_m": surge_m, "flood_m": np.maximum(level - elevation_m, 0.0)}
