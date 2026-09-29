"""VAYU-RAKSHA 5-Agent LangGraph Workflow Orchestrator.

Wires the directed StateGraph connecting BHUMI, VAYU, SETU, SANCHAR, and NIRNAY.
"""

from typing import Any, Dict, Optional
import time

from vayu_raksha.agents.bhumi_earth import BhumiEarthAgent
from vayu_raksha.agents.nirnay_supervisor import NirnaySupervisorAgent
from vayu_raksha.agents.sanchar_comms import SancharCommsAgent
from vayu_raksha.agents.setu_cascade import SetuCascadeAgent
from vayu_raksha.agents.vayu_atmosphere import VayuAtmosphereAgent
from vayu_raksha.data.mock_scenarios import (
    get_cyclone_dana_metadata,
    get_cyclone_fani_metadata,
    get_odisha_coastal_infrastructure,
)
from vayu_raksha.graph.state import CycloneState


class VayuRakshaWorkflow:
    """StateGraph orchestrator managing the 5-agent pipeline."""

    def __init__(self) -> None:
        self.bhumi = BhumiEarthAgent()
        self.vayu = VayuAtmosphereAgent()
        self.setu = SetuCascadeAgent()
        self.sanchar = SancharCommsAgent()
        self.nirnay = NirnaySupervisorAgent()

    def create_initial_state(self, scenario_type: str = "fani") -> CycloneState:
        """Initializes state with Odisha infrastructure and chosen cyclone trajectory."""
        nodes, edges = get_odisha_coastal_infrastructure()

        if scenario_type.lower() == "dana":
            meta = get_cyclone_dana_metadata()
            scenario_id = "dana-2024"
        else:
            meta = get_cyclone_fani_metadata()
            scenario_id = "fani-2019"

        initial_state: CycloneState = {
            "scenario_id": scenario_id,
            "cyclone_metadata": meta,
            "earth_data": {
                "elevation_raster_resolution_m": 30,
                "sar_satellite": "ISRO RISAT-1A + Sentinel-1 SAR",
                "sar_cloud_penetration_status": "PENDING INGESTION",
                "flood_inundation_zones": [],
                "max_inundation_depth_m": 0.0,
                "water_extent_sqkm": 0.0,
                "worldpop_coastal_density_raster": "WorldPop 100m",
                "high_susceptibility_area_sqkm": 0.0,
            },
            "atmospheric_data": {
                "wind_field_model": "Holland (1980)",
                "storm_surge_crest_m": 0.0,
                "surge_corridor_coast_extent_km": 0.0,
                "cumulative_72h_rainfall_mm": 0.0,
                "r_cliper_rain_peak_mm_hr": 0.0,
                "wind_radii_34kt_nm": 0.0,
                "wind_radii_50kt_nm": 0.0,
                "wind_radii_64kt_nm": 0.0,
            },
            "infrastructure_nodes": nodes,
            "dependency_edges": edges,
            "evacuation_corridors": [],
            "ranked_action_queue": [],
            "advisories": [],
            "parametric_insurance": {
                "policy_id": "PARAMETRIC_POL_ODISHA_2026",
                "insured_entity": "Odisha State Disaster Management Authority",
                "wind_threshold_kmh": 89.0,
                "flood_extent_threshold_pct": 30.0,
                "observed_wind_kmh": 0.0,
                "observed_flood_pct": 0.0,
                "satellite_evidence_sources": [],
                "trigger_status": "MONITORING",
                "payout_liquidity_inr_crores": 0.0,
                "payout_smart_contract_hash": None,
                "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
            "agent_telemetry": {},
            "audit_log": [
                {
                    "event": "PIPELINE_INITIALIZED",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                    "details": f"Scenario {scenario_id} loaded with {len(nodes)} assets and {len(edges)} links.",
                }
            ],
            "final_situation_summary": "Pipeline initialized. Ready for agent assessment.",
        }
        return initial_state

    def execute_pipeline(self, state: CycloneState) -> CycloneState:
        """Runs the 5-Agent pipeline:

        [BHUMI + VAYU] in parallel -> SETU -> SANCHAR -> NIRNAY (Supervisor).
        """
        audit = list(state.get("audit_log", []))
        telemetry = dict(state.get("agent_telemetry", {}))

        # 1. Step 1: BHUMI (Earth Intelligence)
        bhumi_out = self.bhumi.run(state)
        state["earth_data"] = bhumi_out["earth_data"]
        telemetry["BHUMI"] = bhumi_out["telemetry"]
        audit.append({
            "event": "AGENT_STEP_COMPLETED",
            "agent": "BHUMI",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "details": bhumi_out["telemetry"]["last_thought"],
        })

        # 2. Step 2: VAYU (Atmospheric Intelligence)
        vayu_out = self.vayu.run(state)
        state["atmospheric_data"] = vayu_out["atmospheric_data"]
        telemetry["VAYU"] = vayu_out["telemetry"]
        audit.append({
            "event": "AGENT_STEP_COMPLETED",
            "agent": "VAYU",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "details": vayu_out["telemetry"]["last_thought"],
        })

        # 3. Step 3: SETU (Infrastructure Cascade Agent)
        setu_out = self.setu.run(state)
        state["infrastructure_nodes"] = setu_out["infrastructure_nodes"]
        state["evacuation_corridors"] = setu_out["evacuation_corridors"]
        state["direct_hazard_failures"] = setu_out["direct_hazard_failures"]
        telemetry["SETU"] = setu_out["telemetry"]
        audit.append({
            "event": "AGENT_STEP_COMPLETED",
            "agent": "SETU",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "details": setu_out["telemetry"]["last_thought"],
        })

        # 4. Step 4: SANCHAR (Communication & Insurance Agent)
        sanchar_out = self.sanchar.run(state)
        state["advisories"] = sanchar_out["advisories"]
        state["parametric_insurance"] = sanchar_out["parametric_insurance"]
        telemetry["SANCHAR"] = sanchar_out["telemetry"]
        audit.append({
            "event": "AGENT_STEP_COMPLETED",
            "agent": "SANCHAR",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "details": sanchar_out["telemetry"]["last_thought"],
        })

        # 5. Step 5: NIRNAY (Supervisor & Counterfactual Optimizer)
        nirnay_out = self.nirnay.run_optimization(state)
        state["ranked_action_queue"] = nirnay_out["ranked_action_queue"]
        state["final_situation_summary"] = nirnay_out["final_situation_summary"]
        telemetry["NIRNAY"] = nirnay_out["telemetry"]
        audit.append({
            "event": "AGENT_STEP_COMPLETED",
            "agent": "NIRNAY",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "details": nirnay_out["telemetry"]["last_thought"],
        })

        state["agent_telemetry"] = telemetry
        state["audit_log"] = audit
        return state
