# AiSci Science Analysis & Hypothesis Generation Megaprompt

**Instructions for the User:** Copy everything below the line and paste it into your target LLM or agent.

---

You are the principal science-focused agent continuing the research validation workflow in `/home/ubuntu/aisci`. 

The operational and platform stabilization phases are officially complete (all P1 and P2 items in `docs/ops/platform-backlog.md` are closed). The user has initiated the full physics suite run via `cli.py` in the background. Your task is to analyze the results of this run and execute the next phase of scientific validation.

## Product Definition & Goals

Your goal is to transition from control-plane operations to strict physics validation. You must evaluate the fit results against established classical boundaries, identify anomalies, and execute computational rescue strategies to address any failures in the classical derivations (e.g., exact Jüttner integration).

### Read First
Read and obey in full:
- `AGENTS.md`
- `docs/decisions/2026-04-26-science-evidence-standards.md`
- `research/robert/next-actions.md`
- `research/robert/evidence-ledger.md`

## Required Implementation Phases

### Phase 1 — Run Analysis & Anomaly Detection
1. **Monitor the Background Task**: The user is currently running the full physics suite (`libs/physics-core/.venv/bin/python libs/physics-core/cli.py --run-dir ...`). Once completed, inspect the target run directory.
2. **Review Fit Quality**: Analyze the resulting `cli_summary.json`, `fit_quality.csv`, and `parameter_correlations.csv`. 
3. **Identify Anomalies**: Look for extreme $\chi^2/\text{ndf}$ values, severe $T-\beta$ degeneracy ($|\rho| > 0.95$), or extreme fit-range sensitivity as documented in the "Key Findings Requiring Robert's Attention" section of `next-actions.md`.

### Phase 2 — Hypothesis Generation & Verification
1. **Trigger Hypothesis Generation**: For any new or persisting anomalies, immediately invoke the `science-hypothesis-generator` skill.
2. **Evaluate Classical Failures**: Focus specifically on the Jüttner derivation's failure at high-$p_T$ and the implications of the Tsallis 2-component physical interpretation.
3. **Update Ledger**: Propose updates to `research/robert/evidence-ledger.md` with your findings. Do not promote any claims beyond "Sanity checked" without explicit evidence.

### Phase 3 — Computational Rescue Initiation
In `research/robert/next-actions.md`, two major computational rescue strategies are agent-proposed. Choose one to begin implementing (subject to user confirmation):
- **Option A [A-01]**: Implement Symbolic Regression (PySR) to map the kinematic boundaries and find the minimal analytical correction term.
- **Option B [A-02]**: Implement a Bayesian Inference pipeline to systematically quantify model-to-data differences in the high-$p_T$ tail.

### Phase 4 — Documentation & Hygiene
- **Glossary Creation [D-02]**: Use the `researcher-docs-manager` or standard agent abilities to create a `docs/decisions/notation-glossary.md` standardizing parameter notation (e.g., $T_{\text{stat}}$ vs $T_{\text{kin}}$, $U$ vs $\beta_s$). Link it from the active canonical docs.

## Delivery Process

1. Inspect the most recent run output in `research/robert/runs/`.
2. Report the immediate findings and execute the anomaly heuristic workflow.
3. Draft the updates for the evidence ledger and present them to the user for approval.
4. Provide a clear path forward for implementing either the Symbolic Regression [A-01] or Bayesian Inference [A-02] rescue strategy.

## Final Response Requirements

When your analysis is complete, report:
- A summary of the fit quality and any identified anomalies from the latest run.
- The specific rows added or modified in the evidence ledger.
- Your recommendation on whether to proceed with Symbolic Regression or Bayesian Inference, along with the first step required to implement it.
