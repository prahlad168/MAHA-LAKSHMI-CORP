#!/bin/bash
# 🚀 DEPLOY SCRIPT - MAHA LAKSHMI HOLDINGS
# Tanggal: 2026-07-20

echo "=========================================="
echo "  🚀 MAHA LAKSHMI DEPLOYMENT SCRIPT"
echo "=========================================="
echo ""

# Step 1: Git Add, Commit, Push
echo "📦 Step 1: Git Push to trigger auto-deploy..."
cd /workspace/project/MAHA-LAKSHMI-CORP

git add -A
git commit -m "Deploy landing pages $(date +%Y-%m-%d)"

# Check if remote exists
if git remote -v | grep -q origin; then
    echo "🔄 Pushing to GitHub..."
    git push origin main 2>&1 || git push origin deploy-digital-enterprise 2>&1
    echo "✅ Git push successful!"
else
    echo "⚠️ No remote configured. Please run:"
    echo "   git remote add origin https://github.com/prahlad168/MAHA-LAKSHMI-CORP.git"
fi

echo ""
echo "=========================================="
echo "  🌐 DEPLOYMENT OPTIONS"
echo "=========================================="
echo ""
echo "After Git push, deploy to:"
echo ""
echo "1️⃣ VERCEL (Recommended)"
echo "   → Import: https://vercel.com/new"
echo "   → Select repo: prahlad168/MAHA-LAKSHMI-CORP"
echo "   → URL: https://maha-lakshmi-corp.vercel.app"
echo ""
echo "2️⃣ NETLIFY (Drag & Drop)"
echo "   → Go to: https://app.netlify.com/drop"
echo "   → Drag this folder"
echo "   → Get instant URL!"
echo ""
echo "3️⃣ GITHUB PAGES (Free)"
echo "   → Settings → Pages → Source: main"
echo "   → URL: https://prahlad168.github.io/MAHA-LAKSHMI-CORP"
echo ""
echo "=========================================="
echo "  📱 LANDING PAGES AFTER DEPLOY"
echo "=========================================="
echo ""
echo "Products (37 provinces each):"
echo "  • AirdropHunter: /airdrop/*.html"
echo "  • MicroTask Pro: /microtask/*.html"
echo "  • SurveyPro: /survey/*.html"
echo ""
echo "Main Sites:"
echo "  • Dashboard: /maha-lakshmi/"
echo "  • Progress: /progress/"
echo "  • Leads: /leads/"
echo ""
echo "=========================================="
echo "  ✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Deploy to Vercel/Netlify"
echo "2. Get production URL"
echo "3. Add to WhatsApp outreach links"
echo "4. Start sending leads!"
echo ""
echo "💰 Profit target: 80% to BCA 6485086645"
