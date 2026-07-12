# Project Agent Instructions

These instructions apply to any AI coding or research agent working in this repository. They are intentionally generic and vendor-neutral. Do not add model-, IDE-, or CLI-specific rule files unless the user explicitly asks for them.

## Source Of Truth

- `research/robert/evidence-ledger.md` is the canonical science claim-status file.
- `research/robert/next-actions.md` is the canonical science task queue.
- `ACTION_PLAN.md` is high-level project tracking only.
- `docs/decisions/` records durable architecture and process decisions.
- `docs/ops/` is for platform, deployment, MCP, Docker, model, and security notes.
- `research/robert/` is for science-facing questions, evidence, validation criteria, fits, reports, and reproducible runs.
- `docs/archive/` is historical context only; do not treat archive files as current status.
- `docs/user-manual/USER_MANUAL.md` is the skill map, pipeline structure, and daily routine reference for all agents and Robert. Read it when onboarding or when unsure which skill applies to a task.
- GitHub Issues and Pull Requests are the execution and review layer for accepted work. They do not replace canonical docs for current state, decisions, science evidence, or runbooks.

## Science Rules

- Treat local scripts as sanity checks unless assumptions, input data, manuscript references, and outputs are recorded.
- Do not promote claims beyond `Sanity checked` without evidence-ledger support.
- Do not infer causality or root cause from suggestive fit behavior alone.
- Keep Bose-Einstein versus Boltzmann/Juttner wording explicit.
- Do not interpret fit parameters physically until chi2/ndf, covariance, correlations, residuals, fit-range sensitivity, and baseline comparisons exist.
- Compare against literature-matched Tsallis/Tsallis-Pareto and Blast-Wave baselines before making novelty or model-quality claims.

## File Hygiene

- Do not create empty placeholder run files.
- Put real run artifacts under `research/robert/runs/YYYY-MM-DD-*`.
- For blocked runs, keep requirements and status in the run `README.md` until artifacts exist.
- Keep platform implementation details out of science files.
- Keep science claims and fit conclusions out of `docs/ops/`.
- Preserve unrelated user changes in the working tree.
- Put temporary helper scripts in `deployment/helper/`.
- Do not create new backlog, audit, or status markdown files when a GitHub Issue plus an update to an existing canonical doc will do.

## GitHub Workflow

- Use GitHub Issues for accepted actionable work: platform tasks, docs drift, security remediation, and follow-up implementation.
- Use Pull Requests for reviewable code/docs changes and keep the PR body focused on what changed, why, verification, and safety constraints.
- Keep durable facts in repo docs: `docs/ops/` for platform state, `docs/decisions/` for stable decisions, and `research/robert/` for science state.
- When an Issue and a canonical doc disagree, inspect the recent PR/Issue history, then update the canonical file or correct the Issue rather than creating a new parallel note.
- Do not paste secret values into Issues, PRs, docs, commit messages, or chat. Report only file paths, variable names, and commit SHAs.

## Analysis Follow-Through

- After any analysis, review, audit, or research iteration, do not automatically write all suggestions into canonical project files. Offer the user three follow-through paths:
  - Implement selected findings now, respecting any user exclusions.
  - Write selected findings into the specific document or documents where they belong.
  - Create a concise prompt for a fresh agent/session to implement selected findings later.
- When offering to persist findings, name the exact target file or files and briefly map what would go where. For example: "I can write the platform tasks into `docs/ops/platform-backlog.md` and the durable rationale into `docs/ops/<existing-note>.md`."
- If the analysis includes secondary notes that should be logged separately, name those target files too rather than referring to a generic suggestions document.
- Only promote suggestions into canonical trackers after the user agrees they are accepted tasks, decisions, or evidence updates.
- Before storing findings anywhere, read the target file and avoid duplicates. Merge with existing entries, update statuses, or add evidence links rather than creating parallel copies.
- Do not create a new markdown report by default. Prefer updating existing canonical files with the smallest useful durable note.
- Create a new dated analysis file only when the analysis is substantial, likely to be reread as a standalone artifact, and cannot be represented clearly as backlog rows, evidence-ledger entries, next actions, or a short update to an existing ops note.
- If a new analysis file is justified, explain why it is justified and ask before creating it. Also identify the canonical tracker updates that should accompany it.
- Store platform, deployment, MCP, model, Docker, security, and tooling findings in `docs/ops/`, with actionable items added or updated in `docs/ops/platform-backlog.md`.
- For accepted active platform work, prefer creating or updating a GitHub Issue and linking the relevant canonical doc instead of expanding `docs/ops/platform-backlog.md` with long operational history.
- Store durable architecture or process decisions in `docs/decisions/` only when the decision is stable enough to guide future work.
- Store science-facing questions, evidence states, validation gates, and run tasks under `research/robert/`, using `research/robert/evidence-ledger.md` and `research/robert/next-actions.md` as the canonical files.
- Keep `ACTION_PLAN.md` high level; do not duplicate detailed backlog rows there.
- If the user asks only for analysis and not edits, do not persist suggestions unless asked. Report the recommended storage location and offer either targeted persistence, immediate implementation, or a handoff prompt.

