# 🎫 VAYU-RAKSHA — Master Feature Ticket List & Sprint Plan

> **Project:** VAYU-RAKSHA (वायु रक्षा) — Anticipatory Cyclone & Infrastructure Cascade Intelligence Platform  
> **Track:** Track 5 — Track-Based Cyclone Impact & Infrastructure Vulnerability Forecaster  
> **Team:** SYNTRIX (Nishant Maurya · Lead Developer & AI Architect)  
> **Repository:** [https://github.com/Niss54/gdg](https://github.com/Niss54/gdg)  
> **Target Version:** v2.0.0-PROD  
> **Status:** 🟢 Ready for Step-by-Step Execution  

---

## 📌 Sprint Execution Matrix

| Epic ID | Epic Title | Focus Area | Total Tickets | Status |
|---|---|---|---|---|
| **EPIC-01** | Foundation & Repository Reset | Git Clean, VAYU-RAKSHA Rebrand, Configs | 4 Tickets | 🔄 In Progress |
| **EPIC-02** | 5-Agent LangGraph Architecture | NIRNAY, BHUMI, VAYU, SETU, SANCHAR | 5 Tickets | ⬜ Ready |
| **EPIC-03** | Core Physics & Cascade Failure Engines | Holland Wind, Surge, NetworkX Cascade, Counterfactual | 5 Tickets | ⬜ Ready |
| **EPIC-04** | ISRO Native & GEE Satellite Ingestion | INSAT-3DS, RISAT-1A SAR, GEE Sentinel-1, WorldPop | 4 Tickets | ⬜ Ready |
| **EPIC-05** | Ultra-Premium Tactical Command HUD (Next-Gen UI) | Cyber HUD, Agent Brain, Cascade Graph, What-If Sandbox | 6 Tickets | ⬜ Ready |
| **EPIC-06** | Multilingual Comms, Parametric Payout & Validation | 6 Languages, Automated Insurance Trigger, Fani Demo | 4 Tickets | ⬜ Ready |

---

## 🏛️ EPIC-01: Foundation & Project Architecture Reset

### TICKET-0101 — Clean Git History & Configure Remote
- **Summary:** Initialize fresh git tree on `main`, purge legacy shadowcast history, link `origin https://github.com/Niss54/gdg`.
- **Deliverables:** Clean git log, branch `main`, verified remotes.
- **Priority:** 🔴 P0 (Critical)
- **Status:** ✅ Done

### TICKET-0102 — Project Rebranding & Metadata Modernization
- **Summary:** Rename project across `README.md`, `package.json`, environment definitions, and documentation from ShadowCast to **VAYU-RAKSHA (Team SYNTRIX)**.
- **Deliverables:** Updated root `README.md`, `apps/web/package.json`, `services/geo/pyproject.toml`.
- **Priority:** 🔴 P0 (Critical)
- **Status:** 🔄 In Progress

### TICKET-0103 — PRD & Documentation Alignment
- **Summary:** Overwrite legacy DevBlueprint templates with comprehensive VAYU-RAKSHA Product Requirements and technical specifications.
- **Deliverables:** `docs/Prd.md`, `docs/FEATURE_TICKET_LIST.md`, `docs/TODO.md`.
- **Priority:** 🔴 P0 (Critical)
- **Status:** ✅ Done

### TICKET-0104 — Unified Environment & Scripting Orchestration
- **Summary:** Create workspace build, lint, and run scripts for rapid concurrent development of Python services and Next.js frontend.
- **Deliverables:** Root developer scripts, verified port bindings (Web: 3000, API: 8000).
- **Priority:** 🟠 P1 (High)
- **Status:** ⬜ Ready

---

## 🤖 EPIC-02: Five-Agent LangGraph Intelligence System

### TICKET-0201 — Shared CycloneState Schema & StateGraph Backbone
- **Summary:** Implement TypedDict schema tracking cyclone trajectory, hourly wind grid, inundation probability, 5-layer infrastructure graph, counterfactual scenarios, and action queues.
- **Deliverables:** `services/geo/src/vayu_raksha/graph/state.py`, `services/geo/src/vayu_raksha/graph/workflow.py`.
- **Priority:** 🔴 P0 (Critical)
- **Status:** ⬜ Ready

### TICKET-0202 — NIRNAY Supervisor Agent Node
- **Summary:** Orchestrator agent using Gemini 3.8 Flash with extended thinking. Routes between BHUMI, VAYU, SETU, and SANCHAR, evaluates counterfactual tradeoffs, synthesizes final DM situation report.
- **Deliverables:** `services/geo/src/vayu_raksha/agents/nirnay_supervisor.py`.
- **Priority:** 🔴 P0 (Critical)
- **Status:** ⬜ Ready

### TICKET-0203 — BHUMI Earth Intelligence Agent Node
- **Summary:** Integrates ISRO RISAT-1A SAR and GEE Sentinel-1 SAR flood masks through monsoon clouds, 30m NASADEM elevation, and WorldPop rasters.
- **Deliverables:** `services/geo/src/vayu_raksha/agents/bhumi_earth.py`.
- **Priority:** 🟠 P1 (High)
- **Status:** ⬜ Ready

### TICKET-0204 — VAYU Atmospheric Intelligence Agent Node
- **Summary:** Computes hourly Holland parametric wind vectors, storm surge corridors, and rainfall accumulation grids from IMD/ECMWF tracks and MOSDAC INSAT-3DS products.
- **Deliverables:** `services/geo/src/vayu_raksha/agents/vayu_atmosphere.py`.
- **Priority:** 🟠 P1 (High)
- **Status:** ⬜ Ready

### TICKET-0205 — SETU Infrastructure Cascade & SANCHAR Comms Nodes
- **Summary:** SETU runs the NetworkX cascade failure graph and evacuation router. SANCHAR generates 6-language alerts, IVR audio, and parametric insurance trigger payloads.
- **Deliverables:** `services/geo/src/vayu_raksha/agents/setu_cascade.py`, `services/geo/src/vayu_raksha/agents/sanchar_comms.py`.
- **Priority:** 🔴 P0 (Critical)
- **Status:** ⬜ Ready

---

## ⚙️ EPIC-03: Core Physics & Cascade Failure Engines

### TICKET-0301 — Holland (1980) Parametric Wind Field Engine
- **Summary:** High-precision numerical wind field generator converting 6-hourly storm positions into 15-minute resolution radial wind velocity and pressure profiles.
- **Deliverables:** `services/geo/src/vayu_raksha/engine/holland_wind.py`, unit test suite.
- **Priority:** 🔴 P0 (Critical)
- **Status:** ⬜ Ready

### TICKET-0302 — Bathtub + Hydrodynamic Proxy Storm Surge Model
- **Summary:** Physics-informed coastal surge calculation modeling bathymetric slope, storm forward speed, and maximum onshore wind friction to project hourly surge heights.
- **Deliverables:** `services/geo/src/vayu_raksha/engine/surge_model.py`.
- **Priority:** 🟠 P1 (High)
- **Status:** ⬜ Ready

### TICKET-0303 — NetworkX 5-Layer Infrastructure Cascade Failure Graph
- **Summary:** Directed graph $G=(V,E)$ modeling dependencies between L1 Substations $\rightarrow$ L2 Hospitals $\rightarrow$ L3 Roads $\rightarrow$ L4 Telecom $\rightarrow$ L5 Water Treatment with probabilistic failure propagation.
- **Deliverables:** `services/geo/src/vayu_raksha/engine/cascade_graph.py`.
- **Priority:** 🔴 P0 (Critical)
- **Status:** ⬜ Ready

### TICKET-0304 — Counterfactual Pre-Landfall Scenario Optimizer
- **Summary:** Evaluates pre-landfall interventions (substation de-energization, fuel pre-positioning, bridge reinforcement) to rank candidate municipal orders by $\frac{\Delta \text{Population Protected}}{\text{Cost}}$.
- **Deliverables:** `services/geo/src/vayu_raksha/engine/counterfactual.py`.
- **Priority:** 🔴 P0 (Critical)
- **Status:** ⬜ Ready

### TICKET-0305 — Flood-Penalized Evacuation Route Optimizer
- **Summary:** Modified Dijkstra routing on arterial road networks that dynamically penalizes water-logged road links to preserve safe evacuation and relief convoy corridors.
- **Deliverables:** `services/geo/src/vayu_raksha/engine/evacuation_router.py`.
- **Priority:** 🟡 P2 (Medium)
- **Status:** ⬜ Ready

---

## 🛰️ EPIC-04: ISRO Native Data & Google Earth Engine Integration

### TICKET-0401 — ISRO MOSDAC INSAT-3DS & Oceansat-3 Ingestion Client
- **Summary:** Native wrapper for ISRO Meteorological & Oceanographic Satellite Data Archival Centre (MOSDAC) fetching 10-minute cyclone intensity, cloud motion vectors, and scatterometer ocean winds.
- **Deliverables:** `services/geo/src/vayu_raksha/data/mosdac_client.py`.
- **Priority:** 🟠 P1 (High)
- **Status:** ⬜ Ready

### TICKET-0402 — ISRO RISAT-1A SAR Cloud-Penetrating Flood Client
- **Summary:** Ingestion module for Bhoonidhi RISAT-1A C-band SAR data enabling ground-truth flood inundation mapping through heavy cyclone cloud covers where optical satellites fail.
- **Deliverables:** `services/geo/src/vayu_raksha/data/risat_client.py`.
- **Priority:** 🟠 P1 (High)
- **Status:** ⬜ Ready

### TICKET-0403 — Google Earth Engine (GEE) Python Ingestion Pipeline
- **Summary:** Authenticated GEE pipeline extracting Sentinel-1 SAR GRD, NASA NASADEM 30m, JRC Surface Water, and WorldPop population rasters for coastal districts.
- **Deliverables:** `services/geo/src/vayu_raksha/data/gee_client.py`.
- **Priority:** 🟠 P1 (High)
- **Status:** ⬜ Ready

### TICKET-0404 — OpenStreetMap (OSM) Infrastructure Ingestion
- **Summary:** Overpass API harvester gathering substations, hospitals, emergency shelters, telecom towers, and arterial road networks across coastal Odisha, Andhra Pradesh, and West Bengal.
- **Deliverables:** `services/geo/src/vayu_raksha/data/osm_client.py`.
- **Priority:** 🟠 P1 (High)
- **Status:** ⬜ Ready

---

## 🎨 EPIC-05: Ultra-Premium Tactical Command HUD (Next-Gen UI)

### TICKET-0501 — Tactical Mission Control Design System & Layout
- **Summary:** Complete visual overhaul of `apps/web`: sleek dark aesthetic (`#050811`), tactical cyber glassmorphism, animated glowing telemetry indicators, and high-density command center layout.
- **Deliverables:** `apps/web/src/app/globals.css`, core layout tokens, header and status HUD.
- **Priority:** 🔴 P0 (Critical)
- **Status:** ⬜ Ready

### TICKET-0502 — Five-Agent Live Brain HUD & Telemetry Monitor
- **Summary:** Dedicated visual component displaying real-time orchestration states of NIRNAY, BHUMI, VAYU, SETU, and SANCHAR with live token telemetry, thought traces, and status badges.
- **Deliverables:** `apps/web/src/components/agent-brain-hud.tsx`.
- **Priority:** 🔴 P0 (Critical)
- **Status:** ⬜ Ready

### TICKET-0503 — Interactive Cascade Network Topology Visualizer
- **Summary:** Interactive visual graph component rendering the multi-layer infrastructure dependency network (Substations $\rightarrow$ Hospitals $\rightarrow$ Telecom $\rightarrow$ Water $\rightarrow$ Roads) with real-time failure cascade animations.
- **Deliverables:** `apps/web/src/components/cascade-graph-view.tsx`.
- **Priority:** 🔴 P0 (Critical)
- **Status:** ⬜ Ready

### TICKET-0504 — Counterfactual "What-If" Simulation Sandbox UI
- **Summary:** Interactive control drawer enabling District Collectors to toggle proactive interventions (e.g., "De-energize Substation S-7 at T-36h", "Deploy generator to ICU") and observe instant live delta in protected population.
- **Deliverables:** `apps/web/src/components/counterfactual-sandbox.tsx`.
- **Priority:** 🔴 P0 (Critical)
- **Status:** ⬜ Ready

### TICKET-0505 — 4D Tactical Geospatial Map & Radar/Satellite Overlays
- **Summary:** Enhanced Deck.gl / MapLibre map with multi-layer controls: ISRO RISAT-1A SAR flood layer, Holland wind vectors, ensemble track cones, road network closures, and pulsing critical asset markers.
- **Deliverables:** `apps/web/src/components/tactical-map.tsx`.
- **Priority:** 🔴 P0 (Critical)
- **Status:** ⬜ Ready

### TICKET-0506 — Gemini 3.8 Flash Duty Analyst with Voice & Audit Log
- **Summary:** Next-generation AI analyst interface with streaming responses, audio IVR playback, quick situational prompt chips, and cryptographic audit log for municipal order approvals.
- **Deliverables:** `apps/web/src/components/duty-analyst-panel.tsx`.
- **Priority:** 🟠 P1 (High)
- **Status:** ⬜ Ready

---

## 📢 EPIC-06: Multilingual Comms, Parametric Insurance & Historical Validation

### TICKET-0601 — Six-Language Contextual Advisory Engine
- **Summary:** Real-time generation of cultural, context-aware emergency advisories in Odia, Bengali, Telugu, Tamil, Hindi, and English with downloadable CAP 1.2 XML and PDF Collector Briefs.
- **Deliverables:** `apps/web/src/components/advisory-hub.tsx`, `services/geo/src/vayu_raksha/advisory/multilingual.py`.
- **Priority:** 🟠 P1 (High)
- **Status:** ⬜ Ready

### TICKET-0602 — Automated Parametric Insurance Trigger Event Generator
- **Summary:** Smart contract trigger module emitting JSON payout events when VAYU detects sustained winds $\ge 89\text{ km/h}$ within 50km and Sentinel-1/RISAT SAR confirms flood extent $\ge 30\%$.
- **Deliverables:** `apps/web/src/components/parametric-insurance-card.tsx`, trigger schemas.
- **Priority:** 🟠 P1 (High)
- **Status:** ⬜ Ready

### TICKET-0603 — Historical Retrospective Benchmark: Cyclone Fani (2019)
- **Summary:** Pre-loaded historical benchmark simulation of Cyclone Fani (175 km/h landfall in Odisha), demonstrating prevented cascade failures, saved hospital beds, and satellite truth validation.
- **Deliverables:** Scenario datasets for Fani 2019, Dana 2024, and Amphan 2020.
- **Priority:** 🟠 P1 (High)
- **Status:** ⬜ Ready

### TICKET-0604 — End-to-End Test Suite, Demo Video Preparation & CI/CD
- **Summary:** Unit tests for cascade graph and wind algorithms, end-to-end integration tests, and presentation documentation.
- **Deliverables:** `tests/test_cascade.py`, `tests/test_holland.py`, GitHub Actions workflow.
- **Priority:** 🟡 P2 (Medium)
- **Status:** ⬜ Ready

---
*Created for paired step-by-step execution. Ready for user command.*
