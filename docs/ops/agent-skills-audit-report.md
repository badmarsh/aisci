# Agent Skills Audit Report

This report checks all `SKILL.md` files against `TEMPLATE.md` compliance.

## 2026-05-06 Workflow Audit Update

- All 15 local skills still have valid front matter and the required
  `Read First`, `Rules`, `Workflow`, and `Output & Approval Gates` sections.
- `aisci-ops-auditor` now explicitly checks submodule gitlink reachability and
  separates host-local MCP routes from Docker-network routes.
- `aisci-living-docs` now treats
  `deployment/onyx/nginx_configs/mcp_proxy.conf.template` as the MCP proxy
  ground truth instead of the standalone reference copy.
- `vendored-runtime-maintainer` no longer points at a removed DeerFlow
  assessment note; it now reads the canonical deployment reference and platform
  backlog.
- Markdown link scan across `docs/`, `agent-skills/`, and
  `deployment/onyx/docs/` found no broken Markdown links.

| Skill | YAML `name` | YAML `desc` | Title | Read First | Rules | Workflow | Output & Approval | Notes |
|---|---|---|---|---|---|---|---|---|
| aisci-living-docs | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Compliant |
| aisci-ops-auditor | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Compliant |
| aisci-tech-kickoff | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Compliant |
| analysis-handoff-router | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Compliant |
| git-worktree-guard | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Compliant |
| mcp-integration-planner | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Compliant |
| onyx-rag-eval-manager | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Compliant |
| platform-backlog-manager | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Compliant |
| reproducible-physics-runner | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Compliant |
| researcher-docs-manager | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Compliant |
| science-ledger-manager | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Compliant |
| science-report-writer | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Compliant |
| science-source-curator | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Compliant |
| secret-config-auditor | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Compliant |
| vendored-runtime-maintainer | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Compliant |
