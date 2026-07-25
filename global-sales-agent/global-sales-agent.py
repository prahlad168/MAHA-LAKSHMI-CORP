#!/usr/bin/env python3
"""
🌍 GLOBAL SALES AGENT - MAHA LAKSHMI
Target: International SMEs yang butuh digital transformation
Revenue: USD $5,000 - $50,000/month
Mode: Autonomous outreach + follow-up + closing
"""

import json
import random
import time
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional

# ============== GLOBAL LEADS DATABASE ==============
GLOBAL_LEADS = [
    # USA
    {"company": "TechStart Solutions", "email": "contact@techstart.io", "industry": "Technology", "size": "11-50", "country": "USA", "website": "techstart.io", "contact": "John Smith", "linkedin": "johnsmith-tech"},
    {"company": "CloudNine Systems", "email": "hello@cloudnine.tech", "industry": "SaaS", "size": "51-200", "country": "USA", "website": "cloudnine.tech", "contact": "Sarah Johnson", "linkedin": "sarah-johnson"},
    {"company": "DataFlow Analytics", "email": "sales@dataflow.ai", "industry": "AI/ML", "size": "11-50", "country": "USA", "website": "dataflow.ai", "contact": "Mike Chen", "linkedin": "mike-chen-ai"},
    {"company": "ShopNow Platform", "email": "contact@shopnow.io", "industry": "E-Commerce", "size": "11-50", "country": "USA", "website": "shopnow.io", "contact": "Emily Davis", "linkedin": "emily-davis-ecom"},
    {"company": "MoneyWise App", "email": "hello@moneywise.io", "industry": "FinTech", "size": "11-50", "country": "USA", "website": "moneywise.io", "contact": "David Wilson", "linkedin": "david-wilson-fintech"},
    
    # UK
    {"company": "FinServe Corp", "email": "contact@finserve.com", "industry": "Finance", "size": "51-200", "country": "UK", "website": "finserve.com", "contact": "James Brown", "linkedin": "james-brown-finance"},
    {"company": "HealthTech Solutions", "email": "hello@healthtech.io", "industry": "HealthTech", "size": "11-50", "country": "UK", "website": "healthtech.io", "contact": "Emma Wilson", "linkedin": "emma-wilson-health"},
    {"company": "RetailBoost", "email": "hello@retailboost.co", "industry": "RetailTech", "size": "11-50", "country": "UK", "website": "retailboost.co", "contact": "Oliver Jones", "linkedin": "oliver-jones-retail"},
    {"company": "LegalEase Partners", "email": "contact@legalease.law", "industry": "LegalTech", "size": "11-50", "country": "UK", "website": "legalease.law", "contact": "Sophie Taylor", "linkedin": "sophie-taylor-legal"},
    {"company": "ConsultPro Group", "email": "hello@consultpro.co", "industry": "Consulting", "size": "51-200", "country": "UK", "website": "consultpro.co", "contact": "Robert Miller", "linkedin": "robert-miller-consulting"},
    
    # Australia
    {"company": "MediCare Plus", "email": "contact@medicareplus.com", "industry": "Healthcare", "size": "51-200", "country": "Australia", "website": "medicareplus.com", "contact": "Linda Taylor", "linkedin": "linda-taylor-health"},
    {"company": "TrustFinance Ltd", "email": "info@trustfinance.au", "industry": "Finance", "size": "11-50", "country": "Australia", "website": "trustfinance.au", "contact": "Mark Johnson", "linkedin": "mark-johnson-finance"},
    {"company": "SkillsFirst Institute", "email": "info@skillsfirst.au", "industry": "Education", "size": "11-50", "country": "Australia", "website": "skillsfirst.au", "contact": "Sarah Williams", "linkedin": "sarah-williams-edu"},
    {"company": "Aussie Tech Hub", "email": "hello@aussietech.com.au", "industry": "Technology", "size": "11-50", "country": "Australia", "website": "aussietech.com.au", "contact": "Chris Evans", "linkedin": "chris-evans-tech"},
    {"company": "GrowthPath Advisory", "email": "contact@growthpath.com.au", "industry": "Consulting", "size": "11-50", "country": "Australia", "website": "growthpath.com.au", "contact": "Amanda White", "linkedin": "amanda-white-advisory"},
    
    # Singapore
    {"company": "InnovateTech Lab", "email": "info@innovatetech.co", "industry": "Technology", "size": "1-10", "country": "Singapore", "website": "innovatetech.co", "contact": "Kevin Lee", "linkedin": "kevin-lee-tech"},
    {"company": "TravelMate Asia", "email": "hello@travelmate.asia", "industry": "Tourism", "size": "11-50", "country": "Singapore", "website": "travelmate.asia", "contact": "Rachel Tan", "linkedin": "rachel-tan-travel"},
    {"company": "MarketFresh", "email": "info@marketfresh.sg", "industry": "E-Commerce", "size": "11-50", "country": "Singapore", "website": "marketfresh.sg", "contact": "Daniel Lim", "linkedin": "daniel-lim-ecom"},
    {"company": "LearnHub Asia", "email": "hello@learnhub.asia", "industry": "EdTech", "size": "11-50", "country": "Singapore", "website": "learnhub.asia", "contact": "Michelle Wong", "linkedin": "michelle-wong-edu"},
    {"company": "HR Solutions Asia", "email": "info@hrsolutions.asia", "industry": "HRTech", "size": "11-50", "country": "Singapore", "website": "hrsolutions.asia", "contact": "Alex Chen", "linkedin": "alex-chen-hr"},
    
    # Europe
    {"company": "Berlin Digital", "email": "contact@berlin-digital.de", "industry": "Technology", "size": "11-50", "country": "Germany", "website": "berlin-digital.de", "contact": "Hans Mueller", "linkedin": "hans-mueller-tech"},
    {"company": "Paris Creative", "email": "hello@pariscreative.fr", "industry": "Design", "size": "11-50", "country": "France", "website": "pariscreative.fr", "contact": "Marie Dubois", "linkedin": "marie-dubois-design"},
    {"company": "Amsterdam FinTech", "email": "info@amsterdamfintech.nl", "industry": "FinTech", "size": "11-50", "country": "Netherlands", "website": "amsterdamfintech.nl", "contact": "Jan de Vries", "linkedin": "jan-devries-fintech"},
    {"company": "Barcelona Tourism", "email": "contact@barcelonatourism.es", "industry": "Tourism", "size": "51-200", "country": "Spain", "website": "barcelonatourism.es", "contact": "Carlos Garcia", "linkedin": "carlos-garcia-travel"},
    {"company": "Milan Fashion Tech", "email": "hello@milanfashiontech.it", "industry": "FashionTech", "size": "11-50", "country": "Italy", "website": "milanfashiontech.it", "contact": "Giuseppe Rossi", "linkedin": "giuseppe-rossi-fashion"},
    
    # Middle East
    {"company": "Dubai Digital", "email": "contact@dubaidigital.ae", "industry": "Technology", "size": "51-200", "country": "UAE", "website": "dubaidigital.ae", "contact": "Ahmed Al-Mansoori", "linkedin": "ahmed-almansoori"},
    {"company": "Riyadh Tech", "email": "hello@riyadhtech.sa", "industry": "Technology", "size": "11-50", "country": "Saudi Arabia", "website": "riyadhtech.sa", "contact": "Mohammed Al-Saud", "linkedin": "mohammed-alsaud"},
]

