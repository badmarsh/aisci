# how will Robert run command with skills when he does not use vs code, how the deer flow comes in

There are two entirely separate interfaces here — they serve different people.

## The Two-Layer Architecture

```
Robert (physicist, no VS Code)
    │
    └─► Browser → DeerFlow web UI (port 2026)
                      │
                      └─► DeerFlow "Local Searcher" agent (SOUL.md)
                                │
                                ├─ rag_search → Onyx indexed corpus
                                ├─ read_file / grep / glob → repo files
                                ├─ python exec → physics/src/ scripts
                                └─ rag_manage → document sets

You (operator/developer)
    │
    └─► VS Code / Claude / Cursor → skill pipelines (USER_MANUAL.md)
                      │
                      └─► same codebase, same server
```

## What Each Layer Is For

**DeerFlow is Robert's no-code interface.** He opens a browser, types a research question in plain language, and the DeerFlow agent (configured in `SOUL.md` as a "Local Searcher") handles it — searching Onyx via `rag_search`, reading files directly, running physics scripts, and always citing sources. Robert never touches a terminal.

**The skills in `USER_MANUAL.md` are _your_ workflow tools**, not Robert's. When you open a coding agent session (VS Code, Claude, Cursor), you invoke skills like `reproducible-physics-runner` or `science-ledger-manager` to do structured work on Robert's behalf — fixing a script, updating the evidence ledger, running a fit. Robert asks you to do something; you run the appropriate skill pipeline to do it safely.

## What Robert Actually Does Day-to-Day

| Robert types in DeerFlow                          | DeerFlow agent does                                                              |
| :------------------------------------------------ | :------------------------------------------------------------------------------- |
| "Does my formula reduce to Cooper-Frye at U=0?"   | `rag_search` corpus → reads `boson_paper_analysis.py` output                     |
| "What does the evidence ledger say about χ²/ndf?" | `read_file research/robert/evidence-ledger.md` → returns relevant claims         |
| "Run the symbolic sanity check"                   | Executes `physics/src/sympy_validation_agent.py`, returns structured JSON report |
| "What papers cite my paper and contradict it?"    | Calls Scite MCP via Onyx's Physics Validation Mode persona                       |

## Where DeerFlow Ends and the Skill Pipeline Begins

DeerFlow handles **read and run** tasks autonomously — things Robert can see and verify himself. When a task requires **writing to canonical files** (amending `evidence-ledger.md`, updating `platform-backlog.md`, changing a system prompt), that's a boundary DeerFlow's agent respects: it proposes, Robert approves, then you execute the change via the skill pipeline. The `SOUL.md` instruction "if a document set doesn't exist, suggest creating one with `rag_manage`" rather than doing it silently is exactly this discipline in practice.

## How the 15 Skills Connect

The skills form **two parallel pipelines** — one for platform/ops work, one for science work — joined by three shared infrastructure skills that both pipelines call.

---

## The Skill Map

```
╔══════════════════════════════════════════════════════════════════════╗
║                     SHARED INFRASTRUCTURE                           ║
║                                                                      ║
║   git-worktree-guard          analysis-handoff-router               ║
║   (safe git context           (post-analysis routing:               ║
║    before any change)          implement / persist / handoff)        ║
║                                                                      ║
║   secret-config-auditor                                             ║
║   (called by ops pipeline whenever config files are touched)        ║
╚══════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════╗   ╔══════════════════════════════════╗
║    OPS / PLATFORM PIPELINE   ║   ║      SCIENCE PIPELINE            ║
║                              ║   ║                                  ║
║  aisci-tech-kickoff          ║   ║  reproducible-physics-runner     ║
║  (session start → pick task) ║   ║  (run scripts, save artifacts)   ║
║          ↓                   ║   ║          ↓                       ║
║  aisci-ops-auditor           ║   ║  science-source-curator          ║
║  (full structured audit)     ║   ║  (extract evidence from papers)  ║
║          ↓                   ║   ║          ↓                       ║
║  onyx-rag-eval-manager       ║   ║  science-ledger-manager          ║
║  (RAG tuning gate)           ║   ║  (update claim status)           ║
║          ↓                   ║   ║          ↓                       ║
║  mcp-integration-planner     ║   ║  science-report-writer           ║
║  (plan/document MCP tools)   ║   ║  (draft referee reports)         ║
║          ↓                   ║   ║                                  ║
║  platform-backlog-manager    ║   ║  researcher-docs-manager         ║
║  (maintain task tracker)     ║   ║  (curate all docs, archive stale)║
║          ↓                   ║   ╚══════════════════════════════════╝
║  vendored-runtime-maintainer ║
║  (deer-flow / vendor trees)  ║
║          ↓                   ║
║  aisci-living-docs           ║
║  (mirror: docs vs repo state)║
║          ↓                   ║
║  aisci-tech-kickoff          ║
║  (next session kickoff)      ║
╚══════════════════════════════╝
```

