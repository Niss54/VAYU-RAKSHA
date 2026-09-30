"""Pre-landfall counterfactual action optimizer.

For each top cascade initiator, simulates what happens to the cascade graph if
that initiator is hardened (P(outage) forced to 0) before landfall. Ranks
hardening actions by (population protected / hardening cost proxy).

This is VAYU-RAKSHA's second core differentiator.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import networkx as nx
import pandas as pd

from shadowcast_geo.cascade import (
    build_dependency_graph,
    find_cascade_chains,
    propagate_cascade,
)

# Relative hardening cost proxy by asset kind (dimensionless, higher = harder/more disruptive)
HARDENING_COST: dict[str, float] = {
    "substation": 2.0,  # de-energizing disrupts current users
    "power_plant": 4.0,  # major disruption
    "water_works": 1.5,  # needs tanker pre-positioning
    "hospital": 3.0,  # cannot easily shut down
    "health_centre": 1.5,
    "fire_station": 1.0,
    "police": 1.0,
    "cyclone_shelter": 0.5,  # already designated for hardening
    "school": 0.3,
    "clinic": 1.0,
}


@dataclass
class HardeningAction:
    """One recommended pre-landfall hardening action."""

    rank: int
    asset_id: str
    asset_kind: str
    asset_name: str
    hardening_action: str  # what to do (plain language)
    timing_hours_before_landfall: int
    direct_p_outage: float  # without hardening
    population_protected: float  # WorldPop benefit of hardening this one asset
    cascade_victims_prevented: int  # number of cascade victim assets prevented
    cascade_population_protected: float
    total_population_benefit: float
    hardening_cost_proxy: float
    benefit_cost_ratio: float  # population_benefit / cost_proxy
    counterfactual_summary: str  # one sentence for the DM brief


def _compute_baseline_cascade_population(G: nx.DiGraph, direct_outage: dict[str, float]) -> float:
    """Total population at cascade risk in baseline (no hardening)."""
    _, p_cascade = propagate_cascade(G, direct_outage)
    total = 0.0
    for node_id, cascade_p in p_cascade.items():
        direct_p = direct_outage.get(node_id, 0.0)
        if cascade_p > 0.05 and direct_p < 0.3:
            total += float(G.nodes[node_id].get("population", 0) or 0)
    return total


def optimize_hardening_actions(
    assets: pd.DataFrame,
    top_n_actions: int = 10,
) -> list[HardeningAction]:
    """Rank pre-landfall hardening actions by benefit-cost ratio.

    For each candidate initiator: simulate hardening it → compute population
    benefit vs. baseline → rank.

    Args:
        assets: Ranked DataFrame from ranking.py with p_outage, kind, lat, lon, population.
        top_n_actions: How many ranked actions to return.

    Returns:
        list[HardeningAction]: Ranked from highest to lowest benefit-cost ratio.
    """
    direct = dict(zip(assets["asset_id"], assets["p_outage"].fillna(0)))
    G = build_dependency_graph(assets)

    # Find candidate initiators (assets above threshold with downstream victims)
    chains = find_cascade_chains(G, direct, top_n=20)
    candidates = [c for c in chains if c["initiator_p_outage"] >= 0.5]

    actions = []
    for c in candidates:
        initiator_id = c["initiator"]
        asset_row = assets[assets["asset_id"] == initiator_id]
        if asset_row.empty:
            continue
        row = asset_row.iloc[0]

        # Simulate hardening this one initiator
        hardened_direct = dict(direct)
        hardened_direct[initiator_id] = 0.0  # hardened = no direct failure

        # Compare chain victim count before vs after hardening
        hardened_chains = find_cascade_chains(G, hardened_direct, top_n=20)
        hardened_chain_for_this = next(
            (hc for hc in hardened_chains if hc["initiator"] == initiator_id), None
        )

        if hardened_chain_for_this:
            victims_prevented = len(c["victims"]) - len(hardened_chain_for_this["victims"])
            cascade_pop_protected = max(
                0.0,
                float(c["cascade_population"] - hardened_chain_for_this.get("cascade_population", 0)),
            )
        else:
            # Hardening eliminated this cascade chain entirely
            victims_prevented = len(c["victims"])
            cascade_pop_protected = float(c["cascade_population"])

        # Asset's own population
        own_pop = float(row.get("population", 0) or 0)
        total_pop_benefit = own_pop * float(row["p_outage"]) + cascade_pop_protected

        kind = str(row["kind"])
        cost = HARDENING_COST.get(kind, 2.0)
        bcr = total_pop_benefit / cost if cost > 0 else 0.0

        timing = _timing_recommendation(kind, float(row["p_outage"]))
        action_text = _action_text(row, c)

        actions.append(
            HardeningAction(
                rank=0,  # assigned after sorting
                asset_id=initiator_id,
                asset_kind=kind,
                asset_name=str(row.get("name", "") or initiator_id),
                hardening_action=action_text,
                timing_hours_before_landfall=timing,
                direct_p_outage=float(row["p_outage"]),
                population_protected=own_pop,
                cascade_victims_prevented=victims_prevented,
                cascade_population_protected=cascade_pop_protected,
                total_population_benefit=total_pop_benefit,
                hardening_cost_proxy=cost,
                benefit_cost_ratio=bcr,
                counterfactual_summary=(
                    f"Hardening {kind} '{row.get('name', initiator_id)}' at T-{timing}h "
                    f"prevents {victims_prevented} cascade failures "
                    f"protecting ~{int(cascade_pop_protected):,} additional people."
                ),
            )
        )

    actions.sort(key=lambda a: a.benefit_cost_ratio, reverse=True)
    for i, a in enumerate(actions[:top_n_actions]):
        a.rank = i + 1

    return actions[:top_n_actions]


def _timing_recommendation(kind: str, p_outage: float) -> int:
    """Hours before landfall at which hardening should begin."""
    base = {
        "substation": 36,
        "power_plant": 48,
        "water_works": 48,
        "hospital": 24,
        "health_centre": 24,
        "fire_station": 12,
        "police": 12,
    }
    t = base.get(kind, 24)
    # High-risk assets need more time
    if p_outage > 0.8:
        t = min(t + 12, 72)
    return t


def _action_text(row: pd.Series, chain: dict[str, Any]) -> str:
    """Plain-language hardening action for district officer."""
    kind = str(row["kind"])
    name = str(row.get("name", "") or row["asset_id"])
    victims = len(chain["victims"])
    texts = {
        "substation": (
            f"De-energize and isolate substation '{name}' before surge arrival. "
            f"Coordinate with TRANSCO/DISCOMS for controlled shutdown. "
            f"This prevents cascade failure across {victims} dependent assets."
        ),
        "power_plant": (
            f"Switch power plant '{name}' to minimum safe load mode. "
            f"Pre-position mobile generator units at {victims} downstream substations."
        ),
        "water_works": (
            f"Pre-fill all storage tanks at water works '{name}' to 100% capacity. "
            f"Pre-position 3 water tankers at {victims} dependent hospitals and shelters."
        ),
        "hospital": (
            f"Verify backup generator fuel at hospital '{name}' — minimum 72h supply. "
            f"Stock 2-week critical medication supply. Pre-transfer non-critical patients."
        ),
        "cyclone_shelter": (
            f"Open shelter '{name}' 48h before landfall. "
            f"Pre-position emergency rations, water, and first aid for 72h capacity."
        ),
    }
    return texts.get(kind, f"Harden '{name}' before T-24h. Prevents cascade to {victims} assets.")
