# Claude-to-DeerFlow Delegation Skill

## Description
This skill allows external agents (like Claude Code, Cursor, or specialized local bots) to delegate deep research or complex implementation tasks to this DeerFlow instance.

## API Endpoint
`POST http://localhost:8001/api/delegate`

## Usage Instructions for External Agents
If you are an external agent and the task requires:
- Extensive web searching (Brave Search)
- Browser automation (Puppeteer)
- Isolated code execution (Docker Sandbox)
- Long-horizon multi-step planning

You should delegate the task to DeerFlow.

### Example Delegation Payload
```json
{
  "task": "Research the latest architectural patterns for high-throughput LLM gateways and provide a report with Mermaid diagrams.",
  "priority": "high",
  "context": "The user is building a production-grade agentic system."
}
```

## Internal Agent Instructions
When you receive a delegation request via this skill:
1. Acknowledge the handoff from the external agent.
2. Activate **Ultra Mode** (Subagents) to handle the complexity.
3. Use the **System Architect** agent if diagrams are needed.
4. Return the final result in a structured Markdown format.
