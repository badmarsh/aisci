#!/bin/bash
# Check if bad documents exist in OpenSearch
echo "=== Searching bad documents ==="
docker exec onyx-opensearch curl -s -X POST 'http://localhost:9200/_all/_search' -H 'Content-Type: application/json' -d '{
  "query": {
    "terms": {
      "document_id": [
        "FILE_CONNECTOR__5b321135-a81d-445f-ab69-3b9945fd02df",
        "FILE_CONNECTOR__b55d05ea-5a20-48fe-8fd0-ac050b958e81",
        "FILE_CONNECTOR__82db767b-877f-4e56-90e3-3d6da43b580a",
        "FILE_CONNECTOR__14becb62-8c7b-4fc0-b80a-4216f473bc6f",
        "FILE_CONNECTOR__4f8cd06b-22fc-4aef-9898-c375aa5f290f"
      ]
    }
  }
}' | grep -o '"total":[^,]*' | head -2

echo "=== Deleting bad documents ==="
docker exec onyx-opensearch curl -s -X POST 'http://localhost:9200/_all/_delete_by_query' -H 'Content-Type: application/json' -d '{
  "query": {
    "terms": {
      "document_id": [
        "FILE_CONNECTOR__5b321135-a81d-445f-ab69-3b9945fd02df",
        "FILE_CONNECTOR__b55d05ea-5a20-48fe-8fd0-ac050b958e81",
        "FILE_CONNECTOR__82db767b-877f-4e56-90e3-3d6da43b580a",
        "FILE_CONNECTOR__14becb62-8c7b-4fc0-b80a-4216f473bc6f",
        "FILE_CONNECTOR__4f8cd06b-22fc-4aef-9898-c375aa5f290f"
      ]
    }
  }
}'

echo "=== Verifying after deletion ==="
docker exec onyx-opensearch curl -s -X POST 'http://localhost:9200/_all/_search' -H 'Content-Type: application/json' -d '{
  "query": {
    "terms": {
      "document_id": [
        "FILE_CONNECTOR__5b321135-a81d-445f-ab69-3b9945fd02df",
        "FILE_CONNECTOR__b55d05ea-5a20-48fe-8fd0-ac050b958e81",
        "FILE_CONNECTOR__82db767b-877f-4e56-90e3-3d6da43b580a",
        "FILE_CONNECTOR__14becb62-8c7b-4fc0-b80a-4216f473bc6f",
        "FILE_CONNECTOR__4f8cd06b-22fc-4aef-9898-c375aa5f290f"
      ]
    }
  }
}' | grep -o '"total":[^,]*' | head -2
