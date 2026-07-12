# AiSci Dashboard + Control-Plane Integration Completion Megaprompt

## Role

You are the lead engineer completing the active AiSci research control plane: the Vite/TanStack Router dashboard, the FastAPI Ignition API, the SQLite operational read model, the worker, and project-owned pipeline integration.

Your deliverable is a trustworthy, local-first research control plane. It must show real project state, safely request registered work, preserve canonical science records, and never substitute mock AI/cluster telemetry for evidence.

Do not stop at passing shallow UI tests. Complete and verify the end-to-end contracts.

## Start here

Work in `/home/ubuntu/aisci`.

Read in full before editing:

- `AGENTS.md`
- `README.md`
- `ACTION_PLAN.md`
- `docs/ops/CURRENT_STATUS.md`
- `docs/ops/architecture-overview.md`
- `docs/ops/deployment-reference.md`
- `docs/ops/platform-backlog.md`
- `docs/user-manual/USER_MANUAL.md`
- `deployment/aisci-dashboard/AGENTS.md`
- `research/projects.toml`
- `research/robert/evidence-ledger.md`
- `research/robert/next-actions.md`
- `deployment/aisci-dashboard/ignition/pyproject.toml`

Then:

1. Run `git status --short --untracked-files=all`.
2. Preserve existing committed work, the dashboard redesign archive, and untracked `docs/ops/megaprompts/*.md`.
3. Do not reset, checkout, rebase, delete, or overwrite unrelated work.
4. Do not create a new status, backlog, or audit Markdown file.
5. Do not alter Robert’s canonical evidence ledger or task queue merely to accommodate a parser or demo UI.
6. Do not expose secrets through browser environment variables, logs, docs, tests, or commits.

## Reality check: do not trust prior completion claims blindly

The following are verified current conditions and must be treated as remaining work until independently fixed and tested:

- **Verified Baseline**: The frontend has successfully migrated to a pure Vite SPA using `@tanstack/react-router`. `@tanstack/react-start` has been fully removed. Types across the frontend (`src/lib/api.ts`) have been unified.
- `npm run typecheck`, `npm run lint`, and `npm run test:e2e` pass with 0 errors (all critical typing issues, physics model nomenclature mismatches, and SSR test timeouts are resolved).
- `deployment/aisci-dashboard/ignition/.venv/bin/python -m pytest tests` cannot run because that environment lacks `pytest`.
- Current docs contradict the repository: `research/projects.toml` registers both `robert-boson-manuscript` and `phd-audit`, while current docs state one registered project.
- The current API and UI contain new endpoints and route guards, but multiple backend contracts remain incomplete or misleading.

## Product boundary

AiSci is a research control plane:

```text
Browser
  → Dashboard
  → Ignition API
  → project registry + canonical project files + SQLite operational projection
  → validated project pipeline
  → physics-core environment and reproducible run artifacts
```

It is not a scientific authority.

- `research/<project>/evidence-ledger.md` is canonical for scientific claims.
- `research/<project>/next-actions.md` is canonical for science tasks.
- Successful jobs and good-looking fit cards do not promote claims.
- Keep Bose-Einstein, Boltzmann/Jüttner, Tsallis-Pareto, and Blast-Wave wording exact to their artifact/model keys.
- No active Onyx, DeerFlow, LiteLLM, MCP proxy, OpenSearch, Celery, Docker Compose, or model-routing platform exists in this checkout. Do not claim otherwise.
- The existing direct OpenRouter extraction client is optional and must not be represented as Gemini, a generic AI agent mesh, or a configured provider when no verified provider is available.

## Target outcome

A researcher must be able to:

1. Select a registered project.
2. See only routes and controls allowed by that project’s capabilities.
3. Inspect real evidence, tasks, literature, runs, fit diagnostics, anomalies, jobs, logs, and provenance.
4. Understand when data is stale, incomplete, unavailable, or malformed.
5. Request only a genuinely validated pipeline.
6. Follow a job from queued to completed/failed with real logs and artifacts.
7. Submit a review request without silently editing canonical science files.
8. Use the dashboard on desktop and mobile with accessible loading, empty, error, and unavailable states.

## Priority P0 — restore integrity before adding features

### 1. Consolidate build hygiene

- Keep `npm run typecheck`, `npm run lint`, `npm run build`, and `npm run test:e2e` as explicit package scripts. They must continue to pass without errors.
- Do not hide lint errors by weakening rules.
- Audit the committed `fix_tests*.sh` files in `deployment/aisci-dashboard/`. They are temporary-style helper scripts in an application root. Verify whether they have any remaining operational value; remove or relocate them to `deployment/helper/` only after confirming no required workflow depends on them.

### 2. Define one typed API contract

