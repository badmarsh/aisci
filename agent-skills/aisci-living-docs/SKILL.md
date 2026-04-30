---
name: aisci-living-docs
description: Scan the entire AiSci codebase to understand its current real state, then add, update, or archive documentation so that three audiences always have accurate information: the coding agents manager (ops/platform), Robert the researcher (science workflow), and any new agent reading the repo for the first time. Optionally drafts a DeerFlow deep-research run to cross-check platform status against running services.
---

# AiSci Living Docs

Use this when documentation has drifted from reality — after a burst of platform work,
after onboarding a new service, after a large cleanup, or at any point where someone
asks "how does AiSci actually work right now?"

This skill does NOT produce a new analysis file by default.
It produces targeted edits to existing canonical docs.

---

## Audiences

This skill always writes for three distinct readers:

| Audience | Primary concern | Canonical files |
|---|---|---|
| **Coding agents manager** | What services are running, how to operate them, what is broken, what is next | `README.md`, `docs/ops/platform-backlog.md`, `docs/ops/deployment-reference.md`, `docs/ops/mcp-endpoints.md` |
| **Robert the researcher** | What tools are available to me, how do I submit work, what is the current platform capability for my physics workflow | `research/robert/workflow.md`, `research/robert/next-actions.md` (platform-blocked items only) |
| **New agent / onboarding** | Where is everything, what are the rules, which skills exist and what do they do | `AGENTS.md`, `README.md`, `agent-skills/README.md` |

---

## Read First

- `AGENTS.md`
- `README.md`
- `ACTION_PLAN.md`
- `docs/ops/platform-backlog.md`
- `docs/ops/deployment-reference.md`
- `docs/ops/mcp-endpoints.md`
- `docs/decisions/*.md` (all ADRs)
- `agent-skills/README.md`
- `research/robert/workflow.md`
- `deployment/onyx/docker-compose.yml` (ground truth for running services)
- `deployment/onyx/litellm_config.yaml` (model routing ground truth)
- `mcp_config.yaml`
- **`docs/user-manual/USER_MANUAL.md`** (declared skill map, pipelines, daily routines, and physics tools reference — check this last, after all other files, so drift can be assessed against the actual current state)

---

## Rules

- **Do not create new files** unless no existing file can hold the information. Ask first.
- **Do not touch science claims.** `research/robert/evidence-ledger.md`, `fit-plan.md`, `validation-plan.md`, and `runs/` are read-only for this skill.
- **Only the platform-blocked items** in `research/robert/next-actions.md` are in scope — tasks that say "waiting on Ollama", "waiting on Scite key", or similar. Never add, remove, or reword science task items.
- Use `secret-config-auditor` if you encounter config files with potential secrets during the scan; do not reproduce values.
- Severity of documentation drift follows the same scale as `aisci-ops-auditor`: `Critical` / `High` / `Medium` / `Low`.
- After every scan, explicitly confirm which parts of the documentation were accurate and required no change.

---

## Scan Checklist

Work through these areas in order. For each, check whether the current documentation matches the actual file content.

### 1. Services (ground truth: `docker-compose.yml`)
- Which containers are defined?
- Does `docs/ops/deployment-reference.md` list them all correctly?
- Are pinned image versions in the compose file reflected in the docs?
- Are any containers defined but known to be non-functional?

### 2. Models (ground truth: `litellm_config.yaml`, Ollama model list)
- Which LLM and embedding models are configured vs. actually pulled?
- Does `README.md` or any ops doc claim a model is available that is not yet pulled?
- Are the embedding dimensions consistent across `litellm_config.yaml` and the RAG ADR?

### 3. MCP Endpoints (ground truth: `mcp_config.yaml`, `nginx_mcp_proxy.conf`, `docs/ops/mcp-endpoints.md`)
- Does `mcp-endpoints.md` reflect the actual proxy routes?
- Are any endpoints now tested that were previously marked Untested?
- Are any endpoints missing from the table entirely?

### 4. Agent Skills (ground truth: `agent-skills/` directory listing)
- Does `agent-skills/README.md` list all currently existing skills?
- Does `AGENTS.md` reference any skill that no longer exists?
- Are any skills present in the directory but missing from `AGENTS.md`?

### 5. Researcher Platform View (ground truth: `research/robert/workflow.md`)
- Does `workflow.md` accurately describe what tools Robert can use today?
- Are there platform capabilities now available that `workflow.md` does not mention?
- Are there platform items blocking Robert's work that should be noted
  in `next-actions.md` as a platform dependency (not a science task)?

