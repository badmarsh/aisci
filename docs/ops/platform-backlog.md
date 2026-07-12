# Platform Backlog


## How to update this file

- **Add** new issues at the top of the table with the correct priority.
- **Close** items by changing Status to `Done — YYYY-MM-DD` and moving the row to the Archive section below.
- **Never** leave a row with conflicting Done/Open signals — pick one.
- Security table: update "Current Tree Exposure" immediately after a key is rotated or scrubbed.

| Priority | System | Issue | Why It Matters | Next Action | Status |
|---|---|---|---|---|---|
| P1 | Infra | **Dashboard CQRS and Playwright Tests** — Replaced `subprocess.Popen` with safe asyncio-based background task execution. Added Playwright `page.route` intercepts to mock backend for E2E tests, verified 0 errors in CI mode, and ensured zero `8081` references remain. | Fixes blocking E2E test failures and improves Ignition engine's concurrency and task management. | None. | Done — 2026-07-12 |
| P1 | Infra | **Physics Structure Consolidation** — Merged `physics/` logic into `libs/physics-core/` and deleted the redundant root folder. Legacy python dashboard references dropped. | Removes structural duplication of physics core logic, conforming to monorepo standard. | None. | Done — 2026-07-12 |
| P1 | Infra | **Virtual Environment Consolidation** — Migrated the scattered physics virtual environments (`physics/.venv`, `physics_env`) into a single standard `libs/physics-core/.venv`. | Removes environment fragmentation and ensures predictable dependencies for tests and agents. | None. | Done — 2026-07-12 |
| P1 | Infra | **Merge aisci-phase3-review** — Unmerged Phase 3 architecture, physics CLI, Devendoring plan, and Agent skills (`ledger-anomaly-detector`, `science-hypothesis-generator`). | Required for moving away from DeerFlow and fully enabling autonomous loops. | Execute `git merge aisci-phase3-review`. | Done — 2026-07-11 |
| P1 | Infra | **Cherry-pick pr-28 agent skills** — Unmerged skills `data-visualization-plotting`, `hepdata-native-fetcher`, `sympy-mathematical-validator`. | Highly useful skills for HEP validations and data pipelines. | Execute `git checkout pr-28 -- .agents/skills/ && git commit -m "Cherry-pick new agent skills from pr-28"`. | Done — 2026-07-11 |
| P2 | Infra | **bgbw_jax_autodiff.py integration decision** — `libs/physics-core/src/bgbw_jax_autodiff.py` exists (5.7 KB) but is not referenced in any canonical doc, task queue, or test. | It provides JAX autodiff for BGBW, which would give exact Hessians and solve the T–β degeneracy without numerical finite-difference approximation. | Decision required: (a) integrate into fitting_pipeline.py as optional --autodiff flag, (b) deprecate and delete, or (c) document as experimental. | Done — 2026-07-11 |
| P2 | Infra | **ml_pipeline.py documentation** — `libs/physics-core/src/ml_pipeline.py` exists (5 KB) but is not referenced in any canonical doc, task queue, or test. | It is unclear whether this is an active experiment or an orphaned file. | Decision required: document its purpose in this backlog and either link to a GitHub Issue or delete. | Open |
| P1 | Architecture | **De-vendor DeerFlow** — `deployment/deer-flow/` is gitignored and ~50K lines of vendor code. Orchestration fragility is the #1 CI/CD reliability blocker. | Reproducible deploys and a clear surface area for the science runtime. | Create `docs/decisions/2026-07-09-deerflow-devendoring.md` committing to a Q3 2026 de-vendor timeline. Extract AiSci-specific skills into `agent-skills/`. Wire `libs/physics-core/cli.py` wrapper for standalone physics runs. | Done — 2026-07-11 |
| P1 | Research Loop | **Ledger Anomaly Detector skill** — no automated mechanism detects when `evidence-ledger.md` claim gates have been met or missed by existing run artifacts. | Closes Gap 3 (broken research loop) from the architecture review. Enables a nightly self-check without requiring Robert to manually compare runs/ to the ledger. | Create `agent-skills/ledger-anomaly-detector/SKILL.md`. Instruct it to detect promotable claims and draft entries under `## 🤖 Agent-Proposed` in `next-actions.md`. Wire as a nightly GitHub Actions cron job. | Done — 2026-07-11 |
| P1 | Research Loop | **AGENTS.md Autonomous Queue Management section** — agents have no constitutional rule for self-queuing after anomalous fit results. | Agents silently continue after discovering anomalies (e.g., T–β |ρ| > 0.9 in new bins), creating untracked science debt. | ✅ Added in Phase 3 review (2026-07-09). Rule requires agents to append to `## 🤖 Agent-Proposed` and cite literature before proposing hypothesis extensions. | Done — 2026-07-09 |
| P2 | Execution | **Sandboxed Python kernel for autonomous model testing** — agents cannot write and test new physics model code without modifying tracked `libs/physics-core/src/` files. | Closes Gap 1 (Static Sandbox). Enables frontier-style autonomous hypothesis testing comparable to OpenHands. | Provision a persistent, isolated Jupyter kernel (or `subprocess`-based sandbox) reachable as a DeerFlow tool. Kernel reads `libs/physics-core/data/`, writes only to `research/robert/runs/…/scratch/`. | Open |
| P2 | Execution | **`libs/physics-core/cli.py` standalone wrapper** — `fitting_pipeline.py` can only be invoked as a script; it is not callable from DeerFlow, MCP, or CI without shell escaping. | Required for Track B (de-vendoring) and Track A (auto-FitSpec promotion PRs). | Create `libs/physics-core/cli.py` with `argparse`: `--run-dir`, `--data-path`, `--model`. Returns structured JSON summary of chi²/ndf, AIC, BIC to stdout. | Open |