`src/lib/api.ts` currently mixes DTOs, duplicated domain types, unvalidated JSON, and endpoints that do not exist.

Create a single source for frontend API DTOs and query contracts.

Requirements:

- Define typed models for projects, capabilities, pipelines, preflight results, overview, health, fits, model descriptors, anomalies, literature, evidence, tasks, review decisions, jobs, artifacts, worker status, and errors.
- Use Zod or equivalent runtime validation at the fetch boundary.
- Remove duplicate `Paper`, `EvidenceRow`, task, agent, and anomaly definitions.
- Centralize query keys and mutation invalidation in `src/lib/queries.ts`.
- Remove `searchEvidence` unless you implement a tested, project-scoped `/evidence/search` API endpoint.
- Make client function names and API paths match exactly.
- Use typed TanStack links and redirects; do not re-introduce `any`.

### 3. Fix capability gating centrally

Current route-level `beforeLoad` checks repeatedly fetch projects directly and cast redirects.

Implement a single project loader/capability guard pattern that:

- Validates that the project exists.
- Uses cached project data where appropriate.
- Returns a deliberate 404 for an unknown project.
- Redirects capability-denied users to the project overview with an understandable unavailable message.
- Applies consistently to sidebar entries, header actions, route loaders, and rendered controls.
- Ensures `phd-audit` does not expose fit, anomaly, or physics-run controls.
- Does not leak project data through a global endpoint such as `/api/agents`.

### 4. Repair scientific status and review lifecycle

Current evidence/task update endpoints immediately insert decisions as `Approved`, despite returning “review requested.” This is unsafe and misleading.

Implement the following lifecycle:

```text
Dashboard action
  → proposed review decision
  → explicit approval or rejection
  → explicit authorized materialization
  → source-hash/concurrency validation
  → canonical update
  → projection sync and activity record
```

Requirements:

- Add an explicit `target_kind` such as `evidence` or `task`.
- Persist `target_id`, expected canonical-source hash, requested state, reviewer, rationale, review status, created/reviewed/applied timestamps, and materialization result.
- New dashboard requests must begin as `Proposed`.
- Approval/rejection must verify the decision exists and is in a valid transition state.
- Materialization must apply only approved decisions selected for materialization, not every pending decision indiscriminately.
- A stale source hash must block materialization and explain why.
- Task and evidence materialization must be implemented equivalently.
- The UI must say “Review requested” until materialization actually succeeds.
- Add a review queue page or a clearly scoped panel with approve, reject, and materialize actions. Use confirmation dialogs and show audit history.
- Do not silently promote science claims or tasks.

### 5. Make Markdown projection lossless and safe

The current Markdown parser can corrupt evidence columns when a narrative includes literal `|` characters. Unknown status text can be incorrectly interpreted or rendered.

Implement a robust projection strategy:

- Parse the canonical table structure using an approach tested against actual Robert files.
- Preserve raw canonical status text exactly.
- Maintain a separate UI classification only for styling; unknown statuses must remain visibly unknown.
- Never silently turn unknown states into `Proposed`, `Supported`, or another science state.
- Return per-row parse warnings and an explicit raw-source fallback when safe extraction is impossible.
- Parse task states and metadata from the actual canonical structure; do not fabricate dates, priorities, or state changes.
- Add fixtures containing literal pipes, escaped Markdown, unknown statuses, completed tasks, and malformed rows.
- Do not “fix” Robert’s Markdown automatically. Any canonical cleanup requires explicit user/researcher approval.

## Priority P0 — make pipeline and worker integration real

### 6. Replace fake pipeline preflight

Current `PipelineSpec.dry_run()` only serializes command metadata. `GET /pipelines` labels commands as available even when scripts do not exist.

Implement structured preflight.

Each pipeline response must include:

- `available: boolean`
- `checks: [{ name, passed, message }]`
- working-directory validity
- project/repository containment
- non-empty command
- interpreter/executable availability
- required-input checks
- required virtual environment/dependency checks
- capability eligibility
- output/run-directory strategy
- safe dry-run result when supported

Requirements:

- Do not judge safety using substring blacklists such as `"rm -rf"` alone.
- Keep command execution list-based; never invoke a shell for TOML-provided commands.
- Validate all resolved paths with `os.path.commonpath`.
- Return 4xx errors for unknown pipelines and invalid project/pipeline configurations.
- Disable unavailable UI actions and display the exact failed preflight checks.

### 7. Make project pipeline definitions executable

`research/robert/pipelines.toml` currently points to non-existent project-relative scripts. Correct this only after validating actual commands.

For physics fits:

