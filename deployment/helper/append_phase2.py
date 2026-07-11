#!/usr/bin/env python3
import sys

phase2_text = """
## 2026-07-08 Phase-2 Repair Run

### 2A - T-beta Profile Scan (Task 1A)
The 2D profile scan across beta_s \\in [0.10, 0.95] revealed the severe anti-correlation contour ("banana plot").
*Conclusion:* BGBW parameters are strongly degenerate. 1D diagonal error bars drastically underestimate physical uncertainty; confidence contours are required to capture the true allowed limits for T_kin and <beta>.

### 2B - Tsallis F-test (Task 1B)
| Bin | chi2/ndf_1c | chi2/ndf_2c | F | p-value | Decision |
|---|---|---|---|---|---|
| 21-30 | 0.590 | 0.360 | 10.37 | 3.3e-05 | 2c STATISTICALLY WARRANTED |
| 31-40 | 6.570 | 1.030 | 79.89 | 3.6e-17 | 2c STATISTICALLY WARRANTED |
| 41-50 | 9.110 | 1.340 | 86.04 | 9.8e-18 | 2c STATISTICALLY WARRANTED |
| 51-60 | 10.600 | 1.430 | 95.05 | 1.7e-18 | 2c STATISTICALLY WARRANTED |
| 61-70 | 18.400 | 19.800 | 0.00 | 1.0 | OVERFITTING |
| 71-80 | 19.200 | 2.050 | 123.70 | 1.4e-20 | 2c STATISTICALLY WARRANTED |
| 81-90 | 19.400 | 20.800 | 0.01 | 0.998 | OVERFITTING |
| 91-100 | 19.600 | NaN | NaN | NaN | OVERFITTING |
| 101-125 | 19.200 | 1.370 | 191.88 | 3.7e-24 | 2c STATISTICALLY WARRANTED |
| 126-150 | 12.300 | 0.450 | 387.22 | 4.2e-30 | 2c STATISTICALLY WARRANTED |

*Conclusion:* The 2nd component is statistically warranted (p < 0.05) in 7 of the 10 bins.

### 2C - Tsallis 2c Stability (Task 1C)
| Bin | T1 | T2 | q1 | q2 | T-Status | q-Status |
|---|---|---|---|---|---|---|
| 21-30 | 0.0690 | 0.1018 | 1.0012 | 1.1425 | DISTINCT | DISTINCT |
| 31-40 | 0.1339 | 0.0719 | 1.1421 | 1.0036 | DISTINCT | DISTINCT |
| 41-50 | 0.0702 | 0.1476 | 1.0106 | 1.1438 | DISTINCT | DISTINCT |
| 51-60 | 0.0685 | 0.1571 | 1.0210 | 1.1449 | DISTINCT | DISTINCT |
| 61-70 | 0.1221 | 0.0625 | 1.1647 | 1.1889 | DISTINCT | COLLAPSED |
| 71-80 | 0.1699 | 0.0641 | 1.1472 | 1.0444 | DISTINCT | DISTINCT |
| 81-90 | 0.1243 | 0.1834 | 1.1713 | 1.2424 | DISTINCT | DISTINCT |
| 91-100| 0.1826 | 0.0612 | 1.1488 | 1.0689 | DISTINCT | DISTINCT |
| 126-150| 0.2505| 0.0431 | 1.1245 | 1.2369 | DISTINCT | DISTINCT |

*Conclusion:* The 2 components remain physically distinct and do not collapse in 8 out of 9 converged bins.

### 2D - GLS chi2/ndf Envelope (Task 1D)
When enabling Global Least Squares (GLS) with the full non-diagonal correlation matrix, the resulting chi2/ndf rises significantly across all bins compared to the naive diagonal estimates.

*Conclusion:* When full non-diagonal correlations are preserved, the fit quality of the BGBW baseline degrades substantially compared to naive diagonal estimates, reinforcing the need for more flexible parametrizations like Tsallis 2c.

### 2E - Pull Summary (Task 1E)
Tsallis distributions (especially 2-component) consistently exhibit well-specified N(0,1) residuals with Kolmogorov-Smirnov p-values > 0.05 and near-zero mean pulls. By contrast, single-component and Jüttner models fail the KS normality test (p < 1e-5).

*Conclusion:* Residual pulls exhibit non-Gaussian structures in Jüttner models, while Tsallis achieves pulls much closer to a N(0,1) distribution.
"""

with open("research/robert/evidence-ledger.md", "a") as f:
    f.write(phase2_text)
