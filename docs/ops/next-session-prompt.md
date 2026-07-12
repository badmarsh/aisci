# Next Session Prompt

_Last updated: 2026-05-17_

Two prompts are maintained here: one for **platform/ops** work, one for **science workflow** work. Use whichever matches your session goal.

---

## Prompt A — Platform / Ops (unchanged from 2026-05-06)

Use this prompt to continue the AiSci platform repair work in a fresh coding
agent session.

```text
You are continuing the AiSci Onyx/DeerFlow platform repair.
Repo: /home/ubuntu/aisci, GitHub: badmarsh/aisci.

Read first:
- AGENTS.md
- agent-skills/git-worktree-guard/SKILL.md
- agent-skills/aisci-ops-auditor/SKILL.md
- agent-skills/secret-config-auditor/SKILL.md if touching env/config
- docs/ops/platform-backlog.md
- docs/ops/onyx-configure.md
- docs/ops/mcp-endpoints.md
- docs/ops/deployment-reference.md

Current known-good state from 2026-05-06:
- Onyx health endpoint returned 200.
- Redis AOF was verified with `aof_enabled:1`.
- alembic head is `14162713706c`.
- `search_settings.multilingual_expansion` exists again as `varchar[] not null
  default '{}'` because the recreated `craft-latest` background image expects
  it during `check_for_indexing`.
- Active embedding is `Alibaba-NLP/gte-Qwen2-1.5B-instruct`, 1536 dims,
  search_settings id 10.
- `deployment/helper/sitecustomize.py` is required for Transformers 5 / Qwen2.
- `deployment/onyx/.env` is tracked and secret-free; `.env.local` is ignored.
- Craft should remain enabled: `ENABLE_CRAFT=true`, `IMAGE_TAG=craft-latest`.
- Onyx MCP host route is `http://127.0.0.1:8095/...`.
- DeerFlow container route is `http://onyx-mcp-proxy:80/...`.
- Onyx MCP submodule URL is `https://github.com/badmarsh/onyx-mcp-server.git`;
  do not point the parent repo at an unreachable local submodule commit.
- GitHub Issues are now the active work layer; canonical docs stay in repo.
  Start with issues #4 (key rotation), #5 (Onyx docs connector monitoring),
  and #6 (docs/backlog migration).
- Onyx Documentation connector is CC pair 11 / connector 15. Its
  `refresh_freq` was reduced to 86400 seconds on 2026-05-06.
- LiteLLM has RAG routes `qwen-rag-fast`, `qwen-rag-balanced`,
  `qwen-rag-vision`, and local fallback `qwen-rag-local`. Probe with
  `deployment/helper/litellm_quota_check.py --timeout 90`.

Hard constraints:
- Do not restart `onyx-db`.
- Do not print secrets or modify `.env.local` unless explicitly asked.
- Do not change embedding dimensions or switch active search_settings id 10.
- Keep platform details out of science files.
- Preserve unrelated user changes.

Next highest-value work:
1. Rotate provider/tool API keys listed in issue #4 and the 2026-05-06
   secret-history audits, then update only ignored private env/config. Do not
   commit key values.
2. Monitor the next Onyx Documentation connector run from issue #5. Confirm it
   does not retry every 30 minutes, does not hit heartbeat timeout, and does not
   produce repeated DashScope 429s.
3. Start issue #6 by migrating only active open backlog rows to GitHub Issues,
   then shrink `docs/ops/platform-backlog.md` instead of adding new reports.
4. Fix the `onyx-mcp-server` full Jest failures around `send-chat-message`
   nock expectations, then remove the need for `--no-verify` pushes.
5. Rebuild `onyx-python-webdeps:3.11` reproducibly once Docker buildx and PyPI
   DNS are healthy.
6. Verify real DeerFlow MCP tool calls after the `extensions_config.json` route
   update. The gateway was restarted on 2026-05-06 and basic connectivity to
   `onyx-mcp-proxy:80` passed, but an authenticated end-to-end tool call should
   still be exercised.
7. Add monitoring for `onyx-background` errors, Redis queue depth, and Alembic
   version drift.
8. Decide whether OpenSearch retrieval is worth the memory cost or whether a
   measured Vespa-only fallback should reclaim RAM.

Before closing:
- Run `git status -sb`.
- Run `docker compose config --quiet` from `deployment/onyx`.
- Check `curl -fsS http://127.0.0.1:3000/api/health`.
- Report what was changed, what was pushed, and any remaining test gaps.
```

---

## Prompt B — Science Workflow: Data Collection → Model Training → Documentation

Use this prompt to execute the AiSci physics research workflow in a fresh local agent session.

```text
You are continuing the AiSci physics research and documentation workflow.
Repo: /home/ubuntu/aisci, GitHub: badmarsh/aisci.

Read first (in this order):
- AGENTS.md
- agent-skills/git-worktree-guard/SKILL.md
- research/robert/next-actions.md       ← canonical science task queue
- research/robert/evidence-ledger.md    ← canonical claim-status file
- physics/README.md
- docs/ops/critical-components.md

