#!/bin/bash
docker exec multica-postgres-1 psql -U multica -d multica -c "SELECT * FROM chat_session WHERE session_id = '99375b6a-67ea-4948-9c25-4b8b79ed4c2c';" > /home/ubuntu/aisci/chat_session.txt 2>&1
docker exec multica-postgres-1 psql -U multica -d multica -c "SELECT * FROM chat_message WHERE session_id = '99375b6a-67ea-4948-9c25-4b8b79ed4c2c' ORDER BY created_at ASC;" > /home/ubuntu/aisci/chat_messages.txt 2>&1
