---
name: aisci-ops-auditor
description: Audit the technical architecture and operations of AiSci, including FastAPI, React, Vite, models, paths, deployment docs, and security-sensitive config. Use for full structured audits with a findings table output — not for single-task session kickoff.
---

# AiSci Ops Auditor

Use this for architecture, platform, or operations analysis.

## Read First

- `AGENTS.md`
- `README.md`
- `ACTION_PLAN.md`
- `docs/README.md`
- `docs/ops/platform-backlog.md`
- Relevant `docs/ops/*.md`
- `docs/decisions/*.md`
- Relevant files under `deployment/aisci-dashboard/`

## Rules

- Scope is limited to platform and operations. Do not modify science files (`research/robert/`) unless the finding is execution-provenance only.
- Use `secret-config-auditor` for deep secret scanning; do not reproduce secret values inline.
- Do not recommend destructive operations (container deletion, volume wipes) without explicit user approval.
- Flag documentation drift between `README.md`, `ACTION_PLAN.md`, `docs/ops/`, and deployment files as a separate finding category.
- Severity levels are: `Critical` (data loss / secret exposure risk), `High` (service broken), `Medium` (degraded functionality), `Low` (drift / tech debt).

## Workflow

1. Read `AGENTS.md` and the canonical ops files listed in **Read First**.
2. Inspect relevant deployment files under `deployment/aisci-dashboard/`.
3. Cross-reference Ignition API routes and Vite configuration for path and model drift.
4. Identify each finding with: severity, evidence file path and line where possible, impact, and suggested next action.
5. Classify each action as: safe to implement now, needs user approval, or out of scope (refer to `secret-config-auditor`).
6. Offer three continuations: implement safe actions now, persist findings to `docs/ops/platform-backlog.md`, or prepare a next-session prompt.

## Output & Approval Gates

- Produce a findings table with columns: Severity · Finding · Evidence Path · Impact · Suggested Action · Approval Required.
- Do not implement `Critical` or destructive actions without explicit user confirmation per action.
- After listing findings, invoke `analysis-handoff-router` behavior: offer implementation, targeted persistence, or a next-session prompt.
