"""LangGraph StateGraph wiring for VAYU-RAKSHA multi-agent system."""
from __future__ import annotations

import logging
from typing import Any

from shadowcast_geo.agents import bhumi, nirnay, sanchar, setu, vayu
from shadowcast_geo.agents.state import CycloneState

logger = logging.getLogger("shadowcast_geo.agents.workflow")


def build_vayu_raksha_graph() -> Any:
    """Build the 5-node StateGraph.

    Flow:
        NIRNAY (entry) → BHUMI + VAYU (parallel) → SETU → SANCHAR → NIRNAY (final)

    Returns:
        Compiled StateGraph or workflow pipeline.
    """
    try:
        from langgraph.graph import END, StateGraph

        workflow = StateGraph(CycloneState)

        # Add all agent nodes
        workflow.add_node("bhumi", bhumi.run)
        workflow.add_node("vayu", vayu.run)
        workflow.add_node("setu", setu.run)
        workflow.add_node("sanchar", sanchar.run)
        workflow.add_node("nirnay", nirnay.run)

        # Entry point: NIRNAY initiates
        workflow.set_entry_point("nirnay")

        # NIRNAY routes to BHUMI and VAYU in parallel
        workflow.add_conditional_edges(
            "nirnay",
            nirnay.route,
            {
                "start_parallel": ["bhumi", "vayu"],
                "finalize": END,
            },
        )

        # BHUMI and VAYU both feed into SETU
        workflow.add_edge("bhumi", "setu")
        workflow.add_edge("vayu", "setu")

        # SETU feeds into SANCHAR
        workflow.add_edge("setu", "sanchar")

        # SANCHAR feeds back to NIRNAY for final synthesis
        workflow.add_edge("sanchar", "nirnay")

        return workflow.compile()
    except ImportError:
        logger.info("LangGraph package not installed locally — using deterministic state graph runner")
        return None


def run_vayu_raksha(scenario_id: str, storm_name: str) -> CycloneState:
    """Entry point: run the full multi-agent pipeline for one scenario.

    Args:
        scenario_id: e.g. "fani-2019"
        storm_name: e.g. "FANI"

    Returns:
        Final CycloneState with all agent outputs.
    """
    initial_state: CycloneState = {
        "scenario_id": scenario_id,
        "storm_name": storm_name,
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

    graph = build_vayu_raksha_graph()
    if graph is not None:
        try:
            return graph.invoke(initial_state)
        except Exception as exc:
            logger.warning("LangGraph invoke raised %s — falling back to deterministic runner", exc)

    # Deterministic StateGraph execution fallback:
    # 1. NIRNAY entry (iteration 1)
    state = nirnay.run(initial_state)
    # 2. Parallel BHUMI + VAYU
    state = bhumi.run(state)
    state = vayu.run(state)
    # 3. SETU (Cascade Graph)
    state = setu.run(state)
    # 4. SANCHAR (Advisories & Triggers)
    state = sanchar.run(state)
    # 5. NIRNAY final synthesis (iteration 2)
    state = nirnay.run(state)
    return state
