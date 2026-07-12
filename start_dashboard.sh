#!/bin/bash

echo "Cleaning up existing processes on ports 8001 and 5173..."
fuser -k 8001/tcp 2>/dev/null
fuser -k 5173/tcp 2>/dev/null
sleep 1

echo "Starting AiSci Dashboard Services..."

# Start Backend
echo "Starting Backend (uvicorn)..."
cd deployment/aisci-dashboard/ignition
python3 -m uvicorn api:app --reload --port 8001 > ../backend.log 2>&1 &
BACKEND_PID=$!

echo "Starting Worker..."
python3 worker.py > ../worker.log 2>&1 &
WORKER_PID=$!
cd ../../..

# Start Frontend
echo "Starting Frontend (npm run dev on port 5173)..."
cd deployment/aisci-dashboard
npm run dev -- --port 5173 > frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..

echo "=========================================="
echo "✅ Services Started!"
echo "📡 Backend running on port 8001 (PID: $BACKEND_PID) -> deployment/aisci-dashboard/backend.log"
echo "⚙️  Worker running (PID: $WORKER_PID) -> deployment/aisci-dashboard/worker.log"
echo "🖥️  Frontend running on port 5173 (PID: $FRONTEND_PID) -> deployment/aisci-dashboard/frontend.log"
echo "=========================================="
echo "Press Ctrl+C to stop all services."

# Trap Ctrl+C and kill all background processes
trap "echo -e '\nStopping services...'; kill $BACKEND_PID $FRONTEND_PID $WORKER_PID 2>/dev/null; exit" SIGINT SIGTERM

# Wait for background processes
wait $BACKEND_PID $FRONTEND_PID $WORKER_PID
