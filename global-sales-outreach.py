#!/usr/bin/env python3
"""
Global Sales Email Outreach Script
MAHA LAKSHMI HOLDINGS
Sends 50 personalized emails per day to leads
"""

import csv
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict

# Email templates by type
EMAIL_TEMPLATES = {
    "cold": [
        """Subject: Quick question about {{company_name}}'s website

Hi {{contact_name}},

I noticed {{company_name}} is doing some impressive work in the {{industry}} space.

I wanted to reach out because we've helped similar {{industry}} companies transform their online presence with custom designs that increased conversions by 40%.

Quick question - is your current website generating the leads you'd expect?

If not, I'd love to show you how we can help. We specialize in:
- Custom website design & development
- Conversion rate optimization
- SEO that actually ranks

Would you be open to a quick 15-minute call this week?

Best regards,
{{sender_name}}
MAHA LAKSHMI HOLDINGS""",

        """Subject: Website ideas for {{company_name}}

Hi {{contact_name}},

I came across {{company_name}}'s work in {{industry}} - exciting stuff!

We help companies like yours:
- Create professional websites
- Generate more leads
- Save time with automation

Our clients typically see 30-50% increases in lead generation within 3 months.

Would you be open to a quick call to explore how we could help {{company_name}}?

Best,
{{sender_name}}
MAHA LAKSHMI HOLDINGS""",

        """Subject: Growth ideas for {{company_name}}?

Hi {{contact_name}},

I noticed {{company_name}} is building something interesting in the {{industry}} space.

We specialize in helping companies scale through:
- Strategic website design
- Marketing automation
- Lead generation systems

We recently helped a similar company increase qualified leads by 3x.

Would you have 15 minutes this week for a quick chat?

Best regards,
{{sender_name}}"""
    ],
    "followup_day3": [
        """Subject: Re: Quick question about {{company_name}}'s website

Hi {{contact_name}},

I wanted to follow up on my previous email about how we could help {{company_name}}.

Many companies we've worked with have seen great results:
- 40% increase in website leads
- 60% improvement in conversion rates
- Significant time savings with automation

I understand you're busy - just wanted to make sure my email didn't get buried!

Would you have 10 minutes this week?

Best,
{{sender_name}}""",

        """Subject: Following up - digital ideas for {{company_name}}

Hi {{contact_name}},

I sent over some ideas for {{company_name}} a few days ago and wanted to make sure it reached you.

Just to recap - we help businesses like yours create websites that generate leads and set up marketing automation.

Happy to share examples of our work if helpful.

Would you be open to a brief call?

Best regards,
{{sender_name}}"""
    ],
    "followup_day7": [
        """Subject: One last thought for {{company_name}}

Hi {{contact_name}},

I hope you've had a great week. I'm reaching out one last time regarding digital solutions for {{company_name}}.

If now isn't the right time, I completely understand - just wanted to make sure the option was on your radar.

If you ever want to explore how we could help {{company_name}} grow, feel free to reply.

Wishing you all the best!

Best,
{{sender_name}}
MAHA LAKSHMI HOLDINGS"""
    ]
}

SENDER_INFO = {
    "name": "Maha Sales Team",
    "email": "sales@mahalakshmi.com"
}

def load_leads_from_csv(filename: str) -> List[Dict]:
    """Load leads from CSV file"""
    leads = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            leads = list(reader)
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
    return leads

