#!/bin/bash
# CEO Revenue Share - Automation Setup
# Setup daily automation at 12:00 WITA

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  👑 CEO REVENUE SHARE - AUTOMATION SETUP              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Get the directory where script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📂 Working directory: $SCRIPT_DIR"
echo ""

# Make Python scripts executable
echo "🔧 Making scripts executable..."
chmod +x daily-execution.py
chmod +x add-revenue.py
chmod +x generate-report.py
chmod +x 04-CEO-SHARE-CALCULATOR.py
echo "   ✅ Done"
echo ""

# Check Python
echo "🐍 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ Python installed: $PYTHON_VERSION"
else
    echo "   ❌ Python3 not found"
    echo "   Please install Python3 first"
    exit 1
fi
echo ""

# Test imports
echo "🔍 Testing script imports..."
cd "$SCRIPT_DIR"
if python3 -c "import json" 2>/dev/null; then
    echo "   ✅ json module available"
else
    echo "   ❌ json module not available"
    exit 1
fi
echo ""

# Create directories
echo "📁 Creating directories..."
mkdir -p DAILY-REPORTS
echo "   ✅ DAILY-REPORTS/"
echo ""

# Show current status
echo "📊 CURRENT STATUS:"
echo "─────────────────────────────────────────────────────"
python3 daily-execution.py
echo ""

# Show menu
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  AUTOMATION OPTIONS                                   ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                        ║"
echo "║  OPTION 1: Cron Job (Linux/Mac)                        ║"
echo "║  ───────────────────────────────────────────────────── ║"
echo "║  Run this command to add cron job:                    ║"
echo "║                                                        ║"
echo "║  crontab -e                                           ║"
echo "║                                                        ║"
echo "║  Add this line:                                       ║"
echo "║  0 12 * * * cd $SCRIPT_DIR && python3 daily-execution.py >> /dev/null 2>&1"
echo "║                                                        ║"
echo "║  This will run at 12:00 WITA (04:00 UTC) daily       ║"
echo "║                                                        ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                        ║"
echo "║  OPTION 2: Systemd Timer (Linux)                       ║"
echo "║  ───────────────────────────────────────────────────── ║"
echo "║  Create a systemd service and timer                   ║"
echo "║                                                        ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                        ║"
echo "║  OPTION 3: OpenHands Automation                       ║"
echo "║  ───────────────────────────────────────────────────── ║"
echo "║  Setup via OpenHands Cloud for cloud execution         ║"
echo "║                                                        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Instructions for OpenHands
echo "📋 OPENHANDS CLOUD SETUP INSTRUCTIONS:"
echo "─────────────────────────────────────────────────────────"
echo ""
echo "1. Login to OpenHands Cloud"
echo "2. Create new automation with:"
echo "   - Name: 'CEO Daily Revenue Share'"
echo "   - Schedule: '0 12 * * *' (12:00 WITA)"
echo "   - Timezone: 'Asia/Makassar'"
echo "   - Prompt: See below"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "PROMPT FOR OPENHANDS AUTOMATION:"
echo "═══════════════════════════════════════════════════════════════"
echo ""
cat << 'PROMPT'
You are the CEO Revenue Share Execution Agent for MAHA LAKSHMI HOLDINGS.

Every day at 12:00 WITA, execute the following:

1. Run the daily execution script:
   cd ceo-revenue-share && python3 daily-execution.py

2. Read the generated report from:
   ceo-revenue-share/DAILY-REPORTS/daily-report-YYYY-MM-DD.md

3. Send summary to WhatsApp (if configured):
   - Total revenue today
   - CEO share (60%)
   - BTC wallet address: 1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2

4. Update the CEO dashboard if available

Configuration:
- CEO: i Made Purna Ananda (Pak Pur)
- WhatsApp: 081337558787
- CEO Share: 60% of total revenue
- BTC Wallet: 1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2
PROMPT
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Ask to run test
echo "❓ Run test execution now? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Running test execution..."
    echo ""
    python3 daily-execution.py
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📁 Files created:"
echo "   - ceo-revenue-share/00-CEO-REVENUE-SHARE-MASTER.md"
echo "   - ceo-revenue-share/01-config.json"
echo "   - ceo-revenue-share/02-revenue-tracker.json"
echo "   - ceo-revenue-share/03-audit-log.json"
echo "   - ceo-revenue-share/add-revenue.py"
echo "   - ceo-revenue-share/daily-execution.py"
echo "   - ceo-revenue-share/generate-report.py"
echo "   - ceo-revenue-share/04-CEO-SHARE-CALCULATOR.py"
echo "   - ceo-revenue-share/DAILY-REPORTS/"
echo ""
