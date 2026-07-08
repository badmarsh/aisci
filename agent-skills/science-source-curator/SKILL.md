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
5. If source ingestion/document-set work is needed, propose a GitHub ops issue
   and a concise `docs/ops/platform-backlog.md` state update instead.

## Output & Approval Gates

- Request approval before writing to the evidence ledger.
- Do not create new markdown files without user permission.

## MCP Tool: Consensus

Consensus is available as an MCP tool routed via the nginx proxy at `/consensus/`.

### Auth model

Consensus uses **OAuth Bearer tokens**, not a static API key. The calling agent is
responsible for supplying the `Authorization: Bearer <token>` header. The nginx
`mcp_proxy.conf.template` passes this header upstream via `proxy_pass_header Authorization`
without injecting or overriding it.

### Token setup

Complete the Consensus OAuth flow from the MCP-aware client that will make the
request. Do not extract browser session tokens into repo env files, and do not
commit bearer tokens. If a non-OAuth client must be used, treat the bearer token
as ignored local operator config and document only the variable name, never the
value.

### When to use Consensus vs. Scite

| Tool | Best for |
|---|---|
| **Consensus** | Plain-language questions: "Do papers support X?" — returns AI-synthesised consensus summaries across many papers |
| **Scite** | Citation-level evidence: "How do papers cite Y?" — returns supporting/contrasting/mentioning citation snippets |

For physics validation, prefer **Scite** for extracting equation-level evidence from
specific papers. Use **Consensus** for broad literature landscape questions
(e.g., "Is the Jüttner distribution the standard in relativistic kinetic theory?").
