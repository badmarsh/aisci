#!/bin/bash
sed -i 's|await page.goto("/");|await page.goto("/projects/robert-boson-manuscript");|g' tests/e2e/navigation.spec.ts
sed -i 's|/Overview/|/Overview — AiSci/|g' tests/e2e/navigation.spec.ts

sed -i 's|await page.goto("/");|await page.goto("/projects/robert-boson-manuscript");|g' tests/e2e/mutations.spec.ts
sed -i 's|"\*\*/api/ingest\*"|"\*\*/api/projects/\*/pipelines/ingest-paper/dry-run"|g' tests/e2e/mutations.spec.ts
sed -i 's|"\*\*/api/fits/run\*"|"\*\*/api/projects/\*/pipelines/run-fits/dry-run"|g' tests/e2e/mutations.spec.ts
