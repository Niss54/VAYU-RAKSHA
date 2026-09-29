from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from shadowcast_geo.api import create_app
from shadowcast_geo.config import Settings
from tests.conftest import MemoryArtifacts, make_fixes


def _asset(asset_id: str, rank: int, kind: str, score: float, lon: float, name: str | None = None) -> dict[str, Any]:
    return {
        "asset_id": asset_id, "rank": rank, "kind": kind, "name": name, "source": "OpenStreetMap",
        "lat": 19.5, "lon": lon, "peak_wind_kt": 110.0, "peak_time": "2019-05-02T21:00:00Z", "min_dist_km": 5.0,
        "closest_time": "2019-05-02T21:00:00Z", "band_kt": 64, "band_entry": "2019-05-02T18:00:00Z",
        "population": 1000.0, "elevation_m": 3.0, "criticality": 5, "p_outage": 0.9, "score": score,
        "observed_loss_pct": None, "reasons": ["Modelled peak wind 110 kt"], "extra_field": "ignored",
    }  # fmt: skip


@pytest.fixture
def store() -> MemoryArtifacts:
    artifacts = MemoryArtifacts()
    region = {"id": "odisha-coast", "name": "Odisha coast", "bbox": [19.0, 84.4, 21.7, 87.6]}
    summary = {"id": "fani-2019", "storm": "Fani", "season": 2019, "region": region,
               "landfall": "2019-05-03T03:30:00Z", "peak_vmax_kt": 150.0}  # fmt: skip
    artifacts.write_json("scenarios/index.json", [summary])
    artifacts.write_json("scenarios/fani-2019/scenario.json", {
        **summary, "track_source": "IBTrACS best track", "asset_counts": {"hospital": 1, "school": 1},
        "model": {"intercept": -12.8, "slope": 0.128}, "skill": {"auc": 0.91, "out_of_sample": False},
        "loss_by_band": [{"low_kt": 100.0, "high_kt": 130.0, "n": 36.0, "median": 82.0}],
        "rain": {"model": "R-CLIPER", "truth": "GPM IMERG", "n": 2, "spearman": 0.7, "median_ratio": 1.2,
                 "max_modelled_mm": 180.0, "max_observed_mm": 150.0, "extreme_sites": 0},
        "insurance": {"terms": "illustrative", "districts": []},
        "roads": {"roads": 1, "km": 10, "km_cut": 10, "km_at_risk": 0, "first_closure": "2019-05-02T22:00:00Z",
                  "cut_by_surge": 0},
        "surge": {"peak_m": 1.5, "lat": 19.8, "lon": 85.8, "time": "2019-05-03T03:00:00Z", "coast_points": 1,
                  "flooded_sites": 0, "method": "1D wind setup"},
        "forecasts": [{"key": "20190501T12Z", "issued": "2019-05-01T12:00:00Z", "lead_h": 39.5, "storm_id": "01B",
                       "members": 52, "assets_likely_gale": 1, "assets_likely_hurricane": 0, "max_p_outage": 0.4,
                       "source": "ECMWF IFS ensemble"}],
        "built_at": "2026-09-26T00:00:00Z",
    })  # fmt: skip
    artifacts.write_json("scenarios/fani-2019/track.json", make_fixes())
    artifacts.write_json("scenarios/fani-2019/assets.json", [
        _asset("osm:node/1", 1, "hospital", 0.9, 86.05, "District Hospital Puri"),
        _asset("osm:way/2", 2, "school", 0.36, 86.4),
    ])  # fmt: skip
    artifacts.write_json("scenarios/fani-2019/backtest.json", {"skill": {"auc": 0.91}, "substations": []})
    artifacts.write_json("scenarios/fani-2019/roads.json", {"type": "FeatureCollection", "features": []})
    for name in ("night-lights-pre", "night-lights-post"):
        artifacts.write_bytes(f"scenarios/fani-2019/evidence/{name}.png", f"png:{name}".encode(), "image/png")
    artifacts.write_json("scenarios/fani-2019/surge.json", [
        {"lat": 19.8, "lon": 85.8, "peak_m": 1.5, "setup_m": 0.8, "barometer_m": 0.7,
         "peak_time": "2019-05-03T03:00:00Z"},
    ])  # fmt: skip
    forecast_asset = {**_asset("osm:node/1", 1, "hospital", 0.4, 86.05), "p34": 0.9, "p64": 0.25, "wind_p10": 40.0,
                      "wind_p90": 80.0, "members": 52, "p_rain": 0.1,
                      "gale_arrival": "2019-05-02T18:00:00Z"}  # fmt: skip
    artifacts.write_json("scenarios/fani-2019/forecasts/20190501T12Z/assets.json", [forecast_asset])
    artifacts.write_json(
        "scenarios/fani-2019/forecasts/20190501T12Z/tracks.json",
        [{"member": 1, "fixes": make_fixes()}, {"member": 2, "fixes": make_fixes(lon=86.5, vmax=80.0)}],
    )
    return artifacts