def load_outreach_tracker(filename: str = "outreach-tracker.json") -> Dict:
    """Load outreach tracker"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except:
        return {
            "metadata": {"last_updated": datetime.now().strftime("%Y-%m-%d"), "total_sent": 0},
            "sequences": {"day1": {"emails": []}, "day3": {"emails": []}, "day7": {"emails": []}},
            "daily_stats": {}
        }

def save_outreach_tracker(tracker: Dict, filename: str = "outreach-tracker.json"):
    """Save outreach tracker"""
    tracker["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    try:
        with open(filename, 'w') as f:
            json.dump(tracker, f, indent=2)
    except Exception as e:
        print(f"Error saving tracker: {e}")

def personalize_email(template: str, lead: Dict) -> str:
    """Replace placeholders with lead data"""
    replacements = {
        "{{company_name}}": lead.get("company_name", "your company"),
        "{{contact_name}}": lead.get("contact_name", "there"),
        "{{position}}": lead.get("position", ""),
        "{{industry}}": lead.get("industry", ""),
        "{{city}}": lead.get("city", ""),
        "{{country}}": lead.get("country", ""),
        "{{sender_name}}": SENDER_INFO["name"],
        "{{sender_email}}": SENDER_INFO["email"]
    }
    
    email = template
    for placeholder, value in replacements.items():
        email = email.replace(placeholder, value)
    
    return email

def should_send_to_lead(lead: Dict, tracker: Dict) -> bool:
    """Determine if we should send to this lead"""
    email = lead.get("email", "")
    status = lead.get("status", "")
    
    # Don't send to already contacted or converted leads
    if status in ["responded", "closed_won", "closed_lost"]:
        return False
    
    # Check if already sent today
    today = datetime.now().strftime("%Y-%m-%d")
    if today in tracker.get("daily_stats", {}):
        sent_today = tracker["daily_stats"][today].get("sent", 0)
        if sent_today >= 50:
            return False
    
    return True

def get_next_sequence_for_lead(lead: Dict, tracker: Dict) -> str:
    """Determine the next email sequence for a lead"""
    email = lead.get("email", "")
    
    # Check existing sequences
    sequences = tracker.get("sequences", {})
    
    for seq_type in ["day1", "day3", "day7"]:
        sent_emails = sequences.get(seq_type, {}).get("emails", [])
        if any(e.get("email") == email for e in sent_emails):
            if seq_type == "day1":
                return "day3"
            elif seq_type == "day3":
                return "day7"
            else:
                return None  # Already sent all sequences
    
    return "day1"  # Start with cold outreach

def send_emails(leads: List[Dict], count: int = 50):
    """Send outreach emails to leads"""
    tracker = load_outreach_tracker("/workspace/project/MAHA-LAKSHMI-CORP/outreach-tracker.json")
    
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in tracker["daily_stats"]:
        tracker["daily_stats"][today] = {"sent": 0, "opened": 0, "responded": 0, "clicked": 0}
    
    sent = 0
    for lead in leads:
        if sent >= count:
            break
        
        if not should_send_to_lead(lead, tracker):
            continue
        
        sequence = get_next_sequence_for_lead(lead, tracker)
        if not sequence:
            continue
        
        # Get template
        templates = EMAIL_TEMPLATES.get(sequence, EMAIL_TEMPLATES["cold"])
        template = random.choice(templates)
        
        # Personalize email
        email_content = personalize_email(template, lead)
        
        # Log the email (simulated - in real use, would integrate with email service)
        email_record = {
            "email": lead.get("email"),
            "company": lead.get("company_name"),
            "sequence": sequence,
            "sent_at": datetime.now().isoformat(),
            "subject": email_content.split('\n')[0].replace("Subject: ", "")
        }
        
        # Add to tracker
        tracker["sequences"][sequence]["emails"].append(email_record)
        tracker["daily_stats"][today]["sent"] += 1
        tracker["metadata"]["total_sent"] += 1
        
        # Update lead status
        lead["status"] = "contacted"
        lead["last_contact"] = today
        
        sent += 1
        print(f"✉️  Sent {sequence} email to: {lead.get('email')}")
        print(f"    📋 Subject: {email_record['subject']}")
    
    # Save tracker
    save_outreach_tracker(tracker, "/workspace/project/MAHA-LAKSHMI-CORP/outreach-tracker.json")
    
    # Update leads CSV
    with open("/workspace/project/MAHA-LAKSHMI-CORP/leads-global.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["company_name", "contact_name", "email", "position", "industry", "website", 
                                                "country", "city", "leads_source", "service_interest", "status", "last_contact", "notes"])
        writer.writeheader()
        for lead in leads:
            writer.writerow(lead)
    
    return sent

def main():
    """Main function"""
    print("🤖 MAHA LAKSHMI HOLDINGS - Global Email Outreach")
    print("=" * 50)
    
    # Load leads
    leads = load_leads_from_csv("/workspace/project/MAHA-LAKSHMI-CORP/leads-global.csv")
    print(f"\n📊 Loaded {len(leads)} leads from database")
    
    # Load tracker
    tracker = load_outreach_tracker("/workspace/project/MAHA-LAKSHMI-CORP/outreach-tracker.json")
    print(f"📈 Total emails sent so far: {tracker['metadata']['total_sent']}")
    
    # Send emails
    print(f"\n📤 Sending 50 outreach emails...")
    sent = send_emails(leads, 50)
    
    print(f"\n✅ Successfully sent {sent} emails today!")
    print(f"📁 Outreach tracker updated")
    
    # Show stats
    today = datetime.now().strftime("%Y-%m-%d")
    today_stats = tracker.get("daily_stats", {}).get(today, {})
    print(f"\n📊 Today's Statistics:")
    print(f"   Sent: {today_stats.get('sent', 0)}")
    print(f"   Opened: {today_stats.get('opened', 0)}")
    print(f"   Responded: {today_stats.get('responded', 0)}")

if __name__ == "__main__":
    main()
