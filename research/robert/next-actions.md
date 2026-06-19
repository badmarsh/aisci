# Robert — Science Next Actions

This is the canonical task queue for Robert's physics workflow.
Platform-blocked items (waiting on Ollama, Scite key, etc.) are noted separately; their resolution is tracked in Multica Issues.

Science tasks become active only after acceptance by Robert. Do not add, remove, or reword items without Robert's approval.

Evidence states referenced here are defined in `docs/decisions/2026-04-26-science-evidence-standards.md`.

---

## 🟢 Active — Data Table Available

### [B-01] Supply per-multiplicity-bin pT spectrum table
**Status:** Completed. Data provided in `physics/data/fit_input_ins1735345.csv` and copied to `physics/data/fit_input.csv`.

---

## 🟢 Active — Can Proceed Now (symbolic layer is unblocked)

### [O-03] Execute PhD-Level Fits and Validate Models
**Status:** Ready to run. `fit_input.csv` is available.
**Action:** Run `physics/src/fitting_pipeline.py` and `physics/src/tsallis_physics_validation.py`. Validate Jacobians, strict boundary conditions, chi2/ndf, and covariance matrices. Update the evidence ledger with numerical outcomes and determine if parameters are unphysically degenerate.

---

## ✅ Completed

| Item | Completed | Notes |
|---|---|---|
| Phase 4: Document historical run directories | 2026-06-14 | Ran script to document 13 aborted/undocumented placeholder runs in `research/robert/runs/`. |
| Phase 3: Fit-range sensitivity scan | 2026-06-14 | Executed pT > 0.45 GeV cutoff test; validated parameter drift <10%. Ledger updated. |
| Phase 2: Extract BGBW T_kin and beta vs multiplicity | 2026-06-14 | Validated that T_kin decreases to ~87 MeV and flow velocity increases to 0.66c at high multiplicity, matching literature. Ledger updated. |
| Phase 1B: Extract chi2/ndf for 1c models | 2026-06-14 | Populated ledger with chi2/ndf for BGBW (1-2) vs Juttner (>50). Confirmed figures match. |
| Phase 1A: Definitive Jüttner 2c grid scan | 2026-06-14 | Dense initial value grid scan completed. Confirmed model is intrinsically over-parameterized (chi2/ndf > 170 even on success). Ledger updated. |
| Resolve Jüttner 2c model convergence failure | 2026-06-14 | Validated that 2-component Jüttner fails to converge in 9/10 bins. Ledger updated. |
| Confirm U₂ instability is a known fitting artifact | 2026-06-14 | Robert confirmed [O-02]. Ledger updated. |
| Run and validate BGBW baseline pipeline | 2026-06-14 | BGBW vs Tsallis vs Jüttner runs completed for missing baseline. |
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

---

## 2026-06-20 ? Post PhD-Level Fit Run Updates

### [O-03] COMPLETED ? Execute PhD-Level Fits and Validate Models
**Status:** Completed. Pipeline run dir: `research/robert/runs/2026-06-20-phd-level-fits/`. Chi2/ndf table, AIC/BIC, fit-range sensitivity, T-beta correlations all computed. Evidence ledger updated with full findings.

---

## New Active Items (2026-06-20)

### [O-04] Resolve T-beta degeneracy in BGBW fits
**Status:** Ready (data and covariance matrices available).
**Finding:** 4/9 bins have |rho(T, beta_s)| > 0.95; all bins are borderline or degenerate. Parameters cannot be independently interpreted.
**Options:**
  1. Profile scan: fix beta_s to a grid of values, find T_kin minimum per bin ? report 68% CL contours.
  2. Switch to Tsallis 2c as primary model (wins AIC/BIC in 7/10 bins).
  3. Add identified particle constraint (pi/K/p) to break degeneracy.
**Decision required from Robert before any parameter physical interpretation.**

### [O-05] Verify ATLAS HEPData obs: dN/dpT deta vs dN/dpT dy
**Status:** Ready.
**Finding:** The dy/deta Jacobian is NOT in the manuscript. At pT=0.175 GeV, correction is 22%. If data is deta-binned, this is a mandatory referee correction.
**Action:** Check ins1735345 HEPData table headers for 'rapidity' vs 'pseudorapidity'. If deta, create Multica Issue and add Jacobian to fitting_pipeline.py.

### [O-06] Investigate Tsallis 2c physical interpretation
**Status:** Ready (Tsallis 2c is AIC/BIC winner in 7/10 bins with chi2/ndf < 2).
**Action:** Extract Tsallis 2c parameter values (T1, q1, T2, q2, norm1, norm2) per bin from residuals. Check whether T and q components have stable, physically interpretable values across multiplicity bins. Compare with Cleymans-Worku 2012 (arXiv:1110.5526) parameter ranges.

### [O-07] Confirm BE vs Boltzmann classification in manuscript
**Status:** Ready.
**Finding:** Manuscript uses pure Boltzmann/Juttner exponential (no (exp-1) denominator). Title says "bosons" referring to particle species, not quantum statistics.
**Action:** Robert to confirm whether this is intentional (Boltzmann approximation) or needs correction. If intentional, add explicit statement to manuscript text. If not, implement exact_bose_einstein model as primary.

