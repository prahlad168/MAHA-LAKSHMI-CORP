#!/usr/bin/env python3
"""
Global Sales Outreach Script
MAHA LAKSHMI HOLDINGS
"""

import csv
import json
import random
from datetime import datetime, timedelta

TEMPLATES = {
    "cold_usa_tech": """Subject: Quick question about {company_name}

Hi {contact_name},

I noticed {company_name} is doing interesting work in {industry}.

We build high-converting websites and apps for businesses. 40-60% increase in online presence in 3 months.

Is your digital presence driving the results you want?

I'd love to show you how we can help - starting at $500.

Open to a quick 15-minute call?

Best,
Alex Johnson
MAHA LAKSHMI HOLDINGS
alex@mahalakshmi.io""",

    "cold_usa_healthcare": """Subject: Helping {industry} companies grow online

Hi {contact_name},

Impressed by {company_name}'s work in {industry}.

How's your digital presence working for you?

We help healthcare companies build websites that convert. 50% more patient inquiries in 60 days.

Flexible packages starting at $500.

Interested?

Alex Johnson
MAHA LAKSHMI HOLDINGS""",

    "cold_uk": """Subject: Digital partner for UK {industry} firms?

Hi {contact_name},

We work with {industry} companies across the UK.

45% increase in qualified leads in 90 days.

Professional websites, lead generation, client portals.

Open to a brief call?

Alex Johnson
MAHA LAKSHMI HOLDINGS""",

    "cold_australia": """Subject: Partner for {company_name}'s digital growth?

Hi {contact_name},

Impressive work in {industry}!

We help AU tourism/hospitality businesses. 40-70% increase in bookings.

Brief chat?

Alex Johnson
MAHA LAKSHMI HOLDINGS""",

    "cold_singapore": """Subject: Growing your {industry} business online?

Hi {contact_name},

Following {company_name}'s work in {industry}.

We help Asia tech companies build digital presence that converts.

50% more leads, 40% better conversion.

Open to a chat?

Alex Johnson
MAHA LAKSHMI HOLDINGS"""
}

def get_template(lead):
    country = lead.get('country', 'USA')
    industry = lead.get('industry', '').lower()
    if country == 'USA':
        if 'health' in industry or 'medical' in industry:
            return TEMPLATES['cold_usa_healthcare']
        return TEMPLATES['cold_usa_tech']
    elif country == 'UK':
        return TEMPLATES['cold_uk']
    elif country == 'Australia':
        return TEMPLATES['cold_australia']
    return TEMPLATES['cold_singapore']

def personalize(template, lead):
    return template.format(
        contact_name=lead.get('contact_name', 'there'),
        company_name=lead.get('company_name', 'your company'),
        industry=lead.get('industry', 'tech')
    )

def load_leads():
    try:
        with open('leads-global.csv', 'r') as f:
            return list(csv.DictReader(f))
    except: return []

def load_tracker():
    try:
        with open('outreach-tracker.json', 'r') as f:
            return json.load(f)
    except: return {"emails": [], "stats": {"total_sent": 0, "responses": 0}}

def save_tracker(t):
    with open('outreach-tracker.json', 'w') as f:
        json.dump(t, f, indent=2)

def main():
    print("🚀 Global Sales Outreach - MAHA LAKSHMI HOLDINGS")
    print("=" * 50)
    
    leads = load_leads()
    if not leads:
        print("❌ No leads found!")
        return
    
    tracker = load_tracker()
    contacted = {e['lead_email'] for e in tracker['emails']}
    new_leads = [l for l in leads if l.get('email') not in contacted]
    
    print(f"📊 Total: {len(leads)} | Contacted: {len(contacted)} | New: {len(new_leads)}")
    
    batch = min(50, len(new_leads))
    if batch == 0:
        print("❌ No new leads!")
        return
    
    todays = random.sample(new_leads, batch)
    print(f"\n📤 Sending {len(todays)} emails...")
    
    for i, lead in enumerate(todays, 1):
        template = get_template(lead)
        email_body = personalize(template, lead)
        
        tracker['emails'].append({
            "id": f"email_{datetime.now().strftime('%Y%m%d')}_{i}",
            "timestamp": datetime.now().isoformat(),
            "lead_email": lead.get('email'),
            "lead_name": lead.get('contact_name'),
            "company": lead.get('company_name'),
            "country": lead.get('country'),
            "status": "sent",
            "email_body": email_body,
            "responded": False
        })
        tracker['stats']['total_sent'] += 1
        print(f"  {i}. ✅ {lead.get('contact_name')} <{lead.get('email')}>")
    
    save_tracker(tracker)
    
    print("\n" + "=" * 50)
    print(f"✅ Sent {len(todays)} emails")
    print(f"📊 Total sent: {tracker['stats']['total_sent']}")

if __name__ == "__main__":
    main()