---

## Daily Routine — Coding Agent Manager

### Morning Kickoff (every session start)

**Skill: `aisci-tech-kickoff`**

1. Read `AGENTS.md`, `ACTION_PLAN.md`, `docs/ops/platform-backlog.md`, open GitHub Issues, and `docs/decisions/2026-04-26-system-boundaries.md`
2. Run `git status --short` + `git log --oneline -n 20` via `git-worktree-guard`
3. Pick the single highest-leverage non-destructive task from the backlog
4. State the task and reasoning — then implement or produce an approval-gated plan
5. End with `analysis-handoff-router`: implement now / persist / handoff prompt

---

### Platform Work Session

**Trigger:** Docker, Onyx, LiteLLM, MCP, compose, or deployment issue

```
aisci-tech-kickoff          → orient, pick task
  ├── aisci-ops-auditor      → full audit if broad investigation needed
  ├── onyx-rag-eval-manager  → if RAG settings are on the table
  ├── mcp-integration-planner → if adding or fixing an MCP endpoint
  ├── secret-config-auditor  → always when touching .env / config files
  ├── vendored-runtime-maintainer → if deer-flow tree is involved
  ├── aisci-living-docs      → if docs have drifted from reality
  └── platform-backlog-manager → route accepted active work to GitHub Issues; keep backlog concise
        └── analysis-handoff-router → close session with 3 options
```

---

### Science Work Session

**Trigger:** Robert asks to run a fit, check a claim, find a paper, or draft a report

```
science-source-curator       → find and extract evidence from papers/Onyx
  └── reproducible-physics-runner → run scripts, save dated run artifacts
        └── science-ledger-manager → update claim status in evidence-ledger.md
              └── science-report-writer → only when a claim reaches Supported
                    └── researcher-docs-manager → archive anything stale this session
```

---

### End-of-Session Cleanup (always)

**Skill: `researcher-docs-manager`** — runs last in any session:

- Are any docs now stale because of today's work?
- Did any new file get created that belongs in archive?
- Are GitHub Issues, `platform-backlog.md`, and `evidence-ledger.md` still in sync?

Then `analysis-handoff-router` closes with the three options for the next agent.

---

## Where New Ideas Come From

The system has **three idea inlets**, each with a designated landing zone:

| Source                                                                     | Landing Zone                                                                 | Skill That Processes It                                                                 |
| :------------------------------------------------------------------------- | :--------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------- |
| Robert's physics intuition / new manuscript version                        | `research/robert/next-actions.md`                                            | `science-ledger-manager` to gate it, `science-source-curator` to ground it              |
| Platform observation (something broken, slow, or missing)                  | GitHub Issue for active work; `docs/ops/platform-backlog.md` only for concise canonical state | `platform-backlog-manager` to route it, `aisci-ops-auditor` to audit the surrounding area |
| External literature (new paper on Tsallis, arXiv preprint, Scite citation) | `research/robert/science-questions.md` or directly into `evidence-ledger.md` | `science-source-curator` → `science-ledger-manager`                                     |

**Ideas never go directly into `ACTION_PLAN.md`** — that file is high-level tracking only. An idea becomes real only after it lands in the right execution or canonical tracker and is accepted by the user: GitHub Issues for active platform work, `platform-backlog.md` for concise platform state, or `next-actions.md` for science tasks.

---

## The One Rule That Holds Everything Together

Every skill in both pipelines respects the same hard boundary: **platform details stay out of science files; science claims stay out of ops files**. `analysis-handoff-router` is the enforcement mechanism — it routes findings to the correct canonical file rather than letting an agent dump everything into one document. `git-worktree-guard` ensures no session ever destroys another agent's in-progress work. `secret-config-auditor` ensures no credentials ever cross into `docs/`. These three cross-cutting skills are the connective tissue that makes the rest safe to run in parallel.

---

## Physics Tools Reference — `physics/src/`

The five scripts in `physics/src/` are the computational layer of the science pipeline. Each exists for a specific, non-overlapping reason. They are invoked by `reproducible-physics-runner` and their outputs feed `science-ledger-manager`.

### What Each Script Does and Why It Exists

