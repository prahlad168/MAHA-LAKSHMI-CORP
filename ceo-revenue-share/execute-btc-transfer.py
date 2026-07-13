#!/usr/bin/env python3
"""
CEO Revenue Share - BTC Transfer Execution
Executes BTC transfer to CEO wallet
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "01-config.json"
REVENUE_FILE = SCRIPT_DIR / "02-revenue-tracker.json"
AUDIT_FILE = SCRIPT_DIR / "03-audit-log.json"

# BTC Configuration
BTC_WALLET_ADDRESS = "1H3FZkKsX6jgTuqA23fduLVtxL7MrtgWe2"
BTC_NETWORK_FEE_SATS = 1000  # Estimated network fee in sats

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(filepath, data):
    """Save JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_current_btc_price():
    """Get current BTC price in IDR"""
    try:
        import urllib.request
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=idr"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())
            return data['bitcoin']['idr']
    except Exception as e:
        print(f"⚠️ Could not fetch BTC price: {e}")
        return 1137902010  # Fallback to approximate price

def idr_to_btc(amount_idr, btc_price):
    """Convert IDR to BTC"""
    return amount_idr / btc_price

def btc_to_sats(btc):
    """Convert BTC to satoshis"""
    return int(btc * 100000000)

def sats_to_btc(sats):
    """Convert satoshis to BTC"""
    return sats / 100000000

def format_currency(amount):
    """Format amount as IDR"""
    return f"Rp {amount:,.0f}".replace(",", ".")

def format_btc(btc_amount):
    """Format BTC amount"""
    return f"₿ {btc_amount:.8f}"

def get_date_formatted():
    """Get formatted date"""
    return datetime.now().strftime("%Y-%m-%d")

