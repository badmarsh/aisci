# ADR 2026-06-05: webapp/ replaces deployment/hep-physics/

**Date:** 2026-06-05  
**Status:** Accepted  
**Deciders:** badmarsh/aisci maintainers

## Context

The repository previously referenced a `deployment/hep-physics/` directory containing a Next.js API for the HEP physics frontend. This directory was never fully implemented and does not exist in the repository. Multiple documentation files, CI workflow comments, and dependency scanning scopes referenced it as if it were active.

A new `webapp/` module has been introduced as a v0 Next.js draft to serve the HEP physics frontend, replacing the planned-but-never-built `deployment/hep-physics/`.

## Decision

- **`deployment/hep-physics/`** is formally deprecated and considered non-existent. All references to it in documentation, CI, and dependency scanning are to be removed or updated.
- **`webapp/`** is the official replacement and the canonical location for the HEP physics Next.js frontend going forward.
- Any app/api/ route logic that was planned for `deployment/hep-physics/app/api/` should be implemented under `webapp/app/api/` instead.

## Consequences

- Removes confusion caused by ghost references to a non-existent directory.
- `webapp/` needs tests (vitest or Playwright) — currently has 0 coverage.
- `README.md` to be updated with a "Webapp / Frontend" section linking to `webapp/README.md`.
- A GitHub Actions workflow for `webapp/` CI should be added once the v0 shell is stable.
