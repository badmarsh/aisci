# Decision: MCP Tool Topology

Date: 2026-04-27

## Decision

Use a shared project-level MCP/tooling layer rather than IDE-specific MCP configuration as the source of truth.

Onyx should own curated evidence retrieval: document ingestion, document sets, citation-grounded RAG, and physics personas. External research MCPs such as Scite, Consensus, arXiv, INSPIRE-HEP, HEPData, Semantic Scholar, or OpenAlex should be connected through a shared local MCP proxy or documented project-level config when they are useful to more than one agent.

Coding agents may access Onyx and selected direct MCP/API tools, but Onyx should not be treated as a universal MCP aggregator unless a working Onyx-exposed endpoint is explicitly documented and tested.

## Rationale

This keeps the workspace portable across agents and editors. Onyx is strongest as the curated knowledge layer, while coding agents are strongest when they can run code, inspect files, and call specific tools for external evidence. Putting every MCP only inside one IDE or one agent makes the workflow fragile and hard to reproduce.

## Consequences

- Prefer project-level MCP config and local proxy routes over VS Code-only setup.
- Attach citation and literature tools to Onyx personas when the output should be source-grounded inside Onyx.
- Also expose essential research tools directly to coding/orchestration agents when they need to fetch or verify external evidence during a run.
- Keep secrets in ignored environment files or secret stores, not committed YAML.
- Record tested MCP endpoints and operational caveats in `docs/ops/`.
