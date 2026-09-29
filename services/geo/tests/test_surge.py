import numpy as np
import pytest

from shadowcast_geo.config import GRAVITY, MIN_WATER_DEPTH_M, RHO_SEA, SHELF_DEPTH_M, TRANSECT_STEP_KM
from shadowcast_geo.hazard import Track
from shadowcast_geo.surge import coast_from_grid, coastal_surge, destination, inundation, wind_setup
from tests.conftest import CELL_DEG, east_facing_coast, make_fixes

BBOX = (18.6, 84.0, 20.4, 88.0)


def test_grid_sample_is_nan_off_the_grid() -> None:
    grid = east_facing_coast()

    assert grid.sample(np.array([20.0]), np.array([85.0]))[0] == 10.0
    assert np.isnan(grid.sample(np.array([25.0]), np.array([85.0])))[0]


def test_destination_moves_along_the_bearing() -> None:
    lat, lon = destination(np.array([19.0]), np.array([86.0]), np.array([90.0]), 101)

    assert lat[0, 0] == pytest.approx(19.0)
    assert lat[0, -1] == pytest.approx(19.0, abs=0.01)
    assert (lon[0, -1] - 86.0) * 111.195 * np.cos(np.radians(19.0)) == pytest.approx(100.0 * TRANSECT_STEP_KM, rel=0.01)


def test_coast_from_grid_finds_the_open_coast_facing_seaward() -> None:
    coast = coast_from_grid(east_facing_coast(lagoon=True), BBOX)

    assert coast.lat.size > 50
    assert np.allclose(coast.lon, 86.0 + 0.5 * CELL_DEG, atol=CELL_DEG)  # only the sea cells on the open shore
    assert np.median(coast.seaward_deg) == pytest.approx(90.0, abs=1.0)
    depth = coast.depth_m[coast.lat.size // 2]
    shelf = depth[np.isfinite(depth)]
    assert shelf[0] > 0 and (np.diff(shelf) >= 0).all() and shelf.max() < SHELF_DEPTH_M


def test_coast_from_grid_drops_transects_that_never_reach_the_shelf() -> None:
    shallow_everywhere = east_facing_coast(slope_m_per_km=0.1)  # never deeper than ~20 m on the grid

    assert coast_from_grid(shallow_everywhere, BBOX).lat.size == 0


def test_wind_setup_matches_the_analytic_solution_for_constant_stress() -> None:
    depth = np.array([[10.0, 20.0, 30.0, np.nan]])
    stress = np.full((1, 4, 2), 2.0)
    stress[..., 1] = -2.0

    eta = wind_setup(depth, stress)

    # Small setup: eta ~ tau dx / (rho g) * sum(1 / h) over the wet samples.
    expected = 2.0 * 1000.0 / (RHO_SEA * GRAVITY) * (1 / 10 + 1 / 20 + 1 / 30)
    assert eta[0, 0] == pytest.approx(expected, rel=0.02)
    assert eta[0, 1] == pytest.approx(-expected, rel=0.05)  # setdown under offshore wind


def test_wind_setup_is_finite_at_the_shoreline() -> None:
    eta = wind_setup(np.array([[0.1]]), np.array([[[1.0]]]))

    assert eta[0, 0] == pytest.approx(1000.0 / (RHO_SEA * GRAVITY * MIN_WATER_DEPTH_M))


def test_coastal_surge_peaks_where_the_storm_blows_onshore() -> None:
    coast = coast_from_grid(east_facing_coast(), BBOX)
    # Northbound storm offshore at 86.6E: onshore (westward) winds lie north of the centre on an east-facing coast.
    track = Track.from_records(make_fixes(n=9, lon=86.6, vmax=110.0))

    out = coastal_surge(coast, track)

    assert out["peak_m"].shape == coast.lat.shape
    assert np.nanmax(out["peak_m"]) > 0.5
    peak = np.nanargmax(out["peak_m"])
    assert out["barometer_m"][peak] > 0
    assert out["peak_m"][peak] == pytest.approx(out["setup_m"][peak] + out["barometer_m"][peak])
    assert not np.isnat(out["peak_time"][peak])


def test_coastal_surge_is_nan_when_the_storm_stays_far_away() -> None:
    coast = coast_from_grid(east_facing_coast(), BBOX)
    far = Track.from_records(make_fixes(n=3, lon=100.0))

    out = coastal_surge(coast, far)

    assert np.isnan(out["peak_m"]).all() and np.isnat(out["peak_time"]).all()


def test_inundation_decays_inland_and_stays_above_the_ground() -> None:
    lon = 86.0 - np.array([0.0, 14.5, 1.0]) / (111.195 * np.cos(np.radians(19.5)))

    out = inundation(
        np.full(3, 19.5),
        lon,
        np.array([0.5, 0.0, np.nan]),
        coast_lat=np.array([19.5]),
        coast_lon=np.array([86.0]),
        peak_m=np.array([2.0]),
    )

    assert out["coast_km"][:2] == pytest.approx([0.0, 14.5], abs=0.1)
    assert out["surge_m"] == pytest.approx([2.0, 2.0, 2.0])
    assert out["flood_m"][0] == pytest.approx(1.5, abs=0.01)
    assert out["flood_m"][1] == pytest.approx(1.0, abs=0.02)  # 1 m lost over 14.5 km
    assert np.isnan(out["flood_m"][2])