- Use the verified `libs/physics-core/.venv/bin/python` physics runtime.
- Use the actual `libs/physics-core/cli.py` interface.
- Generate a job-owned, project-contained run directory.
- Persist that run directory on the job.
- Validate through a controlled dry-run before enabling the UI action.
- Do not run expensive fits as part of normal browser or E2E tests.

For `phd-audit`:

- Make its role explicit. If it remains a lightweight integrity check, label it accurately and do not present it as a research-analysis pipeline.
- Ensure capability gating prevents it from appearing as physics work.

### 8. Complete worker/job observability

Upgrade `worker.py`, database schema, and job endpoints so a job has an auditable lifecycle.

Required job fields include:

- project ID, pipeline ID, requester
- status
- created, started, updated, completed timestamps
- worker ID/heartbeat
- safe run directory
- log path
- exit code
- concise sanitized failure summary
- git commit
- artifact manifest
- input/config provenance

Requirements:

- Claim pending jobs atomically.
- Prevent duplicate active jobs atomically.
- Record `pending → running → completed|failed` transitions in activity.
- Capture failure details for nonzero exits, exceptions, and timeouts.
- Do not create empty log files from read-only requests.
- Expose logs by job ID, not inferred pipeline aliases.
- Keep streaming bounded and cancellable.
- Add a worker heartbeat and a real `/health` response that checks registry, database, and worker freshness.
- Ensure artifact manifest paths remain inside the project run directory.
- Add isolated worker tests using safe temporary fixture commands, not real physics jobs.

### 9. Repair database migration and isolation design

Replace the current single catch-all migration with explicit, independently idempotent migrations.

Address:

- Project-scoped paper and task uniqueness.
- Project-safe literature identities and claim/dataset idempotency.
- Review decision lifecycle fields.
- Worker/job provenance fields.
- A schema version migration path from existing runtime databases.
- Fresh database initialization.
- Upgrade path tests.

Tests must use a temporary database configured through an explicit test-only database path. Never run tests against the live dashboard database.

## Priority P1 — complete API and data integration

### 10. Correct fits, runs, and anomalies

The API and UI still contain inaccurate fit assumptions.

Implement:

- Run ID validation and traversal prevention for `run` and `compare_run`.
- Run metadata with complete/partial/invalid state and artifact parse warnings.
- Sorting by actual modification time or explicit run metadata, not lexical directory name.
- A stable backend model descriptor:
  - raw model key
  - family
  - component count
  - display label
- Dynamic UI filters and legends derived from those descriptors.
- Fit comparison data that compares the same quantity. Do not render chi² data in a temperature chart.
- A correctly named correlation heatmap unless actual covariance is available.
- Residual/pull panels only when real artifacts exist.
- Accurate incomplete-run states rather than fabricated fit output.
- Anomaly thresholds returned from the backend validation policy.
- Explicit UI mapping for known and unknown quality states.

Do not label `Bose` output as Bose-Einstein unless the artifact/model key establishes that it is the Bose-Einstein model.

### 11. Make overview and agents truthful

The overview still contains fabricated content such as 99.98% uptime, agent workloads, GPU throughput, replica consistency, latency, and static sparklines.

Replace it with a real project overview endpoint returning:

- canonical projection freshness and parse warnings
- evidence/task counts by actual state
- literature count
- valid/latest fit-run summary
- active/completed/failed job counts
- anomaly summary
- worker health
- recent activity
- pipeline availability

Requirements:

- Remove invented cluster/GPU/throughput telemetry.
- Remove or replace fake footer telemetry and fake git SHA.
- Link each card to a project-scoped route.
- Present empty, error, unavailable, and stale states explicitly.
- Keep the visual hierarchy restrained: one clear research-state message per screen, with data—not decoration—as the focal point.

### 12. Fix literature and AI-provider integration

Current literature behavior infers provider from paper IDs, does not fully expose provenance through Pydantic response models, and can duplicate claims/datasets. The UI and `/api/agents` also mislabel providers.

Implement:

- Explicit persisted source/provider, external identifier, provenance, and source hash.
- Idempotent paper, claim, and dataset ingestion.
- Project isolation even if two projects receive an identical external ID.
- Provider and bridge classification based on stored metadata/claim type, not ID/category heuristics.
- Accurate frontend provenance display.
- A provider-neutral extraction adapter with configuration-driven provider/model metadata.
- A no-provider state that reports extraction unavailable rather than pretending Gemini, OpenAI, or another service is active.
- Never expose provider API keys to browser code.
- Make `ingest_pipeline.py` project-scoped and compatible with authenticated/local API operation. Remove hard-coded Robert-only assumptions where project configuration should govern behavior.

### 13. Fix agents and logs

Either make agents project-scoped or label shared process information clearly.