### 6. Onboarding Clarity (`README.md`, `AGENTS.md`)
- Can a new agent read `README.md` and immediately understand how to start?
- Does `AGENTS.md` need any new rules based on patterns seen during this scan?
- Are any instructions in `AGENTS.md` now obsolete?

### 7. User Manual Drift (`docs/user-manual/USER_MANUAL.md`)

Run this section **after** completing §1–§6 so you have the full current-state picture before comparing it against the declared model.

The user manual is the authoritative description of how AiSci is *intended* to be used. It declares:
- The 15-skill map and two-pipeline model (ops + science)
- The daily routine for each session type (kickoff, platform, science, end-of-session)
- The three idea inlets and their landing zones
- The physics tools reference (`physics/src/` dependency map, current blocker, script purposes)

Check each declared section against what you found in §1–§6:

**Skill map accuracy**
- Does every skill listed in the map diagram still exist in `agent-skills/`?
- Has any new skill been added to `agent-skills/` that is not yet in the map?
- Have any skill descriptions drifted from what the actual `SKILL.md` files say?

**Pipeline flow accuracy**
- Does the ops pipeline sequence (`aisci-tech-kickoff → aisci-ops-auditor → onyx-rag-eval-manager → ...`) still reflect the correct recommended order?
- Does the science pipeline sequence still match the intended workflow?

**Daily routine accuracy**
- Does the Morning Kickoff step list match what `aisci-tech-kickoff/SKILL.md` actually instructs?
- Are the "Read First" files listed in the daily routine still the correct canonical files?

**Physics tools reference accuracy**
- Do the five script descriptions (`boson_paper_analysis.py`, `fitting_pipeline.py`, `data_loader.py`, `sympy_validation_agent.py`, `tsallis_physics_validation.py`) still accurately describe what those files do?
- Has the blocker status changed? (i.e., has `physics/data/fit_input.csv` appeared, meaning the data layer is no longer blocked?)
- Has the manuscript been moved to `research/robert/manuscript/` as recommended? If so, update the "Manuscript Location" note.

**Idea inlets accuracy**
- Are the three landing zones (`research/robert/next-actions.md`, `docs/ops/platform-backlog.md`, `research/robert/science-questions.md`) still the correct routing targets?

**Proposed adjustment protocol**
- If a drift is found: add a row to the drift report (see Workflow §2) with `Severity | Section in USER_MANUAL.md | What the manual says | What is actually true | Proposed edit`.
- Edits to the user manual follow the same approval gate as any other canonical file: present the diff, wait for confirmation, then apply.
- Do not rewrite entire chapters. Make the minimum targeted edit that makes the section accurate.
- If a new skill, service, or physics script has been added since the last manual update, add a description that matches the style of the existing entries — do not pad with speculation.

---

## DeerFlow Integration (Optional)

When the platform scan reveals service status that cannot be confirmed from
static files alone (e.g., whether Onyx is reachable, whether Ollama has models
loaded, whether LiteLLM routes are healthy), you may request a DeerFlow
deep-research pass:

1. Draft a DeerFlow task prompt that asks for:
   - Live `docker ps` output for the aisci stack
   - `ollama list` output
   - A single RAG query to Onyx to confirm the persona is responding
   - `curl` of each MCP proxy route listed in `mcp-endpoints.md`
2. Present the draft to the user for approval before submitting.
3. Use the DeerFlow output to update `docs/ops/mcp-endpoints.md` status
   cells and any open `platform-backlog.md` rows that are now confirmed done.
4. Do not use DeerFlow to make or verify science claims.

---

## Workflow

1. Read all files in **Read First** and complete **Scan Checklist §1–§6**.
2. Produce a drift report: one row per finding with
   `Severity | File | What the doc says | What is actually true | Proposed fix`.
   Separate findings by audience: Ops / Researcher / Onboarding.
3. Complete **Scan Checklist §7** (User Manual). Append any user-manual drift rows
   to the same drift report under a **User Manual** heading.
4. Present the full drift report to the user.
5. For each accepted fix: edit the target file with the minimum necessary change.
6. For each rejected fix: note it as a known drift item in `docs/ops/platform-backlog.md`.
7. If DeerFlow live verification is warranted, draft the task prompt and ask for approval.
8. After all edits, confirm which files were changed and which were accurate.
9. Close with `analysis-handoff-router`: implement remaining fixes now,
   persist to backlog, or write a next-session prompt.

---

## Output & Approval Gates

- Present the drift report before making any edits.
- Do not edit more than one canonical file without a pause for user confirmation
  when findings are Medium severity or above.
- Do not add new files without asking and naming exactly why no existing file
  can hold the content.
- Do not commit unless the user explicitly asks.
- State what was accurate and unchanged — silence on a file means it was not checked.
