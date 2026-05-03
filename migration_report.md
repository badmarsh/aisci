# Migration Report: OpenClaw -> OpenFang

## Summary

- Imported: 6 items
- Skipped: 4 items
- Warnings: 0

## Imported

| Type | Name | Destination |
|------|------|-------------|
| Config | openclaw.json | config.toml |
| Agent | orchestrator | agents/orchestrator/agent.toml |
| Agent | developer | agents/developer/agent.toml |
| Agent | research-analyst | agents/research-analyst/agent.toml |
| Agent | content-creator | agents/content-creator/agent.toml |
| Agent | reviewer-qa | agents/reviewer-qa/agent.toml |

## Skipped

| Type | Name | Reason |
|------|------|--------|
| Config | hooks | Webhook hooks not supported — use OpenFang's event system instead |
| Config | auth-profiles | Auth profiles (API keys, OAuth tokens) not migrated for security — set env vars manually |
| Skill | 1 skill entries | Skills must be reinstalled via `openfang skill install` |
| Config | session | Session scope config differs — OpenFang uses per-agent sessions by default |

## Next Steps

1. Review imported agent manifests in `~/.openfang/agents/`
2. Review `~/.openfang/secrets.env` — verify tokens were migrated correctly
3. Set any remaining API keys referenced in `~/.openfang/config.toml`
4. Start the daemon: `openfang start`
5. Test your agents: `openfang agent list`
