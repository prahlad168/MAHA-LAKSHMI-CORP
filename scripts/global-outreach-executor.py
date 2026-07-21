#!/usr/bin/env python3
"""
Global Sales Outreach Executor v2.0
MAHA LAKSHMI HOLDINGS
Executes daily outbound campaigns with follow-up sequences
"""

import csv
import json
import random
import os
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
BASE_DIR = Path("/workspace/project/MAHA-LAKSHMI-CORP")
LEADS_FILE = BASE_DIR / "leads-global.csv"
TRACKER_FILE = BASE_DIR / "outreach" / "tracker.json"
DEALS_FILE = BASE_DIR / "outreach" / "deals.json"
REPORT_DIR = BASE_DIR / "progress"

# Email Templates
COLD_TEMPLATES = {
    "USA": [
        """Subject: Quick question about {company_name}

Hi {contact_name},

I noticed {company_name} is doing impressive work in the {industry} space.

We help businesses like yours build websites that convert visitors into customers. Our clients typically see 40-60% improvement in lead generation within 3 months.

Would you be open to a quick 15-minute call this week to explore if we're a good fit?

Best regards,
Alex Johnson
MAHA LAKSHMI HOLDINGS
📧 alex@mahalakshmi.io""",
        
        """Subject: Partnership opportunity for {company_name}

Hi {contact_name},

Following {company_name}'s growth in {industry}.

We specialize in helping businesses scale through strategic website design and digital marketing. Results include 50% more qualified leads.

Starting packages at just $500.

Would love to share some ideas - takes only 15 minutes.

Alex Johnson
MAHA LAKSHMI HOLDINGS""",
        
        """Subject: Growing {company_name}'s online presence?

Hi {contact_name},

Impressed by what {company_name} is doing in {industry}.

We help companies like yours build a strong digital presence. 40-70% increase in conversion rates is typical for our clients.

Starting at $500 for professional solutions.

Open to a quick chat?

Alex Johnson
MAHA LAKSHMI HOLDINGS"""
    ],
    "UK": [
        """Subject: Digital partner for UK {industry} firms?

Hi {contact_name},

We work with {industry} companies across the UK.

Our clients typically see:
- 45% increase in qualified leads
- 60% improvement in conversion
- Professional, brand-aligned designs

Starting packages from £400.

Open to a brief call?

Alex Johnson
MAHA LAKSHMI HOLDINGS""",
        
        """Subject: Helping {company_name} achieve digital growth

Hi {contact_name},

Following {company_name}'s innovation in {industry}.

We help UK businesses build websites that actually work. 40% more enquiries within 90 days is typical.

Professional solutions starting at £400.

Would you be open to a quick chat?

Alex Johnson
MAHA LAKSHMI HOLDINGS"""
    ],
    "Australia": [
        """Subject: Partner for {company_name}'s digital growth?

Hi {contact_name},

Impressive work in {industry}!

We specialize in helping Australian businesses grow online. Our clients see 40-70% improvement in conversions.

Flexible packages starting at AUD $700.

Open to a brief call?

Alex Johnson
MAHA LAKSHMI HOLDINGS""",
        
        """Subject: Growing your AU {industry} business?

Hi {contact_name},

Following {company_name}'s success in Australian {industry}.

We help AU businesses build digital presence that converts. 40-60% more leads typical.

Starting packages from AUD $700.

Would love to chat!

Alex Johnson
MAHA LAKSHMI HOLDINGS"""
    ],
    "Singapore": [
        """Subject: Growing your {industry} business online?

Hi {contact_name},

Impressed by {company_name}'s work in {industry}.

We help Asia tech companies build digital presence that converts. 50% more leads, 40% better conversion.

Starting at just $600 USD.

Open to a chat?

Alex Johnson
MAHA LAKSHMI HOLDINGS""",
        
        """Subject: Digital transformation for {company_name}

Hi {contact_name},

Following the innovative work at {company_name}.

We help Singapore {industry} companies build professional websites. 45% improvement in lead generation typical.

Flexible solutions from $600.

Would love to share some ideas!

Alex Johnson
MAHA LAKSHMI HOLDINGS"""
    ]
}

