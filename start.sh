#!/bin/bash
# OmniNode Launcher for Unix/Linux/macOS
# This script sets up and launches the OmniNode application

set -e  # Exit on error

echo "========================================"
echo "   OmniNode Launcher"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Python 3 is not installed or not in PATH"
    echo "Please install Python 3.12+ and try again"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Node.js is not installed or not in PATH"
    echo "Please install Node.js 20+ and try again"
    exit 1
fi

echo -e "${GREEN}[1/5]${NC} Installing Python dependencies..."
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi
echo "Installing backend packages..."
pip3 install -e ".[dev]" --quiet || pip install -e ".[dev]" --quiet
echo ""

echo -e "${GREEN}[2/5]${NC} Running setup script..."
python3 scripts/setup.py
echo ""

echo -e "${GREEN}[3/5]${NC} Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing npm packages for the first time..."
    npm install
else
    echo "npm packages already installed, skipping..."
fi
cd ..
echo ""

echo -e "${GREEN}[4/5]${NC} Starting backend server..."
# Start backend in background
cd backend
python3 main.py &
BACKEND_PID=$!
cd ..
echo "Backend started (PID: $BACKEND_PID)"
sleep 3
echo ""

echo -e "${GREEN}[5/5]${NC} Starting frontend server..."
# Start frontend in background
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo "Frontend started (PID: $FRONTEND_PID)"
echo ""

echo "========================================"
echo "   OmniNode is running!"
echo "========================================"
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "Servers stopped."
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT TERM

# Wait for both processes
wait
