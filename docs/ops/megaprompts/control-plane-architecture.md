# AiSci Control Plane Architecture Megaprompt

**Instructions for the User:** Copy everything below the line and paste it into your target LLM or agent.

---

You are the principal engineer implementing AiSci’s project-based research control-plane architecture in `/home/ubuntu/aisci`.

The user has approved this architecture. Implement it end-to-end, in safe incremental phases, without replacing scientific provenance or silently weakening validation rules.

## Product definition

AiSci Dashboard must become a simple control and monitoring panel for a portfolio of repository-based research projects.

- Robert’s manuscript validation is the first project, not the platform’s core identity.
- A future PhD audit must be onboarded as a new project with different papers, workflows, evidence, outputs, and possibly no physics fitting at all.
- The dashboard is the control plane.
- Canonical project files, immutable run artifacts, reusable code, and external tools are the data/execution plane.
- The dashboard must never invent scientific status or promote claims merely because a job completed.

Target architecture:

```text
Dashboard + Control API
  ├─ Portfolio: projects, attention queue, jobs, system health
  ├─ Project view: evidence, tasks, sources, runs, reports
  └─ Controlled job launch: registered project pipelines only

Project workspace
  ├─ Canonical science files
  ├─ Inputs and source provenance
  ├─ Pipeline definitions
  └─ Immutable dated run artifacts

Execution adapters
  ├─ Shared libraries: fitting/model/validation utilities
  ├─ Project-specific pipeline wrappers
  └─ Local Python, Onyx, DeerFlow, or manual-review runners
```

### Read first
Read and obey in full:
- `AGENTS.md`
- `deployment/aisci-dashboard/AGENTS.md`
- `docs/user-manual/USER_MANUAL.md`
- `research/robert/README.md`
- `research/robert/workflow.md`
- `research/robert/evidence-ledger.md`
- `research/robert/next-actions.md`
- `docs/decisions/2026-04-26-system-boundaries.md`
- `docs/decisions/2026-04-26-science-evidence-standards.md`
- `docs/ops/architecture-overview.md`
- `docs/ops/platform-backlog.md`

Inspect the entire current worktree and recent commits before editing. A recent dashboard remediation commit exists (`f6173c345`). Preserve its useful work and verify it; do not revert it blindly.
There is an untracked `deployment/aisci-dashboard/ignition/evidence_graph.db.archive`. Treat it as user data: inspect it only if needed and do not delete, overwrite, or commit it.
Do not commit, push, force-push, create GitHub Issues, or create external resources unless explicitly asked. Do not create scratch files. Use apply_patch for edits.

### Current repository reality

Classify and preserve these boundaries:

**Shared or potentially reusable**
- `libs/physics-core/src/models/`: Jüttner/Boltzmann, exact Bose-Einstein, Tsallis, Blast-Wave/BGBW
- `libs/physics-core/src/fitting/`: generic fitting machinery, artifact production, metrics
- `agent-skills/`: reusable research and operational workflows
- `docs/decisions/`: durable platform/science policies

**Robert-project-specific**
- `research/robert/`
- `libs/physics-core/src/boson_paper_analysis.py`
- `libs/physics-core/src/data_loader.py`
- `scripts/` data mappings referring to Robert’s manuscript, ins1735345, manuscript bins, specific cuts, or Robert-specific evidence
- all current Robert run directories and manuscript assets

**Archived / not active runtime**
`deployment/hep-physics/` is a v0 design concept with mocked frontend data and direct filesystem assumptions. It is not a second production dashboard. Do not revive it or delete it without a verified archival decision.
Docs currently have drift about this directory and must be corrected to describe it as archived concept material.

**Integration adapters, not core truth**
Onyx, DeerFlow, OpenRouter, Scite, and local Python are execution/retrieval adapters.
The dashboard must work even when one adapter is unavailable and must report that unavailability truthfully.

## Required implementation

### Phase 1 — Project registry and project-scoped paths
Replace the single hardcoded Robert research root with a project registry.
Use a small human-readable structured registry that does not require a new YAML dependency; TOML is preferred because Python’s tomllib is available.

Create:
`research/projects.toml`

Initially register only Robert, without moving his existing files:
```toml
[[projects]]
id = "robert-boson-manuscript"
title = "Robert — Boson probability function for the moving system"
owner = "Robert"
research_type = "manuscript_validation"
root = "research/robert"
sensitivity = "private"
capabilities = [
  "evidence",
  "tasks",
  "literature",
  "symbolic_validation",
  "fit_validation",
  "reports",
]
```

Implement a typed `ProjectSpec`/registry service in Ignition that:
- validates every project root stays inside repository root;
- resolves canonical ledger, task queue, runs, inputs, and reports relative to the project root;
- provides explicit project-not-found and project-misconfigured errors;
- allows a legacy project layout such as `research/robert/`;
- has no global `RESEARCH_ROOT`, `EVIDENCE_FILE`, `TASKS_FILE`, or `RUNS_BASE` assumption;
- validates project IDs against a strict slug format;
- never permits arbitrary filesystem paths through API parameters.

