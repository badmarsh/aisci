# Decision: Parser And RAG Baseline

Date: 2026-04-26

## Decision

Use local Unstructured as the production parser for now. Keep Docling as an experimental side parser only after the current validation workflow is stable.

Use the active Onyx contextual RAG baseline:

- Embeddings: `nomic-ai/nomic-embed-text-v1`
- Dimensions: 768
- Hybrid retrieval enabled
- Multipass/contextual RAG enabled
- Reranking enabled

## Rationale

The current Onyx stack is healthy with Unstructured. The active DB/index settings already use Nomic 768-dim embeddings and contextual RAG. Switching parsers or embedding dimensions before the evaluation set exists would add noise.

## Consequences

- Align `.env` with the active embedding model.
- Reindex once after config alignment.
- Build a 20-30 question retrieval evaluation set before further tuning.

## Status (2026-04-30)

- Unstructured parser: active ✅
- nomic-embed-text 768-dim embeddings: configured but Ollama model
  not yet pulled — open item in `docs/ops/platform-backlog.md`
- Retrieval evaluation set (20-30 questions): not yet built —
  open item in `docs/ops/platform-backlog.md`
- Consequence: no RAG tuning should proceed until both items above
  are resolved; `onyx-rag-eval-manager` enforces this gate.
