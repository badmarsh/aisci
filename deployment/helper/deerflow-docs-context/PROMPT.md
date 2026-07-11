# Task: Scaffold a Standalone Documentation Portal for AiSci

You are building a documentation portal for an AI-assisted physics research project. The portal should render existing Markdown files in a clean, searchable, professional design.

---

## Requirements

### 1. Location
Create a new directory at `/workspace/aisci/aisci-docs-portal/`.
All files must be written to `/workspace/aisci/` so they survive container restarts.

### 2. Framework
Use **Next.js 14+** with **Fumadocs** (https://www.fumadocs.dev).
- Fumadocs is preferred over Nuxt because this project is already Next.js-based
- Install: `fumadocs-ui`, `fumadocs-core`
- Add **KaTeX** support for rendering physics equations ($p_T$, $\chi^2$/ndf, Bose-Einstein distributions, etc.)

### 3. Content Source
Do NOT copy Markdown files. Configure Fumadocs to read MDX/Markdown directly from:
- `/workspace/aisci/research/robert/` (science-facing docs)
- `/workspace/aisci/docs/` (ops, decisions, archive)
- `/workspace/aisci/` root (README.md, ACTION_PLAN.md)
- `/workspace/aisci/agent-skills/*/SKILL.md` (agent skills reference)

Use Fumadocs' `source` configuration or `fumadocs-mdx` to point at these paths.

### 4. Sidebar Structure
Match the project's information architecture:

```
AiSci Docs
├── Overview
│   ├── Home
│   └── Action Plan
├── Research (Robert's Validation)
│   ├── Workspace Overview
│   ├── Workflow
│   ├── Evidence Ledger
│   ├── Next Actions
│   ├── Validation Plan
│   ├── Fit Plan
│   ├── Science Questions
│   ├── Referee Report Draft
│   └── Data Onboarding
├── Operations & Deployment
│   ├── Deployment Reference
│   ├── Platform Backlog
│   ├── Troubleshooting
│   └── Critical Components
├── Architecture Decisions
│   ├── Parser & RAG Choice
│   ├── Science Evidence Standards
│   ├── System Boundaries
│   └── MCP Topology
└── Agent Skills
    └── Researcher Docs Manager
```

### 5. Design
- Use **shadcn/ui** for components
- Follow "Apple-like" design: clean layout, large typography, neutral colors, generous whitespace
- The portal should feel like a professional research dashboard, not a startup marketing site

### 6. KaTeX / Math Rendering
Ensure all inline math (`$...$`) and display math (`$$...$$`) render correctly. The docs contain:
- Inline: `$p_T$`, `$\chi^2$/ndf`, `$T$`, `$v$`
- Block equations for Bose-Einstein distributions, Tsallis fits, Blast-Wave parameterizations

---

## Workflow

1. **Scaffold**: Initialize Next.js app with App Router in `/workspace/aisci/aisci-docs-portal/`
2. **Install**: fumadocs-ui, fumadocs-core, fumadocs-mdx, @fumadocs/ui, katex, rehype-katex, remark-math
3. **Configure**: Set up MDX source to read from parent directory paths
4. **Layout**: Configure sidebar matching the structure above
5. **Theme**: Apply clean, minimal shadcn theme
6. **Verify**: Build and confirm the dev server serves pages with rendered math

---

## Sandbox Environment

You are running inside an OpenClaw sandbox (DeerFlow's execution environment).
- The host workspace is mounted at `/workspace/aisci/`
- If `node` or `npx` are missing: `apt-get update && apt-get install -y nodejs npm`
- All output must be under `/workspace/aisci/aisci-docs-portal/`
- Use `pnpm` if available, otherwise `npm`

---

## Context Files

Read these files for context before building:
- `/workspace/aisci/deployment/helper/deerflow-docs-context/CONTEXT.md` — project overview and IA
- `/workspace/aisci/README.md` — high-level dashboard
- `/workspace/aisci/AGENTS.md` — project rules and conventions
- `/workspace/aisci/agent-skills/researcher-docs-manager/SKILL.md` — documentation principles

---

## Deliverables

1. `/workspace/aisci/aisci-docs-portal/` — fully scaffolded Next.js + Fumadocs app
2. `package.json`, `next.config.ts`, `source.config.ts` — properly configured
3. Sidebar navigation matching the IA above
4. KaTeX rendering verified working
5. A `README.md` in the portal directory explaining how to run it
