"""Tests for counterfactual hardening optimizer."""
import pandas as pd

try:
    import pytest
except ImportError:
    pytest = None

from shadowcast_geo.counterfactual import (
    HardeningAction,
    _timing_recommendation,
    optimize_hardening_actions,
)


def _make_assets() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"asset_id": "sub1", "kind": "substation", "lat": 20.0, "lon": 86.0, "population": 0, "p_outage": 0.92},
            {"asset_id": "hosp1", "kind": "hospital", "lat": 20.1, "lon": 86.0, "population": 5000, "p_outage": 0.08},
            {"asset_id": "ww1", "kind": "water_works", "lat": 20.0, "lon": 86.1, "population": 0, "p_outage": 0.05},
        ]
    )


def test_optimize_returns_list():
    assets = _make_assets()
    actions = optimize_hardening_actions(assets)
    assert isinstance(actions, list)


def test_actions_ranked():
    assets = _make_assets()
    actions = optimize_hardening_actions(assets)
    if len(actions) >= 2:
        assert actions[0].benefit_cost_ratio >= actions[1].benefit_cost_ratio


def test_substation_timing():
    assert _timing_recommendation("substation", 0.5) == 36
    assert _timing_recommendation("substation", 0.9) == 48


def test_action_rank_assigned():
    assets = _make_assets()
    actions = optimize_hardening_actions(assets)
    for i, a in enumerate(actions):
        assert a.rank == i + 1


def test_hardening_action_text_not_empty():
    assets = _make_assets()
    actions = optimize_hardening_actions(assets)
    for a in actions:
        assert len(a.hardening_action) > 10
        assert len(a.counterfactual_summary) > 10
