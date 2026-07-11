# Robert — Science Next Actions

This is the canonical task queue for Robert's physics workflow.
Platform-blocked items (waiting on Ollama, Scite key, etc.) are noted separately; their resolution is tracked in Multica Issues.

Science tasks become active only after acceptance by Robert. Do not add, remove, or reword items without Robert's approval.

Evidence states referenced here are defined in `docs/decisions/2026-04-26-science-evidence-standards.md`.

---

## 🟢 Active — Robert's Decision Required


### [O-12] Merge `pr28` (BGBW per-class fits)
**Status:** ACTIVE — Ready for merge.
**Context:** The `pr28` branch contains the structural updates to `physics/src/` to support BGBW per-class fits (Issue #27) and locks the dependencies via `uv.lock`.
**Actions (Robert or ALICE collaboration):**
1. Merge `pr28` into `main` (`git merge pr28`).
2. Verify tests pass.



### [O-11] Deprecate 3-Component Jüttner & Execute 2-Component Exact Bose-Einstein Fits
**Status:** ACTIVE — Pipeline is scaffolded and ready.
**Context:** We mathematically proved that the 3-component model is degenerate at low radial velocities (Fisher Information rank deficiency) and that the Boltzmann approximation underestimates high-T yield by 84%.
**Actions (Robert or ALICE collaboration):**
1. Run the `fitting_pipeline.py` using ONLY the 2-component exact Bose-Einstein model (`component_counts = (1, 2)`).
2. Validate that the 2-component Bose-Einstein fit removes the infinite uncertainties seen in the 3c Jüttner model.
3. Update the manuscript text to declare the usage of the exact Bose-Einstein denominator.
**Acceptance:** `fitting_pipeline.py` run completes cleanly for 2c exact Bose-Einstein and yields finite parameter uncertainties.

---

### [O-08] Issue #27 — C1: Obtain cross-estimator dataset and response matrix
**Status:** ACTIVE — V0M estimator datasets located (arXiv:2310.10236, arXiv:2603.13203).
**Context:** ins1735345 uses SPD-tracklets (|η| < 0.8) estimator. The manuscript uses a different Nch definition. The T_kin rising trend (partially an estimator artifact) cannot be de-coupled from physics without a cross-estimator comparison.
**Scaffold done:**
- `physics/src/nch_response_matrix.py` — identity placeholder + Moore–Penrose unfolder.
- `research/robert/runs/2026-07-08-bgbw-estimator-crosscheck/README.md` — unblock path documented.
- `evidence-ledger.md` — Agent documented the INSPIRE-HEP DOIs/arXivs containing the ALICE V0M datasets.
**Actions (Robert or ALICE collaboration):**
1. Pull the HEPData records for `ins2711421` (arXiv:2310.10236) to construct the true V0M response matrix.
2. Generate response matrix R (ALICE MC: PYTHIA8 + GEANT4 → SPD tracklets vs Nch).
3. Save R to `physics/data/response_matrix/R_spd_to_nch.npy`.
4. Run: `python physics/src/bgbw_fit.py --run-dir research/robert/runs/YYYY-MM-DD-bgbw-estimator-crosscheck --data-path <v0m_csv>`
5. Populate delta table in `evidence-ledger.md`.
**Acceptance:** delta table T_kin, ⟨β⟩ per bin for SPD-tracklets vs second estimator recorded.

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



### [O-07] Confirm BE vs Boltzmann classification in manuscript
**Status:** RESOLVED — Agent proved catastrophic failure of Boltzmann approximation.
**Finding:** SymPy exact fractional error analysis shows `(Boltz - BE)/BE = -exp(-E/T)`. At low pT (~100 MeV) for the high-multiplicity thermal component (kT3 ~ 1000 MeV), the Boltzmann approximation causes an 84.2% underestimation of the yield. 
**Action:** The manuscript MUST transition to the exact Bose-Einstein model `(exp(...)-1)⁻¹`. The text stating "Boson probability function" is physically false if integrated as a Boltzmann distribution at these temperatures.
**Note:** exact_bose_einstein fits are already scaffolded in `fitting_pipeline.py`. Robert must run them.

---

## 🤖 Agent-Proposed

### [A-01] Computational Rescue Strategy: Symbolic Regression for Kinematic Boundaries
**Context:** Robert's exact Jüttner derivation fails at high-$p_T$. Recent work by Bendavid et al. (arXiv:2508.00989v3) demonstrates using Symbolic Regression (e.g., PySR) to derive compact analytical expressions for complex kinematic observables in HEP.
**Action:** Use Symbolic Regression to map the boundary between the validity of the Jüttner derivation and the onset of non-extensive QCD scattering (the heavy tails). Let the symbolic regressor find the minimal analytical correction term required to bridge the exact classical kinematics with the Tsallis tails.

### [A-02] Computational Rescue Strategy: Bayesian Inference for Model-to-Data Quantification
**Context:** The pipeline shows severe $\chi^2/\text{ndf}$ for classical models. Lu et al. (arXiv:2407.09207v3) recently used Bayesian inference to quantify the low-$p_T$ pion excess against hydrodynamic frameworks.
**Action:** Implement a Bayesian parameter estimation pipeline to systematically quantify the model-to-data differences in the high-$p_T$ tail. Instead of rejecting the Jüttner derivation entirely, use Bayesian inference to formally constrain its region of applicability and extract the posterior probability of the exact analytical integration's validity.

- [ ] **D-01 (Analysis):** The Fisher Information matrix shows the 3-component Jüttner parameterization (T_stat, T_kin, β_s) is mathematically singular at U → 0, meaning it cannot be fitted with physical meaning. Execute `fit-anomaly-resolution` skill to recommend a non-singular baseline (e.g., exact Bose-Einstein 2-component) and document the mathematical proof for Robert.
- [ ] **D-02 (Docs):** The project lacks a central glossary for parameter notation (e.g., T_stat vs T_kin, U vs β_s). Execute `aisci-living-docs` skill to create a `docs/decisions/notation-glossary.md` and link it from `workflow.md`.
- [ ] **D-03 (Data):** The `ins1735345` data file is loaded but the pipeline script `fitting_pipeline.py` currently hardcodes paths to earlier test tables. Modify the script to accept an `--input` argument, defaulting to the new `ins1735345` file, ensuring the upcoming fits actually use the unblocked data.

### [A-03] Theoretical Derivation: Exact Analytical Integration of Moving Tsallis Source over η
**Status:** AGENT-PROPOSED — requires Robert's approval to activate.
**Source:** Perplexity academic + GitHub analysis, 2026-07-11.
**Context:** Evidence-ledger entry (2026-07-10, "Exact analytical integration of a moving
Tsallis source over pseudorapidity") confirms that no exact closed-form analytical
integration of a moving Tsallis source over pseudorapidity (with proper dy/dη Jacobian
and collective flow U) exists in the literature. The closest work is Lao et al.
(arXiv:1611.08391v4) which only derives a first-order Taylor expansion in (q-1).
This is a genuine theoretical gap that could form the core novelty of a revised manuscript.
**Proposed approach:**
1. Use SymPy (already in physics/.venv) to attempt a full symbolic integration of:
   (d²N/dp_T dη) = ∫ f_Tsallis(p_T, η, U, T, q) × (dy/dη) dη
   over the ALICE acceptance |η| < 0.8, with the exact dy/dη = p/(m_T cosh η) Jacobian.
2. If closed-form is not achievable, construct a Padé approximant [M/N] rational function
   to the integrand. Padé approximants converge outside the Taylor radius and are more
   accurate than truncated series for transcendental functions.
3. As an alternative, apply Symbolic Regression via PySR (arXiv:2508.00989v3, Bendavid
   et al., already referenced as [A-01]) to find the minimal compact analytical correction.
4. If an exact or high-order approximation is found, this becomes the manuscript's primary
   theoretical contribution, superseding the Boltzmann/Jüttner derivation.
**Target file for results:** research/robert/runs/YYYY-MM-DD-tsallis-exact-eta-integration/
**Acceptance:** SymPy derivation script produces a closed-form or Padé expression validated
against numerical quadrature to < 0.1% across pT ∈ [0.15, 3.0] GeV, η ∈ [-0.8, 0.8].

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

### [A-05] Bayesian MCMC Posterior for T_kin–β_s Joint Contours
**Status:** AGENT-PROPOSED — requires Robert's approval to activate.
**Source:** Perplexity academic + GitHub analysis, 2026-07-11.
**Context:** Task 9 (evidence-ledger.md, 2026-06-20) confirmed T–β correlations |ρ| up
to −0.999 in BGBW fits. The Minuit covariance matrix gives the χ² curvature at the
minimum but does not capture the non-Gaussian shape of the joint posterior, which is
what a referee will demand when |ρ| > 0.95. The file physics/src/bgbw_jax_autodiff.py
(5.7 KB, currently orphaned per platform-backlog.md) provides exact JAX gradients
suitable for a NUTS/HMC sampler.
**Proposed approach:**
1. Wire physics/src/bgbw_jax_autodiff.py into a NumPyro or BlackJAX HMC sampler.
2. Run NUTS posterior sampling for each of the 10 multiplicity bins with 2000 warmup +
   2000 draw steps.
3. Plot 2D (T_kin, β_s) posterior contours at 68% and 95% credible intervals.
4. Report marginal posteriors and compare their widths to the Minuit diagonal errors to
   quantify the underestimation from covariance-diagonal reporting.
5. These corner plots become the publishable replacement for the degenerate parameter table.
**Target file:** research/robert/runs/YYYY-MM-DD-bgbw-mcmc-posteriors/
**Acceptance:** Corner plots for all 10 bins stored in the run dir with R-hat < 1.01 for
all chains, and a summary claim row added to evidence-ledger.md.

---

## ✅ Completed

| Item | Completed | Notes |
|---|---|---|
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
