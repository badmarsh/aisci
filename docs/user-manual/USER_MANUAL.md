# AiSci User Manual

This is the canonical skill map, pipeline structure, and daily routine reference for all agents and Robert.

## Skill Map
*For a full list of vendor-neutral workflow skills, see `agent-skills/`.*

## Pipeline Structure
The application primarily runs on a CQRS (Command Query Responsibility Segregation) pattern mediated by the Ignition Engine (FastAPI). Long-running science pipeline operations (e.g. fitting) are dispatched as `asyncio` background tasks rather than blocking API calls. For more details on system architecture, see `docs/ops/architecture-overview.md`.

## Daily Routine Reference
*(To be populated)*