| P1 | DeerFlow | **Docker Compose startup failure — missing BETTER_AUTH_SECRET** — `docker compose` failed with "empty section between colons" errors because critical environment variables (BETTER_AUTH_SECRET, DEER_FLOW_*) were not loaded from `.env` in project root when compose file was in `docker/` subdirectory | Containers could not start; appeared as "hydration errors" but was actually a docker-compose configuration issue preventing any container initialization | Added `BETTER_AUTH_SECRET` to `.env`, removed stale containers, started stack with explicit `--env-file .env` flag. All containers now running, HTTP 200 on frontend, gateway logs show successful config load and sqlite backend initialization. All critical config.yaml settings preserved (sandbox mounts, run_events backend, gemini subagents, loop detection). | Done — 2026-05-31 |
| P1 | Ops | **Milestone closure: RAG hardening + ops baseline (2026-05-31)** — five Next-Ops follow-ups landed in one push: persona snapshot exporter, Scite/Consensus liveness probe, extensions_config regen helper with idempotent `--check`, RAG baseline runner emitting JSON artifacts plus the first usable baseline, literature curation policy. | Closes the final operational gaps from the milestone closure note: stack rebuilds are now reproducible from snapshot, OAuth state is observable from cron, the example MCP config can no longer drift unnoticed, and the eval runner produces diffable artifacts on a schedule. | Helpers under `deployment/helper/` (`export_persona_snapshot.py`, `check_mcp_liveness.py`, `regenerate_extensions_config_example.py`, refactored `run_rag_tests.py`); docs under `docs/ops/literature-corpus-policy.md`, `docs/ops/rag-baselines/README.md`, `deployment/onyx/snapshots/README.md`. | Done — 2026-05-31 |
| P1 | Security | Rotate DeerFlow AUTH_JWT_SECRET after agent session exposure | `deployment/deer-flow/.env` | Done 2026-05-30 — new secret generated and deployed |
| P0 | Security | **Live API keys in tracked `.env`** — `DASHSCOPE_API_KEY`, `NVIDIA_API_KEY`, and `ONYX_API_KEY` are present in `deployment/onyx/.env` which is committed to git | These are dev keys; user confirmed rotation is not required | Skipped — GitHub Issue #7 closed | Closed — 2026-05-30 |
| P0 | Security | **Brave Search API key rotated** — old key `BSA_fhKzGSCyLKHHngce8P-V8rvf5qt` was hardcoded in tracked file; replaced with placeholder 2026-05-30; rotated by user 2026-05-30 | Key was in git history; new key must be injected via non-tracked env or DeerFlow env mechanism | Inject rotated Brave key into `.env.local` or DeerFlow `.env` to restore DeerFlow web search. | Done — rotated 2026-05-30 |
| P1 | Vision | **Vision model misconfiguration resolved** — aligned references to `qwen2.5vl:7b` since it is successfully pulled in Ollama and set `IMAGE_MODEL_NAME=qwen2.5vl:7b` in `.env` | Image/table summarization during PDF indexing was misaligned with the active local visual RAG model | Aligned `.env` to `qwen2.5vl:7b` to match LiteLLM config, `onyx-configure.md`, and the active Ollama model. Verified that `qwen2.5vl:7b` and `gemma2:27b` are pulled and active. | Done — 2026-05-30 |
| P1 | Docs | Documentation drift between canonical docs and actual deployment | Port numbers were incorrect, DeerFlow was briefly documented as down incorrectly, and recent fixes were not discoverable | Fixed 2026-05-30: corrected ports and service status in deployment-reference.md, HANDOFF.md, README.md, and the status snapshot docs. | Done — corrected 2026-05-30 |
| P2 | MCP | Serena MCP for semantic code tools | Serena gives coding agents symbol-level navigation and editing that complements text search and filesystem tools | **Removed 2026-05-04**: Uninstalled per user instruction. Removed from `mcp-endpoints.md`, `mcp_config.yaml`, and `extensions_config.json`. | Removed |
| P1 | MCP | Scite and Consensus MCP OAuth flows were unverified | Uncertainty about whether tools available in personas were actually reaching upstream APIs | **Verified path 2026-05-06**: DeerFlow gateway connects to `onyx-mcp-proxy:80`; Scite and Consensus return `401` without OAuth, proving proxy reachability. Complete OAuth from a capable MCP client for real literature calls. | Done — route verified; OAuth still client-owned |
| P2 | DeerFlow | `deployment/deer-flow/deer-flow.code-workspace` status was unresolved | `git log --diff-filter=D -- deployment/deer-flow/deer-flow.code-workspace` shows it was removed from tracking in `f4775fdf0`; a local ignored copy can still exist because `.gitignore` ignores `deployment/deer-flow/` | Treat the workspace file as ignored local runtime/editor material; do not re-track it unless the de-vendoring plan explicitly needs it | Done |
| P2 | DeerFlow | Seven `*_orig.py` / `*.py.orig` upstream vendor reference copies remain in `deployment/onyx/` | Files `github_connector.py.orig`, `llm_loop_orig.py`, `llm_step_orig.py`, `model_configs_orig.py`, `multi_llm_orig.py`, `tracing_wrap_orig.py`, `utils_orig.py` are upstream reference snapshots tracked in git; they add noise, inflate diffs, and risk diverging silently from the live patched copies | **Fixed 2026-05-04**: Approval granted and files removed from git history. | Done |
| P1 | DeerFlow | Service orchestration and model configuration | DeerFlow services were previously failing to start due to container name conflicts and configuration syntax errors. Environment variable resolution for `$OPENAI_API_KEY` was also failing due to brace syntax `${}`. | **Fixed 2026-05-02**: GPT-4 model successfully registered in `config.yaml` using `$VAR` syntax. Service stack started with `make docker-start` after clearing stale containers. Logs confirm `Configuration loaded successfully`. | Done — 2026-05-02 |
| P2 | DeerFlow | Programmatic agentic runs | Understanding the v2 "agent" structure and execution workflow for research automation | Agents are LangGraph graphs in v2. Programmatic access is via `DeerFlowClient` in `packages/harness/deerflow/client.py` or the REST API at `http://localhost:2026/api`. | Done — 2026-05-02 |
| P1 | DeerFlow | HTTP 404 on `GET /runs/{run_id}` — run IDs not found after creation | `run_events.backend: memory` in `config.yaml` means run state is never written to persistent storage; every run ID becomes invalid after the spawning request completes or the container restarts | **Fixed 2026-05-03**: Changed `run_events.backend` from `memory` to `db` in live `config.yaml`; removed conflicting legacy `checkpointer:` block (was splitting LangGraph state into a separate `checkpoints.db`); fixed `summarization:` YAML nesting bug (4 keys were indented inside `keep:` instead of as siblings); corrected `nvidia-qwen3-5-122b` `base_url` from `$OPENROUTER_API_BASE` → `$NVIDIA_API_BASE`. `deployment/deer-flow/config.example.yaml` updated in git to reflect all fixes. | Done — 2026-05-03 |
| P1 | DeerFlow | AIO Sandbox file visibility drift — uploaded/unzipped files not accessible to sandbox agents | When `AioSandboxProvider` uses deterministic persistent mounts, `sync_to_sandbox=False` skips the gateway's `_make_file_sandbox_writable()` call entirely. Files written by the gateway inherit a restrictive host umask, making them inaccessible to the sandbox user. | **Fixed 2026-05-03**: `deployment/deer-flow/backend/app/gateway/routers/uploads.py` patched to call `_make_file_sandbox_writable(file_path)` unconditionally for every uploaded file upon creation, and updated to set both `S_IROTH` and `S_IWOTH`. Change is live on host but not committed to git (deployment/deer-flow/ is gitignored). Re-apply after any container rebuild or volume reset. See `docs/ops/troubleshooting.md` for the full patch. | Done — 2026-05-03 |
| P2 | DeerFlow | DashScope API keys hardcoded in `config.yaml` | A literal DashScope key appeared inline in model entries for DashScope models instead of referencing `$DASHSCOPE_API_KEY` env var | **Fixed 2026-05-04**: Keys are fully abstracted behind `$DASHSCOPE_API_KEY` in `config.yaml` and `.env.example`. Rotate the exposed key; do not print it in docs or chat. | Done for config; rotation required |
| P0 | Infra | Hardcoded secrets in `deployment/onyx/.env` | Provider keys had been stored in tracked and local env/config files before cleanup | **Fixed config 2026-05-06**: `.env` is now tracked as a secret-free defaults file and `.env.local` is ignored. Rotation remains required because values are present in history. | Done for config; rotation tracked above |

