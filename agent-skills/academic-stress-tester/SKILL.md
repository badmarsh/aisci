---
name: academic-stress-tester
description: A fail-closed workflow to extract literal quotes from drafts, run them through a strict verification gate, and aggressively stress-test logic against the evidence ledger.
---

# Academic Stress Tester

Use this skill immediately after a draft or report has been produced by the Peer Reviewer or Report Writer to guarantee zero hallucinations.

## Read First
- `AGENTS.md`
- `research/robert/evidence-ledger.md`
- Dashboard Database (`deployment/aisci-dashboard/data/evidence_graph.db`)

## Rules
- **Verification Gate:** Stop immediately if the local parse drifts to generic non-HEP topics (e.g., Neural Networks, Fluid Dynamics).
- **Literal Quotes:** Every citation must map to an exact literal quote found in the literature database.
- **Fail-Closed:** Do not update canonical science files or pass the stress test unless all exact local quotes pass the verification gate.

## Workflow
1. Parse the target draft (e.g., `research/robert/referee-report-draft.md`).
2. Extract all physics claims and literature references.
3. Cross-reference them heavily with the `evidence-ledger.md` and `deployment/aisci-dashboard/data/evidence_graph.db`.
4. If ANY claim lacks a literal quote or ledger backing, halt the pipeline and demand human review.

## Output
Produce an `extraction.json` summary of verified quotes, or a fatal error blocking further pipeline progression.
