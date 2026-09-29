import numpy as np
import pandas as pd
import pytest

from shadowcast_geo.roads import nearest_access, road_status, sample_roads

ROADS = [
    {
        "road_id": "osm:way/1",
        "name": "NH-316",
        "ref": "NH316",
        "highway": "trunk",
        "coords": [[19.8, 85.8], [19.8, 85.9]],
    },
    {
        "road_id": "osm:way/2",
        "name": None,
        "ref": "SH13",
        "highway": "primary",
        "coords": [[20.5, 85.8], [20.51, 85.8]],
    },
    {"road_id": "osm:way/3", "name": None, "ref": None, "highway": "primary", "coords": [[21.0, 86.5], [21.0, 86.51]]},
]


def test_sample_roads_every_kilometre_including_both_ends() -> None:
    samples = sample_roads(ROADS)

    first = samples[samples["road"] == 0]
    assert len(first) == 12  # ~10.5 km: stations at 0..10 km plus the far end
    assert (first["lat"].iloc[0], first["lon"].iloc[0]) == (19.8, 85.8)
    assert first["lon"].iloc[-1] == pytest.approx(85.9)
    assert len(samples[samples["road"] == 1]) == 3  # ~1.1 km: start, 1 km, end


def _samples(**overrides: list[object]) -> pd.DataFrame:
    base: dict[str, list[object]] = {
        "road": [0, 0, 1, 2],
        "lat": [19.8, 19.8, 20.5, 21.0],
        "lon": [85.8, 85.9, 85.8, 86.5],
        "peak_wind_kt": [110.0, 90.0, 55.0, 20.0],
        "band_kt": [64, 64, 50, 0],
        "band_entry": list(
            pd.to_datetime(pd.Series(["2019-05-02T23:00:00", "2019-05-02T22:15:00", "2019-05-02T20:00:00", None]))
        ),
        "flood_m": [0.0, 0.0, 0.0, 0.5],
        "rain_mm": [150.0, 150.0, 250.0, 100.0],
        "elevation_m": [8.0, 8.0, 2.0, 1.0],
    }
    return pd.DataFrame({**base, **overrides})


def test_road_status_marks_cuts_risks_and_closures() -> None:
    trunk, state_road, lane = road_status(ROADS, _samples())

    assert trunk["status"] == "cut" and trunk["causes"] == ["hurricane winds"]
    assert trunk["closes_at"] == "2019-05-02T22:15:00Z"  # the first sample inside the 64-kt radius
    assert trunk["peak_wind_kt"] == 110.0 and trunk["path"][0] == [85.8, 19.8]
    assert state_road["status"] == "at risk" and state_road["causes"] == ["extreme rain"]
    assert state_road["closes_at"] is None
    assert lane["status"] == "cut" and lane["causes"] == ["surge"] and lane["flood_m"] == 0.5
    calm = road_status(ROADS[2:], _samples(road=[0, 0, 0, 0], peak_wind_kt=[10.0] * 4, flood_m=[0.0] * 4)
                       .assign(rain_mm=0.0))[0]  # fmt: skip
    assert calm["status"] == "open" and calm["causes"] == []


def test_nearest_access_links_sites_to_roads_within_reach() -> None:
    samples = sample_roads(ROADS)
    statuses = road_status(ROADS, samples.assign(
        peak_wind_kt=100.0, band_kt=64, band_entry=pd.Timestamp("2019-05-02T22:00:00"), flood_m=0.0, rain_mm=0.0,
        elevation_m=5.0,
    ))  # fmt: skip

    access = nearest_access(np.array([19.81, 20.505, 23.0]), np.array([85.85, 85.8, 80.0]), samples, statuses)

    assert access["access_road"].tolist()[:2] == ["NH-316", "SH13"] and pd.isna(access["access_road"].iloc[2])
    assert access["road_km"].iloc[0] == pytest.approx(1.1, abs=0.1)
    assert np.isnan(access["road_km"].iloc[2])
    assert access["access_closes"].iloc[0] == pd.Timestamp("2019-05-02T22:00:00")
    assert pd.isna(access["access_closes"].iloc[2])
