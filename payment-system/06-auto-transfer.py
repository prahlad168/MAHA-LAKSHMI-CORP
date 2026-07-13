#!/usr/bin/env python3
"""
BCA Auto-Transfer System
Handles automatic transfer to CEO BCA account
"""

import json
import os
from datetime import datetime
from pathlib import Path
import hashlib

# Configuration
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "02-CONFIG.json"
PAYMENT_LOG = SCRIPT_DIR / "payment-log.json"

# CEO Destination
CEO_DESTINATION = {
    "bank": "BCA",
    "account_number": "6485086645",
    "account_name": "i Made Purna Ananda"
}

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def format_currency(amount):
    return f"Rp {amount:,.0f}".replace(",", ".")

def generate_reference():
    return f"CEO-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def load_payment_log():
    if PAYMENT_LOG.exists():
        return load_json(PAYMENT_LOG)
    else:
        return {"transfers": [], "total_sent": 0}

def save_payment_log(log):
    save_json(PAYMENT_LOG, log)

def get_available_transfer_methods():
    """Get available transfer methods based on configured APIs"""
    methods = []
    
    # Check Flip API
    if os.environ.get('FLIP_API_KEY'):
        methods.append({
            "name": "Flip",
            "type": "bank_transfer",
            "fee": 2500,
            "min_amount": 10000,
            "max_amount": 50000000,
            "status": "available"
        })
    
    # Check BCA API (if configured)
    config_file = SCRIPT_DIR / "02-CONFIG.json"
    if config_file.exists():
        config = load_json(config_file)
        if config.get('bca_api'):
            methods.append({
                "name": "BCA Transfer",
                "type": "bca_direct",
                "fee": 0,
                "min_amount": 1,
                "max_amount": 100000000,
                "status": "available"
            })
    
    # Manual transfer always available
    methods.append({
        "name": "Manual (Instructions)",
        "type": "manual",
        "fee": 0,
        "min_amount": 1,
        "max_amount": 999999999,
        "status": "always_available"
    })
    
    return methods

def calculate_transfer(amount_idr, method_fee=0):
    """Calculate transfer with fees"""
    fee = method_fee
    net_amount = amount_idr - fee
    
    return {
        "gross_amount": amount_idr,
        "fee": fee,
        "net_amount": net_amount,
        "transfer_amount": net_amount  # Amount that goes to CEO
    }

