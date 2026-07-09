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
- **Anomaly duty:** If a fit run produces chi²/ndf > 10 on a model that previously scored below 5, or reveals a new |ρ| > 0.9 parameter correlation, you MUST append a proposed follow-up item to `research/robert/next-actions.md` under a `## 🤖 Agent-Proposed (Pending Robert Approval)` section before ending your session. Do not silently proceed.
- **Literature grounding duty:** Before proposing any new hypothesis or model modification, query Scite or Consensus MCP for at least one retrieved paper supporting or refuting the hypothesis. Record the citation in the proposed `next-actions.md` entry.

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
- Use Onyx for curated document ingestion, document sets, and source-grounded retrieval.
- Use direct MCP/API tools for task-specific literature or citation lookups when they need fresh external evidence.
- Do not assume Onyx is a universal MCP gateway unless a working endpoint is documented and tested.
- If the same external service is needed by multiple agents, document it under `docs/ops/` and route it through the shared local MCP proxy when practical.

## Autonomous Queue Management

These rules govern how agents may extend the science task queue without direct human instruction.

- Agents that complete a fit run **may** append items to `research/robert/next-actions.md` only under a dedicated `## 🤖 Agent-Proposed (Pending Robert Approval)` section. Never add items to the `## 🟢 Active` section without Robert's explicit approval.
- Agent-proposed items must include: the triggering observation (e.g., chi²/ndf value, parameter correlation), the proposed action, and at least one literature citation retrieved from Scite/Consensus supporting the rationale.
- When `evidence-ledger.md` contains a claim at `Status = Sanity checked` whose `Next Gate` criteria appear to have been met by existing `runs/` artifacts, the agent must draft a promotion proposal as a PR — not unilaterally update the ledger.
- Agents must never remove or overwrite existing `## 🟢 Active` or `## ✅ Completed` items in `next-actions.md`. Only append to `## 🤖 Agent-Proposed`.
- The `agent-skills/ledger-anomaly-detector/` skill (when available) is the canonical automation path for nightly ledger gap detection. Do not replicate its logic inline in ad-hoc scripts.
