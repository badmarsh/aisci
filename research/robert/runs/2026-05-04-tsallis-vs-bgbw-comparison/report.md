# Model Comparison Report: Tsallis vs. BGBW

**Date:** 2026-05-04  
**Run ID:** `2026-05-04-tsallis-vs-bgbw-comparison`  
**Author:** Antigravity (AiSci Platform Engineer)

## Objective
Establish a baseline comparison between the **Thermodynamically Consistent Tsallis Distribution** and the **Boltzmann-Gibbs Blast-Wave (BGBW)** model to quantify parameter bias when fitting flow-dominated spectra with a non-flow distribution.

## Method
1. **BGBW Truth Generation**: Generated a synthetic pion spectrum ($m=0.139$ GeV) using BGBW parameters typical for pp at 7 TeV:
   - $T_{kin} = 0.160$ GeV
   - $\langle \beta \rangle = 0.40$
   - $n = 1.0$ (Linear velocity profile)
2. **Tsallis Fitting**: Fitted the noisy synthetic data (5% noise) using the thermodynamically consistent Tsallis formula:
   - $dN/dp_T \propto p_T m_T [1 + (q-1)m_T/T]^{-q/(q-1)}$
3. **Validation**: Evaluated the fitted $T$ and $q$ against the input "truth".

## Results

| Parameter | Truth (BGBW) | Fitted (Tsallis) | Shift |
|---|---|---|---|
| **Temperature ($T$)** | 0.1600 GeV | 0.1171 GeV | -26.8% |
| **Non-extensivity ($q$)** | N/A | 1.0988 | N/A |

### Observations
- **Temperature Under-prediction**: The Tsallis distribution significantly under-predicts the temperature when radial flow is present. This is because the flow boost shifts the $p_T$ peak to the right, which the Tsallis model tries to compensate for by lowering $T$ (narrowing the thermal core) or increasing $q$ (broadening the tail).
- **Internal Consistency**: The refined Tsallis model ($T \approx 0.117$ GeV) is much closer to expected literature values than the previous simplified model ($T \approx 0.076$ GeV), confirming that the thermodynamically consistent form is necessary for meaningful comparisons.
- **Velocity Map**: Verified the $U \to v$ mapping for relativistic flow, confirming $v \to c$ behavior at large $U$.

## Conclusions
The Tsallis baseline is now stable and thermodynamically consistent. However, for Identified particles (Pions, Protons), the **BGBW model must be the primary fitting tool** to avoid the -27% bias in kinetic temperature extraction. The Tsallis model remains useful for high-$p_T$ power-law characterization ($q$ parameter).

## Next Steps
1. **Identified Fitting**: Once the $21-150$ data is unblocked, run parallel BGBW and Tsallis fits to extract $T$ vs. multiplicity.
2. **Residual Analysis**: Compare the residuals of both models to detect "flow-like" signatures in the low-$p_T$ region ($p_T < 1.0$ GeV).
