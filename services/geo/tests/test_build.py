from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import numpy as np
import pandas as pd
import pytest

from shadowcast_geo import build
from shadowcast_geo.api import load_scenarios
from shadowcast_geo.calibration import OutageModel
from shadowcast_geo.config import SCENARIOS, Settings
from shadowcast_geo.ensemble import StormForecast
from shadowcast_geo.surge import Grid
from tests.conftest import MemoryArtifacts, east_facing_coast, make_fixes

SUBSTATION_LONS = [86.02, 86.05, 86.1, 86.2, 86.4, 86.8, 87.2, 87.6]


@pytest.fixture
def pipeline(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> MemoryArtifacts:
    """Stub every external input: synthetic track, eight substations and night lights that fade near the track."""
    frame = pd.DataFrame(
        {
            "asset_id": [f"osm:node/{i}" for i in range(len(SUBSTATION_LONS))] + ["osdma:PURI:19.5,86.3"],
            "kind": ["substation"] * len(SUBSTATION_LONS) + ["cyclone_shelter"],
            "name": [f"Sub {i}" for i in range(len(SUBSTATION_LONS))] + ["Shelter"],
            "source": ["OpenStreetMap"] * len(SUBSTATION_LONS) + ["OSDMA (MCS)"],
            "lat": [19.5] * (len(SUBSTATION_LONS) + 1),
            "lon": [*SUBSTATION_LONS, 86.3],
        }
    )

    def nightlights(points: pd.DataFrame, pre: object, post: object) -> pd.DataFrame:
        loss = np.where(points["lon"] < 86.3, 85.0, 5.0)
        return pd.DataFrame({"ntl_pre": 5.0, "ntl_post": 5.0 * (1 - loss / 100), "loss_pct": loss}, index=points.index)

    def best_track(_client: object, _settings: object, storm: str, _season: int) -> list[dict[str, Any]]:
        landfall = next(s.landfall for s in SCENARIOS.values() if s.storm == storm)
        return make_fixes(start=landfall - timedelta(hours=9))

    def ensemble(_client: object, _settings: object, issued: datetime) -> list[StormForecast]:
        start = SCENARIOS["dana-2024"].landfall - timedelta(hours=9)
        members = {m: make_fixes(lon=86.0 + 0.05 * m, vmax=60.0, start=start) for m in range(1, 5)}
        return [StormForecast("70B", issued, members), StormForecast("99A", issued, {1: make_fixes(lon=70.0)})]

    def assets(*_: object) -> pd.DataFrame:
        return frame

    def enrich(points: pd.DataFrame) -> pd.DataFrame:
        return points.assign(population=1500.0, elevation_m=4.0)

    def night_light_images(bbox: object, pre: object, post: object) -> tuple[str, str]:
        return "https://ee.test/pre", "https://ee.test/post"

    def fetch_image(_client: object, _settings: object, cache_name: str, urls: tuple[str, ...]) -> bytes:
        return f"{cache_name}:{urls[0]}".encode()

    def roads(*_: object) -> list[dict[str, Any]]:
        return [{"road_id": "osm:way/9", "name": "NH-16", "ref": "NH16", "highway": "trunk",
                 "coords": [[19.2, 86.05], [19.8, 86.05]]}]  # fmt: skip

    def ground(points: pd.DataFrame) -> pd.Series:
        return pd.Series(3.0, index=points.index)

    def districts(points: pd.DataFrame) -> pd.Series:
        return pd.Series(["Puri"] * (len(points) - 1) + [None], index=points.index, dtype=object)

    def observed_rain(points: pd.DataFrame, start: datetime, end: datetime) -> pd.Series:
        assert end - start == timedelta(days=6)
        return pd.Series(np.linspace(80.0, 160.0, len(points)), index=points.index)

    def relief(bbox: tuple[float, float, float, float]) -> Grid:
        return east_facing_coast(coast_lon=(bbox[1] + bbox[3]) / 2)  # a coast through the middle of every region

    def initialize(project: str) -> None:
        assert project == "argmax-cyclone-2026"

    monkeypatch.setattr(build, "load_best_track", best_track)
    monkeypatch.setattr(build, "load_assets", assets)
    monkeypatch.setattr(build, "load_ensemble", ensemble)
    monkeypatch.setattr(build.earth, "initialize", initialize)
    monkeypatch.setattr(build.earth, "enrich", enrich)
    monkeypatch.setattr(build.earth, "nightlight_loss", nightlights)
    monkeypatch.setattr(build.earth, "relief", relief)
    monkeypatch.setattr(build.earth, "observed_rain", observed_rain)
    monkeypatch.setattr(build.earth, "districts", districts)
    monkeypatch.setattr(build.earth, "nightlight_image_urls", night_light_images)
    monkeypatch.setattr(build, "download", fetch_image)
    monkeypatch.setattr(build, "fetch_osm_roads", roads)
    monkeypatch.setattr(build.earth, "ground_elevation", ground)
    store = MemoryArtifacts()

    def artifact_store(_settings: Settings) -> MemoryArtifacts:
        return store

    monkeypatch.setattr(build, "artifact_store", artifact_store)
    return store


def test_main_builds_every_scenario(pipeline: MemoryArtifacts) -> None:
    assert build.main([]) == 0

    index = pipeline.read_json("scenarios/index.json")
    assert [entry["id"] for entry in index] == list(SCENARIOS)
    model = pipeline.read_json("models/outage.json")
    assert model["model"]["trained_on"] == "fani-2019"
    assert model["model"]["auc"] == 1.0
    fani = pipeline.read_json("scenarios/fani-2019/scenario.json")
    assert fani["skill"]["out_of_sample"] is False
    assert fani["skill"]["spatial_holdout"]["folds"] == 5
    assert "spatial_holdout" not in pipeline.read_json("scenarios/dana-2024/scenario.json")["skill"]
    assert fani["asset_counts"] == {"substation": 8, "cyclone_shelter": 1}
    dana = pipeline.read_json("scenarios/dana-2024/scenario.json")
    assert dana["skill"]["out_of_sample"] is True
    assert fani["forecasts"] == []
    assert [f["key"] for f in dana["forecasts"]] == [
        "20241022T00Z", "20241022T12Z", "20241023T00Z", "20241023T12Z", "20241024T00Z"
    ]  # fmt: skip
    first = dana["forecasts"][0]
    assert (first["storm_id"], first["members"], first["lead_h"]) == ("70B", 4, 68.0)
    forecast_assets: list[dict[str, Any]] = pipeline.read_json("scenarios/dana-2024/forecasts/20241022T00Z/assets.json")
    assert {"p34", "p64", "wind_p10", "wind_p90", "members", "gale_arrival"} <= set(forecast_assets[0])
    assert forecast_assets[0]["members"] == 4
    assert "flood_m" not in forecast_assets[0]  # no hindsight surge in a forecast replay
    assert "observed_rain_mm" not in forecast_assets[0] and "p_rain" in forecast_assets[0]
    tracks = pipeline.read_json("scenarios/dana-2024/forecasts/20241022T00Z/tracks.json")
    assert [t["member"] for t in tracks] == [1, 2, 3, 4]


def test_build_output_satisfies_api_schemas(pipeline: MemoryArtifacts) -> None:
    build.main([])

    loaded = load_scenarios(pipeline)  # validates every artifact against the API response models

    assert set(loaded) == set(SCENARIOS)
    assert len(loaded["dana-2024"].forecasts) == 5
    first = next(iter(loaded["dana-2024"].forecasts.values()))
    assert first.assets[0].closest_time is not None
    assert loaded["fani-2019"].assets[0].gale_arrival is not None
    assets: list[dict[str, Any]] = pipeline.read_json("scenarios/fani-2019/assets.json")
    assert [a["rank"] for a in assets] == list(range(1, 10))
    assert assets[0]["peak_time"].endswith("Z")
    assert {"coast_km", "surge_m", "flood_m", "rain_mm", "observed_rain_mm"} <= set(assets[0])
    rain = pipeline.read_json("scenarios/fani-2019/scenario.json")["rain"]
    assert rain["n"] == 9 and rain["max_observed_mm"] == 160.0 and rain["spearman"] is not None
    roads = pipeline.read_json("scenarios/fani-2019/roads.json")["features"]
    assert roads[0]["properties"]["status"] == "cut" and roads[0]["properties"]["closes_at"].endswith("Z")
    summary_roads = pipeline.read_json("scenarios/fani-2019/scenario.json")["roads"]
    assert summary_roads["roads"] == 1 and summary_roads["km_cut"] > 0
    near = next(a for a in assets if a["asset_id"] == "osm:node/0")  # 3 km from the road
    assert near["access_road"] == "NH-16" and near["access_closes"].endswith("Z") and near["road_km"] < 5
    assert next(a for a in assets if a["kind"] == "cyclone_shelter")["access_road"] is None  # 26 km away
    image = pipeline.read_bytes("scenarios/fani-2019/evidence/night-lights-post.png")
    assert image == b"fani-2019-night-lights-post.png:https://ee.test/post"
    insurance = pipeline.read_json("scenarios/fani-2019/scenario.json")["insurance"]
    assert [d["district"] for d in insurance["districts"]] == ["Puri"]
    assert insurance["districts"][0]["lit_substations"] == 8
    dana = pipeline.read_json("scenarios/dana-2024/scenario.json")
    assert dana["forecasts"][0]["districts"][0]["district"] == "Puri"
    surge = pipeline.read_json("scenarios/fani-2019/surge.json")
    summary = pipeline.read_json("scenarios/fani-2019/scenario.json")["surge"]
    assert len(surge) == summary["coast_points"] > 0
    assert summary["peak_m"] == max(p["peak_m"] for p in surge if p["peak_m"] is not None) > 0
    assert summary["flooded_sites"] >= 0 and summary["time"].endswith("Z")
    assert summary["observed"]["place"] == "Puri coast" and summary["observed"]["modelled_m"] is not None
    assert {a["kind"] for a in assets if a["observed_loss_pct"] is None} == {"cyclone_shelter"}
    backtest = pipeline.read_json("scenarios/fani-2019/backtest.json")
    assert len(backtest["substations"]) == 8
    fani_start = SCENARIOS["fani-2019"].landfall - timedelta(hours=9)
    assert pipeline.read_json("scenarios/fani-2019/track.json") == make_fixes(start=fani_start)


def test_main_rebuilds_one_scenario_with_stored_model(pipeline: MemoryArtifacts) -> None:
    build.main(["fani-2019"])

    assert build.main(["dana-2024"]) == 0

    assert [entry["id"] for entry in pipeline.read_json("scenarios/index.json")] == ["fani-2019", "dana-2024"]


def test_main_rejects_unknown_scenario(pipeline: MemoryArtifacts) -> None:
    with pytest.raises(SystemExit):
        build.main(["atlantis-2030"])


def test_forecasts_need_landfall_inside_best_track(
    pipeline: MemoryArtifacts, settings: Settings, model: OutageModel, monkeypatch: pytest.MonkeyPatch
) -> None:
    def track_from_2019(*_: object) -> list[dict[str, Any]]:
        return make_fixes()  # 2019 track, 2024 landfall

    monkeypatch.setattr(build, "load_best_track", track_from_2019)
    pipeline.write_json(build.MODEL_PATH, {"model": model.to_dict(), "bands": []})

    with httpx.Client() as client, pytest.raises(ValueError, match="landfall time is outside the best track"):
        build.build_scenario(SCENARIOS["dana-2024"], client, settings, pipeline, model)


def test_non_reference_scenario_requires_model(pipeline: MemoryArtifacts, settings: Settings) -> None:
    with httpx.Client() as client, pytest.raises(ValueError, match="needs the reference outage model"):
        build.build_scenario(SCENARIOS["dana-2024"], client, settings, pipeline, None)


def test_json_safe() -> None:
    value = {"a": np.float64(1.5), "b": [float("nan"), np.int64(2), (float("inf"), "x")], 3: None}

    assert build.json_safe(value) == {"a": 1.5, "b": [None, 2, [None, "x"]], "3": None}


def test_frame_records(model: OutageModel) -> None:
    frame = pd.DataFrame(
        {
            "asset_id": ["x"],
            "peak_wind_kt": [101.26],
            "peak_time": [pd.Timestamp("2019-05-03T03:00:00")],
            "band_entry": [pd.NaT],
            "p_outage": [np.float64(0.123456)],
        }
    )

    records = build.frame_records(frame, ["asset_id", "peak_wind_kt", "peak_time", "band_entry", "p_outage", "absent"])

    assert records == [
        {
            "asset_id": "x",
            "peak_wind_kt": 101.3,
            "peak_time": "2019-05-03T03:00:00Z",
            "band_entry": None,
            "p_outage": 0.1235,
        }
    ]
