# Manuscript Patches

Below are the suggested text patches you can directly insert into the manuscript to address the referee findings and the fundamental failure of the 1-component thermal model at high $p_T$.

## 1. Reframing the Manuscript (Choose ONE Path)

Robert's derivation fails at high-$p_T$ due to hard-scattering heavy tails ( $\chi^2/\text{ndf} > 4$ ), but successfully describes the low-$p_T$ thermal bulk. Furthermore, the title claims a "boson" distribution, but the mathematical derivation lacks the Bose-Einstein denominator. You must choose one of the following paths to survive peer review.

### Path A (Restrict the Fit to the Soft Sector and Justify Boltzmann Approximation)
**Insert this in the Methodology/Results section:**
> "While our model is motivated by quantum Bose-Einstein statistics for a locally thermalized source, the derived functional form utilizes a classical Boltzmann/Jüttner approximation: $f(p) \sim \exp(-\beta U \cdot p)$ rather than the exact $f(p) = 1/(\exp(\beta U \cdot p) - 1)$. We restrict our fitting procedure strictly to the soft sector ($p_T < 2.5$ GeV) where collective flow dominates, but we acknowledge that the exact Bose-Einstein treatment is required at very low $p_T$ (where $p_T \lesssim 3T$). Thus, our approximation is valid primarily in the intermediate thermal range."

### Path B (Adopt the Tsallis Distribution and Rename)
**Insert this in the Methodology section:**
> "Although a standard Bose-Einstein Blast-Wave model captures the low-$p_T$ collective flow, it fails to describe the high-$p_T$ power-law tail inherent to high-energy hadronic collisions. To account for both the thermalized bulk and the non-extensive hard-scattering tail, we adopt the Tsallis distribution. We explicitly note that we utilize a classical limit in our derivation, and we rename the manuscript to 'momentum distribution function of particles in a moving system' to avoid the strict quantum statistical requirement of the exact Bose-Einstein denominator."

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

## 4. Update Table 1 with $\chi^2/\text{ndf}$ Values

**Insert the following in the results section replacing Table 1:**
> "In Table 1, we report the $\chi^2/\text{ndf}$ values for all compared models across all multiplicity bins. We explicitly note that there are $n_{pts} = 47$ data points per bin, and the number of parameters is 3 for the 1-component models (MJ, BE, TS), 4 for BW 1c, and 6 for the 2-component models. Note that the 1-component Jüttner model yields unacceptable $\chi^2/\text{ndf}$ (50–218), while the 2-component Tsallis model provides the best description of the data ($\chi^2/\text{ndf} \approx 1$)."
> 
> *(See `table1_replacement.md` for the full data to copy into Table 1, as well as the supplementary AIC/BIC table.)*

## 5. Fit-Range Sensitivity Documentation

**Insert this paragraph in the systematic uncertainties or methodology section:**
> "We assessed the stability of the BGBW extracted parameters by performing a fit-range sensitivity scan. When the low-$p_T$ region ($p_T < 0.45$ GeV) is excluded from the fit, the kinetic freeze-out temperature $T_{kin}$ drifts by up to 43 MeV in certain multiplicity bins, representing a statistical deviation of $>7\sigma$ relative to the full-range fit covariance. This extreme sensitivity underscores that the extracted parameters are highly dependent on the softest sector of the spectrum, and any physical interpretation must account for this fit-range dependency as a primary source of systematic uncertainty."
