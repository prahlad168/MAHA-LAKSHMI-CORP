#!/usr/bin/env python3
"""
CEO Revenue Share - Report Generator
Generate various reports for CEO review
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "01-config.json"
REVENUE_FILE = SCRIPT_DIR / "02-revenue-tracker.json"
AUDIT_FILE = SCRIPT_DIR / "03-audit-log.json"
REPORTS_DIR = SCRIPT_DIR / "DAILY-REPORTS"

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(filepath, data):
    """Save JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def format_currency(amount):
    """Format amount as IDR"""
    return f"Rp {amount:,.0f}".replace(",", ".")

def get_date_formatted():
    """Get formatted date"""
    return datetime.now().strftime("%Y-%m-%d")

def get_datetime_formatted():
    """Get formatted datetime"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_weekly_report():
    """Generate weekly report"""
    config = load_json(CONFIG_FILE)
    revenue = load_json(REVENUE_FILE)
    
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    
    print("=" * 70)
    print("📊 WEEKLY CEO REVENUE SHARE REPORT")
    print("=" * 70)
    print(f"📅 Period: {week_ago.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}")
    print()
    
    # Calculate weekly totals
    weekly_total = 0
    weekly_by_day = {}
    weekly_by_company = {}
    weekly_by_source = {}
    
    for i in range(7):
        date = (week_ago + timedelta(days=i)).strftime("%Y-%m-%d")
        if date in revenue['daily_revenue']:
            day_data = revenue['daily_revenue'][date]
            weekly_total += day_data['total']
            weekly_by_day[date] = day_data['total']
            
            for company_id, amount in day_data.get('by_company', {}).items():
                if company_id not in weekly_by_company:
                    weekly_by_company[company_id] = 0
                weekly_by_company[company_id] += amount
            
            for source, amount in day_data.get('by_source', {}).items():
                if source not in weekly_by_source:
                    weekly_by_source[source] = 0
                weekly_by_source[source] += amount
    
    # CEO Share
    ceo_share = weekly_total * 0.6
    reinvest = weekly_total * 0.25
    team_bonus = weekly_total * 0.1
    csr = weekly_total * 0.05
    
    print("📈 DAILY BREAKDOWN:")
    print("-" * 50)
    for date, amount in sorted(weekly_by_day.items()):
        bar = "█" * int(amount / 100000) if amount > 0 else "░"
        print(f"  {date}: {format_currency(amount):>15} {bar}")
    print("-" * 50)
    print(f"  {'TOTAL':10}: {format_currency(weekly_total):>15}")
    print()
    
    print("🏢 BY COMPANY:")
    print("-" * 50)
    company_names = {c['id']: c['name'] for c in config['companies']}
    for company_id, amount in sorted(weekly_by_company.items(), key=lambda x: x[1], reverse=True):
        company_name = company_names.get(int(company_id), f"Company #{company_id}")
        ceo = amount * 0.6
        print(f"  {company_name:<25}: {format_currency(amount):>12} → CEO: {format_currency(ceo)}")
    print()
    
    print("📋 BY SOURCE:")
    print("-" * 50)
    source_names = {
        "website": "Website",
        "marketplace": "Marketplace",
        "payment_gateway": "Payment Gateway",
        "direct_transfer": "Direct Transfer",
        "whatsapp": "WhatsApp",
        "offline": "Offline"
    }
    for source, amount in sorted(weekly_by_source.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source_names.get(source, source):<25}: {format_currency(amount)}")
    print()
    
    print("💰 WEEKLY CEO SHARE:")
    print("=" * 50)
    print(f"  Total Revenue: {format_currency(weekly_total)}")
    print(f"  👑 CEO Share (60%): {format_currency(ceo_share)}")
    print(f"  🔄 Reinvestasi (25%): {format_currency(reinvest)}")
    print(f"  👥 Team Bonus (10%): {format_currency(team_bonus)}")
    print(f"  ❤️ CSR (5%): {format_currency(csr)}")
    print("=" * 50)
    print()
    
    return {
        "period": f"{week_ago.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}",
        "total_revenue": weekly_total,
        "ceo_share": ceo_share
    }

def generate_monthly_report(month=None):
    """Generate monthly report"""
    config = load_json(CONFIG_FILE)
    revenue = load_json(REVENUE_FILE)
    
    if not month:
        month = datetime.now().strftime("%Y-%m")
    
    print("=" * 70)
    print("📊 MONTHLY CEO REVENUE SHARE REPORT")
    print("=" * 70)
    print(f"📅 Period: {month}")
    print()
    
    if month in revenue['monthly_summary']:
        data = revenue['monthly_summary'][month]
        total = data['total_revenue']
        target = config['total_target_monthly']
        progress = (total / target * 100) if target > 0 else 0
        
        print("📈 SUMMARY:")
        print("-" * 50)
        print(f"  Total Revenue: {format_currency(total)}")
        print(f"  Target: {format_currency(target)}")
        print(f"  Progress: {progress:.1f}%")
        print(f"  Days Recorded: {data['days_recorded']}")
        print(f"  Daily Average: {format_currency(data['daily_average'])}")
        print()
        
        # Progress bar
        bar_length = 40
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"  Progress: [{bar}] {progress:.1f}%")
        print()
        
        # CEO Share
        ceo_share = total * 0.6
        reinvest = total * 0.25
        team_bonus = total * 0.1
        csr = total * 0.05
        
        print("💰 CEO SHARE CALCULATION:")
        print("=" * 50)
        print(f"  Total Revenue: {format_currency(total)}")
        print("-" * 50)
        print(f"  👑 CEO Share (60%): {format_currency(ceo_share)}")
        print(f"  🔄 Reinvestasi (25%): {format_currency(reinvest)}")
        print(f"  👥 Team Bonus (10%): {format_currency(team_bonus)}")
        print(f"  ❤️ CSR (5%): {format_currency(csr)}")
        print("=" * 50)
        print()
        
        # By company
        if data.get('by_company'):
            print("🏢 BY COMPANY:")
            print("-" * 50)
            company_names = {c['id']: c['name'] for c in config['companies']}
            for company_id, amount in sorted(data['by_company'].items(), key=lambda x: x[1], reverse=True):
                company_name = company_names.get(int(company_id), f"Company #{company_id}")
                ceo = amount * 0.6
                pct = (amount / total * 100) if total > 0 else 0
                print(f"  {company_name:<25}: {format_currency(amount):>12} ({pct:>5.1f}%) → CEO: {format_currency(ceo)}")
            print()
        
        # By currency
        if data.get('by_currency'):
            print("💱 BY CURRENCY:")
            print("-" * 50)
            for curr, amount in data['by_currency'].items():
                if amount > 0:
                    print(f"  {curr}: {format_currency(amount)}")
            print()
        
        return {
            "period": month,
            "total_revenue": total,
            "target": target,
            "progress": progress,
            "ceo_share": ceo_share
        }
    else:
        print(f"  ⚠️ Tidak ada data untuk {month}")
        print()
        
        # Calculate from daily
        total = sum(
            revenue['daily_revenue'].get(date, {}).get('total', 0)
            for date in revenue['daily_revenue']
            if date.startswith(month)
        )
        
        if total > 0:
            print(f"  Total from daily records: {format_currency(total)}")
            print()
            
            ceo_share = total * 0.6
            print(f"  👑 CEO Share (60%): {format_currency(ceo_share)}")
            print()
        
        return {
            "period": month,
            "total_revenue": total,
            "ceo_share": total * 0.6 if total > 0 else 0
        }

def generate_audit_summary():
    """Generate audit summary"""
    audit = load_json(AUDIT_FILE)
    
    print("=" * 70)
    print("📋 AUDIT LOG SUMMARY")
    print("=" * 70)
    print()
    
    print(f"📊 Total Entries: {audit['metadata']['total_entries']}")
    print(f"🕐 Last Updated: {audit['metadata']['last_updated']}")
    print()
    
    # Execution log
    executions = audit.get('execution_log', [])
    if executions:
        print("📜 RECENT EXECUTIONS:")
        print("-" * 50)
        for entry in executions[-5:]:
            print(f"  {entry['timestamp'][:19]}")
            print(f"    Date: {entry['date']}")
            print(f"    Revenue: {format_currency(entry['total_revenue'])}")
            print(f"    CEO Share: {format_currency(entry['ceo_share'])}")
            print(f"    Status: {entry['status']}")
            print()
    
    # Errors
    errors = audit.get('errors', [])
    if errors:
        print(f"⚠️ ERRORS ({len(errors)}):")
        print("-" * 50)
        for error in errors[-3:]:
            print(f"  {error}")
        print()
    else:
        print("✅ No errors recorded")
        print()

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == "--weekly" or arg == "-w":
            generate_weekly_report()
            
        elif arg == "--monthly" or arg == "-m":
            month = sys.argv[2] if len(sys.argv) > 2 else None
            generate_monthly_report(month)
            
        elif arg == "--audit" or arg == "-a":
            generate_audit_summary()
            
        elif arg == "--all" or arg == "-a":
            print("\n" + "=" * 70)
            print("📊 COMPLETE REPORT PACKAGE")
            print("=" * 70 + "\n")
            
            generate_weekly_report()
            print("\n" + "-" * 70 + "\n")
            
            generate_monthly_report()
            print("\n" + "-" * 70 + "\n")
            
            generate_audit_summary()
            
        else:
            print("Usage:")
            print("  python3 generate-report.py --weekly")
            print("  python3 generate-report.py --monthly [YYYY-MM]")
            print("  python3 generate-report.py --audit")
            print("  python3 generate-report.py --all")
    else:
        # Default: show today's calculation
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")
        
        print("\n" + "=" * 70)
        print("📊 TODAY'S CEO REVENUE SHARE")
        print("=" * 70 + "\n")
        
        revenue = load_json(REVENUE_FILE)
        config = load_json(CONFIG_FILE)
        
        if date in revenue['daily_revenue']:
            total = revenue['daily_revenue'][date]['total']
        else:
            total = 0
        
        print(f"📅 Date: {date}")
        print(f"💰 Total Revenue: {format_currency(total)}")
        print()
        
        ceo_share = total * 0.6
        print(f"👑 CEO SHARE (60%): {format_currency(ceo_share)}")
        print(f"   Destination: {config['destination']['address']}")
        print()
        
        # Show monthly progress
        month = date[:7]
        if month in revenue['monthly_summary']:
            month_total = revenue['monthly_summary'][month]['total_revenue']
            target = config['total_target_monthly']
            progress = (month_total / target * 100) if target > 0 else 0
            month_ceo = month_total * 0.6
            
            print(f"📈 MONTHLY PROGRESS ({month}):")
            print(f"   Revenue: {format_currency(month_total)} / {format_currency(target)}")
            print(f"   Progress: {progress:.1f}%")
            print(f"   CEO Share YTD: {format_currency(month_ceo)}")
        print()

if __name__ == "__main__":
    main()
