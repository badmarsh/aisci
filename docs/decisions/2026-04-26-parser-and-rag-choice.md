# Decision: Parser And RAG Baseline

Date: 2026-04-26

## Decision

Use local Unstructured as the production parser for now. Keep Docling as an experimental side parser only after the current validation workflow is stable.

At decision time, use the active Onyx contextual RAG baseline:

- Embeddings: `nomic-ai/nomic-embed-text-v1`
- Dimensions: 768
- Hybrid retrieval enabled
- Multipass/contextual RAG enabled
- Reranking enabled

## Rationale

At decision time, the Onyx stack was healthy with Unstructured. The active DB/index settings used Nomic 768-dim embeddings and contextual RAG. Switching parsers or embedding dimensions before the evaluation set existed would have added noise.

## Consequences

- Align `.env` with the active embedding model.
- Reindex once after config alignment.
- Build a 20-30 question retrieval evaluation set before further tuning.

## Status (2026-04-30)

- Unstructured parser: active ✅
- nomic-embed-text 768-dim embeddings: configured baseline at the time;
  later superseded operationally by the Alibaba/OpenSearch rebuild noted below
- Retrieval evaluation set (20-30 questions): not yet built —
  open item in `Multica Issues`
- Consequence: no RAG tuning should proceed until both items above
  are resolved; `onyx-rag-eval-manager` enforces this gate.

## Status (2026-05-02)

- Parser choice remains unchanged: local Unstructured is active.
- Embedding baseline is superseded operationally by the Alibaba/OpenSearch stack:
  `Alibaba-NLP/gte-Qwen2-1.5B-instruct`, 1536 dimensions, contextual RAG enabled.
- `deployment/helper/onyx_opensearch_cutover.py --json` reports active-index chunk parity as green for the Alibaba index; keep it as the regression gate after future reindexes.
