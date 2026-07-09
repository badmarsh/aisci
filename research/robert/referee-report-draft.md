# Referee Report Draft

> **Draft date:** 2026-07-09  
> **Based on:** `research/robert/evidence-ledger.md` state as of 2026-07-09.

This is an output draft, not the source of truth. Promote or revise findings from `evidence-ledger.md` after the relevant evidence gates pass.

## Summary

The paper proposes a moving-system boson probability model and applies it to ATLAS 13 TeV data. Our detailed kinematic checks show that while the formulation has interesting phenomenological properties, there are specific mathematical and reporting omissions that must be addressed before the results can be properly evaluated. In particular, the omission of the pseudo-rapidity Jacobian factor significantly biases the reported parameter values, and the absence of goodness-of-fit metrics prevents a fair comparison with established baselines.

## Major Concerns

1. **Missing Jacobian Correction:** The manuscript integrates the Jüttner-like distribution over pseudorapidity ($\eta$) but omits the mandatory $dy/d\eta = p/E$ Jacobian factor. This omission inflates the phase-space integral and causes a known ~22% systematic error at $p_T = 0.175$ GeV. This must be corrected in the formula and the parameters must be re-fitted.
2. **Goodness-of-Fit Reporting:** Table 1 omits the $\chi^2/\text{ndf}$ values entirely. The manuscript must report $\chi^2/\text{ndf}$ for all multiplicity bins so the statistical support for the model can be evaluated.
3. **Approximation Ambiguity:** The manuscript must state clearly whether the fitted formula is a full Bose-Einstein distribution or a Jüttner/Boltzmann approximation, as the integration logic currently implements the latter.
4. **Baseline Comparisons:** The paper lacks comparison with standard phenomenological baselines. The fit results should be evaluated against Tsallis-Pareto (with proper Jacobian) and Blast-Wave models to demonstrate whether the new distribution provides a statistically significant improvement.
5. **High-Multiplicity Parameter Constraints:** The high-multiplicity bins exhibit severe parameter degeneracy ($| \rho | > 0.9$ between $T$ and velocity components). This must be explicitly disclosed via parameter uncertainties and correlation matrices (or profile likelihood contours).

## Minor Concerns

- Equation numbering and cross-references should be checked after the final manuscript export.
- Figure captions should explicitly state the fit range and any excluded data regions.

## Requested Actions for the Authors

- Apply the $dy/d\eta$ Jacobian to the model integrand and rerun all fits.
- Update Table 1 to include parameter uncertainties and $\chi^2/\text{ndf}$.
- Insert an explicit sentence justifying the use of the Jüttner approximation.
