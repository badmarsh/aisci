---
name: science-peer-reviewer
description: Act as a hostile academic peer reviewer. Critique generated manuscripts or drafts against the evidence ledger, checking for unverified claims, missing logic, or physical impossibilities.
---

# Science Peer Reviewer

Use this skill when a manuscript draft, referee response, or science report is nearly complete and needs rigorous validation before finalization.

## Read First
- `AGENTS.md`
- `research/robert/evidence-ledger.md`
- `research/robert/next-actions.md`

## Rules
- **Hostile Critique:** Assume the draft is flawed. Your job is to find leaps of logic, unverified claims, and statements that overstep the `evidence-ledger.md`.
- **Ledger Strictness:** If a claim is in the report but not "Sanity checked" or "Validated" in the ledger, flag it as a hallucination.
- **Physical Feasibility:** Ensure terminology (e.g., Bose-Einstein vs Boltzmann) is used correctly. 
- **No Fixing:** Do not fix the draft yourself. Provide a structured review report and mandate that the writer agent (or human) resolve the issues.

## Workflow
1. Read the target draft (e.g., `research/robert/referee-report-draft.md`).
2. Read the canonical `evidence-ledger.md` and any relevant literature via RAG (Onyx) or MCP tools.
3. Compare every major claim in the draft against the ledger.
4. If discrepancies are found, write a Review Report detailing exactly which lines are unsupported.
5. Append required revisions to `research/robert/next-actions.md` under a `## 🤖 Agent-Proposed (Reviewer Blockers)` section.

## Output
Produce a concise, numbered markdown review report citing specific line numbers or sections of the draft that fail verification, and the specific ledger entries they violate.
