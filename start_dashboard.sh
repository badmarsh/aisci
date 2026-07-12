#!/bin/bash

echo "Cleaning up existing processes on ports 8001 and 8081..."
fuser -k 8001/tcp 2>/dev/null
fuser -k 8081/tcp 2>/dev/null
sleep 1

echo "Starting AiSci Dashboard Services..."

# Start Backend
echo "Starting Backend (uvicorn)..."
cd deployment/aisci-dashboard/ignition
python3 -m uvicorn api:app --reload --port 8001 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ../../..

# Start Frontend
echo "Starting Frontend (npm run dev on port 8081)..."
cd deployment/aisci-dashboard
npm run dev -- --port 8081 > frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..

echo "=========================================="
echo "✅ Services Started!"
echo "📡 Backend running on port 8001 (PID: $BACKEND_PID) -> deployment/aisci-dashboard/backend.log"
echo "🖥️  Frontend running on port 8081 (PID: $FRONTEND_PID) -> deployment/aisci-dashboard/frontend.log"
echo "=========================================="
echo "Press Ctrl+C to stop all services."

# Trap Ctrl+C and kill both background processes
trap "echo -e '\nStopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM

# Wait for background processes
wait $BACKEND_PID $FRONTEND_PID
