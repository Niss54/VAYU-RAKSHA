try:
    import pytest
except ImportError:
    pytest = None
from datetime import datetime
try:
    from shadowcast_geo.api import (
        get_cascade,
        get_climada_comparison,
        get_isro_status,
        get_sar_validation,
        router,
    )
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from shadowcast_geo.models import Asset, RegionOut, ScenarioDetail


class MockScenario:
    def __init__(self, with_cached: bool = False):
        self.detail = ScenarioDetail(
            id="fani-2019",
            storm="Fani",
            season=2019,
            region=RegionOut(id="odisha", name="Odisha", bbox=[19.0, 84.5, 21.5, 87.5]),
            landfall="2019-05-03T03:30:00Z",
            track_source="IBTrACS",
            peak_vmax_kt=140.0,
            asset_counts={"substation": 5, "hospital": 3},
            model={"intercept": -3.5, "slope": 0.05, "trained_on": "fani-2019", "n": 200, "auc": 0.97, "brier": 0.08},
            skill={"n": 200, "observed_outage_rate": 0.35, "auc": 0.97, "brier": 0.08, "spearman": 0.85, "out_of_sample": False},
            loss_by_band=[],
            surge={"peak_m": 2.91, "lat": 19.8, "lon": 85.8, "time": "2019-05-03T03:30:00Z", "coast_points": 50, "flooded_sites": 12, "method": "1D"},
            rain={"model": "R-CLIPER", "truth": "GPM", "n": 100, "spearman": 0.72, "median_ratio": 1.05, "max_modelled_mm": 350.0, "max_observed_mm": 380.0, "extreme_sites": 25},
            roads={"roads": 45, "km": 680, "km_cut": 120, "km_at_risk": 200, "first_closure": "2019-05-02T18:00:00Z", "cut_by_surge": 14},
            forecasts=[],
            built_at="2026-09-30T10:00:00Z",
        )
        self.fixes = [{"lat": 16.5, "lon": 86.8, "vmax_kt": 140.0, "rmw_km": 25.0, "time": "2019-05-02T18:00:00Z"}]
        self.assets = [
            Asset(asset_id="sub1", kind="substation", name="Puri Substation", lat=20.0, lon=86.0, criticality=4, p_outage=0.92, peak_wind_kt=125.0, score=0.736, rank=1, reasons=[]),
            Asset(asset_id="hosp1", kind="hospital", name="Puri Hospital", lat=20.1, lon=86.0, criticality=5, p_outage=0.15, peak_wind_kt=95.0, score=0.15, rank=2, reasons=[]),
        ]
        if with_cached:
            self.cascade = {"top_chains": [], "top_actions": [], "population_at_cascade_risk": 15000.0, "cascade_edges": 12, "cascade_nodes": 8}
            self.isro = {"mosdac_available": True, "insat3ds_intensity_kt": 140.0, "ri_risk": True, "sst_c": 29.2, "citation": {}}
            self.sar = {"scenario_id": "fani-2019", "iou": 0.54, "sar_source": "RISAT-1A"}
            self.climada = {"agreement_rate": 0.76, "mean_absolute_difference": 0.12}
        else:
            self.cascade = None
            self.isro = None
            self.sar = None
            self.climada = None


def test_routes_registered():
    if not HAS_FASTAPI:
        return
    route_paths = [r.path for r in router.routes]
    assert "/scenarios/{scenario_id}/cascade" in route_paths
    assert "/scenarios/{scenario_id}/isro" in route_paths
    assert "/scenarios/{scenario_id}/sar" in route_paths
    assert "/scenarios/{scenario_id}/climada" in route_paths


import asyncio


def test_get_cascade_cached_and_fallback():
    if not HAS_FASTAPI:
        return
    # Cached
    cached_scenario = MockScenario(with_cached=True)
    res = asyncio.run(get_cascade(cached_scenario))
    assert res["cascade_nodes"] == 8

    # Dynamic fallback
    uncached_scenario = MockScenario(with_cached=False)
    res2 = asyncio.run(get_cascade(uncached_scenario))
    assert "top_actions" in res2
    assert "top_chains" in res2


def test_get_isro_status():
    if not HAS_FASTAPI:
        return
    cached_scenario = MockScenario(with_cached=True)
    res = asyncio.run(get_isro_status(cached_scenario))
    assert res["mosdac_available"] is True

    uncached_scenario = MockScenario(with_cached=False)
    res2 = asyncio.run(get_isro_status(uncached_scenario))
    assert "citation" in res2
    assert res2["insat3ds_intensity_kt"] > 0


def test_get_sar_validation():
    if not HAS_FASTAPI:
        return
    cached_scenario = MockScenario(with_cached=True)
    res = asyncio.run(get_sar_validation(cached_scenario))
    assert res["iou"] == 0.54

    uncached_scenario = MockScenario(with_cached=False)
    res2 = asyncio.run(get_sar_validation(uncached_scenario))
    assert "iou" in res2


def test_get_climada_comparison():
    if not HAS_FASTAPI:
        return
    cached_scenario = MockScenario(with_cached=True)
    res = asyncio.run(get_climada_comparison(cached_scenario))
    assert res["agreement_rate"] == 0.76

    uncached_scenario = MockScenario(with_cached=False)
    res2 = asyncio.run(get_climada_comparison(uncached_scenario))
    assert "agreement_rate" in res2

