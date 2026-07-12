# Science Questions

## Primary Question

Is Robert's moving-system boson probability model internally consistent, physically interpretable, and statistically supported when compared with the reported ATLAS 13 TeV data behavior?

## Current Framing

The current local checks are sanity checks under explicit assumptions, not final validation. In particular, the implemented checks use a Boltzmann/Juttner-like exponential form and massless or ultra-relativistic kinematics in places. The manuscript must be checked separately if it claims a full Bose-Einstein distribution, finite-mass treatment, or combined pT/eta cuts beyond those assumptions.

## Active Questions

1. Does the manuscript clearly distinguish a Boltzmann/Juttner approximation from a full Bose-Einstein distribution?
2. Are the derivations Lorentz-covariant, dimensionally consistent, and explicit about Jacobians and normalization?
3. Does the eta-cut formula reduce correctly in the static limit?
4. Are the massless, pseudorapidity, and low-pT assumptions justified for the fitted range?
5. Are the high-multiplicity fit parameters constrained by the available pT range?
6. Are the reported high-multiplicity uncertainties evidence of over-parameterization?
7. [ANSWERED 2026-06-20] Does any velocity trend with multiplicity remain physically interpretable after testing parameter degeneracy and fit-range sensitivity?
   → No. In all 9 BGBW bins, |ρ(T, β_s)| ≥ 0.934. In 4 bins |ρ| > 0.95 (degenerate). T_kin and β_s cannot be reported as independent parameters. The correct representation is a 2D joint posterior contour. See evidence-ledger.md T-β Correlation Analysis (2026-06-20).
8. What chi2/ndf values, covariance matrices, and parameter correlations are obtained across all bins?
9. How do the results compare with literature-matched Tsallis/Tsallis-Pareto and Blast-Wave baselines?
10. What missing tables, plots, data, or derivation steps would a referee require?

## Blocking Input

[RESOLVED 2026-06-14] Data provided in libs/physics-core/data/fit_input_ins1735345.csv. Active blockers are now C1 (estimator mismatch) and O-11 (BE fit execution). See next-actions.md.
