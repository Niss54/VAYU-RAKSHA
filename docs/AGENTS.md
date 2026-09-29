# 🤖 Agents — WeightGuard AI Pipeline

> **Project:** WeightGuard — Steganographic Malware Detection in AI Model Weights
> **Agent Framework:** Multi-Agent Scanning Pipeline
> **Runtime:** Python 3.11+ | PyTorch | NumPy | FastAPI
> **Last Updated:** 2026-09-23

---

## 📑 Table of Contents

1. [Agent System Overview](#1-agent-system-overview)
2. [Pipeline Architecture](#2-pipeline-architecture)
3. [Agent Definitions](#3-agent-definitions)
   - [IngestAgent](#-ingestagent)
   - [EntropyAgent](#-entropyagent)
   - [LSBAgent](#-lsbagent)
   - [ClusterAgent](#-clusterAgent)
   - [ReportAgent](#-reportagent)
   - [QuarantineAgent](#-quarantineagent)
4. [Agent Communication Protocol](#4-agent-communication-protocol)
5. [Threat Model per Agent](#5-threat-model-per-agent)
6. [Configuration](#6-configuration)
7. [Adding a New Agent](#7-adding-a-new-agent)
8. [Testing Agents](#8-testing-agents)
9. [Related Documents](#9-related-documents)

---

## 🧠 1. Agent System Overview

WeightGuard uses a **sequential multi-agent pipeline** to scan AI model weight files for signs of steganographic malware. Each agent is a specialized, stateless module responsible for one detection layer. Agents pass a shared `ScanContext` object downstream.

```
┌─────────────────────────────────────────────────────────────────┐
│                   WeightGuard Agent Pipeline                     │
│                                                                   │
│  [Model File]                                                     │
│      │                                                            │
│      ▼                                                            │
│  IngestAgent  ──→  EntropyAgent  ──→  LSBAgent  ──→  ClusterAgent│
│                                                                   │
│                                             │                     │
│                                             ▼                     │
│                                      ReportAgent                  │
│                                             │                     │
│                           ┌────────────────┴───────────────┐     │
│                           │                                │     │
│                    CLEAN  ▼                     SUSPECT    ▼     │
│                 [Pass / Log]              QuarantineAgent         │
│                                                  │               │
│                                           [Isolate + Alert]      │
└─────────────────────────────────────────────────────────────────┘
```

### Design Principles

| Principle | Description |
|---|---|
| **Single Responsibility** | Each agent does exactly one detection job |
| **Stateless** | Agents do not store scan state between runs |
| **Composable** | Agents can be enabled / disabled via config |
| **Fail-Safe** | If an agent crashes, pipeline logs error and continues |
| **Auditable** | Every agent action is logged with timestamp + risk_delta |

---

## 🏗️ 2. Pipeline Architecture

### Shared Context Object

All agents receive and mutate a single `ScanContext` as they execute:

```python
# weightguard/core/context.py

from dataclasses import dataclass, field
from typing import Optional
import torch

@dataclass
class ScanContext:
    # Input
    file_path: str
    file_format: str                   # "pt" | "h5" | "safetensors" | "onnx"
    
    # Loaded weights
    weight_tensors: dict[str, torch.Tensor] = field(default_factory=dict)
    
    # Risk tracking
    risk_score: float = 0.0            # 0.0 (clean) → 1.0 (critical)
    risk_flags: list[str] = field(default_factory=list)
    
    # Per-agent results
    entropy_map: dict[str, float] = field(default_factory=dict)
    lsb_anomalies: dict[str, float] = field(default_factory=dict)
    cluster_flags: list[str] = field(default_factory=list)
    
    # Final verdict
    verdict: Optional[str] = None      # "clean" | "suspicious" | "malicious"
    report_path: Optional[str] = None
    quarantined: bool = False
    
    # Metadata
    scan_id: str = ""
    started_at: str = ""
    completed_at: str = ""
```

### Pipeline Runner

```python
# weightguard/pipeline.py

from weightguard.agents import (
    IngestAgent, EntropyAgent, LSBAgent,
    ClusterAgent, ReportAgent, QuarantineAgent
)
from weightguard.core.context import ScanContext
import uuid, datetime

class WeightGuardPipeline:
    def __init__(self, config: dict):
        self.agents = [
            IngestAgent(config),
            EntropyAgent(config),
            LSBAgent(config),
            ClusterAgent(config),
            ReportAgent(config),
            QuarantineAgent(config),
        ]
    
    def run(self, file_path: str) -> ScanContext:
        ctx = ScanContext(
            file_path=file_path,
            file_format=file_path.rsplit(".", 1)[-1],
            scan_id=str(uuid.uuid4()),
            started_at=datetime.datetime.utcnow().isoformat(),
        )
        
        for agent in self.agents:
            if agent.is_enabled():
                try:
                    agent.run(ctx)
                except Exception as e:
                    ctx.risk_flags.append(f"[{agent.name}] ERROR: {str(e)}")
        
        ctx.completed_at = datetime.datetime.utcnow().isoformat()
        return ctx
```

---

## 🔍 3. Agent Definitions

---

### 📥 IngestAgent

**Purpose:** Loads the model weight file into memory and validates its format.

| Property | Value |
|---|---|
| **File** | `weightguard/agents/ingest_agent.py` |
| **Input** | `ctx.file_path`, `ctx.file_format` |
| **Output** | `ctx.weight_tensors` populated |
| **Fail Behavior** | Raises `IngestError` — pipeline aborts |
| **Risk Impact** | None (detection hasn't started) |

```python
# weightguard/agents/ingest_agent.py

import torch
import h5py
from safetensors import safe_open
from weightguard.core.context import ScanContext
from weightguard.core.base import BaseAgent

class IngestAgent(BaseAgent):
    name = "IngestAgent"

    def run(self, ctx: ScanContext) -> None:
        fmt = ctx.file_format.lower()

        if fmt in ("pt", "pth"):
            state_dict = torch.load(ctx.file_path, map_location="cpu")
            ctx.weight_tensors = {
                k: v for k, v in state_dict.items()
                if isinstance(v, torch.Tensor)
            }

        elif fmt == "safetensors":
            with safe_open(ctx.file_path, framework="pt", device="cpu") as f:
                ctx.weight_tensors = {k: f.get_tensor(k) for k in f.keys()}

        elif fmt == "h5":
            import numpy as np
            with h5py.File(ctx.file_path, "r") as f:
                def load_weights(group, prefix=""):
                    for key in group.keys():
                        item = group[key]
                        full_key = f"{prefix}/{key}" if prefix else key
                        if isinstance(item, h5py.Dataset):
                            ctx.weight_tensors[full_key] = torch.tensor(item[()])
                        else:
                            load_weights(item, prefix=full_key)
                load_weights(f)
        else:
            raise ValueError(f"Unsupported format: {fmt}")

        self.log(ctx, f"Loaded {len(ctx.weight_tensors)} weight tensors from {fmt}")
```

**Supported Formats:**

| Format | Extension | Framework |
|---|---|---|
| PyTorch | `.pt`, `.pth` | PyTorch |
| SafeTensors | `.safetensors` | HuggingFace |
| HDF5 | `.h5`, `.hdf5` | Keras / TensorFlow |
| ONNX | `.onnx` | ONNX Runtime |

---

### 📊 EntropyAgent

**Purpose:** Computes Shannon entropy for each weight tensor. Unusually high or low entropy suggests abnormal weight distributions — a key indicator of steganographic content.

| Property | Value |
|---|---|
| **File** | `weightguard/agents/entropy_agent.py` |
| **Input** | `ctx.weight_tensors` |
| **Output** | `ctx.entropy_map`, `ctx.risk_score` updated |
| **Fail Behavior** | Logs warning; skips affected layers |
| **Risk Impact** | +0.1 per layer flagged as anomalous |

```python
# weightguard/agents/entropy_agent.py

import numpy as np
from scipy.stats import entropy as scipy_entropy
from weightguard.core.context import ScanContext
from weightguard.core.base import BaseAgent

ENTROPY_NORMAL_RANGE = (0.5, 7.5)   # Empirically derived from benign model corpus

class EntropyAgent(BaseAgent):
    name = "EntropyAgent"

    def run(self, ctx: ScanContext) -> None:
        for name, tensor in ctx.weight_tensors.items():
            flat = tensor.float().numpy().flatten()

            # Compute histogram-based entropy
            hist, _ = np.histogram(flat, bins=256, density=True)
            hist = hist[hist > 0]
            layer_entropy = float(scipy_entropy(hist))

            ctx.entropy_map[name] = layer_entropy

            lo, hi = ENTROPY_NORMAL_RANGE
            if layer_entropy < lo or layer_entropy > hi:
                ctx.risk_score += 0.1
                ctx.risk_flags.append(
                    f"[EntropyAgent] Anomalous entropy={layer_entropy:.4f} in layer '{name}'"
                )

        self.log(ctx, f"Entropy scan complete. {len(ctx.entropy_map)} layers analyzed.")
```

**Entropy Thresholds:**

| Entropy Range | Classification | Risk Delta |
|---|---|---|
| `0.5 – 7.5` | Normal distribution | `+0.0` |
| `< 0.5` | Suspiciously uniform (possible overwriting) | `+0.1` |
| `> 7.5` | Suspiciously random (possible embedded payload) | `+0.1` |

---

### 🔬 LSBAgent

**Purpose:** Inspects the Least Significant Bits (LSBs) of floating-point weight values. Steganographic tools often embed data in LSBs — this agent performs statistical analysis to detect non-random LSB patterns.

| Property | Value |
|---|---|
| **File** | `weightguard/agents/lsb_agent.py` |
| **Input** | `ctx.weight_tensors` |
| **Output** | `ctx.lsb_anomalies`, `ctx.risk_score` updated |
| **Fail Behavior** | Logs warning; skips layer |
| **Risk Impact** | +0.15 per layer with LSB chi-square failure |

```python
# weightguard/agents/lsb_agent.py

import struct
import numpy as np
from scipy.stats import chisquare
from weightguard.core.context import ScanContext
from weightguard.core.base import BaseAgent

LSB_CHI2_PVALUE_THRESHOLD = 0.05   # p < 0.05 → reject null (non-random LSBs)
MIN_TENSOR_SIZE = 1000              # Skip tiny layers (not enough data)

class LSBAgent(BaseAgent):
    name = "LSBAgent"

    def _extract_lsbs(self, tensor_np: np.ndarray) -> np.ndarray:
        """Extract the least significant bit of float32 byte representation."""
        flat = tensor_np.flatten().astype(np.float32)
        raw_bytes = flat.view(np.uint32)
        lsbs = (raw_bytes & 0x1).astype(np.uint8)
        return lsbs

    def run(self, ctx: ScanContext) -> None:
        for name, tensor in ctx.weight_tensors.items():
            flat = tensor.float().numpy()

            if flat.size < MIN_TENSOR_SIZE:
                continue

            lsbs = self._extract_lsbs(flat)
            ones = int(np.sum(lsbs))
            zeros = len(lsbs) - ones

            # Chi-square test: expect 50/50 split in truly random weights
            observed = np.array([zeros, ones])
            expected = np.array([len(lsbs) / 2, len(lsbs) / 2])
            _, p_value = chisquare(observed, expected)

            ctx.lsb_anomalies[name] = p_value

            if p_value < LSB_CHI2_PVALUE_THRESHOLD:
                ctx.risk_score += 0.15
                ctx.risk_flags.append(
                    f"[LSBAgent] Non-random LSB pattern (p={p_value:.5f}) in layer '{name}'"
                )

        self.log(ctx, f"LSB scan complete. {len(ctx.lsb_anomalies)} layers checked.")
```

---

### 🧩 ClusterAgent

**Purpose:** Uses statistical clustering to identify weight tensors that are outliers relative to the model's own weight distribution. Embedded payloads often create statistically distinct weight clusters.

| Property | Value |
|---|---|
| **File** | `weightguard/agents/cluster_agent.py` |
| **Input** | `ctx.weight_tensors`, `ctx.entropy_map` |
| **Output** | `ctx.cluster_flags`, `ctx.risk_score` updated |
| **Fail Behavior** | Logs warning; skips |
| **Risk Impact** | +0.2 per outlier cluster detected |

```python
# weightguard/agents/cluster_agent.py

import numpy as np
from sklearn.ensemble import IsolationForest
from weightguard.core.context import ScanContext
from weightguard.core.base import BaseAgent

CONTAMINATION = 0.05   # Expected fraction of outlier layers

class ClusterAgent(BaseAgent):
    name = "ClusterAgent"

    def run(self, ctx: ScanContext) -> None:
        if len(ctx.weight_tensors) < 5:
            self.log(ctx, "Too few layers for cluster analysis. Skipping.")
            return

        # Feature vector per layer: [mean, std, min, max, entropy]
        features = []
        layer_names = []

        for name, tensor in ctx.weight_tensors.items():
            flat = tensor.float().numpy().flatten()
            entropy = ctx.entropy_map.get(name, 0.0)
            features.append([
                float(np.mean(flat)),
                float(np.std(flat)),
                float(np.min(flat)),
                float(np.max(flat)),
                entropy,
            ])
            layer_names.append(name)

        X = np.array(features)
        clf = IsolationForest(contamination=CONTAMINATION, random_state=42)
        preds = clf.fit_predict(X)   # -1 = outlier, 1 = inlier

        for name, pred in zip(layer_names, preds):
            if pred == -1:
                ctx.cluster_flags.append(name)
                ctx.risk_score += 0.2
                ctx.risk_flags.append(
                    f"[ClusterAgent] Statistical outlier layer detected: '{name}'"
                )

        self.log(ctx, f"Cluster scan complete. {len(ctx.cluster_flags)} outlier(s) flagged.")
```

---

### 📄 ReportAgent

**Purpose:** Computes final verdict, generates a structured JSON + PDF report, and determines the scan outcome.

| Property | Value |
|---|---|
| **File** | `weightguard/agents/report_agent.py` |
| **Input** | Full `ScanContext` (all agents complete) |
| **Output** | `ctx.verdict`, `ctx.report_path` |
| **Fail Behavior** | Logs error; verdict defaults to "unknown" |
| **Risk Impact** | None (reporting only) |

```python
# weightguard/agents/report_agent.py

import json, os, datetime
from weightguard.core.context import ScanContext
from weightguard.core.base import BaseAgent

RISK_THRESHOLDS = {
    "clean":      (0.00, 0.30),
    "suspicious": (0.30, 0.65),
    "malicious":  (0.65, 9999),
}

class ReportAgent(BaseAgent):
    name = "ReportAgent"

    def run(self, ctx: ScanContext) -> None:
        # Determine verdict
        score = min(ctx.risk_score, 1.0)
        for verdict, (lo, hi) in RISK_THRESHOLDS.items():
            if lo <= score < hi:
                ctx.verdict = verdict
                break

        # Build JSON report
        report = {
            "scan_id": ctx.scan_id,
            "file": ctx.file_path,
            "format": ctx.file_format,
            "started_at": ctx.started_at,
            "completed_at": ctx.completed_at,
            "risk_score": round(score, 4),
            "verdict": ctx.verdict,
            "risk_flags": ctx.risk_flags,
            "layers_scanned": len(ctx.weight_tensors),
            "entropy_map": {k: round(v, 6) for k, v in ctx.entropy_map.items()},
            "lsb_anomalies": {k: round(v, 6) for k, v in ctx.lsb_anomalies.items()},
            "cluster_flags": ctx.cluster_flags,
        }

        # Save report
        reports_dir = os.environ.get("REPORTS_DIR", "./reports")
        os.makedirs(reports_dir, exist_ok=True)
        report_path = os.path.join(reports_dir, f"{ctx.scan_id}.json")

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        ctx.report_path = report_path
        self.log(ctx, f"Report saved → {report_path} | Verdict: {ctx.verdict.upper()}")
```

**Verdict Thresholds:**

| Verdict | Risk Score Range | Action |
|---|---|---|
| ✅ **clean** | `0.00 – 0.30` | Pass — model is safe |
| ⚠️ **suspicious** | `0.30 – 0.65` | Flag — manual review recommended |
| 🚨 **malicious** | `0.65 – 1.00` | Quarantine immediately |

---

### 🔒 QuarantineAgent

**Purpose:** If verdict is `suspicious` or `malicious`, moves the model file to a quarantine directory and triggers an alert.

| Property | Value |
|---|---|
| **File** | `weightguard/agents/quarantine_agent.py` |
| **Input** | `ctx.verdict`, `ctx.file_path` |
| **Output** | File moved to quarantine; `ctx.quarantined = True` |
| **Fail Behavior** | Logs critical error; does NOT delete file |
| **Risk Impact** | None (remediation only) |

```python
# weightguard/agents/quarantine_agent.py

import os, shutil
from weightguard.core.context import ScanContext
from weightguard.core.base import BaseAgent

QUARANTINE_VERDICTS = {"suspicious", "malicious"}

class QuarantineAgent(BaseAgent):
    name = "QuarantineAgent"

    def run(self, ctx: ScanContext) -> None:
        if ctx.verdict not in QUARANTINE_VERDICTS:
            self.log(ctx, f"Verdict is '{ctx.verdict}' — no quarantine needed.")
            return

        quarantine_dir = os.environ.get("QUARANTINE_DIR", "./quarantine")
        os.makedirs(quarantine_dir, exist_ok=True)

        filename = os.path.basename(ctx.file_path)
        dest = os.path.join(quarantine_dir, f"{ctx.scan_id}_{filename}")
        shutil.move(ctx.file_path, dest)

        ctx.quarantined = True
        ctx.risk_flags.append(
            f"[QuarantineAgent] File moved to quarantine: {dest}"
        )
        self.log(ctx, f"🚨 QUARANTINED → {dest}")

        # TODO: Send alert (Slack / Email / Webhook)
        self._send_alert(ctx, dest)

    def _send_alert(self, ctx: ScanContext, dest: str) -> None:
        """Placeholder for alerting integration (Slack / email / webhook)."""
        # Example: POST to webhook
        pass
```

---

## 📡 4. Agent Communication Protocol

Agents communicate **only** through the shared `ScanContext`. No agent calls another agent directly.

```
Agent Input / Output Contract
─────────────────────────────────────────────────
Agent           Reads                   Writes
─────────────────────────────────────────────────
IngestAgent     file_path, file_format  weight_tensors
EntropyAgent    weight_tensors          entropy_map, risk_score, risk_flags
LSBAgent        weight_tensors          lsb_anomalies, risk_score, risk_flags
ClusterAgent    weight_tensors,         cluster_flags, risk_score, risk_flags
                entropy_map
ReportAgent     (all fields)            verdict, report_path
QuarantineAgent verdict, file_path      quarantined (bool), risk_flags
─────────────────────────────────────────────────
```

### Base Agent Class

```python
# weightguard/core/base.py

import logging
from abc import ABC, abstractmethod
from weightguard.core.context import ScanContext

logger = logging.getLogger("weightguard")

class BaseAgent(ABC):
    name: str = "BaseAgent"

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def run(self, ctx: ScanContext) -> None:
        """Execute agent logic. Mutates ctx in-place."""
        ...

    def is_enabled(self) -> bool:
        return self.config.get("agents", {}).get(self.name, {}).get("enabled", True)

    def log(self, ctx: ScanContext, message: str) -> None:
        logger.info(f"[{self.name}] [scan={ctx.scan_id[:8]}] {message}")
```

---

## 🎯 5. Threat Model per Agent

| Agent | Threat Detected | Attack Type |
|---|---|---|
| `IngestAgent` | Corrupted / malformed model files | Format exploit |
| `EntropyAgent` | Hidden payloads via entropy manipulation | Steganography |
| `LSBAgent` | LSB-encoded data in float32 weights | Bit-level steganography |
| `ClusterAgent` | Injected weight clusters (outlier layers) | Weight poisoning |
| `ReportAgent` | — (aggregator) | — |
| `QuarantineAgent` | — (remediator) | — |

---

## ⚙️ 6. Configuration

```yaml
# weightguard.config.yml

pipeline:
  strict_mode: false         # If true: any single agent flag → quarantine immediately
  reports_dir: "./reports"
  quarantine_dir: "./quarantine"

agents:
  IngestAgent:
    enabled: true

  EntropyAgent:
    enabled: true
    normal_range: [0.5, 7.5]

  LSBAgent:
    enabled: true
    chi2_pvalue_threshold: 0.05
    min_tensor_size: 1000

  ClusterAgent:
    enabled: true
    contamination: 0.05

  ReportAgent:
    enabled: true
    formats: ["json"]           # Future: ["json", "pdf"]

  QuarantineAgent:
    enabled: true
    alert_webhook: ""           # POST webhook URL for alerts (optional)
    alert_email: ""             # SMTP alert email (optional)
```

---

## 🔌 7. Adding a New Agent

To add a detection layer:

```python
# 1. Create file: weightguard/agents/my_new_agent.py

from weightguard.core.base import BaseAgent
from weightguard.core.context import ScanContext

class MyNewAgent(BaseAgent):
    name = "MyNewAgent"

    def run(self, ctx: ScanContext) -> None:
        # Your detection logic here
        # Read from ctx, write findings back to ctx
        ctx.risk_flags.append("[MyNewAgent] Found something suspicious")
        ctx.risk_score += 0.1

# 2. Register in weightguard/pipeline.py
from weightguard.agents import MyNewAgent
# Add to self.agents list in WeightGuardPipeline.__init__

# 3. Add config entry in weightguard.config.yml
# agents:
#   MyNewAgent:
#     enabled: true
```

---

## 🧪 8. Testing Agents

```bash
# Run all agent unit tests
pytest tests/agents/ -v

# Run specific agent
pytest tests/agents/test_entropy_agent.py -v

# Run with coverage
pytest tests/agents/ --cov=weightguard.agents --cov-report=html

# Scan a specific model file
python -m weightguard.cli scan ./models/test_model.pt

# Scan with verbose output
python -m weightguard.cli scan ./models/test_model.pt --verbose

# Generate synthetic malicious model for testing
python -m weightguard.cli generate-test-model --inject-lsb ./models/malicious_test.pt
```

### Test Fixtures

```
tests/
├── agents/
│   ├── test_ingest_agent.py
│   ├── test_entropy_agent.py
│   ├── test_lsb_agent.py
│   ├── test_cluster_agent.py
│   ├── test_report_agent.py
│   └── test_quarantine_agent.py
├── fixtures/
│   ├── benign_model.pt          ← Clean model (known safe)
│   ├── lsb_injected_model.pt    ← Synthetic LSB payload
│   ├── entropy_anomaly.pt       ← High-entropy injected layer
│   └── cluster_outlier.pt       ← Statistical outlier layers
└── integration/
    └── test_full_pipeline.py     ← End-to-end pipeline test
```

---

## 🔗 9. Related Documents

| Document | Purpose |
|---|---|
| [ACCEPTANCE_REPORT.md](./ACCEPTANCE_REPORT.md) | PCC 2026 competition submission tracking |
| [CLAUDE.md](./CLAUDE.md) | Claude AI project context — onboarding for AI tools |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | How to deploy WeightGuard in production |
| [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) | Step-by-step live demo guide for judges |
| [ADMIN_HANDBOOK.md](./ADMIN_HANDBOOK.md) | Operations and admin runbook |

---

**WeightGuard Agents — Multi-Layer Defense for AI Model Integrity 🛡️**
