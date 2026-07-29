#!/bin/bash
# 🚀 MAHA LAKSHMI AUTONOMOUS SALES AGENT
# CEO MODE: Start all agents and receive revenue reports only

echo "=========================================="
echo "👑 MAHA LAKSHMI - AUTONOMOUS SALES AGENT"
echo "=========================================="
echo ""
echo "Starting autonomous sales system..."
echo "Domain: mahalaksmi.web.id"
echo "CEO: i Made Purna Ananda"
echo ""
echo "🤖 Agents starting:"
echo "  1. Sales Agent - handles all outreach and closing"
echo "  2. Finance Agent - handles all payments and payouts"
echo "  3. Market Analyzer - analyzes trends and optimizes"
echo "  4. Self-Improvement - continuously improves performance"
echo ""
echo "👑 CEO receives:"
echo "  - Daily revenue reports"
echo "  - Financial summaries"
echo "  - Transfer confirmations to BCA 6485086645"
echo ""
echo "=========================================="
echo ""

# Create necessary directories
mkdir -p autonomous-sales-agent/logs
mkdir -p autonomous-sales-agent/data

# Check Python version
python3 --version || { echo "Error: Python 3 required"; exit 1; }

# Install dependencies if needed
if [ ! -f "requirements-agent.txt" ]; then
    echo "📦 Installing dependencies..."
    pip3 install requests python-dotenv schedule --quiet
fi

# Start the orchestrator
echo "🚀 Starting autonomous orchestrator..."
echo ""

python3 autonomous-sales-agent/orchestrator.py
