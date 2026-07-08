---
name: researcher-docs-manager
description: Reconcile active docs, separate science from platform infrastructure, and archive historical detail.
---

# Researcher Docs Manager

Use this when creating, updating, or curating project documentation to ensure it remains a high-signal "Research Dashboard" rather than a technical log, and to clean up stale or duplicated notes.

## Read First
- `AGENTS.md`
- `README.md`
- `ACTION_PLAN.md`
- `research/robert/evidence-ledger.md` (Source of Truth for science)
- `research/robert/next-actions.md` (Active task queue)
- `docs/ops/platform-backlog.md` (concise infrastructure state)
- Open GitHub Issues (active platform/security/docs-drift work)

## Rules
- **Separation of Concerns:** Keep physics theory and results in `research/robert/`. Keep platform and deployment details in `docs/ops/`. Do not mix them.
- **Evidence-Led:** Do not promote claims beyond "Sanity checked" without ledger-supported evidence. No physical interpretation of fit parameters without chi2/ndf, covariance, and residuals.
- **Terminology:** Always distinguish between Bose-Einstein distributions and Boltzmann/Juttner approximations. Flag massless/pseudorapidity assumptions.
- **Curating Hygiene:** Keep active docs short and current. Prefer editing existing active docs over creating new files. Use GitHub Issues for active work history instead of growing markdown backlogs.
- **Archiving:** Move historical detail to `docs/archive/` only when it is no longer current. Preserve a durable one-sentence summary in the active doc. Add a legacy note when archiving. Do not delete scientific evidence history.

## Workflow
1. Analyze the request and active docs: Is it Science, Infrastructure, or Documentation? Are there stale or duplicated items?
2. Compare active docs against current repo state and git history.
3. For implemented items, update status or compress the note to a durable summary.
4. For stale detail, keep the crucial sentence in the active doc and archive the rest.
5. Update canonical trackers (`evidence-ledger.md`, `next-actions.md`, or compact `platform-backlog.md` state) appropriately. Put accepted active platform follow-up in GitHub Issues.
6. Record durable architectural choices in `docs/decisions/`.

## Output & Approval Gates
- Ask before creating a new Markdown file. A new file is justified only if an existing canonical doc cannot hold the information clearly.
- Offer the user "Follow-Through" paths (Implement, Persist, or Handoff) for identified technical issues rather than fixing them silently.
