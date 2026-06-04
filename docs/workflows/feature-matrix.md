# Feature Matrix

**Purpose:** Comprehensive list of all platform features with testability status, priority, and coverage information.

---

## Overview

This matrix tracks all features across Onyx, DeerFlow, and Physics Pipeline with their testing status.

**Legend:**
- ✅ **Tested** - Has automated tests
- 🔄 **Partial** - Some tests exist
- ❌ **Untested** - No automated tests
- 🚫 **Not Testable** - Requires manual verification

---

## Onyx Features

### Document Ingestion

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| File upload | Upload PDF/DOCX/TXT files | ✅ | ❌ Untested | P0 | 0% |
| GitHub connector | Index GitHub repositories | ✅ | ❌ Untested | P1 | 0% |
| Web connector | Scrape web pages | ✅ | ❌ Untested | P1 | 0% |
| API ingestion | Ingest via REST API | ✅ | ❌ Untested | P1 | 0% |
| Document parsing | Extract text from documents | ✅ | ❌ Untested | P0 | 0% |
| Metadata extraction | Extract title, author, date | ✅ | ❌ Untested | P1 | 0% |
| Image OCR | Extract text from images | ✅ | ❌ Untested | P2 | 0% |

### Chunking & Embedding

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| Semantic chunking | Split by meaning | ✅ | ❌ Untested | P0 | 0% |
| Chunk overlap | Preserve context | ✅ | ❌ Untested | P0 | 0% |
| Embedding generation | Generate 1536-dim vectors | ✅ | ❌ Untested | P0 | 0% |
| Batch embedding | Process multiple chunks | ✅ | ❌ Untested | P1 | 0% |
| Embedding caching | Cache by content hash | ✅ | ❌ Untested | P2 | 0% |

### Indexing

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| OpenSearch indexing | Index chunks in OpenSearch | ✅ | ❌ Untested | P0 | 0% |
| Bulk operations | Batch index/update/delete | ✅ | ❌ Untested | P0 | 0% |
| Index locking | Prevent concurrent writes | ✅ | ❌ Untested | P1 | 0% |
| Chunk count validation | Verify chunk counts | ✅ | ❌ Untested | P1 | 0% |
| ACL generation | Generate access control lists | ✅ | ❌ Untested | P0 | 0% |
| Metadata filtering | Filter by metadata | ✅ | ❌ Untested | P1 | 0% |

### Search

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| Hybrid search | Semantic + keyword | ✅ | ❌ Untested | P0 | 0% |
| Semantic search | Vector similarity only | ✅ | ❌ Untested | P1 | 0% |
| Keyword search | BM25 only | ✅ | ❌ Untested | P1 | 0% |
| Result ranking | Score and rank results | ✅ | ❌ Untested | P0 | 0% |
| Persona filtering | Filter by persona | ✅ | ❌ Untested | P0 | 0% |
| Document set filtering | Filter by doc set | ✅ | ❌ Untested | P1 | 0% |
| ACL filtering | Filter by permissions | ✅ | ❌ Untested | P0 | 0% |
| Date range filtering | Filter by date | ✅ | ❌ Untested | P2 | 0% |

### RAG Generation

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| Context assembly | Prepare LLM context | ✅ | 🔄 Partial | P0 | 20% |
| Citation tracking | Track source citations | ✅ | 🔄 Partial | P1 | 20% |
| Streaming responses | Stream LLM output | ✅ | ❌ Untested | P1 | 0% |
| Model routing | Route to best model | ✅ | ❌ Untested | P0 | 0% |
| Fallback handling | Fallback on quota | ✅ | ❌ Untested | P0 | 0% |
| Error recovery | Retry on failure | ✅ | ❌ Untested | P1 | 0% |

### Personas

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| Persona creation | Create new personas | ✅ | ❌ Untested | P1 | 0% |
| Tool assignment | Assign tools to persona | ✅ | ❌ Untested | P1 | 0% |
| Doc set assignment | Assign doc sets | ✅ | ❌ Untested | P1 | 0% |
| Prompt customization | Custom system prompts | ✅ | ❌ Untested | P1 | 0% |
| Model override | Override default model | ✅ | ❌ Untested | P2 | 0% |

### Connectors

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| Connector CRUD | Create/read/update/delete | ✅ | ❌ Untested | P0 | 0% |
| Credential pairing | Pair with credentials | ✅ | ❌ Untested | P1 | 0% |
| Indexing triggers | Trigger indexing | ✅ | ❌ Untested | P0 | 0% |
| Scheduling | Schedule periodic runs | ✅ | ❌ Untested | P1 | 0% |
| Pruning | Remove old documents | ✅ | ❌ Untested | P1 | 0% |
| Error handling | Handle connector errors | ✅ | ❌ Untested | P1 | 0% |

---

## DeerFlow Features

### Agent Runtime

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| Agent creation | Create new agents | ✅ | ✅ Tested | P0 | 80% |
| Task execution | Execute agent tasks | ✅ | ✅ Tested | P0 | 80% |
| State management | Manage agent state | ✅ | ✅ Tested | P0 | 75% |
| Turn limiting | Limit max turns | ✅ | ✅ Tested | P1 | 70% |
| Timeout handling | Handle timeouts | ✅ | ✅ Tested | P1 | 70% |
| Error recovery | Recover from errors | ✅ | ✅ Tested | P1 | 65% |