Do not create an empty PhD project directory. Instead, implement and document the project contract so a real project can be added later with real content.

### Phase 2 — Standard project contract
Define a project workspace standard for future projects:
```text
research/projects/<project-id>/
  project.toml
  canonical/
    evidence-ledger.md
    next-actions.md
    questions.md
  inputs/
  pipelines/
  runs/
  reports/
```

A project may omit capabilities it does not use. A PhD audit must not be forced to have fit pages or HEP data.
Add a documented `project.toml` schema with:
- project ID, title, owner, research type, sensitivity;
- canonical document locations;
- enabled capabilities;
- registered pipelines;
- source/corpus boundaries;
- optional data governance restrictions;
- artifact schema version.

Do not create redundant status documents. Use this manifest only as configuration.

### Phase 3 — Registered pipeline architecture
Replace dashboard knowledge of individual script paths with project-scoped pipeline definitions.

Implement a typed `PipelineSpec` that includes:
- id
- project ID
- display name and description
- runner type: python, onyx, deerflow, manual
- command/entrypoint or adapter configuration
- typed parameters
- required inputs and pre-flight gates
- expected artifact contract
- time/resource limits
- approval requirement
- version/commit provenance

The API must only launch a pipeline through a project pipeline ID. It must never accept an arbitrary command or script path.
Wrap existing Robert workflows as registered pipelines where valid, for example:
- symbolic/manuscript validation;
- data mapping/qualification;
- fit validation;
- literature intake;
- report/referee preparation.

Do not invent a pipeline if its current script is broken or simulated. Mark it unavailable with a truthful reason until repaired.
Pipeline execution must produce a run manifest, for example:
```json
{
  "schema_version": "1",
  "project_id": "robert-boson-manuscript",
  "pipeline_id": "fit-validation",
  "run_id": "...",
  "git_commit": "...",
  "parameters": {},
  "input_artifacts": [],
  "output_artifacts": [],
  "started_at": "...",
  "completed_at": "...",
  "status": "succeeded"
}
```
Store manifest and artifacts inside the project’s dated run directory.

### Phase 4 — Jobs, runners, and truthful monitoring
Implement a persistent job lifecycle:
`queued → running → succeeded | failed | cancelled`

Each job must store:
- project ID and pipeline ID;
- requester/reviewer identity;
- run ID;
- parameter payload;
- timestamps;
- worker heartbeat;
- exit code;
- structured failure;
- log location;
- artifact manifest location;
- git revision and runtime version.

Requirements:
- Do not report “complete” upon HTTP acceptance.
- Do not infer activity from log-file existence.
- Do not expose or use `subprocess.Popen` directly in request handlers.
- Prevent duplicate active jobs for the same idempotency key unless explicitly allowed.
- Logs and status events must be tied to a job ID.
- Use SSE or WebSockets only after persisted job state exists.
- Implement a local worker mode suitable for development.
- Create a database abstraction supporting PostgreSQL via `AISCI_DATABASE_URL` for deployed multi-writer operation.
- SQLite may remain for local/test mode only, with WAL, foreign keys, transactions, busy timeout, and documented single-worker limitations.
- Add migrations and avoid committing databases, generated artifacts, logs, virtual environments, or test results.
- Onyx/DeerFlow runner adapters may initially be “not configured” states, but they must be structured, explicit, and visible to the UI. Do not fake health or results.

### Phase 5 — Canonical science and review workflow
The project’s Markdown science files remain canonical.

Implement this data flow:
```text
Canonical Markdown + immutable run artifacts
  → validated project read model
  → dashboard/API

Dashboard review request
  → structured review-decision record
  → explicit approval + version check
  → controlled materialization command
  → canonical Markdown update
```

Requirements:
- UI actions must not silently mutate `evidence-ledger.md` or `next-actions.md`.
- Create project-scoped review requests containing:
  - stable ID;
  - target claim/task;
  - expected canonical revision/hash;
  - requested change;
  - reviewer identity;
  - rationale;
  - source/run/evidence references;
  - decision status and timestamps.
- Materialization must be an explicit authorized action, not an incidental browser PATCH request.
- Use atomic write + lock + revision checking.
- Reject conflicts visibly and preserve both versions.
- Preserve/add stable IDs in canonical entries without destructively rewriting all Markdown.
- Never promote a scientific claim beyond its evidence-ledger status because an automated job succeeded.
- Continue to distinguish Bose-Einstein from Boltzmann/Jüttner explicitly.

### Phase 6 — Artifact and scientific-result contract
Make fit and audit results project-neutral but scientifically faithful.
Create versioned artifact schemas for:
- RunManifest
- ArtifactManifest
- FitResult
- ModelSpec
- ParameterEstimate
- CorrelationArtifact
- CovarianceArtifact
- ResidualArtifact
- ValidationGate
- Anomaly
- LiteratureSource
- ReviewDecision

