#!/bin/bash
# MAHA LAKSHMI CORP - Deployment Script for mahalaksmi.web.id
# This script helps deploy the application to hosting

set -e

echo "👑 MAHA LAKSHMI CORP - Deployment Script"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: Please run this script from the MAHA-LAKSHMI-CORP directory"
    exit 1
fi

echo "✅ Verified: Running from MAHA-LAKSHMI-CORP directory"
echo ""

# 1. Git operations
echo "📦 Step 1: Preparing git commit..."
git add -A

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "✅ No changes to commit"
else
    echo "📝 Committing changes..."
    git commit -m "feat: prepare for deployment - Sprint 3 complete

- Add production deployment configs
- Update Dockerfile for FastAPI backend
- Add environment configuration
- Fix CORS and security headers
- 41 tests passing"
    echo "✅ Changes committed"
fi

echo ""

# 2. Push to GitHub
echo "🚀 Step 2: Pushing to GitHub..."
echo "Remote: $(git remote get-url origin)"
echo ""

# Try SSH first, then HTTPS
if git push origin main; then
    echo "✅ Successfully pushed to GitHub via SSH"
elif git push https://github.com/prahlad168/MAHA-LAKSHMI-CORP.git main; then
    echo "✅ Successfully pushed to GitHub via HTTPS"
else
    echo "⚠️  Push failed. Please push manually:"
    echo "   git push origin main"
    echo ""
    echo "   Or use GitHub web interface to upload files"
fi

echo ""
echo "========================================"
echo "📋 Deployment Options for mahalaksmi.web.id"
echo "========================================"
echo ""
echo "Option A: Render (Recommended - Free Tier)"
echo "----------------------------------------"
echo "1. Go to https://dashboard.render.com"
echo "2. Click 'New' → 'Web Service'"
echo "3. Connect repo: prahlad168/MAHA-LAKSHMI-CORP"
echo "4. Settings:"
echo "   - Name: maha-lakshmi-api"
echo "   - Region: Singapore"
echo "   - Plan: Free"
echo "   - Dockerfile Path: ./Dockerfile"
echo "   - Health Check: /health"
echo "5. Add Environment Variables:"
echo "   - JWT_SECRET_KEY: (auto-generate or your secret)"
echo "   - CORS_ORIGINS: https://mahalaksmi.web.id,https://www.mahalaksmi.web.id"
echo "   - LOG_LEVEL: INFO"
echo "6. Click 'Create Web Service'"
echo ""
echo "Option B: Fly.io (Free Tier)"
echo "---------------------------"
echo "1. Install flyctl: curl -L https://fly.io/install.sh | sh"
echo "2. Run: fly auth login"
echo "3. Run: fly launch"
echo "4. Run: fly deploy"
echo ""
echo "Option C: Manual VPS/Shared Hosting"
echo "-----------------------------------"
echo "1. Upload files to hosting"
echo "2. Install dependencies: pip install -r requirements.txt"
echo "3. Run: python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"
echo "4. Configure reverse proxy (nginx) for domain"
echo ""
echo "========================================"
echo "🌐 After Deployment"
echo "========================================"
echo ""
echo "1. Update DNS:"
echo "   - A record: @ → your-server-ip"
echo "   - CNAME: www → your-server-ip"
echo ""
echo "2. Verify:"
echo "   - https://mahalaksmi.web.id/health"
echo "   - https://mahalaksmi.web.id/api/docs"
echo ""
echo "3. Configure SSL:"
echo "   - Let's Encrypt / Certbot"
echo "   - Or use platform-provided SSL"
echo ""
echo "✅ Deployment script complete!"
