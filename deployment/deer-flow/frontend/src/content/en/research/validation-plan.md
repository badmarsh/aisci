# Validation Plan

## Formula Checks

- Re-run symbolic checks for each numbered equation, not only extracted snippets.
- Confirm whether the manuscript uses a full Bose-Einstein form or an explicit Boltzmann/Juttner approximation.
- Confirm dimensions of distribution, normalization, fit parameters, and integration measures.
- Confirm mass-shell and theta-function handling.
- Confirm eta-cut and pT-cut boundaries, including Jacobians and acceptance limits.
- Confirm U parameterization maps to subluminal physical velocity.
- Record every approximation: massless limit, pseudorapidity versus rapidity, finite acceptance, and low-pT exclusion.

## Numerical Checks

- Generate distributions for representative U and temperature values.
- Check blue-shift behavior as U increases.
- Validate low-pT exclusion assumptions.
- Test sensitivity to pT range and binning.
- Compare one-, two-, and three-component variants to test whether the extra components are constrained.
- Report optimizer status, covariance quality, parameter correlations, and local-minimum sensitivity.

## Literature Checks

- Compare against literature-matched Tsallis/Tsallis-Pareto fit expectations.
- Compare against Blast-Wave model behavior in pp or p-Pb/AA contexts where relevant, without assuming pp trends must be hydrodynamic.
- Check whether comparable studies report chi2/ndf, uncertainties, and multiplicity trends.
- Record whether comparison papers use identified particles, charged particles, different pT ranges, or different collision systems.

## Acceptance Criteria

- Equations are internally consistent under stated assumptions.
- Any Bose-Einstein versus Boltzmann/Juttner approximation is explicit.
- Fit parameters are constrained with realistic uncertainties.
- chi2/ndf is reported for every bin.
- Model behavior has a clear explanation at high multiplicity.
- Simpler baseline models have been tested before interpreting multi-component parameters physically.
- Claims are supported by cited literature or explicitly marked as speculative.
