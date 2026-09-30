"""Infrastructure cascade failure engine.

Models the coastal district as a directed interdependency graph G = (V, E) where
nodes are critical assets and edges are dependency relationships. When an asset
fails (P(outage) > threshold), downstream dependents receive cascaded failure
probability up to MAX_CASCADE_HOPS hops away.

This is VAYU-RAKSHA's primary differentiator over ShadowCast.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import networkx as nx
import numpy as np
import pandas as pd

# Cascade hop limit: how many dependency steps to propagate
MAX_CASCADE_HOPS = 3

# Dependency rules: (upstream_kind, downstream_kind) → dependency_strength [0-1]
# A strength of 0.9 means: if upstream fails, downstream receives 0.9 * P(upstream failure)
DEPENDENCY_RULES: dict[tuple[str, str], float] = {
    ("substation", "hospital"): 0.90,  # hospitals depend on grid power
    ("substation", "health_centre"): 0.85,
    ("substation", "water_works"): 0.80,  # pumping requires electricity
    ("substation", "police"): 0.60,
    ("substation", "fire_station"): 0.60,
    ("power_plant", "substation"): 0.95,  # substations fed by power plants
    ("water_works", "hospital"): 0.70,  # hospitals need water supply
    ("water_works", "health_centre"): 0.65,
    ("hospital", "clinic"): 0.30,  # tertiary overflow
    ("cyclone_shelter", "school"): 0.20,  # shelters repurpose schools
}

# How far two assets must be (km) for a dependency edge to be drawn
MAX_DEPENDENCY_KM: dict[tuple[str, str], float] = {
    ("substation", "hospital"): 15.0,
    ("substation", "health_centre"): 12.0,
    ("substation", "water_works"): 20.0,
    ("substation", "police"): 10.0,
    ("substation", "fire_station"): 10.0,
    ("power_plant", "substation"): 50.0,
    ("water_works", "hospital"): 10.0,
    ("water_works", "health_centre"): 8.0,
    ("hospital", "clinic"): 5.0,
    ("cyclone_shelter", "school"): 2.0,
}

OUTAGE_CASCADE_THRESHOLD = 0.70  # P(outage) above this → node treated as failed for cascade


@dataclass
class CascadeResult:
    """Cascade failure analysis result for one scenario."""

    graph: nx.DiGraph  # the dependency graph (networkx)
    cascade_scores: pd.Series  # asset_id → additional cascade P(failure) contribution
    cascade_chains: list[dict[str, Any]]  # top cascade chains (initiator → victims)
    population_at_cascade_risk: float  # WorldPop sum for cascade-affected assets
    top_initiators: list[dict[str, Any]]  # ranked by cascade_impact_score


def _great_circle_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Fast haversine distance in km."""
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2
    return float(2 * R * np.arcsin(np.sqrt(a)))


def build_dependency_graph(assets: pd.DataFrame) -> nx.DiGraph:
    """Build the directed infrastructure dependency graph.

    Args:
        assets: DataFrame with columns: asset_id, kind, lat, lon, population, p_outage.

    Returns:
        nx.DiGraph: Nodes are asset_ids; edges carry 'strength' and 'kind_pair' attributes.
    """
    G = nx.DiGraph()

    # Add nodes
    for _, row in assets.iterrows():
        G.add_node(
            row["asset_id"],
            kind=row["kind"],
            lat=row["lat"],
            lon=row["lon"],
            population=row.get("population", 0) or 0,
            p_outage=row.get("p_outage", 0) or 0,
            name=row.get("name", ""),
        )

    # Add dependency edges
    asset_list = assets.to_dict("records")
    for up in asset_list:
        for dn in asset_list:
            if up["asset_id"] == dn["asset_id"]:
                continue
            pair = (up["kind"], dn["kind"])
            if pair not in DEPENDENCY_RULES:
                continue
            max_km = MAX_DEPENDENCY_KM.get(pair, 15.0)
            dist_km = _great_circle_km(up["lat"], up["lon"], dn["lat"], dn["lon"])
            if dist_km <= max_km:
                strength = DEPENDENCY_RULES[pair]
                G.add_edge(
                    up["asset_id"],
                    dn["asset_id"],
                    strength=strength,
                    distance_km=dist_km,
                    kind_pair=pair,
                )
    return G


def propagate_cascade(G: nx.DiGraph, direct_outage: dict[str, float]) -> tuple[dict[str, float], dict[str, float]]:
    """Propagate cascade failure probabilities through the dependency graph.

    Uses iterative belief propagation up to MAX_CASCADE_HOPS hops.

    Args:
        G: The dependency graph from build_dependency_graph().
        direct_outage: asset_id → P(direct outage from wind/surge).

    Returns:
        tuple[dict[str, float], dict[str, float]]: (p_total, p_cascade_only)
    """
    p_total = dict(direct_outage)
    p_cascade_only = {nid: 0.0 for nid in G.nodes()}

    for hop in range(MAX_CASCADE_HOPS):
        new_cascade: dict[str, float] = {}
        for upstream_id, downstream_id, edge_data in G.edges(data=True):
            p_up = p_total.get(upstream_id, 0.0)
            if p_up < OUTAGE_CASCADE_THRESHOLD:
                continue  # upstream not likely to fail — no cascade
            strength = edge_data["strength"]
            # Cascade contribution decays with hop count
            hop_decay = 0.7**hop
            contribution = p_up * strength * hop_decay
            new_cascade[downstream_id] = max(
                new_cascade.get(downstream_id, 0.0),
                contribution,
            )

        for nid, contrib in new_cascade.items():
            p_cascade_only[nid] = max(p_cascade_only[nid], contrib)
            p_total[nid] = min(1.0, (direct_outage.get(nid, 0.0) + p_cascade_only[nid]))

    return p_total, p_cascade_only


