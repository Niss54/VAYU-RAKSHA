  # 🏆 ULTIMATE README GENERATION PROMPT
> Inspired by: gofiber/fiber · httpie/httpie · doomemacs · lobehub/lobe-chat · sniffnet · ThePhish · PostHog · nerd-fonts · Pacman-Game · dbt-core



## HOW TO USE
1. Upload your project ZIP file to Claude
2. Copy-paste the entire prompt below
3. Get the best README ever written for your project



---
---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✂️  COPY EVERYTHING BELOW THIS LINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
You are a world-class technical writer and open-source documentation expert who has
studied every top GitHub README — gofiber/fiber, httpie/httpie, doomemacs/doomemacs,
lobehub/lobe-chat, sniffnet, PostHog, nerd-fonts, dbt-core, and more.

I have given you a ZIP file of my project. Your ONLY job in this response is to:
  1. Silently analyze the ZIP (no narration)
  2. Output a single, complete, PERFECT README.md
  3. Add a brief "Customization Checklist" at the very end

Do NOT explain what you are doing. Do NOT say "Here is your README."
Output the raw markdown ONLY.

═══════════════════════════════════════════════════════
PHASE 1 — DEEP PROJECT ANALYSIS  (silent, internal)
═══════════════════════════════════════════════════════

Before writing one word, scan every file in the ZIP and extract:

CONFIG FILES (find and parse ALL that exist):
  package.json / pyproject.toml / Cargo.toml / go.mod / build.gradle /
  pom.xml / setup.py / composer.json / pubspec.yaml / *.csproj
  → Extract: project name, version, description, author, license, scripts,
    dependencies (separate dev deps from runtime)

SOURCE CODE (read enough to understand):
  → What does this project ACTUALLY do? (not just the name — the real behavior)
  → Core algorithm / main flow: input → processing → output
  → Key functions / classes / modules and their roles
  → Any unique technical decisions or clever approaches

EXISTING ASSETS:
  → Screenshots, GIFs, images → note their paths
  → Existing README → note what's already good, what's missing
  → Diagrams, docs, wikis → extract any useful architecture info
  → .env.example / config files → extract all variables

PROJECT FINGERPRINT (determine ALL that apply):
  Type:
    □ CLI Tool / Developer Utility
    □ Web Application (Frontend / Full-stack / SaaS)
    □ REST / GraphQL API / Backend Service
    □ Library / SDK / Framework / Package
    □ Desktop Application (Electron / Tauri / Qt)
    □ Mobile Application
    □ Game (terminal / web / 2D / 3D)
    □ AI / ML / Data Science / Research
    □ DevOps Tool / Infrastructure
    □ Academic / Student / Hackathon Project
    □ Browser Extension / Plugin
    □ Script / Automation

  Audience:
    □ End users (non-technical)  →  tone: friendly, jargon-free
    □ Developers / engineers     →  tone: technical, precise, witty ok
    □ Enterprise / teams         →  tone: professional, ROI-focused
    □ Students / learners        →  tone: encouraging, step-by-step
    □ Researchers                →  tone: academic, cite methodology

  Maturity:
    □ Prototype / student project (keep it honest + fun)
    □ Active open-source         (full contrib guide needed)
    □ Production / enterprise    (SLA, security, support info needed)

═══════════════════════════════════════════════════════
PHASE 2 — ADAPTIVE STRATEGY SELECTION
═══════════════════════════════════════════════════════

Based on the fingerprint above, choose the matching strategy:

STRATEGY A — CLI / Developer Tool  (inspired by: httpie, sniffnet, dbt-core)
  Priority sections: Quick install → Usage examples → Man-page-style options table
  Voice: confident, terse, "it just works" energy
  Must include: terminal recording placeholder, options/flags table, pipe examples

