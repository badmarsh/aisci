#!/bin/bash
curl -v http://localhost:2026/workspace/chats/99375b6a-67ea-4948-9c25-4b8b79ed4c2c > /home/ubuntu/aisci/curl_chat.txt 2>&1
curl -v http://localhost:2026/api/chats/99375b6a-67ea-4948-9c25-4b8b79ed4c2c > /home/ubuntu/aisci/curl_api.txt 2>&1
