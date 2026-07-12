#!/bin/bash
sed -i 's|getByRole("tab", { name: /Active/ })|getByRole("button", { name: /Active/i })|g' tests/e2e/tasks-agents.spec.ts
sed -i 's|getByRole("tab", { name: /Blocked/ })|getByRole("button", { name: /Blocked/i })|g' tests/e2e/tasks-agents.spec.ts
sed -i 's|getByRole("tab", { name: /Agent-Proposed/ })|getByRole("button", { name: /Proposed/i })|g' tests/e2e/tasks-agents.spec.ts
