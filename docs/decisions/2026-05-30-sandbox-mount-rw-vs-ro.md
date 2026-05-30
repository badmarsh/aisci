# Decision: Sandbox Workspace Mount — Read-Write vs Read-Only

**Date:** 2026-05-30
**Status:** Active

## Context

The DeerFlow AIO sandbox mounts the host workspace at `/mnt/host/aisci`. This mount was
set to read-only (`:ro`) during the May 2026 deployment repair as a hardening measure to
prevent agents from accidentally modifying host files.

## Decision

The mount is set back to **read-write (`:rw`)** effective 2026-05-30
(commit `d889ad99` — *"ops: change workspace mount to rw to allow agent file generation"*).

**Reason:** Agents need write access to generate output files, save run artifacts, and
commit results back to the workspace. Read-only mode blocks the core research workflow
(fit runs, artifact saving, report generation).

## Trade-offs

| `:ro` | `:rw` |
|---|---|
| Prevents accidental host file mutation by agents | Allows agents to write run artifacts and outputs |
| Safer if an agent loops or goes rogue | Required for normal DeerFlow research operations |
| Blocks core workflow | Accepted operational risk |

## Mitigations in place

- `loop_detection` in `deployment/deer-flow/config.example.yaml` limits repeated identical
  tool calls (warn at 3, hard stop at 5 within a 20-call window).
- Agents operate under the epistemic gates defined in `AGENTS.md` — they may not promote
  findings without evidence-ledger support.
- `AGENTS.md` prohibits agents from persisting findings to canonical files without user approval.

## Revisit trigger

If agents begin modifying canonical docs without user approval, or if a runaway tool loop
is observed, revert the mount to `:ro` and route all artifact output through explicit
`write_file` tool calls with path whitelisting.