- Replace the global `/api/agents` endpoint with project-scoped status where appropriate.
- Derive pipeline/agent state from real jobs and worker health.
- Do not claim an `ingest-pipeline` or `fit-pipeline` is active when actual registered IDs are `ingest-validation` and `fit-validation`.
- Do not label a provider as “Gemini Pro” when the code is configured for an OpenRouter model or no provider.
- Make job detail pages the primary location for logs and provenance.

## Priority P1 — frontend completion

### 14. Finish project routes

For portfolio, overview, evidence, tasks, fits, anomalies, jobs, literature, and agents:

- Use shared typed query hooks.
- Supply skeleton, empty, error, unavailable, and stale-data states.
- Make all mutations reflect actual server state.
- Keep tables usable on narrow screens with horizontal affordance or accessible card alternatives.
- Provide keyboard-accessible dialogs and focus restoration.
- Do not rely on color alone for status.
- Preserve `prefers-reduced-motion`.
- Ensure mobile navigation contains the same permitted project routes as desktop.
- Implement global search only with a real, project-scoped API. Otherwise remove the inert search input.

### 15. Strengthen end-to-end tests

The current six Playwright tests pass but do not completely prove end-to-end integration:

- Several mocks are incomplete.
- Tests can accidentally rely on the live API because route guards fetch `/projects`.
- Agent tests mock a path that the frontend does not request.
- The fit wildcard can intercept both fit data and run-list requests with the wrong payload.

Replace this with reliable test infrastructure:

- Start dedicated frontend/API test servers on test-only ports (avoiding port 5173 collisions with local dev workflows).
- Use a temporary test database and fixture project registry.
- Do not kill external listeners.
- Mock all route-loader and page requests deliberately, or run a fully seeded test backend.
- Cover:
  - portfolio selection
  - unknown project and capability-denied routes
  - `phd-audit` capability isolation
  - real model descriptor filtering
  - incomplete runs
  - unavailable preflight state
  - job queue/running/completed/failed transitions
  - job-specific logs
  - review request, approval, rejection, stale materialization, and successful materialization in fixtures
  - literature provenance
  - mobile navigation
  - keyboard navigation and no uncaught browser errors

## Runtime boundary

Do not use undocumented global Python.

Establish and document a reproducible runtime split:

- FastAPI/worker environment: explicitly provisioned and testable.
- Physics execution environment: `libs/physics-core/.venv/bin/python`.

If retaining `deployment/aisci-dashboard/ignition/.venv`, make it reproducible through `pyproject.toml` or requirements and ensure it contains all runtime/test dependencies. Update `start_dashboard.sh` to invoke explicit Python binaries rather than `python3`.

Do not claim either environment works until its tests run successfully.

## Documentation reconciliation

After implementation and verification, update only existing canonical documentation with verified facts:

- `docs/ops/architecture-overview.md`
- `docs/ops/CURRENT_STATUS.md`
- `docs/ops/deployment-reference.md`
- `docs/ops/platform-backlog.md`, only for accepted remaining work

Correct these facts:

- The frontend is Vite + React + TanStack Router.
- Two projects are currently registered, but `phd-audit` is skeletal unless proven otherwise.
- Pipelines are project-owned only once the code/config actually verifies this.
- The worker is local and SQLite-backed, not distributed infrastructure.
- Historical services remain absent.

Do not add a new status document, audit report, or parallel tracker.

## Verification gates

All must pass before completion:

```bash
cd deployment/aisci-dashboard
npm run typecheck
npm run lint
npm run build
npm run test:e2e
```

Run backend tests through the explicitly provisioned Ignition environment, for example:

```bash
cd deployment/aisci-dashboard/ignition
.venv/bin/python -m pytest tests
```

Also verify:

1. A fresh temporary database initializes and migrates successfully.
2. An existing fixture database upgrades successfully.
3. Pipeline preflight rejects the current missing-command scenario and accepts only a verified replacement.
4. A harmless fixture job completes through the worker with logs and artifact provenance.
5. A real physics CLI dry-run succeeds through the physics environment in a temporary project-contained run directory.
6. `bash start_dashboard.sh` starts the dashboard, API, and worker with the documented Python environments.
7. Both registered projects render correctly and capability gating holds.
8. No canonical science file changes unless an explicit, isolated materialization test intentionally performs one.

## Completion criteria

Finish only when:

- The application builds, lints, and tests cleanly.
- Dashboard labels, charts, agents, health, and pipelines are truthful.
- Project isolation works through API, UI, database, worker, and tests.
- Pipeline availability reflects executable reality.
- Jobs are observable end-to-end.
- Review decisions cannot silently alter canonical science.
- AI/provider integration is explicit, configured, and non-fabricated.
- Current operational docs accurately describe the verified system.
