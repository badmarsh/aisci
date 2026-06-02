# AiSci Docs Portal — Context for DeerFlow Agent

## Project Overview

AiSci is an AI-assisted scientific research workspace for validating high-energy physics (HEP) papers. The current focus is validating a "Boson probability function for the moving system" paper against ATLAS 13 TeV data.

The project has three layers:
1. **Science** (`research/robert/`) — physics validation workflow, evidence ledger, fit plans, referee reports
2. **Platform** (`docs/ops/`, `docs/decisions/`) — deployment, architecture, MCP tools, Docker stack
3. **Tools** — Onyx (private RAG at :3000), DeerFlow (orchestration at :2026), LiteLLM proxy (:4000), MCP proxy (:8095)

## What We Need

A standalone documentation portal that renders the existing Markdown/MDX files from this repo in a clean, searchable, "Apple-like" design. The portal should:

- Read files directly from the repo (no copying)
- Render physics equations with KaTeX/MathJax
- Have a sidebar matching the repo's information architecture
- Use Next.js + Fumadocs (preferred) or shadcn-docs-nuxt

## Information Architecture (Sidebar Structure)

```
AiSci Documentation
├── Overview
│   └── Home (README.md)
│   └── Action Plan (ACTION_PLAN.md)
├── Research (Robert's Validation)
│   └── Workspace Overview (research/robert/README.md)
│   └── Workflow (research/robert/workflow.md)
│   └── Evidence Ledger (research/robert/evidence-ledger.md)
│   └── Next Actions (research/robert/next-actions.md)
│   └── Validation Plan (research/robert/validation-plan.md)
│   └── Fit Plan (research/robert/fit-plan.md)
│   └── Science Questions (research/robert/science-questions.md)
│   └── Referee Report Draft (research/robert/referee-report-draft.md)
│   └── Data Onboarding (research/robert/data-onboarding.md)
├── Operations & Deployment
│   └── Deployment Reference (docs/ops/deployment-reference.md)
│   └── Platform Status (docs/ops/platform-status.md)
│   └── Troubleshooting (docs/ops/troubleshooting.md)
│   └── Critical Components (docs/ops/critical-components.md)
├── Architecture Decisions
│   └── Parser & RAG Choice (docs/decisions/2026-04-26-parser-and-rag-choice.md)
│   └── Science Evidence Standards (docs/decisions/2026-04-26-science-evidence-standards.md)
│   └── System Boundaries (docs/decisions/2026-04-26-system-boundaries.md)
│   └── MCP Topology (docs/decisions/2026-04-27-mcp-topology.md)
└── Agent Skills
    └── Researcher Docs Manager (agent-skills/researcher-docs-manager/SKILL.md)
    └── [other skills as needed]
```

## Key Design Rules (from researcher-docs-manager skill)

1. **Separation of Concerns**: Science files stay in `research/`, platform files stay in `docs/ops/`
2. **Evidence-Led**: No claims beyond what the evidence ledger supports
3. **Terminology**: Distinguish Bose-Einstein distributions from Boltzmann/Juttner approximations
4. **Researcher-First UX**: Clean, high signal-to-noise ratio, physicist-friendly

## Sandbox Notes

You are running inside an OpenClaw sandbox. The host-mounted workspace is at `/workspace/aisci/`. All files you create should be written under `/workspace/aisci/` so they survive container restarts. If Node.js or npx are missing, install them or work within the project folder directly.
