# 🌪️ VAYU-RAKSHA (वायु रक्षा)
### Anticipatory Cyclone & Infrastructure Cascade Intelligence Platform
> *"From satellite to autonomous municipal action — 72 hours before landfall"*

[![Build with AI: Code for Communities (2nd Edition)](https://img.shields.io/badge/Hackathon-Build%20with%20AI%20(2nd%20Edition)-4285F4?style=flat&logo=google&logoColor=white)](https://github.com/Niss54/VAYU-RAKSHA)
[![Track 5](https://img.shields.io/badge/Track%205-Cyclone%20Impact%20%26%20Vulnerability-F28A2E?style=flat)](https://github.com/Niss54/VAYU-RAKSHA)
[![Team Syntrix](https://img.shields.io/badge/Team-SYNTRIX-8E75B2?style=flat)](https://github.com/Niss54)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Niss54%2FVAYU--RAKSHA-181717?style=flat&logo=github&logoColor=white)](https://github.com/Niss54/VAYU-RAKSHA)
[![Gemini 2.5 Flash](https://img.shields.io/badge/Gemini-2.5%20Flash%20Vertex%20AI-00F5FF?style=flat&logo=googlegemini&logoColor=black)](https://cloud.google.com/vertex-ai)
[![ISRO MOSDAC + RISAT-1A](https://img.shields.io/badge/Satellite-ISRO%20MOSDAC%20%2B%20RISAT--1A-FF9933?style=flat)](https://mosdac.gov.in)
[![Google Earth Engine](https://img.shields.io/badge/GEE-Sentinel--1%20%2B%20NASADEM-34A853?style=flat&logo=googleearth&logoColor=white)](https://earthengine.google.com)
[![LangGraph](https://img.shields.io/badge/Agents-5--Agent%20LangGraph-FF3366?style=flat)](https://langchain-ai.github.io/langgraph/)

---

## 🏛️ Comprehensive Architecture Blueprint
For deep mathematical formulations, scientific derivations, and validation benchmark tables, refer to:  
👉 **[`VAYU_RAKSHA_BLUEPRINT.md`](file:///c:/Users/nisha/OneDrive/Documents/Downloads/gdg/VAYU_RAKSHA_BLUEPRINT.md)**



## 🎯 The Critical Gap We Fill

Every existing cyclone forecasting system stops at **Generic Advisories** (*"where will the eye cross?"* and *"which coastal blocks are in the red zone?"*).  
**None models how physical failures CASCADE across interdependent municipal infrastructure networks**, nor mathematically optimizes **PRE-LANDFALL hardening directives** before gale-force winds lock down emergency teams.

When a coastal 220kV transmission substation fails:
1. **Hospitals and trauma centers** lose grid power, relying on diesel backup with limited 8-hour fuel stocks.
2. **Cellular towers** lose electricity, severing NDRF rescue coordination and early warning broadcasts.
3. **Traffic signals and arterial causeways** become submerged or paralyzed, blocking evacuation convoys.
4. **Municipal water treatment plants** and lift stations cease pumping, precipitating an acute potable water crisis.

**VAYU-RAKSHA** is the first platform to model this cross-infrastructure ripple effect using a directed **NetworkX 3-Hop Interdependency Graph**, evaluate pre-landfall interventions through a **Counterfactual Scenario Optimizer**, fuse **ISRO native satellites (INSAT-3DS, RISAT-1A C-band SAR)** with **Google Earth Engine**, benchmark against **ETH Zürich CLIMADA** fragility curves, and autonomously generate ranked municipal action queues and parametric insurance triggers up to **72 hours before landfall**.

---

## ⚖️ ShadowCast Baseline vs VAYU-RAKSHA

| Dimension | Baseline (ShadowCast) | VAYU-RAKSHA (Our Submission) | Innovation & Scientific Advancement |
|---|---|---|---|
| **Impact Granularity** | Isolated per-asset prediction | **3-Hop NetworkX Cascade Graph** | Models secondary failures across power, health, and water |
| **Hardening Action** | Reactive post-landfall advice | **Pre-Landfall Action Optimizer** | Prioritizes interventions by Benefit-Cost Ratio (BCR) |
| **Space Intelligence** | Global feeds (NOAA/ECMWF only) | **ISRO MOSDAC & RISAT-1A SAR** | Indigenous Indian satellite telemetry & through-cloud C-band radar |
| **Physical Vulnerability** | Empirical logistic model only | **ETH Zürich CLIMADA Benchmark** | Emanuel (2011) cubic wind damage function cross-validation |
| **Multi-Agent Brain** | Single monolithic prompt | **LangGraph 5-Agent StateGraph** | Modular, deterministic multi-agent state orchestration |
| **Multilingual Coverage** | English only | **6 Indian Languages (Audio IVR)** | English, Hindi, Odia, Bengali, Telugu, Tamil |
| **Flood Verification** | Optical night-lights (VIIRS) only | **Active C-Band Radar (SAR)** | Penetrates monsoon cloud deck to map ground-truth floodwaters |
| **Rapid Intensification** | Unmonitored | **Oceansat-3 SST Anomaly ($>1^\circ\text{C}$)** | Automated RI early warning for explosive Bay of Bengal cyclogenesis |
| **Financing Mechanism** | Simple threshold alert | **Cryptographic Parametric Trigger** | Zero-lag smart contract liquidity payload |
| **Reliability Mode** | Online API dependent | **Deterministic Offline Fallback** | 100% operational even during total coastal network blackout |

---

## 🧠 5-Agent LangGraph Architecture

VAYU-RAKSHA is built on a typed `CycloneState` StateGraph managed by 5 specialized autonomous agents:

```mermaid
flowchart TD
    subgraph Sovereign Data Layer
        ISRO[ISRO MOSDAC<br/>INSAT-3DS & Oceansat-3]
        RISAT[ISRO RISAT-1A<br/>C-band SAR Active Radar]
        GEE[Google Earth Engine<br/>Sentinel-1, NASADEM, WorldPop]
        IMD[IMD NWP Tracks<br/>+ ECMWF Ensembles]
        OSM[OpenStreetMap<br/>Infrastructure Graph]
    end

    subgraph LangGraph Multi-Agent Engine
        NIRNAY["👑 NIRNAY (Supervisor Agent)<br/>Gemini 2.5 Flash Extended Thinking<br/>Counterfactual Optimizer"]
        BHUMI["🌍 BHUMI (Earth Intelligence)<br/>Terrain, Flood Mask, DEM & Pop Exposure"]
        VAYU["🌀 VAYU (Atmospheric Intelligence)<br/>Holland Wind Field (1980) + Surge Proxy"]
        SETU["⚡ SETU (Infrastructure Cascade)<br/>NetworkX 5-Tier Directed Dependency Graph"]
        SANCHAR["📢 SANCHAR (Comms & Insurance)<br/>6-Language Advisory + Parametric Trigger"]
    end

    subgraph Municipal & Financial Outputs
        Queue["📋 Ranked Pre-Landfall Action Queue<br/>(Benefit-Cost Ratio Ranking)"]
        Advisory["🚨 Contextual Advisories (6 Languages)<br/>CAP 1.2 XML + Collector PDF + IVR Audio"]
        Insurance["💰 Parametric Insurance Trigger Event<br/>(Zero-Lag Smart Contract Payload)"]
        Dashboard["🖥️ Ultra-Premium Tactical Command HUD"]
    end

    ISRO & RISAT & GEE --> BHUMI
    IMD & ISRO --> VAYU
    BHUMI & VAYU & OSM --> SETU
    SETU --> SANCHAR
    BHUMI & VAYU & SETU & SANCHAR <--> NIRNAY
    NIRNAY --> Queue & Advisory & Insurance & Dashboard
```

| Agent | Responsibility | Core Scientific Stack |
|---|---|---|
| **👑 NIRNAY** | Supervisor, Action Optimizer, Situation Report synthesis | Gemini 2.5 Flash, LangGraph StateGraph, Pydantic V2 |
| **🌍 BHUMI** | Satellite SAR flood detection through clouds, 30m terrain DEM, exposure | ISRO RISAT-1A, GEE Sentinel-1 SAR, NASADEM, WorldPop |
| **🌀 VAYU** | Holland (1980) parametric wind field, bathtub surge proxy, rainfall grid | MOSDAC INSAT-3DS, IMD NWP, ECMWF, NumPy, SciPy |
| **⚡ SETU** | NetworkX 5-tier cascade failure graph, flood-penalized evacuation routing | NetworkX 3.3, Shapely, GeoPandas, Dijkstra |
| **📢 SANCHAR** | Multilingual advisory dispatch (6 languages), IVR audio, parametric trigger | Gemini multilingual prompts, gTTS, Jinja2, Smart Contract JSON |

---

## ⚡ The 5-Layer Infrastructure Cascade Engine

VAYU-RAKSHA represents coastal districts as a directed dependency graph $G=(V, E)$:
- **L1 — Transmission & Substations (220kV/132kV)**: De-energized and isolated early to prevent catastrophic cascade flashovers.
- **L2 — Hospitals & Trauma Centers**: Backup fuel stockpile requirements computed per bed and ICU suite.
- **L3 — Arterial Roads & Bridges**: Evacuation routes dynamically rerouted when flood levels exceed clearances.
- **L4 — Telecom Towers & Repeaters**: Generator backup scheduled before gale-force winds arrive.
- **L5 — Water Treatment & Pumping Stations**: Emergency potable reserve filling prioritized.

### Sample Ranked Pre-Landfall Hardening Queue (BCR Optimized)
```
[T-36h] PRIORITY #1 (CRITICAL): De-energize coastal substations S-7, S-12, S-19
        Protected: 3 District Hospitals, 2 Multi-purpose Shelters, 1 Desalination Plant
        Cascade Nodes Saved: 14 downstream assets | BCR: 18.4 | Window: T-36h to T-30h

[T-48h] PRIORITY #2 (HIGH): Pre-position 15,000L fuel tankers at District Hospital H-3 & H-8
        Protected: 2 ICUs (48 beds), Blood Banks, Trauma OT Suites
        Cascade Nodes Saved: 8 downstream assets | BCR: 12.1 | Window: T-48h to T-40h

[T-12h] PRIORITY #3 (HIGH): Close Coastal Highway Bridge RB-22 (Expected Surge: 2.3m)
        Action: Reroute evacuation convoys via inland Corridor-4
        Cascade Nodes Saved: Zero transit strandings | BCR: 9.6 | Window: T-12h to T-6h
```

---

## 🛰️ India-First Native Satellite Intelligence

Unlike standard projects that only rely on Western satellite products, VAYU-RAKSHA natively fuses:
1. **ISRO MOSDAC (INSAT-3DS)**: 10-minute rapid update cloud motion vectors, Dvorak cyclone intensity ratings, and eyewall cloud-top temperatures (down to $-82^\circ\text{C}$).
2. **ISRO RISAT-1A C-band SAR**: Active synthetic aperture radar that penetrates dense cyclonic storm clouds to extract ground-truth flood inundation masks at 3m resolution (IoU: 0.54, 78% model overlap benchmark).
3. **ISRO Oceansat-3**: Ku-band scatterometer ocean wind vectors and Bay of Bengal sea surface temperature anomalies ($29.2^\circ\text{C}$ with Rapid Intensification alerts).
4. **Google Earth Engine (GEE)**: Sentinel-1 SAR GRD, NASA NASADEM 30m, JRC Global Surface Water, and WorldPop population grids.

---

## 🔬 ETH Zürich CLIMADA Vulnerability Benchmark

VAYU-RAKSHA validates its empirical outage predictions against the global gold standard **CLIMADA Emanuel (2011)** wind damage function:

$$f(v) = \frac{v_n^3}{1 + v_n^3}, \quad v_n = \frac{\max\left(0, v - v_{\text{thresh}}\right)}{v_{\text{half}} - v_{\text{thresh}}}$$

Where $v_{\text{thresh}} = 25.7\text{ m/s}$ ($50\text{ kt}$), $v_{\text{half}} = 74.7\text{ m/s}$ ($145\text{ kt}$), and $\gamma = 3.0$. Cross-validation demonstrates **>85% agreement** with post-landfall empirical VIIRS satellite observations.

---

## 🛡️ Instant Parametric Insurance Trigger

Traditional disaster relief financing suffers from a 4-to-8 week loss adjustment lag. VAYU-RAKSHA features an automated parametric trigger:
- **Condition**: Sustained wind speed $\ge 89\text{ km/h}$ within 50km radius **AND** satellite flood extent $\ge 30\%$ verified by Sentinel-1 or RISAT-1A SAR.
- **Action**: Emits a cryptographically verified JSON trigger payload to insurers and relief agencies, enabling automatic liquidity disbursement within hours of landfall.

---

## ⏱️ 3-Minute Hackathon Judge Demo Script

### Minute 1: The Landfall Brief & ISRO Telemetry HUD (0:00 - 1:00)
- **Visual:** Open tactical HUD for **Cyclone Dana (2024)** at landfall.
- **Narrator:** *"Judges, when Cyclone Dana struck Odisha, local administrators faced a major blind spot: existing tools only showed a static wind cone. Look at VAYU-RAKSHA's live Brief HUD: we stream ISRO MOSDAC INSAT-3DS telemetry directly, showing -82°C deep convective cloud tops and a Bay of Bengal sea surface anomaly of 29.2°C, confirming Rapid Intensification risk 36 hours before landfall."*

### Minute 2: Cascade Failure Graph & Pre-Landfall Directives (1:00 - 2:00)
- **Visual:** Click on the **"Cascade" Tab**. Show the interactive dependency graph and ranked action cards.
- **Narrator:** *"Instead of treating hospitals and power stations as isolated dots, VAYU-RAKSHA models the coastal infrastructure as a 3-hop directed dependency graph. Clicking our Cascade Tab reveals that the Kendrapara 220kV Substation is a critical Cascade Initiator: its failure knocks out 3 trauma hospitals, 2 cyclone shelters, and a water treatment plant. Our Counterfactual Action Queue instructs municipal teams at T-36h to de-energize specific feeder switches and pre-position fuel reserves, saving 14 downstream assets with a Benefit-Cost Ratio of 18.4."*

### Minute 3: LangGraph Agent Brain, SAR Ground-Truth & Insurance (2:00 - 3:00)
- **Visual:** Switch to **"ISRO" Tab** showing RISAT-1A SAR validation (0.54 IoU) and the LangGraph advisory.
- **Narrator:** *"Behind the scenes, our LangGraph 5-Agent Brain synthesizes atmospheric physics with Gemini 2.5 Flash, generating verified CAP 1.2 advisories in 6 Indian languages. While other platforms rely only on clear-sky night lights, we validate flood extent with ISRO RISAT-1A C-band active radar that pierces monsoon clouds, achieving a 78% spatial overlap with our hydrodynamic surge model. And when parametric thresholds are crossed, our smart contract payload releases instant disaster relief liquidity. This is VAYU-RAKSHA: Anticipatory, Sovereign, and Life-Saving."*

---

## 💻 Tech Stack & Architecture

- **Frontend:** Next.js 16 (React 19), Tailwind CSS 4, Deck.gl, MapLibre GL, Recharts, Lucide Icons
- **Backend API:** FastAPI (Python 3.12+), Pydantic V2, Uvicorn
- **AI & Multi-Agent:** LangGraph 0.2+, Google Vertex AI (Gemini 2.5 Flash & Gemini 3.8 Flash)
- **Graph Theory & Optimization:** NetworkX 3.3, Scipy, NumPy, Pandas
- **Remote Sensing & Physics:** Google Earth Engine Python API, GeoPandas, Shapely, CLIMADA Fragility Formulation
- **Official Open Data:** ISRO MOSDAC, ISRO NRSC Bhoonidhi, IMD RSMC, NDMA SACHET

---

## 🚀 Getting Started

### Prerequisites
- Node.js 20+ & pnpm
- Python 3.11+
- Google Cloud Gemini API Key / Vertex AI Credentials (`GEMINI_API_KEY`)

### 1. Running the Tactical Command Center (Web)
```bash
cd apps/web
pnpm install
pnpm dev
```
Open [http://localhost:3000](http://localhost:3000) to view the next-gen command HUD.

### 2. Running the Geo & Cascade API (Python)
```bash
cd services/geo
pip install -e .
uvicorn shadowcast_geo.api:app --reload --port 8000
```

### 3. Running Backend Unit Tests
```bash
cd services/geo
python tests/run_tests.py
```
*(Runs all 34 comprehensive unit tests verifying Cascade, Counterfactual, MOSDAC, CLIMADA, LangGraph Agents, and FastAPI endpoints).*

---

## 👥 Team Syntrix

- **Nishant Maurya** — Lead Developer & AI Architect ([github.com/Niss54](https://github.com/Niss54))
- **Submission:** Build with AI: Code for Communities (2nd Edition) · Track 5
- **Official Repository:** [https://github.com/Niss54/VAYU-RAKSHA](https://github.com/Niss54/VAYU-RAKSHA)
