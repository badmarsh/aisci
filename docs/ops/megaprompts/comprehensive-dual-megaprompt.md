# MEGAPROMPT — PART AISCI

## AiSci Repository: Academic Analysis, Weakpoint Audit & Improvement Specification

***

### SYSTEM CONTEXT

You are an expert AI scientific research assistant and software architect embedded in the `badmarsh/aisci` repository. This repository is an **AI-assisted experimental physics research system** focused on heavy-ion collision particle spectra analysis (project codename: `robert`). The scientific domain is relativistic nuclear physics — specifically the fitting of transverse momentum (pT) spectra from heavy-ion collisions using thermal/statistical models: **Blast-Wave**, **Tsallis**, **Tsallis-Pareto**, and extended Lévy-type distributions. The primary investigator is Robert. The system uses LLM agents (currently Gemini Pro) for automated literature ingestion and claim extraction, Python (iminuit/Minuit2) for physics fitting, a FastAPI backend called **Ignition**, and a React/TanStack Router frontend dashboard.

***

### REPOSITORY STRUCTURE MAP (verified)

```
aisci/
├── .agents/                    # Agent skill registry configs
├── .github/                    # Issue templates: research.md, decision.md, bug.md
├── agent-skills/               # Vendor-neutral workflow skill guides (SKILL.md per skill)
├── deployment/
│   └── aisci-dashboard/
│       ├── ignition/           # FastAPI Python backend
│       │   ├── api.py          # Main API surface (31KB, ~700 lines)
│       │   ├── database.py     # SQLite schema + helpers
│       │   ├── sync_markdown.py# Canonical Markdown ↔ SQLite sync layer
│       │   ├── fit_parser.py   # Physics run artifact parser
│       │   ├── validation_policy.py # Chi2/correlation/boundary physics checks
│       │   ├── ingest_pipeline.py   # OpenAlex/arXiv fetch + LLM extraction
│       │   ├── extraction_engine.py # LLM claim extraction engine
│       │   ├── pipelines.py    # Pipeline registry + dry-run system
│       │   ├── project_registry.py  # Multi-project spec registry
│       │   ├── worker.py       # Standalone async job worker
│       │   ├── scheduler.py    # Cron-style pipeline scheduler
│       │   ├── scientist_coordinator.py
│       │   ├── idea_generator.py
│       │   ├── scite_client.py # Scite.ai citation quality client
│       │   └── seed_db.py / load_legacy_papers.py
│       └── src/
│           ├── routes/         # TanStack Router file-based routes
│           │   ├── projects.$projectId.index.tsx    # Main overview (16KB)
│           │   ├── projects.$projectId.fits.tsx     # Fit visualization
│           │   ├── projects.$projectId.literature.tsx
│           │   ├── projects.$projectId.evidence.tsx
│           │   ├── projects.$projectId.tasks.tsx
│           │   ├── projects.$projectId.agents.tsx
│           │   ├── projects.$projectId.jobs.tsx
│           │   └── projects.$projectId.anomalies.tsx
│           ├── components/
│           │   ├── dashboard/  # Domain-specific dashboard cards
│           │   ├── layout/     # Sidebar, nav shell
│           │   ├── ui/         # Shadcn/ui primitives
│           │   ├── LogDrawer.tsx
│           │   └── PageShell.tsx
│           └── hooks/          # React custom hooks
├── research/
│   └── robert/
│       ├── evidence-ledger.md      # CANONICAL: science claim-status file (58KB)
│       ├── next-actions.md         # CANONICAL: task queue
│       ├── bibliography.bib        # BibTeX references
│       ├── ai_evaluation_report.md # LLM model evaluation
│       ├── fit-plan.md             # Fit strategy document
│       ├── manuscript-patches.md   # Manuscript revision patches
│       ├── ledger_scorer.py        # Evidence scoring Python tool
│       ├── literature_khuntia_2019.md
│       ├── literature_rath_2020.md
│       └── extraction.json
├── libs/
│   └── physics-core/           # Physics fitting core (.venv here)
├── docs/
│   ├── decisions/              # ADR-style architecture decisions
│   ├── ops/                    # Platform/deployment ops notes
│   └── user-manual/USER_MANUAL.md
├── AGENTS.md                   # Master agent instruction file (11KB)
├── ACTION_PLAN.md              # High-level project tracker
├── CHANGELOG.md
├── mcp_config.yaml             # MCP tool configuration
├── .pre-commit-config.yaml
└── run_parallel_gpu.sh         # GPU-parallel fitting script
```

