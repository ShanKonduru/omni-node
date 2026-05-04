#!/bin/bash
# Quick Start - OmniNode (Skip setup if already configured)

echo "========================================"
echo "   OmniNode Quick Start"
echo "========================================"
echo ""

# Start backend in background
cd backend
python3 main.py &
BACKEND_PID=$!
cd ..
echo "Backend started (PID: $BACKEND_PID)"
sleep 2

# Start frontend in background
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo "Frontend started (PID: $FRONTEND_PID)"
echo ""

echo "========================================"
echo "Servers are running!"
echo "========================================"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "Stopped."
    exit 0
}

trap cleanup INT TERM
wait
