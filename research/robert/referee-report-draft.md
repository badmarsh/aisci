# Expanded Referee Report

> **Draft date:** 2026-07-11
> **Based on:** `research/robert/evidence-ledger.md` and automated validation pipeline.

This report summarizes the comprehensive mathematical and phenomenological review of the proposed "boson probability function for the moving system." While the functional form introduces interesting non-extensive thermodynamic properties, several critical physical omissions, statistical ambiguities, and unaddressed systematic biases must be rectified before the manuscript can be recommended for publication.

## Major Concerns

### 1. Missing Pseudorapidity Jacobian (W-01 & W-02)
The derivation integrates the Jüttner-like distribution over pseudorapidity ($\eta$), but it omits the fundamental kinematic Jacobian $dy/d\eta = p/E$. For a massive particle (e.g., pion), rapidity $y \neq \eta$ at low $p_T$. This omission inflates the phase-space volume and biases the extracted parameters by up to ~22% at $p_T = 0.175$ GeV. 
- **Action Required**: The model integrand must explicitly incorporate the $dy/d\eta$ correction, and all datasets must be re-fitted.

### 2. Ambiguity Between Jüttner and Bose-Einstein (N-01)
The manuscript claims a quantum Bose-Einstein distribution but mathematically employs a classical Boltzmann/Jüttner approximation ($f(p) \sim \exp(-\beta U \cdot p)$ instead of the exact quantum denominator). Our analytical checks confirm that an exact closed-form integration of the true Bose-Einstein/Tsallis moving source over $\eta$ is not mathematically convergent without Padé approximations.
- **Action Required**: Explicitly state that the derivation utilizes a classical Boltzmann limit and restrict the physical claims accordingly, or rename the manuscript to "momentum distribution function of particles in a moving system."

### 3. Missing Goodness-of-Fit Metrics (W-04)
Table 1 omits the $\chi^2/\text{ndf}$ values, reporting only parameter values. Our independent verification pipeline shows that the 1-component Jüttner model yields an unacceptable fit quality ($\chi^2/\text{ndf}$ ranging from 50 to 218). In contrast, a 2-component Tsallis model fits the data with $\chi^2/\text{ndf} \approx 1$. 
- **Action Required**: The manuscript must explicitly report the $\chi^2/\text{ndf}$ for all multiplicity bins to allow readers to evaluate statistical support.

### 4. Severe Parameter Degeneracy (W-03 & W-09)
Within the Blast-Wave framework, the kinetic freeze-out temperature ($T_{kin}$) and the average transverse flow velocity ($\langle \beta \rangle$) exhibit severe negative correlation ($\rho < -0.95$). Providing 1-dimensional marginalized uncertainties via diagonal errors vastly understates the true uncertainty.
- **Action Required**: The authors must provide 2-dimensional posterior probability contours (via profile likelihoods or Bayesian MCMC corner plots) to correctly report the parameter degeneracy. 

### 5. Extreme Fit-Range Sensitivity (W-05)
A systematic fit-range sensitivity scan reveals that BGBW parameters are highly unstable. When excluding the low-$p_T$ region ($p_T < 0.45$ GeV), $T_{kin}$ drifts by up to 43 MeV in certain bins ($>7\sigma$ deviation).
- **Action Required**: Document this extreme sensitivity to the low-$p_T$ boundary as a primary source of systematic uncertainty in the methodology section.

### 6. Estimator Mismatch and Matrix Unfolding (W-06)
The manuscript incorrectly compares generic multiplicity estimators without addressing detector response boundaries. Fitting against the raw V0M spectra yields artificially inflated $\chi^2/\text{ndf}$.
- **Action Required**: The authors must apply a proper MC-derived response matrix ($R_{\text{SPD} \to \text{Nch}}$) to unfold the measured spectra back to the true primary charged particle multiplicity before fitting. (Our verification confirms this reduces $\chi^2$ by 40-95% while preserving the physical temperature trend).

### 7. Pion-Mass Assumption Bias (W-07)
Performing fits using a pure pion-mass hypothesis on unidentified inclusive hadron data mathematically underestimates the true effective kinetic temperature due to the heavier mass contributions of kaons and protons.
- **Action Required**: The authors must either fit strictly identified spectra ($\pi, K, p$) simultaneously, or explicitly document the estimated thermodynamic bias incurred by the unphysical single-mass approximation.

## Conclusion

The manuscript requires a major revision to incorporate the correct kinematic Jacobian, report goodness-of-fit metrics, and document the profound systematic uncertainties associated with parameter degeneracy and fit-range sensitivity. Once these technical rectifications are implemented, the phenomenological conclusions regarding multiplicity-dependent freeze-out states can be robustly evaluated.