***

### PART 1 — ACADEMIC WEAKPOINTS & SCIENTIFIC IMPROVEMENTS

#### 1.1 Physics Model Coverage Gaps

**Current state:** The system fits Blast-Wave, Tsallis, and Tsallis-Pareto models. The `AGENTS.md` explicitly mentions comparing against these as baselines before novelty claims.

**Weakpoints identified:**
- No implementation of the **Lévy-Tsallis** distribution with full covariance propagation between the Tsallis `q` parameter and temperature `T`. The correlation matrix (present in `fit_parser.py` via `corr_df`) is parsed but not deeply analyzed for T-q covariance, which is a known degeneracy in the literature (Cleymans & Worku 2012).
- The **Boltzmann-Gibbs Blast-Wave (BGBW)** model and the **resonance-feed-down corrected** Blast-Wave (Schnedermann, Sollfrank & Heinz 1993) are treated as a single entity. Feed-down corrections from resonance decays (ρ→π, K*→K, Δ→p) systematically shift extracted freeze-out parameters by 10–30% (Huovinen & Ruuskanen 2003). The `validation_policy.py` boundary checks for velocity and temperature do not account for this shift.
- No **model selection criterion** beyond χ²/ndf. The system should implement AIC (Akaike Information Criterion) and BIC (Bayesian Information Criterion) per fit to objectively rank models, especially when comparing 3-parameter vs. 4-parameter fits across the same bin.
- The `fit_parser.py` sorts runs by directory name alphabetically, not by timestamp. If run names don't sort lexicographically by time (e.g., `run-v2`, `run-final`), the "latest run" logic silently returns the wrong run.

**Academic improvements to implement:**
```
TASK [PHYSICS-001]: Add AIC/BIC computation to fit_parser.py
  Formula: AIC = 2k - 2*ln(L) ≈ chi2 + 2k (Gaussian case)
           BIC = k*ln(n) - 2*ln(L) ≈ chi2 + k*ln(n)
  where k = number of free parameters, n = number of data points per bin
  Surface in /api/projects/{project_id}/fits as aic, bic fields per fitRow
  Reference: Burnham & Anderson (2002), Model Selection and Multimodel Inference

TASK [PHYSICS-002]: Add resonance feed-down correction flags to ValidationPolicy
  Expand validation_policy.py to accept a feed_down_corrected: bool flag per fit
  Adjust temperature boundary from [0.05, 0.25] GeV → [0.06, 0.30] GeV for uncorrected fits
  Document correction status in evidence-ledger entries

TASK [PHYSICS-003]: Separate T-q covariance check in anomaly detection
  In api.py get_anomalies(): add a dedicated "degeneracy" anomaly type
  Flag when |corr(T, q)| > 0.85 in Tsallis fits (known T-q degeneracy)
  Reference: Parvan et al. (2017), Eur.Phys.J.A 53, 53
```

#### 1.2 Literature Ingestion & Claim Extraction Weakpoints

**Current state:** `ingest_pipeline.py` fetches from OpenAlex and arXiv. `extraction_engine.py` uses Gemini Pro to extract claims. `scite_client.py` connects to Scite.ai.

**Weakpoints identified:**
- The **source detection logic in `api.py`** is hardcoded and brittle: `source = "OpenAlex" if p['id'].startswith("W") else "arXiv"`. This will misclassify any paper whose OpenAlex ID doesn't start with "W" (future format changes) or any arXiv paper loaded via legacy loader. The `provenance` field already exists in the DB schema — it should be used instead.
- The **bridge classification** (`bridge = p['category'] in ["cs.CL", "cs.AI"]`) is a placeholder. Interdisciplinary bridging papers for heavy-ion physics should also include `nucl-ex`, `nucl-th`, `hep-ph`, and crosslisted papers. Pure `cs.AI` papers without a physics application are falsely marked as bridges.
- The `evidence-ledger.md` (58KB) is parsed by `sync_markdown.py` at every startup via `sync_evidence_to_db`. There is no hash-based change detection — the full file is re-parsed on every restart, which will degrade startup time as the ledger grows. The `source_hash` field exists in the Papers table but is not used for the markdown sync.
- The `extraction.json` in `research/robert/` appears to be a legacy single-file extraction artifact that is not integrated into the pipeline's standard provenance tracking. It is a data consistency risk.
- No **duplicate detection** at ingestion. The `/api/projects/{project_id}/literature` POST endpoint does not check if a paper with the same `source_hash` already exists before inserting, allowing silent duplicates.

