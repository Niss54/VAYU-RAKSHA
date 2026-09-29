"""VAYU-RAKSHA NIRNAY — Supervisor Agent & Counterfactual Optimizer.

Orchestrator for the 5-agent LangGraph system, evaluating counterfactual pre-landfall
interventions, optimizing action queues, and synthesizing final municipal directives.
"""

from typing import Any, Dict, List
import time

from vayu_raksha.engine.cascade_graph import CascadeGraphEngine
from vayu_raksha.engine.counterfactual import CounterfactualOptimizer
from vayu_raksha.graph.state import (
    CounterfactualAction,
    CycloneState,
)


class NirnaySupervisorAgent:
    """Supreme Orchestrator & Decision Optimization Agent."""

    AGENT_NAME = "NIRNAY"

    def __init__(self) -> None:
        self.cascade_engine = CascadeGraphEngine()
        self.optimizer = CounterfactualOptimizer(self.cascade_engine)

    def run_optimization(self, state: CycloneState) -> Dict[str, Any]:
        """Runs counterfactual scenario comparisons and finalizes action queue."""
        start_time = time.time()
        nodes = state.get("infrastructure_nodes", [])
        edges = state.get("dependency_edges", [])
        direct_hazard_failures = state.get("direct_hazard_failures", {})

        # Candidate pre-landfall interventions to evaluate counterfactually
        candidates: List[Dict[str, Any]] = [
            {
                "action_id": "ACT_DE_ENERGIZE_COASTAL_SUBSTATIONS",
                "action_title": "De-energize coastal 220kV substations (S-7, S-12, S-19)",
                "target_node_ids": ["S_PURI_220KV", "S_BALIKUDA_132KV", "S_PARADIP_220KV"],
                "description": (
                    "Controlled pre-landfall de-energization prevents saltwater arc-explosions "
                    "and protects 14 downstream transmission lines, preserving transformer cores."
                ),
                "window_deadline": "T-36h before landfall",
                "cost_proxy": 18.0,
                "approved_by_officer": True,
            },
            {
                "action_id": "ACT_PREPOSITION_HOSPITAL_FUEL",
                "action_title": "Pre-position 15,000L fuel tankers at Trauma Centers (H-3, H-8)",
                "target_node_ids": ["H_PURI_DISTRICT", "H_JAGATSINGHPUR_TRAUMA"],
                "description": (
                    "Secures 72 hours of uninterrupted diesel generator power for 2 ICUs, "
                    "48 ventilator beds, neonatal units, and cold-chain vaccine storages."
                ),
                "window_deadline": "T-48h before landfall",
                "cost_proxy": 12.0,
                "approved_by_officer": True,
            },
            {
                "action_id": "ACT_CLOSE_COASTAL_BRIDGE_RB22",
                "action_title": "Close Coastal Highway Bridge RB-22 & Divert to Corridor-4",
                "target_node_ids": ["RB_BALIKUDA_BRIDGE"],
                "description": (
                    "Surge height projected to reach 2.2m overtopping bridge deck at T-6h. "
                    "Pre-emptive barricading prevents civilian stranding and vehicular submergence."
                ),
                "window_deadline": "T-12h before landfall",
                "cost_proxy": 5.0,
                "approved_by_officer": False,
            },
            {
                "action_id": "ACT_BACKUP_TELECOM_TOWERS",
                "action_title": "Activate diesel generators on Telecom Towers (TC-4, TC-11)",
                "target_node_ids": ["TC_PURI_TOWER", "TC_PARADIP_VHF"],
                "description": (
                    "Maintains vital cellular and NDRF emergency VHF radio coverage during and "
                    "after storm passage across coastal lowlands."
                ),
                "window_deadline": "T-24h before landfall",
                "cost_proxy": 8.0,
                "approved_by_officer": False,
            },
            {
                "action_id": "ACT_PREFILL_WATER_RESERVOIRS",
                "action_title": "Pre-fill municipal potable water overhead tanks (WP-2, WP-5)",
                "target_node_ids": ["WP_PURI_HEADWORKS"],
                "description": (
                    "Pumping stations will lose power post-landfall. Pre-filling overhead reserves "
                    "guarantees 4 days of gravity-fed drinking water for 120,000 residents."
                ),
                "window_deadline": "T-48h before landfall",
                "cost_proxy": 7.0,
                "approved_by_officer": False,
            },
        ]

        # Run counterfactual permutations
        ranked_queue, summary = self.optimizer.evaluate_candidates(
            nodes=nodes,
            edges=edges,
            direct_hazard_failures=direct_hazard_failures,
            candidate_interventions=candidates,
        )

        # Synthesize Collector Situation Summary
        meta = state["cyclone_metadata"]
        lead_h = meta["lead_time_hours"]
        wind_kmh = meta["max_sustained_wind_kmh"]
        surge_m = state.get("atmospheric_data", {}).get("storm_surge_crest_m", 2.3)

        situation_report = (
            f"VAYU-RAKSHA SITUATION REPORT: Cyclone '{meta['storm_name']}' is at T-{lead_h:.0f}h to landfall. "
            f"Modeled intensity: {wind_kmh:.0f} km/h core winds with a {surge_m}m storm surge crest. "
            f"Without proactive intervention, cascade failure propagation will sever {summary['baseline_failed_nodes']} "
            f"critical nodes, jeopardizing {summary['baseline_population_at_risk']:,} citizens. "
            f"Top recommended pre-landfall action: '{summary['top_recommended_action']}' "
            f"(ROI: {ranked_queue[0]['roi_score'] if ranked_queue else 0:.1f}, "
            f"salvaging up to {summary['max_possible_population_salvage']:,} population coverage)."
        )

        latency_ms = round((time.time() - start_time) * 1000.0, 2)
        telemetry = {
            "agent_name": self.AGENT_NAME,
            "status": "COMPLETED",
            "active_step": "Counterfactual Optimization & Final Directive Synthesis Finished",
            "last_thought": (
                f"Evaluated {len(candidates)} counterfactual scenarios. Ranked {len(ranked_queue)} "
                f"pre-landfall actions. Max potential population protected: {summary['max_possible_population_salvage']:,}. "
                "District Collector Action Queue finalized."
            ),
            "latency_ms": latency_ms,
            "confidence_score": 0.99,
        }

        return {
            "ranked_action_queue": ranked_queue,
            "counterfactual_summary": summary,
            "final_situation_summary": situation_report,
            "telemetry": telemetry,
        }
