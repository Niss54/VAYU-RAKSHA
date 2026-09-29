"""VAYU-RAKSHA Counterfactual Pre-Landfall Scenario Optimizer.

Evaluates candidate municipal interventions (e.g. de-energizing coastal substations,
pre-positioning fuel at trauma centers) and ranks them by (delta_population_protected / cost_proxy).
"""

from typing import Any, Dict, List, Set, Tuple
from vayu_raksha.engine.cascade_graph import CascadeGraphEngine
from vayu_raksha.graph.state import CounterfactualAction, DependencyEdge, InfrastructureNode


class CounterfactualOptimizer:
    """Pre-landfall decision optimization engine."""

    def __init__(self, cascade_engine: CascadeGraphEngine) -> None:
        self.engine = cascade_engine

    def evaluate_candidates(
        self,
        nodes: List[InfrastructureNode],
        edges: List[DependencyEdge],
        direct_hazard_failures: Dict[str, Dict[str, Any]],
        candidate_interventions: List[Dict[str, Any]],
    ) -> Tuple[List[CounterfactualAction], Dict[str, Any]]:
        """Compares baseline cascade failure against hardened counterfactuals.

        Args:
            nodes: Infrastructure asset list.
            edges: Dependency links.
            direct_hazard_failures: Environmental hazard failure mapping.
            candidate_interventions: List of prospective pre-landfall actions.

        Returns:
            Ranked action queue sorted by ROI score and priority.
        """
        # Rebuild graph
        self.engine.build_graph(nodes, edges)

        # Baseline run (no interventions)
        _, baseline_metrics = self.engine.simulate_cascade(
            direct_hazard_failures,
            hardened_nodes=set(),
        )
        baseline_affected_pop = baseline_metrics["total_population_affected"]
        baseline_failed_nodes = baseline_metrics["nodes_failed"]

        ranked_actions: List[CounterfactualAction] = []

        for candidate in candidate_interventions:
            action_id = candidate["action_id"]
            target_node_ids = set(candidate.get("target_node_ids", []))
            cost_proxy = float(candidate.get("cost_proxy", 20.0))

            # Simulate counterfactual world where target nodes are hardened/isolated
            _, counterfactual_metrics = self.engine.simulate_cascade(
                direct_hazard_failures,
                hardened_nodes=target_node_ids,
            )

            sim_affected_pop = counterfactual_metrics["total_population_affected"]
            sim_failed_nodes = counterfactual_metrics["nodes_failed"]

            delta_pop = max(0, baseline_affected_pop - sim_affected_pop)
            nodes_saved = max(0, baseline_failed_nodes - sim_failed_nodes)

            # Avoid division by zero
            safe_cost = max(1.0, cost_proxy)
            roi_score = round(delta_pop / safe_cost, 2)

            # Determine priority tier based on lives/population protected
            priority = candidate.get("priority", "MED")
            if delta_pop >= 50000 or any("hospital" in n.lower() for n in target_node_ids):
                priority = "CRITICAL"
            elif delta_pop >= 20000:
                priority = "HIGH"

            action_obj: CounterfactualAction = {
                "action_id": action_id,
                "priority": priority,
                "action_title": candidate["action_title"],
                "target_node_ids": list(target_node_ids),
                "description": candidate["description"],
                "window_deadline": candidate.get("window_deadline", "T-36h"),
                "cost_proxy": cost_proxy,
                "delta_population_protected": delta_pop,
                "roi_score": roi_score,
                "approved_by_officer": candidate.get("approved_by_officer", False),
                "cascade_nodes_saved": nodes_saved,
            }
            ranked_actions.append(action_obj)

        # Sort by priority rank (CRITICAL -> HIGH -> MED -> LOW) then by roi_score descending
        priority_weights = {"CRITICAL": 4, "HIGH": 3, "MED": 2, "LOW": 1}
        ranked_actions.sort(
            key=lambda x: (priority_weights.get(x["priority"], 1), x["roi_score"]),
            reverse=True,
        )

        comparison_summary = {
            "baseline_population_at_risk": baseline_affected_pop,
            "baseline_failed_nodes": baseline_failed_nodes,
            "total_candidate_scenarios_evaluated": len(candidate_interventions),
            "top_recommended_action": ranked_actions[0]["action_title"] if ranked_actions else None,
            "max_possible_population_salvage": max(
                (a["delta_population_protected"] for a in ranked_actions), default=0
            ),
        }

        return ranked_actions, comparison_summary
