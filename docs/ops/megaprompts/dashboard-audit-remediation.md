# Megaprompt: Implement Claude Audit Suggestions for AiSci Dashboard

## Context
This megaprompt is designed to guide an AI agent to clean up the AiSci dashboard and backend, removing or labeling "theater" features and replacing them with structurally sound implementations that expose the real computational science engine underneath (`libs/physics-core`).

## Goal
Rip out or clearly flag fake UI elements and backend stubs that pretend to do work, and establish a real `Pipeline` primitive that bridges the gap between the physics engine and the control plane dashboard. 

## Phase 1: Rip Out or Label the "Theater"

The following components currently present mock data or fake capabilities. You must either completely remove them from the UI/backend or explicitly label them as `[Mock]` or `[Coming Soon]` if they serve as necessary placeholders.

1. **"Generated Hypotheses" Panel (`projects.$projectId.index.tsx` & `ignition/idea_generator.py`)**
   - **Current State:** Hardcoded strings returned from `IdeaGenerator.brainstorm()`, regardless of actual project context.
   - **Action:** Remove the mock strings. The `IdeaGenerator` must be rewritten to query the real Claims/Papers tables and the pipeline registry, citing the specific real data that triggered a suggestion. If this cannot be done immediately, label the UI panel explicitly as `[Mock - Not Connected to Engine]`.

2. **ScientistCoordinator (`ignition/scientist_coordinator.py`)**
   - **Current State:** A 6-stage DAG where every stage outputs a canned string.
   - **Action:** Document this clearly as a mock/stub in its docstring and remove it from any production-facing execution path until it is actually wired to real backend validation processes.

3. **Hardcoded Overview Metrics (`projects.$projectId.index.tsx`)**
   - **Current State:** 99.98% pipeline uptime, 12 ms read latency, 100% "Consistent" DB sync are typed directly into the JSX.
   - **Action:** Remove these string literals. Either bind these to real queries (e.g., from DB performance metrics) or remove the metrics entirely so the dashboard stops lying to the user.

4. **Contradictions Table**
   - **Current State:** Exists in DB schema but no rows are ever inserted.
   - **Action:** Update the UI to clearly indicate `0 Contradictions (Feature Pending Wiring)`. Do not present the empty state as if an agent actively searched and found zero contradictions.

5. **Literature Page Chart (`projects.$projectId.literature.tsx`)**
   - **Current State:** A static `<div>` styled like a recharts container with no real data.
   - **Action:** Rip out the fake chart graphic. Only render a chart if real data from the literature ingest is being plotted.

6. **scite.ai Integration**
   - **Current State:** Inert without `SCITE_API_KEY` and only tallies citations without contextual reasoning.
   - **Action:** Clearly document this limitation in the UI or settings page so users know what it actually does.

## Phase 2: First-Class Pipeline Architecture

The core of the issue is that the computational science engine (`libs/physics-core/src/`) is real, but the dashboard's representation of a "pipeline" is just a flat list of shell commands.

1. **Redefine `pipelines.toml` Schema**
   - Design a real schema for `pipelines.toml` that includes:
     - `owner`: e.g., "Robert" vs "User".
     - `title`: Human-readable name.
     - `entrypoint`: The specific target script in `libs/physics-core/src/`.
     - `citation`: Paper/DOI it implements.
     - `status`: Active, Deprecated, etc.
   - **Example Sketch:**
     ```toml
     [[pipelines]]
     id = "tsallis-pareto-fit"
     owner = "Robert"
     title = "Tsallis-Pareto Distribution Fit"
     entrypoint = "libs/physics-core/src/fit_tsallis.py"
     citation = "doi:10.1016/j.physletb.2023.138356"
     status = "active"
     description = "Runs the differential-evolution global optimization feeding into Minuit local refinement."
     ```

2. **Create a Browsable Pipelines UI**
   - Build a new `/pipelines` route (or a dedicated tab inside the project) that parses the new `pipelines.toml` schema.
   - The UI must clearly separate "My Pipelines" (user-owned) from "Robert's Pipelines" (AI/System-owned).
   - Display the metadata (citation, underlying script) so the user sees the real computational science work being done.

3. **Expose the Real Engine**
   - Expose the ~25 real scripts in `physics-core/src/` (MCMC, JAX autodiff, PySR, etc.) in the UI rather than collapsing them behind generic "fit-validation" buttons. Make them individually executable and attribute them correctly.

## Phase 3: Cleanup Stubs

1. **`phd-audit` Project**
   - **Current State:** The second project proof is a stub running `echo "Audit checks complete."`.
   - **Action:** Either delete the stub project entirely, or implement a real second project that demonstrates the engine against a different dataset/configuration. Do not claim the backlog item "onboard a second real project" is done until this is real.

## Execution Rules for the Agent
- Do not build new mock data to replace old mock data.
- Do not break the underlying `libs/physics-core/` engine. It works and is the real asset.
- Update `docs/ops/architecture-overview.md` to reflect these changes once implemented.
- Create tests for the new `pipelines.toml` parser.