### Tool Execution

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| MCP tool calls | Call MCP tools | ✅ | ✅ Tested | P0 | 75% |
| Tool discovery | Discover available tools | ✅ | ✅ Tested | P1 | 70% |
| Tool validation | Validate tool arguments | ✅ | ✅ Tested | P1 | 65% |
| Result formatting | Format tool results | ✅ | ✅ Tested | P1 | 60% |
| Error handling | Handle tool errors | ✅ | ✅ Tested | P1 | 70% |
| Timeout handling | Handle tool timeouts | ✅ | ✅ Tested | P1 | 65% |

### MCP Integration

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| HTTP MCP servers | Connect to HTTP servers | ✅ | ✅ Tested | P0 | 70% |
| Stdio MCP servers | Connect to stdio servers | ✅ | ✅ Tested | P0 | 70% |
| OAuth handling | Handle OAuth tokens | ✅ | ✅ Tested | P1 | 60% |
| Token refresh | Refresh expired tokens | ✅ | 🔄 Partial | P1 | 40% |
| Cache invalidation | Invalidate tool cache | ✅ | ✅ Tested | P2 | 55% |
| Error propagation | Propagate MCP errors | ✅ | ✅ Tested | P1 | 65% |

### Sandbox Execution

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| Command execution | Execute bash commands | ✅ | ✅ Tested | P0 | 80% |
| File operations | Read/write files | ✅ | ✅ Tested | P0 | 75% |
| Workspace mounting | Mount host workspace | ✅ | ✅ Tested | P0 | 70% |
| Permission handling | Handle file permissions | ✅ | ✅ Tested | P1 | 65% |
| Path validation | Validate file paths | ✅ | ✅ Tested | P0 | 80% |
| Traversal prevention | Prevent path traversal | ✅ | ✅ Tested | P0 | 85% |
| Resource limits | Enforce CPU/memory limits | ✅ | 🔄 Partial | P1 | 50% |

### Subagent Orchestration

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| Subagent spawning | Spawn subagents | ✅ | ✅ Tested | P0 | 75% |
| Concurrency control | Limit concurrent agents | ✅ | ✅ Tested | P1 | 70% |
| State merging | Merge subagent state | ✅ | ✅ Tested | P1 | 65% |
| Error isolation | Isolate subagent errors | ✅ | ✅ Tested | P1 | 60% |
| Result collection | Collect subagent results | ✅ | ✅ Tested | P0 | 70% |

### Memory System

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| Memory extraction | Extract facts | ✅ | ✅ Tested | P1 | 65% |
| Memory storage | Store in vector DB | ✅ | ✅ Tested | P1 | 60% |
| Memory retrieval | Retrieve relevant facts | ✅ | ✅ Tested | P1 | 65% |
| Memory injection | Inject into context | ✅ | ✅ Tested | P1 | 60% |
| User isolation | Isolate user memories | ✅ | ✅ Tested | P0 | 75% |

### State Persistence

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| State serialization | Serialize agent state | ✅ | ✅ Tested | P0 | 80% |
| State storage | Store in database | ✅ | ✅ Tested | P0 | 75% |
| State recovery | Recover from checkpoint | ✅ | ✅ Tested | P1 | 70% |
| Run persistence | Persist run metadata | ✅ | ✅ Tested | P0 | 75% |

---

## Physics Pipeline Features

### Data Loading

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| HEPData fetch | Fetch from API | ✅ | ✅ Tested | P0 | 70% |
| Data parsing | Parse JSON response | ✅ | ✅ Tested | P0 | 75% |
| Validation gates | Validate data format | ✅ | ✅ Tested | P0 | 65% |
| Error handling | Handle API errors | ✅ | ✅ Tested | P1 | 60% |
| Timeout handling | Handle timeouts | ✅ | ✅ Tested | P1 | 55% |
| CSV export | Export to CSV | ✅ | ✅ Tested | P1 | 70% |

### Model Fitting

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| Jüttner model | Fit Jüttner distribution | ✅ | ✅ Tested | P0 | 60% |
| Bose-Einstein model | Fit B-E distribution | ✅ | ✅ Tested | P0 | 60% |
| Tsallis model | Fit Tsallis distribution | ✅ | ✅ Tested | P0 | 60% |
| Blast-Wave model | Fit Blast-Wave | ✅ | ✅ Tested | P0 | 60% |
| Parameter bounds | Enforce physical bounds | ✅ | ✅ Tested | P1 | 55% |
| Convergence check | Check fit convergence | ✅ | ✅ Tested | P1 | 65% |
| Error estimation | Estimate parameter errors | ✅ | ✅ Tested | P0 | 70% |
| Correlation matrix | Compute correlations | ✅ | ✅ Tested | P1 | 60% |

