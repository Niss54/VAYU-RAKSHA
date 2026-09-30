try:
    import pytest
except ImportError:
    class MockPytest:
        @staticmethod
        def approx(expected, abs_tol=1e-5):
            class Approx:
                def __eq__(self, other):
                    return abs(other - expected) <= abs_tol
            return Approx()

        @staticmethod
        def raises(exc_cls, match=None):
            class RaisesContext:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc_val, exc_tb):
                    if exc_type is None:
                        raise AssertionError(f"Expected {exc_cls} was not raised")
                    return issubclass(exc_type, exc_cls)
            return RaisesContext()

    pytest = MockPytest()

import pandas as pd
from shadowcast_geo.cascade import (
    MAX_CASCADE_HOPS,
    build_dependency_graph,
    find_cascade_chains,
    propagate_cascade,
    run_cascade_analysis,
)


def _make_assets() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"asset_id": "sub1", "kind": "substation", "lat": 20.0, "lon": 86.0, "population": 0, "p_outage": 0.95},
            {"asset_id": "hosp1", "kind": "hospital", "lat": 20.1, "lon": 86.0, "population": 5000, "p_outage": 0.10},
            {"asset_id": "ww1", "kind": "water_works", "lat": 20.0, "lon": 86.1, "population": 0, "p_outage": 0.05},
            {"asset_id": "clin1", "kind": "clinic", "lat": 20.1, "lon": 86.1, "population": 200, "p_outage": 0.02},
            {"asset_id": "sch1", "kind": "school", "lat": 20.2, "lon": 86.2, "population": 800, "p_outage": 0.01},
        ]
    )


def test_build_graph_nodes():
    assets = _make_assets()
    G = build_dependency_graph(assets)
    assert set(G.nodes()) == set(assets["asset_id"])


def test_build_graph_substation_to_hospital():
    assets = _make_assets()
    G = build_dependency_graph(assets)
    # sub1 → hosp1 should exist (both in range, rule exists)
    assert G.has_edge("sub1", "hosp1")
    assert G["sub1"]["hosp1"]["strength"] == pytest.approx(0.90)


def test_propagate_cascade_high_upstream():
    assets = _make_assets()
    G = build_dependency_graph(assets)
    direct = dict(zip(assets["asset_id"], assets["p_outage"]))
    p_total, p_cascade = propagate_cascade(G, direct)
    # hospital has direct 0.10 but sub1 (0.95) should cascade into it
    assert p_total["hosp1"] > direct["hosp1"]
    assert p_cascade["hosp1"] > 0.1


def test_propagate_cascade_clamp_at_one():
    assets = _make_assets()
    G = build_dependency_graph(assets)
    direct = {a: 1.0 for a in assets["asset_id"]}  # everyone at 100%
    p_total, _ = propagate_cascade(G, direct)
    assert all(v <= 1.0 for v in p_total.values())


def test_find_cascade_chains_returns_correct_initiator():
    assets = _make_assets()
    G = build_dependency_graph(assets)
    direct = dict(zip(assets["asset_id"], assets["p_outage"]))
    chains = find_cascade_chains(G, direct, top_n=5)
    assert len(chains) >= 1
    # sub1 should be the top initiator (highest p_outage with most victims)
    assert chains[0]["initiator"] == "sub1"


def test_run_cascade_analysis_full():
    assets = _make_assets()
    result = run_cascade_analysis(assets)
    assert result.cascade_scores is not None
    assert len(result.top_initiators) >= 1
    assert result.top_initiators[0]["asset_id"] == "sub1"
    assert result.population_at_cascade_risk >= 0


def test_run_cascade_analysis_missing_columns():
    bad = pd.DataFrame([{"asset_id": "x", "kind": "hospital"}])
    with pytest.raises(ValueError, match="missing columns"):
        run_cascade_analysis(bad)


def test_max_cascade_hops_respected():
    assets = _make_assets()
    G = build_dependency_graph(assets)
    direct = dict(zip(assets["asset_id"], assets["p_outage"]))
    chains = find_cascade_chains(G, direct)
    for chain in chains:
        for v in chain["victims"]:
            assert v["hop"] <= MAX_CASCADE_HOPS
