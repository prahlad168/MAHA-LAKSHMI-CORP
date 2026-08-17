#!/bin/bash
# MAHA LAKSHMI CORP - Backend Startup Script
# Usage: ./start-server.sh [port]
# Default port: 8000

set -e

PORT=${1:-8000}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================================"
echo "MAHA LAKSHMI CORP - Backend Server"
echo "============================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found"
    exit 1
fi

echo "[1/3] Python found: $(python3 --version)"

# Check dependencies
echo "[2/3] Checking dependencies..."
cd "$SCRIPT_DIR/backend"
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
else
    echo "Dependencies already installed"
fi

# Check .env
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "WARNING: .env file not found. Copying from .env.example..."
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo "IMPORTANT: Edit .env and set JWT_SECRET_KEY and other required values!"
fi

# Kill any existing process on the port
echo "[3/3] Starting server on port $PORT..."
EXISTING_PID=$(lsof -ti :$PORT 2>/dev/null || true)
if [ -n "$EXISTING_PID" ]; then
    echo "Killing existing process on port $PORT (PID: $EXISTING_PID)"
    kill -9 $EXISTING_PID 2>/dev/null || true
    sleep 1
fi

# Start server
cd "$SCRIPT_DIR"
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT --log-level info &
SERVER_PID=$!

echo ""
echo "============================================================"
echo "Server starting..."
echo "============================================================"
echo "  API Docs: http://localhost:$PORT/api/docs"
echo "  Health:   http://localhost:$PORT/health"
echo "  Login:    http://localhost:$PORT/login/"
echo "  Dashboard: http://localhost:$PORT/dashboard/"
echo "  Public:   http://localhost:$PORT/public/"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================================"

# Wait for server to be ready
sleep 4
if curl -s http://localhost:$PORT/health > /dev/null; then
    echo "Server is ready!"
else
    echo "Server is starting... (may take a few more seconds)"
fi

# Keep script running
wait $SERVER_PID
