"""Test suite for VAYU-RAKSHA 5-Agent Pipeline."""

import sys
from pathlib import Path

# Add src to python path
src_dir = Path(__file__).resolve().parent.parent / "services" / "geo" / "src"
sys.path.insert(0, str(src_dir))

from vayu_raksha.graph.workflow import VayuRakshaWorkflow


def test_pipeline_fani():
    workflow = VayuRakshaWorkflow()
    state = workflow.create_initial_state("fani")

    assert state["cyclone_metadata"]["storm_name"] == "Fani"
    assert len(state["infrastructure_nodes"]) > 0
    assert len(state["dependency_edges"]) > 0

    result = workflow.execute_pipeline(state)

    # 1. Verify Atmospheric & Earth data
    assert result["atmospheric_data"]["storm_surge_crest_m"] > 0.0
    assert result["earth_data"]["water_extent_sqkm"] > 0.0

    # 2. Verify SETU cascade evaluation
    assert "SETU" in result["agent_telemetry"]
    assert len(result["infrastructure_nodes"]) == len(state["infrastructure_nodes"])

    # 3. Verify SANCHAR multilingual notices & insurance
    assert len(result["advisories"]) == 6
    assert result["parametric_insurance"]["trigger_status"] in ["TRIGGER_DISPATCHED", "MONITORING"]
    assert result["parametric_insurance"]["payout_liquidity_inr_crores"] >= 0.0

    # 4. Verify NIRNAY counterfactual ranking
    assert len(result["ranked_action_queue"]) > 0
    top_action = result["ranked_action_queue"][0]
    assert top_action["roi_score"] > 0
    assert top_action["delta_population_protected"] > 0

    print("=== TEST PASSED SUCCESSFULLY ===")
    print(f"Top Action: {top_action['action_title']}")
    print(f"ROI Score: {top_action['roi_score']}")
    print(f"Protected Population: {top_action['delta_population_protected']:,}")
    print(f"Parametric Payout: Rs {result['parametric_insurance']['payout_liquidity_inr_crores']} Cr")


if __name__ == "__main__":
    test_pipeline_fani()
