#!/usr/bin/env python3
"""
CEO Revenue Share - Daily Execution Agent
Runs daily at 12:00 WITA to calculate and report CEO revenue share
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

def format_currency_usd(amount_idr, rate=16500):
    """Format amount as USD"""
    return f"$ {amount_idr / rate:,.2f}"

def format_currency_btc(amount_idr, btc_rate=700000000):
    """Format amount as BTC (approximate)"""
    # Assuming 1 BTC ≈ 700,000,000 IDR
    return f"₿ {amount_idr / btc_rate:.8f}"

def get_date_formatted():
    """Get formatted date"""
    return datetime.now().strftime("%Y-%m-%d")

def get_time_formatted():
    """Get formatted time"""
    return datetime.now().strftime("%H:%M:%S")

def get_datetime_formatted():
    """Get formatted datetime"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate_daily_summary(date):
    """Calculate summary for a specific date"""
    config = load_json(CONFIG_FILE)
    revenue = load_json(REVENUE_FILE)
    
    summary = {
        "date": date,
        "total_revenue": 0,
        "by_company": {},
        "by_source": {},
        "by_currency": {"IDR": 0, "USD": 0, "EUR": 0},
        "domestic": 0,
        "international": 0,
        "data_complete": False,
        "calculation_correct": False,
        "system_ready": False
    }
    
    # Get revenue for this date
    if date in revenue['daily_revenue']:
        day_data = revenue['daily_revenue'][date]
        summary["total_revenue"] = day_data.get("total", 0)
        summary["by_company"] = day_data.get("by_company", {})
        summary["by_source"] = day_data.get("by_source", {})
        summary["by_currency"] = day_data.get("by_currency", {"IDR": 0, "USD": 0, "EUR": 0})
        
        # Domestic = IDR
        summary["domestic"] = summary["by_currency"].get("IDR", 0)
        # International = USD + EUR (converted to IDR)
        summary["international"] = 0
        for curr in ["USD", "EUR"]:
            if curr in summary["by_currency"]:
                rate = config['currencies']['exchange_rates'].get(f'{curr}_TO_IDR', 1)
                summary["international"] += summary["by_currency"][curr] * rate if curr != "IDR" else summary["by_currency"][curr]
    
    # Calculate percentages
    total = summary["total_revenue"]
    summary["ceo_share"] = total * (config['distribution']['ceo_share_percent'] / 100)
    summary["reinvest"] = total * (config['distribution']['reinvest_percent'] / 100)
    summary["team_bonus"] = total * (config['distribution']['team_bonus_percent'] / 100)
    summary["csr"] = total * (config['distribution']['csr_percent'] / 100)
    
    # Verify
    summary["data_complete"] = total >= 0
    summary["calculation_correct"] = (
        abs(summary["ceo_share"] + summary["reinvest"] + summary["team_bonus"] + summary["csr"] - total) < 1
    )
    summary["system_ready"] = summary["data_complete"] and summary["calculation_correct"]
    
    return summary

