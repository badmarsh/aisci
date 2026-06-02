---
name: researcher-docs-manager
description: Maintain canonical AiSci documentation by ensuring a rigorous separation between scientific claims and platform infrastructure, optimized for the researcher's workflow.
---

# Researcher Docs Manager

Use this when creating or updating project documentation to ensure it remains a high-signal "Research Dashboard" rather than a technical log.

## Documentation Principles

1.  **Separation of Concerns:** Keep physics theory, results, and workflows in `research/robert/`. Keep platform, deployment, and technical infrastructure details in `docs/ops/`.
2.  **Evidence-Led:** Do not promote claims beyond "Sanity checked" in the `evidence-ledger.md` without ledger-supported evidence (equations, data, or reproducible outputs).
3.  **Researcher-First UX:** The root `README.md` must be a high-level dashboard. Move technical "noise" (ports, docker commands, logs) to `docs/ops/deployment-reference.md`.
4.  **Explicit Terminology:** Always distinguish between Bose-Einstein distributions and Boltzmann/Juttner approximations. Use precise HEP terminology.

## Read First

- `README.md` & `AGENTS.md`
- `research/robert/evidence-ledger.md` (Source of Truth for science)
- `research/robert/next-actions.md` (Active task queue)
- Multica Issues (Infrastructure queue — run `multica issue list`)

## Operational Tasks

- **Science Updates:** When data (like $p_T$ tables) arrives or findings change, update the `evidence-ledger.md` and `next-actions.md`.
- **Infrastructure Sync:** Create or update Multica Issues when platform milestones or blockers are identified.
- **Decision Logging:** Record durable architectural or methodological choices in `docs/decisions/`.
- **Archive Drift:** Move implemented or superseded details to `docs/archive/` to keep active docs concise.

## Science Integrity Rules

- **No physical interpretation** of fit parameters without chi2/ndf, covariance, and residuals.
- **Mandatory baselines:** Always compare results against Tsallis and Blast-Wave models.
- **Flag Assumptions:** Explicitly document massless or pseudorapidity assumptions in any analysis.

## Workflow

1.  Analyze the current request: Is it Science, Infrastructure, or Documentation?
2.  Identify the canonical file(s) that should hold the information.
3.  Draft changes that prioritize the "Signal-to-Noise" ratio for a physicist.
4.  Log any identified technical issues into the relevant backlog, but do not fix them unless explicitly directed.
5.  Offer the user "Follow-Through" paths (Implement, Persist, or Handoff).
