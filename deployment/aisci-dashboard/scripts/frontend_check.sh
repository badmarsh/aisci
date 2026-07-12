#!/bin/bash
echo "Checking frontend dependencies and build..."
cd /home/ubuntu/aisci/deployment/aisci-dashboard
bun run typecheck
bun run build
