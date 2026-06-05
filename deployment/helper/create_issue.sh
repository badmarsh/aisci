#!/bin/bash
export MULTICA_SERVER_URL=http://localhost:8080
multica issue create \
  --title "Fix DeerFlow LangGraph and Run Persistence" \
  --status "todo" \
  --priority "high" \
  --description "DeerFlow is configured for SQLite data and run_events using db, but the .deer-flow/data directory is missing causing silent persistence failures. Need to fix database configuration, preferably by pointing to Multica's Postgres container." \
  > /home/ubuntu/aisci/create_issue_output.txt 2>&1
