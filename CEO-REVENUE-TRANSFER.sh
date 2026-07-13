#!/bin/bash
# 🚀 CEO REVENUE TRANSFER - DEPLOY & RUN
# MAHA LAKSHMI HOLDINGS
# CEO: i Made Purna Ananda
# BTC Wallet: 1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2 (Tokocrypto)

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║     🚀 CEO REVENUE TRANSFER - DEPLOY & RUN                  ║"
echo "║     MAHA LAKSHMI HOLDINGS                               ║"
echo "║     CEO: i Made Purna Ananda                            ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_info() { echo -e "${YELLOW}[INFO]${NC} $1"; }

# ============================================
# PHASE 1: UPDATE REVENUE DATA
# ============================================
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  PHASE 1: CEO REVENUE CALCULATION"
echo "═══════════════════════════════════════════════════════════"
echo ""

python3 << 'PYTHON_EOF'
import json
from datetime import datetime

# Load revenue tracker
with open('ceo-revenue-share/02-revenue-tracker.json', 'r') as f:
    revenue = json.load(f)

# Load config
with open('ceo-revenue-share/01-config.json', 'r') as f:
    config = json.load(f)

# Calculate total revenue
total_revenue = revenue['monthly_summary']['total_revenue']

# CEO share calculation (60%)
ceo_percentage = config['profit_distribution']['ceo_share_percentage']
ceo_share_idr = total_revenue * (ceo_percentage / 100)

# BTC conversion
btc_price_idr = 165000000  # Approximate
ceo_share_btc = ceo_share_idr / btc_price_idr

# Print calculation
print("╔════════════════════════════════════════════════════════════╗")
print("║       📊 CEO REVENUE CALCULATION                       ║")
print("╠════════════════════════════════════════════════════════════╣")
print("║                                                            ║")
print(f"║  📅 Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC        ║")
print("║                                                            ║")
print("╠════════════════════════════════════════════════════════════╣")
print("║                                                            ║")
print("║  💰 REVENUE BREAKDOWN:                               ║")
print("║                                                            ║")
print(f"║  • Global Digital Sales:     Rp {total_revenue:>15,}  ║")
print(f"║  • MAHA LAKSHMI Companies:   Rp {0:>15,}  ║")
print(f"║  • Other Sources:             Rp {0:>15,}  ║")
print("║  ───────────────────────────────────────────────────   ║")
print(f"║  TOTAL REVENUE:              Rp {total_revenue:>15,}  ║")
print("║                                                            ║")
print("╠════════════════════════════════════════════════════════════╣")
print("║                                                            ║")
print("║  👑 CEO SHARE CALCULATION (60%):                     ║")
print("║                                                            ║")
print(f"║  Total Revenue:          Rp {total_revenue:>15,}  ║")
print(f"║  CEO Percentage:                      {ceo_percentage:>3}%  ║")
print("║  ───────────────────────────────────────────────────   ║")
print(f"║  CEO SHARE (IDR):       Rp {int(ceo_share_idr):>15,}  ║")
print(f"║  CEO SHARE (BTC):        {ceo_share_btc:>15.8f} BTC  ║")
print("║                                                            ║")
print("╠════════════════════════════════════════════════════════════╣")
print("║                                                            ║")
print("║  🪙 TRANSFER DETAILS:                                  ║")
print("║                                                            ║")
print("║  Platform:     TOKOCRYPTO                               ║")
print("║  Network:      BITCOIN (BTC)                            ║")
print("║  Wallet:       1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2      ║")
print("║                                                            ║")
print(f"║  Amount:      {ceo_share_btc:.8f} BTC                           ║")
print(f"║  Value:       Rp {int(ceo_share_idr):,}                             ║")
print("║                                                            ║")
print("╚════════════════════════════════════════════════════════════╝")

# Save to file for reference
with open('ceo-revenue-share/latest-transfer.txt', 'w') as f:
    f.write(f"CEO Revenue Transfer - {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC\n")
    f.write(f"Total Revenue: Rp {total_revenue:,}\n")
    f.write(f"CEO Share (60%): Rp {int(ceo_share_idr):,}\n")
    f.write(f"CEO Share (BTC): {ceo_share_btc:.8f} BTC\n")
    f.write(f"\nTransfer to:\n")
    f.write(f"Platform: Tokocrypto\n")
    f.write(f"Wallet: 1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2\n")
    f.write(f"Amount: {ceo_share_btc:.8f} BTC\n")

