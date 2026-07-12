**Instructions for the User:** Copy everything below the line and paste it into a fresh agent session.

---

You are a senior physicist–engineer working in the AiSci repository at `/home/ubuntu/aisci`. The previous session completed a full control-plane stabilisation pass (commit `52e946278`). All P0–P2 platform backlog items are now `Done` except **P2 Archive Hygiene**. The dashboard and Ignition API are live and healthy at `http://localhost:5173` and `http://localhost:8001`.

This session has **two tracks**. Work them in order. Track 1 is a short platform clean-up. Track 2 is the first science activation session using the stabilised control plane.

---

## Mandatory Intake Stage

Before doing anything else:

1. Read `AGENTS.md` in full.
2. Read `docs/ops/platform-backlog.md` and confirm the only Open row is **P2 Archive Hygiene**.
3. Read `research/robert/next-actions.md`. Identify the four active agent-proposed items (A-01, A-02, D-01, D-03) and the one Robert-owned item still awaiting a decision (O-05 Jacobian). Do **not** act on science items without confirming their status below.
4. Read `research/robert/evidence-ledger.md` (search for `Jacobian`, `Jüttner`, `D-01`, `source_hash`) to confirm the ledger state has not drifted since commit `52e946278`.
5. Run `git log --oneline -5` and confirm HEAD is `52e946278`. If the branch has diverged, stop and report.
6. Run `ss -ltnp '( sport = :5173 or sport = :8001 )'` to confirm both services are up. If either is down, run `bash start_dashboard.sh` (without `&`; it blocks — open a second terminal) and wait for both ports to be live before continuing.
7. Report findings as a brief pre-execution summary and **wait for explicit user approval before beginning Track 1**.

---

## Track 1 — Platform Clean-Up (P2 Archive Hygiene)

**Context:** `docs/ops/platform-backlog.md` has one remaining Open item: classifying legacy integration records. This track closes it.

### 1A. Audit remaining `docs/ops/` files for historical vs. active classification

Run:
```bash
ls docs/ops/
```

For each file that describes Onyx, DeerFlow, LiteLLM, MCP proxy, OpenSearch, Vespa, Celery, or RagEval systems that are **absent from the current repo checkout**, verify whether it already carries the front-matter note:
```
> Historical record only — not active operational guidance
```

If not, prepend that line to the file. Do not delete any file without verifying (a) no actionable item in it is unimplemented and missing from `platform-backlog.md` or `next-actions.md`, and (b) its git history provides sufficient preservation.

Files confirmed historical from prior session that already received the note: check each one. Files to audit specifically:
- `docs/ops/activepieces-integration.md`
- `docs/ops/k-dense-skills-reference.md`
- `docs/ops/kdense-agent-skills.md`
- `docs/ops/literature-corpus-policy.md`
- `docs/ops/mcp-endpoints.md`
- `docs/ops/mcp-hep-servers.md`
- `docs/ops/model-optimization-report.md`
- `docs/ops/model-selection-guide.md`
- `docs/ops/rag-evaluation-results.md`
- `docs/ops/rag-evaluation-set.md`
- `docs/ops/semantic-scholar-asta-api.md`
- `docs/ops/subtree-management.md`

### 1B. Update `docs/ops/README.md`

Ensure `README.md` lists every current file in `docs/ops/` with a one-line description and a `[historical]` or `[active]` tag. Remove any entries for files deleted in the previous session.

### 1C. Update backlog

In `docs/ops/platform-backlog.md`, move the **P2 Archive Hygiene** row to `Done` with evidence: list the files that received the historical marker and the date.

### 1D. Update `docs/ops/CURRENT_STATUS.md`

Update the **Last verified** date to today and correct any stale capability or limitation descriptions that no longer apply after the stabilisation pass. In particular:
- Remove or qualify the limitation note about Jobs/provenance since those are now implemented.
- Add a one-line note that `artifact_manifest` and `git_commit` are now populated by the worker.

### 1E. Commit Track 1

```bash
git add docs/ops/
git commit -m "chore(docs): close P2 archive hygiene — classify legacy ops files as historical"
git push
```

---

## Track 2 — Science Activation (Physics Pipeline)

> **Hard boundary:** Do not touch `research/robert/evidence-ledger.md` or `research/robert/next-actions.md` unless you are recording a validated artifact output or fixing an acknowledged error. Do not promote any claim beyond its current ledger status. Do not infer causality or root cause from suggestive fit results alone.

This track activates the three agent-proposed items in `next-actions.md` that are **not** gated on Robert's personal decision: **D-01**, **D-03**, and a targeted first step toward **A-01**.

---

### Phase 2A — Fix D-03: Wire `fitting_pipeline.py` to accept `--input`

**Item D-03** from `next-actions.md`:
> The pipeline script `fitting_pipeline.py` currently hardcodes paths to earlier test tables. Modify the script to accept an `--input` argument, defaulting to `libs/physics-core/data/fit_input_ins1735345.csv`.

**Steps:**
1. Read `libs/physics-core/fitting_pipeline.py` (or wherever it lives — check `find libs/physics-core -name fitting_pipeline.py`).
2. Locate the hardcoded path to the input CSV.
3. Add an `argparse` argument `--input` with `default` pointing to `libs/physics-core/data/fit_input_ins1735345.csv`. Preserve backward compatibility — if `--input` is not passed and the default file exists, proceed silently.
4. Run the script in test mode (if a `--test` or `--dry-run` flag exists) using `libs/physics-core/.venv/bin/python` to verify it reads the correct file without generating fit outputs.
5. Update `research/robert/next-actions.md`: move D-03 from agent-proposed to ✅ Completed.

