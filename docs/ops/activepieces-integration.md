# Activepieces Integration & Multica Embedding

This document outlines how Activepieces is integrated into the AiSci platform as the visual execution engine for Multica Autopilot tasks.

## 1. Architecture Overview

- **Engine Location**: `docker-compose.selfhost.yml` alongside Multica.
- **Port**: `8082` internally and mapped to `localhost:8082`.
- **Database**: Separate `activepieces_postgres` container isolated from Multica's core db.
- **Webhook Endpoint**: `http://localhost:8082/api/v1/webhooks/multica-autopilot` (configured in `deployment/helper/multica_custom_runtimes.yaml`).

## 2. Multica UI React Embedding

Activepieces supports direct embedding inside React applications using their `@activepieces/ee-embed` package or via an iframe builder.

### Frontend Integration Steps (For Multica Web)

1. **Install SDK in Multica Frontend**:
   ```bash
   cd /home/ubuntu/aisci/multica-frontend
   npm install @activepieces/ee-embed
   ```

2. **React Component Definition**:
   In your Next.js/React frontend (e.g., `src/pages/workflows.tsx`), embed the builder:
   ```tsx
   import { ActivepiecesEmbedded } from '@activepieces/ee-embed';

   export default function VisualWorkflowBuilder() {
     return (
       <div style={{ height: '100vh', width: '100%' }}>
         <ActivepiecesEmbedded
           instanceUrl="http://localhost:8082"
           jwtToken="<User JWT Token generated via Activepieces API>"
         />
       </div>
     );
   }
   ```

3. **Routing Multica Issues to the Builder**:
   When an Autopilot runs (like `AIS-103`), users can click a "View Process" button on the issue card which routes them to the embedded Activepieces builder tab for that specific webhook flow.

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
        issueId: Property.ShortText({ displayName: 'Multica Issue ID', required: true }),
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