print("\n✅ Revenue calculation saved!")
PYTHON_EOF

# ============================================
# PHASE 2: TRIGGER ALL AUTOMATIONS
# ============================================
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  PHASE 2: TRIGGERING ALL AUTOMATIONS"
echo "═══════════════════════════════════════════════════════════"
echo ""

# List of automation IDs to trigger
AUTOMATIONS=(
  "4a8a8c40-3886-4002-b2f7-95c7d3837412:AI WhatsApp Automation"
  "b4d014ab-97b8-41ec-9916-fe9204853162:AI Content Generator"
  "829a4fbd-bea1-4534-a4be-468c145ba0ae:AI Hotel Solution"
  "f9d2743d-1092-4001-9b54-7321636d8b5a:AI Restaurant Solution"
  "9e31ac70-05bd-409f-9915-e36d957e03b4:AI Medical Assistant"
  "6a5f7318-52ca-4a7f-9fb8-4432fe3c61fe:AI CEO Strategy Agent"
  "da38ccdc-f332-4ebe-a40e-7502707f46a8:AI Market Expansion Indonesia"
  "735ed6c0-11b7-4e32-bf24-411ecbec4ecc:AI Market Expansion Global"
  "fe650676-37cd-4e32-a28f-69e37050be21:AI Marketing Assistant"
  "496b2c4c-1806-451c-82b6-b7627e0123d8:AI Finance Assistant"
  "b9b44919-4361-49af-96cc-7fc6423774c8:AI Government Solution"
  "c3c98dd9-4d6c-499b-a054-6e72befd657f:Content Marketing Agent"
  "5085da1b-0a6d-4afc-bc64-feb934bd9c68:SaaS Sales Agent"
)

for auto in "${AUTOMATIONS[@]}"; do
  IFS=':' read -r id name <<< "$auto"
  log_info "Triggering $name..."
  response=$(curl -s -X POST "https://app.all-hands.dev/api/automation/v1/${id}/dispatch" \
    -H "Authorization: Bearer ${OPENHANDS_API_KEY}")
  if echo "$response" | grep -q "PENDING\|RUNNING"; then
    log_success "$name triggered!"
  else
    log_error "Failed to trigger $name"
  fi
done

# ============================================
# PHASE 3: GIT PUSH & DEPLOY
# ============================================
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  PHASE 3: GIT PUSH & DEPLOY"
echo "═══════════════════════════════════════════════════════════"
echo ""

log_step "Adding all files..."
git add -A

log_step "Committing changes..."
git commit -m "🚀 CEO Revenue Transfer - $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null || echo "Nothing to commit"

log_step "Pushing to GitHub..."
git push origin ceo-revenue-share-system 2>&1 && log_success "Git push successful!" || log_error "Git push failed"

# ============================================
# PHASE 4: FINAL SUMMARY
# ============================================
echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ DEPLOYMENT COMPLETE                         ║"
echo "╠════════════════════════════════════════════════════════════════════════╣"
echo "║                                                                    ║"
echo "║  🌐 GitHub: https://github.com/prahlad168/MAHA-LAKSHMI-CORP     ║"
echo "║  📱 GitHub Pages: https://prahlad168.github.io/MAHA-LAKSHMI-CORP ║"
echo "║                                                                    ║"
echo "║  🤖 Automations Triggered: 13                                    ║"
echo "║  📊 Revenue Calculated: Ready                                     ║"
echo "║                                                                    ║"
echo "╠════════════════════════════════════════════════════════════════════════╣"
echo "║                                                                    ║"
echo "║  🪙 CEO TRANSFER - MANUAL ACTION REQUIRED:                       ║"
echo "║                                                                    ║"
echo "║  Platform:  TOKOCRYPTO                                            ║"
echo "║  Wallet:    1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2                 ║"
echo "║  Network:   Bitcoin (BTC)                                         ║"
echo "║                                                                    ║"
echo "║  Amount:    [CALCULATED FROM REVENUE]                            ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🎯 MOTTO: 'ADA REVENUE = ADA TRANSFER! 🚀'"
echo ""
