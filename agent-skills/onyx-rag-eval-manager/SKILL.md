---
name: onyx-rag-eval-manager
description: Manage Onyx RAG evaluation discipline, including retrieval question sets, expected citations, persona/document-set coverage, embedding/rerank changes, and tuning gates.
---

# Onyx RAG Eval Manager

Use this before changing RAG settings or when evaluating retrieval quality.

## Core Rule

Do not tune embeddings, rerank counts, hybrid weights, contextual RAG, parser choices, or document sets without an evaluation set or explicit user approval.

## Evaluation Set

Maintain a 20-30 question set when available. Each question should include:

- Question.
- Expected source document or citation.
- Required answer type.
- Pass/fail criteria.
- Notes on missing coverage.

Store platform evaluation notes in `docs/ops/`. Do not store science claim conclusions there.

## Workflow

1. Read current Onyx/RAG docs and decisions.
2. Identify active document sets, personas, parser, embedding model, dimensions, hybrid/rerank/contextual settings.
3. Check whether the proposed change requires reindexing.
4. If no evaluation set exists, propose one before tuning.
5. When testing retrieval, record exact queries, expected sources, and observed behavior.

## Approval Gates

Ask before reindexing, resetting connectors, recreating containers, changing embedding dimensions, or switching production parsers.
