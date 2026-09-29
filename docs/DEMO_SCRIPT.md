# 🎬 Demo Script — WeightGuard

> **Competition:** GE HealthCare Precision Care Challenge 2026
> **Demo Type:** Live Technical Demonstration
> **Total Duration:** 5–8 minutes
> **Presenter:** Nishant Maurya
> **Last Updated:** 2026-09-23
> **Audience:** GE HealthCare Judges + Panel

---

## 📑 Table of Contents

1. [Pre-Demo Setup](#1-pre-demo-setup)
2. [Demo Flow Overview](#2-demo-flow-overview)
3. [Scene 1 — Opening Hook (60 sec)](#3-scene-1--opening-hook-60-sec)
4. [Scene 2 — Problem Statement (60 sec)](#4-scene-2--problem-statement-60-sec)
5. [Scene 3 — Live Demo: Clean Model Scan (90 sec)](#5-scene-3--live-demo-clean-model-scan-90-sec)
6. [Scene 4 — Live Demo: Malicious Model Scan (90 sec)](#6-scene-4--live-demo-malicious-model-scan-90-sec)
7. [Scene 5 — How It Works (60 sec)](#7-scene-5--how-it-works-60-sec)
8. [Scene 6 — Healthcare Impact (30 sec)](#8-scene-6--healthcare-impact-30-sec)
9. [Scene 7 — Closing & Q&A Prep (30 sec)](#9-scene-7--closing--qa-prep-30-sec)
10. [Anticipated Q&A](#10-anticipated-qa)
11. [Fallback Plans](#11-fallback-plans)
12. [Terminal Commands Cheatsheet](#12-terminal-commands-cheatsheet)

---

## ⚙️ 1. Pre-Demo Setup

> ⚠️ **Do this 30 minutes before the demo. Do not skip.**

### Checklist

- [ ] Laptop charged to 100% — power adapter plugged in
- [ ] WeightGuard running locally on Docker (`docker compose up -d`)
- [ ] Cloud URL accessible: `https://weightguard.onrender.com/health` → `200 OK`
- [ ] Terminal open → `cd WeightGuard` → logs visible
- [ ] Browser open on `http://localhost:8000/health`
- [ ] Test models ready in `./models/`:
  - `clean_model.pt` — benign ResNet-18 weights
  - `malicious_lsb.pt` — LSB-injected model (synthetic)
- [ ] `DEMO_SCRIPT.md` open on second screen (phone / tablet)
- [ ] Slides open (if needed as backup visual): `WeightGuard_PCC2026.pptx`

### Environment State

```bash
# Confirm everything is running
docker compose ps
# → weightguard   Up    0.0.0.0:8000->8000/tcp

curl http://localhost:8000/health
# → { "status": "ok", "agents": 6, ... }

# Clear previous reports for a clean demo
rm -f reports/*.json
ls reports/
# → (empty)
```

### Screen Layout (Recommended)

```
┌─────────────────────┬──────────────────────┐
│                     │                      │
│   TERMINAL          │   BROWSER            │
│   (docker logs)     │   localhost:8000     │
│                     │                      │
├─────────────────────┴──────────────────────┤
│   SLIDES / DEMO_SCRIPT (secondary screen)  │
└────────────────────────────────────────────┘
```

---

## 🗺️ 2. Demo Flow Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   WEIGHTGUARD DEMO (7 min)                  │
├──────────┬────────────────────────────────┬─────────────────┤
│ SCENE    │ CONTENT                        │ TIME            │
├──────────┼────────────────────────────────┼─────────────────┤
│ 1        │ Opening Hook — The threat       │ 0:00 – 1:00    │
│ 2        │ Problem Statement               │ 1:00 – 2:00    │
│ 3        │ LIVE: Clean model scan          │ 2:00 – 3:30    │
│ 4        │ LIVE: Malicious model scan      │ 3:30 – 5:00    │
│ 5        │ How It Works (agents)           │ 5:00 – 6:00    │
│ 6        │ Healthcare Impact               │ 6:00 – 6:30    │
│ 7        │ Closing + invite Q&A            │ 6:30 – 7:00    │
│ —        │ Q&A                             │ 7:00 – 10:00   │
└──────────┴────────────────────────────────┴─────────────────┘
```

---

## 🎤 3. Scene 1 — Opening Hook (60 sec)

**[No terminal visible yet. Look directly at judges.]**

> **SAY:**
> *"Imagine your hospital just deployed a new AI model for chest X-ray diagnosis.*
> *Your cybersecurity team scanned it — antivirus says it's clean.*
> *It passes hash verification.*
> *But hidden inside its 70 million weight values... is a dormant malware payload,*
> *waiting to activate once the model is in production.*
> *Traditional security tools cannot see it — because it's hiding inside the math.*
> *That is the threat WeightGuard was built to solve."*

**[Pause 2 seconds. Let it land.]**

> **SAY:**
> *"My name is Nishant Maurya, and I built WeightGuard — a multi-layer scanning engine*
> *that detects steganographic malware embedded inside AI model weight files.*
> *Let me show you how it works — live."*

---

## 🎤 4. Scene 2 — Problem Statement (60 sec)

**[Optionally show Slide 1 from the deck, or just speak.]**

> **SAY:**
> *"The attack is called model weight steganography.*
> *An attacker distributes a pre-trained model — say, a publicly available diagnostic AI.*
> *Before sharing it, they manipulate the Least Significant Bits of the floating-point weights.*
> *To any statistical tool, these weights look normal.*
> *But they're carrying a hidden binary payload — a reverse shell, a ransomware dropper, a data exfiltration script.*
> *Once the hospital loads and runs the model, the payload executes.*"*

> **SAY:**
> *"Healthcare is especially vulnerable because:*
> *One — diagnostic AI models are increasingly downloaded from public repos.*
> *Two — there's no standard protocol for scanning model files.*
> *Three — traditional antivirus doesn't understand tensor math."*

> **SAY:**
> *"WeightGuard fills that gap."*

---

## 💻 5. Scene 3 — Live Demo: Clean Model Scan (90 sec)

**[Switch to terminal. Full screen or split with browser.]**

> **SAY:** *"Let me start with a clean model — a standard ResNet-18 trained on ImageNet."*

```bash
# Run this command live
python -m weightguard.cli scan ./models/clean_model.pt --verbose
```

**[While it runs — narrate the output]**

> **SAY:** *"You can see WeightGuard loading 62 weight layers... running entropy analysis... LSB chi-square test... clustering... and here — the verdict."*

**[Point to the output]**

```
[IngestAgent] Loaded 62 weight tensors from pt
[EntropyAgent] Entropy scan complete. 62 layers analyzed.
[LSBAgent] LSB scan complete. 61 layers checked.
[ClusterAgent] Cluster scan complete. 0 outlier(s) flagged.
[ReportAgent] Report saved → ./reports/abc123.json | Verdict: CLEAN

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  WeightGuard Scan Result
  File     : clean_model.pt
  Verdict  : ✅  CLEAN
  Risk     : 0.00 / 1.00
  Flags    : None
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

> **SAY:** *"Risk score: zero. Verdict: clean. This model is safe to deploy."*

> **SAY:** *"Let me show you the JSON report generated."*

```bash
cat reports/abc123.json | python -m json.tool | head -30
```

> **SAY:** *"Every scan produces a cryptographic, auditable JSON report — scan ID, timestamp, layer-by-layer entropy map, LSB p-values. This is your compliance record."*

---

## 💻 6. Scene 4 — Live Demo: Malicious Model Scan (90 sec)

**[Stay in terminal. This is the WOW moment.]**

> **SAY:** *"Now — let me scan a model where I've synthetically injected a steganographic payload into the LSBs of two layers."*

```bash
python -m weightguard.cli scan ./models/malicious_lsb.pt --verbose
```

**[Narrate as it runs]**

> **SAY:** *"Same pipeline... same 62 layers... but watch the LSB agent..."*

```
[IngestAgent] Loaded 62 weight tensors from pt
[EntropyAgent] Entropy scan complete. 62 layers analyzed.
[LSBAgent] ⚠️  Non-random LSB pattern (p=0.00002) in layer 'layer2.weight'
[LSBAgent] ⚠️  Non-random LSB pattern (p=0.00008) in layer 'layer3.weight'
[ClusterAgent] ⚠️  Statistical outlier layer detected: 'layer2.weight'
[ReportAgent] Report saved → ./reports/def456.json | Verdict: MALICIOUS
[QuarantineAgent] 🚨 QUARANTINED → ./quarantine/def456_malicious_lsb.pt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  WeightGuard Scan Result
  File     : malicious_lsb.pt
  Verdict  : 🚨  MALICIOUS
  Risk     : 0.80 / 1.00
  Flags    : 3 anomalies detected
  Action   : File QUARANTINED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**[Let the red output sit for a second. Then:]**

> **SAY:**
> *"Risk score: 0.80. Verdict: MALICIOUS.*
> *The file has been automatically moved to quarantine.*
> *Two layers showed non-random LSB patterns — statistically impossible in a legitimately trained model.*
> *One layer flagged as a statistical outlier by the Isolation Forest.*
> *The payload was caught before it ever touched a production system."*

> **SAY:** *"This — in under 4 seconds — is what WeightGuard does."*

---

## 🧠 7. Scene 5 — How It Works (60 sec)

**[Optional: show AGENTS.md or a quick diagram on screen]**

> **SAY:**
> *"WeightGuard runs 4 specialized detection agents in sequence:"*

> *"First — IngestAgent loads the model file. It supports PyTorch, SafeTensors, HDF5 — all major formats used in healthcare AI."*

> *"Second — EntropyAgent computes Shannon entropy per layer. Payload embedding shifts the entropy distribution away from what we expect in a normally-trained model."*

> *"Third — LSBAgent performs a chi-square test on the Least Significant Bits of every float32 weight value. Legitimate model weights have statistically random LSBs. Injected payloads don't."*

> *"Fourth — ClusterAgent uses Isolation Forest to find layers that are statistical outliers relative to the model's own weight distribution."*

> *"If any agent flags a risk, it accumulates into a composite risk score. At the end, the verdict is clean, suspicious, or malicious. Malicious → auto-quarantined."*

---

## 🏥 8. Scene 6 — Healthcare Impact (30 sec)

**[Speak clearly — this is for the judges' evaluation criteria]**

> **SAY:**
> *"In healthcare, this matters at three levels:*
>
> *Patient safety — a compromised diagnostic model could give wrong outputs, misdiagnose, harm patients.*
>
> *Data security — a payload inside a radiology AI could silently exfiltrate patient imaging data.*
>
> *Regulatory compliance — HIPAA, FDA 21 CFR Part 11, and emerging EU AI Act requirements all demand that medical AI systems be auditable and tamper-evident.*
>
> *WeightGuard provides a model provenance verification layer that addresses all three.*"*

---

## 🎤 9. Scene 7 — Closing & Q&A Prep (30 sec)

**[Look up from screen. Direct eye contact with judges.]**

> **SAY:**
> *"WeightGuard is a proof-of-concept today.*
> *But the detection techniques — entropy analysis, LSB chi-square testing, statistical clustering —*
> *are sound, well-established methods applied to a novel threat vector.*
>
> *The next step is building a production-grade scanning service that integrates with*
> *hospital AI deployment pipelines — a gate that every model must pass before it goes live.*
>
> *Thank you. I'm happy to walk through the code, the math, or the architecture.*
> *What would you like to explore?"*

**[Stop. Smile. Wait.]**

---

## ❓ 10. Anticipated Q&A

### "Can this detect all types of steganographic attacks?"

> *"WeightGuard v1 covers the most practical attack surfaces — LSB manipulation and entropy distortion, which are the dominant techniques documented in ML security research. Future versions can add pattern-match signatures for known payload structures, and we can train a detection model on a corpus of malicious vs. benign weights. No single tool is 100%, which is why we output a risk score rather than a binary — it's designed to be one layer in a defense-in-depth stack."*

### "What about false positives — could it flag a legitimate model as malicious?"

> *"Great question. We designed the thresholds based on empirical entropy ranges from a corpus of benign models. The composite risk score — rather than any single agent — reduces false positives significantly. In testing, legitimately trained models score 0.00–0.10. The 'suspicious' range (0.30–0.65) is intentionally conservative — flagging for human review rather than auto-quarantine. Only 0.65+ triggers automatic quarantine."*

### "Why not just verify the model hash?"

> *"Hash verification only tells you if the file was modified after the hash was generated. If the attacker is the one distributing the model — or if they modify it before the hash is taken — hash verification fails completely. WeightGuard analyzes the statistical properties of the weights themselves, independent of any external metadata."*

### "Is this open source?"

> *"Yes — the plan is to open-source WeightGuard post-competition. Healthcare security benefits from community review. We'd also want to collaborate with GE HealthCare's AI deployment team to calibrate the thresholds against real diagnostic model corpora."*

### "How does it perform on large models — GPT-scale?"

> *"Scanning is parallelizable per layer. For a 70B parameter model, we'd run the pipeline with batch processing and GPU tensor operations — reducing scan time to minutes rather than seconds. The architecture is designed to scale horizontally."*

### "What formats do you support?"

> *"Currently: `.pt`, `.pth` (PyTorch), `.safetensors` (HuggingFace), `.h5` / `.hdf5` (Keras/TensorFlow). ONNX is on the roadmap. These cover the vast majority of healthcare AI deployment formats."*

---

## 🆘 11. Fallback Plans

| Situation | Response |
|---|---|
| Cloud URL is down | Switch to local Docker (`localhost:8000`) — always have it running |
| Docker is not starting | Run directly: `uvicorn weightguard.api:app --port 8000` |
| CLI scan crashes | Fall back to API: `curl -X POST localhost:8000/scan -F "file=@models/clean_model.pt"` |
| No internet on demo device | Everything works offline — Docker is local-only |
| Forgot terminal command | Use [Section 12 cheatsheet](#12-terminal-commands-cheatsheet) on phone |
| Live demo fails entirely | Show saved report screenshots + walk through the slides instead |

---

## 📋 12. Terminal Commands Cheatsheet

> Print this page or keep it open on your phone as backup.

```bash
# ── HEALTH CHECK ──────────────────────────────────────
curl http://localhost:8000/health

# ── CLEAN MODEL SCAN ──────────────────────────────────
python -m weightguard.cli scan ./models/clean_model.pt --verbose

# ── MALICIOUS MODEL SCAN ──────────────────────────────
python -m weightguard.cli scan ./models/malicious_lsb.pt --verbose

# ── VIEW REPORT ───────────────────────────────────────
ls reports/
cat reports/<scan_id>.json | python -m json.tool

# ── API SCAN (Alternate) ──────────────────────────────
curl -X POST http://localhost:8000/scan \
  -F "file=@./models/clean_model.pt"

# ── DOCKER STATUS ─────────────────────────────────────
docker compose ps
docker compose logs -f weightguard

# ── RESTART IF NEEDED ─────────────────────────────────
docker compose down && docker compose up -d

# ── CLEAR REPORTS (fresh demo) ────────────────────────
rm -f reports/*.json && rm -f quarantine/*

# ── GENERATE TEST MODELS ──────────────────────────────
python -m weightguard.cli generate-test-model --type clean --output ./models/clean_model.pt
python -m weightguard.cli generate-test-model --type lsb   --output ./models/malicious_lsb.pt
```

---

## ⏱️ Timing Reference Card

```
0:00 ──── Scene 1: Opening Hook (60s)
1:00 ──── Scene 2: Problem Statement (60s)
2:00 ──── Scene 3: LIVE — Clean Model Scan (90s)
3:30 ──── Scene 4: LIVE — Malicious Model Scan (90s)  ← WOW moment
5:00 ──── Scene 5: How It Works (60s)
6:00 ──── Scene 6: Healthcare Impact (30s)
6:30 ──── Scene 7: Closing (30s)
7:00 ──── Q&A (open)
```

---

**Breathe. Speak slowly. The demo speaks for itself. You've got this. 🛡️**

*WeightGuard — GE HealthCare Precision Care Challenge 2026 | Nishant Maurya*
