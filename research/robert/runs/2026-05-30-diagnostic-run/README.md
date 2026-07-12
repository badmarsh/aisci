# Diagnostic Run 2026-05-30

## Purpose
Advance the AiSci project by running core physics validation scripts and capturing the current status of the symbolic and numerical layers.

## Artifacts
- \`boson_analysis.log\`: Output of \`libs/physics-core/src/boson_paper_analysis.py\`
- \`sympy_validation.log\`: Output of \`libs/physics-core/src/sympy_validation_agent.py\`
- \`tsallis_validation.log\`: Output of \`libs/physics-core/src/tsallis_physics_validation.py\`

## Summary of Findings
- **Symbolic Layer**: All sanity checks passed for Lorentz covariance, eta integration, and U-parameterization.
- **Data Issues**: Identified unconstrained fits and unphysical temperatures in high-multiplicity bins from retrieved manuscript chunks.
- **Tsallis Validation**: Successfully fitted Tsallis distribution to BGBW truth (Pions), confirming the expected T-bias (-27%).
- **Blocked**: Numerical fitting against real data remains blocked on \`fit_input.csv\`.
