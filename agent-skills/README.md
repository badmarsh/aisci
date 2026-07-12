# Agent Skills

This folder contains vendor-neutral workflow skills for agents working in this repository.
They are plain Markdown guides, not tied to any specific model, IDE, or CLI.

Use these skills by reading only the relevant `SKILL.md` for the current task. Do not bulk-load every skill unless the user asks for a broad process review.

## Skill Structure
All skills follow the `TEMPLATE.md` schema:
1. `## Read First`: Lists `AGENTS.md` and required canonical context.
2. `## Rules`: Hard boundaries and constraints.
3. `## Workflow`: Step-by-step execution guides.
4. `## Output & Approval Gates`: When to ask for permission and how to shape output.

## Available Skills
| Skill | Purpose | Status | Last Use |
|-------|---------|--------|----------|
| `academic-stress-tester` | A fail-closed workflow to extract literal quotes from drafts, run them through a strict verification gate, and aggressively stress-test logic against the evidence ledger. | Active | Unknown |
| `aisci-living-docs` | Scan the entire codebase to understand the current real state of AiSci, then update documentation for three audiences. | Active | Unknown |
| `aisci-ops-auditor` | Audit the technical architecture and operations of AiSci. | Active | Unknown |
| `aisci-tech-kickoff` | Start a technical work session in /home/ubuntu/aisci by reading current project context. | Active | Unknown |
| `analysis-handoff-router` | Route findings after an analysis, audit, review, or research pass. | Active | Unknown |
| `fit-anomaly-resolution` | Playbook for translating mathematical fit anomalies into physically sound model modifications. | Active | Unknown |
| `git-worktree-guard` | Use git safely for project context and change hygiene. | Active | Unknown |
| `hitl-checkpoint-manager` | Intercept high-uncertainty decisions and format structured prompts to force human alignment. | Active | Unknown |
| `hypothesis-generator` | Brainstorm physically sound extensions to the Tsallis-Pareto and Bose-Einstein models based on literature gaps. | Active | Unknown |
| `latex-poster-builder` | End-to-end LaTeX poster generation pipeline. | Active | Unknown |
| `mcp-integration-planner` | Plan shared MCP or direct API integrations for research and citation tools. | Active | Unknown |
| `physics-auditor` | Act as a strict gatekeeper that rejects fit results violating boundary conditions or fundamental physical constraints. | Active | Unknown |
| `platform-backlog-manager` | Manage actionable platform, deployment, MCP, Docker, model, security, and tooling tasks in docs/ops/platform-backlog.md. | Active | Unknown |
| `reproducible-physics-runner` | Run or prepare Robert physics validation scripts, fits, plots, and sanity checks. | Active | Unknown |
| `researcher-docs-manager` | Reconcile active docs, separate science from platform infrastructure, and archive historical detail. | Active | Unknown |
| `science-ledger-manager` | Manage Robert science-facing claim status, evidence states, validation gates, and next actions. | Active | Referenced in trackers |
| `science-peer-reviewer` | Act as a hostile academic peer reviewer. | Active | Unknown |
| `science-report-writer` | Draft or revise referee reports, science summaries, validation reports, and response notes. | Active | Unknown |
| `science-source-curator` | Manage science source materials such as Robert's manuscript PDF, literature PDFs, arXiv/INSPIRE/HEPData references. | Active | Unknown |
| `secret-config-auditor` | Review repository config, deployment files, docs, and runtime assumptions for committed secrets. | Active | Unknown |
| `vendored-runtime-maintainer` | Work safely in vendored or nested runtime trees. | Active | Unknown |

## Common Rules

- Follow `AGENTS.md` first.
- Preserve unrelated user changes.
- Do not print secrets.
- Prefer existing canonical files over creating new Markdown files.
- Ask before promoting analysis suggestions into accepted task, decision, or evidence trackers.
