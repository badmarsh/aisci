# Robert — Science Next Actions

This is the canonical task queue for Robert's physics workflow.
Platform-blocked items (waiting on Ollama, Scite key, etc.) are noted separately; their resolution is tracked in Multica Issues.

Science tasks become active only after acceptance by Robert. Do not add, remove, or reword items without Robert's approval.

Evidence states referenced here are defined in `docs/decisions/2026-04-26-science-evidence-standards.md`.

---

## 🔴 Blocked — Data Table Required

### [B-01] Supply per-multiplicity-bin pT spectrum table
**Blocking:** `fitting_pipeline.py`, `tsallis_physics_validation.py`, all chi2/ndf results, and **[O-03]** below
**What is needed:** Per-bin pT spectra matching multiplicity classes `21–30, 31–40, 41–50, 51–60, 61–70, 71–80, 81–90, 91–100, 101–125, 126–150`
**Why HEPData is insufficient:** Record `ins1419652` returns only inclusive spectra, not per-class bins
**Action:** Robert to provide the data table directly, or identify the correct HEPData record / paper table number
**Unblocks:** `data_loader.py` → `fit_input.csv` → full fitting pipeline → **[O-03]**

---

## 🟡 Open — Can Proceed Now (symbolic layer is unblocked)

### [O-02] Confirm U₂ ≈ 0.011 ± 0.847 is a known instability
**Status in ledger:** Flagged — numerics show U₂ unconstrained at high multiplicity
**What is needed:** Robert to confirm whether this is expected (a known fitting instability at high multiplicity in the original paper) or a new finding
**Action:** Robert reads `boson_paper_analysis.py` §7 output and provides a one-line confirmation or correction for the ledger

### [O-03] Run and validate fitting pipeline on preprocessed pT spectra
**Depends on:** [B-01] — requires `physics/data/fit_input.csv` to exist
**Infrastructure status:** `fitting_pipeline.py` is complete — chi2/ndf, covariance, AIC/BIC, residuals, pulls, and diagnostic plots are all implemented and tested. The pipeline is blocked only on the input data, not on implementation.
**Action:**
- Use `python-executor` to run `physics/src/fitting_pipeline.py` against `physics/data/fit_input.csv`. Use the latest model architecture and hyperparameters defined in the script.
- Use `python-performance-optimization` to profile the fitting loops, scipy optimization calls, and data loading steps. Output a performance report to `physics/reports/fitting_profile.txt`.
- Use `python-testing-patterns` to extend `physics/tests/test_fitting_pipeline.py` with edge-case tests for out-of-bounds parameter inputs and empty dataset handling. Add regression tests asserting key output metrics (chi2/ndf, T, U, n per bin) are reproducible across runs.
- Cross-validate outputs of `boson_paper_analysis.py` against reference values in `research/robert/evidence-ledger.md`. Flag any deviation exceeding defined tolerance thresholds.
- Run `physics/src/tsallis_physics_validation.py` to verify Tsallis distribution parameters (T, q, n) converge within expected physical bounds. Log any fit failures or chi²/ndf anomalies.
- Run `physics/src/sympy_validation_agent.py` to confirm symbolic derivations match numerical outputs from `fitting_pipeline.py` within floating-point tolerance.
- Save all run artifacts (chi2/ndf, covariance, parameter correlations, residuals, plots) to `research/robert/runs/YYYY-MM-DD-fitting-pipeline-validation/`.
- Do not promote any parameter to physical interpretation until chi2/ndf, covariance, correlations, residuals, fit-range sensitivity, and baseline comparisons are recorded in `evidence-ledger.md`.

**Prompt (copy into agent session):**
```
Run and validate the physics curve-fitting pipeline on the preprocessed spectra in
physics/data/fit_input.csv. This is NOT a machine learning task — the pipeline uses
scipy curve_fit / minimize for chi² minimisation of the Jüttner/Boltzmann distribution
against measured pT spectra. Do NOT use ML frameworks (PyTorch, sklearn, etc.).
Steps:
Run physics/src/fitting_pipeline.py against physics/data/fit_input.csv.
Profile the scipy optimisation calls and data loading using cProfile or line_profiler.
Output a performance report to physics/reports/fitting_profile.txt.
Extend physics/tests/test_fitting_pipeline.py with edge-case tests for out-of-bounds
parameter inputs and empty dataset handling. Add regression tests asserting that key
output metrics (chi2/ndf, T, U, n per bin) are reproducible across runs.
Cross-validate outputs of boson_paper_analysis.py against reference values in
research/robert/evidence-ledger.md. Flag any deviation exceeding defined tolerances.
Run physics/src/tsallis_physics_validation.py to verify Tsallis distribution parameters
(T, q, n) converge within expected physical bounds. Log any fit failures or chi²/ndf anomalies.
Run physics/src/sympy_validation_agent.py to confirm symbolic derivations match
numerical outputs from fitting_pipeline.py within floating-point tolerance.
Save all run artifacts (chi2/ndf, covariance, parameter correlations, residuals, plots)
to research/robert/runs/YYYY-MM-DD-fitting-pipeline-validation/.
Do not promote any parameter to physical interpretation until chi2/ndf, covariance,
correlations, residuals, fit-range sensitivity, and baseline comparisons are all recorded
in evidence-ledger.md.
```

---

## ✅ Completed

| Item | Completed | Notes |
|---|---|---|
| Verify Cooper-Frye static-limit recovery is cited | 2026-04-30 | Implicitly recovered, not explicitly named in text. Ledger updated. |
| Resolve χ²/ndf absence in manuscript | 2026-04-30 | Found in Fig 7-9 legends; updated draft to request inclusion in Table 1. |
| Move manuscript PDF to canonical location | 2026-04-30 | Moved to `research/robert/manuscript/` |
| Symbolic validation of core distribution §1–§5 | 2026-04-26 | `boson_paper_analysis.py` all sections green |
| U parameterization verified | 2026-04-26 | `v < c`, `γv = U`, `Y = arcsinh(U)` confirmed |
| η integration proved | 2026-04-26 | `U^μp_μ = pT·cosh(η−Y)` via SymPy |
| Tsallis/Blast-Wave baseline scripts written | 2026-04-27 | `tsallis_physics_validation.py` ready; awaiting data |
| Execute Tsallis physics validation run | 2026-05-04 | Captured in `research/robert/runs/2026-05-04-tsallis-validation/`. Comparison against Khuntia (2019) and Rath (2020) suggests model refinement needed. |
| Fitting pipeline infrastructure built | 2026-04-27 | `fitting_pipeline.py` ready; awaiting `fit_input.csv` |
| chi2/ndf, covariance, AIC/BIC, residuals, pulls implemented | 2026-04-27 | All computed in `fitting_pipeline.py` `fit_one_spec()` and written to `fit_quality.csv` / `parameter_correlations.csv`; **blocked on `fit_input.csv`**, not on implementation |
