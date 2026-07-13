#!/usr/bin/env python3
"""
CEO Revenue Share - Add Revenue Entry
Add daily revenue from various sources
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

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(filepath, data):
    """Save JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_current_date():
    """Get current date in YYYY-MM-DD format"""
    return datetime.now().strftime("%Y-%m-%d")

def get_current_month():
    """Get current month in YYYY-MM format"""
    return datetime.now().strftime("%Y-%m")

def format_currency(amount):
    """Format amount as IDR"""
    return f"Rp {amount:,.0f}".replace(",", ".")

def safe_input(prompt, default=""):
    """Safe input with default value"""
    try:
        value = input(prompt).strip()
        return value if value else default
    except:
        return default

def add_revenue_entry():
    """Add a new revenue entry"""
    print("=" * 60)
    print("📊 ADD REVENUE ENTRY")
    print("=" * 60)
    print()
    
    # Load config
    config = load_json(CONFIG_FILE)
    revenue = load_json(REVENUE_FILE)
    audit = load_json(AUDIT_FILE)
    
    # Get date
    date = safe_input(f"Tanggal (YYYY-MM-DD) [default: {get_current_date()}]: ", get_current_date())
    
    print()
    print("Pilih Company:")
    print("-" * 40)
    for company in config['companies']:
        print(f"  {company['id']}. {company['name']}")
    print("  0. Semua Company")
    print()
    
    company_choice = safe_input("Pilih Company (0-10): ", "0")
    try:
        company_id = int(company_choice) if company_choice != "0" else None
    except ValueError:
        company_id = None
    
    print()
    print("Pilih Source:")
    print("-" * 40)
    sources = ["website", "marketplace", "payment_gateway", "direct_transfer", "whatsapp", "offline"]
    source_names = {
        "website": "Website Direct",
        "marketplace": "Marketplace",
        "payment_gateway": "Payment Gateway",
        "direct_transfer": "Direct Transfer",
        "whatsapp": "WhatsApp Sales",
        "offline": "Offline Sales"
    }
    for i, source in enumerate(sources, 1):
        print(f"  {i}. {source_names[source]}")
    print()
    
    source_choice = safe_input(f"Pilih Source (1-6) [default: 1]: ", "1")
    try:
        source_index = int(source_choice) - 1
        if source_index < 0 or source_index >= len(sources):
            source_index = 0
    except ValueError:
        source_index = 0
    
    source = sources[source_index]
    
    print()
    currency_input = safe_input("Mata Uang (IDR/USD/EUR) [default: IDR]: ", "").upper()
    currency = currency_input if currency_input in ["IDR", "USD", "EUR"] else "IDR"
    
    print()
    amount_input = safe_input(f"Amount ({currency}): ", "")
    try:
        amount = float(amount_input.replace(".", "").replace(",", ""))
    except ValueError:
        print("❌ Amount tidak valid!")
        return
    
    # Convert to IDR if needed
    if currency == "USD":
        rate = config['currencies']['exchange_rates']['USD_TO_IDR']
        amount_idr = amount * rate
    elif currency == "EUR":
        rate = config['currencies']['exchange_rates']['EUR_TO_IDR']
        amount_idr = amount * rate
    else:
        amount_idr = amount
        currency = "IDR"
    
    print()
    description = safe_input("Deskripsi (optional): ", "")
    
    # Get company info
    company_name = "All Companies"
    if company_id is not None:
        company = next((c for c in config['companies'] if c['id'] == company_id), None)
        if company:
            company_name = company['name']
    
    # Create entry
    entry = {
        "id": f"REV-{date.replace('-', '')}-{len(revenue['transactions']) + 1:03d}",
        "date": date,
        "company_id": company_id,
        "company_name": company_name,
        "source": source,
        "source_name": source_names[source],
        "amount": amount,
        "currency": currency,
        "amount_idr": amount_idr,
        "description": description,
        "created_at": datetime.now().isoformat(),
        "status": "recorded"
    }
    
    # Add to transactions
    revenue['transactions'].append(entry)
    
    # Update daily revenue
    if date not in revenue['daily_revenue']:
        revenue['daily_revenue'][date] = {
            "total": 0,
            "by_source": {s: 0 for s in sources},
            "by_company": {},
            "by_currency": {"IDR": 0, "USD": 0, "EUR": 0}
        }
    
    revenue['daily_revenue'][date]["total"] += amount_idr
    revenue['daily_revenue'][date]["by_source"][source] += amount_idr
    revenue['daily_revenue'][date]["by_currency"][currency] += amount_idr
    
    if company_id is not None:
        str_company_id = str(company_id)
        if str_company_id not in revenue['daily_revenue'][date]["by_company"]:
            revenue['daily_revenue'][date]["by_company"][str_company_id] = 0
        revenue['daily_revenue'][date]["by_company"][str_company_id] += amount_idr
    
    # Update company daily
    if company_id is not None:
        str_company_id = str(company_id)
        if date not in revenue['company_daily'][str_company_id]:
            revenue['company_daily'][str_company_id][date] = 0
        revenue['company_daily'][str_company_id][date] += amount_idr
    
    # Update sources daily
    if date not in revenue['sources_daily'][source]:
        revenue['sources_daily'][source][date] = 0
    revenue['sources_daily'][source][date] += amount_idr
    
    # Update monthly summary
    month = date[:7]
    if month not in revenue['monthly_summary']:
        revenue['monthly_summary'][month] = {
            "total_revenue": 0,
            "days_recorded": 0,
            "daily_average": 0,
            "highest_day": None,
            "lowest_day": None,
            "by_company": {},
            "by_source": {},
            "by_currency": {"IDR": 0, "USD": 0, "EUR": 0}
        }
    
    revenue['monthly_summary'][month]["total_revenue"] += amount_idr
    
    # Count unique days
    unique_days = set()
    for d in revenue['daily_revenue']:
        if d.startswith(month):
            unique_days.add(d)
    revenue['monthly_summary'][month]["days_recorded"] = len(unique_days)
    revenue['monthly_summary'][month]["daily_average"] = revenue['monthly_summary'][month]["total_revenue"] / max(len(unique_days), 1)
    
    # Update metadata
    revenue['metadata']['total_entries'] += 1
    revenue['metadata']['total_revenue_all_time'] += amount_idr
    revenue['metadata']['last_updated'] = datetime.now().isoformat()
    
    # Save files
    save_json(REVENUE_FILE, revenue)
    
    # Add to audit log
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": "ADD_REVENUE",
        "entry_id": entry["id"],
        "amount": amount,
        "currency": currency,
        "amount_idr": amount_idr,
        "company": entry["company_name"],
        "source": entry["source_name"],
        "status": "SUCCESS"
    }
    audit['entries'].append(audit_entry)
    audit['metadata']['total_entries'] += 1
    audit['metadata']['last_updated'] = datetime.now().isoformat()
    save_json(AUDIT_FILE, audit)
    
    # Print confirmation
    print()
    print("=" * 60)
    print("✅ REVENUE ADDED SUCCESSFULLY")
    print("=" * 60)
    print(f"  ID: {entry['id']}")
    print(f"  Tanggal: {date}")
    print(f"  Company: {entry['company_name']}")
    print(f"  Source: {entry['source_name']}")
    print(f"  Amount: {format_currency(amount)} {currency}")
    print(f"  Amount (IDR): {format_currency(amount_idr)}")
    if description:
        print(f"  Description: {description}")
    print("=" * 60)
    print()

