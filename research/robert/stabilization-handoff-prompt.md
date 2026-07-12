# Megaprompt: Stabilize Robert's Manuscript Fits and Mitigate Flawed Conclusions Globally

Execute the following plan to implement the mathematical conclusions from our stabilization work across the entire repository. We have rigorously proven that the 3-component Jüttner/Boltzmann model used in the manuscript is both physically invalid at high temperatures (underestimating yield by ~84%) and mathematically degenerate at low radial velocities ($U \approx 0$).

Your tasks are:

## 1. Switch to Exact Bose-Einstein
Modify the relevant physics fitting scripts (e.g., `libs/physics-core/src/fitting_pipeline.py`) to use the **exact Bose-Einstein distribution** denominator instead of the Boltzmann approximation. The manuscript's core equation must be corrected for all high-temperature thermal systems.

## 2. Implement 2-Component Constraints
Since the Fisher Information matrix proved the 3-component model is completely over-parameterized (degenerate), transition the fit pipeline to a 2-component exact Bose-Einstein model. Run the fits for the multiplicity bins and evaluate convergence and parameter uncertainties.

## 3. Global Mitigation Sweep
Sweep the repository to mitigate the flawed 3-component Jüttner model conclusions, adhering strictly to the `AGENTS.md` **Global Mitigation Rule**.
- Update `research/robert/next-actions.md` to formally deprecate any tasks related to the 3-component Jüttner fits and prioritize the 2-component Bose-Einstein approach.
- Update `research/robert/evidence-ledger.md` to firmly declare that all future fit runs must use exact Bose-Einstein statistics and that 3-component parameter extraction is mathematically forbidden due to degeneracy.
- Sweep the `docs/ops/` and platform backlog to remove any legacy configuration references to the failed Jüttner runs.
- Ensure any UI/dashboard components that read from the `evidence-ledger.md` are aligned with these updated conclusions.

## 4. Verification
Verify that the new fits converge cleanly without generating infinite covariances or `nan` matrices, and that the single source of truth across all docs is strictly aligned.
