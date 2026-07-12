#!/bin/bash
sed -i 's|"/agents"|"/projects/robert-boson-manuscript/agents"|g' tests/e2e/tasks-agents.spec.ts
sed -i 's|"\*\*/api/agents"|"\*\*/api/projects/\*/agents"|g' tests/e2e/tasks-agents.spec.ts