## Audit Notes (2026-04-30)

### Items C–G — findings summary

**C. nginx path vs routing config cross-check**
- `mcp_config.yaml` now exists as a repo-local client reference; `deployment/onyx/nginx_configs/mcp_proxy.conf.template` remains the live nginx proxy template.
- `/consensus/` → `https://mcp.consensus.app/mcp/` — `proxy_pass_header Authorization` correctly forwards the client-supplied OAuth Bearer token; no static token injection (correct).
- `/scite/` → `https://api.scite.ai/mcp` — no static auth injection; live empty-request tests return route/auth-body statuses rather than the earlier 404.
- **Both Scite and Consensus confirmed returning real API results in chat session `35a68f12-3df2-4652-8548-330c5dd86b1d` (2026-05-02).**

**D. litellm_config.yaml verification — all PASS**
- `router_settings.timeout: 300` ✓
- `router_settings.retry_after: 10` ✓
- `gemma2:27b` present both as standalone alias and as weight-1 fallback in `qwen-cloud-fast` pool ✓
- Ollama endpoint `http://ollama:11434/v1` used by all local models ✓

**E. docs/ops/onyx-rag-optimization-2026-04-27.md**
- Resolved after the original audit: the file exists and now records the Alibaba/1536 retrieval-stack status plus the OpenSearch parity gate.

