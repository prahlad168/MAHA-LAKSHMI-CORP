#!/usr/bin/env python3
"""
Global Sales Daily Report
MAHA LAKSHMI HOLDINGS
"""

import json
import csv
from datetime import datetime, timedelta
from pathlib import Path

def load_tracker():
    try:
        with open('outreach-tracker.json', 'r') as f:
            return json.load(f)
    except: return {"emails": [], "stats": {"total_sent": 0, "responses": 0, "deals_closed": 0}}

def load_deals():
    try:
        with open('deals-pipeline.json', 'r') as f:
            return json.load(f)
    except: return {"deals": [], "stats": {"total_deals": 0, "total_value": 0}}

def load_leads():
    try:
        with open('leads-global.csv', 'r') as f:
            return list(csv.DictReader(f))
    except: return []

def generate_report():
    today = datetime.now().strftime("%Y-%m-%d")
    
    tracker = load_tracker()
    deals = load_deals()
    leads = load_leads()
    
    # Stats
    total_sent = tracker['stats']['total_sent']
    total_responses = tracker['stats']['responses']
    total_deals = deals['stats']['total_deals']
    total_value = deals['stats']['total_value']
    total_leads = len(leads)
    
    # Today's emails
    today_emails = [e for e in tracker['emails'] if e['timestamp'].startswith(today)]
    
    # Response rate
    response_rate = (total_responses / total_sent * 100) if total_sent > 0 else 0
    
    report = f"""# 📊 Global Sales Daily Report

**Date:** {today}
**Company:** MAHA LAKSHMI HOLDINGS
**Agent:** AI Global Sales Agent

---

## 📈 TODAY'S PROGRESS

| Metric | Value | Target |
|--------|-------|--------|
| Emails Sent Today | {len(today_emails)} | 50 |
| Total Leads in DB | {total_leads} | 1000+ |
| Total Emails Sent | {total_sent} | - |
| Responses | {total_responses} | - |
| Deals Closed | {total_deals} | - |
| Revenue (USDT) | ${total_value:.2f} | $500-2000/mo |

---

## 📊 KEY METRICS

- **Response Rate:** {response_rate:.1f}%
- **Average Deal Size:** ${total_value/max(total_deals,1):.2f}
- **Pipeline Value:** ${sum(d.get('value',0) for d in deals['deals']):.2f}

---

## 🌍 LEADS BY COUNTRY

| Country | Leads | % |
|---------|-------|---|
| USA | {sum(1 for l in leads if l.get('country')=='USA')} | {sum(1 for l in leads if l.get('country')=='USA')/max(len(leads),1)*100:.0f}% |
| UK | {sum(1 for l in leads if l.get('country')=='UK')} | {sum(1 for l in leads if l.get('country')=='UK')/max(len(leads),1)*100:.0f}% |
| Australia | {sum(1 for l in leads if l.get('country')=='Australia')} | {sum(1 for l in leads if l.get('country')=='Australia')/max(len(leads),1)*100:.0f}% |
| Singapore | {sum(1 for l in leads if l.get('country')=='Singapore')} | {sum(1 for l in leads if l.get('country')=='Singapore')/max(len(leads),1)*100:.0f}% |

---

## 💰 DEALS PIPELINE

| Stage | Count | Value |
|-------|-------|-------|
| Qualified | {sum(1 for d in deals['deals'] if d.get('stage')=='qualified')} | ${sum(d.get('value',0) for d in deals['deals'] if d.get('stage')=='qualified'):.2f} |
| Proposal Sent | {sum(1 for d in deals['deals'] if d.get('stage')=='proposal')} | ${sum(d.get('value',0) for d in deals['deals'] if d.get('stage')=='proposal'):.2f} |
| Negotiation | {sum(1 for d in deals['deals'] if d.get('stage')=='negotiation')} | ${sum(d.get('value',0) for d in deals['deals'] if d.get('stage')=='negotiation'):.2f} |
| Closed Won | {sum(1 for d in deals['deals'] if d.get('stage')=='closed_won')} | ${sum(d.get('value',0) for d in deals['deals'] if d.get('stage')=='closed_won'):.2f} |

---

## 🎯 TOMORROW'S TARGETS

- [ ] Send 50 emails
- [ ] Follow up on {sum(1 for e in tracker['emails'] if not e.get('responded') and 'followup' not in e.get('status',''))} non-responded leads
- [ ] Generate 50 new leads
- [ ] Close at least 1 deal

---

## 💳 PAYMENT INFO

**USDT TRC20 Address:** TNFs1SP2C8HxGSJkSH3hJamf8ukgtnW7U6

---

*Report generated: {datetime.now().isoformat()}*
*MAHA LAKSHMI HOLDINGS - AI Global Sales Agent*
"""
    
    # Save report
    report_path = f"progress/global-sales-{today}.md"
    Path("progress").mkdir(exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(report)
    print(f"\n💾 Report saved to: {report_path}")

if __name__ == "__main__":
    generate_report()
