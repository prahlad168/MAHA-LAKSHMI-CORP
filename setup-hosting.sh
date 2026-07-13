#!/bin/bash
# ============================================
# MAHA LAKSHMI AIOS - Hosting Setup Script
# Run this on your hosting server
# ============================================

echo "============================================"
echo "  MAHA LAKSHMI AIOS - HOSTING SETUP"
echo "============================================"
echo ""

# Configuration
REPO_URL="https://github.com/prahlad168/Bot_Molty5.git"
HOST_PATH="/home/payangan/public_html"
WEBHOOK_SECRET="gauranga-deploy-2026"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

# Check if running as root or appropriate user
echo "📁 Current directory: $(pwd)"
echo "📁 Target path: $HOST_PATH"
echo ""

# Step 1: Navigate to hosting path
echo "Step 1: Navigating to hosting path..."
cd $HOST_PATH || { error "Cannot access $HOST_PATH"; exit 1; }
success "Changed to $HOST_PATH"

# Step 2: Clone or Pull repository
echo ""
echo "Step 2: Syncing with GitHub..."
if [ -d ".git" ]; then
    echo "Git repository exists. Pulling latest..."
    git pull origin main
else
    echo "Cloning repository..."
    git clone $REPO_URL .
fi
success "Repository synced"

# Step 3: Setup Webhook
echo ""
echo "Step 3: Creating webhook.php..."
cat > webhook.php << 'WEBHOOK_EOF'
<?php
/**
 * MAHA LAKSHMI - GitHub Webhook Auto-Deploy
 */

$secret = 'gauranga-deploy-2026';
$repo_path = __DIR__;

// Verify secret
if (isset($_GET['secret']) && $_GET['secret'] !== $secret) {
    http_response_code(403);
    echo "Invalid secret";
    exit;
}

// Git pull
$output = shell_exec("cd $repo_path && git pull origin main 2>&1");

// Log
file_put_contents("$repo_path/deploy.log", date("Y-m-d H:i:s") . " - $output\n", FILE_APPEND);

echo "OK: $output";
WEBHOOK_EOF
success "webhook.php created"

# Step 4: Setup Cron Job
echo ""
echo "Step 4: Setting up cron job for daily report..."
CRON_JOB="0 6 * * * /usr/bin/php $HOST_PATH/MAHA-OS/notifications/api/send-report.php >> $HOST_PATH/cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "send-report.php"; then
    warning "Cron job already exists"
else
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    success "Cron job added"
fi

# Step 5: Create necessary directories
echo ""
echo "Step 5: Creating directories..."
mkdir -p logs
mkdir -p temp
success "Directories created"

# Step 6: Set permissions
echo ""
echo "Step 6: Setting permissions..."
chmod 755 logs temp
chmod 644 *.php 2>/dev/null
chmod 644 MAHA-OS/**/*.php 2>/dev/null
success "Permissions set"

# Step 7: Display summary
echo ""
echo "============================================"
echo "  SETUP COMPLETE!"
echo "============================================"
echo ""
echo "📁 Files location: $HOST_PATH"
echo ""
echo "🔗 Important URLs:"
echo "   Login: $HOST_PATH/MAHA-OS/auth/login.php"
echo "   Daily Report API: $HOST_PATH/MAHA-OS/notifications/api/send-report.php"
echo "   Webhook: $HOST_PATH/webhook.php"
echo ""
echo "⏰ Cron job: Daily at 6:00 AM WIB"
echo ""
echo "🔐 GitHub Webhook URL:"
echo "   https://payanganhospital.gianyarkab.go.id/webhook.php?secret=$WEBHOOK_SECRET"
echo ""
echo "📧 Email Report: ceo@mahalakshmi.id"
echo "📱 WhatsApp: wa.me/6281337558787"
echo ""
echo "============================================"
echo ""