## Reusable Agent Skills

- Vendor-neutral workflow skills live under `agent-skills/`.
- When a user request clearly matches one of those skills, read only that skill's `SKILL.md` plus any directly relevant project files.
- These skills are plain Markdown guides for any capable coding agent, not a model-specific or CLI-specific mechanism.
- Prefer improving these shared skills over adding model-, IDE-, or vendor-specific instruction files.
- Use `agent-skills/git-worktree-guard/SKILL.md` for git history context, worktree safety, and commit hygiene when coding or changing docs.

## MCP And Tooling

- Prefer shared project-level MCP/tool configuration over IDE-specific duplication.
- Keep credentials out of git and out of committed MCP config files.
- Use direct MCP/API tools for task-specific literature or citation lookups when they need fresh external evidence.
- If the same external service is needed by multiple agents, document it under `docs/ops/` and route it through the shared local MCP proxy when practical.

## General Practices

- Always verify that the application and its services are running successfully after finishing an implementation, so the user doesn't have to discover errors themselves.
- **Global Mitigation Rule:** When fixing an issue, catching a hallucination, or updating a theoretical conclusion (e.g., invalidating a model approximation), agents MUST verify and apply the fix across the entire repository. This includes updating tests, data files, evidence ledgers, run scripts, and UI tracking. Do not limit the fix to the single isolated source file where the issue was first found.
- **Complete Reading & Verification:** Agents MUST read files, diffs, commit logs, and terminal outputs thoroughly to the very end. Do not prematurely stop reading after finding an initial match or familiar pattern at the top of an output. When analyzing branches, PRs, or large logs, explicitly review the full list of changed files and the entire commit message before drawing conclusions or taking action.

## Mandatory Intake Stage: Principle Violation & Verification Analysis

Before executing any large task, agents must perform a repository health check against established principles:
- **Analyze Redundancy:** Check if the user request implies creating a new tracking document or "Megaprompt". If so, reject the creation of a new file and instead route the data into existing canonical files (`next-actions.md`, `evidence-ledger.md`, `platform-backlog.md`).
- **Verify Before Deletion:** Before removing any outdated Megaprompt, tracking document, or task list, explicitly verify (by checking the target files in the codebase) whether the most valuable/critical items in those documents were actually implemented. Any uncompleted actionable items must be migrated to the canonical queues.
- **Check for Outdated State:** Quickly scan the root for redundant files or orphaned documentation that violates the single-source-of-truth rule. Recommend their cleanup (following the verification step above).
- **Ensure Canonical Alignment:** Verify that any UI or code wiring explicitly respects the exact capitalization and structure of canonical documents.

## Environment & Execution Protocols

- **Windows/WSL Boundary:** When operating in a Windows environment but the workspace is a WSL UNC path (e.g., `\\wsl.localhost\Ubuntu\...`), avoid running Node/NPM or Python commands directly in Windows `pwsh`. Wrap execution in WSL bash: `wsl bash -c "cd /home/ubuntu/aisci && <command>"`.
- **Python Virtual Environment Isolation:** The Python environment is nested in `libs/physics-core/.venv`, not the project root. Agents must explicitly source `libs/physics-core/.venv/bin/activate` or use `libs/physics-core/.venv/bin/python` to ensure dependencies like `iminuit` and `pytest` are correctly resolved.

## Knowledge Capture & Tagging Taxonomy

When creating GitHub Issues to capture research, decisions, or bugs, always structure them properly:
- **Use Templates**: Utilize the templates in `.github/ISSUE_TEMPLATE/` (`research.md`, `decision.md`, `bug.md`).
- **Use Domain Tags**: Apply relevant domain labels (e.g., `physics`, `fitting`).
- **Use Source Tags**: Apply source labels if the info came from an external tool or agent (e.g., `from-perplexity`, `from-mcp`, `from-claude-code`).
- **Link the Graph**: Proactively link related issues using `AIS-XXX` notation to build a searchable knowledge graph.
- **Keep GitHub Clean**: In PR descriptions, do not duplicate context. Provide a high-level summary and link to the relevant Issue for the full "why" and "how".

## Temporary & Scratch Files

- **No Scratch Files Allowed**: No temporary or scratch files (e.g., scratch scripts, debug logs, one-off plotting scripts, local db copies, or screenshots) should ever be saved to the repository working directory without explicit user allowance.
