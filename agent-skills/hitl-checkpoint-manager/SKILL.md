---
name: hitl-checkpoint-manager
description: Intercept high-uncertainty decisions and format structured prompts to force human alignment before proceeding.
---

# Human-In-The-Loop Checkpoint Manager

Use this skill to prevent autonomous runaways when a decision boundary is highly uncertain or destructive.

## Read First
- `AGENTS.md`

## Rules
- **Triggers:** Invoke this skill when an agent wants to:
  - Change the base functional form of the model in `physics/src/`.
  - Overwrite a "Validated" claim in `evidence-ledger.md`.
  - Delete older run data.
- **Workflow:**
  1. Halt execution.
  2. Format a concise markdown prompt using the `/grill-me` slash command or direct user question.
  3. Wait for the user to type "Proceed" or provide corrections.
- **Never:** Never try to guess the user's intent on high-uncertainty decisions.

## Output
A direct message to the user containing the exact context and the decision options.
