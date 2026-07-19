#!/bin/bash
# Deploy Crypto Payment System to Railway

echo "🚀 Crypto Payment System - Deploy Script"
echo "======================================"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if logged in
echo "📋 Checking Railway login..."
railway whoami &>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ Not logged in to Railway"
    echo ""
    echo "📝 To deploy, you need to:"
    echo "1. Go to https://railway.app"
    echo "2. Create account / Login"
    echo "3. Connect GitHub repository"
    echo "4. Deploy this project"
    echo ""
    echo "Or run: railway login"
    exit 1
fi

echo "✅ Logged in to Railway"

# Deploy
echo "📦 Deploying..."
railway up --service crypto-payment

# Get URL
echo ""
echo "🌐 Deployment URL:"
railway status --json 2>/dev/null || railway status

echo ""
echo "✅ Deploy complete!"