# ============== EMAIL TEMPLATES ==============
EMAIL_TEMPLATES = {
    "initial": """Subject: Quick question about {company}'s digital growth

Hi {first_name},

I noticed {company} ({website}) is doing interesting work in {industry}.

We help {industry} companies like yours:
• Increase leads by 40-60% within 90 days
• Build professional websites that convert
• Automate customer acquisition

Recent results for similar companies:
- {industry} company in {country} → 3x more qualified leads
- Saved 20+ hours/week with marketing automation

Would you be open to a quick 15-minute call this week?

If not, no worries - I'll follow up in a week.

Best,
Alex Johnson
MAHA LAKSHMI HOLDINGS
📧 alex@mahalakshmi.io
🌐 mahalakshmi.web.id""",

    "followup": """Subject: Re: Quick question about {company}

Hi {first_name},

Following up on my previous email about helping {company} grow.

I know you're busy, so I'll keep this short:

🔥 We helped a {industry} company in {country}:
   - 150% increase in website traffic
   - 3x more demo requests
   - 40% improvement in conversion rate

Would a quick 15-min call this Thursday work?

Or simply reply "interested" and I'll send over our case study.

Either way, I'd love to connect.

Best,
Alex Johnson""",

    "value_proposition": """Subject: How {company} can get 3x more leads

Hi {first_name},

I did some research on {company} and have a quick idea:

{industry} companies we work with typically see:
📈 40-60% increase in qualified leads
⏱️ 50% reduction in customer acquisition time  
💰 ROI positive within the first month

If you're open to it, I'd love to share exactly how we'd approach {company}'s growth.

Quick 15-min call this week?

Best,
Alex Johnson
MAHA LAKSHMI HOLDINGS""",

    "final_offer": """Subject: Limited: Digital growth package for {company}

Hi {first_name},

I'm following up one last time about {company}.

I have a special offer for the first 3 companies this month:

🚀 DIGITAL GROWTH PACKAGE
├── Professional Website ($2,500 value)
├── SEO & Marketing Automation ($1,500 value)
├── Lead Generation System ($2,000 value)
└── TOTAL VALUE: $6,000
    SPECIAL PRICE: $1,997 (67% OFF)

This includes:
✅ Complete website redesign
✅ SEO optimization
✅ Marketing automation setup
✅ Lead capture forms
✅ 30 days support

If interested, reply "YES" and I'll send invoice immediately.

Best,
Alex Johnson
MAHA LAKSHMI HOLDINGS"""
}

