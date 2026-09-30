# 🛡️ VAYU-RAKSHA — Recheck & Verification List
> **Status:** Current codebase state audit (Built vs Active)  
> **Target:** Verification checklist of all existing modules, APIs, UI, and infrastructure.

---

## 1. Executive Summary: What We Have Already Built

In the previous sprints, we achieved high visual fidelity, full frontend interactivity, live payment flows, containerized orchestration, and Cloudinary storage. Here is the verified status of all existing assets:

```
[✅ VERIFIED LIVE] Next.js 16 Web Dashboard (Port 3000)
[✅ VERIFIED LIVE] 5-Agent LangGraph HUD & Thought Stream UI
[✅ VERIFIED LIVE] 4D Tactical Command Map UI & Layer Toggles
[✅ VERIFIED LIVE] 5-Tier Cascade Failure Topology Visualizer UI
[✅ VERIFIED LIVE] Counterfactual Action Optimizer UI (What-If Sandbox)
[✅ VERIFIED LIVE] 6-Language Multilingual Advisory Hub & Voice IVR Player
[✅ VERIFIED LIVE] Parametric Smart Trigger & RazorpayX Simulation
[✅ VERIFIED LIVE] Razorpay India SDRF Disaster Relief Donation Modal
[✅ VERIFIED LIVE] Gemini Duty Analyst Co-pilot UI & Extended Thinking Chat
[✅ VERIFIED LIVE] Cloudinary Storage Integration (Replaced AWS S3 / R2)
[✅ VERIFIED LIVE] Multi-Stage Docker Orchestration (Dev & Prod)
[✅ VERIFIED LIVE] Python Geo Engine on Cloud Run (Holland wind, surge, VIIRS)
```

---

## 2. Component-by-Component Recheck Checklist

### A. Frontend Core & UI Components (`apps/web/src/components`)

