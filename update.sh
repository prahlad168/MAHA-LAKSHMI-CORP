#!/bin/bash
# MAHA LAKSHMI CORP - Update Script
# Usage: ./update.sh
# Updates code, dependencies, and restarts server

set -e

echo "============================================================"
echo "MAHA LAKSHMI CORP - Production Update"
echo "============================================================"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Backup database
echo "[1/4] Backing up database..."
./backup.sh ./backups

# 2. Pull latest code
echo "[2/4] Pulling latest code..."
cd "$PROJECT_ROOT"
git pull origin main

# 3. Update dependencies
echo "[3/4] Updating dependencies..."
cd backend
pip3 install -r requirements.txt -q
cd ..

# 4. Restart server
echo "[4/4] Restarting server..."

# Kill existing server
EXISTING_PID=$(lsof -ti :8000 2>/dev/null || true)
if [ -n "$EXISTING_PID" ]; then
    echo "Stopping existing server (PID: $EXISTING_PID)..."
    kill -9 $EXISTING_PID 2>/dev/null || true
    sleep 2
fi

# Start server
echo "Starting server..."
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --log-level info > logs/server.log 2>&1 &
SERVER_PID=$!

sleep 4

# Verify
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo ""
    echo "============================================================"
    echo "Update completed successfully!"
    echo "============================================================"
    echo "Server PID: $SERVER_PID"
    echo "Health: http://localhost:8000/health"
    echo "Logs: logs/server.log"
    echo "============================================================"
else
    echo "ERROR: Server failed to start. Check logs/server-error.log"
    exit 1
fi
