# Manuscript Patches

Below are the suggested text patches you can directly insert into the manuscript to address the referee findings and the fundamental failure of the 1-component thermal model at high $p_T$.

## 1. Reframing the Manuscript (Choose ONE Path)

Robert's derivation fails at high-$p_T$ due to hard-scattering heavy tails ( $\chi^2/\text{ndf} > 4$ ), but successfully describes the low-$p_T$ thermal bulk. You must choose one of the following paths to survive peer review.

### Path A (Restrict the Fit to the Soft Sector)
**Insert this in the Methodology/Results section:**
> "While our model is motivated by quantum Bose-Einstein statistics for a locally thermalized source, we recognize that the high-$p_T$ region ($p_T > 2.5$ GeV) is dominated by non-thermal hard QCD scattering (parton fragmentation). Consequently, the purely hydrodynamic Blast-Wave formulation breaks down in this regime. To accurately extract the thermodynamic freeze-out parameters of the bulk medium, we restrict our fitting procedure strictly to the soft sector ($p_T < 2.5$ GeV), where the assumption of local thermal equilibrium and collective flow remains physically robust."

### Path B (Adopt the Tsallis Distribution)
**Insert this in the Methodology section:**
> "Although a standard Bose-Einstein Blast-Wave model captures the low-$p_T$ collective flow, it fails to describe the high-$p_T$ power-law tail inherent to high-energy hadronic collisions. To account for both the thermalized bulk and the non-extensive hard-scattering tail, we adopt the Tsallis distribution. This functional form naturally incorporates an exponential cutoff at low energies while accommodating the power-law tail through the non-extensivity parameter $q$, allowing for a thermodynamically consistent fit across the full $p_T$ spectrum."

## 2. Jacobian Correction for Pseudorapidity Integration

**Insert this paragraph where the integration over $\eta$ is introduced:**
> "Because the experimental measurements are binned in pseudorapidity ($\eta$) rather than rapidity ($y$), the theoretical momentum distribution must be transformed accordingly. We apply the standard rapidity-to-pseudorapidity Jacobian $dy/d\eta$:
> 
> $$ \frac{dy}{d\eta} = \frac{p}{E} = \frac{\sqrt{p_T^2 \cosh^2(\eta) + m^2 \sinh^2(\eta)}}{m_T \cosh(\eta)} $$
> 
> This factor multiplies the integrand to ensure the phase-space integral correctly models the detector acceptance."

## 3. T-β Degeneracy & Uncertainty Reporting

**Insert this paragraph into the methodology or results section where errors are reported:**
> "It is important to note that within the Blast-Wave framework, the kinetic freeze-out temperature ($T_{kin}$) and the average transverse flow velocity ($\langle \beta \rangle$) exhibit a strong negative correlation ($\rho < -0.95$). Consequently, the 1-dimensional marginalized parameter uncertainties derived from the diagonal elements of the covariance matrix understate the true systematic uncertainty of the fit. To interpret the thermodynamic state accurately, these parameters must be considered as a joint 2-dimensional posterior probability contour."
