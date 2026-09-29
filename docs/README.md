<div align="center">

<img src="https://raw.githubusercontent.com/Niss54/DevBlueprint/main/assets/logo.png" alt="DevBlueprint Logo" width="120" />

# 🧠 DevBlueprint

### *Production-Ready Documentation Framework + AI Security Toolkit*

> **Two things in one repo:**
> `[1]` A complete full-stack project documentation starter kit  
> `[2]` The official documentation hub for **WeightGuard** — a steganographic malware detector for AI model weights, built for [GE HealthCare PCC 2026](https://www.gehealthcare.com)

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Node.js](https://img.shields.io/badge/Node.js-20.x_LTS-339933?logo=node.js&logoColor=white)](https://nodejs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?logo=next.js)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7.x-DC382D?logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](./DEPLOYMENT.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#-contributing)
[![Maintained](https://img.shields.io/badge/Maintained-Yes-green.svg)](https://github.com/Niss54/DevBlueprint)

<br/>

[📋 What Is This?](#-what-is-devblueprint) · [🛡️ WeightGuard](#️-weightguard--ai-security-tool) · [📁 All Documents](#-complete-document-index) · [🚀 Quick Start](#-quick-start) · [🏗️ Tech Stack](#️-tech-stack) · [🤝 Contributing](#-contributing)

---

</div>

## 📖 What Is DevBlueprint?

**DevBlueprint** is a two-in-one repository:

### Part 1 — Documentation Starter Kit

A battle-tested collection of **28 production-grade Markdown templates** that give any software project a structured brain before a single line of code is written. Stop googling "what docs does my project need" — everything is here.

> **The Problem:** Most projects fail not because of bad code, but because of vague requirements, missing architecture decisions, and zero process. DevBlueprint solves this from day zero.

| Without DevBlueprint | With DevBlueprint |
|---|---|
| ❌ Requirements change every week | ✅ Locked PRD with user stories + KPIs |
| ❌ Architecture decided on a whiteboard | ✅ Documented ADRs and system diagrams |
| ❌ Security bolted on after launch | ✅ OWASP Top 10 checklist baked in from day 1 |
| ❌ "It works on my machine" | ✅ Docker + CI/CD pipeline defined |
| ❌ No testing strategy | ✅ Unit / Integration / E2E pyramid defined |
| ❌ Devs argue about commit format | ✅ Conventional Commits enforced |
| ❌ New devs lost for their first two weeks | ✅ `memory.md` gives AI & humans instant context |

### Part 2 — WeightGuard Project Docs

All documentation for **WeightGuard** — a Python-based AI security tool that detects steganographic malware hidden inside neural network model weight files (`.pt`, `.h5`, `.safetensors`). Submitted to the **GE HealthCare Precision Care Challenge 2026**.

---

## 🛡️ WeightGuard — AI Security Tool

> **"AI model files can be weaponized. WeightGuard detects it."**

### The Problem

AI model weight files (`.pt`, `.h5`, `.safetensors`) can secretly carry malicious payloads hidden inside their float values via **LSB (Least Significant Bit) manipulation** — a technique borrowed from classic image steganography. Traditional antivirus tools are blind to this. A poisoned model uploaded to HuggingFace or a model registry can silently exfiltrate data, execute code, or backdoor a healthcare AI system.

### The Solution

WeightGuard is a **multi-agent scanning pipeline** that analyzes model weight tensors for:

```
Threat Vector         Detection Method
─────────────────     ──────────────────────────────────────
LSB Steganography  →  Bit-pattern entropy analysis (LSBAgent)
Statistical Noise  →  Tensor distribution anomaly scan (EntropyAgent)
Cluster Anomalies  →  Weight clustering outlier detection (ClusterAgent)
Suspicious Payload →  Quarantine + cryptographic provenance report
```

### Agent Pipeline

```
 ┌──────────────────────────────────────────────────────────┐
 │                WeightGuard Scan Pipeline                  │
 │                                                          │
 │   [Model File: .pt / .h5 / .safetensors]                │
 │        │                                                 │
 │        ▼                                                 │
 │   IngestAgent ──→ EntropyAgent ──→ LSBAgent ──→ ClusterAgent
 │                                          │               │
 │                                          ▼               │
 │                                    ReportAgent           │
 │                                          │               │
 │                         ┌───────────────┴────────────┐  │
 │                    CLEAN ▼                  SUSPECT   ▼  │
 │               [Pass / Log]            QuarantineAgent    │
 │                                             │            │
 │                                    [Isolate + Alert]     │
 └──────────────────────────────────────────────────────────┘
```

### Competition Context

| Field | Detail |
|---|---|
| **Competition** | GE HealthCare Precision Care Challenge 2026 (PCC 2026) |
| **Track** | AI Security / Adversarial Robustness |
| **Format** | Paper → Prototype → Live Demo |
| **Status** | 🟡 Under Review — Round 1 Submitted |
| **Submitter** | Nishant Maurya ([@Niss54](https://github.com/Niss54)) |
| **Demo URL** | `https://weightguard.onrender.com` |

---

## 📁 Complete Document Index

> 28 files. Each one earns its place.

### 🏗️ Core Template Documents

| File | Category | What It Contains |
|------|----------|-----------------|
| [`Prd.md`](./Prd.md) | 📋 Product | Product Requirements — personas, user stories, KPIs, MVP vs. nice-to-have |
| [`Architecture.md`](./Architecture.md) | 🏗️ Design | System design, ADRs, tech stack decision matrix, architecture diagrams |
| [`TECHNICAL_ARCHITECTURE.md`](./TECHNICAL_ARCHITECTURE.md) | 🏗️ Design | Deep-dive: data flow, component boundaries, caching strategy, scalability plan |
| [`Database.md`](./Database.md) | 🗄️ Data | Schema design, Prisma models, indexes, migration strategy, seed data |
| [`API.md`](./API.md) | 🔌 API | REST endpoints, auth headers, request/response formats, error codes |
| [`UI-UX.md`](./UI-UX.md) | 🎨 Frontend | Design system, color tokens, typography, component specs, user flows |
| [`FRONTEND_SPEC.md`](./FRONTEND_SPEC.md) | 🎨 Frontend | Complete frontend spec — pages, routing, state management, perf budgets, a11y |
| [`Testing.md`](./Testing.md) | ✅ QA | Unit / integration / E2E test strategy with code examples and coverage targets |
| [`Deployment.md`](./Deployment.md) | 🚀 DevOps | Docker, Nginx, CI/CD pipeline, monitoring, rollback strategy |
| [`Security.md`](./Security.md) | 🔒 Security | OWASP Top 10 coverage, JWT strategy, rate limiting, incident response |
| [`SECURITY_AND_ACCESS.md`](./SECURITY_AND_ACCESS.md) | 🔒 Security | RBAC design, authentication flows, audit logging, vulnerability disclosure |
| [`SECURITY_GUIDELINES_HARDENED_EXPERT.md`](./SECURITY_GUIDELINES_HARDENED_EXPERT.md) | 🔒 Security | Expert-level hardened security guidelines (advanced teams / regulated industries) |
| [`SECURITY_POLICY_HARDENED_EXPERT.md`](./SECURITY_POLICY_HARDENED_EXPERT.md) | 🔒 Security | Full organizational security policy — contracts, compliance, enforcement |
| [`FEATURE_TICKET_LIST.md`](./FEATURE_TICKET_LIST.md) | 📋 PM | Sprint ticket tracker — epics, stories, estimates, status, acceptance criteria |
| [`TODO.md`](./TODO.md) | 📋 PM | Phase-wise task tracker with progress bars and bug board |
| [`Changelog.md`](./Changelog.md) | 📝 History | Semantic versioning changelog — Keep a Changelog format |
| [`PRD_CLOSURE.md`](./PRD_CLOSURE.md) | 📋 PM | PRD sign-off report — delivery matrix, scope delta, KPI achievement, lessons learned |
| [`memory.md`](./memory.md) | 🤖 AI | AI session context file — instant project state for Claude / Copilot / Cursor |
| [`.env`](./.env) | ⚙️ Config | Fully documented environment variables with descriptions and generation commands |

### 🛡️ WeightGuard-Specific Documents

| File | Category | What It Contains |
|------|----------|-----------------|
| [`AGENTS.md`](./AGENTS.md) | 🤖 AI Pipeline | Agent definitions, `ScanContext` schema, inter-agent protocol, threat model per agent |
| [`DEPLOYMENT.md`](./DEPLOYMENT.md) | 🚀 DevOps | WeightGuard deployment — Docker, Render, Railway, GCP Cloud Run, CI/CD |
| [`ACCEPTANCE_REPORT.md`](./ACCEPTANCE_REPORT.md) | 📋 Competition | PCC 2026 submission tracker — evaluation criteria, scoring breakdown, Round 2 prep |
| [`DEMO_SCRIPT.md`](./DEMO_SCRIPT.md) | 🎬 Presentation | 5–8 min live demo script for GE HealthCare judges with fallback plans |
| [`Presentation.md`](./Presentation.md) | 🎬 Presentation | Full presentation narrative + slide notes |
| [`CLAUDE.md`](./CLAUDE.md) | 🤖 AI | Claude Code context — repo structure, active tasks, architecture for AI agents |

### 📖 Extended References

| File | What It Contains |
|------|-----------------|
| [`ReadmeEX.MD`](./ReadmeEX.MD) | Extended README with additional deep-dive sections |
| [`LICENSE`](./LICENSE) | MIT License — free to use, modify, distribute |

---

## 🏗️ Tech Stack

### Full-Stack Web Application (Template)

<table>
<tr><th>Layer</th><th>Technology</th><th>Version</th><th>Purpose</th></tr>
<tr>
  <td rowspan="5"><b>🖥️ Frontend</b></td>
  <td>Next.js (App Router)</td><td>14.x</td><td>SSR/SSG, routing, React framework</td>
</tr>
<tr><td>TypeScript</td><td>5.x</td><td>End-to-end type safety</td></tr>
<tr><td>Tailwind CSS + shadcn/ui</td><td>3.x / Latest</td><td>Styling + accessible component library</td></tr>
<tr><td>TanStack Query</td><td>v5</td><td>Server state, caching, data sync</td></tr>
<tr><td>Zustand</td><td>4.x</td><td>Lightweight client state management</td></tr>
<tr>
  <td rowspan="4"><b>⚙️ Backend</b></td>
  <td>Node.js + Express.js</td><td>20 LTS</td><td>API server runtime</td>
</tr>
<tr><td>TypeScript</td><td>5.x</td><td>Consistent type layer across stack</td></tr>
<tr><td>Prisma ORM</td><td>5.x</td><td>Type-safe database queries + migrations</td></tr>
<tr><td>Zod</td><td>3.x</td><td>Runtime input validation + schema inference</td></tr>
<tr>
  <td rowspan="2"><b>🗄️ Data</b></td>
  <td>PostgreSQL</td><td>15</td><td>Primary relational database</td>
</tr>
<tr><td>Redis</td><td>7.x</td><td>Cache, session management, rate limiting</td></tr>
<tr>
  <td rowspan="4"><b>☁️ DevOps</b></td>
  <td>Docker + Compose</td><td>24.x</td><td>Containerised dev and prod environments</td>
</tr>
<tr><td>Nginx</td><td>Latest</td><td>Reverse proxy, SSL termination, rate limiting</td></tr>
<tr><td>GitHub Actions</td><td>—</td><td>CI/CD pipeline (test → build → deploy)</td></tr>
<tr><td>Sentry</td><td>—</td><td>Error monitoring + performance tracking</td></tr>
</table>

### WeightGuard AI Security Tool

| Component | Technology | Purpose |
|---|---|---|
| **Runtime** | Python 3.11+ | Agent pipeline execution |
| **ML Framework** | PyTorch + NumPy | Weight tensor analysis |
| **API Layer** | FastAPI | REST scanning endpoints |
| **Detection: Entropy** | SciPy / NumPy | Statistical anomaly detection |
| **Detection: LSB** | Custom bit-manipulation | Steganography signature detection |
| **Detection: Clustering** | scikit-learn (DBSCAN) | Weight cluster outlier detection |
| **Reports** | JSON + hashlib | Cryptographic provenance reports |
| **Deployment** | Docker / Render / GCP | Cloud-hosted scanner API |

---

## 🚀 Quick Start

### Option A — Use as Documentation Template Kit

```bash
# 1. Clone the repository
git clone https://github.com/Niss54/DevBlueprint.git
cd DevBlueprint

# 2. Start with the PRD — fill in your project details
open Prd.md

# 3. Work through documents in order
#    PRD → Architecture → Database → API → UI-UX → Testing → Deployment → Security
```

> 💡 **Tip:** Search and replace `[Project Name]` across all files with your actual project name.

---

### Option B — Run WeightGuard Locally

**Prerequisites:**

```bash
python --version     # >= 3.11
pip --version        # >= 23.x
docker --version     # >= 24.x (optional, for containerised run)
```

**Setup:**

```bash
# 1. Clone
git clone https://github.com/Niss54/WeightGuard.git
cd WeightGuard

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate       # macOS / Linux
# .venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — set API keys, output paths

# 5. Run a scan
python -m weightguard.cli scan --model ./models/your_model.pt

# Expected output:
# → { "status": "CLEAN", "risk_score": 0.03, "agents_run": 4, ... }
```

**Run via Docker:**

```bash
docker compose up -d

# Health check
curl http://localhost:8000/health
# → { "status": "ok", "agents": 6, "version": "1.0.0" }

# Scan a model via API
curl -X POST http://localhost:8000/api/v1/scan \
  -F "model=@./models/clean_model.pt"
```

---

### Option C — Run the Full-Stack Web App Template

**Prerequisites:**

```bash
node --version    # >= 20.x
npm --version     # >= 10.x
docker --version  # >= 24.x
```

**Setup:**

```bash
# 1. Clone and install
git clone https://github.com/Niss54/DevBlueprint.git
cd DevBlueprint
npm install

# 2. Configure environment
cp .env .env.local
# Fill in: JWT_SECRET, DATABASE_URL, REDIS_URL

# 3. Start databases
docker compose up -d postgres redis

# 4. Run migrations + seed
npx prisma migrate dev
npx prisma db seed

# 5. Start dev servers
npm run dev              # starts both frontend (3000) + backend (8000)

# 6. Verify
curl http://localhost:8000/health
# → { "status": "healthy", "database": "up", "redis": "up" }
open http://localhost:3000
```

---

## 🔑 Feature Highlights (Template Kit)

```
🔐 Authentication       JWT access tokens + HttpOnly refresh cookies
👥 Authorization       Role-based access control (USER, ADMIN, SUPER_ADMIN)
🛡️ Security            OWASP Top 10 coverage + Helmet.js + rate limiting
🗄️ Database            PostgreSQL + Prisma ORM — type-safe, migration-tracked
⚡ Caching             Redis for sessions, hot data, and rate limit counters
📧 Email               Pluggable adapter (Resend / SendGrid / SMTP)
📁 File Upload         S3 / R2 / Cloudinary with MIME type validation
✅ Testing             Vitest (unit) + Supertest (integration) + Playwright (E2E)
🚀 CI/CD              GitHub Actions: lint → test → build → deploy on push to main
🐳 Docker              Full containerisation with multi-stage Dockerfiles
📊 Monitoring          Sentry error tracking + Winston structured logging
🤖 AI Context         memory.md + CLAUDE.md for stateful AI coding sessions
```

---

## 🧪 Running Tests (Web App Template)

```bash
# All tests
npm run test

# Unit tests only (Vitest)
npm run test:unit

# Integration tests (Supertest)
npm run test:integration

# End-to-end tests (Playwright)
npm run test:e2e

# Coverage report
npm run test:coverage

# Watch mode (development)
npm run test:watch
```

**Coverage Targets:** Lines `80%+` · Functions `80%+` · Branches `75%+`

---

## 🧪 Running Tests (WeightGuard)

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (requires running API server)
pytest tests/integration/ -v

# Full test suite with coverage
pytest --cov=weightguard --cov-report=html

# Test specific agent
pytest tests/unit/test_lsb_agent.py -v
```

---

## 📂 Project Structure

```
DevBlueprint/
│
├── 📋 Prd.md                              Product Requirements Document
├── 🏗️ Architecture.md                    System architecture + tech decisions
├── 🏗️ TECHNICAL_ARCHITECTURE.md          Deep technical architecture
├── 🗄️ Database.md                        Database schema + Prisma models
├── 🔌 API.md                             REST API docs + error codes
├── 🎨 UI-UX.md                           UI design system + component guide
├── 🎨 FRONTEND_SPEC.md                   Complete frontend specification
├── ✅ Testing.md                          Testing strategy + code examples
├── 🚀 Deployment.md                      Docker + CI/CD + deployment guide
├── 🚀 DEPLOYMENT.md                      WeightGuard deployment guide
├── 🔒 Security.md                        Security guidelines template
├── 🔒 SECURITY_AND_ACCESS.md            RBAC + auth + access control
├── 🔒 SECURITY_GUIDELINES_HARDENED_EXPERT.md  Expert security guidelines
├── 🔒 SECURITY_POLICY_HARDENED_EXPERT.md     Full security policy document
├── 📋 FEATURE_TICKET_LIST.md             Sprint ticket tracker
├── 📝 TODO.md                            Phase-wise task tracker
├── 📝 Changelog.md                       Version history (Keep a Changelog)
├── 📋 PRD_CLOSURE.md                     PRD sign-off + delivery matrix
│
├── 🤖 AGENTS.md                          WeightGuard agent pipeline docs
├── 📋 ACCEPTANCE_REPORT.md              PCC 2026 competition tracker
├── 🎬 DEMO_SCRIPT.md                     Live demo script for judges
├── 🎬 Presentation.md                   Full presentation narrative
│
├── 🤖 CLAUDE.md                          Claude Code context file
├── 🧠 memory.md                          AI session memory + project state
├── 📄 ReadmeEX.MD                        Extended README reference
│
├── ⚙️ .env                              Documented environment variables
└── 📄 LICENSE                           MIT License
```

---

## 🔒 Security

### Reporting a Vulnerability

Found a security issue? **Do NOT open a public GitHub issue.**

Contact directly: **nishantmaurya@[domain].com**

We follow responsible disclosure — you will receive a response within 72 hours.

### Security Coverage

This repository includes three levels of security documentation:

| Document | Audience | Scope |
|---|---|---|
| `Security.md` | All teams | OWASP Top 10, JWT, rate limiting basics |
| `SECURITY_AND_ACCESS.md` | Backend / DevOps | RBAC, audit logs, incident response |
| `SECURITY_GUIDELINES_HARDENED_EXPERT.md` | Security teams | Advanced hardening, regulated environments |
| `SECURITY_POLICY_HARDENED_EXPERT.md` | Leadership / Legal | Org-level policy, compliance, enforcement |

---

## 🚢 Deployment

### WeightGuard (Cloud)

| Environment | URL | Branch |
|---|---|---|
| Development | `http://localhost:8000` | `feature/*` |
| Staging | `https://weightguard-staging.onrender.com` | `develop` |
| Production | `https://weightguard.onrender.com` | `main` |

### Web App Template (Docker)

```bash
# Build production images
docker compose -f docker-compose.prod.yml build

# Deploy
docker compose -f docker-compose.prod.yml up -d

# Run production migrations
docker compose exec backend npx prisma migrate deploy
```

### CI/CD — Every push to `main` automatically:

1. ✅ Runs full test suite (unit + integration + E2E)
2. 🔨 Builds and tags Docker image
3. 🚀 Deploys to production server
4. 📊 Reports deployment status to Slack / GitHub

---

## 🤝 Contributing

Contributions are welcome — both for the documentation templates and the WeightGuard codebase.

```bash
# Fork → clone → branch
git checkout -b feat/your-feature-name

# Make your changes
# Run tests
npm test      # web app template
pytest        # WeightGuard

# Commit (Conventional Commits format)
git commit -m "feat(docs): add GraphQL API template to API.md"

# Push + open Pull Request
git push origin feat/your-feature-name
```

**Branch naming:** `feat/`, `fix/`, `docs/`, `chore/`, `test/`  
**Commit format:** [Conventional Commits](https://www.conventionalcommits.org/)  
**Coverage requirement:** New code must maintain `80%+` line coverage

---

## 📜 Changelog

See [`Changelog.md`](./Changelog.md) for the full version history.

**Latest:** `v0.1.0` — Initial release 🎉

---

## 📄 License

This project is licensed under the **MIT License** — see [`LICENSE`](./LICENSE) for details.

```
MIT License — Copyright (c) 2026 Nishant Maurya
Free to use, modify, and distribute.
Attribution appreciated but not required.
```

---

## 🙏 Acknowledgements

**Documentation Framework built with:**  
[Next.js](https://nextjs.org) · [Node.js](https://nodejs.org) · [PostgreSQL](https://postgresql.org) · [Prisma](https://prisma.io) · [Redis](https://redis.io) · [shadcn/ui](https://ui.shadcn.com) · [Tailwind CSS](https://tailwindcss.com) · [Vitest](https://vitest.dev) · [Playwright](https://playwright.dev) · [Docker](https://docker.com)

**WeightGuard built with:**  
[PyTorch](https://pytorch.org) · [FastAPI](https://fastapi.tiangolo.com) · [NumPy](https://numpy.org) · [scikit-learn](https://scikit-learn.org) · [Render](https://render.com)

---

<div align="center">

**Made with ❤️ by [Nishant Maurya](https://github.com/Niss54)**

*Competing in GE HealthCare Precision Care Challenge 2026 · Building tools that matter*

⭐ **Star this repo if DevBlueprint saved you time!** ⭐

[![GitHub stars](https://img.shields.io/github/stars/Niss54/DevBlueprint?style=social)](https://github.com/Niss54/DevBlueprint)
[![GitHub forks](https://img.shields.io/github/forks/Niss54/DevBlueprint?style=social)](https://github.com/Niss54/DevBlueprint/fork)
[![GitHub watchers](https://img.shields.io/github/watchers/Niss54/DevBlueprint?style=social)](https://github.com/Niss54/DevBlueprint)

</div>