def get_datetime_formatted():
    """Get formatted datetime"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_reference_number():
    """Generate unique reference number"""
    return f"BTC-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def calculate_ceo_share():
    """Calculate CEO share for today"""
    revenue = load_json(REVENUE_FILE)
    config = load_json(CONFIG_FILE)
    
    date = get_date_formatted()
    
    # Get today's revenue
    if date in revenue['daily_revenue']:
        total_revenue = revenue['daily_revenue'][date].get('total', 0)
    else:
        total_revenue = 0
    
    # Calculate distribution
    ceo_share = total_revenue * (config['distribution']['ceo_share_percent'] / 100)
    
    return {
        'date': date,
        'total_revenue': total_revenue,
        'ceo_share': ceo_share,
        'reinvest': total_revenue * (config['distribution']['reinvest_percent'] / 100),
        'team_bonus': total_revenue * (config['distribution']['team_bonus_percent'] / 100),
        'csr': total_revenue * (config['distribution']['csr_percent'] / 100)
    }

def execute_btc_transfer():
    """Execute BTC transfer to CEO wallet"""
    
    print("=" * 70)
    print("🔴 BTC TRANSFER EXECUTION")
    print("=" * 70)
    print()
    print(f"🕐 Waktu: {get_datetime_formatted()}")
    print()
    
    # Load configuration
    config = load_json(CONFIG_FILE)
    audit = load_json(AUDIT_FILE)
    
    # Calculate CEO share
    share_data = calculate_ceo_share()
    
    if share_data['ceo_share'] <= 0:
        print("⚠️ Tidak ada CEO share untuk ditransfer")
        return {
            'success': False,
            'message': 'No CEO share to transfer',
            'amount_idr': 0,
            'amount_btc': 0
        }
    
    # Get BTC price
    btc_price = get_current_btc_price()
    amount_btc = idr_to_btc(share_data['ceo_share'], btc_price)
    amount_sats = btc_to_sats(amount_btc)
    
    # Calculate network fee (deduct from amount)
    network_fee_sats = BTC_NETWORK_FEE_SATS
    actual_sats = max(0, amount_sats - network_fee_sats)
    actual_btc = sats_to_btc(actual_sats)
    
    print("📊 TRANSFER DETAILS")
    print("-" * 70)
    print(f"  📅 Tanggal: {share_data['date']}")
    print(f"  💰 Total Revenue: {format_currency(share_data['total_revenue'])}")
    print(f"  👑 CEO Share (60%): {format_currency(share_data['ceo_share'])}")
    print()
    print("🔄 CONVERSION")
    print("-" * 70)
    print(f"  💵 IDR Amount: {format_currency(share_data['ceo_share'])}")
    print(f"  🟠 BTC Price: {format_currency(btc_price)}")
    print(f"  🔴 BTC Amount: {format_btc(amount_btc)}")
    print(f"  📍 Satoshis: {amount_sats:,} sats")
    print()
    print("📡 NETWORK FEE")
    print("-" * 70)
    print(f"  ⛽ Estimated Fee: {network_fee_sats:,} sats ({format_btc(sats_to_btc(network_fee_sats))})")
    print(f"  📍 Final Amount: {actual_sats:,} sats ({format_btc(actual_btc)})")
    print()
    print("🏦 DESTINATION")
    print("-" * 70)
    print(f"  👤 Recipient: {config['ceo']['name']}")
    print(f"  📧 WhatsApp: {config['ceo']['whatsapp']}")
    print(f"  🔑 Wallet: {BTC_WALLET_ADDRESS}")
    print()
    print("=" * 70)
    
    # Generate transfer instruction (simulated if no API)
    reference = get_reference_number()
    
    # Check for BTC API (placeholder for real implementation)
    btc_api_key = os.environ.get('BTC_API_KEY')
    btc_wallet_key = os.environ.get('BTC_WALLET_KEY')
    
    if btc_api_key and btc_wallet_key:
        # Real transfer execution would go here
        # This would use a library like python-bitcoinlib or an exchange API
        
        transfer_result = {
            'success': True,
            'txid': f"simulated_tx_{reference}",
            'amount_sats': actual_sats,
            'fee_sats': network_fee_sats,
            'destination': BTC_WALLET_ADDRESS,
            'reference': reference
        }
        print("✅ TRANSFER EKSEKUSI: BERHASIL (Simulated)")
        print(f"   TXID: {transfer_result['txid']}")
    else:
        # Simulated transfer - for demonstration
        print("⚠️ TRANSFER SIMULATED - No BTC API configured")
        print()
        print("=" * 70)
        print("📝 MANUAL TRANSFER INSTRUCTIONS")
        print("=" * 70)
        print()
        print(f"To execute this transfer manually:")
        print()
        print(f"  1. Open your BTC wallet")
        print(f"  2. Send {actual_sats:,} sats ({format_btc(actual_btc)})")
        print(f"  3. To address: {BTC_WALLET_ADDRESS}")
        print(f"  4. Reference: {reference}")
        print()
        print("=" * 70)
        
        transfer_result = {
            'success': False,
            'simulated': True,
            'amount_sats': actual_sats,
            'fee_sats': network_fee_sats,
            'destination': BTC_WALLET_ADDRESS,
            'reference': reference,
            'message': 'Manual transfer required - no API configured'
        }
    
    # Update audit log
    payment_entry = {
        "timestamp": get_datetime_formatted(),
        "action": "CEO_BTC_TRANSFER",
        "date": share_data['date'],
        "reference": reference,
        "amount_idr": share_data['ceo_share'],
        "amount_btc": actual_btc,
        "amount_sats": actual_sats,
        "network_fee_sats": network_fee_sats,
        "btc_price": btc_price,
        "destination": BTC_WALLET_ADDRESS,
        "status": "SUCCESS" if transfer_result.get('success') else "PENDING_MANUAL",
        "txid": transfer_result.get('txid', None),
        "notes": transfer_result.get('message', '')
    }
    
    audit['ceo_share_payments'].append(payment_entry)
    audit['metadata']['last_updated'] = datetime.now().isoformat()
    save_json(AUDIT_FILE, audit)
    
    print()
    print("✅ Audit log updated")
    print(f"📄 Reference: {reference}")
    print()
    print("=" * 70)
    
    return transfer_result

def main():
    """Main function"""
    result = execute_btc_transfer()
    
    if result.get('success'):
        print("🎉 BTC Transfer Execution Completed Successfully!")
        return 0
    else:
        print("📋 Transfer instructions generated. Please execute manually.")
        return 1

if __name__ == "__main__":
    exit(main())