STRATEGY B — Web App / SaaS  (inspired by: lobehub/lobe-chat, PostHog)
  Priority sections: Live demo badge → Feature cards → Deploy-in-one-click button
  Voice: marketing-meets-engineering — sell the vision AND show the code
  Must include: tech stack badges, deploy buttons (Vercel/Netlify/Railway), env table

STRATEGY C — Library / SDK / Framework  (inspired by: gofiber/fiber)
  Priority sections: Performance benchmarks → API reference → Code snippets
  Voice: authoritative, benchmark-driven
  Must include: install command (npm/pip/cargo/go get), quickstart snippet, link to full docs

STRATEGY D — Game / Student / Hackathon  (inspired by: ma-shamshiri/Pacman-Game, doomemacs)
  Priority sections: Animated demo → Controls/rules → Fun facts
  Voice: enthusiastic, personal, show your personality
  Must include: GIF per major feature, "why I built this," known bugs section

STRATEGY E — AI / ML / Research  (inspired by: emalderson/ThePhish, nerd-fonts)
  Priority sections: Architecture diagram → Dataset/model info → Results table
  Voice: precise, reproducible, cite everything
  Must include: UML or Mermaid flow, requirements.txt snapshot, metrics table

STRATEGY F — Enterprise / Infrastructure  (inspired by: dbt-core, PostHog)
  Priority sections: Architecture → Security → Support/SLA
  Voice: no fluff, maximum signal per word
  Must include: production readiness checklist, env config table, upgrade notes

═══════════════════════════════════════════════════════
PHASE 3 — README STRUCTURE  (follow EXACTLY, no sections skipped)
═══════════════════════════════════════════════════════

────────────────────────────────────────
BLOCK 1 · HEADER  (center-aligned)
────────────────────────────────────────