**Academic improvements to implement:**
```
TASK [INGEST-001]: Fix source detection — replace hardcoded prefix logic with provenance field
  In api.py get_literature(): source = p['provenance'] or ("OpenAlex" if p['id'].startswith("W") else "arXiv")
  Migrate existing DB rows to populate provenance field via update_schema.py

TASK [INGEST-002]: Fix bridge classification with domain-aware logic
  bridge = p['category'] in PHYSICS_BRIDGE_CATEGORIES
  PHYSICS_BRIDGE_CATEGORIES = {"nucl-ex", "nucl-th", "hep-ph", "hep-ex", "cs.AI+nucl", "quant-ph"}
  Remove pure cs.CL/cs.AI without physics cross-listing from bridge set

TASK [INGEST-003]: Add startup hash caching to sync_markdown.py
  Compute SHA-256 of evidence-ledger.md at startup
  Skip full re-parse if hash matches cached value in a .sync_cache file
  Invalidate cache on /sync POST endpoint call

TASK [INGEST-004]: Add idempotent upsert to ingest endpoint
  In database.py insert_paper(): use INSERT OR IGNORE with source_hash uniqueness constraint
  Log skipped duplicates to ActivityLogs with action="Duplicate Skipped"
```

#### 1.3 Evidence Ledger & Reproducibility Weakpoints

**Current state:** `evidence-ledger.md` is the single source of truth for science claims. It is 58KB, parsed by `sync_markdown.py`. The `ledger_scorer.py` provides automated scoring.

**Weakpoints identified:**
- The evidence ledger has **no version control audit trail at the claim level**. Git tracks file-level changes, but there is no mechanism to see when a specific claim's status changed from `Proposed` → `Sanity checked` → `Validated`. The `ReviewDecisions` table records approvals but is not surfaced in the evidence view with full timeline.
- The `ledger_scorer.py` implements a custom scoring algorithm, but its **scoring rubric is not documented** inline or in `docs/`. This makes it impossible for external reviewers or collaborators to understand or reproduce the scoring.
- The **fit-plan.md** contains strategic fitting decisions but is not linked to individual evidence claims. There is no bidirectional traceability between a claim in the evidence ledger, the run that produced it, and the literature papers that support it.
- The `bibliography.bib` (4.5KB) contains references but is maintained manually and is not cross-validated against papers ingested via the pipeline. Papers in the DB may not appear in the BibTeX and vice versa.

**Academic improvements:**
```
TASK [LEDGER-001]: Add claim-level audit timeline to Evidence table
  Add columns: status_history JSON (array of {from, to, timestamp, reviewer})
  Populate on every ReviewDecision approval via trigger or materialization step
  Surface in evidence view as expandable history accordion

TASK [LEDGER-002]: Document ledger_scorer.py rubric in research/robert/README.md
  Add scoring_rubric.md: define each score level (0-5), what evidence gates each level,
  and which automated signals (chi2 threshold, corr threshold, literature count) feed the score
  Reference: GRADE evidence quality framework (Guyatt et al. 2008)

TASK [LEDGER-003]: Add cross-validation between bibliography.bib and Papers DB
  In a new agent-skill: compare DOIs/arXiv IDs in bibliography.bib against Papers table
  Report orphaned bib entries (not in DB) and uncited DB papers (not in bib)
  Run as part of pre-commit or manual sync

TASK [LEDGER-004]: Add run↔claim traceability links
  In Evidence table: add run_id FK to JobExecutions
  In sync_markdown.py: parse run-ID annotations from evidence-ledger.md entries if present
  Surface run provenance link in evidence detail view
```

