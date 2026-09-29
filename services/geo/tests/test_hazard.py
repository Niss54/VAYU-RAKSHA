from datetime import UTC, datetime, timedelta, timezone

import numpy as np
import pytest

from shadowcast_geo.hazard import (
    Track,
    exposure,
    geodesics,
    holland_wind,
    radii_to_km,
    rcliper_rain,
    track_position,
    willoughby_rmw_km,
    wind_at,
    wind_timeline,
)
from tests.conftest import START, make_fixes


def test_track_from_records(track: Track) -> None:
    assert track.times.dtype == np.dtype("datetime64[s]")
    assert track.times[0] == np.datetime64("2019-05-02T12:00:00")
    assert track.radii_km[64].shape == (4, 7)
    assert np.isnan(track.radii_km[64][1]).all()
    assert track.radii_km[34][0, 0] == 200.0


@pytest.mark.parametrize(
    ("asset", "expected_km", "expected_bearing"),
    [((19.0, 86.0), 111.2, 0.0), ((18.0, 87.0), 105.8, 90.0), ((17.0, 86.0), 111.2, 180.0)],
)
def test_geodesics(asset: tuple[float, float], expected_km: float, expected_bearing: float) -> None:
    distance, bearing = geodesics(np.array([asset[0]]), np.array([asset[1]]), np.array([18.0]), np.array([86.0]))

    assert distance.shape == (1, 1)
    assert distance[0, 0] == pytest.approx(expected_km, abs=0.5)
    assert bearing[0, 0] == pytest.approx(expected_bearing, abs=0.5)


def test_holland_wind_profile() -> None:
    distance = np.array([[30.0], [60.0], [300.0], [0.0]])

    wind = holland_wind(distance, np.array([100.0]), np.array([30.0]))[:, 0]

    assert wind[0] == pytest.approx(100.0)  # maximum at the radius of maximum wind
    assert wind[0] > wind[1] > wind[2] > 0
    assert wind[3] < wind[0]  # calm eye


def test_exposure_near_mid_far_and_missing_intensity(track: Track) -> None:
    lat, lon = np.array([19.5, 19.5, 19.5]), np.array([86.05, 86.4, 88.5])

    result = exposure(lat, lon, track)

    near, mid, far = range(3)
    assert result["band_kt"].tolist() == [64, 64, 0]
    # The eyewall passes over the near-track asset between 3-hourly fixes; densification must catch it.
    assert result["peak_wind_kt"][near] == pytest.approx(100.0, abs=0.5)
    assert result["peak_wind_kt"][near] > result["peak_wind_kt"][mid] > result["peak_wind_kt"][far]
    assert result["peak_time"][near] == np.datetime64("2019-05-02T19:30:00")
    assert result["closest_time"][near] == np.datetime64("2019-05-02T21:00:00")
    assert result["band_entry"][mid] == np.datetime64("2019-05-02T18:45:00")
    assert np.isnat(result["band_entry"][far])
    assert result["gale_arrival"][near] == result["gale_arrival"][mid] == track.times[0]  # gales from the first fix
    assert np.isnat(result["gale_arrival"][far])
    assert result["min_dist_km"][near] == pytest.approx(5.2, abs=0.2)

    calm = Track.from_records(make_fixes(vmax=float("nan")))
    assert np.isnan(exposure(lat[:1], lon[:1], calm)["peak_wind_kt"][0])


def test_densify(track: Track) -> None:
    dense = track.densify(15)

    assert dense.times.size == 73
    assert dense.times[1] == np.datetime64("2019-05-02T12:15:00")
    assert dense.lat[2] == pytest.approx(18.0 + 0.5 * 30 / 180)
    assert dense.times[-1] == track.times[-1]
    assert np.isnan(dense.radii_km[64][1]).all()
    assert dense.radii_km[34].shape == (4, 73)


def test_wind_timeline(track: Track) -> None:
    times, winds = wind_timeline(19.5, 86.4, track)

    assert times.size == winds.size == 73
    assert times[int(winds.argmax())] == np.datetime64("2019-05-02T21:00:00")


@pytest.mark.parametrize(
    ("when", "expected_lat"),
    [
        (START + timedelta(hours=1, minutes=30), 18.25),
        ((START + timedelta(hours=3)).astimezone(timezone(timedelta(hours=5, minutes=30))), 18.5),
        ((START + timedelta(hours=6)).replace(tzinfo=None), 19.0),
        (START - timedelta(hours=1), None),
        (START + timedelta(days=2), None),
    ],
)
def test_track_position(track: Track, when: datetime, expected_lat: float | None) -> None:
    position = track_position(track, when)

    if expected_lat is None:
        assert position is None
    else:
        assert position is not None
        assert position["lat"] == pytest.approx(expected_lat)
        assert position["vmax_kt"] == 100.0


def test_wind_at(track: Track) -> None:
    lat, lon = np.array([19.5, 25.0]), np.array([86.05, 86.0])

    inside = wind_at(lat, lon, track, START + timedelta(hours=7, minutes=30))  # eyewall over the first asset
    outside = wind_at(lat, lon, track, datetime(2020, 1, 1, tzinfo=UTC))

    assert inside[0] > 90  # eyewall
    assert inside[1] < 20  # ~600 km away
    assert outside.tolist() == [0.0, 0.0]


def test_rcliper_rain_profile() -> None:
    distance = np.array([[0.0, 30.0, 300.0, 30.0]])

    rate = rcliper_rain(distance, np.array([100.0, 100.0, 100.0, np.nan]))

    # 100 kt: U = 2.97; T0 = 10.66 and Tm = 12.66 in/day, rm = 25.9 km, re = 102.5 km.
    assert rate[0, 0] == pytest.approx(10.66 * 25.4 / 24, rel=0.01)
    assert rate[0, 1] == pytest.approx(12.66 * np.exp(-(30 - 25.89) / 102.48) * 25.4 / 24, rel=0.01)
    assert rate[0, 2] < rate[0, 1]
    assert rate[0, 3] == 0.0  # missing intensity rains nothing


def test_exposure_accumulates_storm_rain(track: Track) -> None:
    rain = exposure(np.array([19.5, 19.5]), np.array([86.05, 88.5]), track)["rain_mm"]

    assert rain[0] > rain[1] > 0


def test_willoughby_rmw_km() -> None:
    rmw = willoughby_rmw_km(np.array([40.0, 100.0, 100.0]), np.array([20.0, 20.0, -20.0]))

    assert rmw[0] == pytest.approx(46.4 * np.exp(-0.0155 * 40 / 1.943844 + 0.0169 * 20))
    assert rmw[0] > rmw[1]  # stronger storms have tighter cores
    assert rmw[1] == rmw[2]  # symmetric in latitude


def test_radii_to_km() -> None:
    assert radii_to_km([10.0, None, float("nan"), 0.0]) == [18.5, None, None, 0.0]
