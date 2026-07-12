#!/bin/bash
sed -i 's|"/literature"|"/projects/robert-boson-manuscript/literature"|g' tests/e2e/literature.spec.ts
sed -i 's|"\*\*/api/literature"|"\*\*/api/projects/*/literature"|g' tests/e2e/literature.spec.ts

sed -i 's|"/"|"/projects/robert-boson-manuscript"|g' tests/e2e/overview.spec.ts
sed -i 's|"\*\*/api/tasks"|"\*\*/api/projects/*/tasks"|g' tests/e2e/overview.spec.ts

sed -i 's|"/evidence"|"/projects/robert-boson-manuscript/evidence"|g' tests/e2e/evidence.spec.ts
sed -i 's|"\*\*/api/evidence"|"\*\*/api/projects/*/evidence"|g' tests/e2e/evidence.spec.ts

sed -i 's|"/tasks"|"/projects/robert-boson-manuscript/tasks"|g' tests/e2e/tasks-agents.spec.ts
sed -i 's|"\*\*/api/tasks"|"\*\*/api/projects/*/tasks"|g' tests/e2e/tasks-agents.spec.ts

# fits uses live api or lacks mock. fits expects "Jüttner 1c" which is actually "Jüttner/Boltzmann 1c" in api.py
sed -i 's|"Jüttner 1c"|"Jüttner/Boltzmann 1c"|g' tests/e2e/fits.spec.ts
sed -i 's|"Tsallis 2c"|"Tsallis-Pareto 2c"|g' tests/e2e/fits.spec.ts
sed -i 's|"Bose-Einstein 1c"|"Bose 1c"|g' tests/e2e/fits.spec.ts