<div align="center">

  <!-- BANNER: If a logo/image exists in the zip, reference it.
       Otherwise create a text-art banner using the project name + emoji.
       Use this exact format for text banners: -->

  ```
  ██████╗ ██████╗  ██████╗      ██╗███████╗ ██████╗████████╗
  ██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝██╔════╝╚══██╔══╝
  ██████╔╝██████╔╝██║   ██║     ██║█████╗  ██║        ██║   
  ██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝  ██║        ██║   
  ██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗╚██████╗   ██║   
  ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝   
  ```
  <!-- Adapt the above ASCII to the actual project name, or use the logo image -->

  # [EMOJI] Project Name

  > **[ONE-LINE TAGLINE]**  ← ≤15 words, zero jargon, answers "what does it do FOR ME?"

  <!-- BADGE ROW — fill real values from package files -->
  ![Build](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/ci.yml?style=flat-square&label=Build)
  ![Version](https://img.shields.io/github/v/release/OWNER/REPO?style=flat-square&label=Version)
  ![License](https://img.shields.io/github/license/OWNER/REPO?style=flat-square)
  ![Language](https://img.shields.io/github/languages/top/OWNER/REPO?style=flat-square)
  ![Stars](https://img.shields.io/github/stars/OWNER/REPO?style=flat-square)
  ![Last Commit](https://img.shields.io/github/last-commit/OWNER/REPO?style=flat-square)
  <!-- Add more from: npm downloads / PyPI downloads / Docker pulls / coverage — whatever applies -->

  <!-- RAINBOW DIVIDER (use this exact line) -->
  <img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" alt="divider"/>

</div>

────────────────────────────────────────
BLOCK 2 · HOOK  (the "why this exists")
────────────────────────────────────────

Write 2–4 sentences answering: What problem existed? How does this project solve it?
Use "Before / After" OR "Problem → Solution" pattern.
NO bullet points. Pure prose. Make it compelling.

For student/game projects: be personal — "I built this because..." works great.
For enterprise/library: use data — "X hours wasted on Y, so we built Z."

────────────────────────────────────────
BLOCK 3 · DEMO
────────────────────────────────────────

## 🎬 Demo

<!-- If screenshots/GIFs exist in the ZIP, use them here.
     If multiple features, use a 2-column HTML table:          -->

<div align="center">

| Feature A | Feature B |
|:---------:|:---------:|
| ![Feature A](./assets/feature-a.gif) | ![Feature B](./assets/feature-b.gif) |

<!-- If no assets exist, write the placeholder clearly: -->
<!-- 🖼️ Add a demo GIF here: record with Terminalizer (CLI) or Kap (GUI) -->
<!-- Suggested content to record: [describe the most impressive 30-second demo] -->

</div>

────────────────────────────────────────
BLOCK 4 · TABLE OF CONTENTS
────────────────────────────────────────

## 📋 Table of Contents

- [✨ Features](#-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
- [💻 Usage](#-usage)
- [🏗️ Architecture](#️-architecture)
- [⚙️ Configuration](#️-configuration)
[Add/remove sections based on what exists in the project]
- [🤝 Contributing](#-contributing)
- [❓ FAQ](#-faq)
- [📄 License](#-license)
- [🙏 Acknowledgements](#-acknowledgements)

────────────────────────────────────────
BLOCK 5 · FEATURES
────────────────────────────────────────

## ✨ Features

<!-- 6–12 features extracted from the ACTUAL source code — not invented.
     Each feature = emoji + bold name + one real description sentence.
     If 8+ features, group them into 2–3 categories with subheadings.    -->

- 🚀 **[Feature Name]** — [what it actually does, in user terms]
- ⚡ **[Feature Name]** — [concrete benefit, not vague]
- 🔒 **[Feature Name]** — [technical detail that impresses developers]
...

<!-- End with a roadmap teaser if you found TODO/FIXME/future comments in code: -->
<details>
<summary>🗺️ Roadmap — Coming Soon</summary>

- [ ] [Feature found in TODOs or issues]
- [ ] [Another planned feature]

</details>

────────────────────────────────────────
BLOCK 6 · TECH STACK
────────────────────────────────────────

## 🛠️ Tech Stack

<!-- Use shields.io for-the-badge style. Only include what's ACTUALLY in the project. -->
<!-- Group logically. Examples below — adapt to real stack:                           -->

**Core**
![Language](https://img.shields.io/badge/LANG-COLOR?style=for-the-badge&logo=LOGO&logoColor=white)

**Frontend** *(if applicable)*
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)

**Backend** *(if applicable)*
![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)

**Database** *(if applicable)*
...

**DevOps / Tooling**
...

────────────────────────────────────────
BLOCK 7 · GETTING STARTED
────────────────────────────────────────

## 🚀 Getting Started

### Prerequisites

<!-- List EXACT versions found in config files — no guessing -->
- [Runtime] >= [exact version from config]
- [Package manager] >= [version]
- [Any external service or API key needed]

```bash
# Verify your setup:
[runtime] --version   # expected: >= X.Y
```

### Installation

<!-- Every command must be copy-pasteable with ZERO modification needed -->

```bash
# 1. Clone the repository
git clone https://github.com/OWNER/REPO.git
cd REPO

# 2. Install dependencies
[exact install command from package file]

# 3. Configure environment
cp .env.example .env
# → Edit .env with your values (see Configuration section)

# 4. [Any build step if needed]
[build command]

# 5. Run
[start command]
```

<!-- If Windows steps differ, add a collapsible: -->
<details>
<summary>🪟 Windows-specific steps</summary>

```powershell
[Windows commands if different]
```

</details>

### ⚡ Quick Start (TL;DR)

```bash
[Absolute minimum: 3–5 commands from clone to running, no explanation]
```

────────────────────────────────────────
BLOCK 8 · USAGE
────────────────────────────────────────

## 💻 Usage

<!-- 3–5 real examples using ACTUAL function/class/command names from source code.
     NOT pseudocode. Real, runnable examples.                                      -->

### [Most common use case]

```[language]
[real code example extracted or inferred from source]
```

### [Second most common use case]

```[language]
[real code example]
```

<!-- For CLI tools: show flag combinations -->
<!-- For libraries: show import + initialization + common operations -->
<!-- For web apps: show the main user flow with screenshots referenced  -->

<details>
<summary>📚 Advanced Usage</summary>

```[language]
[More complex example — pipeline, edge case, full config, etc.]
```

</details>

────────────────────────────────────────
BLOCK 9 · ARCHITECTURE
────────────────────────────────────────

## 🏗️ Architecture

<!-- Choose the diagram type that best fits the project:
     - flowchart TD → for data/process flows (most projects)
     - sequenceDiagram → for API/request flows
     - classDiagram → for OOP libraries
     - graph LR → for pipelines
     Build the diagram from ACTUAL code structure, not a generic template -->

```mermaid
flowchart TD
    A([User / Client]) --> B[Entry Point\nfrom main file]
    B --> C{Core Logic\nfrom source}
    C --> D[Module 1\nreal name]
    C --> E[Module 2\nreal name]
    D --> F[(Storage / Output)]
    E --> F
    
    style A fill:#4CAF50,color:#fff
    style F fill:#2196F3,color:#fff
```

### Project Structure

```
[project-name]/
├── [main source dir]/     ← [what lives here]
│   ├── [key file]         ← [its role]
│   └── [key file]         ← [its role]
├── [test dir]/            ← test suite
├── [config files]         ← project configuration
└── README.md
```

<!-- For AI/ML projects: add model architecture diagram or pipeline diagram -->
<!-- For web apps: add a system context diagram showing external services   -->

────────────────────────────────────────
BLOCK 10 · CONFIGURATION
────────────────────────────────────────

## ⚙️ Configuration

<!-- Extract ALL variables from .env.example, config.yaml, settings files, etc. -->

| Variable | Type | Default | Required | Description |
|----------|------|---------|:--------:|-------------|
| `VAR_NAME` | `string` | `""` | ✅ | [what it controls] |
| `VAR_NAME` | `number` | `3000` | ❌ | [what it controls] |
| `VAR_NAME` | `boolean` | `false` | ❌ | [what it controls] |

<!-- If complex config exists (YAML/TOML), show a complete annotated example:  -->

```yaml
# Full config example with comments explaining each field
```

────────────────────────────────────────
BLOCK 11 · API / CLI REFERENCE  (include ONLY if project has API or CLI)
────────────────────────────────────────

## 📡 API Reference

<!-- For REST APIs: document each endpoint -->
### `[METHOD] /endpoint`

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `param` | `string` | ✅ | Description |

**Response:**
```json
{
  "key": "value"
}
```

<!-- For CLI tools: document flags/subcommands -->
### Commands

| Command | Shorthand | Description |
|---------|-----------|-------------|
| `--flag` | `-f` | [what it does] |

<!-- For libraries: document main public API -->
### `functionName(params)`

**Parameters:** `param` (type) — description

**Returns:** `type` — description

────────────────────────────────────────
BLOCK 12 · PERFORMANCE  (include ONLY if benchmarks exist or can be inferred)
────────────────────────────────────────

## ⚡ Performance

<!-- If benchmark code or results exist in the ZIP, show them here.
     If not applicable, skip this entire block.
     Format: comparison table vs alternatives                          -->

| Scenario | This Project | [Alternative 1] | [Alternative 2] |
|----------|:------------:|:---------------:|:---------------:|
| [Test]   | **Xms**      | Yms             | Zms             |
| [Test]   | **X ops/s**  | Y ops/s         | Z ops/s         |

> 📊 Benchmarks run on: [hardware from comments/docs if found]

────────────────────────────────────────
BLOCK 13 · CONTRIBUTING
────────────────────────────────────────

## 🤝 Contributing

Contributions are what make open source amazing. Any contribution you make is
**greatly appreciated**.

1. Fork the repository
2. Create your feature branch: `git checkout -b feat/amazing-feature`
3. Commit your changes: `git commit -m 'feat: add amazing feature'`
4. Push to the branch: `git push origin feat/amazing-feature`
5. Open a Pull Request

<!-- If CONTRIBUTING.md exists in the ZIP: -->
> 📖 Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

<!-- If no CONTRIBUTING.md, add the quick essentials: -->
**Good first issues are labeled** `good first issue` **— perfect for newcomers!**

────────────────────────────────────────
BLOCK 14 · FAQ
────────────────────────────────────────

## ❓ FAQ

<!-- Write 4–6 questions that a REAL user/developer would actually ask,
     based on what the project does. No filler questions.              -->

<details>
<summary><b>[Most common "how do I..." question]</b></summary>
[Concrete answer with code snippet if needed]
</details>

<details>
<summary><b>[Most common error or gotcha]</b></summary>
[Explanation + fix]
</details>

<details>
<summary><b>[Integration or compatibility question]</b></summary>
[Answer]
</details>

<details>
<summary><b>[Question about limitations or scope]</b></summary>
[Honest answer]
</details>

────────────────────────────────────────
BLOCK 15 · LICENSE
────────────────────────────────────────

## 📄 License

Distributed under the **[LICENSE NAME]** License.
[One sentence: what this license allows — e.g., "Free for personal and commercial use with attribution."]

See [`LICENSE`](./LICENSE) for the full text.

────────────────────────────────────────
BLOCK 16 · ACKNOWLEDGEMENTS
────────────────────────────────────────

## 🙏 Acknowledgements

<!-- Credit ONLY things actually found in the ZIP:
     - Libraries used (check package files)
     - Tutorials or articles referenced (check comments/docs)
     - Tools that made development possible
     - Inspirations mentioned in existing README/comments              -->

- [**Library Name**](link) — [how it's used in this project]
- [**Tool Name**](link) — [how it helped]
- [**Article / Tutorial**](link) — [what you learned from it]

<!-- If contributors exist (check git history if available, or AUTHORS file): -->
### 👥 Contributors

<a href="https://github.com/OWNER/REPO/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=OWNER/REPO" alt="Contributors"/>
</a>

────────────────────────────────────────
BLOCK 17 · FOOTER
────────────────────────────────────────

---

<div align="center">

  <a href="#top">⬆️ Back to Top</a>

  <br/><br/>

  <!-- Choose tone based on project type: -->
  <!-- Student/fun: --> Made with ❤️ and ☕ by **[Author Name]**
  <!-- Enterprise: --> Built and maintained by **[Team/Org Name]**

  <br/>

  If this project helped you, please consider giving it a ⭐ **Star** — it means a lot!

  <br/>

  ![GitHub Repo stars](https://img.shields.io/github/stars/OWNER/REPO?style=social)

</div>

═══════════════════════════════════════════════════════
PHASE 4 — QUALITY GATES  (internal checks before output)
═══════════════════════════════════════════════════════

Before outputting, verify EVERY item:

CONTENT ACCURACY:
  □ Project name matches package file exactly
  □ All features listed actually exist in source code
  □ Installation commands match actual package manager and scripts
  □ Tech stack badges match actual dependencies found
  □ Config table matches actual .env.example / config files
  □ API/CLI reference matches actual code signatures
  □ Architecture diagram reflects actual file/module structure
  □ Mermaid node labels use real module/file names from source

FORMATTING:
  □ Every code block has a language specifier (```bash, ```python, ```js, etc.)
  □ All badges use correct shields.io URL format
  □ Mermaid syntax is valid (no unclosed brackets, no invalid chars in labels)
  □ Table of Contents anchor links match actual heading text exactly
  □ All `<details>` tags are properly closed
  □ `<div align="center">` blocks are properly closed

COMPLETENESS:
  □ No "TODO: fill this in" left visible in the README
  □ No placeholder like "INSERT PROJECT NAME" still present
  □ Every section marked (include ONLY if...) is either included or removed
  □ OWNER/REPO replaced with actual values if found in zip

VOICE CHECK:
  □ Tone matches audience (check PHASE 1 audience classification)
  □ One-liner passes the "explain to a non-technical friend" test
  □ No corporate buzzwords unless this is an enterprise project
  □ No cringe motivational filler ("This amazing project will change...")

═══════════════════════════════════════════════════════
PHASE 5 — OUTPUT FORMAT
═══════════════════════════════════════════════════════

Output structure (in this exact order):

1. The complete README.md (raw markdown, starting from BLOCK 1)
   → No preamble. No "Here is your README." Just the markdown.

2. A separator: ---

3. A "📋 CUSTOMIZATION CHECKLIST" section at the very end:
   → List every placeholder that still needs human action
   → Format as checkboxes: - [ ] Replace X with Y
   → Group by category: Images / Badges / Links / Content
   → Include an estimate: "⏱️ Estimated time to finalize: ~15 minutes"

THAT IS ALL. No other text. Begin now.
```

---
---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✂️  END OF COPY SECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

## 📊 Pattern Analysis — Top 10 READMEs

This prompt was built by extracting the following patterns:

| Repo | What it contributes to this prompt |
|------|-------------------------------------|
| **gofiber/fiber** | Collapsible advanced usage, benchmark tables, language switcher concept |
| **httpie/httpie** | Clean narrative flow, "Before/After" hook, screenshot placement strategy |
| **doomemacs/doomemacs** | Center-aligned header discipline, witty-but-precise voice, badge placement |
| **lobehub/lobe-chat** | Animated banner approach, feature card layout, 2-column demo tables |
| **GyulyVGC/sniffnet** | Rainbow divider lines, tabular config reference, minimalist section design |
| **emalderson/ThePhish** | UML/Mermaid diagram requirement, step-by-step config table, academic tone |
| **PostHog/posthog** | Custom section icons, deploy button badges, contributor gallery |
| **ryanoasis/nerd-fonts** | Unique diagram type selection (Sankey idea → pick best diagram per project) |
| **ma-shamshiri/Pacman-Game** | GIF-per-feature in 2-column table, personal "why I built this" hook |
| **dbt-labs/dbt-core** | Enterprise simplicity mode, "every word must earn its place" philosophy |

## 🔑 The 12 Universal Elements (how each is handled)

| # | Element | Where in Prompt |
|---|---------|-----------------|
| 1 | Logo / Banner | BLOCK 1 — ASCII fallback if no image |
| 2 | Badges | BLOCK 1 — 6 standard + project-specific |
| 3 | One-line description | BLOCK 1 — ≤15 words, jargon-free rule |
| 4 | GIF demo / screenshots | BLOCK 3 — 2-column table layout |
| 5 | Table of Contents | BLOCK 4 — emoji anchors, 8+ entries |
| 6 | Quick install | BLOCK 7 — copy-paste single block |
| 7 | Usage examples | BLOCK 8 — real code, not pseudocode |
| 8 | Feature list | BLOCK 5 — emoji + bold + description |
| 9 | Architecture diagram | BLOCK 9 — Mermaid with real module names |
| 10 | Contributors | BLOCK 16 — contrib.rocks widget |
| 11 | License | BLOCK 15 — one-sentence human summary |
| 12 | Back to top | BLOCK 17 — footer with star CTA |

## 💡 Pro Tips

- **Best results**: Include `.env.example` in your ZIP — it auto-generates the config table
- **Faster**: If you have existing screenshots/GIFs, name them clearly before zipping
- **For libraries**: Make sure your `package.json` / `pyproject.toml` has a `description` field
- **For web apps**: Include a `DEPLOY.md` or deployment notes — prompt will pick them up

---

*Prompt version: 1.0 · Tested against 10 top GitHub READMEs · Works for any project type*
