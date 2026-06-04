# Onyx Persona Snapshots

Reproducible JSON dumps of the science-stack personas. Produced by
`deployment/helper/export_persona_snapshot.py`.

## Why these exist

The Onyx admin UI is the canonical edit surface, but the underlying persona
config — system prompt, doc-set bindings, tool list, model binding, starter
messages — is fragile across stack rebuilds. These snapshots are the audit
trail: a stack reset can be diffed against the most recent snapshot to
identify what was lost, and a future restore script can ingest the JSON to
recreate the stack.

## Layout

```
deployment/onyx/snapshots/
└── YYYY-MM-DD/
    ├── persona-000.json   ← Assistant
    ├── persona-002.json   ← physics-validator
    ├── persona-003.json   ← arxiv-intake
    ├── persona-005.json   ← evidence-auditor
    ├── persona-006.json   ← referee-prep
    └── personas.json      ← aggregate (index + all per-persona records)
```

`personas.json` includes a `persona_index` listing every persona the API
knows about, so a missing-from-default-set persona is still discoverable in
the snapshot.

## What gets stripped/redacted

- `owner.email` is replaced with `<redacted-email>` by default. Pass
  `--keep-emails` to retain it.
- Tool entries are reduced to identity fields (`id`, `name`,
  `in_code_tool_id`, `mcp_server_id`, `display_name`, `enabled`,
  `chat_selectable`, `default_enabled`). The transient `oauth_config_id` and
  per-tool description noise is dropped.
- Document set entries are reduced to `id`, `name`, `is_public`.
- Token-shaped strings (`on_…`, `sk-…`) are scrubbed before write as a
  belt-and-braces guard against accidental capture.

## Usage

```bash
# default: dump the science stack {0, 2, 3, 5, 6} into today's folder
python3 deployment/helper/export_persona_snapshot.py

# pin specific persona ids
python3 deployment/helper/export_persona_snapshot.py --persona-id 2 --persona-id 5

# keep operator emails (e.g. for a private offline backup)
python3 deployment/helper/export_persona_snapshot.py --keep-emails
```

## Cron suggestion

Daily, just after the nightly RAG eval, so the snapshot reflects the same
state that produced the baseline:

```bash
45 3 * * * cd /home/ubuntu/aisci && \
    python3 deployment/helper/export_persona_snapshot.py \
        >> /tmp/onyx-persona-export.log 2>&1
```

## Diffing two snapshots

The per-persona files are stable JSON, so `diff -u` works well after
piping through `jq` to canonicalize key order:

```bash
diff -u \
    <(jq -S . 2026-05-30/persona-002.json) \
    <(jq -S . 2026-05-31/persona-002.json)
```

Common things to watch for in a diff:
- `default_model_configuration_id` change (model rebind)
- `tools[]` membership change (tool added/removed without a backlog row)
- `document_sets[]` becoming `[]` (corpus binding silently lost)
- `system_prompt` length jumping or shrinking (prompt rewritten)

## Curation

There's no automated retention. Reasonable retention policy:

- Keep the most recent snapshot per UTC date.
- Keep snapshots adjacent to a known operational milestone (`Multica Issues` completed items) for at least 30 days.
- Old snapshots can be deleted; git history holds the long-term record.
