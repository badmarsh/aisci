#!/bin/bash
docker exec multica-postgres-1 psql -U multica -d multica -t -c "SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%task%';"
docker exec multica-postgres-1 psql -U multica -d multica -t -c "ALTER TABLE agent_tasks ADD COLUMN IF NOT EXISTS last_heartbeat_at timestamp with time zone;"
docker exec multica-postgres-1 psql -U multica -d multica -t -c "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS last_heartbeat_at timestamp with time zone;"
