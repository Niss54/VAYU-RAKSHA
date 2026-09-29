"""VAYU-RAKSHA Infrastructure Cascade Failure Graph Engine.

Implements the 5-layer directed interdependency network G = (V, E)
and probabilistic cascade propagation algorithm.
"""

from typing import Any, Dict, List, Literal, Optional, Set, Tuple
import math
import networkx as nx

from vayu_raksha.graph.state import (
    CycloneMetadata,
    DependencyEdge,
    EvacuationCorridor,
    InfrastructureNode,
    TerrainAndFloodData,
)


class CascadeGraphEngine:
    """NetworkX-powered multi-layer infrastructure interdependency cascade engine."""

    def __init__(self) -> None:
        self.graph = nx.DiGraph()

    def build_graph(
        self,
        nodes: List[InfrastructureNode],
        edges: List[DependencyEdge],
    ) -> nx.DiGraph:
        """Constructs the directed infrastructure network."""
        self.graph.clear()

        for node in nodes:
            self.graph.add_node(
                node["id"],
                name=node["name"],
                type=node["type"],
                tier=node["tier"],
                lat=node["lat"],
                lon=node["lon"],
                district=node.get("district", "Puri"),
                elevation_m=node.get("elevation_m", 4.0),
                capacity=node.get("capacity", "Standard"),
                backup_power_hrs=node.get("backup_power_hrs", 8.0),
                population_served=node.get("population_served", 10000),
                status=node.get("status", "OPERATIONAL"),
                failure_probability=node.get("failure_probability", 0.0),
                cascade_depth=node.get("cascade_depth", 0),
                direct_hazard_cause=node.get("direct_hazard_cause", None),
                cascade_predecessor_id=node.get("cascade_predecessor_id", None),
                plain_language_reasons=list(node.get("plain_language_reasons", [])),
            )

        for edge in edges:
            self.graph.add_edge(
                edge["source_id"],
                edge["target_id"],
                dependency_type=edge["dependency_type"],
                weight=edge.get("weight", 1.0),
                description=edge.get("description", ""),
            )

        return self.graph

    def simulate_cascade(
        self,
        direct_hazard_failures: Dict[str, Dict[str, Any]],
        hardened_nodes: Optional[Set[str]] = None,
        max_depth: int = 3,
    ) -> Tuple[List[InfrastructureNode], Dict[str, Any]]:
        """Propagates cascade failures across the dependency graph.

        Args:
            direct_hazard_failures: Mapping of node_id -> {
                'probability': float,
                'hazard_cause': str,
                'reasons': List[str]
            }
            hardened_nodes: Set of node_ids that have been proactively isolated
              or reinforced.
            max_depth: Maximum hops for cascade propagation.

        Returns:
            Tuple of updated nodes list and aggregate cascade statistics.
        """
        if hardened_nodes is None:
            hardened_nodes = set()

        # Reset all nodes to base state or hardened
        for node_id in self.graph.nodes:
            attrs = self.graph.nodes[node_id]
            if node_id in hardened_nodes:
                attrs["status"] = "HARDENED"
                attrs["failure_probability"] = 0.05
                attrs["cascade_depth"] = 0
                attrs["direct_hazard_cause"] = None
                attrs["cascade_predecessor_id"] = None
                attrs["plain_language_reasons"] = ["Hardened pre-landfall: Isolated or backed up."]
            else:
                attrs["status"] = "OPERATIONAL"
                attrs["failure_probability"] = 0.0
                attrs["cascade_depth"] = 0
                attrs["direct_hazard_cause"] = None
                attrs["cascade_predecessor_id"] = None
                attrs["plain_language_reasons"] = []

        # Step 1: Apply direct environmental hazards (wind, surge, pluvial flood)
        failed_frontier: Set[str] = set()

        for node_id, hazard in direct_hazard_failures.items():
            if node_id in hardened_nodes or node_id not in self.graph:
                continue

            prob = float(hazard.get("probability", 0.0))
            if prob >= 0.65:
                attrs = self.graph.nodes[node_id]
                attrs["status"] = "FAILED"
                attrs["failure_probability"] = min(1.0, prob)
                attrs["cascade_depth"] = 0
                attrs["direct_hazard_cause"] = hazard.get("hazard_cause", "Severe Storm Hazard")
                attrs["plain_language_reasons"].extend(hazard.get("reasons", []))
                failed_frontier.add(node_id)
            elif prob >= 0.35:
                attrs = self.graph.nodes[node_id]
                attrs["status"] = "AT_RISK"
                attrs["failure_probability"] = prob
                attrs["plain_language_reasons"].extend(hazard.get("reasons", []))

        # Step 2: Multi-hop cascade propagation
        current_depth = 1
        visited_in_cascade: Set[str] = set(failed_frontier)

        while failed_frontier and current_depth <= max_depth:
            next_frontier: Set[str] = set()

            for source_id in failed_frontier:
                source_attrs = self.graph.nodes[source_id]

                # Outward edges represent dependent downstream assets
                # e.g., Substation S1 -> Hospital H2 (Hospital depends on Substation)
                for _, target_id, edge_data in self.graph.out_edges(source_id, data=True):
                    if target_id in hardened_nodes:
                        continue

                    target_attrs = self.graph.nodes[target_id]
                    dep_type = edge_data.get("dependency_type", "power")
                    edge_weight = float(edge_data.get("weight", 0.9))

                    # Calculate downstream failure probability attenuation
                    parent_prob = float(source_attrs.get("failure_probability", 1.0))
                    cascade_prob = parent_prob * edge_weight

                    # Backup mitigations (e.g. hospital has diesel generator)
                    backup_hours = float(target_attrs.get("backup_power_hrs", 8.0))
                    if dep_type == "power" and backup_hours > 0:
                        # Backup buys time, reduces immediate probability
                        mitigation_factor = max(0.25, 1.0 - (backup_hours / 24.0))
                        cascade_prob *= mitigation_factor

                    if cascade_prob > target_attrs.get("failure_probability", 0.0):
                        target_attrs["failure_probability"] = round(min(1.0, cascade_prob), 3)

                    if cascade_prob >= 0.55:
                        if target_attrs["status"] != "FAILED":
                            target_attrs["status"] = "FAILED"
                            target_attrs["cascade_depth"] = current_depth
                            target_attrs["cascade_predecessor_id"] = source_id
                            reason = (
                                f"Cascade failure (Hop {current_depth}): Lost {dep_type} supply "
                                f"from upstream {source_attrs.get('name', source_id)}"
                            )
                            if reason not in target_attrs["plain_language_reasons"]:
                                target_attrs["plain_language_reasons"].append(reason)

                            if target_id not in visited_in_cascade:
                                visited_in_cascade.add(target_id)
                                next_frontier.add(target_id)
                    elif cascade_prob >= 0.25:
                        if target_attrs["status"] == "OPERATIONAL":
                            target_attrs["status"] = "AT_RISK"
                            target_attrs["cascade_depth"] = current_depth
                            warning = (
                                f"Cascade warning: Upstream {dep_type} link from "
                                f"{source_attrs.get('name', source_id)} severed/degraded"
                            )
                            if warning not in target_attrs["plain_language_reasons"]:
                                target_attrs["plain_language_reasons"].append(warning)

            failed_frontier = next_frontier
            current_depth += 1

        # Step 3: Compute aggregate metrics
        total_pop_affected = 0
        nodes_failed_count = 0
        nodes_at_risk_count = 0
        hospitals_compromised = 0
        shelters_compromised = 0
        substations_offline = 0
        updated_nodes: List[InfrastructureNode] = []

        for node_id, attrs in self.graph.nodes(data=True):
            node_dict: InfrastructureNode = {
                "id": node_id,
                "name": attrs["name"],
                "type": attrs["type"],
                "tier": attrs["tier"],
                "lat": float(attrs["lat"]),
                "lon": float(attrs["lon"]),
                "district": attrs["district"],
                "elevation_m": float(attrs["elevation_m"]),
                "capacity": str(attrs["capacity"]),
                "backup_power_hrs": float(attrs["backup_power_hrs"]),
                "population_served": int(attrs["population_served"]),
                "status": attrs["status"],
                "failure_probability": float(attrs["failure_probability"]),
                "cascade_depth": int(attrs["cascade_depth"]),
                "direct_hazard_cause": attrs["direct_hazard_cause"],
                "cascade_predecessor_id": attrs["cascade_predecessor_id"],
                "plain_language_reasons": list(attrs["plain_language_reasons"]),
            }
            updated_nodes.append(node_dict)

            if attrs["status"] == "FAILED":
                nodes_failed_count += 1
                total_pop_affected += int(attrs["population_served"])
                if attrs["type"] == "hospital":
                    hospitals_compromised += 1
                elif attrs["type"] == "shelter":
                    shelters_compromised += 1
                elif attrs["type"] == "substation":
                    substations_offline += 1
            elif attrs["status"] == "AT_RISK":
                nodes_at_risk_count += 1
                total_pop_affected += int(attrs["population_served"] * 0.4)

        metrics = {
            "total_nodes": len(self.graph.nodes),
            "nodes_failed": nodes_failed_count,
            "nodes_at_risk": nodes_at_risk_count,
            "hospitals_compromised": hospitals_compromised,
            "shelters_compromised": shelters_compromised,
            "substations_offline": substations_offline,
            "total_population_affected": total_pop_affected,
            "cascade_max_depth_reached": min(max_depth, current_depth - 1),
        }

        return updated_nodes, metrics
