#!/bin/bash
# ============================================
# CRYPTO PAYMENT SYSTEM - QUICK START
# ============================================
# Run this script to start the payment system
# ============================================

set -e

echo "🚀 Starting Crypto Payment System..."

# Check if Docker is running
if ! sudo docker info > /dev/null 2>&1; then
    echo "📦 Starting Docker..."
    sudo dockerd > /tmp/docker.log 2>&1 &
    sleep 5
fi

# Stop old container if exists
sudo docker stop crypto-payment 2>/dev/null || true
sudo docker rm crypto-payment 2>/dev/null || true

# Build image
echo "🔨 Building Docker image..."
cd "$(dirname "$0")"
sudo docker build -t crypto-payment:latest .

# Run container
echo "▶️ Starting container..."
sudo docker run -d \
    --name crypto-payment \
    -p 5000:5000 \
    --restart unless-stopped \
    crypto-payment:latest

# Wait for container to start
sleep 3

# Check if running
if sudo docker ps | grep -q crypto-payment; then
    echo "✅ Container is running!"
    
    # Start cloudflared tunnel
    echo "🌐 Starting cloudflared tunnel..."
    pkill -f cloudflared 2>/dev/null || true
    
    nohup cloudflared tunnel --url http://localhost:5000 > /tmp/cloudflared.log 2>&1 &
    sleep 10
    
    # Get URL
    TUNNEL_URL=$(cat /tmp/cloudflared.log | grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' | head -1)
    
    echo ""
    echo "🎉===============================================🎉"
    echo "   CRYPTO PAYMENT SYSTEM - LIVE!"
    echo "🎉===============================================🎉"
    echo ""
    echo "   🌐 PUBLIC URL: $TUNNEL_URL"
    echo ""
    echo "   📋 Endpoints:"
    echo "      - Checkout: $TUNNEL_URL"
    echo "      - API:      $TUNNEL_URL/api/v1"
    echo "      - Health:   $TUNNEL_URL/health"
    echo ""
    echo "🎉===============================================🎉"
    echo ""
else
    echo "❌ Container failed to start!"
    echo "   Check logs: sudo docker logs crypto-payment"
fi
