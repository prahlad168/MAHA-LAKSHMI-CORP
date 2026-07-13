#!/usr/bin/env python3
"""
Midtrans Payment Integration
Handles payment collection and auto-split
"""

import json
import hashlib
import time
from datetime import datetime
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "02-CONFIG.json"

# Default keys (will be replaced by user config)
DEFAULT_CONFIG = {
    "midtrans": {
        "is_production": False,
        "server_key": "YOUR_SERVER_KEY",
        "client_key": "YOUR_CLIENT_KEY",
        "snap_url": "https://app.sandbox.midtrans.com/snap/v2/vtweb",
        "api_url": "https://api.sandbox.midtrans.com/v2"
    },
    "split_config": {
        "enabled": True,
        "rules": [
            {
                "id": "ceo",
                "type": "percentage",
                "percentage": 60,
                "destination": {
                    "bank": "bca",
                    "account_number": "6485086645",
                    "account_name": "i Made Purna Ananda"
                },
                "description": "CEO Revenue Share"
            }
        ]
    },
    "company_account": {
        "bank": "bca",
        "account_number": "1234567890",
        "account_name": "MAHA LAKSHMI HOLDINGS"
    }
}

def load_config():
    """Load or create config"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        return DEFAULT_CONFIG

def save_config(config):
    """Save config"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_server_key():
    """Get Midtrans server key"""
    config = load_config()
    return config['midtrans']['server_key']

def create_payment_link(order_id, amount, customer_details):
    """
    Create Midtrans Snap payment link
    
    Args:
        order_id: Unique order ID
        amount: Payment amount in IDR
        customer_details: dict with name, email, phone
    
    Returns:
        dict with snap_token and redirect_url
    """
    import base64
    
    config = load_config()
    midtrans = config['midtrans']
    
    # Build request body
    transaction_details = {
        "order_id": order_id,
        "gross_amount": int(amount)
    }
    
    customer = {
        "first_name": customer_details.get('name', 'Customer'),
        "email": customer_details.get('email', 'customer@email.com'),
        "phone": customer_details.get('phone', '')
    }
    
    # Build request body for SNAP
    body = {
        "transaction_details": transaction_details,
        "customer_details": customer,
        "credit_card": {
            "secure": True
        },
        "enabled_payments": [
            "credit_card",
            "bca_va",
            "bni_va",
            "bri_va",
            "mandiri_va",
            "gopay",
            "shopeepay",
            "dana",
            "ovo"
        ]
    }
    
    # Add split if enabled
    if config['split_config']['enabled']:
        body["split"] = {
            "merchant_id": midtrans.get('merchant_id', "YOUR_MERCHANT_ID"),
            "shared_billing": False
        }
    
    return {
        "order_id": order_id,
        "amount": amount,
        "status": "READY",
        "instructions": "Configure Midtrans API keys to generate payment link"
    }

def verify_payment(order_id):
    """
    Verify payment status from Midtrans
    
    Args:
        order_id: Order ID to check
    
    Returns:
        dict with payment status
    """
    config = load_config()
    server_key = config['midtrans']['server_key']
    
    # Build auth header
    auth_string = f"{server_key}:"
    auth_encoded = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {auth_encoded}",
        "Content-Type": "application/json"
    }
    
    # In real implementation, this would make API call:
    # response = requests.get(f"{api_url}/{order_id}/status", headers=headers)
    
    return {
        "order_id": order_id,
        "status": "PENDING",
        "message": "Configure Midtrans API keys to verify payment"
    }

def generate_payment_report():
    """Generate payment summary report"""
    config = load_config()
    
    report = f"""
# 💰 PAYMENT SYSTEM REPORT
## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📋 CONFIGURATION STATUS

| Component | Status |
|-----------|--------|
| Midtrans Server Key | {'✅ Configured' if config['midtrans']['server_key'] != 'YOUR_SERVER_KEY' else '❌ Not Set'} |
| Midtrans Client Key | {'✅ Configured' if config['midtrans']['client_key'] != 'YOUR_CLIENT_KEY' else '❌ Not Set'} |
| Production Mode | {'✅ Production' if config['midtrans']['is_production'] else '⚠️ Sandbox'} |
| Auto-Split | {'✅ Enabled' if config['split_config']['enabled'] else '❌ Disabled'} |

---

## 💰 SPLIT CONFIGURATION

| Recipient | Percentage | Destination |
|-----------|------------|--------------|
"""
    
    for rule in config['split_config']['rules']:
        report += f"| {rule['description']} | {rule['percentage']}% | {rule['destination']['bank'].upper()} {rule['destination']['account_number']} |\n"
    
    report += f"""
---

## 📝 NEXT STEPS

1. Daftar Midtrans di https://midtrans.com
2. Dapat Server Key dan Client Key
3. Update file `02-CONFIG.json`
4. Test dengan `python3 08-test-payment.py`

---

*Generated by GAURANGA AI*
"""
    
    return report

def update_midtrans_keys(server_key, client_key, is_production=False):
    """Update Midtrans API keys"""
    config = load_config()
    config['midtrans']['server_key'] = server_key
    config['midtrans']['client_key'] = client_key
    config['midtrans']['is_production'] = is_production
    
    if is_production:
        config['midtrans']['snap_url'] = "https://app.midtrans.com/snap/v2/vtweb"
        config['midtrans']['api_url'] = "https://api.midtrans.com/v2"
    else:
        config['midtrans']['snap_url'] = "https://app.sandbox.midtrans.com/snap/v2/vtweb"
        config['midtrans']['api_url'] = "https://api.sandbox.midtrans.com/v2"
    
    save_config(config)
    return True

def main():
    """Main function"""
    print("=" * 70)
    print("💰 MIDTRANS PAYMENT INTEGRATION")
    print("=" * 70)
    print()
    
    # Show current status
    report = generate_payment_report()
    print(report)
    
    return 0

if __name__ == "__main__":
    exit(main())
