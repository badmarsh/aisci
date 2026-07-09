# Decision: DeerFlow De-Vendoring Plan

**Date:** 2026-07-09
**Status:** Accepted — Q3 2026 target
**Replaces:** None
**Impacts:** `deployment/deer-flow/`, `CHANGELOG.md`, `platform-backlog.md`

## Context

`deployment/deer-flow/` contains a full vendored copy (~50K lines) of
the DeerFlow orchestration framework. The directory is listed in
`.gitignore`, making:
- CI verification of the orchestration layer impossible.
- Patch reproducibility fragile (manual `apply_local_patches.sh` required
  after every clean checkout).
- The AiSci science loop unnecessarily coupled to a heavyweight web
  application backend.

The architectural review (2026-07-09, `docs/aisci-review/gap-analysis-scorecard.md`)
classified this as Gap 2 ("Over-reliance on DeerFlow") with Priority P1.

## Decision

De-vendor DeerFlow over Q3 2026 (target: 2026-09-30). The AiSci science
loop will be migrated to the "AiSci Runtime Minimal" stack:

| Component | Current | Target |
| :--- | :--- | :--- |
| Orchestration | DeerFlow (web app) | Direct LLM SDK + `agent-skills/` |
| Tool routing | DeerFlow gateway | `mcp_config.yaml` shared proxy |
| Physics execution | DeerFlow skill call | `python physics/cli.py` |
| Frontend | DeerFlow UI | Not required for science loop |

DeerFlow may continue to run as an optional UI layer for Robert's
day-to-day chat interface, but no science workflow should depend on it
being available.

## Migration Path

1. **Phase 1 (now):** Extract all AiSci-specific skills from
   `deployment/deer-flow/skills/` and `deployment/deer-flow/agents/`
   into `agent-skills/` as vendor-neutral `SKILL.md` files.
2. **Phase 2 (2026-08):** Wire `physics/cli.py` as the canonical
   physics execution entrypoint. Remove DeerFlow skill wrappers for physics.
3. **Phase 3 (2026-09):** Confirm science loop runs end-to-end via
   `python physics/cli.py` + `mcp_config.yaml` without DeerFlow.
   Archive `deployment/deer-flow/` as `deployment/archive/deer-flow/`.

## Guardrails

- Do NOT delete `deployment/deer-flow/` until Phase 3 is verified.
- AiSci-specific patches (documented in `deployment/deer-flow/README-local-patches.md`)
  must be preserved in `docs/decisions/` before deletion.
- Onyx remains in place — only the orchestration layer is migrated.

## Acceptance Criteria

- [ ] All AiSci skills migrated to `agent-skills/`.
- [ ] `python physics/cli.py --dry-run` passes in CI.
- [ ] Science loop documented in `docs/user-manual/USER_MANUAL.md` no
      longer references DeerFlow as a required runtime.
- [ ] `deployment/deer-flow/` removed or archived.
