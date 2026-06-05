#!/bin/bash
docker exec multica-postgres-1 psql -U multica -d multica -c "SELECT * FROM chats WHERE id = '99375b6a-67ea-4948-9c25-4b8b79ed4c2c';" > /home/ubuntu/aisci/multica_chat.txt 2>&1
docker exec multica-postgres-1 psql -U multica -d multica -c "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';" > /home/ubuntu/aisci/multica_tables.txt 2>&1
