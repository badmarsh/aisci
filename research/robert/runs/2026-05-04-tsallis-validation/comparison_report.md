# Science Baseline Validation Report
# Date: 2026-05-04
# Run: 2026-05-04-tsallis-validation

## 1. Run Summary
- **Script**: `libs/physics-core/src/tsallis_physics_validation.py`
- **Method**: Synthetic data generation followed by Tsallis-like distribution fitting.
- **Data**: Synthetic ATLAS-like spectra (13 TeV proxy).

## 2. Fitting Results (Demonstration)
| Parameter | True Value | Fitted Value | Error |
|-----------|------------|--------------|-------|
| T (GeV)   | 0.160      | 0.076        | 0.133 |
| beta_T    | 0.600      | 0.457        | 0.720 |
| q         | 1.150      | 2.656        | 2.619 |

**Observation**: The fitting procedure failed to accurately recover the true parameters from synthetic data with 10% noise. The `q` parameter is significantly overestimated, and `T` is underestimated. This suggests a potential degeneracy in the simplified Tsallis-like model or instability in the `curve_fit` routine for this parameter space.

## 3. Comparison with Literature (BGBW)
Based on Khuntia et al. (2019) and Rath et al. (2020):

| Source | System | T_kin (GeV) | beta_avg | Notes |
|--------|--------|-------------|----------|-------|
| Khuntia 2019 | pp 7 TeV | ~0.160 | ~0.3 - 0.5 | beta almost independent of multiplicity |
| Rath 2020 | pp 13 TeV | ~0.150 - 0.170 | ~0.4 | T_kin significantly multiplicity dependent |
| **Current Run** | Synthetic | 0.076 | 0.457 | High uncertainty, fit failed to converge on truth |

**Analysis**:
- Our "fitted" temperature (0.076 GeV) is significantly lower than the literature values (~0.160 GeV).
- Our "fitted" flow velocity (0.457) is within the literature range, but the uncertainty is extremely high (0.720).
- The discrepancy in `T` and `q` confirms that the current validation script requires further refinement of the model function and initial guess logic to match thermodynamically consistent Tsallis baselines used in the papers.

## 4. Next Actions
- [ ] Implement the exact "thermodynamically consistent" Tsallis distribution from Khuntia 2019.
- [ ] Obtain the missing pT spectra for multiplicity bins 21-150 to unblock the real fitting pipeline.
- [ ] Review the `q` parameter bounds and initial guesses in `tsallis_physics_validation.py`.
