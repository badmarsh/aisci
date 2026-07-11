# Activepieces Integration as Standalone Orchestrator

This document outlines how Activepieces is integrated into the AiSci platform as the visual execution engine for platform tasks.

## 1. Architecture Overview

- **Engine Location**: `docker-compose.selfhost.yml` alongside platform services.
- **Port**: `8082` internally and mapped to `localhost:8082`.
- **Database**: Separate `activepieces_postgres` container for workflow state.
- **Webhook Endpoint**: `http://localhost:8082/api/v1/webhooks/github-webhook`

## 3. Custom Node ("Piece") Development

To make Activepieces execute our actual python scripts (e.g., `trigger_onyx_agent.py`), we build a custom "Piece".

### Example: Onyx Agent Wrapper Piece
Instead of opaque polling, create a custom Activepieces typescript piece that calls the python shell:

```typescript
import { createPiece, createAction, Property } from '@activepieces/pieces-framework';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export const onyxAgentPiece = createPiece({
  displayName: 'Onyx Craft Agent',
  logoUrl: 'https://onyx.app/logo.png',
  authors: ['aisci-admin'],
  actions: [
    createAction({
      name: 'run_onyx_agent',
      displayName: 'Trigger Onyx Agent',
      description: 'Executes the local python wrapper for Onyx',
      props: {
        issueId: Property.ShortText({ displayName: 'GitHub Issue ID', required: true }),
        persona: Property.ShortText({ displayName: 'Onyx Persona', required: true }),
      },
      async run(context) {
        const { issueId, persona } = context.propsValue;
        // The docker container must have access to the volume or we use SSH/Docker APIs
        const { stdout } = await execAsync(`python3 /home/ubuntu/aisci/deployment/helper/trigger_onyx_agent.py --card-id ${issueId} --persona ${persona}`);
        return { success: true, logs: stdout };
      }
    })
  ],
  triggers: []
});
```

*(Note: In production, since Activepieces runs in its own docker container, running python shell scripts requires either mapping the repo volume into the `activepieces` container and installing python, or making HTTP calls to a lightweight Python executor API).*
