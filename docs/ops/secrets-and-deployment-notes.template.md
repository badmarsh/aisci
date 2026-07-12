# Secrets And Deployment Notes Template

Do not put real secrets in this tracked template.

Private deployment notes belong in `docs/ops/private/`, which is gitignored.

## Local Secret Inventory

| Secret | Location | Used By | Rotation Notes |
|---|---|---|---|
| Example only | Example only | Example only | Example only |

## Exposure Checks

- Confirm the Dashboard and Ignition API use only intended local bindings before
  exposing them beyond development.
- Confirm `AISCI_DASHBOARD_TOKEN` and allowed origins are configured before
  enabling mutating control-plane endpoints outside local development.
- Rotate any token that appears in shell logs, screenshots, copied chat text,
  or committed history.
