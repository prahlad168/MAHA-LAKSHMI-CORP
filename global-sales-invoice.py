#!/usr/bin/env python3
"""
Global Sales Invoice Generator
MAHA LAKSHMI HOLDINGS
Generates USDT invoices for closed deals
"""

import json
import argparse
from datetime import datetime
from typing import Dict, List
import os

USDT_WALLET = "TNFs1SP2C8HxGSJkSH3hJamf8ukgtnW7U6"

def generate_invoice_id() -> str:
    """Generate unique invoice ID"""
    date_str = datetime.now().strftime("%Y%m%d")
    random_suffix = datetime.now().strftime("%H%M%S")
    return f"INV-GLOBAL-{date_str}-{random_suffix}"

def generate_invoice(client_name: str, client_email: str, company: str, 
                     country: str, services: List[Dict], output_dir: str = "invoices") -> Dict:
    """Generate invoice for client"""
    
    invoice = {
        "invoice_id": generate_invoice_id(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "due_date": (datetime.now()).strftime("%Y-%m-%d"),
        "client": {
            "name": client_name,
            "email": client_email,
            "company": company,
            "country": country
        },
        "services": services,
        "subtotal_usd": sum(s.get("price_usd", 0) for s in services),
        "total_usd": sum(s.get("price_usd", 0) for s in services),
        "payment": {
            "method": "USDT",
            "network": "TRC20 (Tron)",
            "wallet": USDT_WALLET,
            "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=trc20:{USDT_WALLET}"
        },
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    # Save invoice
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/USDT-invoice-{invoice['invoice_id']}.json"
    with open(filename, 'w') as f:
        json.dump(invoice, f, indent=2)
    
    return invoice

def generate_invoice_markdown(invoice: Dict) -> str:
    """Generate markdown version of invoice"""
    md = f"""# 📄 INVOICE

## {invoice['invoice_id']}

---

### Bill To:
**{invoice['client']['name']}**
- Company: {invoice['client']['company']}
- Email: {invoice['client']['email']}
- Country: {invoice['client']['country']}

### Invoice Details:
- **Date:** {invoice['date']}
- **Due Date:** {invoice['due_date']}
- **Status:** ⏳ {invoice['status'].upper()}

---

## Services

| # | Service | Description | Amount |
|---|---------|-------------|--------|
"""
    
    for i, service in enumerate(invoice['services'], 1):
        md += f"| {i} | {service.get('item', 'Service')} | {service.get('description', '')} | ${service.get('price_usd', 0):.2f} |\n"
    
    md += f"""
---

## Payment Summary

| Description | Amount |
|-------------|--------|
| Subtotal | ${invoice['subtotal_usd']:.2f} |
| **Total Due** | **${invoice['total_usd']:.2f} USD** |

---

## 💰 Payment Instructions

### USDT (TRC20) Preferred

**Network:** TRC20 (Tron)

**Wallet Address:**
```
{USDT_WALLET}
```

**QR Code:** [Scan to pay]({invoice['payment']['qr_code_url']})

---

### Important:
- Please pay the exact amount shown above
- Send payment to the wallet address above
- Once paid, send confirmation to: sales@mahalakshmi.com

---

**Thank you for your business!** 🙏

*MAHA LAKSHMI HOLDINGS*
Global Digital Solutions
"""

    return md

def mark_invoice_paid(invoice_id: str, tx_hash: str = None):
    """Mark invoice as paid"""
    filename = f"invoices/USDT-invoice-{invoice_id}.json"
    
    try:
        with open(filename, 'r') as f:
            invoice = json.load(f)
        
        invoice['status'] = 'paid'
        invoice['paid_at'] = datetime.now().isoformat()
        if tx_hash:
            invoice['tx_hash'] = tx_hash
        
        with open(filename, 'w') as f:
            json.dump(invoice, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error updating invoice: {e}")
        return False

def get_invoices_summary() -> Dict:
    """Get summary of all invoices"""
    total_pending = 0
    total_paid = 0
    pending_count = 0
    paid_count = 0
    
    try:
        for filename in os.listdir("invoices"):
            if filename.endswith(".json"):
                with open(f"invoices/{filename}", 'r') as f:
                    invoice = json.load(f)
                    if invoice['status'] == 'paid':
                        total_paid += invoice['total_usd']
                        paid_count += 1
                    else:
                        total_pending += invoice['total_usd']
                        pending_count += 1
    except:
        pass
    
    return {
        "pending": {"count": pending_count, "total_usd": total_pending},
        "paid": {"count": paid_count, "total_usd": total_paid},
        "total_revenue": total_paid
    }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Generate USDT invoices")
    parser.add_argument("--client", required=True, help="Client name")
    parser.add_argument("--email", required=True, help="Client email")
    parser.add_argument("--company", required=True, help="Client company")
    parser.add_argument("--country", required=True, help="Client country")
    parser.add_argument("--service", required=True, help="Service name")
    parser.add_argument("--description", help="Service description")
    parser.add_argument("--amount", type=float, required=True, help="Amount in USD")
    
    args = parser.parse_args()
    
    services = [{
        "item": args.service,
        "description": args.description or args.service,
        "price_usd": args.amount
    }]
    
    print("🤖 MAHA LAKSHMI HOLDINGS - Invoice Generator")
    print("=" * 50)
    
    invoice = generate_invoice(
        client_name=args.client,
        client_email=args.email,
        company=args.company,
        country=args.country,
        services=services
    )
    
    print(f"\n✅ Invoice created: {invoice['invoice_id']}")
    print(f"💰 Amount: ${invoice['total_usd']:.2f} USD")
    print(f"📁 Saved to: invoices/USDT-invoice-{invoice['invoice_id']}.json")
    
    # Show markdown
    print("\n" + "=" * 50)
    print(generate_invoice_markdown(invoice))
    
    # Show payment info
    print("\n" + "=" * 50)
    print(f"\n💳 PAYMENT ADDRESS:")
    print(f"   USDT (TRC20): {USDT_WALLET}")

if __name__ == "__main__":
    main()
