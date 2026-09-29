"""VAYU-RAKSHA Shared State Schema for 5-Agent LangGraph System.

Defines the typed data structures passed between NIRNAY, BHUMI, VAYU, SETU, and SANCHAR.
"""

from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict
import operator


class GeoCoordinate(TypedDict):
    lat: float
    lon: float


class CycloneMetadata(TypedDict):
    storm_id: str
    storm_name: str
    basin: str
    current_center: GeoCoordinate
    max_sustained_wind_kt: float
    max_sustained_wind_kmh: float
    central_pressure_hpa: float
    forward_speed_kmh: float
    heading_deg: float
    category_imd: str  # e.g., "Extremely Severe Cyclonic Storm (ESCS)"
    forecast_landfall_time: str
    lead_time_hours: float
    trajectory: List[Dict[str, Any]]
    ensemble_member_count: int


class TerrainAndFloodData(TypedDict):
    elevation_raster_resolution_m: int
    sar_satellite: str  # "ISRO RISAT-1A + Sentinel-1 SAR"
    sar_cloud_penetration_status: str  # "ACTIVE - C-band radar through storm cloud cover"
    flood_inundation_zones: List[Dict[str, Any]]
    max_inundation_depth_m: float
    water_extent_sqkm: float
    worldpop_coastal_density_raster: str
    high_susceptibility_area_sqkm: float


class AtmosphericHazardData(TypedDict):
    wind_field_model: str  # "Holland (1980) Parametric Wind Field"
    storm_surge_crest_m: float
    surge_corridor_coast_extent_km: float
    cumulative_72h_rainfall_mm: float
    r_cliper_rain_peak_mm_hr: float
    wind_radii_34kt_nm: float
    wind_radii_50kt_nm: float
    wind_radii_64kt_nm: float


class InfrastructureNode(TypedDict):
    id: str
    name: str
    type: Literal["substation", "hospital", "shelter", "telecom", "water_plant", "road_bridge"]
    tier: Literal["L1", "L2", "L3", "L4", "L5"]
    lat: float
    lon: float
    district: str
    elevation_m: float
    capacity: str
    backup_power_hrs: float
    population_served: int
    status: Literal["OPERATIONAL", "AT_RISK", "FAILED", "HARDENED"]
    failure_probability: float
    cascade_depth: int
    direct_hazard_cause: Optional[str]
    cascade_predecessor_id: Optional[str]
    plain_language_reasons: List[str]


class DependencyEdge(TypedDict):
    source_id: str
    target_id: str
    dependency_type: Literal["power", "fuel", "access", "telecom", "water"]
    weight: float
    description: str


class EvacuationCorridor(TypedDict):
    route_id: str
    corridor_name: str
    start_point: str
    end_point: str
    status: Literal["CLEAR", "AT_RISK", "SEVERED"]
    water_hazard_depth_m: float
    detour_recommended: bool
    safe_alternative_id: Optional[str]


class CounterfactualAction(TypedDict):
    action_id: str
    priority: Literal["CRITICAL", "HIGH", "MED", "LOW"]
    action_title: str
    target_node_ids: List[str]
    description: str
    window_deadline: str
    cost_proxy: float  # Operational disruption / logistics cost (scale 1-100)
    delta_population_protected: int
    roi_score: float  # (delta_population_protected / cost_proxy)
    approved_by_officer: bool
    cascade_nodes_saved: int


class AdvisoryNotice(TypedDict):
    language_code: Literal["or", "bn", "te", "ta", "hi", "en"]
    language_name: str
    headline: str
    district: str
    urgency: Literal["IMMEDIATE", "EXPECTED", "FUTURE"]
    plain_body: str
    action_bulletins: List[str]
    ivr_speech_script: str
    cap_xml_payload: Optional[str]


class ParametricInsuranceTrigger(TypedDict):
    policy_id: str
    insured_entity: str
    wind_threshold_kmh: float
    flood_extent_threshold_pct: float
    observed_wind_kmh: float
    observed_flood_pct: float
    satellite_evidence_sources: List[str]
    trigger_status: Literal["MONITORING", "CRITERIA_MET", "TRIGGER_DISPATCHED"]
    payout_liquidity_inr_crores: float
    payout_smart_contract_hash: Optional[str]
    timestamp_utc: str


class AgentTelemetry(TypedDict):
    agent_name: Literal["NIRNAY", "BHUMI", "VAYU", "SETU", "SANCHAR"]
    status: Literal["IDLE", "RUNNING", "COMPLETED", "ERROR"]
    active_step: str
    last_thought: str
    latency_ms: float
    confidence_score: float


class CycloneState(TypedDict):
    """The master CycloneState TypedDict passed across the LangGraph StateGraph."""
    scenario_id: str
    cyclone_metadata: CycloneMetadata
    earth_data: TerrainAndFloodData
    atmospheric_data: AtmosphericHazardData
    infrastructure_nodes: List[InfrastructureNode]
    dependency_edges: List[DependencyEdge]
    evacuation_corridors: List[EvacuationCorridor]
    ranked_action_queue: List[CounterfactualAction]
    advisories: List[AdvisoryNotice]
    parametric_insurance: ParametricInsuranceTrigger
    agent_telemetry: Dict[str, AgentTelemetry]
    audit_log: List[Dict[str, Any]]
    final_situation_summary: str
