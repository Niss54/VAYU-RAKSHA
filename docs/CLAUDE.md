# 🤖 CLAUDE.md — WeightGuard

> This file is read by **Claude Code** and other Claude AI tools to understand the WeightGuard project.
> Keep this file up-to-date as the codebase evolves.
> **Do not delete this file** — it is Claude's primary context source for this repository.

---

## 🧠 Project Summary

**WeightGuard** is a Python-based security tool that scans AI/ML model weight files for steganographic malware — hidden payloads embedded inside neural network weight tensors.

**Competition context:** Built for the **GE HealthCare Precision Care Challenge 2026 (PCC 2026)** as a proof-of-concept to demonstrate AI supply-chain security in healthcare settings.

**Core idea:**
> AI model files (`.pt`, `.h5`, `.safetensors`) can carry hidden payloads in their weight values via LSB manipulation or entropy manipulation — bypassing traditional antivirus tools. WeightGuard detects these anomalies using statistical analysis.

---

## 📁 Repository Structure

```
weightguard/
│
├── CLAUDE.md                    ← You are here
├── ACCEPTANCE_REPORT.md         ← PCC 2026 submission tracking
├── AGENTS.md                    ← AI agent pipeline documentation
├── DEPLOYMENT.md                ← Deployment guide
├── DEMO_SCRIPT.md               ← Live demo script for judges
├── ADMIN_HANDBOOK.md            ← Operations runbook
│
├── weightguard/                 ← Main Python package
│   ├── __init__.py
│   ├── pipeline.py              ← Orchestrates agents sequentially
│   ├── cli.py                   ← CLI entry point (python -m weightguard.cli)
│   ├── api.py                   ← FastAPI REST endpoints
│   │
│   ├── core/
│   │   ├── context.py           ← ScanContext dataclass (shared agent state)
│   │   ├── base.py              ← BaseAgent abstract class
│   │   └── config.py            ← Config loader (weightguard.config.yml)
│   │
│   └── agents/
│       ├── __init__.py
│       ├── ingest_agent.py      ← Loads model file into tensors
│       ├── entropy_agent.py     ← Shannon entropy scan per layer
│       ├── lsb_agent.py         ← LSB chi-square anomaly detection
│       ├── cluster_agent.py     ← Isolation Forest outlier detection
│       ├── report_agent.py      ← Generates JSON verdict + report
│       └── quarantine_agent.py  ← Moves flagged files to quarantine
│
├── api/
│   ├── routes/
│   │   ├── scan.py              ← POST /scan endpoint
│   │   └── reports.py           ← GET /reports/:scan_id endpoint
│   └── schemas.py               ← Pydantic request/response models
│
├── tests/
│   ├── agents/                  ← Unit tests per agent
│   ├── integration/             ← End-to-end pipeline tests
│   └── fixtures/                ← Benign + synthetic malicious model files
│
├── reports/                     ← Auto-generated scan reports (gitignored)
├── quarantine/                  ← Quarantined model files (gitignored)
├── models/                      ← Test model files (gitignored)
│
├── weightguard.config.yml       ← Agent configuration
├── pyproject.toml               ← Project metadata + dependencies
├── requirements.txt             ← Pinned dependencies
├── Dockerfile                   ← Container image
├── docker-compose.yml           ← Local dev stack
└── .env.example                 ← Environment variable template
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.11+ | Core implementation |
| **ML / Tensors** | PyTorch 2.x | Loading and analyzing weight tensors |
| **Stats** | NumPy, SciPy | Entropy calculation, chi-square test |
| **Clustering** | scikit-learn | Isolation Forest for outlier detection |
| **HDF5 Support** | h5py | Reading `.h5` / `.hdf5` model files |
| **SafeTensors** | safetensors | Reading HuggingFace `.safetensors` files |
| **API** | FastAPI + Uvicorn | REST API for scan endpoint |
| **Validation** | Pydantic v2 | Request / response schema validation |
| **CLI** | Click / argparse | Command-line scan interface |
| **Testing** | pytest + pytest-cov | Unit and integration tests |
| **Containerization** | Docker + Compose | Portable deployment |

---

## ⚡ Common Commands

### Setup

```bash
# Clone and install
git clone https://github.com/Niss54/WeightGuard.git
cd WeightGuard
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Copy env vars
cp .env.example .env
```

### Running

```bash
# CLI — scan a model file
python -m weightguard.cli scan ./models/test_model.pt

# CLI — with verbose output
python -m weightguard.cli scan ./models/test_model.pt --verbose

# API server (development)
uvicorn weightguard.api:app --reload --port 8000

# API server via Docker
docker compose up -d

# Health check
curl http://localhost:8000/health
```

### Testing

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/agents/ -v

# Integration tests
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=weightguard --cov-report=html

# Generate synthetic test models
python -m weightguard.cli generate-test-model --type lsb --output ./models/malicious_lsb.pt
python -m weightguard.cli generate-test-model --type clean --output ./models/clean_test.pt
```

### Development

```bash
# Format code
black weightguard/ tests/

# Lint
ruff check weightguard/ tests/

# Type check
mypy weightguard/

# Run all checks at once
make check    # if Makefile is present
```

---

## 🔑 Key Concepts Claude Must Know

### 1. ScanContext is the Single Source of Truth

All agents read from and write to one `ScanContext` dataclass. Never let agents call each other directly.