**F. deployment/deer-flow/ vendor files**
- `deer-flow.code-workspace` was removed from tracking in `f4775fdf0`; any present copy is ignored local editor/runtime material.
- Other upstream vendor examples present: `config.example.yaml` (38 KB), `extensions_config.example.json`, `.env.example`, `.gitignore`, `.dockerignore`. These are `.example` copies and lower-risk, but should be reviewed during any de-vendoring migration.
- Seven `*_orig.py` / `*.py.orig` files remain in `deployment/onyx/` — approval-gated removal (see backlog row above).

**G. research/robert/ ops/platform content check**
- ✅ No ops or platform content found. All files are scientific research artefacts: `evidence-ledger.md`, `fit-plan.md`, `next-actions.md`, `referee-report-draft.md`, `science-questions.md`, `validation-plan.md`, `workflow.md`, plus `archive/`, `manuscript/`, `runs/` subdirectories.

## Operational Guardrails

- [ ] Implement content-hash signed run artifacts so `reproducible-physics-runner` emits JSON with SHA256 of fit inputs and outputs, and `science-ledger-manager` links to the hash rather than an LLM summary.
- [ ] Add a model-selection-check sub-task to the physics agent so it computes AIC, BIC, and chi-squared per dof for every active model variant after each fit run.
- [ ] Encode pT gate values as versioned `research/robert/config/ptgates.json`, and require `reproducible-physics-runner` to load and record the applied gate values in each run artifact header.
- [ ] Use physics_env: Use the existing virtual environment in `libs/physics-core/.venv` which already has `matplotlib` 3.10.9 and other dependencies installed.
- [ ] Move DashScope API key out of `config.yaml` into `.env` as `$DASHSCOPE_API_KEY` (see security hygiene row above).

## Security Audit Findings (updated 2026-05-31)