For Robert’s fit artifacts:
- preserve model family and component count;
- preserve optimizer success, EDM, covariance validity, gate outcomes, AIC/BIC, residual/pull availability, fit range, data provenance, and seed;
- include BGBW/Blast-Wave, Tsallis/Tsallis-Pareto, Jüttner/Boltzmann, and exact Bose-Einstein when present;
- do not label a 1-component result as 2-component;
- do not merge correlations from different component counts;
- treat `U=\gamma v` distinctly from velocity `v`; never assert `U < c`;
- never label a result “Clean Fit” when fit gate, convergence, covariance, residual, or baseline requirements are absent or failed;
- preserve missing artifacts as explicit missing state, not zeros or synthetic matrices.

Replace global hardcoded anomaly thresholds with a project/versioned validation policy. Exploratory display controls may exist, but must never change official anomaly/review status.

### Phase 7 — Dashboard UX
Make all dashboard routes project-scoped:
```text
/
  Portfolio overview

/projects/:projectId
  Project summary

/projects/:projectId/evidence
/projects/:projectId/tasks
/projects/:projectId/literature
/projects/:projectId/runs
/projects/:projectId/jobs
/projects/:projectId/fits        # only if fit_validation capability exists
/projects/:projectId/reports
/operations
```

Requirements:
- The portfolio page shows projects, blocked gates, active jobs, reviewer attention, and shared service health.
- A project page only renders capabilities declared by its manifest.
- A future PhD audit should naturally show evidence, source map, tasks, audit findings, and reports—but not physics-fit navigation unless it declares that capability.
- Add project switching and persist it in route state.
- Add meaningful states for: loading, no data, invalid project, project misconfigured, runner unavailable, queued/running/failed job, missing artifact, invalid fit, scientifically rejected fit, and API unavailable.
- Add reviewer workflow: anomaly/finding → provenance → diagnostic artifacts → linked evidence/tasks → review request → approved decision → tracked rerun.
- Remove hardcoded “NOMINAL,” fake “ACTIVE,” fake “RUNNING,” and stale fixed pipeline timestamps.
- Ensure navigation includes Evidence Ledger.
- Remove unsafe `dangerouslySetInnerHTML`; render Markdown safely.
- Retain accessibility, keyboard operation, responsive behavior, and reduced-motion support.

### Phase 8 — Literature/source scope
Make literature data project-scoped.
- Store source/provider explicitly; never infer provider from ID prefix.
- Store source provenance, extraction model/version, timestamp, confidence, extraction fallback state, and project ID.
- Deduplicate papers and claims idempotently.
- Do not treat generic fallback keyword extraction as evidence-grade science.
- Let project manifest define literature scope: HEP, thesis literature, methods literature, etc.
- A failed external integration must create an explicit job/source status, not silently return empty data.

### Phase 9 — Legacy and documentation cleanup
- Treat `deployment/hep-physics/` as archived v0 concept material. Do not integrate or deploy it.
- Correct the ADR/documentation contradiction that calls it nonexistent.
- Keep only `deployment/aisci-dashboard/` as the active dashboard.
- Update existing canonical docs only:
  - `README.md`
  - `docs/ops/architecture-overview.md`
  - `docs/ops/CURRENT_STATUS.md`
  - `docs/ops/platform-backlog.md`
  - relevant existing ADR if appropriate
- Do not create a generic new audit/status markdown file.
- Ensure all docs describe actual ports, services, and project architecture.

### Phase 10 — Tests and verification
Add tests before declaring this complete.

Backend tests must cover:
- project registry parsing and path containment;
- legacy Robert mapping;
- project-not-found/misconfigured states;
- pipeline registration and parameter validation;
- job lifecycle and duplicate prevention;
- runner-unavailable behavior;
- Markdown projection and review revision conflicts;
- artifact parser for 1c/2c/3c variants;
- U versus velocity semantics;
- validation-policy behavior;
- idempotent literature ingestion;
- authentication, CORS, and path traversal rejection.

Frontend tests must cover:
- portfolio → Robert project navigation;
- capability-driven views;
- no-fit PhD-audit fixture;
- truthful job states;
- evidence review request flow;
- meaningful error/empty states.

Playwright tests must use fixtures or isolated test services. They must never launch live ingestion, fitting, OpenRouter, Onyx, DeerFlow, or arbitrary subprocesses.

Verification must pass:
```bash
npm run lint
npx tsc --noEmit
# appropriate dashboard backend tests
# relevant physics-core tests using libs/physics-core/.venv
# isolated Playwright tests
```
Do not run mutating production-like jobs merely to satisfy tests.

### Delivery process
1. Inspect current state and produce a concise P0/P1/P2 implementation plan.
2. Implement the project registry and project-scoped read paths first.
3. Add tests and migrate existing Robert dashboard behavior to use `project_id`.
4. Implement pipeline/job contracts and dashboard project routing.
5. Implement review workflow and artifact contracts.
6. Update docs and run all safe verification.
7. Do not stop at scaffolding. Robert must work as the first real registered project.

### Final response requirements
Report:
- architecture implemented;
- exact changed files;
- how Robert was preserved and migrated;
- how to add a real PhD audit project;
- migrations/data-preservation choices;
- exact verification commands and results;
- explicit remaining limitations requiring user/environment authority.

Do not claim production readiness unless the complete project registry, job lifecycle, artifact provenance, review workflow, and tests are implemented and verified.
