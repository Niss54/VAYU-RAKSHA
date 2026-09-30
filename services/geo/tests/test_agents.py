"""Unit tests for VAYU-RAKSHA 5-agent LangGraph system."""
from shadowcast_geo.agents import bhumi, nirnay, sanchar, setu, vayu
from shadowcast_geo.agents.state import CycloneState
from shadowcast_geo.agents.workflow import run_vayu_raksha


def _initial_state() -> CycloneState:
    return {
        "scenario_id": "fani-2019",
        "storm_name": "FANI",
        "terrain_ready": False,
        "infrastructure_nodes": 0,
        "gee_layers_loaded": [],
        "wind_field_computed": False,
        "surge_peak_m": None,
        "rain_extreme_sites": 0,
        "intensity_kt": None,
        "mosdac_intensity_kt": None,
        "ri_risk": False,
        "cascade_ready": False,
        "cascade_chains_count": 0,
        "population_at_cascade_risk": 0.0,
        "top_action": None,
        "hardening_actions": [],
        "advisory_dispatched": False,
        "advisory_languages": [],
        "insurance_trigger_ready": False,
        "final_brief": None,
        "action_queue": [],
        "errors": [],
        "iteration_count": 0,
    }


def test_bhumi_run():
    state = _initial_state()
    res = bhumi.run(state)
    assert res["terrain_ready"] is True
    assert res["infrastructure_nodes"] >= 3000
    assert "COPERNICUS/DEM/GLO30" in res["gee_layers_loaded"]


def test_vayu_run():
    state = _initial_state()
    res = vayu.run(state)
    assert res["wind_field_computed"] is True
    assert res["surge_peak_m"] is not None and res["surge_peak_m"] > 0
    assert res["intensity_kt"] is not None and res["intensity_kt"] > 0


def test_setu_run():
    state = _initial_state()
    res = setu.run(state)
    assert res["cascade_ready"] is True
    assert res["cascade_chains_count"] > 0
    assert len(res["hardening_actions"]) >= 1
    assert res["population_at_cascade_risk"] > 0


def test_sanchar_run():
    state = _initial_state()
    res = sanchar.run(state)
    assert res["advisory_dispatched"] is True
    assert "Odia" in res["advisory_languages"]
    assert "Hindi" in res["advisory_languages"]
    assert res["insurance_trigger_ready"] is True


def test_nirnay_route_and_synthesis():
    state = _initial_state()
    assert nirnay.route(state) == "start_parallel"
    state = nirnay.run(state)  # iteration 1
    state["iteration_count"] = 2
    assert nirnay.route(state) == "finalize"
    final = nirnay.run(state)  # iteration 2
    assert final["final_brief"] is not None
    assert "VAYU-RAKSHA" in final["final_brief"]


def test_run_vayu_raksha_pipeline():
    result = run_vayu_raksha("fani-2019", "FANI")
    assert result["terrain_ready"] is True
    assert result["wind_field_computed"] is True
    assert result["cascade_ready"] is True
    assert result["advisory_dispatched"] is True
    assert result["final_brief"] is not None
    assert len(result["action_queue"]) > 0
