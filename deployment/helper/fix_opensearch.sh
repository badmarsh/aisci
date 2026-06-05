#!/bin/bash
echo "Clearing cluster.blocks.create_index..."
docker exec onyx-opensearch curl -s -X PUT "http://localhost:9200/_cluster/settings" \
  -H "Content-Type: application/json" \
  -d '{"persistent":{"cluster.blocks.create_index":null}}'
echo ""

echo "Enabling auto_create_index..."
docker exec onyx-opensearch curl -s -X PUT "http://localhost:9200/_cluster/settings" \
  -H "Content-Type: application/json" \
  -d '{"persistent":{"action.auto_create_index":"true"}}'
echo ""

echo "Verifying cluster settings..."
docker exec onyx-opensearch curl -s "http://localhost:9200/_cluster/settings?pretty"
echo ""

echo "Restarting onyx-api-server..."
docker restart onyx-api-server
echo "Done."
