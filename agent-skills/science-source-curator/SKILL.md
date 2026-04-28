---
name: science-source-curator
description: Manage science source materials such as Robert's manuscript PDF, literature PDFs, arXiv/INSPIRE/HEPData references, extracted equations, data tables, and citation evidence without overstating claims.
---

# Science Source Curator

Use this when collecting, extracting, reconciling, or organizing source evidence for Robert's analysis.

## Introduction & Scope

Sources include:

- Robert's manuscript and revised drafts.
- Literature PDFs and citation context.
- arXiv, INSPIRE-HEP, HEPData, Scite, Consensus, Semantic Scholar, and OpenAlex outputs.
- Extracted equations, tables, fit values, and figure/caption evidence.
- Onyx document-set membership notes when they affect source availability.

## Read First

- `AGENTS.md`
- `research/robert/evidence-ledger.md`
- `research/robert/science-questions.md`
- `research/robert/validation-plan.md`
- `docs/decisions/2026-04-26-science-evidence-standards.md`

## Rules

- Record source identity, page/section/table/equation when available.
- Distinguish manuscript claims, local derivations, extracted data, and literature support.
- Do not promote claims beyond the evidence state supported by the ledger.
- Keep platform implementation details out of science files unless they are needed as source provenance.
- Store platform ingestion/tooling issues in `docs/ops/`, not in science notes.

## Workflow

1. Identify the source and the claim or question it supports.
2. Extract only the relevant evidence, with location and uncertainty.
3. Cross-check against existing ledger entries to avoid duplicates.
4. Propose updates to `evidence-ledger.md` or `next-actions.md`.
5. If source ingestion/document-set work is needed, propose a platform backlog item instead.
