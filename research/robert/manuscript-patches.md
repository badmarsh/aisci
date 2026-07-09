# Manuscript Patches

Below are the suggested text patches you can directly insert into the manuscript to address the referee findings.

## 1. Boltzmann vs. Bose-Einstein Approximation

**Option A (Explicit Justification - Recommended if keeping current formula):**
> "While our model is motivated by quantum Bose-Einstein statistics for the bosons, the mathematical formulation integrated herein utilizes the Jüttner approximation (a relativistic Boltzmann-like tail). We find this approximation is well justified within our $p_T$ fitting range, as the high-energy exponential tail heavily dominates over the quantum $-1$ term."

**Option B (Promote to full Bose-Einstein - Requires re-running fits with quantum term):**
> "We implement the full Bose-Einstein quantum probability function. The denominator contains the necessary $(e^E - 1)$ term to fully describe the low-$p_T$ kinematic region where quantum statistical effects are non-negligible."

## 2. Jacobian Correction for Pseudorapidity Integration

**Insert this paragraph where the integration over $\eta$ is introduced:**
> "Because the experimental measurements are binned in pseudorapidity ($\eta$) rather than rapidity ($y$), the theoretical momentum distribution must be transformed accordingly. We apply the standard rapidity-to-pseudorapidity Jacobian $dy/d\eta$:
> 
> $$ \frac{dy}{d\eta} = \frac{p}{E} = \frac{\sqrt{p_T^2 \cosh^2(\eta) + m^2 \sinh^2(\eta)}}{m_T \cosh(\eta)} $$
> 
> This factor multiplies the integrand to ensure the phase-space integral correctly models the detector acceptance."
