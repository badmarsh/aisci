# Fit Plan

## Data Acquisition

**Status:** Blocked — awaiting option (a) or (b)

**Resolution Options:**
a) Robert provides private per-bin pT tables.
b) Identify the correct HEPData record or ATLAS open-data release with the correct multiplicity-bin qualifier.
c) Use manuscript Table 1 parameters to generate synthetic spectra for cross-check only (not for primary fitting).

## Inputs Needed

- Full pT data table for all multiplicity bins.
- Measurement uncertainties.
- Bin definitions and fit ranges.
- Exact model equations and parameter constraints.
- Published initial guesses or fitted parameters, if available.
- Normalization convention for each spectrum.
- Collision system, event selection, particle definition, and acceptance cuts.

## Data Acquisition

The fitting pipeline is currently blocked before fit (`fit_run_status.json` reports `pipeline_status = "blocked_before_fit"`) because `ins1419652` only provides inclusive pT spectra with `N(P=3) >= 1`, not spectra conditioned on the manuscript multiplicity intervals. Resolving this requires one of the following:

1. **Primary path (preferred):** Robert provides per-bin pT tables (yields and total uncertainties) for the manuscript multiplicity bins `21-30`, `31-40`, `41-50`, `51-60`, `61-70`, `71-80`, `81-90`, `91-100`, `101-125`, and `126-150` in a fit-ready format.
2. **Alternate path:** Identify an open-data or HEPData record (ATLAS, CMS, ALICE, or ATLAS open data) that contains pT spectra conditioned on the same multiplicity intervals and acceptance as the manuscript.
3. **Synthetic cross-check (not primary evidence):** Use the manuscript's published fit parameters (e.g., Table 1) to generate synthetic spectra for each multiplicity bin for limited cross-checks only. These spectra can be used to validate the fitting machinery and baseline comparisons but must not replace real data in the primary evidence chain.

Until path (1) or (2) is satisfied, no manuscript-bin fits should be treated as physical evidence.

## Fitting Stance

Do not treat fit convergence as physical evidence by itself. A parameter trend is interpretable only if the fit quality, covariance, correlations, and sensitivity to fit range and initial values are acceptable.

## Physics Constraints & Model Handling

1. **Track Acceptance Formulas Separately:** Do not use one monolithic "fit function." Maintain distinct formula families for the $\eta$ cut, the $\eta$-interval cut, the $p_T$ cut, and the combined $p_T+\eta$ cut as derived in the manuscript.
2. **Region-Dependent $p_T$ Gates:** Do not use a single global minimum $p_T$ fit limit. Store fit ranges as metadata per figure/region based on manuscript Figure 5 (e.g., 600 MeV minimum feasibility limit for a 100 MeV $p_T$ cut in forward/general regions; using 120–3500 MeV or 120–5000 MeV ranges depending on the specific multiplicity interval and pseudorapidity region).
3. **Three-Component Baseline:** The manuscript frames the model as two moving systems and one static system (three temperatures). Treat this three-component interpretation as the primary baseline to stress-test, rather than pre-judging it as pathological.
4. **Exponential Form:** Treat the visible working form as an exponential moving-system model (Jüttner/Boltzmann approximation). Do not assume full Bose-Einstein unless the final manuscript equation provides the explicit denominator.

## Pipeline

1. Load data into a canonical table.
2. Implement manuscript model variants as pure Python functions, strictly separating the $\eta$-cut, $p_T$-cut, and combined acceptance formula families.
3. Implement literature-matched Tsallis/Tsallis-Pareto and Blast-Wave baselines.
4. Fit each bin with `iminuit` or equivalent robust optimizer, applying the region-specific low-$p_T$ gates mapped from the manuscript.
5. Compute chi2, ndf, chi2/ndf, covariance, parameter correlations, and Minuit status.
6. Scan initial values and parameter bounds to detect local minima and unconstrained directions.
7. Stress-test the three-component baseline (two moving systems + one static system) against one- and two-component variants using residuals and information criteria.
8. Plot fitted curves, residuals, and pulls.
9. Plot parameter trends versus multiplicity only after fit quality gates pass.
10. Compare baseline and manuscript models in a single table.

## Outputs

- `fit_input.csv`
- `fit_parameters.csv`
- `fit_quality.csv`
- `parameter_correlations.csv`
- `model_comparison.csv`
- residual plots per bin
- pull plots per bin
- U versus multiplicity plot
- temperature versus multiplicity plot
- short interpretation note
