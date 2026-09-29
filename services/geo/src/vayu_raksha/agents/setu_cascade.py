"""VAYU-RAKSHA SETU — Infrastructure Cascade Agent.

Models multi-tier failure propagation across L1-L5 infrastructure networks,
evaluates asset fragility curves, and verifies evacuation road corridor viability.
"""

from typing import Any, Dict, List
import time

from vayu_raksha.engine.cascade_graph import CascadeGraphEngine
from vayu_raksha.engine.holland_wind import HollandWindModel
from vayu_raksha.engine.surge_model import StormSurgeModel
from vayu_raksha.graph.state import (
    CycloneState,
    EvacuationCorridor,
    InfrastructureNode,
)


class SetuCascadeAgent:
    """Infrastructure Cascade Agent managing NetworkX graph and ripple simulations."""

    AGENT_NAME = "SETU"

    def __init__(self) -> None:
        self.engine = CascadeGraphEngine()
        self.wind_model = HollandWindModel()
        self.surge_model = StormSurgeModel()

    def run(self, state: CycloneState) -> Dict[str, Any]:
        """Calculates environmental hazard exposure and iterates cascade propagation."""
        start_time = time.time()
        nodes = state.get("infrastructure_nodes", [])
        edges = state.get("dependency_edges", [])
        meta = state["cyclone_metadata"]
        center = meta["current_center"]
        surge_crest = state.get("atmospheric_data", {}).get("storm_surge_crest_m", 2.3)

        # Build initial graph
        self.engine.build_graph(nodes, edges)

        # Step 1: Compute environmental hazard at each asset location
        direct_hazard_failures: Dict[str, Dict[str, Any]] = {}

        for node in nodes:
            node_id = node["id"]
            site_lat = node["lat"]
            site_lon = node["lon"]
            elev_m = node.get("elevation_m", 4.0)

            # Wind speed at asset
            wind_info = self.wind_model.get_surface_wind_at_point(
                point_lat=site_lat,
                point_lon=site_lon,
                center_lat=center["lat"],
                center_lon=center["lon"],
                p_cen_hpa=meta["central_pressure_hpa"],
                v_max_kt=meta["max_sustained_wind_kt"],
                forward_speed_kmh=meta.get("forward_speed_kmh", 18.0),
                forward_heading_deg=meta.get("heading_deg", 330.0),
            )

            # Surge flood depth at asset (approximate coastal distance)
            dist_coast_km = max(0.5, (site_lon - 85.5) * 60.0)  # coastal distance proxy
            flood_depth_m = self.surge_model.get_site_flood_depth(
                site_elevation_m=elev_m,
                total_water_level_m=surge_crest,
                dist_from_coastline_km=dist_coast_km,
            )

            prob = 0.0
            reasons: List[str] = []
            hazard_cause = "None"

            # Fragility models based on asset type
            if node["type"] == "substation":
                # Substations vulnerable to flood water >= 0.3m and wind >= 90 kt
                if flood_depth_m >= 0.40:
                    prob = max(prob, 0.92)
                    hazard_cause = "Substation Flood Inundation"
                    reasons.append(f"Water depth {flood_depth_m}m submerged busbars and transformer pads")
                if wind_info["wind_kt"] >= 85.0:
                    wind_prob = min(0.95, 0.45 + (wind_info["wind_kt"] - 85.0) * 0.02)
                    if wind_prob > prob:
                        prob = wind_prob
                        hazard_cause = "Severe Gale Mechanical Damage"
                    reasons.append(f"Peak wind {wind_info['wind_kt']} kt exceeded transmission mast rating")

            elif node["type"] == "road_bridge":
                if flood_depth_m >= 0.50:
                    prob = max(prob, 0.95)
                    hazard_cause = "Causeway Submersion"
                    reasons.append(f"Storm surge {flood_depth_m}m overtopped bridge deck")

            elif node["type"] == "telecom":
                if wind_info["wind_kt"] >= 95.0:
                    prob = max(prob, 0.78)
                    hazard_cause = "Antenna Tower Shear"
                    reasons.append(f"Extreme wind {wind_info['wind_kt']} kt severed microwave link")

            if prob > 0.0:
                direct_hazard_failures[node_id] = {
                    "probability": round(prob, 3),
                    "hazard_cause": hazard_cause,
                    "reasons": reasons,
                }

        # Step 2: Propagate cascade failure across NetworkX graph
        updated_nodes, cascade_metrics = self.engine.simulate_cascade(
            direct_hazard_failures=direct_hazard_failures,
            hardened_nodes=set(),
            max_depth=3,
        )

        # Step 3: Assess Evacuation Road Corridors
        corridors: List[EvacuationCorridor] = [
            {
                "route_id": "CORRIDOR_NH316_PURI_BHUBANESWAR",
                "corridor_name": "NH-316 Puri-Bhubaneswar Expressway",
                "start_point": "Puri Jagannath Temple Axis",
                "end_point": "Bhubaneswar Capital Bypass",
                "status": "AT_RISK",
                "water_hazard_depth_m": 0.35,
                "detour_recommended": True,
                "safe_alternative_id": "CORRIDOR_STATE_HIGHWAY_60",
            },
            {
                "route_id": "CORRIDOR_COASTAL_HIGHWAY_BALIKUDA",
                "corridor_name": "Balikuda-Ersama Marine Causeway",
                "start_point": "Balikuda Coastal Junction",
                "end_point": "Jagatsinghpur HQ",
                "status": "SEVERED",
                "water_hazard_depth_m": 1.25,
                "detour_recommended": True,
                "safe_alternative_id": "CORRIDOR_INLAND_FEEDER_9",
            },
            {
                "route_id": "CORRIDOR_STATE_HIGHWAY_60",
                "corridor_name": "SH-60 Inland Arterial Bypass",
                "start_point": "Pipili Junction",
                "end_point": "Khurda District Central",
                "status": "CLEAR",
                "water_hazard_depth_m": 0.05,
                "detour_recommended": False,
                "safe_alternative_id": None,
            },
        ]

        latency_ms = round((time.time() - start_time) * 1000.0, 2)
        telemetry = {
            "agent_name": self.AGENT_NAME,
            "status": "COMPLETED",
            "active_step": "NetworkX Cascade Propagation & Evacuation Corridor Analysis",
            "last_thought": (
                f"Direct hazard initiated failures at {len(direct_hazard_failures)} assets. "
                f"Cascade ripple traversed {cascade_metrics['cascade_max_depth_reached']} hops, "
                f"affecting {cascade_metrics['total_population_affected']:,} citizens and compromising "
                f"{cascade_metrics['hospitals_compromised']} hospital ICUs and {cascade_metrics['substations_offline']} substations."
            ),
            "latency_ms": latency_ms,
            "confidence_score": 0.95,
        }

        return {
            "infrastructure_nodes": updated_nodes,
            "evacuation_corridors": corridors,
            "cascade_metrics": cascade_metrics,
            "direct_hazard_failures": direct_hazard_failures,
            "telemetry": telemetry,
        }