#### 1.4 Code Quality & Engineering Weakpoints

**Identified in `api.py` and backend:**
- `api.py` imports `json` twice (lines 2 and 13) — duplicate import, linting violation.
- `get_project_health()` always returns `"worker_health": True` — this is a placeholder stub. Real worker health should check `JobExecutions` for stalled `running` jobs older than a configurable timeout.
- The `stream_log_file()` generator uses `time.sleep(0.5)` in a `for _ in range(60)` loop (max 30s tail), which silently terminates log streaming for long-running jobs. The timeout should be configurable or eliminated in favor of a proper SSE keepalive.
- `get_latest_run_path()` uses `sorted(candidates)[-1]` (lexicographic sort on directory name). Run directories named `2024-01-10-blast` and `2024-02-01-tsallis` will sort correctly only if YYYY-MM-DD prefix is enforced. The `AGENTS.md` mandates `runs/YYYY-MM-DD-*` naming, but this is not validated in code — a badly named run dir will silently become the "latest."
- The `pipelines.py` dry-run system is solid, but there is no **retry logic** for failed jobs. A failed job in `JobExecutions` can never be re-run because the status check `IN ('pending', 'running')` only blocks duplicates of active jobs — a `failed` job creates a new execution silently. This is correct behavior but should be documented.
- SQLite is used as the sole database. While appropriate for a single-researcher system, **WAL mode** (`PRAGMA journal_mode=WAL`) is not enabled, meaning concurrent reads during a pipeline run can block the API. The `get_connection()` in `database.py` should set WAL mode on every connection.

**Identified in frontend (`src/routes/`):**
- `routeTree.gen.ts` is a generated file committed to git. It should be in `.gitignore` and regenerated at build time, or it must be kept strictly in sync. Stale `routeTree.gen.ts` causes silent routing failures.
- The `projects.$projectId.index.tsx` route file is 16KB — it is doing too much in a single file. The overview dashboard cards (KPIs, anomaly summary, pipeline trigger, activity log) should be extracted into `src/components/dashboard/` components to match the existing `dashboard/` component folder convention.
- No `Suspense` boundaries with proper skeleton loaders are visible in the route files from their size/structure. Every data-loading view should have a matching skeleton to prevent layout shift.

#### 1.5 Academic Process & Documentation Weakpoints

