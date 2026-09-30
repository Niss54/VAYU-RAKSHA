/** Response types of the ShadowCast geo API (mirrors services/geo/src/shadowcast_geo/models.py). */

export interface Region {
  id: string;
  name: string;
  /** south, west, north, east (degrees) */
  bbox: [number, number, number, number];
}

export interface ScenarioSummary {
  id: string;
  storm: string;
  season: number;
  region: Region;
  landfall: string;
  peak_vmax_kt: number;
}

export interface OutageModel {
  intercept: number;
  slope: number;
  trained_on: string;
  n: number;
  auc: number | null;
  brier: number | null;
}

/** Spatial cross-validation on the reference storm: each south-to-north block of coast held out in turn. */
export interface SpatialHoldout {
  folds: number;
  n: number;
  auc: number | null;
  brier: number | null;
  blocks: { lat_min: number; lat_max: number; n: number; observed_outage_rate: number; auc: number | null }[];
}

export interface Skill {
  n: number;
  observed_outage_rate: number | null;
  auc: number | null;
  brier: number | null;
  spearman: number | null;
  out_of_sample: boolean;
  spatial_holdout?: SpatialHoldout;
}

export interface LossBand {
  low_kt: number;
  high_kt: number;
  n: number;
  p25: number;
  median: number;
  p75: number;
}

export interface ForecastSummary {
  key: string;
  issued: string;
  lead_h: number;
  storm_id: string;
  members: number;
  assets_likely_gale: number;
  assets_likely_hurricane: number;
  max_p_outage: number;
  source: string;
  /** Parametric cover per district under this forecast. */
  districts: ForecastDistrict[];
}

export interface ForecastDistrict {
  district: string;
  p_trigger: number;
  expected_payout_share: number;
  index_kt: number;
}

/** Parametric cover per district on the best track, with the outages satellites saw there (basis risk). */
export interface DistrictTrigger {
  district: string;
  lat: number;
  lon: number;
  sites: number;
  index_kt: number;
  payout_share: number;
  trigger_time: string | null;
  lead_h: number | null;
  lit_substations: number;
  observed_outage_rate: number | null;
}

/** Arterial roads through the storm (best track). */
export interface RoadSummary {
  roads: number;
  km: number;
  km_cut: number;
  km_at_risk: number;
  first_closure: string | null;
  cut_by_surge: number;
}

export interface RoadProperties {
  road_id: string;
  name: string | null;
  ref: string | null;
  highway: string;
  length_km: number;
  peak_wind_kt: number;
  flood_m: number;
  rain_mm: number;
  status: "cut" | "at risk" | "open";
  causes: string[];
  closes_at: string | null;
}

export interface RoadCollection {
  type: "FeatureCollection";
  features: {
    type: "Feature";
    geometry: { type: "LineString"; coordinates: [number, number][] };
    properties: RoadProperties;
  }[];
}

/** Modelled storm rain against satellite-measured rain (best track). */
export interface RainSummary {
  model: string;
  truth: string;
  n: number;
  spearman: number | null;
  median_ratio: number;
  max_modelled_mm: number;
  max_observed_mm: number;
  extreme_sites: number;
}

/** IMD's reported surge next to the modelled peak on the same stretch of coast. */
export interface SurgeObservation {
  place: string;
  low_m: number;
  high_m: number;
  kind: string;
  source: string;
  modelled_m: number | null;
}

/** The modelled storm-surge crest along the region's open coast (best track). */
export interface SurgeSummary {
  peak_m: number;
  lat: number;
  lon: number;
  time: string;
  coast_points: number;
  flooded_sites: number;
  method: string;
  observed: SurgeObservation | null;
}

export interface SurgePoint {
  lat: number;
  lon: number;
  peak_m: number | null;
  setup_m: number | null;
  barometer_m: number | null;
  peak_time: string | null;
}

export interface ScenarioDetail extends ScenarioSummary {
  track_source: string;
  asset_counts: Record<string, number>;
  model: OutageModel;
  skill: Skill;
  loss_by_band: LossBand[];
  surge: SurgeSummary;
  rain: RainSummary;
  roads: RoadSummary;
  insurance: { terms: string; districts: DistrictTrigger[] };
  forecasts: ForecastSummary[];
  built_at: string;
}

