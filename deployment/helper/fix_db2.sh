#!/bin/bash
docker exec multica-postgres-1 psql -U multica -d multica -t -c "ALTER TABLE agent_task_queue ADD COLUMN IF NOT EXISTS last_heartbeat_at timestamp with time zone;"
