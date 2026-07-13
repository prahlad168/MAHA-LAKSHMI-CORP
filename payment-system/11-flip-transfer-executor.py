#!/usr/bin/env python3
"""
FLIP AUTO-TRANSFER EXECUTOR
Executes automatic transfer from Company to CEO BCA Account

Usage:
    export FLIP_API_KEY="your_api_key"
    python3 11-flip-transfer-executor.py 600000
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "02-CONFIG.json"
PAYMENT_LOG = SCRIPT_DIR / "payment-log.json"
AUDIT_FILE = SCRIPT_DIR.parent / "ceo-revenue-share" / "03-audit-log.json"

# CEO Destination
CEO_DESTINATION = {
    "bank": "BCA",
    "bank_code": "BCA",
    "account_number": "6485086645",
    "account_name": "i Made Purna Ananda"
}

# Flip API
FLIP_API_URL = "https://flip.id/api/transfer"
FLIP_FEE = 2500  # Estimated fee per transfer

def load_json(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def format_currency(amount):
    return f"Rp {amount:,.0f}".replace(",", ".")

def get_datetime_formatted():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_reference():
    return f"FLIP-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def load_payment_log():
    if PAYMENT_LOG.exists():
        return load_json(PAYMENT_LOG)
    return {"transfers": [], "total_sent": 0}

def save_payment_log(log):
    save_json(PAYMENT_LOG, log)

def get_flip_api_key():
    """Get FLIP API key from environment or config"""
    api_key = os.environ.get('FLIP_API_KEY')
    if api_key:
        return api_key
    
    config = load_json(CONFIG_FILE)
    api_key = config.get('flip_api_key')
    if api_key and api_key != 'YOUR_FLIP_API_KEY':
        return api_key
    
    return None

def check_flip_balance(api_key):
    """Check FLIP account balance"""
    url = "https://flip.id/api/me"
    
    try:
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
            return {
                "success": True,
                "balance": data.get('balance', 0),
                "name": data.get('name', 'Unknown')
            }
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP Error: {e.code}",
            "message": e.read().decode() if e.fp else str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def execute_flip_transfer(amount, api_key, remark=""):
    """
    Execute transfer via FLIP API
    
    Args:
        amount: Amount in IDR
        api_key: FLIP API Key
        remark: Transfer remark/note
    
    Returns:
        dict with transfer result
    """
    reference = generate_reference()
    timestamp = get_datetime_formatted()
    
    # Build request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "account_number": CEO_DESTINATION["account_number"],
        "bank_code": CEO_DESTINATION["bank_code"],
        "amount": int(amount),
        "remark": remark or f"CEO Revenue Share - {datetime.now().strftime('%Y-%m-%d')}"
    }
    
    print("=" * 70)
    print("🔴 FLIP AUTO-TRANSFER")
    print("=" * 70)
    print()
    print(f"🕐 Waktu: {timestamp}")
    print()
    
    # Check balance first
    print("📊 CHECKING FLIP BALANCE...")
    balance_result = check_flip_balance(api_key)
    
    if not balance_result.get('success'):
        print(f"❌ Failed to check balance: {balance_result.get('error')}")
        print(f"   Message: {balance_result.get('message', 'N/A')}")
        return {
            "success": False,
            "reference": reference,
            "error": "Cannot check FLIP balance"
        }
    
    print(f"✅ Balance: {format_currency(balance_result.get('balance', 0))}")
    print(f"   Name: {balance_result.get('name', 'N/A')}")
    print()
    
    # Check if sufficient balance
    required = amount + FLIP_FEE
    if balance_result.get('balance', 0) < required:
        print(f"❌ INSUFFICIENT BALANCE!")
        print(f"   Required: {format_currency(required)}")
        print(f"   Available: {format_currency(balance_result.get('balance', 0))}")
        print(f"   Need additional: {format_currency(required - balance_result.get('balance', 0))}")
        return {
            "success": False,
            "reference": reference,
            "error": "Insufficient FLIP balance"
        }
    
    print("📋 TRANSFER DETAILS")
    print("-" * 70)
    print(f"   💰 Amount: {format_currency(amount)}")
    print(f"   🏦 Bank: {CEO_DESTINATION['bank']}")
    print(f"   🔢 Account: {CEO_DESTINATION['account_number']}")
    print(f"   👤 Name: {CEO_DESTINATION['account_name']}")
    print(f"   📝 Remark: {data['remark']}")
    print()
    
    # Execute transfer
    print("⏳ EXECUTING TRANSFER...")
    
    try:
        req = urllib.request.Request(
            FLIP_API_URL,
            data=json.dumps(data).encode(),
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read())
            
            print()
            print("=" * 70)
            print("✅ TRANSFER SUCCESS!")
            print("=" * 70)
            print()
            print(f"   🆔 FLIP ID: {result.get('id', 'N/A')}")
            print(f"   📋 Status: {result.get('status', 'N/A')}")
            print(f"   💵 Amount: {format_currency(amount)}")
            print(f"   🏦 Recipient: {CEO_DESTINATION['account_number']}")
            print()
            
            # Log success
            log = load_payment_log()
            transfer_record = {
                "reference": reference,
                "flip_id": result.get('id'),
                "timestamp": timestamp,
                "amount": amount,
                "fee": FLIP_FEE,
                "total_debited": amount + FLIP_FEE,
                "destination": CEO_DESTINATION,
                "remark": data['remark'],
                "status": "success",
                "response": result
            }
            log["transfers"].append(transfer_record)
            log["total_sent"] = log.get("total_sent", 0) + amount
            save_payment_log(log)
            
            return {
                "success": True,
                "reference": reference,
                "flip_id": result.get('id'),
                "status": result.get('status'),
                "amount": amount,
                "destination": CEO_DESTINATION
            }
            
    except urllib.error.HTTPError as e:
        error_message = e.read().decode() if e.fp else str(e)
        print()
        print("=" * 70)
        print("❌ TRANSFER FAILED!")
        print("=" * 70)
        print(f"   Error: {e.code} - {error_message}")
        print()
        
        return {
            "success": False,
            "reference": reference,
            "error": f"HTTP {e.code}: {error_message}"
        }
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ TRANSFER FAILED!")
        print("=" * 70)
        print(f"   Error: {str(e)}")
        print()
        
        return {
            "success": False,
            "reference": reference,
            "error": str(e)
        }

def update_audit_log(reference, amount, status, flip_id=None, error=None):
    """Update CEO revenue share audit log"""
    try:
        audit_file = SCRIPT_DIR.parent / "ceo-revenue-share" / "03-audit-log.json"
        audit = load_json(audit_file)
        
        payment_entry = {
            "timestamp": get_datetime_formatted(),
            "action": "CEO_FLIP_TRANSFER",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "reference": reference,
            "amount_idr": amount,
            "destination": f"FLIP → BCA {CEO_DESTINATION['account_number']}",
            "status": status,
            "flip_id": flip_id,
            "notes": error or "Transfer completed via FLIP"
        }
        
        if 'ceo_share_payments' not in audit:
            audit['ceo_share_payments'] = []
        
        audit['ceo_share_payments'].append(payment_entry)
        audit['metadata']['last_updated'] = datetime.now().isoformat()
        
        save_json(audit_file, audit)
        return True
    except Exception as e:
        print(f"⚠️ Could not update audit log: {e}")
        return False

def main():
    """Main function"""
    print()
    print("=" * 70)
    print("🔴 FLIP AUTO-TRANSFER EXECUTOR")
    print("=" * 70)
    print()
    
    # Check API key
    api_key = get_flip_api_key()
    
    if not api_key:
        print("❌ FLIP API KEY NOT CONFIGURED!")
        print()
        print("=" * 70)
        print("📋 SETUP INSTRUCTIONS")
        print("=" * 70)
        print()
        print("1. Daftar FLIP Business: https://flip.id/business")
        print()
        print("2. Set API Key:")
        print()
        print("   export FLIP_API_KEY='your_api_key_here'")
        print()
        print("   ATAU edit file: 02-CONFIG.json")
        print('   Tambahkan: "flip_api_key": "your_key_here"')
        print()
        print("3. Setor saldo ke FLIP:")
        print("   - Minimal Rp 10.000 + fee transfer Rp 2.500")
        print("   - Jadi minimal Rp 602.500 untuk transfer Rp 600.000")
        print()
        print("=" * 70)
        print()
        
        # Show manual transfer option
        if len(sys.argv) > 1:
            try:
                amount = int(sys.argv[1])
                print(f"📝 MANUAL TRANSFER INSTRUCTIONS")
                print("=" * 70)
                print()
                print(f"   Transfer MANUAL ke:")
                print(f"   🏦 Bank: {CEO_DESTINATION['bank']}")
                print(f"   🔢 No Rek: {CEO_DESTINATION['account_number']}")
                print(f"   👤 Nama: {CEO_DESTINATION['account_name']}")
                print(f"   💰 Jumlah: {format_currency(amount)}")
                print()
            except:
                pass
        
        return 1
    
    # Get amount from argument
    if len(sys.argv) > 1:
        try:
            amount = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid amount. Usage: python3 11-flip-transfer-executor.py 600000")
            return 1
    else:
        # Default to CEO share (60% of Rp 1.000.000)
        amount = 600000
        print(f"📊 Using default CEO share: {format_currency(amount)}")
    
    # Execute transfer
    remark = "CEO Revenue Share - MAHA LAKSHMI HOLDINGS"
    if len(sys.argv) > 2:
        remark = sys.argv[2]
    
    result = execute_flip_transfer(amount, api_key, remark)
    
    # Update audit log
    if result.get('success'):
        update_audit_log(
            reference=result.get('reference'),
            amount=amount,
            status="SUCCESS",
            flip_id=result.get('flip_id')
        )
    else:
        update_audit_log(
            reference=result.get('reference'),
            amount=amount,
            status="FAILED",
            error=result.get('error')
        )
    
    # Summary
    print()
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print()
    
    if result.get('success'):
        print(f"✅ Transfer BERHASIL!")
        print(f"   Reference: {result.get('reference')}")
        print(f"   FLIP ID: {result.get('flip_id')}")
        print(f"   Amount: {format_currency(amount)}")
        print(f"   Destination: BCA {CEO_DESTINATION['account_number']}")
        print()
        print("🎉 CEO dapat bayaran HARI INI!")
    else:
        print(f"❌ Transfer GAGAL!")
        print(f"   Reference: {result.get('reference')}")
        print(f"   Error: {result.get('error')}")
        print()
        print("📝 Kemungkinan penyebab:")
        print("   - FLIP balance tidak cukup")
        print("   - API key tidak valid")
        print("   - Limit transfer exceeded")
    
    print()
    print("=" * 70)
    
    return 0 if result.get('success') else 1

if __name__ == "__main__":
    sys.exit(main())
