# Megaprompt: Fits Robustness, Anomalies, and Theoretical Alignment

**Instructions:** Copy and paste the prompt below into a new agent session to harden the physics fit pipeline, fix UI anomalies, and align the dashboard with the canonical evidence ledger.

---

### The Prompt

**Objective:**
You are tasked with analyzing the repository's theoretical principles and objectives, loading the status quo literature and evidence ledger, and making the fitting runs (`http://localhost:5173/projects/robert-boson-manuscript/fits`) more robust by fixing UI anomalies and handling theoretical edge cases. You will not stop working until you have verified these features using Playwright tests and `curl`.

**Step 1: Analyze Theoretical Principles & Objectives (Do NOT code yet)**
Before writing any code, thoroughly read and analyze the following resources to understand the scientific objectives and theoretical constraints of the AiSci repository:
1. `research/robert/evidence-ledger.md` (Crucial for understanding the scientific claim status).
2. `docs/decisions/2026-04-26-science-evidence-standards.md` (For understanding the distinction between sanity checks and supported evidence).

*Key Theoretical Principles to internalize:*
- The **3-component Jüttner parameterization** is mathematically singular at $U \to 0$ and causes rank deficiency/infinite parameter uncertainties.
- The **1-component Bose-Einstein model** is fundamentally incapable of describing the hard QCD scattering tail at high $p_T$.
- A critical **Jacobian correction** ($dy/d\eta$) of up to 22% is required for low-$p_T$ data because ALICE data uses pseudorapidity ($\eta$), while the manuscript uses rapidity ($y$).
- The Tsallis 2-component model is the leading theoretical baseline, winning in AIC/BIC, but requires careful covariance inspection to prevent overfitting.
- The published manuscript incorrectly used a pure Boltzmann/Jüttner exponential instead of a true Bose-Einstein denominator.

**Step 2: Load Status Quo Literature & Evidence**
- Using your available tools, query the MCP endpoints or read the files under `research/robert/literature_*.md` to load the current literature context.
- Ensure you understand the distinction between the original Blast-Wave baseline (SSH 1993) and the Tsallis-Pareto models (Cleymans & Worku 2012).

**Step 3: Harden the Fitting Runs & Fix Anomalies**
Target the backend fit pipeline (`libs/physics-core/src/`) and the frontend dashboard (`deployment/aisci-dashboard/src/routes/projects.$projectId.fits.tsx`).
- **Robustness**: Implement defensive error handling for missing covariance matrices, `valid=False` Minuit convergence failures, and unphysical parameters (e.g., negative temperatures).
- **Anomaly Fixes**: Ensure that UI elements correctly flag the singularity in 3-component Jüttner models and the $dy/d\eta$ Jacobian requirements. Prevent React rendering crashes caused by missing `fitRows`, `correlations`, or `chi2Series` data.
- **Theoretical Alignment**: Ensure the UI surfaces the structural warnings documented in the evidence ledger (e.g., warning users if they attempt a 1-component Bose-Einstein fit on high $p_T$ data).

**Step 4: End-to-End Testing (Playwright & Curl)**
You must verify your work thoroughly:
1. Write and run a `curl` script to hit the backend `/fits` API endpoints, verifying that anomalies and edge cases are handled gracefully without 500 errors.
2. Write and run **Playwright** end-to-end tests to simulate a user visiting `http://localhost:5173/projects/robert-boson-manuscript/fits`.
3. Ensure the Playwright tests verify that the UI renders without "Telemetry interrupted" errors, displays the correct warnings for degenerate fits, and properly renders the covariance matrix sheets.

**Do not terminate your session until both the curl tests and Playwright tests pass successfully.**