# ============== LINKEDIN MESSAGES ==============
LINKEDIN_MESSAGES = {
    "connection": "Hi {first_name}, I'm from MAHA LAKSHMI - we help {industry} companies scale digitally. Would love to connect!",
    "followup": "Thanks for connecting! I saw {company} is doing great work in {industry}. We just helped a similar company increase leads by 150%. Would you be open to a quick chat?",
    "pitch": "I have a specific idea for {company} that could increase your digital revenue by 40-60% in 90 days. Would 15 minutes this week work?"
}

# ============== SALES AGENT ==============
class GlobalSalesAgent:
    def __init__(self):
        self.leads = GLOBAL_LEADS
        self.email_templates = EMAIL_TEMPLATES
        self.linkedin_messages = LINKEDIN_MESSAGES
        self.campaigns = []
        self.stats = {
            "emails_sent": 0,
            "linkedin_sent": 0,
            "responses": 0,
            "meetings": 0,
            "deals": 0,
            "revenue_usd": 0
        }
    
    def generate_personalized_email(self, lead: Dict, template_type: str = "initial") -> str:
        """Generate personalized email based on lead data"""
        template = self.email_templates[template_type]
        first_name = lead["contact"].split()[0]
        
        email = template.format(
            company=lead["company"],
            website=lead["website"],
            industry=lead["industry"],
            country=lead["country"],
            first_name=first_name
        )
        
        return email
    
    def generate_linkedin_message(self, lead: Dict, message_type: str = "connection") -> str:
        """Generate LinkedIn message"""
        template = self.linkedin_messages[message_type]
        first_name = lead["contact"].split()[0]
        
        message = template.format(
            company=lead["company"],
            industry=lead["industry"],
            first_name=first_name
        )
        
        return message
    
    def create_email_campaign(self, batch_size: int = 10) -> Dict:
        """Create email campaign for a batch of leads"""
        campaign = {
            "campaign_id": f"global-email-{datetime.now().strftime('%Y%m%d-%H%M')}",
            "created": datetime.now().isoformat(),
            "batch_size": batch_size,
            "emails": []
        }
        
        for i, lead in enumerate(self.leads[:batch_size]):
            email_data = {
                "lead": lead,
                "sequence": [
                    {
                        "day": 1,
                        "type": "initial",
                        "subject": f"Quick question about {lead['company']}'s digital growth",
                        "status": "ready_to_send"
                    },
                    {
                        "day": 4,
                        "type": "followup",
                        "subject": f"Re: Quick question about {lead['company']}",
                        "status": "scheduled"
                    },
                    {
                        "day": 7,
                        "type": "value_proposition",
                        "subject": f"How {lead['company']} can get 3x more leads",
                        "status": "scheduled"
                    },
                    {
                        "day": 10,
                        "type": "final_offer",
                        "subject": f"Limited: Digital growth package for {lead['company']}",
                        "status": "scheduled"
                    }
                ]
            }
            campaign["emails"].append(email_data)
        
        self.campaigns.append(campaign)
        return campaign
    
    def create_linkedin_campaign(self, batch_size: int = 10) -> Dict:
        """Create LinkedIn outreach campaign"""
        campaign = {
            "campaign_id": f"global-linkedin-{datetime.now().strftime('%Y%m%d-%H%M')}",
            "created": datetime.now().isoformat(),
            "batch_size": batch_size,
            "messages": []
        }
        
        for i, lead in enumerate(self.leads[:batch_size]):
            message_data = {
                "lead": lead,
                "sequence": [
                    {
                        "day": 1,
                        "type": "connection",
                        "message": self.generate_linkedin_message(lead, "connection"),
                        "status": "ready_to_send"
                    },
                    {
                        "day": 3,
                        "type": "followup",
                        "message": self.generate_linkedin_message(lead, "followup"),
                        "status": "scheduled"
                    },
                    {
                        "day": 7,
                        "type": "pitch",
                        "message": self.generate_linkedin_message(lead, "pitch"),
                        "status": "scheduled"
                    }
                ]
            }
            campaign["messages"].append(message_data)
        
        self.campaigns.append(campaign)
        return campaign
    
    def send_email(self, lead: Dict, template_type: str = "initial") -> bool:
        """Send email to a lead (simulation mode - no actual sending)"""
        email_content = self.generate_personalized_email(lead, template_type)
        
        # In production, this would use SMTP or email service
        print(f"📧 Email to: {lead['email']}")
        print(f"   Company: {lead['company']} ({lead['country']})")
        print(f"   Template: {template_type}")
        print(f"   Status: SIMULATED (not sent)")
        print()
        
        self.stats["emails_sent"] += 1
        return True
    
    def send_linkedin_message(self, lead: Dict, message_type: str = "connection") -> bool:
        """Send LinkedIn message (simulation mode)"""
        message = self.generate_linkedin_message(lead, message_type)
        
        print(f"💼 LinkedIn to: {lead['contact']} @ {lead['company']}")
        print(f"   Type: {message_type}")
        print(f"   Message: {message[:100]}...")
        print(f"   Status: SIMULATED (not sent)")
        print()
        
        self.stats["linkedin_sent"] += 1
        return True
    
    def run_daily_outreach(self, email_batch: int = 10, linkedin_batch: int = 10):
        """Run daily outreach routine"""
        print("=" * 70)
        print("🌍 GLOBAL SALES AGENT - DAILY OUTREACH")
        print("=" * 70)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Total Leads Available: {len(self.leads)}")
        print(f"🎯 Target Today: {email_batch} emails, {linkedin_batch} LinkedIn")
        print("=" * 70)
        
        # Email campaign
        print("\n📧 EMAIL OUTREACH")
        print("-" * 70)
        email_campaign = self.create_email_campaign(email_batch)
        for email_data in email_campaign["emails"]:
            self.send_email(email_data["lead"], "initial")
        
        # LinkedIn campaign
        print("\n💼 LINKEDIN OUTREACH")
        print("-" * 70)
        linkedin_campaign = self.create_linkedin_campaign(linkedin_batch)
        for message_data in linkedin_campaign["messages"]:
            self.send_linkedin_message(message_data["lead"], "connection")
        
        # Save campaigns
        self.save_campaigns()
        
        # Print stats
        self.print_stats()
        
        return {
            "email_campaign": email_campaign,
            "linkedin_campaign": linkedin_campaign,
            "stats": self.stats
        }
    
    def run_followup_sequence(self):
        """Run follow-up sequence for previous campaigns"""
        print("=" * 70)
        print("🔄 FOLLOW-UP SEQUENCE")
        print("=" * 70)
        
        for campaign in self.campaigns:
            if "emails" in campaign:
                for email_data in campaign["emails"]:
                    for seq in email_data["sequence"]:
                        if seq["status"] == "scheduled" and seq["day"] == 4:
                            self.send_email(email_data["lead"], "followup")
                            seq["status"] = "sent"
                        elif seq["status"] == "scheduled" and seq["day"] == 7:
                            self.send_email(email_data["lead"], "value_proposition")
                            seq["status"] = "sent"
                        elif seq["status"] == "scheduled" and seq["day"] == 10:
                            self.send_email(email_data["lead"], "final_offer")
                            seq["status"] = "sent"
        
        self.save_campaigns()
    
    def save_campaigns(self):
        """Save campaigns to file"""
        output_file = f"global-sales-campaign-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "campaigns": self.campaigns,
                "stats": self.stats,
                "generated": datetime.now().isoformat()
            }, f, indent=2)
        print(f"\n💾 Campaigns saved: {output_file}")
    
    def print_stats(self):
        """Print campaign statistics"""
        print("\n" + "=" * 70)
        print("📊 CAMPAIGN STATISTICS")
        print("=" * 70)
        print(f"📧 Emails Sent: {self.stats['emails_sent']}")
        print(f"💼 LinkedIn Messages: {self.stats['linkedin_sent']}")
        print(f"💬 Responses: {self.stats['responses']}")
        print(f"📅 Meetings Booked: {self.stats['meetings']}")
        print(f"💰 Deals Closed: {self.stats['deals']}")
        print(f"💵 Revenue (USD): ${self.stats['revenue_usd']:,.2f}")
        print("=" * 70)
    
    def generate_report(self) -> str:
        """Generate daily report"""
        report = f"""
🌍 GLOBAL SALES AGENT - DAILY REPORT
=====================================
Date: {datetime.now().strftime('%Y-%m-%d')}
Time: {datetime.now().strftime('%H:%M:%S')}

📊 STATISTICS:
- Emails Sent: {self.stats['emails_sent']}
- LinkedIn Messages: {self.stats['linkedin_sent']}
- Responses: {self.stats['responses']}
- Meetings: {self.stats['meetings']}
- Deals Closed: {self.stats['deals']}
- Revenue: ${self.stats['revenue_usd']:,.2f}

🎯 TARGETS:
- Daily Emails: 50
- Daily LinkedIn: 30
- Weekly Responses: 10
- Monthly Deals: 5

📈 PROJECTIONS:
- If 5% response rate: {int(self.stats['emails_sent'] * 0.05)} responses
- If 20% close rate: {int(self.stats['emails_sent'] * 0.05 * 0.2)} deals
- At $2,000 avg: ${int(self.stats['emails_sent'] * 0.05 * 0.2 * 2000):,} revenue

🚀 NEXT ACTIONS:
1. Monitor responses
2. Follow up with interested leads
3. Schedule calls
4. Send proposals
5. Close deals

MAHA LAKSHMI GLOBAL SALES AGENT
"""
        return report


def main():
    """Main execution"""
    agent = GlobalSalesAgent()
    
    # Run daily outreach
    results = agent.run_daily_outreach(email_batch=20, linkedin_batch=15)
    
    # Generate report
    report = agent.generate_report()
    print(report)
    
    # Save report
    report_file = f"global-sales-report-{datetime.now().strftime('%Y%m%d')}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    return agent


if __name__ == "__main__":
    agent = main()
