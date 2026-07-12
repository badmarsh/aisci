# High Energy Physics (HEP) MCP Servers

> Historical record only — not active operational guidance.

To enhance agent capabilities within the AiSci project, we utilize several specialized Model Context Protocol (MCP) servers. These are configured globally in the agent environment (`~/.gemini/config/mcp_config.json`).

## Registered Servers

1. **inspirehep**
   - **Command**: `uvx inspirehep-mcp-server`
   - **Purpose**: Connects to the INSPIRE-HEP database. Allows agents to seamlessly search for high-energy physics literature, lookup authors by ORCID, and retrieve citation metadata directly into context.

2. **particlephysics**
   - **Command**: `uvx particlephysics-mcp`
   - **Purpose**: Provides accurate particle properties (mass, spin, lifetime, decay modes) from PDG (Particle Data Group) data.

3. **math-physics-ml**
   - **Command**: `uvx math-physics-ml-mcp`
   - **Purpose**: Provides GPU-accelerated symbolic algebra (via SymPy) and physics simulations.

4. **rooagent**
   - **Command**: `uvx rooagent-mcp`
   - **Purpose**: Integrates ROOT-based HEP analysis tools for deep statistical inference, histogram inspection, and event selection.

## Agent Usage

Agents should utilize these tools whenever asked to perform deep literature reviews, validate mathematical models (e.g., Tsallis fits), or pull exact physical constants.
