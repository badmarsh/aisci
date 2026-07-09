---
name: latex-poster-builder
description: End-to-end LaTeX poster generation pipeline. Ingest markdown analysis, draft a Beamer .tex template, and compile the final PDF poster.
---

# LaTeX Poster Builder

Use this skill as the final stage of the pipeline to synthesize completed physics runs into a presentation-ready poster.

## Read First
- `AGENTS.md`
- `research/robert/runs/` (for final plots and metrics)

## Rules
- **Prerequisites:** Do not proceed if the `fit_results.json` or required figures are missing from the run directory.
- **Compilation:** Always run latex compile (e.g., `pdflatex`, `biber`, `pdflatex`) at least twice to ensure references resolve correctly.
- **Error Handling:** If a LaTeX compilation throws a Fatal Error, attempt to fix it twice. If unresolvable, halt the pipeline.

## Workflow
1. Ingest the final accepted `referee-report-draft.md` and physics plots from the active run directory.
2. Draft a Beamer `.tex` template incorporating the claims and figures.
3. Compile the `.tex` file into a PDF poster.
4. Export the final poster to `research/thesis/` or the run directory.

## Output
A compiled LaTeX poster PDF representing the successful culmination of the autonomous physics run.