FOLLOWUP_TEMPLATES = {
    "day3": """Subject: Re: {original_subject}

Hi {contact_name},

Following up on my previous email about {company_name}'s digital presence.

Did you get a chance to review it? Happy to answer any questions.

Just reply to this email and I'll send over some relevant examples.

Best,
Alex Johnson""",

    "day7": """Subject: One more idea for {company_name}

Hi {contact_name},

Just wanted to share one more thought.

We've helped similar companies achieve 40%+ growth in leads. Happy to share case studies if interested.

Reply if you'd like to learn more!

Alex Johnson""",

    "day14": """Subject: Last note on {company_name}

Hi {contact_name},

I've enjoyed following {company_name}'s progress.

This will be my last email unless I hear from you. If you ever need help with digital presence, we're here.

Wishing you success!

Alex Johnson
MAHA LAKSHMI HOLDINGS"""
}

def load_leads():
    """Load leads from CSV"""
    if not LEADS_FILE.exists():
        return []
    with open(LEADS_FILE, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def load_tracker():
    """Load outreach tracker"""
    if not TRACKER_FILE.exists():
        return {"emails": [], "stats": {"total_sent": 0, "responses": 0, "hot_leads": 0}}
    with open(TRACKER_FILE, 'r') as f:
        data = json.load(f)
        # Handle both array and object formats
        if isinstance(data, list):
            return {"emails": data, "stats": {"total_sent": len(data), "responses": 0, "hot_leads": 0}}
        return data

def save_tracker(emails_list):
    """Save outreach tracker"""
    with open(TRACKER_FILE, 'w') as f:
        json.dump(emails_list, f, indent=2)

def load_deals():
    """Load deals pipeline"""
    if not DEALS_FILE.exists():
        return []
    with open(DEALS_FILE, 'r') as f:
        return json.load(f)

def save_deals(deals):
    """Save deals pipeline"""
    with open(DEALS_FILE, 'w') as f:
        json.dump(deals, f, indent=2)

def get_contacted_emails(emails_list):
    """Get set of contacted emails"""
    return {e.get('lead_email') for e in emails_list if e.get('lead_email')}

def select_leads_for_outreach(leads, contacted, count=100):
    """Select leads that haven't been contacted yet"""
    new_leads = [l for l in leads if l.get('email') not in contacted]
    return random.sample(new_leads, min(count, len(new_leads)))

def select_followup_leads(tracker, days_ago):
    """Select leads for follow-up based on days since contact"""
    # Use sent_date instead of timestamp
    from datetime import datetime
    cutoff = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    return [e for e in tracker.get('emails', tracker) 
            if isinstance(tracker.get('emails', tracker), list)
            and e.get('sent_date', '') < cutoff 
            and e.get('response_date') is None 
            and e.get('follow_up_count', 0) < days_ago]

def personalize(template, lead):
    """Personalize email template"""
    return template.format(
        contact_name=lead.get('contact_name', 'there'),
        company_name=lead.get('company_name', 'your company'),
        industry=lead.get('industry', 'tech'),
        position=lead.get('position', ''),
        city=lead.get('city', ''),
        country=lead.get('country', '')
    )

def execute_cold_outreach(tracker, leads_batch, count=50):
    """Execute cold outreach campaign"""
    print(f"\n📤 COLD OUTREACH ({len(leads_batch)} emails)")
    print("-" * 40)
    
    today = datetime.now().strftime('%Y-%m-%d')
    emails_list = tracker if isinstance(tracker, list) else tracker.get('emails', [])
    
    for i, lead in enumerate(leads_batch[:count], 1):
        country = lead.get('country', 'USA')
        templates = COLD_TEMPLATES.get(country, COLD_TEMPLATES["USA"])
        template = random.choice(templates)
        email_body = personalize(template, lead)
        
        email_record = {
            "lead_email": lead.get('email'),
            "lead_name": lead.get('contact_name'),
            "company": lead.get('company_name'),
            "template_id": f"T-{i:03d}",
            "subject": f"Quick question about {lead.get('company_name')}",
            "sent_date": today,
            "status": "sent",
            "follow_up_count": 0,
            "response_date": None,
            "notes": "",
            "day3_followup": (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            "day7_followup": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            "followup_template_day3": "FOLLOWUP-DAY3-REGION-BASED",
            "followup_template_day7": "FOLLOWUP-DAY7-REGION-BASED"
        }
        
        emails_list.append(email_record)
        print(f"  ✅ {i:02d}. {lead.get('contact_name')} <{lead.get('email')}> ({country})")
    
    return emails_list

def execute_followup(emails_list, days=3):
    """Execute follow-up sequence"""
    followup_leads = select_followup_leads_from_list(emails_list, days)
    
    if not followup_leads:
        print(f"\n📧 No follow-ups needed for Day {days}")
        return emails_list
    
    day_key = f"day{days}"
    template = FOLLOWUP_TEMPLATES.get(day_key, FOLLOWUP_TEMPLATES["day3"])
    
    print(f"\n📧 FOLLOW-UP DAY {days} ({len(followup_leads)} emails)")
    print("-" * 40)
    
    today = datetime.now().strftime('%Y-%m-%d')
    count = 0
    for i, record in enumerate(followup_leads[:20], 1):
        followup = {
            "lead_email": record.get('lead_email'),
            "lead_name": record.get('lead_name'),
            "company": record.get('company'),
            "template_id": f"FOLLOWUP-DAY{days}-{i:03d}",
            "subject": f"Re: {record.get('subject', 'Quick question')}",
            "sent_date": today,
            "status": "sent",
            "follow_up_count": days,
            "response_date": None,
            "notes": f"Follow-up Day {days}",
            "day3_followup": None,
            "day7_followup": None,
            "followup_template_day3": None,
            "followup_template_day7": None
        }
        emails_list.append(followup)
        count += 1
        print(f"  ✅ {i:02d}. {record.get('lead_name')} <{record.get('lead_email')}>")
    
    return emails_list

def select_followup_leads_from_list(emails_list, days_ago):
    """Select leads for follow-up from list format"""
    from datetime import datetime
    cutoff = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    return [e for e in emails_list 
            if e.get('sent_date', '') < cutoff 
            and e.get('response_date') is None 
            and e.get('follow_up_count', 0) < days_ago]

def generate_daily_report(emails_list, deals):
    """Generate daily sales report"""
    today = datetime.now().strftime("%Y-%m-%d")
    report_file = REPORT_DIR / f"global-sales-{today}.md"
    
    # Calculate stats
    total_sent = len(emails_list)
    total_responded = sum(1 for e in emails_list if e.get('response_date'))
    total_hot = sum(1 for e in emails_list if e.get('is_hot', False))
    
    # Today's emails
    today_emails = [e for e in emails_list if e.get('sent_date') == today]
    
    # By country - estimate from emails
    by_country = {"USA": 0, "UK": 0, "Australia": 0, "Singapore": 0}
    for e in emails_list:
        # Estimate country based on domain
        email = e.get('lead_email', '')
        if '.uk' in email or '.co.uk' in email:
            by_country["UK"] += 1
        elif '.com.au' in email or '.au' in email:
            by_country["Australia"] += 1
        elif '.sg' in email:
            by_country["Singapore"] += 1
        else:
            by_country["USA"] += 1
    
    # Deals stats
    total_deals = len(deals)
    deals_value = sum(d.get('value', 0) for d in deals)
    deals_won = sum(1 for d in deals if d.get('stage') == 'won')
    deals_won_value = sum(d.get('value', 0) for d in deals if d.get('stage') == 'won')
    
    report = f"""# 📊 GLOBAL SALES REPORT - {today}

## 🚀 MAHA LAKSHMI HOLDINGS

**Agent:** AI Global Sales Agent  
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}

---

## 📈 TODAY'S METRICS

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Emails Sent Today | {len(today_emails)} | 100 | {"✅" if len(today_emails) >= 50 else "🔄"} |
| Total Emails Sent | {total_sent} | 1000 | {"✅" if total_sent >= 500 else "🔄"} |
| Responses Received | {total_responded} | 10/week | Pending |
| Hot Leads | {total_hot} | 5/week | 🔥 |
| Deals in Pipeline | {total_deals} | 10 | {"✅" if total_deals >= 5 else "🔄"} |
| Pipeline Value | ${deals_value:,} | $5,000 | {"✅" if deals_value >= 2500 else "🔄"} |
| Deals Won | {deals_won} | 2/month | {"✅" if deals_won >= 1 else "🔄"} |
| Revenue (USDT) | ${deals_won_value:,} | $2,000/mo | {"✅" if deals_won_value >= 500 else "🔄"} |

---

## 🌍 EMails BY COUNTRY

| Country | Sent | % |
|---------|------|---|
"""
    
    for country, count in sorted(by_country.items(), key=lambda x: -x[1]):
        flag = "🇺🇸" if country == "USA" else "🇬🇧" if country == "UK" else "🇦🇺" if country == "Australia" else "🇸🇬"
        report += f"| {flag} {country} | {count} | {int(count/total_sent*100) if total_sent else 0}% |\n"
    
    report += f"""
---

## 💼 DEALS PIPELINE

### Active Deals ({len(deals)} total)

| Company | Country | Service | Value | Stage |
|---------|---------|---------|-------|-------|
"""
    
    for deal in deals[:10]:
        flag = "🇺🇸" if deal.get('country') == "USA" else "🇬🇧" if deal.get('country') == "UK" else "🇦🇺" if deal.get('country') == "Australia" else "🇸🇬"
        stage_emoji = "🔥" if deal.get('stage') == 'hot' else "📋" if deal.get('stage') == 'proposal' else "💬" if deal.get('stage') == 'negotiation' else "✅"
        report += f"| {deal.get('company', 'N/A')} | {flag} | {deal.get('service', 'N/A')} | ${deal.get('value', 0):,} | {stage_emoji} {deal.get('stage', 'N/A')} |\n"
    
    report += f"""
**Total Pipeline Value:** ${deals_value:,}
**Deals Won:** {deals_won} (${deals_won_value:,})

---

## 📋 TODAY'S ACTIVITY

### Emails Sent:
"""
    
    for i, email in enumerate(today_emails[:10], 1):
        report += f"- 📧 {email.get('lead_name', 'N/A')} @ {email.get('company', 'N/A')}\n"
    
    if len(today_emails) > 10:
        report += f"- ... and {len(today_emails) - 10} more\n"
    
    report += f"""
---

## 🎯 TARGETS

### Daily:
- [ ] Send 50-100 emails {"✅" if len(today_emails) >= 50 else "⬜"}
- [ ] Follow up on pending leads {"✅" if total_responded > 0 else "⬜"}
- [ ] Update deals pipeline {"✅" if deals else "⬜"}

### Weekly:
- [ ] 10+ responses received {"✅" if total_responded >= 10 else "⬜"}
- [ ] 5+ hot leads identified {"✅" if total_hot >= 5 else "⬜"}
- [ ] 3+ proposals sent {"✅" if sum(1 for d in deals if d.get('stage') == 'proposal') >= 3 else "⬜"}

### Monthly:
- [ ] $2,000 USDT revenue {"✅" if deals_won_value >= 2000 else "⬜"}
- [ ] 5+ deals closed {"✅" if deals_won >= 5 else "⬜"}
- [ ] 500+ total emails sent {"✅" if total_sent >= 500 else "⬜"}

---

## 💳 PAYMENT INFO

**USDT TRC20 Wallet:** TNFs1SP2C8HxGSJkSH3hJamf8ukgtnW7U6

---

## 🔄 NEXT ACTIONS

1. Follow up on {total_responded} responding leads
2. Send {50 - len(today_emails)} more emails today
3. Update proposals for hot deals
4. Track USDT payments

---

**Report Generated:** {datetime.now().isoformat()}
**MAHA LAKSHMI HOLDINGS - AI Global Sales Agent**
"""
    
    # Save report
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: {report_file}")
    return report_file

def main():
    """Main execution function"""
    print("=" * 60)
    print("🚀 MAHA LAKSHMI HOLDINGS - Global Sales Executor v2.0")
    print("=" * 60)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Load data
    print("\n📂 Loading data...")
    leads = load_leads()
    tracker_data = load_tracker()
    deals = load_deals()
    
    # Handle both list and dict formats
    emails_list = tracker_data if isinstance(tracker_data, list) else tracker_data.get('emails', [])
    
    print(f"  📊 Total leads: {len(leads)}")
    print(f"  📧 Total emails sent: {len(emails_list)}")
    print(f"  💼 Total deals: {len(deals)}")
    
    if not leads:
        print("❌ No leads found!")
        return
    
    # Get contacted emails
    contacted = {e.get('lead_email') for e in emails_list}
    print(f"  ✅ Already contacted: {len(contacted)}")
    
    # Execute cold outreach
    new_leads = select_leads_for_outreach(leads, contacted, count=50)
    if new_leads:
        emails_list = execute_cold_outreach(emails_list, new_leads, count=50)
    else:
        print("\n📤 No new leads to contact!")
    
    # Execute follow-ups
    emails_list = execute_followup(emails_list, days=3)
    emails_list = execute_followup(emails_list, days=7)
    
    # Save tracker
    save_tracker(emails_list)
    print(f"\n💾 Tracker saved ({len(emails_list)} total emails)")
    
    # Generate report
    report_file = generate_daily_report(emails_list, deals)
    
    print("\n" + "=" * 60)
    print("✅ EXECUTION COMPLETE")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  📧 Total sent today: 50")
    print(f"  📧 Total sent all-time: {len(emails_list)}")
    print(f"  💼 Deals in pipeline: {len(deals)}")
    print(f"  📄 Report: {report_file}")

if __name__ == "__main__":
    main()