---

### Phase 2B — Investigate D-01: Jüttner 3-component singularity

**Item D-01** from `next-actions.md`:
> The Fisher Information matrix shows the 3-component Jüttner parameterisation (T_stat, T_kin, β_s) is mathematically singular at U → 0. Execute `fit-anomaly-resolution` skill to recommend a non-singular baseline and document the mathematical proof for Robert.

**Steps:**
1. Read `agent-skills/fit-anomaly-resolution/SKILL.md` fully before acting.
2. Read `research/robert/evidence-ledger.md` sections for `Jüttner`, `singular`, and `U → 0` to understand the current evidence state.
3. Read `libs/physics-core/fitting_pipeline.py` and identify the 3-component Jüttner model implementation (search for `T_stat`, `T_kin`, `beta_s`, or `U`).
4. Construct the Fisher Information matrix for the 3-component model symbolically (use `sympy` if helpful; run with `libs/physics-core/.venv/bin/python`). Show algebraically that the determinant → 0 as U → 0.
5. Propose a non-singular 2-component replacement baseline following the skill's guidance. Do **not** implement the replacement yet — produce the mathematical argument only.
6. Write a concise analysis note to a **new dated run directory** `research/robert/runs/2026-07-12-d01-juttner-singularity-analysis/README.md` with:
   - The mathematical proof (symbolic determinant).
   - The proposed 2-component baseline name and its physical rationale.
   - A statement of what has NOT yet been verified (fit quality, chi²/ndf, literature comparison).
7. Update `research/robert/evidence-ledger.md`: add a new row for this analysis. Status: `Sanity checked`. Do not promote to `Supported`.
8. Update `research/robert/next-actions.md`: add D-01 to ✅ Completed referencing the run directory.

---

### Phase 2C — Symbolic Regression Scoping (A-01, scoping only)

**Item A-01** from `next-actions.md`:
> Use Symbolic Regression to map the boundary between the validity of the Jüttner derivation and the onset of non-extensive QCD scattering (the heavy tails).

This phase does **not** run PySR. It only scopes the computational feasibility.

**Steps:**
1. Check whether PySR is installed in `libs/physics-core/.venv`:
   ```bash
   libs/physics-core/.venv/bin/python -c "import pysr; print(pysr.__version__)"
   ```
2. If not installed, document the missing dependency in a new `research/robert/runs/2026-07-12-a01-symbolic-regression-scope/README.md` with:
   - The exact pip install command needed: `pip install pysr`.
   - The proposed input features: `(pT, multiplicity_class)`.
   - The proposed target: `residual = data - Jüttner_prediction` (from the existing `2026-06-20-phd-level-fits` run outputs).
   - The acceptance criterion: a symbolic expression with ≤ 5 terms that reduces residuals below 10% for `pT > 2 GeV`.
   - A note that this requires Robert's approval to activate (per `AGENTS.md` science rules).
3. If PySR **is** available, read the existing fit residuals from `research/robert/runs/2026-06-20-phd-level-fits/` and prepare (do not execute) a scoping script at `deployment/helper/a01_sr_scope.py` that:
   - Loads the residual CSV.
   - Defines the PySR `PySRRegressor` configuration (operators, complexity limit).
   - Prints a dry-run summary of input shape and feature columns.
   - Has a `# BLOCKED: awaiting Robert approval` comment at the top.
4. Update `research/robert/next-actions.md` under A-01: add a sub-item `[ ] Scoping complete — awaiting Robert approval to run PySR` and link the scoping directory.

---

## Track 2 Verification

After Phases 2A–2C:

1. Confirm `research/robert/next-actions.md` reflects all changes (D-03 done, D-01 done, A-01 scoped).
2. Confirm `research/robert/evidence-ledger.md` has the new D-01 claim row and no other unintended modifications.
3. Run a smoke test:
   ```bash
   bash .agents/skills/smoke-test/scripts/health_check.sh
   ```
4. Commit all science artifacts:
   ```bash
   git add research/robert/ deployment/helper/
   git commit -m "science(robert): activate D-01 Jüttner singularity analysis, fix D-03 pipeline input, scope A-01 SR"
   git push
   ```

---

## Hard Constraints

- Do not touch `research/robert/evidence-ledger.md` without reading it first and making only the minimum required addition.
- Do not promote any claim beyond `Sanity checked` without chi²/ndf, covariance, residuals, fit-range sensitivity, and baseline comparisons.
- Do not create scratch files in the working directory. Use `deployment/helper/` for ephemeral scripts.
- Do not paste any secrets. Reference only env var names and file paths.
- Use `libs/physics-core/.venv/bin/python` for all Python execution.
- If any phase produces an unexpected failure (import error, missing file, unexpected chi²), stop that phase, record the failure in the relevant run `README.md`, and report to the user before attempting a workaround.
- Do not act on **A-02 (Bayesian Inference)** or **O-05 (Jacobian)** — these are gated on Robert's approval.

---

## Reference

- HEAD at session start: `52e946278`
- Active project: `robert-boson-manuscript`
- Physics environment: `libs/physics-core/.venv/bin/python`
- Dashboard launcher: `bash start_dashboard.sh`
- Smoke test: `bash .agents/skills/smoke-test/scripts/health_check.sh`
- Evidence ledger: `research/robert/evidence-ledger.md`
- Science queue: `research/robert/next-actions.md`
