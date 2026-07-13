#!/usr/bin/env python3
"""
CEO Revenue Share - Calculator
Calculate CEO share from revenue with detailed breakdown
"""

import json
from datetime import datetime
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "01-config.json"
REVENUE_FILE = SCRIPT_DIR / "02-revenue-tracker.json"

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def format_currency(amount):
    """Format amount as IDR"""
    return f"Rp {amount:,.0f}".replace(",", ".")

def format_currency_usd(amount_idr, rate=16500):
    """Format amount as USD"""
    return f"$ {amount_idr / rate:,.2f}"

def format_currency_btc(amount_idr, btc_rate=700000000):
    """Format amount as BTC"""
    return f"₿ {amount_idr / btc_rate:.8f}"

def calculate_ceo_share(total_revenue, date=None):
    """Calculate CEO share from total revenue"""
    config = load_json(CONFIG_FILE)
    
    dist = config['distribution']
    
    calculation = {
        "total_revenue": total_revenue,
        "ceo_share": total_revenue * (dist['ceo_share_percent'] / 100),
        "reinvest": total_revenue * (dist['reinvest_percent'] / 100),
        "team_bonus": total_revenue * (dist['team_bonus_percent'] / 100),
        "csr": total_revenue * (dist['csr_percent'] / 100),
        "ceo_percent": dist['ceo_share_percent'],
        "reinvest_percent": dist['reinvest_percent'],
        "team_bonus_percent": dist['team_bonus_percent'],
        "csr_percent": dist['csr_percent'],
        "verified": abs(
            total_revenue * (dist['ceo_share_percent'] / 100) +
            total_revenue * (dist['reinvest_percent'] / 100) +
            total_revenue * (dist['team_bonus_percent'] / 100) +
            total_revenue * (dist['csr_percent'] / 100) - total_revenue
        ) < 1
    }
    
    return calculation

def print_calculation(calc, title="CEO SHARE CALCULATION"):
    """Print calculation results"""
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()
    print(f"  💰 Total Revenue: {format_currency(calc['total_revenue'])}")
    print()
    print("  📊 Distribution Breakdown:")
    print("  " + "-" * 50)
    print(f"  │ 👑 CEO Share      │ {calc['ceo_percent']:>3}% │ {format_currency(calc['ceo_share']):>15} │")
    print(f"  │ 🔄 Reinvestasi    │ {calc['reinvest_percent']:>3}% │ {format_currency(calc['reinvest']):>15} │")
    print(f"  │ 👥 Team Bonus    │ {calc['team_bonus_percent']:>3}% │ {format_currency(calc['team_bonus']):>15} │")
    print(f"  │ ❤️ CSR            │ {calc['csr_percent']:>3}% │ {format_currency(calc['csr']):>15} │")
    print("  " + "-" * 50)
    print(f"  │ {'TOTAL':<16} │ {'100%':>3} │ {format_currency(calc['total_revenue']):>15} │")
    print("  " + "-" * 50)
    print()
    print(f"  ✅ Verification: {'PASSED' if calc['verified'] else 'FAILED'}")
    print()
    print("  📋 BTC Equivalent (approximate):")
    print(f"  │ CEO Share: {format_currency_btc(calc['ceo_share'])} (~{format_currency_usd(calc['ceo_share'])})")
    print()
    print("=" * 60)

def calculate_from_date(date):
    """Calculate CEO share for a specific date"""
    revenue = load_json(REVENUE_FILE)
    config = load_json(CONFIG_FILE)
    
    print("=" * 60)
    print(f"  📅 CEO SHARE CALCULATION - {date}")
    print("=" * 60)
    print()
    
    if date in revenue['daily_revenue']:
        total = revenue['daily_revenue'][date]['total']
        print(f"  📊 Revenue untuk {date}:")
        print()
        
        # By company
        print("  🏢 By Company:")
        company_names = {c['id']: c['name'] for c in config['companies']}
        for company_id, amount in revenue['daily_revenue'][date]['by_company'].items():
            company_name = company_names.get(int(company_id), f"Company #{company_id}")
            ceo = amount * 0.6
            print(f"     • {company_name}: {format_currency(amount)} → CEO: {format_currency(ceo)}")
        print()
        
        # By source
        source_names = {
            "website": "Website",
            "marketplace": "Marketplace",
            "payment_gateway": "Payment Gateway",
            "direct_transfer": "Direct Transfer",
            "whatsapp": "WhatsApp",
            "offline": "Offline"
        }
        print("  📋 By Source:")
        for source, amount in revenue['daily_revenue'][date]['by_source'].items():
            if amount > 0:
                print(f"     • {source_names.get(source, source)}: {format_currency(amount)}")
        print()
        
        # Calculate
        calc = calculate_ceo_share(total, date)
        print_calculation(calc, f"DAILY CEO SHARE - {date}")
        
    else:
        print(f"  ⚠️ Tidak ada revenue untuk {date}")
        print()
        
        # Show with 0
        calc = calculate_ceo_share(0, date)
        print_calculation(calc, f"DAILY CEO SHARE - {date} (NO REVENUE)")

