# RAG Test Analysis Report (2026-05-30)

## Overview
This report analyzes the recent RAG (Retrieval-Augmented Generation) test sessions, focusing on the `onyx` internal documentation and physics literature corpus.

## Source Materials Analyzed
- `deployment/onyx/chat_output.txt`: Detailed chat logs regarding Onyx reindexing behavior.
- `deployment/helper/run_rag_tests.py`: The script used for automated RAG validation.
- `docs/ops/rag-evaluation-set.md`: Historical and current RAG test results.
- `docs/ops/platform-backlog.md`: Documented corpus gaps and action items.

## Key Findings: Onyx Reindexing Behavior
The chat logs in `chat_output.txt` reveal a deep dive into how Onyx handles reindexing, specifically when Contextual RAG is enabled.

### Summary of Onyx Internal Logic
- **Document-Level Incrementality**: Onyx skips documents that haven't changed (checked via `doc_updated_at` or content hash).
- **Chunk-Level Regeneration**: If a document *is* reprocessed, **all** its chunks have their contextual summaries regenerated from scratch. There is no chunk-level caching.
- **Web Connector Limitation**: Most scraped pages lack a `Last-Modified` header, causing them to be reindexed on every run.
- **Incremental Sync**: The default reindex is incremental (`from_beginning=False`), which avoids a full rebuild but still reprocesses any document flagged for update.

## RAG Test Results (Run 2026-05-30)
The recent automated tests showed several failures, categorized below:

| Question | Status | Root Cause |
|----------|--------|------------|
| Q1 (Blast-Wave) | ❌ FAIL | Khuntia/Rath PDFs missing from indexed corpus. |
| Q2 (Tsallis-Pareto) | ❌ FAIL | Literature PDFs absent/purged. |
| Q3 (OpenSearch Cmd) | ❌ FAIL | `docs/ops/` markdown files are NOT indexed. |
| Q4 (Manuscript) | ❌ FAIL | HUBY paper never existed in corpus. |
| Q5 (Evidence Ledger) | ❌ FAIL | `docs/` directory not mapped to a connector. |

## Identified Gaps
1. **Structural Gap**: The `docs/` directory (containing system documentation) is not indexed in Onyx.
2. **Literature Gap**: Key physics papers (Khuntia 2019, Rath 2020) were purged and not re-uploaded.
3. **Evaluation Gap**: The `run_rag_tests.py` script returns zero hits due to LiteLLM `BadRequestError` (missing provider prefixes like `openai/`).

## Strategic Recommendations
1. **Index System Docs**: Create a File Connector for `/home/ubuntu/aisci/docs/` and map it to a new `AiSci-System-Docs` document set.
2. **Fix LiteLLM Prefixes**: Ensure all models in `litellm_config.yaml` use explicit provider prefixes (e.g., `openai/qwen-balanced`).
3. **Automate Re-indexing Validation**: Integrate the `onyx_opensearch_cutover.py` parity check into the RAG test workflow to confirm gap-filling.
4. **Local Fallback**: Maintain `gemma2:27b` via Ollama to ensure indexing can continue when cloud quotas are exhausted.

## Next Steps
- [ ] Implement the File Connector for `docs/`.
- [ ] Re-run `upload_literature_pdfs.py` for Khuntia and Rath papers.
- [ ] Update `litellm_config.yaml` with required prefixes.
- [ ] Re-run `run_rag_tests.py` after indexing completes.
