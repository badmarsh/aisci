# Platform Backlog

| Task | Phase | Priority | Notes |
|---|---|---|---|
| Fix Transformer Bug: Patch transformer.py to handle missing/nested document_id in Vespa chunks. | Phase 2 | High | Blocking OpenSearch migration |
| Model Dimension Alignment: Ensure OpenSearch index is created with 768 dimensions instead of 384. | Phase 2 | High | OpenSearch migration |
| Reconcile Chunk Parity: Identify why OpenSearch has fewer chunks than Vespa. | Phase 2 | High | OpenSearch migration |
| Enable OpenSearch Retrieval: Set enable_opensearch_retrieval=true in opensearch_tenant_migration_record. | Phase 2 | High | Pending chunk parity |
| Decommission Vespa: Stop onyx-index-1 after OpenSearch is verified stable. | Phase 2 | Medium | Cleanup |
| Test current PDF ingestion path with Robert's boson paper after next clean restart | Phase 2 | Medium | Parser Baseline |
| Revisit Docling only as an experimental side parser after validation workflow is stable | Phase 2 | Low | Parser Baseline |
| Pull/Configure nomic-embed-text:latest | Phase 2 | Medium | Ollama GPU Models |
| Pull/Configure BAAI/bge-reranker-v2-m3 | Phase 2 | Medium | Ollama GPU Models |
| Pull/Configure qwen2-vl:latest (or check qwen2.5-vl) | Phase 2 | Medium | Ollama GPU Models |
| Pull/Configure gemma2:27b or qwen2.5:32b | Phase 2 | Medium | Ollama GPU Models |
| Confirm IMAGE_ANALYSIS_ENABLED=true + IMAGE_MODEL_NAME=qwen2-vl:latest in .env | Phase 2 | Medium | Visual RAG |
| Test visual RAG: upload paper PDF -> ask about Figure 5 | Phase 2 | Medium | Visual RAG |
| Configure Onyx to extract and index figure captions separately | Phase 2 | Medium | Visual RAG |
| Make Physics Validation Mode the real primary Onyx persona | Phase 2 | High | Persona |
| Attach Physics document sets: Robert draft, HEP references, validation methods | Phase 2 | High | Persona |
| Attach tools: internal search, read file, code interpreter/Python, open URL, Scite, Consensus | Phase 2 | High | Persona |
| System prompt: zero-hallucination, cite chunks only, flag unverified claims | Phase 2 | High | Persona |
| Keep web search disabled by default for strict validation; enable only for literature scouting | Phase 2 | Medium | Persona |
| Add Consensus API key to nginx_mcp_proxy.conf | Phase 3 | High | Consensus MCP |
| Test Consensus: search for papers on Bose-Einstein distributions in pp collisions | Phase 3 | Medium | Consensus MCP |
| Integrate Consensus into deer-flow as a research tool | Phase 3 | Medium | Consensus MCP |
| Integrate Consensus into Onyx as a connector or tool call | Phase 3 | Medium | Consensus MCP |
| Add Scite API key to nginx_mcp_proxy.conf | Phase 3 | High | Scite MCP |
| Test Scite: validate citations in Robert's paper | Phase 3 | Medium | Scite MCP |
| Use Scite to check if cited papers support or contradict the claims | Phase 3 | Medium | Scite MCP |
