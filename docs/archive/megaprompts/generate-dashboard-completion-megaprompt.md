> [!NOTE]\n> Archived on 2026-07-12: Meta-prompt that successfully generated its target prompt.\n\n# Dashboard Completion Meta-Prompt

**Role**: You are a Principal Software Architect and Lead AI Engineer tasked with analyzing an existing codebase and generating a comprehensive set of instructions (a "Megaprompt") for an AI coding agent to finish the application.

**Context**: The project is the `aisci-dashboard`, an AI-driven scientific research platform. 
The application consists of:
- **Frontend**: A React application using TanStack Start, Tailwind CSS, and shadcn/ui located in `deployment/aisci-dashboard/`.
- **Backend**: A FastAPI application with a background worker running in `deployment/aisci-dashboard/ignition/`.

**Your Task**:

1. **Load and Understand Context**:
   - Read the relevant documentation in the repository root (e.g., `README.md`, `ACTION_PLAN.md`, `docs/`) and `deployment/aisci-dashboard/AGENTS.md`.
   - Analyze the frontend architecture, specifically checking `package.json`, `vite.config.ts`, `tsconfig.json`, and the route structure.
   - Analyze the backend architecture in `ignition/`, focusing on `api.py`, `worker.py`, `database.py`, and the underlying data pipelines.

2. **Evaluate Current State & Objectives**:
   - Determine the overarching goal and general idea of the AiSci Dashboard.
   - Map out the currently implemented features (e.g., which frontend pages are complete, which API endpoints exist).
   - Identify gaps, missing components, incomplete wiring, and UX/UI shortcomings that prevent the application from being considered "finished."

3. **Generate the Execution Megaprompt**:
   Based on your analysis, output a highly detailed, actionable Megaprompt intended for an AI coding agent (like yourself). The output Megaprompt MUST include:
   - **System Role & Objectives**: Setting the stage for the agent.
   - **Architecture Guidelines**: Specifying the required tech stack and coding standards (e.g., use TanStack Start, Tailwind, FastAPI).
   - **Identified Missing Components**: A clear, prioritized list of exactly what needs to be built (e.g., specific missing React components, missing API endpoints, missing database schemas).
   - **Step-by-Step Implementation Plan**: Broken down into phases (e.g., Phase 1: Backend API Completion, Phase 2: Frontend Data Fetching, Phase 3: UI Polish & Layout).
   - **Testing & Verification Criteria**: How the agent should verify that the application is fully functional.

**Output Format**:
Provide your response containing *only* the generated Megaprompt, formatted in markdown, ready to be copied and pasted into a new agent session.
