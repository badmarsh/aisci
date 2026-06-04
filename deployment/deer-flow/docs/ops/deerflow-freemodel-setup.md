# DeerFlow FreeModel API Configuration

**Date:** 2026-05-31  
**Status:** Active

## Overview

DeerFlow is configured to use Claude Opus 4.7 via FreeModel.dev API as an independent agent (not callback to current Claude Code session).

## Configuration

### Model Entry in `deployment/deer-flow/config.yaml`

```yaml
- name: claude-freemodel
  display_name: Claude Opus 4.7 (FreeModel)
  use: langchain_openai:ChatOpenAI
  model: claude-opus-4-7
  api_key: $FREEMODEL_API_KEY
  base_url: https://api.freemodel.dev/v1
  max_tokens: 8192
  supports_thinking: true
  supports_vision: true
```

### Environment Variable

Added to `deployment/deer-flow/.env`:
```bash
FREEMODEL_API_KEY=fe_oa_***
```

(Key stored in `/home/ubuntu/aisci/.env` as source of truth)

## How It Works

1. **Independent Agent**: Each DeerFlow task spawns a fresh Claude session via FreeModel API
2. **No Callback**: Does NOT route through the current Claude Code session
3. **Full Capabilities**: Supports extended thinking, vision, and 8K token output
4. **OpenAI-Compatible**: Uses `ChatOpenAI` interface with FreeModel base URL

## Usage in DeerFlow

1. Open http://localhost:2026
2. Create new research task
3. Select model: **"Claude Opus 4.7 (FreeModel)"**
4. DeerFlow will use independent Claude instance

## Benefits

✅ **Autonomous**: DeerFlow agents don't depend on current Claude Code session  
✅ **Scalable**: Multiple DeerFlow tasks can run in parallel  
✅ **Persistent**: Works even when Claude Code session ends  
✅ **Full-featured**: Extended thinking, vision, tool use all supported

## Maintenance

- API key stored in `/home/ubuntu/aisci/.env` (not committed)
- Config in `deployment/deer-flow/config.yaml` (gitignored, vendored)
- To update: Edit config, restart `docker-compose restart deer-flow-gateway`

## Verification

```bash
# Check DeerFlow health
curl http://localhost:2026/health

# Check gateway logs
docker-compose logs deer-flow-gateway --tail 50

# Verify model loaded (requires auth)
# Login to DeerFlow UI and check model dropdown
```

## Related

- FreeModel.dev API: https://freemodel.dev/dashboard/docs
- DeerFlow config reference: `deployment/deer-flow/config.example.yaml`
- Platform backlog: `docs/ops/Multica Issues`