def calculate_monthly(date=None):
    """Calculate CEO share for current month"""
    revenue = load_json(REVENUE_FILE)
    config = load_json(CONFIG_FILE)
    
    if date:
        month = date[:7]
    else:
        month = datetime.now().strftime("%Y-%m")
    
    print("=" * 60)
    print(f"  📅 MONTHLY CEO SHARE CALCULATION - {month}")
    print("=" * 60)
    print()
    
    if month in revenue['monthly_summary']:
        data = revenue['monthly_summary'][month]
        total = data['total_revenue']
        
        print(f"  📊 Monthly Summary:")
        print(f"     • Total Revenue: {format_currency(total)}")
        print(f"     • Days Recorded: {data['days_recorded']}")
        print(f"     • Daily Average: {format_currency(data['daily_average'])}")
        print(f"     • Target: {format_currency(config['total_target_monthly'])}")
        print()
        
        # Calculate
        calc = calculate_ceo_share(total, month)
        print_calculation(calc, f"MONTHLY CEO SHARE - {month}")
        
        # Progress
        if config['total_target_monthly'] > 0:
            progress = (total / config['total_target_monthly']) * 100
            print(f"  📈 Progress to Target: {progress:.1f}%")
            remaining = config['total_target_monthly'] - total
            if remaining > 0:
                print(f"  📉 Remaining to Target: {format_currency(remaining)}")
        print()
        
    else:
        print(f"  ⚠️ Tidak ada data untuk {month}")
        print()
        calc = calculate_ceo_share(0, month)
        print_calculation(calc, f"MONTHLY CEO SHARE - {month} (NO DATA)")

def interactive_calculator():
    """Interactive calculator mode"""
    print("=" * 60)
    print("  👑 CEO SHARE CALCULATOR")
    print("=" * 60)
    print()
    print("  Masukkan jumlah revenue untuk dihitung:")
    print()
    
    while True:
        try:
            amount_str = input("  Amount (Rp): ").strip()
            if amount_str.lower() in ['q', 'quit', 'exit']:
                break
            
            amount = float(amount_str.replace(".", "").replace(",", ""))
            
            calc = calculate_ceo_share(amount)
            print()
            print_calculation(calc)
            print()
            
        except ValueError:
            print("  ❌ Amount tidak valid!")
            print()

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == "--monthly" or arg == "-m":
            # Monthly calculation
            month = sys.argv[2] if len(sys.argv) > 2 else None
            calculate_monthly(month)
            
        elif arg == "--date" or arg == "-d":
            # Calculate for specific date
            if len(sys.argv) > 2:
                calculate_from_date(sys.argv[2])
            else:
                print("Usage: python3 04-CEO-SHARE-CALCULATOR.py --date YYYY-MM-DD")
        
        elif arg == "--interactive" or arg == "-i":
            interactive_calculator()
            
        else:
            # Treat as amount
            try:
                amount = float(arg.replace(".", "").replace(",", ""))
                calc = calculate_ceo_share(amount)
                print()
                print_calculation(calc)
            except:
                print("Usage:")
                print("  python3 04-CEO-SHARE-CALCULATOR.py <amount>")
                print("  python3 04-CEO-SHARE-CALCULATOR.py --date YYYY-MM-DD")
                print("  python3 04-CEO-SHARE-CALCULATOR.py --monthly [YYYY-MM]")
                print("  python3 04-CEO-SHARE-CALCULATOR.py --interactive")
    else:
        # Show today
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")
        calculate_from_date(date)

if __name__ == "__main__":
    main()
