# Secrets And Deployment Notes Template

Do not put real secrets in this tracked template.

Private deployment notes belong in `docs/ops/private/`, which is gitignored.

## Local Secret Inventory

| Secret | Location | Used By | Rotation Notes |
|---|---|---|---|
| Example only | Example only | Example only | Example only |

## Exposure Checks

- Confirm DeerFlow is bound only to localhost before enabling MCPs that expose environment-backed tools.
- Confirm Onyx, LiteLLM, MCP proxy, and DeerFlow do not expose admin or credential-bearing endpoints on LAN.
- Rotate any token that appears in shell logs, screenshots, copied chat text, or committed history.

