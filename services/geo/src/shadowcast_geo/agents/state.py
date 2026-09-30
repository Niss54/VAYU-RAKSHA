"""LangGraph shared CycloneState — passed between all agents."""
from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


class CycloneState(TypedDict):
    """Shared state across all VAYU-RAKSHA LangGraph agents."""

    # Input
    scenario_id: str
    storm_name: str

    # BHUMI Agent outputs
    terrain_ready: bool
    infrastructure_nodes: int
    gee_layers_loaded: list[str]

    # VAYU Agent outputs
    wind_field_computed: bool
    surge_peak_m: float | None
    rain_extreme_sites: int
    intensity_kt: float | None
    mosdac_intensity_kt: float | None
    ri_risk: bool

    # SETU Agent outputs
    cascade_ready: bool
    cascade_chains_count: int
    population_at_cascade_risk: float
    top_action: str | None
    hardening_actions: list[dict[str, Any]]

    # SANCHAR Agent outputs
    advisory_dispatched: bool
    advisory_languages: list[str]
    insurance_trigger_ready: bool

    # NIRNAY Supervisor outputs
    final_brief: str | None
    action_queue: list[dict[str, Any]]
    errors: Annotated[list[str], operator.add]
    iteration_count: int
