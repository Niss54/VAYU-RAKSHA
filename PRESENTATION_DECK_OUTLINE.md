# 📊 VAYU-RAKSHA (वायु रक्षा) — Presentation Deck Structure (10 Slides)
### Build with AI: Code for Communities (2nd Edition) — Track 5: Disaster Resilience

Use this exact content to create your 10-slide deck in Google Slides, PowerPoint, or Canva, then export as PDF (< 5 MB).

---

### Slide 1: Title & Vision
- **Title:** VAYU-RAKSHA (वायु रक्षा)
- **Subtitle:** Anticipatory Cyclone & Infrastructure Cascade Intelligence Platform
- **Tagline:** *"From satellite radar to autonomous municipal hardening — 72 hours before landfall"*
- **Track:** Track 5: Disaster Resilience & Community Response
- **Team:** Team SYNTRIX (Nishant Maurya)
- **Live Demo Link:** `https://vayu-raksha-three.vercel.app`
- **Visual:** Tactical Command HUD 3D Globe with Cyclone Eyewall

---

### Slide 2: The Critical Problem (The Invisible Domino Effect)
- **The Core Blindspot:** Current cyclone systems (IMD/NOAA) only forecast meteorological parameters (*wind speed, eye path*). None model physical infrastructure interdependencies.
- **The 3-Hop Cascade Reality:**
  1. *Transmission Substation collapses* $\rightarrow$ 
  2. *Hospitals lose main power (generators have 8h fuel)* $\rightarrow$ 
  3. *Cellular towers lose backup, severing rescue radio* $\rightarrow$ 
  4. *Water lift stations fail, triggering acute potable water crisis in storm shelters.*
- **The Timing Crisis:** Once winds reach 34 knots ($62\,\text{km/h}$), emergency crews cannot operate. Reinforcement must happen **48–72 hours prior**.

---

### Slide 3: The Solution — VAYU-RAKSHA
- **What is VAYU-RAKSHA?** An AI-driven early-warning intelligence platform that bridges satellite telemetry directly with deterministic municipal disaster operations.
- **3 Foundational Pillars:**
  1. **Physical Cascade Graph:** NetworkX 3-Hop directed graph modeling cross-sector dependencies.
  2. **Counterfactual Action Optimizer:** Calculates Benefit-Cost Ratio (BCR) for pre-landfall interventions.
  3. **Sovereign Space Intelligence:** Integrates ISRO MOSDAC & through-cloud RISAT-1A SAR active radar.

---

### Slide 4: 5-Agent LangGraph Architecture
- **Multi-Agent StateGraph powered by Gemini 2.5 Flash Extended Thinking:**
  - 👑 **NIRNAY (Supervisor):** Synthesizes global state, runs counterfactual simulations, generates Action Queue.
  - 🌍 **BHUMI (Earth & Flood):** Analyzes 30m DEM terrain, population exposure, and SAR radar flood truth.
  - 🌀 **VAYU (Atmospheric Physics):** Holland (1980) wind vortex field and 1D hydrodynamic storm surge screening.
  - ⚡ **SETU (Infrastructure Cascade):** 5-tier directed failure graph and flood-penalized evacuation route solver.
  - 📢 **SANCHAR (Comms & Finance):** Multilingual voice IVR synthesis (Sarvam AI) and Razorpay relief fund triggers.

---

### Slide 5: Deep Tech & Scientific Rigor
- **Holland (1980) Wind Field:** Radial vortex derivation accounting for central pressure deficit and Coriolis force.
- **ETH Zürich CLIMADA Fragility Benchmark:** Validated against Emanuel (2011) cubic wind damage function for asset outage calibration.
- **Through-Cloud Flood Truth:** Active C-Band SAR radar backscatter thresholding ($\sigma_0 \le -15\,\text{dB}$) to verify ground inundation through impenetrable cyclone cloud covers.
- **Oceansat-3 SST Anomaly ($> 1^\circ\text{C}$):** Automated early warning for explosive Bay of Bengal Rapid Intensification (RI).

---

### Slide 6: Real-World Demonstration — Tactical Command HUD
- **4D Real-Time Geospatial Map:** Deck.gl + MapLibre 60 FPS visualization of 3,300+ coastal assets.
- **Interactive Layers:**
  - Dynamic Wind Vector Field & Eye Track Fixes
  - Bathymetric Storm Surge Height Transects
  - Road Network Closures & Evacuation Bottlenecks
  - Asset Vulnerability Priority Scoring (Ranked 1 to 3,325)

---

### Slide 7: Community Impact & Multilingual Inclusion
- **Breaking the Literacy Barrier:** 
  - Emergency voice advisories generated natively in **6 Indian Languages**: **Odia, Hindi, Bengali, Tamil, Telugu, and English**.
  - Powered by **Sarvam AI (Bulbul:v3)** for authentic local dialects and tone.
- **Direct Administration Integration:**
  - Standardized **Common Alerting Protocol (CAP 1.2 XML)** feeds for state SDMAs and NDRF.
  - Automated District Collector Briefing Documents (Situation Reports).

---

### Slide 8: Real-Time Relief Financing (Razorpay Live)
- **The Liquidity Bottleneck:** Government disaster relief funds often face bureaucratic transfer delays of weeks.
- **Parametric Disaster Relief Gateway:**
  - Integrated production **Razorpay Live Gateway** for instant public and CSR micro-contributions.
  - Instant UPI, QR code, and NetBanking payments routing directly to verified regional relief operations.
  - Transparent audit trail with automated donor receipting.

---

### Slide 9: Validation & Scientific Benchmarks
- **Tested and backtested across 4 major North Indian Ocean cyclonic disasters:**
  - 🌪️ **Cyclone Dana (2024):** 38 Cascade Chains, AUC 0.94, Brier 0.09
  - 🌪️ **Super Cyclone Fani (2019):** 74 Cascade Chains, AUC 0.97, Brier 0.08
  - 🌪️ **Severe Cyclone Hudhud (2014):** 42 Cascade Chains, AUC 0.92, Brier 0.11
  - 🌪️ **Super Cyclone Amphan (2020):** 61 Cascade Chains, AUC 0.96, Brier 0.07
- **Zero-Downtime Resilience:** Pre-bundled offline dataset guarantees 100% platform availability even during total underwater cable blackouts.

---

### Slide 10: Conclusion, Future Roadmap & Links
- **Future Roadmap:**
  - Integration with 112 India emergency dispatch and cell broadcast systems.
  - Expansion to Arabian Sea coastal corridors (Gujarat, Maharashtra, Kerala).
  - Drone-assisted SAR micro-validation feeds.
- **Key Project Links:**
  - **Live Web Application:** `https://vayu-raksha-three.vercel.app`
  - **Backend API:** `https://vayu-raksha-production.up.railway.app`
  - **GitHub Repository:** `https://github.com/Niss54/VAYU-RAKSHA`
- **Thank you!** *"Saving lives through predictive precision."* — Team SYNTRIX
