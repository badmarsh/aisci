#!/bin/bash
echo "Backend health check:"
curl -s http://localhost:8001/api/projects | head -n 1
echo ""
echo "Frontend health check:"
curl -s http://localhost:5173 | head -n 1
echo ""