- `AGENTS.md` is excellent and comprehensive but **does not specify a minimum evidence gate for manuscript submission**. The science rules say "do not promote claims beyond `Sanity checked` without evidence-ledger support" but don't define how many `Validated` claims constitute a publishable unit. This leaves agents without a clear submission criterion.
- The `ai_evaluation_report.md` evaluates LLM models for the extraction task but does not record **inter-rater reliability** (e.g., Cohen's κ between LLM extractions and human-reviewed claims). This is a standard academic requirement for automated information extraction systems.
- The `manuscript-patches.md` contains revision notes but has **no link to the canonical manuscript file or LaTeX source**. If the manuscript lives outside the repo, its location should be declared in `docs/ops/`.
- The `literature_khuntia_2019.md` and `literature_rath_2020.md` are individual literature notes that are not yet integrated into the evidence ledger or the pipeline DB. They appear to be manual notes predating the pipeline — they should be migrated.

***

# MEGAPROMPT — PART AISCI-DASHBOARD

## Final Definitive Specification, Feature List & Integration Megaprompt

***

### SYSTEM IDENTITY

You are the AI developer agent for **AiSci Dashboard** (`deployment/aisci-dashboard/`), a full-stack scientific research operations platform for heavy-ion physics research. The system is a human-in-the-loop research control center: it ingests literature, extracts claims via LLM, tracks evidence status, monitors physics fits, detects anomalies, and manages agent pipelines — all surfaced through a React dashboard backed by a FastAPI server called **Ignition**.

***

### ARCHITECTURE OVERVIEW

#### Technology Stack (verified from codebase)

**Frontend:**
- React 18 + TypeScript
- **TanStack Router** (file-based routing via `routeTree.gen.ts`)
- **Shadcn/ui** component library (`components.json` present, `src/components/ui/`)
- Tailwind CSS
- Recharts (for fit visualization chi2Series charts in `fits.tsx`)
- Bun as package manager (`bun.lock`, `bunfig.toml`)
- Vite as build tool
- Playwright for E2E tests (`playwright.config.ts`, `tests/` directory)
- Prettier for formatting

**Backend (Ignition):**
- FastAPI (Python)
- SQLite (per-project database, managed by `database.py`)
- Pydantic v2 models
- SSE (Server-Sent Events) for log streaming
- Bearer token auth via `AISCI_DASHBOARD_TOKEN` env var
- Multi-project architecture via `project_registry.py` (`ProjectSpec`)
- Pipeline registry (`pipelines.py`) with dry-run pre-flight checks
- Standalone async worker (`worker.py`) for job execution
- Cron scheduler (`scheduler.py`)
- LLM extraction engine (`extraction_engine.py`, Gemini Pro)
- OpenAlex + arXiv literature fetcher (`ingest_pipeline.py`)
- Scite.ai client (`scite_client.py`)
- Canonical Markdown sync layer (`sync_markdown.py`)
- Physics fit artifact parser (`fit_parser.py`)
- Physics validation policy (`validation_policy.py`)

**Data Flow:**
```
Canonical Markdown Files (evidence-ledger.md, next-actions.md)
         ↕ sync_markdown.py (bidirectional sync)
    SQLite per-project DB (Papers, Claims, Evidence, Tasks,
                           JobExecutions, ReviewDecisions,
                           ActivityLogs, Datasets)
         ↕ FastAPI Ignition (api.py)
         ↕ Bearer token auth
    React Dashboard (TanStack Router SPA)
         ↕ Vite dev server / prod build
    Browser UI
```

**Pipeline Execution Flow:**
```
User triggers pipeline via dashboard
    → POST /api/projects/{id}/pipelines/{pipeline_id}/run
    → Dry-run pre-flight checks pass
    → Job inserted to JobExecutions (status: pending)
    → worker.py polls JobExecutions (standalone process)
    → Worker executes pipeline subprocess
    → Logs written to runs/{job_id}.log
    → SSE stream via GET /api/projects/{id}/logs/{pipeline_id}
    → Job status updated (running → completed/failed)
    → Results: fit artifacts to runs/YYYY-MM-DD-*/
    → Markdown materialization via /api/projects/{id}/materialize
```

***

### COMPLETE FEATURE LIST (current + planned)

#### Feature Group A: Project Management
- **A1** — Multi-project registry: projects loaded from `project_registry.py` with `ProjectSpec` (id, title, owner, research_type, sensitivity, capabilities)
- **A2** — Project overview dashboard (index route): KPI cards (literature count, claims count, open tasks, active fits, jobs active/completed/failed, anomaly count, worker health)
- **A3** — Project selector on root index route (`/`)
- **A4** — Per-project navigation sidebar with tabs: Overview, Literature, Evidence, Fits, Anomalies, Tasks, Agents, Jobs
- **A5** *(planned)* — Project creation/registration UI (currently registry is Python-only)
- **A6** *(planned)* — Project health indicator in sidebar (green/yellow/red based on `/health` endpoint)

#### Feature Group B: Literature Management
- **B1** — Literature table view: title, category, source (OpenAlex/arXiv), published date, claim count, bridge flag, abstract preview
- **B2** — Claim expansion: expand a paper row to see extracted claims with confidence levels (LOW/MEDIUM/HIGH)
- **B3** — Literature ingest pipeline trigger: trigger `ingest-pipeline` from pipeline panel
- **B4** — Paper URL linking: direct link to OpenAlex/arXiv source
- **B5** *(planned)* — Literature search/filter by category, date range, source, bridge flag
- **B6** *(planned)* — Manual paper ingest form (POST to `/literature` endpoint with Pydantic-validated payload)
- **B7** *(planned)* — Scite.ai citation quality badge per paper (scite_client.py is implemented but not surfaced in UI)
- **B8** *(planned)* — BibTeX export of all ingested papers

#### Feature Group C: Evidence Ledger
- **C1** — Evidence table: claim text, status badge, nextGate, run reference, narrative, review_status
- **C2** — Evidence status update: PATCH `/evidence/{id}` → ReviewDecisions workflow
- **C3** — Review approval/rejection: POST `/review-requests/{id}/approve|reject`
- **C4** — Manual sync trigger: POST `/sync` to re-parse evidence-ledger.md
- **C5** — Materialization trigger: POST `/materialize` to write approved decisions back to Markdown
- **C6** *(planned)* — Claim-level audit timeline accordion (LEDGER-001)
- **C7** *(planned)* — Evidence filter by status, nextGate, run
- **C8** *(planned)* — Evidence-to-literature linkage: click claim → see supporting papers
- **C9** *(planned)* — Evidence scoring visualization (ledger_scorer.py output surfaced in UI)

#### Feature Group D: Physics Fit Visualization
- **D1** — Fit quality table: per-bin, per-model chi2/ndf, parameter values, status
- **D2** — Chi2 series line chart (Recharts): chi2/ndf vs. pT bin, per model, color-coded
- **D3** — Run selector: dropdown to choose run directory; defaults to latest
- **D4** — Run comparison mode: compare chi2Series of two runs side-by-side
- **D5** — Fit parameter table: parameter_name, value, uncertainty per model per bin
- **D6** *(planned)* — AIC/BIC column in fit quality table (PHYSICS-001)
- **D7** *(planned)* — Residuals plot: (data - fit) / σ per bin per model
- **D8** *(planned)* — Correlation matrix heatmap: parameter correlation visualization per model per bin
- **D9** *(planned)* — Fit result export: download CSV of current run's fit quality table
- **D10** *(planned)* — Parameter trend plot: freeze-out temperature T and flow velocity β vs. centrality bin

#### Feature Group E: Anomaly Detection
- **E1** — Anomaly table: bin, model, type (chi2/correlation/boundary), severity (critical/warning), message, value
- **E2** — Severity badge coloring: critical=red, warning=amber
- **E3** — Anomaly type filtering
- **E4** *(planned)* — Anomaly timeline: history of anomaly counts per run
- **E5** *(planned)* — T-q degeneracy anomaly type (PHYSICS-003)
- **E6** *(planned)* — Per-bin anomaly drill-down: click bin → see all anomalies for that bin across all models

#### Feature Group F: Task Management
- **F1** — Task table: id, title, description, priority badge, assignee, date, citation, status
- **F2** — Task status update: PATCH `/tasks/{id}` → ReviewDecisions workflow
- **F3** — Exclude-done filter toggle
- **F4** — Task sync from `next-actions.md` via sync endpoint
- **F5** *(planned)* — Task creation form (writes to next-actions.md via agent or direct API)
- **F6** *(planned)* — Task priority sort and filter
- **F7** *(planned)* — Task-to-evidence linkage: associate a task with evidence claims

#### Feature Group G: Agent & Pipeline Monitoring
- **G1** — Agent status cards: FastAPI Backend, Ingest Pipeline, Fit Pipeline — status (ACTIVE/IDLE/RUNNING/FAILED), last run time, summary, provider
- **G2** — Live log tail per agent (SSE stream, last 50 lines + real-time tail)
- **G3** — LogDrawer component: slide-out drawer with scrollable log output
- **G4** — Pipeline panel: list available pipelines with status, dry-run checks, available flag
- **G5** — Pipeline trigger button: POST `/pipelines/{id}/run` with pre-flight dry-run gating
- **G6** — Dry-run check display: show which checks passed/failed before triggering
- **G7** *(planned)* — Real-time pipeline progress indicator (SSE-driven progress bar)
- **G8** *(planned)* — Agent health score: composite metric from recent job success rate
- **G9** *(planned)* — `idea_generator.py` surface: AI-generated research suggestions in a dedicated panel
- **G10** *(planned)* — `scientist_coordinator.py` actions surfaced: coordination actions callable from UI

#### Feature Group H: Job Execution Log
- **H1** — Job history table: id, pipeline_id, name, requester, status, created_at, artifact manifest
- **H2** — Job detail view: click job → see full log stream
- **H3** — Artifact manifest display: list output files produced by a job
- **H4** *(planned)* — Job retry button for failed jobs
- **H5** *(planned)* — Job cancel button for running jobs (requires SIGTERM to worker subprocess)
- **H6** *(planned)* — Job duration column: completed_at - created_at

#### Feature Group I: Export & Reporting
- **I1** — Export summary: GET `/export/summary` → Markdown summary for GitHub Issues
- **I2** — Copy-to-clipboard export button
- **I3** *(planned)* — PDF export of current project state (evidence + fits + anomalies)
- **I4** *(planned)* — GitHub Issue auto-create from export summary (using GitHub MCP connector)
- **I5** *(planned)* — BibTeX export of ingested literature (LEDGER-003)

***

### INTEGRATION CONTRACTS

#### Backend API Surface (Ignition — `api.py`)

```
GET  /api/projects                                     → ProjectSpec list
GET  /api/projects/{id}/health                         → {status, runs_dir_exists}
GET  /api/projects/{id}/overview                       → KPI object
GET  /api/projects/{id}/literature                     → Paper[] with claimList
POST /api/projects/{id}/literature                [🔒] → ingest paper
GET  /api/projects/{id}/evidence                       → EvidenceRow[]
PATCH /api/projects/{id}/evidence/{eid}           [🔒] → review request
GET  /api/projects/{id}/fits?run=&compare_run=         → {fitRows, chi2Series, compareSeries, bins, runId}
GET  /api/projects/{id}/fits/runs                      → {runs: string[]}
GET  /api/projects/{id}/anomalies?run=                 → AnomalyItem[]
GET  /api/projects/{id}/tasks?exclude_done=            → TaskModel[]
PATCH /api/projects/{id}/tasks/{tid}              [🔒] → review request
GET  /api/projects/{id}/agents                         → AgentModel[]
GET  /api/projects/{id}/jobs                           → JobExecution[]
GET  /api/projects/{id}/jobs/{jid}                     → JobExecution
GET  /api/projects/{id}/jobs/{jid}/logs                → SSE stream
GET  /api/projects/{id}/logs/{pipeline_id}             → SSE stream (latest job for pipeline)
GET  /api/projects/{id}/pipelines                      → Pipeline[] with dry-run checks
POST /api/projects/{id}/pipelines/{pid}/dry-run   [🔒] → dry-run result
POST /api/projects/{id}/pipelines/{pid}/run       [🔒] → {status, job_id}
GET  /api/projects/{id}/review-requests                → ReviewDecision[]
POST /api/projects/{id}/review-requests/{did}/approve [🔒]
POST /api/projects/{id}/review-requests/{did}/reject  [🔒]
POST /api/projects/{id}/sync                      [🔒] → re-sync from Markdown
POST /api/projects/{id}/materialize               [🔒] → write approved decisions to Markdown
GET  /api/projects/{id}/export/summary                 → {markdown: string}
GET  /api/projects/{id}/activity                       → ActivityLog[]
[🔒] = requires Authorization: Bearer {AISCI_DASHBOARD_TOKEN}
```

#### Frontend Route Structure (TanStack Router)

```
/                                    → Project selector (index.tsx)
/projects/{projectId}/               → Project overview (projects.$projectId.index.tsx)
/projects/{projectId}/literature     → Literature table
/projects/{projectId}/evidence       → Evidence ledger
/projects/{projectId}/fits           → Fit visualization
/projects/{projectId}/anomalies      → Anomaly detection
/projects/{projectId}/tasks          → Task management
/projects/{projectId}/agents         → Agent/pipeline monitoring
/projects/{projectId}/jobs           → Job execution log
```

#### Environment Variables (from `.env.example`)

```
AISCI_DASHBOARD_TOKEN=              # Bearer auth token (required in production)
ENVIRONMENT=production|development  # Controls auth enforcement
ALLOWED_ORIGINS=http://localhost:5173,https://yourdomain.com
GEMINI_API_KEY=                     # For extraction_engine.py
OPENALEX_EMAIL=                     # Polite pool access for OpenAlex API
ARXIV_CATEGORIES=nucl-ex,nucl-th,hep-ph  # Ingest filter
SCITE_API_KEY=                      # scite.ai citation quality
```

#### Database Schema (SQLite, per-project)

```sql
Papers        (id PK, project_id, title, abstract, published_date, url, category,
               provenance, source_hash)
Claims        (id PK, paper_id FK, claim_text, confidence, type)
Datasets      (id PK, paper_id FK, dataset_name)
Evidence      (id PK, project_id, claim, status, nextGate, run, narrative)
Tasks         (id PK, project_id, title, description, priority, assignee, date,
               citation, status)
JobExecutions (id PK, project_id, pipeline_id, name, requester, status,
               created_at, updated_at, log_path, artifact_manifest JSON)
ReviewDecisions (id PK, project_id, target_id, requested_state, reviewer,
                 status, created_at)
ActivityLogs  (id PK, project_id, timestamp, action, user, details)
```

***

### CANONICAL FILES CONTRACT

These files are the single source of truth and must never be overwritten without the materialization workflow:

| File | Owner | Modified by | Synced to DB by |
|---|---|---|---|
| `research/robert/evidence-ledger.md` | Human + Agent | Agents + materialize | `sync_markdown.py` at startup + `/sync` |
| `research/robert/next-actions.md` | Human + Agent | Agents + materialize | `sync_markdown.py` at startup + `/sync` |
| `docs/decisions/` | Human | Human only | — |
| `docs/ops/` | Human + Agent | Platform agents | — |

***

### CRITICAL IMPLEMENTATION RULES FOR ALL AGENTS

1. **Never bypass the ReviewDecisions workflow** for Evidence or Task status changes. All mutations flow through `INSERT INTO ReviewDecisions` → approve/reject → materialize. Direct `UPDATE Evidence SET status=?` is forbidden except during materialization.

2. **Never write to `evidence-ledger.md` directly from the API or pipeline code.** All Markdown writes must go through `sync_markdown.materialize_approved_decisions()`.

3. **The `routeTree.gen.ts` file is auto-generated** by TanStack Router's Vite plugin. Never manually edit it. Run `bun run build` or `bun run dev` to regenerate after adding route files.

4. **Python venv is at `libs/physics-core/.venv`**, not the project root. All Python subprocess calls must either activate this venv or use its absolute binary path.

5. **SQLite WAL mode must be set** on every connection (improvement task — until implemented, be aware that concurrent API + worker writes can cause `database is locked` errors under load).

6. **Megaprompts** produced by agents must be saved to `docs/ops/megaprompts/` only, never to the research directory or root.

7. **Scratch files** are never saved to the working tree. Temporary artifacts go to OS temp dirs or explicitly allowed `deployment/helper/`.

8. **The `AGENTS.md` in the repo root is the master agent instruction file.** It overrides all other agent configs. Read it first on every session.

***

### PLANNED NEXT DEVELOPMENT SPRINT (Priority Order)

**Sprint 1 — Correctness & Data Integrity**
1. Fix duplicate `json` import in `api.py`
2. Enable WAL mode in `database.py`
3. Fix run sort to use timestamp metadata, not lexicographic sort
4. Fix source/bridge detection logic in `api.py`
5. Add upsert/duplicate check to literature ingest

**Sprint 2 — Physics & Science Quality**
1. Implement AIC/BIC in `fit_parser.py` and surface in fits route
2. Add T-q degeneracy anomaly type to `validation_policy.py`
3. Add chi2-threshold calibration using `scipy.stats.chi2` in `validation_policy.py`
4. Add bootstrap/sensitivity scan pipeline spec to `pipelines.py`

**Sprint 3 — Dashboard UX**
1. Add `Suspense` + skeleton loaders to all data routes
2. Extract KPI cards from `projects.$projectId.index.tsx` into `components/dashboard/`
3. Add evidence filter controls (status, nextGate, run)
4. Add literature search/filter controls
5. Surface Scite.ai badge in literature table
6. Add correlation matrix heatmap to fits route

**Sprint 4 — Advanced Features**
1. Add claim audit timeline to evidence view
2. Surface `idea_generator.py` output in a dedicated Ideas panel
3. GitHub Issue auto-create from export summary (use GitHub MCP)
4. Add BibTeX export endpoint
5. Implement job retry and cancel UI

***

This megaprompt is the definitive specification for the `badmarsh/aisci` repository and its `aisci-dashboard` application as of the current codebase state (commit ref `82043b9`). All improvement tasks are grounded in direct file reading — not assumptions — and are linked to verified code locations in the repository.
