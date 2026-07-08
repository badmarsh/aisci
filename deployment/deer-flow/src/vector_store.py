"""
Quick-Win #2 - Local Vector Store (Chroma / Qdrant)
====================================================
Auto-indexes completed research reports for semantic recall across sessions.
Prevents redundant web searches by letting the agent query prior work.

Usage:
    from src.vector_store import VectorStore
    vs = VectorStore()
    vs.index_report(report_text, metadata={"title": "...", "run_id": "abc"})
    results = vs.search("CERN Higgs boson decay", top_k=5)

Backend is controlled by VECTOR_STORE_BACKEND env var: chroma | qdrant | disabled
"""
from __future__ import annotations

import hashlib
import os
import time
from typing import Any


class VectorStore:
    """Thin wrapper around Chroma or Qdrant for report memory."""

    def __init__(self) -> None:
        self.backend = os.getenv("VECTOR_STORE_BACKEND", "chroma").lower()
        self.collection_name = os.getenv("CHROMA_COLLECTION", "deerflow_reports")
        self._client: Any = None
        self._collection: Any = None

    def _get_chroma(self) -> Any:
        if self._collection is not None:
            return self._collection
        import chromadb  # type: ignore
        host = os.getenv("CHROMA_HOST", "localhost")
        port = int(os.getenv("CHROMA_PORT", "8000"))
        self._client = chromadb.HttpClient(host=host, port=port)
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        return self._collection

    def _get_qdrant(self) -> Any:
        if self._client is not None:
            return self._client
        from qdrant_client import QdrantClient  # type: ignore
        url = os.getenv("QDRANT_URL", "http://localhost:6333")
        api_key = os.getenv("QDRANT_API_KEY") or None
        self._client = QdrantClient(url=url, api_key=api_key)
        return self._client

    def _embed(self, texts: list[str]) -> list[list[float]]:
        import openai
        api_key = os.getenv("EMBEDDING_API_KEY") or os.getenv("OPENAI_API_KEY", "")
        model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        client = openai.OpenAI(api_key=api_key)
        resp = client.embeddings.create(input=texts, model=model)
        return [e.embedding for e in resp.data]

    def index_report(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
    ) -> int:
        """Chunk, embed, and index a report. Returns number of chunks stored."""
        if self.backend == "disabled" or not text:
            return 0

        # BUGFIX: previously would infinite-loop or spin backwards when
        # chunk_overlap >= chunk_size. Also protects against non-positive sizes.
        if chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be in [0, chunk_size)")

        chunks: list[str] = []
        step = chunk_size - chunk_overlap
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            if end == len(text):
                break
            start += step

        embeddings = self._embed(chunks)
        meta = metadata or {}
        now = int(time.time())

        if self.backend == "chroma":
            coll = self._get_chroma()
            ids = [
                hashlib.sha256(
                    f"{meta.get('run_id','')}-{i}-{c[:32]}".encode()
                ).hexdigest()[:16]
                for i, c in enumerate(chunks)
            ]
            coll.upsert(
                ids=ids,
                documents=chunks,
                embeddings=embeddings,
                metadatas=[{**meta, "chunk_idx": i, "indexed_at": now}
                            for i in range(len(chunks))],
            )

        elif self.backend == "qdrant":
            from qdrant_client.models import PointStruct, VectorParams, Distance  # type: ignore
            client = self._get_qdrant()
            dim = len(embeddings[0])
            existing = [c.name for c in client.get_collections().collections]
            if self.collection_name not in existing:
                client.create_collection(
                    self.collection_name,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
                )
            # BUGFIX: Python's built-in hash() is randomised per process
            # (PYTHONHASHSEED), so the same chunk produced a different point ID
            # on every run — re-indexing created duplicates instead of upserting.
            # Use a stable SHA-256-derived integer ID, matching the Chroma path.
            points = [
                PointStruct(
                    id=int(hashlib.sha256(
                        f"{meta.get('run_id','')}-{i}-{chunk[:32]}".encode()
                    ).hexdigest()[:15], 16),
                    vector=emb,
                    payload={**meta, "text": chunk, "chunk_idx": i, "indexed_at": now},
                )
                for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
            ]
            client.upsert(collection_name=self.collection_name, points=points)

        return len(chunks)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Semantic search over indexed reports."""
        if self.backend == "disabled":
            return []

        [query_emb] = self._embed([query])

        if self.backend == "chroma":
            coll = self._get_chroma()
            results = coll.query(
                query_embeddings=[query_emb],
                n_results=top_k,
                include=["documents", "distances", "metadatas"],
            )
            # BUGFIX: on an empty collection Chroma returns [[]] or [] and
            # `results["documents"][0]` would raise IndexError; guard it.
            docs = (results.get("documents") or [[]])[0] or []
            dists = (results.get("distances") or [[]])[0] or []
            metas = (results.get("metadatas") or [[]])[0] or []
            return [
                {"text": d, "score": 1 - dist, "metadata": m}
                for d, dist, m in zip(docs, dists, metas)
            ]

        elif self.backend == "qdrant":
            client = self._get_qdrant()
            hits = client.search(
                collection_name=self.collection_name,
                query_vector=query_emb,
                limit=top_k,
                with_payload=True,
            )
            return [
                {"text": h.payload.get("text", ""), "score": h.score,
                 "metadata": {k: v for k, v in h.payload.items() if k != "text"}}
                for h in hits
            ]

        return []