| Component | File Path | What is Built | How to Re-test / Verify | Status |
|:---|:---|:---|:---|:---:|
| **Main Mission HUD Console** | [`vayu-console.tsx`](file:///c:/Users/nisha/OneDrive/Documents/Downloads/gdg/apps/web/src/components/vayu-console.tsx) | Header HUD, peak wind, surge, landfall T-hours, scenario switcher (`Fani`, `Dana`, `Amphan`), tab orchestrator | Click scenario buttons in header; watch metrics update dynamically. | ✅ Verified |
| **5-Agent Brain HUD** | [`agent-brain-hud.tsx`](file:///c:/Users/nisha/OneDrive/Documents/Downloads/gdg/apps/web/src/components/agent-brain-hud.tsx) | Pipeline latency tracker (194.6ms), individual agent state chips (NIRNAY, BHUMI, VAYU, SETU, SANCHAR) with confidence % | Switch scenario; verify agent status and thought trace updates. | ✅ Verified |
| **4D Tactical GIS Map** | [`tactical-command-map.tsx`](file:///c:/Users/nisha/OneDrive/Documents/Downloads/gdg/apps/web/src/components/tactical-command-map.tsx) | Radar flood mask layer, Holland wind field, Surge crest contours, Road corridors toggle, Timeline scrubber slider (T-48h to Landfall) | Navigate to `4D Tactical GIS Map` tab; toggle each layer and drag timeline slider. | ✅ Verified |
| **Cascade Failure Topology** | [`cascade-topology-canvas.tsx`](file:///c:/Users/nisha/OneDrive/Documents/Downloads/gdg/apps/web/src/components/cascade-topology-canvas.tsx) | 5-Tier dependency chain (L1 Power Grid -> L2 Hospitals/Shelters -> L3 Road Bridges -> L4 Telecom -> L5 Water Treatment), node inspector panel | Click any node (e.g. `Balikuda Coastal Substation`); inspect failure probability and population impact. | ✅ Verified |
| **What-If Counterfactual Sandbox** | [`counterfactual-sandbox.tsx`](file:///c:/Users/nisha/OneDrive/Documents/Downloads/gdg/apps/web/src/components/counterfactual-sandbox.tsx) | Pre-landfall action cards ranked by BCR, real-time recalculation of Protected Citizens and Saved Downstream Nodes | Click `AUTHORIZE ORDER` on Action #3; verify total protected citizens increases to +1,34,000. | ✅ Verified |
| **Multilingual Advisory Hub** | [`multilingual-advisory-hub.tsx`](file:///c:/Users/nisha/OneDrive/Documents/Downloads/gdg/apps/web/src/components/multilingual-advisory-hub.tsx) | 6-Language localized advisories (Odia, Hindi, English, Bengali, Telugu, Tamil), IVR Voice Broadcast audio player, CAP 1.2 XML trigger | Click `Hindi` / `Odia`; verify localized warning bulletin; click `Play IVR Audio`. | ✅ Verified |
| **Parametric Smart Trigger Engine** | [`parametric-smart-trigger.tsx`](file:///c:/Users/nisha/OneDrive/Documents/Downloads/gdg/apps/web/src/components/parametric-smart-trigger.tsx) | Multi-sensor threshold verification (Wind >= 89 km/h, SAR Flood >= 30%), RazorpayX automated SDRF liquidity disbursement simulation | Click `⚡ EXECUTE RAZORPAYX DIRECT BENEFIT DISBURSEMENT`; check UTR generation. | ✅ Verified |
| **Razorpay Relief Fund Modal** | [`razorpay-relief-modal.tsx`](file:///c:/Users/nisha/OneDrive/Documents/Downloads/gdg/apps/web/src/components/razorpay-relief-modal.tsx) | 4 Dedicated relief campaigns (Puri Food Shield, Balasore Microgrid, Kendrapara Shelter, Gram Panchayat SDRF), amount chips, contributor inputs, Razorpay checkout hook | Click `₹ RELIEF DISASTER FUND` header button; select campaign & amount; enter name/email. | ✅ Verified |
| **Duty Analyst Co-pilot** | Embedded in [`vayu-console.tsx`](file:///c:/Users/nisha/OneDrive/Documents/Downloads/gdg/apps/web/src/components/vayu-console.tsx) & [`prepare-panel.tsx`](file:///c:/Users/nisha/OneDrive/Documents/Downloads/gdg/apps/web/src/components/prepare-panel.tsx) | Gemini 3.8 Flash duty analyst prompt box, quick action directives, extended thinking response streaming | Click `Why is Puri Hospital ICU at risk?` or type a custom prompt. | ✅ Verified |

---

### B. Storage & Cloud APIs

| Module | File Path | What is Built | How to Re-test / Verify | Status |
|:---|:---|:---|:---|:---:|
| **Cloudinary File Storage Client** | [`apps/web/src/lib/storage.ts`](file:///c:/Users/nisha/OneDrive/Documents/Downloads/gdg/apps/web/src/lib/storage.ts) | Server-side Cloudinary v2 SDK client, credentials loaded from env, MIME type validation, IPv4 socket fallback for Node Windows | Verified with live upload test; credentials active on `x9sncqcz`. | ✅ Verified |
| **Upload API Route** | [`apps/web/src/app/api/upload/route.ts`](file:///c:/Users/nisha/OneDrive/Documents/Downloads/gdg/apps/web/src/app/api/upload/route.ts) | `POST /api/upload` endpoint supporting images (JPEG, PNG, WebP), PDFs, and Audio (WAV, MP3, WebM), returns Cloudinary `secure_url` | Run: `curl.exe -F "file=@test.png" http://localhost:3000/api/upload` | ✅ Verified |

---

### C. DevOps, Containerization & Repository

| Target | File Path | What is Built | How to Re-test / Verify | Status |
|:---|:---|:---|:---|:---:|
| **Next.js Web Dockerfile** | [`apps/web/Dockerfile`](file:///c:/Users/nisha/OneDrive/Documents/Downloads/gdg/apps/web/Dockerfile) | Multi-stage Node 20 alpine container with standalone output optimization and unprivileged user | `docker build -t vayu-raksha-web -f apps/web/Dockerfile .` | ✅ Verified |
| **Docker Compose Dev** | [`docker-compose.dev.yml`](file:///c:/Users/nisha/OneDrive/Documents/Downloads/gdg/docker-compose.dev.yml) | Hot-reloading development container with local volume mounts | `docker compose -f docker-compose.dev.yml up` | ✅ Verified |
| **Docker Compose Prod** | [`docker-compose.prod.yml`](file:///c:/Users/nisha/OneDrive/Documents/Downloads/gdg/docker-compose.prod.yml) | Production container setup with healthchecks, restart policies, and environment bindings | `docker compose -f docker-compose.yml -f docker-compose.prod.yml config` | ✅ Verified |
| **Git Repository** | `origin/main` | Clean git history with all Cloudinary and Docker commits pushed to `github.com/Niss54/gdg` | `git status` | ✅ Verified |

---

### D. Base ShadowCast Python Geo Engine

| Python Module | File Path | What is Currently in Repo | Status |
|:---|:---|:---|:---:|
| **Holland Wind Hazard** | `services/geo/src/shadowcast_geo/hazard.py` | Holland (1980) vortex model, Willoughby RMW, R-CLIPER rainfall | ✅ Built |
| **Storm Surge 1D** | `services/geo/src/shadowcast_geo/surge.py` | Wind setup + inverse barometer bathymetric transects | ✅ Built |
| **VIIRS Outage Calibration** | `services/geo/src/shadowcast_geo/calibration.py` | Logistic outage model fitted on VIIRS night-lights | ✅ Built |
| **Single-Asset Ranking** | `services/geo/src/shadowcast_geo/ranking.py` | `Score = P(outage) * criticality / 5` (Per-asset only) | ✅ Built (Needs Cascade Extension) |
| **FastAPI Core Endpoints** | `services/geo/src/shadowcast_geo/api.py` | `/scenarios`, `/assets`, `/timeline`, `/live`, `/snapshots` | ✅ Built (Needs 4 New Endpoints) |
| **Cloud Run Production Deployment** | `https://shadowcast-geo-489356738785.asia-south1.run.app` | Live geo service responding with 4 scenarios (`fani-2019`, `dana-2024`, `hudhud-2014`, `amphan-2020`) | ✅ Active & Healthy |

---

## 3. The Gap Analysis: What is Missing from `VAYU_RAKSHA_CLAUDE.md`?

While the Next.js UI already mocks and displays cascade topologies, what-if sliders, and agent states, **the actual Python backend scientific algorithms from `VAYU_RAKSHA_CLAUDE.md` do NOT yet exist in `services/geo`**:

1. ❌ **`cascade.py`** is missing: No real NetworkX 3-hop belief propagation algorithm in Python.
2. ❌ **`counterfactual.py`** is missing: No backend Benefit-Cost Ratio (BCR) optimizer engine.
3. ❌ **`mosdac.py`** is missing: No ISRO MOSDAC INSAT-3DS & Oceansat-3 SST anomaly client.
4. ❌ **`risat_sar.py`** is missing: No C-band SAR flood validation (IoU) calculation engine.
5. ❌ **`climada_curves.py`** is missing: No ETH Zürich CLIMADA Emanuel fragility curves.
6. ❌ **`agents/` directory** is missing: No Python LangGraph 5-agent state graph pipeline.
7. ❌ **API Endpoints** are missing: `/cascade`, `/isro`, `/sar`, `/climada` not registered in `api.py`.
8. ❌ **Models & Schemas**: `models.py` lacks the extended Pydantic schemas.
9. ❌ **Unit Tests**: No `test_cascade.py`, `test_mosdac.py`, `test_counterfactual.py`, `test_climada_curves.py`.
10. ❌ **Judge Submission Blueprint**: `VAYU_RAKSHA_BLUEPRINT.md` does not yet exist.

All of these missing components are systematically organized into the **Product Requirements Document (`VAYU_RAKSHA_PRD.md`)** below.