**[`boson_paper_analysis.py`](https://github.com/badmarsh/aisci/blob/main/physics/src/boson_paper_analysis.py)** (18.7 KB) is the core script, most directly tied to Robert's manuscript _"Boson Probability Function for the Moving System"_. It works through seven sections entirely in SymPy + NumPy, never touching experimental data files.

| Script section        | What it checks                                                | Paper connection                                                                                                                 |
| --------------------- | ------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| §1 Core distribution  | `f(p) ~ δ(p²−m²)Θ(p⁰)exp(−βU^μp_μ)` — the invariant exponent  | The paper's fundamental distribution formula                                                                                     |
| §2 η integration      | Proves `U^μp_μ = pT·cosh(η−Y)` via cosh addition formula      | The key step from 4-momentum to observable pT spectrum                                                                           |
| §3 Normalization      | `∫₀^∞ pT·exp(−λpT)dpT = 1/λ²`                                 | The paper's normalization constant C                                                                                             |
| §4 U parameterization | Proves `v = U/√(1+U²) < c`, `γv = U`, `Y = arcsinh(U)`        | Robert's specific parameterization, not standard textbook                                                                        |
| §5 η-cut              | Verifies the static limit `U→0` recovers Cooper-Frye          | Regression guard: the moving formula must contain the static one                                                                 |
| §6 χ²/ndf             | Flags the absence of goodness-of-fit in retrieved chunks      | The highest-priority open concern in the evidence ledger                                                                         |
| §7 Numerics           | Numerical shape check at physical and extreme `(T, U)` values | Confirms the distribution is physically sane at low multiplicity; flags U₂ ≈ 0.011 ± 0.847 as unconstrained at high multiplicity |

**[`fitting_pipeline.py`](https://github.com/badmarsh/aisci/blob/main/physics/src/fitting_pipeline.py)** (32.4 KB — the largest script) is the full numerical fitting infrastructure. It takes per-bin pT spectra (the currently blocked data table) and fits the 3-component model, emitting chi2/ndf, covariance matrices, parameter correlations, residuals, and AIC/BIC model comparison. It exists because `boson_paper_analysis.py` only does symbolic sanity-checks — the actual claim "the 3-component fit is over-parameterized at high multiplicity" requires running real data through this.

**[`data_loader.py`](https://github.com/badmarsh/aisci/blob/main/physics/src/data_loader.py)** (14.4 KB) handles the HEPData ingestion and CSV normalisation layer. It exists because the evidence ledger documents that `ins1419652` returns only inclusive spectra, not the per-multiplicity-class bins the fit needs — this script is the bridge that will process whatever data table Robert provides into `physics/data/fit_input.csv`.

**[`sympy_validation_agent.py`](https://github.com/badmarsh/aisci/blob/main/physics/src/sympy_validation_agent.py)** (12.0 KB) is a standalone symbolic algebra checker separate from `boson_paper_analysis.py`. It is specifically for running arbitrary equations from the manuscript through SymPy without contaminating the main analysis script — the equivalent of a scratchpad that produces a structured JSON pass/fail report rather than printed output.

**[`tsallis_physics_validation.py`](https://github.com/badmarsh/aisci/blob/main/physics/src/tsallis_physics_validation.py)** (9.2 KB) implements Tsallis-Pareto and Blast-Wave baseline distributions, completely independent of Robert's paper formula. It exists to satisfy the ledger entry "Tsallis/Blast-Wave baselines are needed" — you cannot claim the Jüttner/moving-system description is better unless you can show it fits the same data as well or better than the established alternatives.

### Dependency Map

```
Robert's paper: "Boson Probability Function for the Moving System"
       │
       ├─ SYMBOLIC LAYER (no data needed)
       │   boson_paper_analysis.py  ← checks the math is internally consistent
       │   sympy_validation_agent.py ← checks individual equations on demand
       │
       ├─ DATA LAYER (currently blocked)
       │   data_loader.py  ← prepares fit_input.csv from HEPData / Robert's tables
       │
       ├─ FITTING LAYER (blocked until data_loader runs)
       │   fitting_pipeline.py  ← runs the actual 3-component fit, emits chi2/ndf
       │
       └─ COMPARISON LAYER (independent, can run now)
           tsallis_physics_validation.py  ← competes against the paper's model
```

The symbolic layer is already green (sanity-checked in the evidence ledger). The rest is blocked on one thing: the per-multiplicity-bin pT data table from Robert.

### Current Blocker

`data_loader.py` cannot produce `physics/data/fit_input.csv` until Robert supplies a per-bin pT spectrum table matching multiplicity classes `21–30, 31–40, 41–50, 51–60, 61–70, 71–80, 81–90, 91–100, 101–125, 126–150`. HEPData record `ins1419652` provides only inclusive spectra. Once `fit_input.csv` exists, `fitting_pipeline.py` and `tsallis_physics_validation.py` can both run without further dependencies.

### Manuscript Location

The primary manuscript PDF lives at `research/robert/manuscript/boson-probability-function-moving-system.pdf`, co-located with `evidence-ledger.md`, `fit-plan.md`, and `validation-plan.md` (consistent with the `research/robert/` boundary defined in `AGENTS.md`).