### Quality Assessment

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| Chi-squared calc | Calculate chi² | ✅ | ✅ Tested | P0 | 80% |
| AIC calculation | Calculate AIC | ✅ | ✅ Tested | P0 | 75% |
| BIC calculation | Calculate BIC | ✅ | ✅ Tested | P0 | 75% |
| Quality flags | Flag poor fits | ✅ | ✅ Tested | P0 | 70% |
| Model ranking | Rank by AIC/BIC | ✅ | ✅ Tested | P1 | 65% |

### Diagnostics

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| Residual calculation | Calculate residuals | ✅ | ✅ Tested | P1 | 70% |
| Pull calculation | Calculate pulls | ✅ | ✅ Tested | P1 | 70% |
| Diagnostic plots | Generate 4-panel plots | ✅ | 🔄 Partial | P2 | 30% |
| CSV export | Export diagnostics | ✅ | ✅ Tested | P1 | 65% |

### Validation

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| Symbolic validation | SymPy checks | ✅ | ✅ Tested | P1 | 60% |
| Literature comparison | Compare to baselines | ✅ | 🔄 Partial | P1 | 40% |
| Ledger updates | Update evidence ledger | ✅ | ❌ Untested | P1 | 0% |

---

## Integration Features

| Feature | Description | Testable | Status | Priority | Coverage |
|---------|-------------|----------|--------|----------|----------|
| DeerFlow → Onyx search | Agent searches Onyx | ✅ | ❌ Untested | P0 | 0% |
| Physics → Onyx literature | Pipeline queries lit | ✅ | ❌ Untested | P1 | 0% |
| Full research workflow | End-to-end workflow | ✅ | ❌ Untested | P1 | 0% |
| MCP proxy routing | Route MCP calls | ✅ | ❌ Untested | P0 | 0% |
| OAuth token handling | Handle OAuth tokens | ✅ | 🔄 Partial | P1 | 30% |

---

## Summary Statistics

### By Component

| Component | Total Features | Tested | Partial | Untested | Coverage |
|-----------|---------------|--------|---------|----------|----------|
| Onyx | 52 | 0 | 2 | 50 | 4% |
| DeerFlow | 35 | 30 | 3 | 2 | 82% |
| Physics | 24 | 19 | 2 | 3 | 75% |
| Integration | 5 | 0 | 1 | 4 | 6% |
| **Total** | **116** | **49** | **8** | **59** | **46%** |

### By Priority

| Priority | Total | Tested | Untested | Coverage |
|----------|-------|--------|----------|----------|
| P0 | 42 | 18 | 24 | 43% |
| P1 | 58 | 26 | 32 | 45% |
| P2 | 16 | 5 | 11 | 31% |

---

## Testing Roadmap

### Phase 1: Critical Path (P0 Features)

**Target:** 80% coverage of P0 features

**Focus:**
- Onyx: Ingestion, indexing, search
- DeerFlow: Already well-covered
- Physics: Already well-covered
- Integration: MCP routing

**Estimated Effort:** 2-3 weeks

---

### Phase 2: Core Features (P1 Features)

**Target:** 70% coverage of P1 features

**Focus:**
- Onyx: Connectors, personas, error handling
- DeerFlow: Memory system, subagents
- Physics: Validation, literature comparison
- Integration: Full workflows

**Estimated Effort:** 3-4 weeks

---

### Phase 3: Nice-to-Have (P2 Features)

**Target:** 50% coverage of P2 features

**Focus:**
- Onyx: Advanced filtering, caching
- DeerFlow: Resource limits, optimization
- Physics: Diagnostic plots, visualization

**Estimated Effort:** 2-3 weeks

---

## Test Implementation Guide

### For Each Feature:

1. **Unit Test** - Test individual function
2. **Integration Test** - Test component interaction
3. **E2E Test** - Test full workflow
4. **Smoke Test** - Basic health check

### Example: Onyx Hybrid Search

**Unit Test:**
```python
def test_hybrid_search_combines_scores():
    """Test hybrid search combines semantic + keyword."""
    semantic_results = [{"id": "1", "score": 0.9}]
    keyword_results = [{"id": "1", "score": 0.7}]
    
    combined = hybrid_search(semantic_results, keyword_results)
    
    assert combined[0]["score"] == 0.83  # 0.7*0.9 + 0.3*0.7
```

**Integration Test:**
```python
def test_hybrid_search_with_opensearch():
    """Test hybrid search with real OpenSearch."""
    results = search(query="Blast-Wave", method="hybrid")
    
    assert len(results) > 0
    assert all("score" in r for r in results)
```

**E2E Test:**
```python
def test_full_search_workflow():
    """Test complete search workflow."""
    # Index document
    doc_id = index_document("test.pdf")
    
    # Search
    results = search("test query")
    
    # Verify
    assert any(r["document_id"] == doc_id for r in results)
```

---

## References

- [Onyx RAG Workflow](./onyx-rag-workflow.md)
- [DeerFlow Agent Workflow](./deerflow-agent-workflow.md)
- [Physics Pipeline Workflow](./physics-pipeline-workflow.md)
- [Integration Workflows](./integration-workflows.md)

---

**Last Updated:** 2026-05-31  
**Maintainer:** Platform Operations