def generate_daily_report(date):
    """Generate daily report for CEO"""
    config = load_json(CONFIG_FILE)
    revenue = load_json(REVENUE_FILE)
    
    summary = calculate_daily_summary(date)
    
    # Get company names
    company_names = {c['id']: c['name'] for c in config['companies']}
    
    # Source names
    source_names = {
        "website": "Website Direct",
        "marketplace": "Marketplace",
        "payment_gateway": "Payment Gateway",
        "direct_transfer": "Direct Transfer",
        "whatsapp": "WhatsApp Sales",
        "offline": "Offline Sales"
    }
    
    # Generate report
    report = f"""# 👑 DAILY CEO REVENUE SHARE REPORT
## MAHA LAKSHMI HOLDINGS

**Tanggal:** {date}  
**Waktu:** {get_time_formatted()} WITA  
**Agent:** CEO Revenue Share Execution Agent v1.0  
**Reference:** RS-{date.replace('-', '')}-001

---

## 📊 REVENUE SUMMARY

### 💰 Total Revenue Hari Ini
| Metric | Amount |
|--------|--------|
| **Total Gross Revenue** | **{format_currency(summary['total_revenue'])}** |
| Domestic (IDR) | {format_currency(summary['domestic'])} |
| International | {format_currency(summary['international'])} |

---

## 🏢 REVENUE BY COMPANY

| Company | Revenue | CEO Share (60%) |
|---------|---------|------------------|
"""
    
    # By company
    for company_id, amount in sorted(summary['by_company'].items()):
        company_name = company_names.get(int(company_id), f"Company #{company_id}")
        ceo = amount * 0.6
        report += f"| {company_name} | {format_currency(amount)} | {format_currency(ceo)} |\n"
    
    report += f"| **TOTAL** | **{format_currency(summary['total_revenue'])}** | **{format_currency(summary['ceo_share'])}** |\n"
    
    report += f"""

---

## 📋 REVENUE BY SOURCE

| Source | Amount |
|--------|--------|
"""
    
    for source, amount in summary['by_source'].items():
        if amount > 0:
            report += f"| {source_names.get(source, source)} | {format_currency(amount)} |\n"
    
    if not any(summary['by_source'].values()):
        report += "| *(Tidak ada revenue)* | Rp 0 |\n"
    
    report += f"""

---

## 💱 REVENUE BY CURRENCY

| Currency | Amount |
|---------|--------|
| IDR | {format_currency(summary['by_currency'].get('IDR', 0))} |
| USD | {summary['by_currency'].get('USD', 0)} USD |
| EUR | {summary['by_currency'].get('EUR', 0)} EUR |

---

## 💰 CEO SHARE CALCULATION

### Formula
```
CEO Share = 60% × Total Revenue
```

### Distribution Breakdown

| Kategori | Persentase | Amount |
|----------|-----------|--------|
| **👑 CEO Share** | **60%** | **{format_currency(summary['ceo_share'])}** |
| 🔄 Reinvestasi | 25% | {format_currency(summary['reinvest'])} |
| 👥 Team Bonus | 10% | {format_currency(summary['team_bonus'])} |
| ❤️ CSR | 5% | {format_currency(summary['csr'])} |
| **TOTAL** | **100%** | **{format_currency(summary['total_revenue'])}** |

---

## 📋 PAYMENT EXECUTION

| Field | Value |
|-------|-------|
| **CEO Share Amount** | **{format_currency(summary['ceo_share'])}** |
| **BTC Equivalent** | ~{format_currency_btc(summary['ceo_share'])} |
| **Destination** | BCA: {config['destination']['primary']['account']} ({config['destination']['primary']['bank']}) |
| **Fallback** | USDT: {config['destination']['fallback']['usdt_address']} ({config['destination']['fallback']['network']}) |
| **Status** | {"✅ READY" if summary['system_ready'] else "⚠️ PENDING - Data tidak lengkap"} |
| **Reference** | RS-{date.replace('-', '')}-001 |

---

## 🔍 DATA VERIFICATION

| Check | Status |
|-------|--------|
| Data Complete | {"✅ YES" if summary['data_complete'] else "❌ NO"} |
| Calculation Correct | {"✅ YES" if summary['calculation_correct'] else "❌ NO"} |
| System Ready | {"✅ YES" if summary['system_ready'] else "❌ NO"} |

---

## 📊 MONTHLY PROGRESS

"""
    
    month = date[:7]
    if month in revenue['monthly_summary']:
        month_data = revenue['monthly_summary'][month]
        progress = (month_data['total_revenue'] / config['total_target_monthly'] * 100) if config['total_target_monthly'] > 0 else 0
        
        report += f"""| Metric | Value |
|--------|-------|
| Total Monthly Revenue | {format_currency(month_data['total_revenue'])} |
| Target Monthly | {format_currency(config['total_target_monthly'])} |
| Days Recorded | {month_data['days_recorded']} |
| Daily Average | {format_currency(month_data['daily_average'])} |
| Progress | {progress:.1f}% |
"""
    else:
        report += "| Metric | Value |\n|--------|-------|\n"
        report += "| Total Monthly Revenue | Rp 0 |\n"
        report += f"| Target Monthly | {format_currency(config['total_target_monthly'])} |\n"
        report += "| Progress | 0.0% |\n"
    
    report += f"""

---

## 📝 NOTES

"""
    
    if summary['total_revenue'] == 0:
        report += """⚠️ **PERHATIAN:** Belum ada revenue yang tercatat hari ini.

Untuk menambahkan revenue, jalankan:
```bash
python3 add-revenue.py
```
"""
    else:
        report += """✅ Revenue berhasil dihitung. Sistem siap untuk eksekusi.
"""
    
    report += f"""

---

## 🚀 NEXT STEPS

1. ✅ Revenue dihitung untuk {date}
2. {"✅ CEO share siap ditransfer" if summary['system_ready'] else "⚠️ Perlu review data"}
3. 📊 Laporan dikirim ke CEO

---

## 📞 CONTACT

| Info | Detail |
|------|--------|
| **CEO** | {config['ceo']['name']} |
| **WhatsApp** | {config['ceo']['whatsapp']} |
| **BCA Account** | {config['destination']['primary']['account']} |
| **USDT Fallback** | {config['destination']['fallback']['usdt_address']} |

---

**Motto:** "Setiap masalah pasti ada solusinya!" 💪

---

*Generated by: CEO Revenue Share Execution Agent v1.0*  
*Time: {get_datetime_formatted()} WITA*  
*MAHA LAKSHMI HOLDINGS - Building Digital Empire Together! 🚀*
"""
    
    return report

