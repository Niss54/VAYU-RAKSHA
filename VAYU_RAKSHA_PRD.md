# 📋 VAYU-RAKSHA — Product Requirements Document (PRD)
> **Document Version:** 2.0 (Post-Audit Edition)  
> **Source Material:** [`VAYU_RAKSHA_CLAUDE.md`](file:///c:/Users/nisha/OneDrive/Documents/Downloads/gdg/VAYU_RAKSHA_CLAUDE.md)  
> **Objective:** Bridge all missing scientific, algorithmic, and backend gaps to build a winning submission for **Build with AI: Track 5**.

---

## 🎯 Project Overview & Core Philosophy

ShadowCast provides baseline **per-asset impact forecasting**.  
**VAYU-RAKSHA** differentiates itself by implementing what ShadowCast explicitly lacks:
1. **NetworkX Infrastructure Cascade Failure Engine** (Multi-hop cross-infrastructure dependency graph).
2. **Pre-landfall Counterfactual Action Optimizer** (Benefit-Cost Ratio ranking of actionable orders).
3. **ISRO MOSDAC + RISAT-1A Satellite Integration** (India-first INSAT-3DS & C-band SAR ground-truth validation).
4. **CLIMADA Physical Vulnerability Curves** (ETH Zürich Emanuel damage function as secondary scientific model).
5. **LangGraph 5-Agent Brain Architecture** (Deterministic StateGraph with Gemini synthesis).

---

## 🗺️ Phased Implementation Roadmap

This PRD divides all unbuilt tasks into **7 sequential phases**. You can prompt the AI agent with specific task codes (e.g. *"Execute Task 1.1"* or *"Start Phase 1"*) to execute them one by one.

```
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 1: Python Geo Dependencies & Data Foundation                    │
│   ├── Task 1.1: pyproject.toml Dependency Upgrades                    │
│   ├── Task 1.2: Global Configuration Constants (config.py)            │
│   ├── Task 1.3: Extended Pydantic Schemas (models.py)                 │
│   └── Task 1.4: Cascade Score Integration in Ranking (ranking.py)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 2: NetworkX Cascade Engine & Counterfactual Action Optimizer     │
│   ├── Task 2.1: NetworkX Cascade Failure Engine (cascade.py)          │
│   ├── Task 2.2: Cascade Engine Unit Tests (test_cascade.py)           │
│   ├── Task 2.3: Pre-landfall Action Optimizer (counterfactual.py)     │
│   └── Task 2.4: Counterfactual Unit Tests (test_counterfactual.py)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 3: ISRO Satellite Data & Physical Model Validation               │
│   ├── Task 3.1: ISRO MOSDAC API Client (mosdac.py)                    │
│   ├── Task 3.2: MOSDAC Client Unit Tests (test_mosdac.py)             │
│   ├── Task 3.3: RISAT-1A C-band SAR Flood Validation (risat_sar.py)   │
│   ├── Task 3.4: ETH Zürich CLIMADA Fragility Curves (climada_curves.py)│
│   └── Task 3.5: CLIMADA Unit Tests (test_climada_curves.py)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 4: LangGraph 5-Agent Brain Architecture (Python Multi-Agent)     │
│   ├── Task 4.1: Shared CycloneState Schema (agents/state.py)          │
│   ├── Task 4.2: BHUMI (Earth) & VAYU (Atmosphere) Sub-agents          │
│   ├── Task 4.3: SETU (Cascade) & SANCHAR (Advisory) Sub-agents        │
│   ├── Task 4.4: NIRNAY Supervisor Agent with Gemini Synthesis         │
│   └── Task 4.5: StateGraph Assembly & Orchestration (workflow.py)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 5: FastAPI Endpoints & Offline Build Pipeline Integration        │
│   ├── Task 5.1: Register 4 New Endpoints in Geo API (api.py)          │
│   └── Task 5.2: Integrate Cascade & ISRO Artifacts in build.py        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 6: Next.js Frontend Types, Standalone Components & API Binding   │
│   ├── Task 6.1: TypeScript Interface Definitions (types.ts)           │
│   ├── Task 6.2: Standalone Cascade Graph Component (cascade-graph.tsx)│
│   ├── Task 6.3: Standalone Action Queue Component (action-queue.tsx)  │
│   ├── Task 6.4: Standalone ISRO Panel Component (isro-panel.tsx)      │
│   ├── Task 6.5: Extend Brief Panel with ISRO & Cascade Badges         │
│   ├── Task 6.6: Add "Cascade" and "ISRO" Tabs in Console UI           │
│   └── Task 6.7: Connect Frontend API Client to Live Geo Endpoints     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 7: Hackathon Submission Blueprint, Final Tests & Git Push        │
│   ├── Task 7.1: Author VAYU_RAKSHA_BLUEPRINT.md for Judges            │
│   ├── Task 7.2: Enhance Root README.md with Citation & Demo Script    │
│   └── Task 7.3: Full Test Suite Run, Typecheck, and GitHub Commit     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Detailed Task Specifications

### 🔷 Phase 1: Python Geo Dependencies & Data Foundation

#### `TASK-1.1`: Update `services/geo/pyproject.toml`
- **File:** `services/geo/pyproject.toml`
- **Objective:** Add required scientific & AI packages: `networkx>=3.3`, `langgraph>=0.2.0`, `google-generativeai>=0.8.0`.
- **Acceptance Criteria:** `pyproject.toml` declares all 3 dependencies cleanly.

#### `TASK-1.2`: Append Global Configuration Constants
- **File:** `services/geo/src/shadowcast_geo/config.py`
- **Objective:** Append all constants required by cascade, CLIMADA, MOSDAC, SAR, and LangGraph:
  - `CASCADE_OUTAGE_THRESHOLD = 0.70`, `CASCADE_MAX_HOPS = 3`
  - `CLIMADA_VHALF_MS = 74.7`, `CLIMADA_VTHRESH_MS = 25.7`, `CLIMADA_EXPONENT = 3.0`
  - `MOSDAC_BASE_URL`, `MOSDAC_RI_SST_THRESHOLD_C = 1.0`
  - `SAR_SIGMA0_WATER_DB = -15.0`, `SAR_CHANGE_THRESHOLD_DB = 3.0`, `SAR_MIN_IOU_ACCEPTABLE = 0.40`
  - `LANGGRAPH_MAX_ITERATIONS = 2`, `LANGGRAPH_TIMEOUT_SECONDS = 120`
  - `HARDENING_WINDOWS` mapping (substation: 36h, power_plant: 48h, hospital: 24h, etc.)
- **Acceptance Criteria:** Constants importable across `shadowcast_geo`.

#### `TASK-1.3`: Append Extended Pydantic Schemas
- **File:** `services/geo/src/shadowcast_geo/models.py`
- **Objective:** Define strongly-typed Pydantic V2 schemas:
  - `CascadeVictim`: asset_id, kind, name, lat, lon, hop
  - `CascadeChain`: initiator, initiator_kind, initiator_name, initiator_p_outage, victims, cascade_population, cascade_impact_score
  - `ActionItem`: rank, asset_id, asset_kind, asset_name, hardening_action, timing_hours_before_landfall, direct_p_outage, cascade_victims_prevented, cascade_population_protected, total_population_benefit, benefit_cost_ratio, counterfactual_summary
  - `CascadeSummary`: top_chains, top_actions, population_at_cascade_risk, cascade_edges, cascade_nodes
  - `ISRODataStatus`: mosdac_available, insat3ds_intensity_kt, ri_risk, sst_c, risat_sar_validation, citation
  - `SARValidation`: scenario_id, sar_source, modelled_flooded_assets, sar_flooded_cells, model_sar_overlap_pct, iou, peak_flood_depth_m, notes, citation
  - `ScenarioDetailV2`: extends `ScenarioDetail` with `cascade`, `isro`, `sar_validation`, `climada_comparison`
- **Acceptance Criteria:** Schemas serialize to/from JSON cleanly.

#### `TASK-1.4`: Integrate Cascade Contribution in Scoring Formula
- **File:** `services/geo/src/shadowcast_geo/ranking.py`
- **Objective:** Modify `rank_assets(...)` scoring logic so if `"cascade_contribution"` exists in columns, add cascade bonus:
  ```python
  cascade_bonus = (ranked["cascade_contribution"].fillna(0) * 0.2).clip(upper=0.2)
  ranked["score"] = (ranked["score"] + cascade_bonus).clip(upper=1.0)
  ```
- **Acceptance Criteria:** Assets that cause severe downstream cascade receive up to +0.2 boost in prioritization.

---

### 🔷 Phase 2: NetworkX Cascade Engine & Counterfactual Optimizer

#### `TASK-2.1`: Implement `cascade.py`
- **File:** `services/geo/src/shadowcast_geo/cascade.py`
- **Objective:** Implement full infrastructure cascade failure engine:
  - `DEPENDENCY_RULES` dict (substation->hospital: 0.90, substation->water_works: 0.80, etc.)
  - `MAX_DEPENDENCY_KM` geographic thresholds (15km, 20km, 50km)
  - `_great_circle_km(lat1, lon1, lat2, lon2)` haversine calculation
  - `build_dependency_graph(assets: pd.DataFrame) -> nx.DiGraph`
  - `propagate_cascade(G: nx.DiGraph, direct_outage: dict) -> (p_total, p_cascade_only)` with 3-hop belief propagation and `0.7**hop` decay
  - `find_cascade_chains(G, direct_outage, top_n=10)`: BFS chain discovery with impact score
  - `run_cascade_analysis(assets) -> CascadeResult`
  - `_action_recommendation(chain)` plain-language generator
- **Acceptance Criteria:** Generates directed dependency graph and identifies initiators.

#### `TASK-2.2`: Create `test_cascade.py`
- **File:** `services/geo/tests/test_cascade.py`
- **Objective:** 8 unit tests testing node addition, edge weights, belief propagation, clamping at 1.0, chain discovery, and missing columns exception.
- **Acceptance Criteria:** 100% test pass with `pytest`.

#### `TASK-2.3`: Implement `counterfactual.py`
- **File:** `services/geo/src/shadowcast_geo/counterfactual.py`
- **Objective:** Implement pre-landfall action optimizer:
  - `HARDENING_COST` proxy dictionary
  - `HardeningAction` dataclass
  - `optimize_hardening_actions(assets, top_n_actions=10)`:
    - Simulates setting `p_outage = 0.0` for candidate initiators
    - Re-evaluates cascade failure propagation
    - Computes `cascade_victims_prevented`, `cascade_population_protected`, and `benefit_cost_ratio`
  - `_timing_recommendation(kind, p_outage)` (T-12h to T-48h)
  - `_action_text(row, chain)` actionable directives
- **Acceptance Criteria:** Outputs list of `HardeningAction` objects sorted by BCR.

#### `TASK-2.4`: Create `test_counterfactual.py`
- **File:** `services/geo/tests/test_counterfactual.py`
- **Objective:** Unit tests verifying BCR ordering, ranking assignment, timing logic, and summary strings.
- **Acceptance Criteria:** All tests pass with zero warnings.

---

### 🔷 Phase 3: ISRO Satellite Data & Physical Model Validation

#### `TASK-3.1`: Implement `mosdac.py` (ISRO API Client)
- **File:** `services/geo/src/shadowcast_geo/mosdac.py`
- **Objective:**
  - `MOSDACCycloneProduct` dataclass (INSAT-3DS Dvorak wind, cloud-top temperature)
  - `fetch_cyclone_intensity(storm_name)`: Live fetch from `https://www.mosdac.gov.in/live/api` with fallback to demo data for FANI/DANA
  - `fetch_bof_sst_anomaly(lat, lon)`: Bay of Bengal SST anomaly & Rapid Intensification (RI) risk flagging
  - `build_isro_data_citation()`: Formal citation dictionary
- **Acceptance Criteria:** Returns valid intensity and SST data with or without `MOSDAC_TOKEN`.

#### `TASK-3.2`: Create `test_mosdac.py`
- **File:** `services/geo/tests/test_mosdac.py`
- **Objective:** Unit tests for demo fallback, coordinate validity, SST anomalies, and citation structures.
- **Acceptance Criteria:** Passes synchronously without requiring live internet access.

#### `TASK-3.3`: Implement `risat_sar.py` (C-band SAR Flood Validation)
- **File:** `services/geo/src/shadowcast_geo/risat_sar.py`
- **Objective:**
  - `SARValidationResult` dataclass
  - `compare_surge_vs_sar(scenario_id, modelled_surge_assets, pre_date, post_date, region_bbox)`
  - Benchmark statistics for Fani (18,500 ha, IoU 0.54, 78% overlap) and Dana
  - Sentinel-1 GEE proxy methodology & formal NRSC/Bhoonidhi citations
- **Acceptance Criteria:** Computes IoU and overlap percentage metrics.

#### `TASK-3.4`: Implement `climada_curves.py` (ETH Zürich Damage Model)
- **File:** `services/geo/src/shadowcast_geo/climada_curves.py`
- **Objective:**
  - Emanuel (2011) wind-damage function implementation:
    $$D(v) = \frac{1}{1 + (V_{half} / \max(v - V_{thresh}, 0))^n}$$
  - `climada_damage_fraction(wind_kt: np.ndarray) -> np.ndarray`
  - `compare_models(wind_kt, viirs_model_p)`: Mean Absolute Difference (MAD), agreement rate, and divergence points
  - Full academic citations (Aznar-Siguan & Bresch 2019)
- **Acceptance Criteria:** Returns damage fraction in [0, 1] with vectorized NumPy calculation.

#### `TASK-3.5`: Create `test_climada_curves.py`
- **File:** `services/geo/tests/test_climada_curves.py`
- **Objective:** Unit tests for zero damage below threshold, half damage near $V_{half}$, monotonic increase, NaN handling, and model comparison.
- **Acceptance Criteria:** 100% test pass.

---

### 🔷 Phase 4: LangGraph 5-Agent Brain Architecture

#### `TASK-4.1`: Define Shared State Schema
- **File:** `services/geo/src/shadowcast_geo/agents/state.py`
- **Objective:** Define `CycloneState(TypedDict)` containing inputs, sub-agent outputs (`bhumi`, `vayu`, `setu`, `sanchar`), and `nirnay` supervisor synthesis fields.
- **Acceptance Criteria:** Type-safe state dictionary compatible with LangGraph.

#### `TASK-4.2`: Implement `bhumi.py` & `vayu.py` Agents
- **Files:** `services/geo/src/shadowcast_geo/agents/bhumi.py`, `services/geo/src/shadowcast_geo/agents/vayu.py`
- **Objective:**
  - `bhumi.py`: Ingests terrain, DEM, LandScan/WorldPop, and OSM critical infrastructure nodes.
  - `vayu.py`: Computes Holland wind vortex, surge crest, GPM rain extremes, and ISRO MOSDAC intensity.
- **Acceptance Criteria:** Both run independently and update state.

#### `TASK-4.3`: Implement `setu.py` & `sanchar.py` Agents
- **Files:** `services/geo/src/shadowcast_geo/agents/setu.py`, `services/geo/src/shadowcast_geo/agents/sanchar.py`
- **Objective:**
  - `setu.py`: Executes NetworkX cascade failure graph, calculates cascade chains, and runs counterfactual optimizer.
  - `sanchar.py`: Synthesizes 6-language contextual CAP 1.2 advisories and verifies parametric smart insurance triggers.
- **Acceptance Criteria:** Consumes outputs from upstream agents and generates actionable outputs.

#### `TASK-4.4`: Implement `nirnay.py` Supervisor Agent
- **File:** `services/geo/src/shadowcast_geo/agents/nirnay.py`
- **Objective:**
  - Supervisor agent orchestrator with 2-iteration loop (`run` and `route`)
  - Synthesizes final District Collector situation brief using Gemini Flash (with template fallback)
  - Prepares final prioritized `action_queue`
- **Acceptance Criteria:** Gracefully handles missing Gemini API key with robust template fallback.

#### `TASK-4.5`: Assemble & Compile `workflow.py`
- **File:** `services/geo/src/shadowcast_geo/agents/workflow.py`
- **Objective:**
  - Construct `StateGraph(CycloneState)`
  - Wire parallel execution: `nirnay` -> [`bhumi`, `vayu`] -> `setu` -> `sanchar` -> `nirnay` -> `END`
  - Provide `run_vayu_raksha(scenario_id, storm_name) -> CycloneState` entry point
- **Acceptance Criteria:** Graph compiles without cycles and executes smoothly.

---

### 🔷 Phase 5: FastAPI Endpoints & Offline Build Pipeline Integration

#### `TASK-5.1`: Register 4 New Endpoints in `api.py`
- **File:** `services/geo/src/shadowcast_geo/api.py`
- **Objective:** Register endpoints:
  - `GET /scenarios/{scenario_id}/cascade`: returns cascade chains & action queue
  - `GET /scenarios/{scenario_id}/isro`: returns ISRO data status & citations
  - `GET /scenarios/{scenario_id}/sar`: returns SAR flood validation vs surge
  - `GET /scenarios/{scenario_id}/climada`: returns CLIMADA fragility comparison
- **Acceptance Criteria:** Endpoints return valid JSON or 404 with standard error format.

#### `TASK-5.2`: Integrate Artifact Generation into `build.py`
- **File:** `services/geo/src/shadowcast_geo/build.py`
- **Objective:**
  - After single-asset ranking, execute `run_cascade_analysis` and re-rank with `cascade_contribution`
  - Run `optimize_hardening_actions`, `fetch_cyclone_intensity`, `compare_surge_vs_sar`, and `compare_models`
  - Persist `cascade.json`, `isro.json`, `sar_validation.json`, and `climada.json` into artifact store
- **Acceptance Criteria:** Scenario builds generate all 4 extended artifact files.

---

### 🔷 Phase 6: Next.js Frontend Types, Standalone Components & API Binding

#### `TASK-6.1`: Update `types.ts`
- **File:** `apps/web/src/lib/types.ts`
- **Objective:** Add TypeScript interfaces: `CascadeVictim`, `CascadeChain`, `ActionItem`, `CascadeSummary`, `ISRODataStatus`, `SARValidation`.
- **Acceptance Criteria:** Passes `pnpm typecheck` without errors.

#### `TASK-6.2`: Create `cascade-graph.tsx`
- **File:** `apps/web/src/components/cascade-graph.tsx`
- **Objective:** Render D3/SVG styled graph showing nodes colored by asset kind (hospital: red, substation: amber, water_works: blue), dependency arrows, and initiator badges.
- **Acceptance Criteria:** Clean rendering with zero hydration errors.

#### `TASK-6.3`: Create `action-queue.tsx`
- **File:** `apps/web/src/components/action-queue.tsx`
- **Objective:** Render ranked pre-landfall action cards with priority color headers, T-hour deadline badges, BCR scores, and population benefit metrics.
- **Acceptance Criteria:** Responsive layout adhering to dark-mode design system.

#### `TASK-6.4`: Create `isro-panel.tsx`
- **File:** `apps/web/src/components/isro-panel.tsx`
- **Objective:** Dedicated panel displaying INSAT-3DS cloud-top temperature, Dvorak wind speed, Bay of Bengal SST anomaly indicator, and formal ISRO SAC/NRSC open data citations.
- **Acceptance Criteria:** Displays live telemetry or demo data with full citation links.

#### `TASK-6.5`: Extend `brief-panel.tsx`
- **File:** `apps/web/src/components/brief-panel.tsx`
- **Objective:** Add ISRO Data Badge and Infrastructure Cascade Failure Risk summary card directly into the default brief tab.
- **Acceptance Criteria:** Appears under the situation directive banner.

#### `TASK-6.6`: Extend Tabs in `console.tsx`
- **File:** `apps/web/src/components/console.tsx`
- **Objective:** Add `Cascade` and `ISRO` tabs alongside `Brief`, `Prioritise`, `Prepare`, `Prove`.
- **Acceptance Criteria:** Seamless tab switching with state preservation.

#### `TASK-6.7`: Connect Frontend API Client to Live Geo Endpoints
- **File:** `apps/web/src/server/geo.ts`
- **Objective:** Add helper functions to fetch `/scenarios/{id}/cascade`, `/isro`, `/sar`, `/climada` from `GEO_API_URL` with cached fallback.
- **Acceptance Criteria:** Next.js fetches from Cloud Run or cached JSON seamlessly.

---

### 🔷 Phase 7: Hackathon Blueprint, Final Tests & Git Push

#### `TASK-7.1`: Author `VAYU_RAKSHA_BLUEPRINT.md`
- **File:** `VAYU_RAKSHA_BLUEPRINT.md`
- **Objective:** Complete document for hackathon judges detailing problem statement, ShadowCast preservation, 5 key innovations, mathematical models, validation metrics table, and system architecture.
- **Acceptance Criteria:** Markdown document ready for submission.

#### `TASK-7.2`: Enhance Root `README.md`
- **File:** `README.md`
- **Objective:** Add VAYU-RAKSHA header, ShadowCast vs VAYU-RAKSHA feature matrix, citations table, and 3-minute judge demo script.
- **Acceptance Criteria:** Top of README displays the competitive advantages clearly.

#### `TASK-7.3`: Full Test Suite, Typecheck & GitHub Push
- **Objective:**
  - Run `pytest` on all Python tests (maintain >88% coverage)
  - Run `pnpm typecheck` & `pnpm test` on web app
  - Commit all changes with conventional commit messages and push to `origin/main`
- **Acceptance Criteria:** Clean git working tree and all checks passing green.

---

## 🚦 How to Work With the Agent

You can now give tasks one by one. For example:
- *"Execute Task 1.1"* ➔ Updates dependencies in `pyproject.toml`.
- *"Execute Phase 1"* ➔ Completes all tasks in Phase 1 (1.1, 1.2, 1.3, 1.4).
- *"Execute Task 2.1"* ➔ Builds `cascade.py`.
- *"Execute Task 2.2"* ➔ Tests `cascade.py`.
