#!/bin/bash
# MAHA LAKSHMI CORP - Production Deployment Script
set -e

echo "============================================================"
echo "MAHA LAKSHMI CORP - Production Deployment"
echo "============================================================"
echo ""

# Check if running from project root
if [ ! -f "backend/main.py" ]; then
    echo "ERROR: Please run this script from the project root directory"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found"
    exit 1
fi

echo "[1/5] Checking environment..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env not found. Copying from deployment/.env.production..."
    cp deployment/.env.production .env
    echo "IMPORTANT: Edit .env and set JWT_SECRET_KEY and other production values!"
fi

# Generate JWT secret if using default
if grep -q "change-me-to-a-random-secret-key" .env; then
    echo "Generating secure JWT_SECRET_KEY..."
    NEW_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i.bak "s/change-me-to-a-random-secret-key-in-production/$NEW_SECRET/" .env
    rm -f .env.bak
    echo "JWT_SECRET_KEY generated and saved to .env"
fi

echo "[2/5] Installing dependencies..."
cd backend
pip3 install -r requirements.txt -q
cd ..

echo "[3/5] Initializing database..."
python3 -c "from backend.db.connection import init_db; init_db()"
echo "Database initialized"

echo "[4/5] Creating logs directory..."
mkdir -p logs
echo "Logs directory created"

echo "[5/5] Starting production server..."
echo ""
echo "============================================================"
echo "Starting server..."
echo "============================================================"

# Kill any existing process on port 8000
EXISTING_PID=$(lsof -ti :8000 2>/dev/null || true)
if [ -n "$EXISTING_PID" ]; then
    echo "Killing existing process on port 8000 (PID: $EXISTING_PID)"
    kill -9 $EXISTING_PID 2>/dev/null || true
    sleep 1
fi

# Start server
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --log-level info &
SERVER_PID=$!

sleep 4

# Verify server is running
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo ""
    echo "============================================================"
    echo "Server started successfully!"
    echo "============================================================"
    echo "  API Docs: http://localhost:8000/api/docs"
    echo "  Health:   http://localhost:8000/health"
    echo "  Login:    http://localhost:8000/login/"
    echo "  Dashboard: http://localhost:8000/dashboard/"
    echo "  Public:   http://localhost:8000/public/"
    echo ""
    echo "Server PID: $SERVER_PID"
    echo "Logs: logs/server.log, logs/server-error.log"
    echo ""
    echo "Next steps:"
    echo "  1. Configure nginx reverse proxy"
    echo "  2. Setup SSL with Let's Encrypt"
    echo "  3. Point domain mahalaksmi.web.id to this server"
    echo "============================================================"
else
    echo "ERROR: Server failed to start. Check logs/server-error.log"
    exit 1
fi