export interface Asset {
  asset_id: string;
  rank: number;
  kind: string;
  name: string | null;
  source: string;
  lat: number;
  lon: number;
  peak_wind_kt: number | null;
  peak_time: string | null;
  min_dist_km: number;
  closest_time: string | null;
  band_kt: number;
  band_entry: string | null;
  gale_arrival: string | null;
  population: number | null;
  elevation_m: number | null;
  district?: string | null;
  /** Modelled storm-total rain (R-CLIPER); satellite-measured rain on the best track only. */
  rain_mm?: number | null;
  observed_rain_mm?: number | null;
  /** The nearest arterial road and when it closes (best track only). */
  road_km?: number | null;
  access_road?: string | null;
  access_closes?: string | null;
  /** Storm surge on the best track only: distance to the open coast, the peak surge there, water depth here. */
  coast_km?: number | null;
  surge_m?: number | null;
  flood_m?: number | null;
  criticality: number;
  p_outage: number;
  score: number;
  observed_loss_pct: number | null;
  reasons: string[];
}

export interface ForecastAsset extends Asset {
  p34: number;
  p64: number;
  wind_p10: number;
  wind_p90: number;
  members: number;
  p_rain: number;
}

export interface Page<T> {
  total: number;
  items: T[];
}

export interface TimelinePoint {
  time: string;
  wind_kt: number | null;
}

export interface AssetDetail {
  asset: Asset;
  timeline: TimelinePoint[];
}

export interface StormPosition {
  lat: number;
  lon: number;
  vmax_kt: number;
  rmw_km: number;
}

export interface HazardSnapshot {
  at: string;
  storm: StormPosition | null;
  asset_ids: string[];
  wind_kt: number[];
}

export interface TrackFeatureCollection {
  type: "FeatureCollection";
  features: {
    type: "Feature";
    geometry: { type: "LineString" | "Point"; coordinates: number[][] | number[] };
    properties: Record<string, unknown>;
  }[];
}

export interface BacktestSubstation {
  asset_id: string;
  name: string | null;
  lat: number;
  lon: number;
  peak_wind_kt: number | null;
  p_outage: number;
  ntl_pre: number | null;
  ntl_post: number | null;
  loss_pct: number | null;
  lit: boolean;
}

export interface Backtest {
  skill: Skill;
  loss_by_band: LossBand[];
  substations: BacktestSubstation[];
}

/** The feed archiver's newest run: cyclones GDACS is tracking and official NDMA SACHET warnings, as issued. */
export interface LiveFeed {
  run_at: string | null;
  cyclones: {
    name: string | null;
    alert: string | null;
    severity: string | null;
    country: string | null;
    start: string | null;
    end: string | null;
    current: boolean;
    url: string;
  }[];
  warnings: {
    identifier: string;
    sender: string;
    sent: string;
    event: string;
    severity: string;
    urgency: string;
    certainty: string;
    headline: string;
    onset: string;
    expires: string;
    areas: string[];
  }[];
}

/** Either the best-track replay or one as-issued ensemble forecast. */
export type ReplayMode = { kind: "best-track" } | { kind: "forecast"; key: string };

// ─── VAYU-RAKSHA EXTENSIONS ───────────────────────────────────────────────

export interface CascadeVictim {
  asset_id: string;
  kind: string;
  name: string | null;
  lat: number;
  lon: number;
  hop: number;
}

export interface CascadeChain {
  initiator: string;
  initiator_kind: string;
  initiator_name: string | null;
  initiator_p_outage: number;
  victims: CascadeVictim[];
  cascade_population: number;
  cascade_impact_score: number;
}

export interface ActionItem {
  rank: number;
  asset_id: string;
  asset_kind: string;
  asset_name: string | null;
  hardening_action: string;
  timing_hours_before_landfall: number;
  direct_p_outage: number;
  cascade_victims_prevented: number;
  cascade_population_protected: number;
  total_population_benefit: number;
  benefit_cost_ratio: number;
  counterfactual_summary: string;
}

export interface CascadeSummary {
  top_chains: CascadeChain[];
  top_actions: ActionItem[];
  population_at_cascade_risk: number;
  cascade_edges: number;
  cascade_nodes: number;
}

export interface ISRODataStatus {
  mosdac_available: boolean;
  insat3ds_intensity_kt: number | null;
  ri_risk: boolean;
  sst_c: number | null;
  risat_sar_validation?: Record<string, unknown> | null;
  citation: Record<string, string>;
}

export interface SARValidation {
  scenario_id: string;
  sar_source: string;
  modelled_flooded_assets: number;
  sar_flooded_cells: number;
  model_sar_overlap_pct: number | null;
  iou: number | null;
  peak_flood_depth_m: number | null;
  notes: string;
  citation: string;
}

export interface CLIMADAComparison {
  agreement_rate: number;
  mean_absolute_difference: number;
  citation: string;
}
