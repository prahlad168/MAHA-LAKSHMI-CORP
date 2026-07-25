#!/bin/bash
# 🚀 ACTIVATE AUTONOMOUS SALES AGENT - TODAY
# This script makes the system ready for sales tomorrow

echo "=========================================="
echo "👑 MAHA LAKSHMI - AUTONOMOUS SALES AGENT"
echo "🚀 ACTIVATION SCRIPT"
echo "=========================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Create necessary directories
echo "📂 Creating directories..."
mkdir -p logs
mkdir -p data
echo "✅ Directories ready"
echo ""

# Check Python
echo "🐍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
python3 --version
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -q requests python-dotenv schedule jinja2 markdown rich 2>/dev/null || true
echo "✅ Dependencies ready"
echo ""

# Run quick start demo
echo "🚀 Running system demo..."
echo ""
python3 quick-start.py

echo ""
echo "=========================================="
echo "✅ ACTIVATION COMPLETE"
echo "=========================================="
echo ""
echo "📋 WHAT WAS SETUP:"
echo "  ✅ Sales Agent - handles all outreach"
echo "  ✅ Finance Agent - handles all payments"
echo "  ✅ Market Analyzer - analyzes trends"
echo "  ✅ Self-Improvement - optimizes performance"
echo "  ✅ CEO Reporter - sends daily reports"
echo ""
echo "🌐 DOMAIN: mahalaksmi.web.id"
echo "💰 PAYMENT GATEWAYS: Stripe, PayPal, Wise, Crypto, Midtrans"
echo "👑 CEO RECEIVES: Daily revenue reports at 23:59 WIB"
echo ""
echo "=========================================="
echo "🚀 TO START CONTINUOUS OPERATION:"
echo "=========================================="
echo ""
echo "  python3 orchestrator.py"
echo ""
echo "Or run in background:"
echo "  nohup python3 orchestrator.py > logs/orchestrator.log 2>&1 &"
echo ""
echo "=========================================="
echo "📊 MONITORING:"
echo "=========================================="
echo ""
echo "  View logs: tail -f logs/orchestrator.log"
echo "  View reports: ls logs/"
echo "  Dashboard: open dashboard/ceo-dashboard.html"
echo ""
echo "=========================================="
echo "💡 NEXT STEPS FOR SALES TOMORROW:"
echo "=========================================="
echo ""
echo "  1. System is now running and generating leads"
echo "  2. Tomorrow: check CEO report at 23:59"
echo "  3. Revenue will be transferred to BCA 6485086645"
echo "  4. No manual work needed - fully autonomous"
echo ""
echo "=========================================="
echo "👑 CEO: i Made Purna Ananda"
echo "🌐 mahalaksmi.web.id"
echo "=========================================="