Keys still present in `deployment/onyx/.env` (tracked file). These are dev/personal keys; user confirmed rotation is not required for current tree exposure (Issue #7 closed). Historical exposure in git history is noted for reference.

| Provider | Current Tree Exposure | Historical Exposure (SHAs) | Variable Names | Status |
|---|---|---|---|---|
| Qwen/DashScope | Yes — `.env` line 313 (new key rotated 2026-05-31) | f64e7c9 | DASHSCOPE_API_KEY | Rotated 2026-05-31 |
| NVIDIA | Yes — `.env` line 305 | 888874d, f64e7c9 | NVIDIA_API_KEY | In use — rotation not required |
| Gemini | No | 471d897, d49a9a6 | GEMINI_API_KEY | Rotated 2026-05-30 |
| OpenRouter | No | e370048, 6ff9470, b3376af, 9e85623, 888874d, 9828157 | OPENROUTER_API_KEY | Rotated 2026-05-30 |
| Brave | No | f64e7c9, 471d897, d49a9a6, e370048, 6ff9470, 9e85623, 888874d | BRAVE_SEARCH_API_KEY | Rotated 2026-05-30 |
| ElevenLabs | No | 471d897, d49a9a6, e370048, 6ff9470, 9e85623, 888874d | ELEVENLABS_API_KEY | Rotated 2026-05-30 |
| HF | No | 471d897, d49a9a6, e370048, 6ff9470 | HF_TOKEN | Rotated 2026-05-30 |
| MCP Proxy | No | 471d897, d49a9a6, 942da26, 1286998 | MCP_PROXY_AUTH_TOKEN | Rotated 2026-05-30 |

**Note:** `deployment/onyx/.env` is tracked intentionally as a dev-defaults file. Live production keys belong in `.env.local` (gitignored). The `~/.bashrc` `DASHSCOPE_API_KEY` export was updated to the new key on 2026-05-31.


| Gap Category | Findings | Next Action | Status |
|---|---|---|---|
| Structural Gap | `docs/ops/` and `docs/decisions/` markdown files — Documentation connector (CC pair 6, connector 4) created 2026-05-30, ACTIVE, refresh_freq=86400. | Q5 confirmed retrieving from `ops_onyx-rag-optimization-2026-04-27.md` in baseline run 2026-05-31T01-08-10Z. | Closed — 2026-05-31 |
| Literature Gap | Khuntia (2019) and Rath (2020) PDFs re-uploaded 2026-05-30 via `upload_literature_pdfs.py`; index attempt 42 triggered. | Q1 confirmed retrieving Khuntia/Rath citations in baseline run 2026-05-31T01-08-10Z. | Closed — 2026-05-31 |
| Eval Gap | `run_rag_tests.py` was returning zero hits due to LiteLLM `BadRequestError` (old DashScope key + wrong model names). | Runner refactored 2026-05-31 to emit JSON artifacts under `docs/ops/rag-baselines/`; first usable baseline committed (3/5 with answer + retrieval, Q2/Q3 hit transient `nvidia-balanced` rate-limit). Cron snippet wired in `deployment/onyx/monitoring/README.md`. | Closed — 2026-05-31 |
| Curation Gap | No documented intake/refresh/dedupe path for literature PDFs. | `docs/ops/literature-corpus-policy.md` codifies the canonical add/remove/refresh flow and the dedup rules. | Closed — 2026-05-31 |
| Persona Snapshot | No reproducible export of persona id=2 (and siblings) for stack rebuilds. | `deployment/helper/export_persona_snapshot.py` writes daily snapshots under `deployment/onyx/snapshots/<date>/`; first snapshot landed 2026-05-31. | Closed — 2026-05-31 |
| OAuth Liveness | `check_health.sh` had no Scite/Consensus probe. | `deployment/helper/check_mcp_liveness.py` added; wired into `monitoring/check_health.sh` as a hard-fail-on-proxy-error / soft-warn-on-missing-token check. Tokens themselves still operator-owned. | Closed — 2026-05-31 |
| Extensions Config Drift | Live `deployment/deer-flow/extensions_config.json` had drifted from tracked example (placeholder GitHub token, `$file:/tmp/...` token paths, null placeholders). | `deployment/helper/regenerate_extensions_config_example.py` re-derives the example from the live file with secrets re-abstracted to `$ENV_VAR`. Idempotent (`--check` flag for CI). Example regenerated 2026-05-31. | Closed — 2026-05-31 |

**Targeted Re-indexing Plan for `docs/`:**
1. **Confirm connector:** Verify CC pair 6 covers `docs/ops/` and `docs/decisions/` with `*.md` filter, excludes `docs/archive/`.
2. **Document Set:** Attach CC pair 6 to `AiSci-System-Docs` doc set (meta-knowledge personas only, not physics personas).
3. **Validation:** Run RAG Q3/Q5 and verify exact command/explanation retrieval.


## Operational State & Backlog Reconciliation

1. **Approval Gates Validation**:
   - Checked `agent-skills/hitl-checkpoint-manager/SKILL.md` and `agent-skills/analysis-handoff-router/SKILL.md`. Both correctly explicitly warn against overwriting validated claims or require offering a handoff without automatic commits, matching the canonical approval gate constraint.