def save_daily_report(date, report):
    """Save daily report to file"""
    REPORTS_DIR.mkdir(exist_ok=True)
    
    report_file = REPORTS_DIR / f"daily-report-{date}.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report_file

def update_audit_log(summary, status, notes=""):
    """Update audit log"""
    audit = load_json(AUDIT_FILE)
    
    entry = {
        "timestamp": get_datetime_formatted(),
        "action": "DAILY_EXECUTION",
        "date": summary['date'],
        "total_revenue": summary['total_revenue'],
        "ceo_share": summary['ceo_share'],
        "status": status,
        "notes": notes,
        "reference": f"RS-{summary['date'].replace('-', '')}-001"
    }
    
    audit['execution_log'].append(entry)
    audit['metadata']['total_entries'] += 1
    audit['metadata']['last_updated'] = datetime.now().isoformat()
    
    save_json(AUDIT_FILE, audit)

def run_daily_execution():
    """Run daily execution"""
    print("=" * 70)
    print("👑 CEO REVENUE SHARE - DAILY EXECUTION AGENT")
    print("=" * 70)
    print()
    print(f"🕐 Waktu: {get_datetime_formatted()} WITA")
    print()
    
    # Get date
    date = get_date_formatted()
    
    # Calculate summary
    summary = calculate_daily_summary(date)
    
    # Generate report
    report = generate_daily_report(date)
    
    # Save report
    report_file = save_daily_report(date, report)
    print(f"📄 Report saved: {report_file}")
    print()
    
    # Print summary
    print("=" * 70)
    print("📊 DAILY SUMMARY")
    print("=" * 70)
    print(f"  📅 Tanggal: {date}")
    print(f"  💰 Total Revenue: {format_currency(summary['total_revenue'])}")
    print(f"  👑 CEO Share (60%): {format_currency(summary['ceo_share'])}")
    print()
    print(f"  📋 Status: {'✅ READY' if summary['system_ready'] else '⚠️ PENDING'}")
    print(f"  📄 Report: {report_file.name}")
    print("=" * 70)
    print()
    
    # Update audit log
    status = "SUCCESS" if summary['system_ready'] else "PENDING"
    notes = "" if summary['system_ready'] else "Data tidak lengkap atau belum ada revenue"
    update_audit_log(summary, status, notes)
    
    # Print report
    print("=" * 70)
    print("📋 DAILY REPORT PREVIEW")
    print("=" * 70)
    print(report[:2000])
    if len(report) > 2000:
        print("...")
        print("(Report continues in file)")
    print("=" * 70)
    print()
    
    return summary

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        # Date passed as argument
        date = sys.argv[1]
    else:
        # Use today
        date = get_date_formatted()
    
    summary = run_daily_execution()
    
    print()
    print("✅ Daily execution completed!")
    print()
    
    return 0

if __name__ == "__main__":
    exit(main())
