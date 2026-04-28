# Decision: System Boundaries For AiSci

Date: 2026-04-26

## Decision

Use three clear layers:

- Onyx is the curated evidence and private RAG layer.
- DeerFlow is the orchestration and execution layer.
- The repository is the durable scientific record and source of reproducible scripts, runs, and markdown outputs.

## Rationale

Onyx is strongest when it owns ingestion, document sets, citation-grounded retrieval, and controlled knowledge. DeerFlow is strongest when it coordinates tools, runs sandboxed code, and produces artifacts. Robert's scientific workflow should not depend on the internal layout of either platform.

## Consequences

- Platform notes live under `docs/ops/`.
- Architecture choices live under `docs/decisions/`.
- Robert's workflow lives under `research/robert/`.
- Run outputs live under dated `research/robert/runs/` folders.
- Tool names can appear in execution notes, but science files should describe the method in tool-agnostic language first.

