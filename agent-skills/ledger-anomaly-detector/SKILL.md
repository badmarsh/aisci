---
name: ledger-anomaly-detector
description: >
  Scans research/robert/evidence-ledger.md for claims whose Next Gate
  criteria appear to have been met by existing runs/ artifacts, and for
  claims with no corresponding active next-actions.md item. Drafts
  proposals under ## 🤖 Agent-Proposed in next-actions.md.
  Trigger when: asked to "check the ledger for gaps", run nightly via
  cron, or invoked after any fit run completes.
---

## Instructions

### Step 0 — Read canonical files in full
1. Read `research/robert/evidence-ledger.md`.
2. Read `research/robert/next-actions.md`.
3. List the contents of `research/robert/runs/` (top level only).

### Step 1 — Gap detection
For each claim row in `evidence-ledger.md`:
- Extract: Claim ID, Status, Next Gate description, Current Evidence.
- If `Status = Sanity checked`:
  - Check whether any run directory under `runs/` matches the
    Next Gate description (e.g., "profile scan CSVs exist" → look for
    `runs/*-bgbw-profile-scan/contour_bin_*.csv`).
  - If matched: mark as PROMOTABLE.
- If `Status = Needs validation` or `Status = Blocked`:
  - Check whether a corresponding item exists in `## 🟢 Active` or
    `## 🤖 Agent-Proposed` of `next-actions.md`.
  - If no item exists: mark as UNTRACKED.

### Step 2 — Literature grounding
For each PROMOTABLE or UNTRACKED claim:
- Query Scite MCP: `search(query="<claim text>", limit=3)`.
- Record the top result: title, DOI, supporting/contrasting count.
- If Scite is unavailable, query Consensus MCP instead.
- If both are unavailable, note "literature check skipped — MCP offline"
  and proceed.

### Step 3 — Draft proposals
For each PROMOTABLE claim:
- Draft a promotion proposal entry:
  ```
  ### [LAD-YYYY-MM-DD] Promote "<Claim ID>" to Validated
  **Trigger:** Next Gate criteria met by `runs/<dir>/`.
  **Evidence:** <file path>.
  **Literature grounding:** <citation from Step 2>.
  **Proposed action:** Open a PR updating evidence-ledger.md Status
  from "Sanity checked" to "Validated" and filling Current Evidence.
  ```

For each UNTRACKED claim:
- Draft a new action entry:
  ```
  ### [LAD-YYYY-MM-DD] Investigate untracked claim "<Claim ID>"
  **Trigger:** Claim has Status="<status>" with no active queue item.
  **Literature grounding:** <citation from Step 2>.
  **Proposed action:** <specific next experiment or computation>.
  ```

### Step 4 — Write proposals
Append ALL drafted proposals to `research/robert/next-actions.md`
under the section `## 🤖 Agent-Proposed (Pending Robert Approval)`.
Create the section if it does not exist. Do NOT modify any other
section.

### Step 5 — Report
Print a summary:
- N claims scanned
- N PROMOTABLE found
- N UNTRACKED found
- N proposals written
- Scite/Consensus availability status