```python
# Always import context from here:
from weightguard.core.context import ScanContext

# Risk score accumulates across agents — each agent ADDS to it, never resets it
ctx.risk_score += 0.1   # Correct ✅
ctx.risk_score = 0.0    # Never do this ❌
```

### 2. Agents are Stateless Modules

Agents do not store any state between `run()` calls. All state lives in `ScanContext`.

```python
class MyAgent(BaseAgent):
    name = "MyAgent"
    
    def run(self, ctx: ScanContext) -> None:
        # Read from ctx → process → write back to ctx
        # Never use self.some_cache or self.previous_result ❌
```

### 3. Weight Tensor Format

All agents work with `torch.Tensor` values loaded by `IngestAgent`:

```python
# Weight tensors are always float32, shape varies by layer
# ctx.weight_tensors is: dict[str (layer_name), torch.Tensor]

for name, tensor in ctx.weight_tensors.items():
    flat = tensor.float().numpy().flatten()  # Always flatten first
    # flat is now a 1D NumPy array of float32 values
```

### 4. Risk Score Interpretation

```python
# Do NOT clamp risk_score inside agents
# ReportAgent clamps it: min(ctx.risk_score, 1.0) before verdict

# Verdict thresholds (in ReportAgent):
# 0.00 – 0.30 → "clean"
# 0.30 – 0.65 → "suspicious"
# 0.65 – 1.00 → "malicious"
```

### 5. Config Loading

```python
# Access agent config via self.config
threshold = self.config.get("agents", {}).get("LSBAgent", {}).get("chi2_pvalue_threshold", 0.05)

# Agents check self.is_enabled() automatically via BaseAgent
# You can disable any agent in weightguard.config.yml
```

---

## 🌐 API Reference (Quick)

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/scan` | POST | Upload + scan a model file |
| `/reports/{scan_id}` | GET | Fetch a previous scan report |
| `/reports` | GET | List all scan reports |

### POST /scan Example

```bash
curl -X POST http://localhost:8000/scan \
  -F "file=@./models/test_model.pt" \
  -F "strict=false"

# Response
{
  "scan_id": "abc123...",
  "verdict": "clean",
  "risk_score": 0.0,
  "risk_flags": [],
  "report_url": "/reports/abc123..."
}
```

---

## 🚫 What NOT to Do

```
❌ Do NOT add business logic inside pipeline.py — agents handle logic
❌ Do NOT let agents import or call other agents directly
❌ Do NOT add state to agent classes (use ScanContext)
❌ Do NOT modify ctx.weight_tensors after IngestAgent runs
❌ Do NOT hardcode file paths — use environment variables
❌ Do NOT commit model files to git (they are gitignored for size reasons)
❌ Do NOT commit .env file (only .env.example)
❌ Do NOT fabricate detection accuracy numbers in documentation
```

---

## ✅ Code Conventions

```python
# File naming: snake_case for all Python files
# Class naming: PascalCase for agents and classes
# Constants: UPPER_SNAKE_CASE
# Agent names: register in self.name = "AgentName"

# All agent files go in: weightguard/agents/
# All core files go in: weightguard/core/
# All tests mirror source: tests/agents/ mirrors weightguard/agents/

# Every public function must have a type hint
def run(self, ctx: ScanContext) -> None:  # ✅
def run(self, ctx):                       # ❌

# Log using self.log(), not print()
self.log(ctx, "Scan complete")   # ✅
print("Scan complete")           # ❌
```

---

## 🔗 Important File Links

| File | Purpose |
|---|---|
| `weightguard/core/context.py` | **Start here** to understand the data model |
| `weightguard/pipeline.py` | Understand agent execution order |
| `weightguard/agents/entropy_agent.py` | Core detection logic example |
| `tests/integration/test_full_pipeline.py` | See full pipeline behavior |
| `AGENTS.md` | Full agent documentation |
| `DEPLOYMENT.md` | How to run in production |

---

## 🗂️ Environment Variables

```bash
# Required
REPORTS_DIR=./reports             # Where JSON scan reports are saved
QUARANTINE_DIR=./quarantine       # Where flagged models are moved

# Optional
LOG_LEVEL=INFO                    # DEBUG | INFO | WARNING | ERROR
ALERT_WEBHOOK=                    # Slack/webhook URL for quarantine alerts
ALERT_EMAIL=                      # Email for critical alerts
CONFIG_PATH=./weightguard.config.yml  # Custom config location

# API
HOST=0.0.0.0
PORT=8000
```

---

## 🧪 Creating Test Model Files

For reproducible testing, use the built-in test model generator:

```python
# tests/fixtures/generate_fixtures.py

import torch

def make_clean_model():
    """Standard normally distributed weights — should pass all checks."""
    return {
        "layer1.weight": torch.randn(256, 128),
        "layer1.bias": torch.randn(256),
        "layer2.weight": torch.randn(128, 64),
        "layer2.bias": torch.randn(128),
    }

def make_lsb_injected_model():
    """LSB-manipulated weights — should fail LSBAgent."""
    state = make_clean_model()
    for name, tensor in state.items():
        raw = tensor.view(torch.int32)
        payload = torch.zeros_like(raw)
        payload[::2] = 1            # Set every other LSB to 1 (non-random pattern)
        state[name] = (raw | payload).view(torch.float32)
    return state
```

---

*WeightGuard — Claude, you now have full context. When making code changes, always check `AGENTS.md` for the agent contract and `context.py` for the data model. Good luck! 🛡️*
