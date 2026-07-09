---
name: science-hypothesis-generator
description: >
  When a fit run produces an anomalous result (chi²/ndf regression,
  unexpected parameter value, or new |ρ| > 0.9 correlation), this skill
  orchestrates: literature retrieval → candidate hypothesis extraction →
  model modification proposal → next-actions.md entry.
  Trigger: "generate hypothesis for <anomalous result>" or automatically
  after any fit run that triggers the Anomaly Duty rule in AGENTS.md.
---

## Prerequisites

- Scite or Consensus MCP must be reachable (test with `check_mcp_liveness.py`).
- The triggering fit run directory must be provided.
- The agent must have already read the evidence-ledger.md entry for the
  relevant claim before invoking this skill.

## Instructions

### Step 0 — Parse the anomaly
Accept the following inputs (from the agent's context or explicit args):
- `anomaly_description`: plain-text description of what was unexpected.
  E.g. "BGBW chi²/ndf jumped from 2.1 to 18.7 in bin 71–80 after GLS
  covariance was applied."
- `run_dir`: path to the triggering fit run directory.
- `claim_id`: the evidence-ledger claim ID this relates to (e.g. "C-1").

### Step 1 — Literature retrieval (Scite MCP)
Query Scite with the anomaly as the search string.
Required query format: `"<observable> <model name> <particle system>"`.
Example: `"blast wave temperature beta degeneracy pp 13 TeV ALICE"`

Record up to 5 results: title, DOI, abstract snippet, supporting/contrasting
citation count.

If Scite returns < 2 results, broaden the query by removing the collision
system. If still < 2, query Consensus MCP with the same string.

### Step 2 — Extract physical explanations
For each retrieved paper:
- Does it offer a physical explanation for the observed anomaly?
- Does it propose a model modification (e.g., incorporating radial flow
  profile, hadronic rescattering corrections, non-equilibrium effects)?
- Tag each as: RELEVANT | TANGENTIAL | CONTRADICTS.

### Step 3 — Draft model modification candidate
From the RELEVANT papers, draft ONE candidate model modification:

```
## Candidate Model Modification
**Anomaly:** <anomaly_description>
**Inspired by:** <paper title, DOI>
**Physical reasoning:** <1-2 sentences from the paper>
**Proposed change to fitting_pipeline.py:**
  - Modify FitSpec: <specific change — e.g., "add radial flow profile
    exponent n as free parameter in bgbw_scalar()">
  - Expected effect: <what chi²/ndf change is expected>
  - Test strategy: run with `python physics/cli.py --models bgbw_nprofile`
    and compare AIC vs current BGBW.
**Literature support:** <citation>
**Acceptance gate:** AIC improvement > 2 units in ≥ 8/10 bins.
```

### Step 4 — Append to next-actions.md
Append the following to `research/robert/next-actions.md` under
`## 🤖 Agent-Proposed (Pending Robert Approval)`:

```
### [HYP-YYYY-MM-DD] Test <model modification name>
**Trigger:** <anomaly_description>
**Triggering run:** <run_dir>
**Literature grounding:** <title> (<DOI>) — <supporting/contrasting> citations via Scite
**Proposed action:** <model modification candidate from Step 3>
**Acceptance:** AIC improvement > 2 in ≥ 8/10 bins; chi²/ndf < 3 in all bins.
```

### Step 5 — Report
Print:
- Anomaly parsed: YES/NO
- Papers retrieved: N (Scite/Consensus)
- RELEVANT papers: N
- Hypothesis drafted: YES/NO
- next-actions.md entry written: YES/NO
