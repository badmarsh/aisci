# Robert — Science Next Actions

This is the canonical task queue for Robert's physics workflow.
Platform-blocked items (waiting on Ollama, Scite key, etc.) are noted separately; their resolution is tracked in Multica Issues.

Science tasks become active only after acceptance by Robert. Do not add, remove, or reword items without Robert's approval.

Evidence states referenced here are defined in `docs/decisions/2026-04-26-science-evidence-standards.md`.

---

## 🟢 Active — Robert's Decision Required

### [O-04] Resolve T–β degeneracy in BGBW fits
**Status:** Active. Data and covariance matrices available in `research/robert/runs/2026-06-20-phd-level-fits/covariance/`.
**Finding:** All 9 BGBW bins show |ρ(T, β_s)| ∈ [0.93, 0.999]. 4/9 bins are DEGENERATE (|ρ| > 0.95). In no bin are T_kin and β_s statistically independent. Parameters cannot be reported or interpreted separately without addressing this.
**Options (Robert selects one before physical interpretation):**
  1. Profile scan: fix β_s to a grid of values, find T_kin minimum per bin — report 68% CL contours instead of single point estimates.
  2. Switch to Tsallis 2c as primary model (wins AIC/BIC in 7/10 bins, chi²/ndf < 2 in 7/10 bins).
  3. Add identified particle constraint (π/K/p separate spectra) to break degeneracy.
**Decision required from Robert before any parameter physical interpretation.**

---

### [O-05] ✅ Verify ALICE/ATLAS HEPData observable: dN/dpT dη vs dN/dpT dy
**Status:** CONFIRMED. dy/dη Jacobian is required.
**Finding:** 
- HEPData ins1735345 is from ALICE arXiv:1905.07208, |η| < 0.8.
- ALICE measures `(1/2π pT) d²N_ch/(dpT dη)` — pseudorapidity, not rapidity.
- The dy/dη Jacobian is absent from the manuscript.
- At pT = 0.175 GeV: `dy/dη = 0.782` → **22% correction** (mandatory).
- At pT = 1.0 GeV: `dy/dη ≈ 0.985` → <2% (negligible).
**Next action:** Create Multica Issue for adding Jacobian to manuscript and pipeline (pending Robert's approval).

---

### [O-06] Investigate Tsallis 2c physical interpretation
**Status:** Active. Tsallis 2c wins AIC/BIC in 7/10 bins with chi²/ndf < 2.
**Finding:** Tsallis 2c is the statistical winner but physical interpretation requires parameter stability across multiplicity bins and comparison with Cleymans–Worku 2012 (arXiv:1110.5526) ranges.
**Action:**
  1. Extract Tsallis 2c parameter values (T₁, q₁, T₂, q₂, norm₁, norm₂) per bin from `fit_parameters.csv`.
  2. Check whether T and q components have physically stable, monotonic trends across multiplicity bins.
  3. Compare with Cleymans–Worku 2012 parameter ranges (T ~ 0.09–0.10 GeV, q ~ 1.1–1.15 in pp collisions).
  4. Inspect covariance matrices for T–q correlations — Tsallis T and q are known to be anti-correlated.
**Output:** Update evidence ledger with physical interpretation summary.

---

### [O-07] Confirm BE vs Boltzmann classification in manuscript
**Status:** Active. Robert's confirmation required.
**Finding:** Manuscript uses pure Boltzmann/Jüttner exponential `f(p) ~ exp(-β U·p)`. No Bose-Einstein denominator `(exp(...)-1)⁻¹` is present. The word "bosons" in the title refers to the particle species (pions), not quantum statistics.
**Action:** Robert to confirm:
  - Is this a deliberate Boltzmann approximation? If yes, add an explicit statement to the manuscript justifying the approximation (e.g., "BE effects are negligible at T >> m_pion, approximation valid to < X%").
  - If not deliberate, implement exact_bose_einstein as primary model (BE denominator is already coded in `fitting_pipeline.py`).
**Note:** exact_bose_einstein fits show chi²/ndf 10–50% better than manuscript_juttner but still 50–100× worse than Tsallis 2c. Adding the denominator alone does not resolve the fit quality issue.

---

## ✅ Completed

| Item | Completed | Notes |
|---|---|---|
| [O-03] Execute PhD-Level Fits and Validate Models | 2026-06-20 | Run dir: `research/robert/runs/2026-06-20-phd-level-fits/`. All 10 multiplicity bins × 5 models. Chi²/ndf table, AIC/BIC, fit-range sensitivity, T-β correlations computed. Evidence ledger updated. |
| Phase 4: Document historical run directories | 2026-06-14 | Ran script to document 13 aborted/undocumented placeholder runs in `research/robert/runs/`. |
| Phase 3: Fit-range sensitivity scan | 2026-06-14 | Executed pT > 0.45 GeV cutoff test; validated parameter drift < 10%. Ledger updated. |
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
| chi2/ndf, covariance, AIC/BIC, residuals, pulls implemented | 2026-04-27 | All computed in `fitting_pipeline.py` `fit_one_spec()` and written to `fit_quality.csv` / `parameter_correlations.csv`. |
| [B-01] Supply per-multiplicity-bin pT spectrum table | 2026-06-14 | Data provided in `physics/data/fit_input_ins1735345.csv` and copied to `physics/data/fit_input.csv`. |

---

## 🔴 Key Findings Requiring Robert's Attention (2026-06-20)

| Item | Finding | Severity |
|------|---------|----------|
| T–β degeneracy | 4/9 BGBW bins \|ρ\| > 0.95 — parameters NOT independently interpretable | **Critical** |
| Fit-range dependence | 9/10 BGBW bins shift T by 15–44 MeV when pT < 0.5 GeV is excluded | **Critical** |
| Jacobian missing | dy/dη = 0.782 at pT = 0.175 GeV (22% correction) — not in manuscript | **High** |
| Tsallis 2c wins | ΔAIC(MJ vs TS2c) > 2700 everywhere — needs physical interpretation decision | **High** |
| BE denominator absent | Manuscript uses pure Boltzmann despite title saying "bosons" — needs explicit statement | **Medium** |
