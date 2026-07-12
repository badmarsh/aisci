# Canonical Notation Glossary

This glossary standardizes the nomenclature for variables and parameters used across the AiSci research project to avoid confusion between similar physical interpretations.

| Notation | Meaning | Notes |
| :--- | :--- | :--- |
| $T_{\text{stat}}$ | Statistical Temperature | The apparent temperature extracted from simple exponential fits without radial flow (e.g., $T$ in a pure Boltzmann or Jüttner distribution). Often substantially higher than $T_{\text{kin}}$ due to blueshifting. |
| $T_{\text{kin}}$ | Kinetic Freeze-out Temperature | The true thermal temperature of the source at the moment elastic collisions cease, extracted from models that explicitly include flow (e.g., Blast-Wave). |
| $T_{\text{eff}}$ | Effective Temperature | Same as $T_{\text{stat}}$. Often used when fitting data that contains radial flow with a static model. We prefer $T_{\text{stat}}$ or explicitly stating the model assumption. |
| $\beta_s$ | Surface Radial Flow Velocity | The maximum radial expansion velocity at the surface of the fireball in the Blast-Wave model. |
| $\langle \beta_r \rangle$ | Average Radial Flow Velocity | The volume-averaged radial flow velocity. Related to $\beta_s$ via the profile index $n$: $\langle \beta_r \rangle = \frac{2}{2+n} \beta_s$. |
| $U$ | Blast-Wave Four-Velocity | Used in some older derivations (e.g., the Jüttner component parameterization). Relates to velocity $v$ via $U = \gamma v = \sinh(Y)$ where $Y$ is the transverse fluid rapidity. It is NOT exactly the same as $\beta_s$, which is explicitly a velocity $v/c$. **Prefer $\beta_s$ when discussing velocity.** |
| $n$ | Velocity Profile Index | The exponent describing the radial dependence of the flow velocity in the Blast-Wave model: $\beta_r(r) = \beta_s (r/R)^n$. |
| $q$ | Non-extensivity Parameter | The parameter in the Tsallis distribution describing the deviation from standard Boltzmann-Gibbs statistics (where $q=1$). It models temperature fluctuations and hard-scattering power-law tails. |

## Notes for Agents

- Always use $T_{\text{kin}}$ and $\beta_s$ when discussing Blast-Wave parameters.
- Do not use $U$ unless specifically discussing the numerical parameterization inside the `manuscript_component_scalar` or `bose_component_scalar` integrands.
- Do not claim $T_{\text{stat}}$ represents the physical freeze-out temperature without qualification.