def show_current_revenue():
    """Show current day revenue"""
    print("=" * 60)
    print("📊 CURRENT REVENUE STATUS")
    print("=" * 60)
    print()
    
    config = load_json(CONFIG_FILE)
    revenue = load_json(REVENUE_FILE)
    
    today = get_current_date()
    this_month = get_current_month()
    
    print(f"📅 Hari ini: {today}")
    print(f"📅 Bulan ini: {this_month}")
    print()
    
    # Today's revenue
    if today in revenue['daily_revenue']:
        today_revenue = revenue['daily_revenue'][today]['total']
    else:
        today_revenue = 0
    
    print(f"💰 Revenue Hari Ini: {format_currency(today_revenue)}")
    
    # Monthly revenue
    if this_month in revenue['monthly_summary']:
        month_revenue = revenue['monthly_summary'][this_month]['total_revenue']
        month_target = config['total_target_monthly']
        progress = (month_revenue / month_target * 100) if month_target > 0 else 0
    else:
        month_revenue = 0
        progress = 0
    
    print(f"💰 Revenue Bulan Ini: {format_currency(month_revenue)}")
    print(f"🎯 Target Bulanan: {format_currency(config['total_target_monthly'])}")
    print(f"📈 Progress: {progress:.1f}%")
    print()
    
    # CEO Share calculation
    ceo_share = month_revenue * (config['distribution']['ceo_share_percent'] / 100)
    print(f"👑 Hak CEO (60%): {format_currency(ceo_share)}")
    print()
    
    print("-" * 60)
    print("📋 BY COMPANY (Hari Ini):")
    print("-" * 60)
    
    if today in revenue['daily_revenue'] and revenue['daily_revenue'][today]['by_company']:
        for company_id, amount in revenue['daily_revenue'][today]['by_company'].items():
            company = next((c for c in config['companies'] if c['id'] == int(company_id)), None)
            if company:
                print(f"  {company['name']}: {format_currency(amount)}")
    else:
        print("  (Tidak ada revenue hari ini)")
    
    print()
    print("-" * 60)
    print("📋 BY SOURCE (Hari Ini):")
    print("-" * 60)
    
    source_names = {
        "website": "Website",
        "marketplace": "Marketplace",
        "payment_gateway": "Payment Gateway",
        "direct_transfer": "Direct Transfer",
        "whatsapp": "WhatsApp",
        "offline": "Offline"
    }
    
    if today in revenue['daily_revenue']:
        for source, amount in revenue['daily_revenue'][today]['by_source'].items():
            if amount > 0:
                print(f"  {source_names.get(source, source)}: {format_currency(amount)}")
    else:
        print("  (Tidak ada revenue hari ini)")
    
    print()
    print("=" * 60)

def main():
    """Main menu"""
    while True:
        print()
        print("╔══════════════════════════════════════════════════════════╗")
        print("║     👑 CEO REVENUE SHARE - REVENUE MANAGEMENT         ║")
        print("╠══════════════════════════════════════════════════════════╣")
        print("║  1. ➕ Add Revenue Entry                              ║")
        print("║  2. 📊 Show Current Status                            ║")
        print("║  3. 🚪 Exit                                           ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        
        choice = safe_input("Pilih menu (1-3): ", "")
        
        if choice == "1":
            add_revenue_entry()
        elif choice == "2":
            show_current_revenue()
        elif choice == "3":
            print("👋 Sampai jumpa!")
            break
        else:
            print("❌ Pilihan tidak valid!")

if __name__ == "__main__":
    main()
