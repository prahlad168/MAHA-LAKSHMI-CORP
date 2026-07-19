#!/usr/bin/env python3
"""
Global Sales Daily Report Generator
MAHA LAKSHMI HOLDINGS
Generates daily progress reports
"""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List

def load_csv_data(filename: str) -> List[Dict]:
    """Load data from CSV file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except:
        return []

def load_json_data(filename: str) -> Dict:
    """Load data from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except:
        return {}

def calculate_stats() -> Dict:
    """Calculate daily statistics"""
    # Load leads
    leads = load_csv_data("/workspace/project/MAHA-LAKSHMI-CORP/leads-global.csv")
    
    # Load outreach tracker
    tracker = load_json_data("/workspace/project/MAHA-LAKSHMI-CORP/outreach-tracker.json")
    
    # Load deals pipeline
    deals = load_json_data("/workspace/project/MAHA-LAKSHMI-CORP/deals-pipeline.json")
    
    # Load invoices
    invoices_summary = {
        "pending": {"count": 0, "total_usd": 0},
        "paid": {"count": 0, "total_usd": 0}
    }
    try:
        invoices_dir = "/workspace/project/MAHA-LAKSHMI-CORP/invoices"
        if os.path.exists(invoices_dir):
            for filename in os.listdir(invoices_dir):
                if filename.endswith(".json"):
                    with open(f"{invoices_dir}/{filename}", 'r') as f:
                        invoice = json.load(f)
                        if invoice.get('status') == 'paid':
                            invoices_summary['paid']['count'] += 1
                            invoices_summary['paid']['total_usd'] += invoice.get('total_usd', 0)
                        else:
                            invoices_summary['pending']['count'] += 1
                            invoices_summary['pending']['total_usd'] += invoice.get('total_usd', 0)
    except:
        pass
    
    # Calculate stats
    today = datetime.now().strftime("%Y-%m-%d")
    today_stats = tracker.get("daily_stats", {}).get(today, {})
    
    # Count leads by country
    by_country = {"USA": 0, "UK": 0, "Australia": 0, "Singapore": 0}
    for lead in leads:
        country = lead.get("country", "")
        if country in by_country:
            by_country[country] += 1
    
    # Count leads by status
    by_status = {}
    for lead in leads:
        status = lead.get("status", "new")
        by_status[status] = by_status.get(status, 0) + 1
    
    # Count closed deals
    closed_deals = [d for d in deals.get("deals", []) if d.get("stage") == "closed_won"]
    
    return {
        "total_leads": len(leads),
        "leads_by_country": by_country,
        "leads_by_status": by_status,
        "emails_sent_today": today_stats.get("sent", 0),
        "emails_opened_today": today_stats.get("opened", 0),
        "emails_responded_today": today_stats.get("responded", 0),
        "total_emails_sent": tracker.get("metadata", {}).get("total_sent", 0),
        "total_deals": len(deals.get("deals", [])),
        "closed_deals": len(closed_deals),
        "usdt_paid": invoices_summary['paid']['total_usd'],
        "usdt_pending": invoices_summary['pending']['total_usd']
    }

def generate_report() -> str:
    """Generate daily report in markdown format"""
    today = datetime.now().strftime("%Y-%m-%d")
    stats = calculate_stats()
    
    report = f"""# 📊 Global Sales Daily Report

**Date:** {today}
**Generated:** {datetime.now().strftime("%H:%M:%S")} WIB
**Agent:** AI Global Sales Agent - MAHA LAKSHMI HOLDINGS

---

## 🎯 TODAY'S STATISTICS

| Metric | Value |
|--------|-------|
| 📧 Emails Sent Today | {stats['emails_sent_today']} |
| 👀 Emails Opened | {stats['emails_opened_today']} |
| 💬 Responses | {stats['emails_responded_today']} |
| 💰 USDT Received | ${stats['usdt_paid']:.2f} |

---

## 📈 LEADS DATABASE

| Country | Leads |
|---------|-------|
| 🇺🇸 USA | {stats['leads_by_country'].get('USA', 0)} |
| 🇬🇧 UK | {stats['leads_by_country'].get('UK', 0)} |
| 🇦🇺 Australia | {stats['leads_by_country'].get('Australia', 0)} |
| 🇸🇬 Singapore | {stats['leads_by_country'].get('Singapore', 0)} |
| **Total** | **{stats['total_leads']}** |

### Leads by Status:
"""
    
    for status, count in stats['leads_by_status'].items():
        report += f"- {status.title()}: {count}\n"
    
    report += f"""
---

## 📧 OUTREACH PERFORMANCE

| Metric | Value |
|--------|-------|
| Total Emails Sent | {stats['total_emails_sent']} |
| Open Rate | {(stats['emails_opened_today'] / max(stats['emails_sent_today'], 1) * 100):.1f}% |
| Response Rate | {(stats['emails_responded_today'] / max(stats['emails_sent_today'], 1) * 100):.1f}% |

---

## 💼 DEALS PIPELINE

| Metric | Value |
|--------|-------|
| Active Deals | {stats['total_deals']} |
| Closed Won | {stats['closed_deals']} |
| USDT Pending | ${stats['usdt_pending']:.2f} |
| **USDT Received** | **${stats['usdt_paid']:.2f}** |

---

## 🎯 REVENUE TARGETS

| Metric | Target | Current | Progress |
|--------|--------|---------|----------|
| Monthly USDT | $500-2000 | ${stats['usdt_paid']:.2f} | {(stats['usdt_paid'] / 2000 * 100):.1f}% |
| Leads Database | 1000 | {stats['total_leads']} | {(stats['total_leads'] / 1000 * 100):.1f}% |
| Emails Sent/Month | 800 | {stats['total_emails_sent']} | {(stats['total_emails_sent'] / 800 * 100):.1f}% |

---

## 📋 NEXT ACTIONS

1. ✅ Continue generating new leads (target: 50/day)
2. ✅ Send daily outreach emails (target: 50/day)
3. ✅ Follow up with warm leads
4. ✅ Send proposals to interested leads
5. ✅ Generate USDT invoices for closed deals

---

## 💳 PAYMENT INFORMATION

**USDT TRC20 Wallet:**
```
TNFs1SP2C8HxGSJkSH3hJamf8ukgtnW7U6
```

---

*Report generated by AI Global Sales Agent*
*MAHA LAKSHMI HOLDINGS*
"""
    
    return report

def save_report():
    """Save report to file"""
    today = datetime.now().strftime("%Y-%m-%d")
    report = generate_report()
    
    # Ensure progress directory exists
    os.makedirs("/workspace/project/MAHA-LAKSHMI-CORP/progress", exist_ok=True)
    
    # Save markdown report
    filename = f"/workspace/project/MAHA-LAKSHMI-CORP/progress/global-sales-{today}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Report saved to: {filename}")
    return filename

def main():
    """Main function"""
    print("🤖 MAHA LAKSHMI HOLDINGS - Daily Report Generator")
    print("=" * 50)
    
    # Generate and display report
    report = generate_report()
    print(report)
    
    # Save report
    filename = save_report()
    
    print("\n" + "=" * 50)
    print(f"✅ Report saved to: {filename}")

if __name__ == "__main__":
    main()
