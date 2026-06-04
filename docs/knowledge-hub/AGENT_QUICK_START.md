# Agent Quick Start Guide: Multica Knowledge Hub

As an agent working on the AiSci project, your role is not just to write code, but to contribute to our collective intelligence by capturing context and decisions in Multica.

## When to Create a Knowledge-Capture Issue

- **Research Findings**: After a deep dive into a topic or literature.
- **Significant Decisions**: When you make an architectural choice or change an approach.
- **Complex Bug Root Cause**: After fixing a non-trivial bug, document the "why" and "how".
- **Integration Details**: When connecting systems or setting up new infrastructure.
- **Workflow Logs**: Summarizing the results of a complex DeerFlow or multi-step process.

## How to Use Templates

1. Find the appropriate template in `docs/knowledge-hub/templates/`.
2. Copy the content and use it as a starting point for your issue description.
3. Follow the suggested title format (e.g., `Research: [topic]`).
4. Fill in all sections, especially **Context** and **Next Steps**.

## Labeling and Metadata

- Always apply a **Type** label (e.g., `research`, `implementation`).
- Apply relevant **Domain** labels (e.g., `physics`, `fitting`).
- Use **Source** labels if the info came from an external tool (e.g., `from-perplexity`).
- Use metadata sparingly for high-value facts that will be read often (e.g., `pr_url`, `decision`).

## Common Patterns

- **Reference existing issues**: Link related work using `AIS-XXX`.
- **Keep GitHub clean**: Put the detailed context here in Multica, and just link to it from your PR.
- **Update status**: When a research idea becomes an implementation task, link the new issue and update the status of the research one.
