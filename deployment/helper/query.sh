#!/bin/bash
sqlite3 /home/ubuntu/deer-flow/backend/.deer-flow/checkpoints.db "SELECT thread_id FROM checkpoints WHERE thread_id LIKE '%99375b6a%';" > /home/ubuntu/aisci/thread_match.txt
