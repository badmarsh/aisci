#!/bin/bash
sqlite3 /home/ubuntu/backups/deer_flow_checkpoints.db "SELECT checkpoint FROM checkpoints WHERE thread_id = '99375b6a-67ea-4948-9c25-4b8b79ed4c2c' ORDER BY checkpoint_id DESC LIMIT 1;" > /home/ubuntu/aisci/backup_checkpoint.txt 2>&1
sqlite3 /home/ubuntu/deer-flow/backend/.deer-flow/checkpoints.db "SELECT checkpoint FROM checkpoints WHERE thread_id = '99375b6a-67ea-4948-9c25-4b8b79ed4c2c' ORDER BY checkpoint_id DESC LIMIT 1;" > /home/ubuntu/aisci/original_checkpoint.txt 2>&1