Current state as of 2026-05-17:
- Physics scripts are ready but blocked on data:
  - `libs/physics-core/src/fitting_pipeline.py`        ready; awaiting `libs/physics-core/data/fit_input.csv`
  - `libs/physics-core/src/tsallis_physics_validation.py`  ready; awaiting data
  - `libs/physics-core/src/boson_paper_analysis.py`    green (all symbolic sections pass)
  - `libs/physics-core/src/sympy_validation_agent.py`  ready
  - `libs/physics-core/src/data_loader.py`             ready
- Virtual environment: `libs/physics-core/.venv` — use it for all script runs.
  It already has matplotlib 3.10.9 installed.
- Tests in `libs/physics-core/tests/` — run with `cd physics && pytest` using `physics_env`.
- Science task queue item [B-01] is the primary blocker: Robert must supply the
  per-multiplicity-bin pT spectrum table (bins 21-30 through 126-150) before
  fitting can run. HEPData record `ins1419652` provides only inclusive spectra.
- Science task [O-02] is open and does not require data: Robert to confirm
  whether U2 ≈ 0.011 ± 0.847 is a known instability at high multiplicity.
- Science task [O-03] (train and validate fitting pipeline) is defined and
  ready to execute the moment `libs/physics-core/data/fit_input.csv` exists.

Step 1 — Data Collection and Preprocessing:
  If Robert has provided a data table, save it as `libs/physics-core/data/fit_input.csv`
  following the format spec in `research/robert/archive/data-onboarding.md`.
  Run `libs/physics-core/src/data_loader.py` to verify integrity. Clean, normalize, and
  check for missing bins or inconsistent uncertainties. Log outcome to
  `research/robert/runs/YYYY-MM-DD-data-load/README.md`.

Step 2 — Model Training and Validation [O-03]:
  Once `fit_input.csv` exists:
  1. Activate `libs/physics-core/.venv` and run `libs/physics-core/src/fitting_pipeline.py`.
  2. Profile execution: time each fitting loop and scipy optimization call;
     save the profile report to `physics/reports/fitting_profile.txt`.
  3. Run `libs/physics-core/src/tsallis_physics_validation.py` — verify T, q, n converge
     within physical bounds; log chi2/ndf anomalies.
  4. Run `libs/physics-core/src/sympy_validation_agent.py` — confirm symbolic derivations
     match numerical outputs within floating-point tolerance.
  5. Cross-validate `boson_paper_analysis.py` outputs against reference values
     in `research/robert/evidence-ledger.md`. Flag deviations beyond tolerance.
  6. Extend `libs/physics-core/tests/test_fitting_pipeline.py` with:
     - Edge-case tests: out-of-bounds parameters, empty dataset inputs.
     - Regression tests: assert chi2/ndf, T, U, n per bin are reproducible.
  7. Save all artifacts (chi2/ndf, covariance, residuals, plots) to
     `research/robert/runs/YYYY-MM-DD-fitting-pipeline-validation/`.
  Do NOT promote any fit result beyond `Sanity checked` in the evidence ledger
  until chi2/ndf, covariance, correlations, residuals, fit-range sensitivity,
  and baseline comparisons are all recorded.

Step 3 — Simulation and Analysis:
  Run a full end-to-end pipeline:
    data_loader → fitting_pipeline → tsallis_physics_validation → boson_paper_analysis
  Capture all stdout/stderr, timing metrics, and output plots.
  Compare against the prior run in `research/robert/runs/2026-05-04-tsallis-validation/`
  to detect regressions. Save to `research/robert/runs/YYYY-MM-DD-full-run/`.

Step 4 — Documentation and Reporting:
  After a successful pipeline run:
  1. Generate a Python-based run report: use `python-executor` to produce a
     Markdown summary of inputs, outputs, chi2/ndf table, parameter table,
     residual plots, and any flagged anomalies. Save to
     `research/robert/runs/YYYY-MM-DD-full-run/report.md`.
  2. Update `research/robert/evidence-ledger.md` — add evidence links and
     update status for any claims that now have run support. Merge with existing
     rows; do not duplicate.
  3. Update `research/robert/next-actions.md` — mark [O-03] completed, add any
     new follow-up tasks that the run reveals.
  4. Do NOT create a new standalone report markdown by default. Prefer updating
     `evidence-ledger.md` and `next-actions.md` with the smallest useful note,
     per AGENTS.md follow-through rules.

Hard constraints:
- All script outputs are "Sanity checks" only until evidence-ledger support exists.
- Do not infer causality from fit behavior alone.
- Keep Bose-Einstein vs Boltzmann/Juttner wording explicit.
- Do not interpret fit parameters physically until chi2/ndf, covariance,
  correlations, residuals, fit-range sensitivity, and baseline comparisons exist.
- Keep platform details (Onyx, DeerFlow, Docker) out of science files.
- Put temporary helper scripts in `deployment/helper/`, not in `libs/physics-core/src/`.
- Do not create empty placeholder run files.
- Preserve unrelated user changes in the working tree.

Before closing:
- Run `cd physics && pytest` and confirm all tests pass.
- Run `git status -sb` — commit only intentional changes.
- Report what was run, what was changed, what was pushed, and any remaining
  blockers or open questions for Robert.
```