def find_cascade_chains(
    G: nx.DiGraph,
    direct_outage: dict[str, float],
    top_n: int = 10,
) -> list[dict[str, Any]]:
    """Find the most impactful cascade chains (initiator → victims).

    Args:
        G: Dependency graph.
        direct_outage: P(direct outage) per asset.
        top_n: How many chains to return.

    Returns:
        list of chain dicts with keys: initiator, initiator_kind, victims, cascade_population.
    """
    chains = []
    for node_id in G.nodes():
        p = direct_outage.get(node_id, 0.0)
        if p < OUTAGE_CASCADE_THRESHOLD:
            continue
        node_data = G.nodes[node_id]
        # BFS to find all downstream victims within MAX_CASCADE_HOPS
        victims = []
        visited = {node_id}
        frontier = [(node_id, 0)]
        cascade_pop = 0.0
        while frontier:
            current, depth = frontier.pop(0)
            if depth >= MAX_CASCADE_HOPS:
                continue
            for _, successor in G.out_edges(current):
                if successor not in visited:
                    visited.add(successor)
                    s_data = G.nodes[successor]
                    victims.append(
                        {
                            "asset_id": successor,
                            "kind": s_data["kind"],
                            "name": s_data.get("name", ""),
                            "lat": s_data["lat"],
                            "lon": s_data["lon"],
                            "hop": depth + 1,
                        }
                    )
                    cascade_pop += float(s_data.get("population", 0) or 0)
                    frontier.append((successor, depth + 1))

        if victims:
            chains.append(
                {
                    "initiator": node_id,
                    "initiator_kind": node_data["kind"],
                    "initiator_name": node_data.get("name", ""),
                    "initiator_p_outage": p,
                    "victims": victims,
                    "cascade_population": cascade_pop,
                    "cascade_depth": max((v["hop"] for v in victims), default=0),
                    "cascade_impact_score": p * len(victims) * (1 + cascade_pop / 10000),
                }
            )

    chains.sort(key=lambda c: c["cascade_impact_score"], reverse=True)
    return chains[:top_n]


def run_cascade_analysis(assets: pd.DataFrame) -> CascadeResult:
    """Full cascade analysis: build graph, propagate, find chains, rank initiators.

    Args:
        assets: DataFrame from ranking.py (must include p_outage, kind, lat, lon, population).

    Returns:
        CascadeResult with graph, cascade_scores, chains, population_at_risk, top_initiators.
    """
    required_cols = {"asset_id", "kind", "lat", "lon", "p_outage"}
    missing = required_cols - set(assets.columns)
    if missing:
        raise ValueError(f"assets DataFrame missing columns: {missing}")

    direct = dict(zip(assets["asset_id"], assets["p_outage"].fillna(0)))
    G = build_dependency_graph(assets)
    p_total, p_cascade_only = propagate_cascade(G, direct)

    cascade_series = pd.Series(p_cascade_only, name="cascade_contribution")
    chains = find_cascade_chains(G, direct, top_n=10)

    # Population at cascade risk = assets whose ONLY failure path is via cascade
    at_risk_pop = 0.0
    for node_id, cascade_p in p_cascade_only.items():
        direct_p = direct.get(node_id, 0.0)
        if cascade_p > 0.1 and direct_p < 0.3:  # cascade-driven failure, not direct
            node_data = G.nodes[node_id]
            at_risk_pop += float(node_data.get("population", 0) or 0)

    top_initiators = [
        {
            "asset_id": c["initiator"],
            "kind": c["initiator_kind"],
            "name": c["initiator_name"],
            "p_outage": c["initiator_p_outage"],
            "victims_count": len(c["victims"]),
            "cascade_population": c["cascade_population"],
            "cascade_impact_score": c["cascade_impact_score"],
            "recommendation": _action_recommendation(c),
        }
        for c in chains
    ]

    return CascadeResult(
        graph=G,
        cascade_scores=cascade_series,
        cascade_chains=chains,
        population_at_cascade_risk=at_risk_pop,
        top_initiators=top_initiators,
    )


def _action_recommendation(chain: dict[str, Any]) -> str:
    """Generate a plain-language pre-landfall action recommendation for a cascade initiator."""
    kind = chain["initiator_kind"]
    victims = len(chain["victims"])
    pop = chain["cascade_population"]
    p = chain["initiator_p_outage"]

    actions = {
        "substation": (
            f"De-energize and isolate this substation before landfall "
            f"({p:.0%} outage probability). Protects {victims} downstream assets "
            f"and approximately {pop:,.0f} people from cascade failure."
        ),
        "power_plant": (
            f"Switch to manual load-shedding protocol. "
            f"Coordinates {victims} dependent substations ({pop:,.0f} people)."
        ),
        "water_works": (
            f"Pre-fill all downstream hospital and shelter water reserves. "
            f"Pre-position emergency water tankers at {victims} dependent sites."
        ),
        "hospital": (
            f"Activate backup generators and verify fuel levels. "
            f"This hospital is a cascade source to {victims} downstream facilities."
        ),
    }
    return actions.get(kind, f"Harden this asset before landfall. Cascade risk to {victims} assets.")
