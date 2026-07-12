# AiSci Evidence Ledger Scoring Rubric

The `ledger_scorer.py` tool objectively evaluates claims in `evidence-ledger.md` against project artifacts (e.g. `fit_quality.csv`, `formula_confirmation.json`, or literature checks) using a GRADE-inspired framework. Each claim receives a score from **0 to 4** based on the robustness of its supporting evidence.

## Scoring Levels

### **Score 4: Validated (Fully Supported)**
- **Criteria:** The claim is confirmed by active computational artifacts or explicit literature matches.
- **Examples:**
  - `fit_quality.csv` confirms successful convergence and reasonable parameter bounds.
  - Symbolic tests (e.g., Lorentz-covariance limits) run and pass via `pytest`.
  - The required literature reference files exist and matches the claim exactly.

### **Score 2: Partial / Sanity Checked**
- **Criteria:** Some artifacts exist but fail to provide definitive confirmation, or the pipeline behavior is inconclusive.
- **Examples:**
  - A model component is claimed to be over-parameterized, but the convergence failure rate is ambiguous.
  - `formula_confirmation.json` exists but does not explicitly classify the model as expected.
  - A claim is marked as "Sanity checked" by a human reviewer without full automated test backing.

### **Score 1: Failing / Unchecked**
- **Criteria:** Automated checks were executed and actively failed, or the claim is strictly manually entered but unchecked.
- **Examples:**
  - `pytest` for the physics logic explicitly fails.
  - Required literature references are missing.
  - The claim is newly proposed and hasn't passed any sanity gate.

### **Score 0: Missing Artifacts**
- **Criteria:** The data files required to even evaluate the claim do not exist.
- **Examples:**
  - `fit_quality.csv`, `fit_parameters.csv`, or `fit_input.csv` are entirely missing from the run directory.
  - The system has no artifact output to test against.

## Process
The scorer runs a predefined heuristic mapping for specific high-priority claims (e.g. Tsallis parameter stability, static limits, model failures in high-multiplicity). For unrecognized claims, it falls back to the human-labeled `status` column (4 for "Supported", 2 for "Sanity checked", 1 for otherwise).
