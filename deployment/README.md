# Deployment

The active local deployment is the AiSci Dashboard and Ignition control API in
`deployment/aisci-dashboard/`.

## Current layout

| Path | Role |
|---|---|
| `aisci-dashboard/` | Active Vite/TanStack Start dashboard and FastAPI Ignition backend |
| `aisci-dashboard/data/` | Ignition runtime SQLite data; ignored from git |
| `helper/` | Temporary operational and migration helpers; not a deployed service |
| `hep-physics/` | Archived v0 UI concept with mocked data; not deployed |
| `data/` | Deployment-local data area; inspect before changing or removing |

No Docker Compose definition exists under `deployment/` in this checkout.
There is no active `onyx/` or `deer-flow/` deployment directory.

Start the active pair from the repository root with:

```bash
bash start_dashboard.sh
```

For current ports, operational constraints, and verification commands, see
[`docs/ops/deployment-reference.md`](../docs/ops/deployment-reference.md).

Do not commit live secrets, runtime databases, logs, or model caches.
