# Analysis: Jüttner 3-Component Singularity at U → 0

**Date:** 2026-07-12
**Status:** Mathematical proof complete; baseline proposed.

## 1. Mathematical Proof of Singularity

The 3-component Jüttner parameterization (or any combination involving a moving component where the velocity $U \to 0$) becomes mathematically singular. We can demonstrate this by constructing the Fisher Information matrix symbolically. 

Let the integrand for the moving component be:
$$ I = \exp\left( - \frac{\gamma m_T \cosh\eta - U p_T \sinh\eta}{T_{kin}} \right) $$
where $\gamma = \sqrt{1 + U^2}$. 

The derivative of the integrand with respect to the velocity parameter $U$, evaluated at $U=0$, is:
$$ \left. \frac{\partial I}{\partial U} \right|_{U=0} = \frac{p_T \sinh\eta}{T_{kin}} \exp\left(-\frac{m_T \cosh\eta}{T_{kin}}\right) $$

This derivative is an **odd function** with respect to pseudorapidity $\eta$. Since the experimental acceptance integrates over a symmetric pseudorapidity window $[-\eta_{max}, +\eta_{max}]$, the integral of this odd function evaluates exactly to zero:
$$ \int_{-\eta_{max}}^{+\eta_{max}} \left. \frac{\partial I}{\partial U} \right|_{U=0} d\eta = 0 $$

Consequently, the gradient of the model with respect to $U$ vanishes everywhere at $U=0$. This causes a column of zeros in the Jacobian matrix $J$, which in turn causes the Fisher Information Matrix ($I = J^T J$) to have a zero determinant ($\det(I) \to 0$ as $U \to 0$). 
**Conclusion:** The model is mathematically singular (rank deficient) at $U \to 0$, leading to infinite parameter uncertainties and making the parameters $T_{stat}$, $T_{kin}$, and $U$ perfectly degenerate and physically meaningless.

## 2. Proposed Non-Singular Baseline

**Proposed Baseline:** Two-Component Soft/Hard Model (Bylinkin & Rostovtsev / Tsallis 2-component)
**Physical Rationale:** Instead of attempting to fit the spectrum with an over-parameterized set of moving and static thermal sources (which collapse into singularity when the flow velocity vanishes), the physics is more robustly described by separating the underlying production mechanisms:
1. **Soft Component:** A static or collective exponential term describing the thermalized bulk medium at low-$p_T$.
2. **Hard Component:** A power-law or Tsallis term describing the perturbative QCD (pQCD) hard scatterings that produce the high-$p_T$ tail.

By using an explicit additive two-component function (e.g., an exact Bose-Einstein thermal term + a Tsallis power-law term, or simply a 2-component Tsallis), we avoid artificial kinematic degrees of freedom and prevent the optimizer from getting trapped in degenerate flow-velocity valleys.

## 3. Unverified Claims

The following have **NOT** yet been verified for the proposed baseline and must be checked before promoting any claims:
- $\chi^2/\text{ndf}$ and fit quality across all multiplicity bins.
- The parameter stability and correlation matrix (ensuring the 2-component model doesn't introduce a new degeneracy).
- Direct quantitative comparison against literature implementations.
