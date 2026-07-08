# DeerFlow Vector Store

This directory holds configuration and tooling for embedding and searching
past research reports via a local vector database.

## Supported Backends

| Backend | Port | Docker service | Notes |
|---------|------|----------------|-------|
| **Chroma** | 8001 | `deerflow-chroma` (docker-compose.extras.yml) | Default; zero-config |
| **Qdrant** | 6333 | `deerflow-qdrant` (docker-compose.extras.yml) | Better for large corpora |

## Quick Start

```bash
# 1. Start the vector store
docker compose -f docker-compose.extras.yml up -d chroma

# 2. Index a completed report
python -m deployment.deer_flow.vector_store.indexer \
    --run-id <run_id> \
    --report-path .deer-flow/reports/<run_id>.md

# 3. Semantic search over past reports
python -m deployment.deer_flow.vector_store.searcher \
    --query "Higgs boson mass measurement"
```

## Environment Variables

```bash
# Chroma
CHROMA_HOST=localhost
CHROMA_PORT=8001
CHROMA_COLLECTION=deerflow_reports

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=          # required for Qdrant Cloud only
QDRANT_COLLECTION=deerflow_reports
```

## Planned Indexing Pipeline

```
Completed Report (Markdown)
        │
        ▼
   Chunker (512 tokens, 64 overlap)
        │
        ▼
   Embedder (sentence-transformers/all-MiniLM-L6-v2)
        │
        ▼
   Upsert → Chroma / Qdrant
        │
        ▼
   Metadata stored: run_id, query, timestamp, model, tags
```

## Integration with DeerFlow

The `onyx_search` tool already searches the Onyx knowledge base.
Add a `vector_search` tool alongside it in `config.example.yaml` to
enrich responses with semantically-similar past reports::

```yaml
tools:
  - name: vector_search
    group: knowledge
    use: deerflow.community.vector_store.tools:vector_search_tool
    collection: deerflow_reports
    top_k: 5
```
