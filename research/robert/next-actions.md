# Robert — Science Next Actions

This is the canonical task queue for Robert's physics workflow.
Platform-blocked items (waiting on Ollama, Scite key, etc.) are noted separately; their resolution is tracked in GitHub Issues.

Science tasks become active only after acceptance by Robert. Do not add, remove, or reword items without Robert's approval.

Evidence states referenced here are defined in `docs/decisions/2026-04-26-science-evidence-standards.md`.

---

## 🟢 Active — Robert's Decision Required





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




## 🤖 Agent-Proposed
### Manuscript Consistency Audit
1. **Extreme Fit-Range Sensitivity (W-05)**
   - ~~**Draft Claim**: "When excluding the low-pT region (pT < 0.45 GeV), T_kin drifts by up to 43 MeV in certain bins (>7σ deviation). Document this extreme sensitivity..."~~
   - ~~**Ledger Status**: The ledger claim...~~
   - **Resolved**: The evidence ledger has been updated to reflect the 2026-06-20 >7σ fit-range sensitivity findings. The draft claim is now consistent with the evidence ledger.

2. **Pion-Mass Assumption Bias (W-07)**
   - **Draft Claim**: "The authors must either fit strictly identified spectra (π, K, p) simultaneously, or explicitly document the estimated thermodynamic bias..."
   - **Ledger Status**: `Sanity check (level-2 only)`.
   - **Violation**: The draft relies on a claim that has not reached `Supported` status. It is currently only a `Sanity check`.
   - **Next Action**: Revise manuscript draft to downgrade the "Pion-Mass Assumption Bias" claim to a hypothesis or warning until the level-1 identified-species refit is complete and the claim reaches `Supported`.


### [A-01] Computational Rescue Strategy: Symbolic Regression for Kinematic Boundaries
**Context:** Robert's exact Jüttner derivation fails at high-$p_T$. Recent work by Bendavid et al. (arXiv:2508.00989v3) demonstrates using Symbolic Regression (e.g., PySR) to derive compact analytical expressions for complex kinematic observables in HEP.
**Action:** Use Symbolic Regression to map the boundary between the validity of the Jüttner derivation and the onset of non-extensive QCD scattering (the heavy tails). Let the symbolic regressor find the minimal analytical correction term required to bridge the exact classical kinematics with the Tsallis tails.

### [A-02] Computational Rescue Strategy: Bayesian Inference for Model-to-Data Quantification
**Context:** The pipeline shows severe $\chi^2/\text{ndf}$ for classical models. Lu et al. (arXiv:2407.09207v3) recently used Bayesian inference to quantify the low-$p_T$ pion excess against hydrodynamic frameworks.
**Action:** Implement a Bayesian parameter estimation pipeline to systematically quantify the model-to-data differences in the high-$p_T$ tail. Instead of rejecting the Jüttner derivation entirely, use Bayesian inference to formally constrain its region of applicability and extract the posterior probability of the exact analytical integration's validity.

- [ ] **D-02 (Docs):** The project lacks a central glossary for parameter notation (e.g., T_stat vs T_kin, U vs β_s). Execute `aisci-living-docs` skill to create a `docs/decisions/notation-glossary.md` and link it from `workflow.md`.


### [A-04] Literature Cross-Check: Femtoscopy HBT Source Size vs Thermal Fit Parameters
**Status:** AGENT-PROPOSED — requires Robert's approval to activate.
**Source:** Perplexity academic + GitHub analysis, 2026-07-11.
**Context:** arXiv:2607.04351 ("Quantum interference effects enhanced in π+p femtoscopic
correlation functions") is already indexed in evidence-ledger.md agent-proposed intake.
HBT femtoscopy measures the space-time extent of the pion-emitting source — the same
source whose momentum distribution is being fitted. If T_kin and flow β extracted from
pT spectra are physically meaningful, they should be consistent with the source size
R_HBT via: R_HBT ~ ℏ/(T_kin × cosh(y)) × f(β). A tension between spectral T_kin and
HBT-inferred T_kin would be strong evidence that the spectral fit is absorbing
non-thermal contributions.
**Action:**
1. Retrieve HBT radii R_out, R_side, R_long from arXiv:2607.04351 for pp 13 TeV.
2. Map them to multiplicity classes matching ins1735345.
3. Compare against the T_kin values in research/robert/runs/2026-07-08-bgbw-per-class/.
4. Record agreement or tension in evidence-ledger.md as a new claim row.
**Target file for results:** research/robert/evidence-ledger.md (new claim row).
**Acceptance:** Comparison table (R_HBT-implied T_kin vs spectral T_kin per bin) added
to evidence-ledger.md with a status of Supported or Tension as appropriate.



## ✅ Completed

| Item | Completed | Notes |
|---|---|---|
| [A-02] `bose_2c` implementation missing | 2026-07-12 | Registered `bose_2c` in `engine.py` and added to defaults in `cli.py`. |
| [D-01] Investigate Jüttner 3-component singularity | 2026-07-12 | Analysed singularity at U -> 0 using sympy; proposed a Two-Component Soft/Hard Model baseline in `runs/2026-07-12-d01-juttner-singularity-analysis/README.md`. |
| [D-03] Wire `fitting_pipeline.py` to accept `--input` | 2026-07-12 | Modified script to accept `--input` defaulting to `ins1735345` data file. |
| [O-10] Dashboard Data Sync & UI Audit | 2026-07-10 | Ran headless Playwright audit to ensure UI syncs perfectly with file system. Fixed bug where `api.py` was limiting the runs dropdown to 5 runs instead of all 34. Verified DB has no missing or incomplete physics runs. |
| [O-04] Resolve T-beta degeneracy in BGBW fits | 2026-07-08 | Profile scan CSVs and contour plot generated. |
| [O-06] Investigate Tsallis 2c physical interpretation | 2026-07-08 | Tsallis 2c parameter stability checked, Cleymans-Worku ranges validated. |
| [O-09] Issue #27 — C3: Run GLS covariance-aware BGBW fit | 2026-07-08 | GLS covariance envelope calculated, confirming poor BGBW fit is not an artifact. |
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
| [B-01] Supply per-multiplicity-bin pT spectrum table | 2026-06-14 | Data provided in `libs/physics-core/data/fit_input_ins1735345.csv` and copied to `libs/physics-core/data/fit_input.csv`. |

---

## 🔴 Key Findings Requiring Robert's Attention (2026-06-20)

| Item | Finding | Severity |
|------|---------|----------|
| T–β degeneracy | 4/9 BGBW bins \|ρ\| > 0.95 — parameters NOT independently interpretable | **Critical** |
| Fit-range dependence | 9/10 BGBW bins shift T by 15–44 MeV when pT < 0.5 GeV is excluded | **Critical** |
| Jacobian missing | dy/dη = 0.782 at pT = 0.175 GeV (22% correction) — not in manuscript | **High** |
| Tsallis 2c wins | ΔAIC(MJ vs TS2c) > 2700 everywhere — needs physical interpretation decision | **High** |
| BE denominator absent | Manuscript uses pure Boltzmann despite title saying "bosons" — needs explicit statement | **Medium** |
