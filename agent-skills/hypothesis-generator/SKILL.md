---
name: hypothesis-generator
description: Brainstorm physically sound extensions to the Tsallis-Pareto and Bose-Einstein models based on literature gaps.
---

# Hypothesis Generator

Use this skill to autonomously brainstorm novel modifications to existing high-energy physics models.

## Read First
- `AGENTS.md`
- `research/robert/evidence-ledger.md`
- `research/literature/`

## Rules
- **Physical Grounding:** Do not invent arbitrary mathematical functions. Modifications must be physically motivated (e.g., collective flow, freeze-out temperature dependencies).
- **Novelty Verification:** Check MCP tools to ensure the hypothesis has not already been ruled out in recent ATLAS 13 TeV papers.
- **Workflow:** 
  1. Identify a gap in `evidence-ledger.md`.
  2. Brainstorm a hypothesis to close the gap.
  3. Append the hypothesis to `research/robert/next-actions.md` under a `## 🤖 Agent-Proposed` block.

## Output
Produce a short Markdown rationale citing the literature gap and the proposed mathematical modification.
