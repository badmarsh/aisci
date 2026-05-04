# DeerFlow Custom Backup

Snapshot created before rebuilding the DeerFlow deployment around upstream Docker
plus the AIO sandbox provider.

Contents:

- `skills/`: local custom skills from `deployment/deer-flow/skills/custom/`.
- `tools/onyx/`: local Onyx community tool package.
- `agents/SOUL.md`: local research agent prompt.
- `workflows/`: local workflow JSON files.
- `playbooks/`: local playbook YAML files.
- `config/`: pre-change `config.yaml` and `extensions_config.json`.

No live `.env`, database, log, cache, or checkpoint files are included.
