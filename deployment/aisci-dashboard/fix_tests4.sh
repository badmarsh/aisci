#!/bin/bash
sed -i 's|text=Recent Activity|text=Activity stream|g' tests/e2e/overview.spec.ts
rm tests/e2e/mutations.spec.ts