@pytest.fixture
def client(store: MemoryArtifacts) -> Iterator[TestClient]:
    with TestClient(create_app(Settings(allowed_origins=("https://shadowcast.test",)), store, store)) as test_client:
        yield test_client


def test_health_and_scenarios(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok", "scenarios": ["fani-2019"]}
    scenarios = client.get("/scenarios").json()
    assert [s["id"] for s in scenarios] == ["fani-2019"]
    assert "model" not in scenarios[0]
    detail = client.get("/scenarios/fani-2019").json()
    assert detail["skill"]["auc"] == 0.91
    assert detail["track_source"] == "IBTrACS best track"


def test_track_geojson(client: TestClient) -> None:
    features = client.get("/scenarios/fani-2019/track").json()["features"]

    assert features[0]["geometry"]["type"] == "LineString"
    assert len(features[0]["geometry"]["coordinates"]) == 7
    assert features[1]["properties"]["vmax_kt"] == 100.0
    assert "lat" not in features[1]["properties"]


@pytest.mark.parametrize(
    ("query", "expected_ids", "expected_total"),
    [
        ("", ["osm:node/1", "osm:way/2"], 2),
        ("?kind=school", ["osm:way/2"], 1),
        ("?kind=school&kind=hospital&limit=1", ["osm:node/1"], 2),
        ("?min_score=0.5", ["osm:node/1"], 1),
        ("?offset=1", ["osm:way/2"], 2),
        ("?q=PURI", ["osm:node/1"], 1),
        ("?q=way/2", ["osm:way/2"], 1),
    ],
)
def test_assets_filters(client: TestClient, query: str, expected_ids: list[str], expected_total: int) -> None:
    page = client.get(f"/scenarios/fani-2019/assets{query}").json()

    assert [a["asset_id"] for a in page["items"]] == expected_ids
    assert page["total"] == expected_total
    assert "extra_field" not in page["items"][0]


def test_asset_detail_with_slash_in_id(client: TestClient) -> None:
    detail = client.get("/scenarios/fani-2019/assets/osm:way/2").json()

    assert detail["asset"]["asset_id"] == "osm:way/2"
    assert [p["time"] for p in detail["timeline"]][:2] == ["2019-05-02T12:00:00Z", "2019-05-02T12:15:00Z"]
    assert len(detail["timeline"]) == 73
    assert max(p["wind_kt"] for p in detail["timeline"]) > 50


def test_hazard_snapshot(client: TestClient) -> None:
    inside = client.get("/scenarios/fani-2019/hazard", params={"at": "2019-05-03T02:30:00+05:30"}).json()
    naive = client.get("/scenarios/fani-2019/hazard", params={"at": "2019-05-02T21:00:00"}).json()
    outside = client.get("/scenarios/fani-2019/hazard", params={"at": "2020-01-01T00:00:00Z"}).json()

    assert inside["at"] == "2019-05-02T21:00:00Z"
    assert inside["storm"]["lat"] == pytest.approx(19.5)
    assert inside["asset_ids"] == ["osm:node/1", "osm:way/2"]
    assert inside["wind_kt"][0] < 5 < inside["wind_kt"][1]  # the near asset sits in the calm eye at this instant
    assert naive["wind_kt"] == inside["wind_kt"]
    assert outside["storm"] is None
    assert outside["wind_kt"] == [0.0, 0.0]


def test_evidence_images(client: TestClient) -> None:
    image = client.get("/scenarios/fani-2019/evidence/night-lights-post.png")

    assert image.status_code == 200 and image.headers["content-type"] == "image/png"
    assert image.content == b"png:night-lights-post"
    assert client.get("/scenarios/fani-2019/evidence/elsewhere.png").status_code == 404


def test_live_digest_is_cached(client: TestClient, store: MemoryArtifacts) -> None:
    assert client.get("/live").json() == {"run_at": None, "cyclones": [], "warnings": []}

    store.write_json("manifests/2026/09/27/0615Z.json", {})
    assert client.get("/live").json()["run_at"] is None  # served from the cache until the TTL passes


def test_roads(client: TestClient) -> None:
    assert client.get("/scenarios/fani-2019/roads").json()["type"] == "FeatureCollection"
    assert client.get("/scenarios/fani-2019").json()["roads"]["km_cut"] == 10


def test_surge(client: TestClient) -> None:
    assert client.get("/scenarios/fani-2019/surge").json()[0]["peak_m"] == 1.5
    assert client.get("/scenarios/fani-2019").json()["surge"]["peak_m"] == 1.5
    assert client.get("/scenarios/fani-2019").json()["rain"]["spearman"] == 0.7


def test_backtest_and_cors_and_gzip(client: TestClient) -> None:
    response = client.get("/scenarios/fani-2019/backtest", headers={"Origin": "https://shadowcast.test"})

    assert response.json()["skill"]["auc"] == 0.91
    assert response.headers["access-control-allow-origin"] == "https://shadowcast.test"
    track = client.get("/scenarios/fani-2019/track", headers={"Accept-Encoding": "gzip"})
    assert track.headers["content-encoding"] == "gzip"


@pytest.mark.parametrize(
    "path",
    [
        "/scenarios/nope",
        "/scenarios/nope/track",
        "/scenarios/fani-2019/assets/osm:node/404",
        "/scenarios/nope/backtest",
    ],
)
def test_not_found(client: TestClient, path: str) -> None:
    assert client.get(path).status_code == 404


def test_empty_store_serves_no_scenarios(tmp_path: Path) -> None:
    with TestClient(create_app(Settings(), MemoryArtifacts())) as empty:
        assert empty.get("/health").json() == {"status": "ok", "scenarios": []}
        assert empty.get("/scenarios").json() == []


def test_forecast_replay_endpoints(client: TestClient) -> None:
    listing = client.get("/scenarios/fani-2019/forecasts").json()
    assert [(f["key"], f["lead_h"], f["members"]) for f in listing] == [("20190501T12Z", 39.5, 52)]

    tracks = client.get("/scenarios/fani-2019/forecasts/20190501T12Z/tracks").json()["features"]
    assert [t["properties"]["member"] for t in tracks] == [1, 2]
    assert tracks[1]["properties"]["max_vmax_kt"] == 80.0
    assert len(tracks[0]["geometry"]["coordinates"]) == len(tracks[0]["properties"]["times"]) == 7

    page = client.get("/scenarios/fani-2019/forecasts/20190501T12Z/assets", params={"kind": "hospital"}).json()
    assert page["total"] == 1
    assert page["items"][0]["p64"] == 0.25
    assert page["items"][0]["gale_arrival"] == "2019-05-02T18:00:00Z"
    assert client.get("/scenarios/fani-2019/forecasts/20190501T12Z/assets?kind=school").json()["total"] == 0


@pytest.mark.parametrize("path", ["/scenarios/fani-2019/forecasts/19000101T00Z/tracks", "/scenarios/nope/forecasts"])
def test_forecast_not_found(client: TestClient, path: str) -> None:
    assert client.get(path).status_code == 404


def test_invalid_query_is_rejected(client: TestClient) -> None:
    assert client.get("/scenarios/fani-2019/assets?limit=0").status_code == 422