def execute_transfer(amount_idr, method="manual", method_config=None):
    """
    Execute transfer to CEO account
    
    Args:
        amount_idr: Amount in IDR
        method: Transfer method (flip, bca_direct, manual)
        method_config: API keys and config for the method
    
    Returns:
        dict with transfer result
    """
    log = load_payment_log()
    reference = generate_reference()
    
    print("=" * 70)
    print("🏦 CEO AUTO-TRANSFER SYSTEM")
    print("=" * 70)
    print()
    print(f"🕐 Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Calculate amounts
    calc = calculate_transfer(amount_idr)
    
    print("📊 TRANSFER DETAILS")
    print("-" * 70)
    print(f"  💰 Amount to CEO: {format_currency(calc['transfer_amount'])}")
    print(f"  🏦 Destination Bank: {CEO_DESTINATION['bank']}")
    print(f"  🔢 Account Number: {CEO_DESTINATION['account_number']}")
    print(f"  👤 Account Name: {CEO_DESTINATION['account_name']}")
    print(f"  📝 Reference: {reference}")
    print()
    
    transfer_result = {
        "reference": reference,
        "timestamp": datetime.now().isoformat(),
        "amount_gross": amount_idr,
        "amount_net": calc['net_amount'],
        "fee": calc['fee'],
        "method": method,
        "destination": CEO_DESTINATION,
        "status": "pending"
    }
    
    if method == "flip":
        # Execute via Flip API
        flip_api_key = os.environ.get('FLIP_API_KEY') or method_config.get('api_key')
        if flip_api_key:
            result = _execute_flip_transfer(calc['net_amount'], flip_api_key)
            transfer_result.update(result)
        else:
            print("❌ Flip API Key not configured!")
            return {"success": False, "error": "Flip API Key not configured"}
    
    elif method == "bca_direct":
        # Execute via BCA API
        print("❌ BCA Direct API not configured yet!")
        print("   Please configure BCA API in 02-CONFIG.json")
        return {"success": False, "error": "BCA API not configured"}
    
    else:
        # Manual transfer - just generate instructions
        print("📝 MANUAL TRANSFER INSTRUCTIONS")
        print("-" * 70)
        print()
        print("  Buka BCA Mobile / Internet Banking:")
        print()
        print(f"  🏦 Transfer ke: {CEO_DESTINATION['bank']}")
        print(f"  🔢 No Rekening: {CEO_DESTINATION['account_number']}")
        print(f"  👤 Nama: {CEO_DESTINATION['account_name']}")
        print(f"  💰 Jumlah: {format_currency(calc['net_amount'])}")
        print(f"  📝 Catatan: {reference}")
        print()
        print("=" * 70)
        
        transfer_result["status"] = "instructions_generated"
        transfer_result["instructions"] = {
            "bank": CEO_DESTINATION['bank'],
            "account": CEO_DESTINATION['account_number'],
            "name": CEO_DESTINATION['account_name'],
            "amount": calc['net_amount'],
            "note": reference
        }
    
    # Save to log
    log["transfers"].append(transfer_result)
    log["total_sent"] = log.get("total_sent", 0) + (calc['net_amount'] if transfer_result['status'] == 'success' else 0)
    save_payment_log(log)
    
    return transfer_result

def _execute_flip_transfer(amount, api_key):
    """Execute transfer via Flip API"""
    import urllib.request
    import urllib.parse
    
    url = "https://flip.id/api/transfer"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "account_number": CEO_DESTINATION['account_number'],
        "bank_code": "BCA",
        "amount": amount,
        "remark": f"CEO Revenue Share - {datetime.now().strftime('%Y-%m-%d')}"
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read())
            
            if result.get('status') == 'success':
                return {
                    "success": True,
                    "status": "success",
                    "flip_id": result.get('id'),
                    "tx_hash": result.get('transaction_id')
                }
            else:
                return {
                    "success": False,
                    "error": result.get('message', 'Transfer failed')
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def setup_flip_api():
    """Setup Flip API for transfer"""
    print("=" * 70)
    print("📱 FLIP API SETUP")
    print("=" * 70)
    print()
    print("Flip adalah service transfer antar-bank dengan fee murah!")
    print()
    print("Step 1: Daftar Flip Business")
    print("  Buka: https://flip.id/business")
    print()
    print("Step 2: Dapat API Key")
    print("  Login → Settings → API Access → Create API Key")
    print()
    print("Step 3: Set API Key")
    print("  export FLIP_API_KEY='your_api_key_here'")
    print()
    print("=" * 70)

def main():
    """Main function"""
    import sys
    
    # Check arguments
    if len(sys.argv) > 1:
        try:
            amount = int(sys.argv[1])
        except ValueError:
            print("Usage: python3 06-auto-transfer.py [amount_idr]")
            return 1
        
        method = sys.argv[2] if len(sys.argv) > 2 else "manual"
        result = execute_transfer(amount, method)
        
        if result.get('success'):
            print("✅ Transfer successful!")
        else:
            print("⏳ Transfer instructions generated - please execute manually")
    else:
        # Show available methods and payment log
        print("=" * 70)
        print("🏦 CEO AUTO-TRANSFER SYSTEM")
        print("=" * 70)
        print()
        
        # Show available methods
        methods = get_available_transfer_methods()
        print("📡 Available Transfer Methods:")
        print()
        for i, m in enumerate(methods, 1):
            status_icon = "✅" if m['status'] == 'available' else "⚠️"
            print(f"  {i}. {status_icon} {m['name']}")
            print(f"     Fee: Rp {m['fee']:,}")
            print(f"     Range: Rp {m['min_amount']:,} - Rp {m['max_amount']:,}")
            print()
        
        # Show recent transfers
        log = load_payment_log()
        print("📋 Recent Transfers:")
        print()
        
        if log.get('transfers'):
            for t in log['transfers'][-5:]:
                status = "✅" if t.get('status') == 'success' else "⏳"
                print(f"  {status} {t['reference']} - {format_currency(t['amount_net'])}")
                print(f"     {t['timestamp'][:10]}")
                print()
        else:
            print("  No transfers yet")
            print()
        
        print(f"💰 Total Sent to CEO: {format_currency(log.get('total_sent', 0))}")
        print()
        
        print("=" * 70)
        print()
        print("Usage:")
        print("  python3 06-auto-transfer.py 600000")
        print("  python3 06-auto-transfer.py 600000 flip")
        print()
    
    return 0

if __name__ == "__main__":
    exit(main())
