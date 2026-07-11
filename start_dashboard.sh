#!/bin/bash

echo "Starting AiSci Dashboard Services..."

# Start Backend
echo "Starting Backend (uvicorn)..."
cd ignition
python3 -m uvicorn api:app --reload --port 8001 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Start Frontend
echo "Starting Frontend (npm run dev)..."
cd apps/aisci-dashboard
npm run dev > ../../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..

echo "=========================================="
echo "✅ Services Started!"
echo "📡 Backend running on port 8001 (PID: $BACKEND_PID) -> backend.log"
echo "🖥️  Frontend running on port 5173 (PID: $FRONTEND_PID) -> frontend.log"
echo "=========================================="
echo "Press Ctrl+C to stop all services."

# Trap Ctrl+C and kill both background processes
trap "echo -e '\nStopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM

# Wait for background processes
wait $BACKEND_PID $FRONTEND_PID
