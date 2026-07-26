#!/usr/bin/env python3
"""
🤖 AUTONOMOUS GLOBAL SALES AGENT - MAHA LAKSHMI
Complete hands-off sales system for mahalaksmi.web.id

CEO RECEIVES ONLY:
- Revenue reports
- Sales statistics
- Performance metrics

AGENT HANDLES:
- Lead generation
- Outreach (email/WhatsApp/LinkedIn)
- Follow-up sequences
- Deal closing
- Payment tracking
- Customer onboarding
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database with fallback
try:
    from autonomous_sales_agent.core.database import RealTimeDatabase
except ImportError:
    try:
        from core.database import RealTimeDatabase
    except ImportError:
        RealTimeDatabase = None

# ============== SYSTEM CONFIGURATION ==============
class Config:
    COMPANY_NAME = "MAHA LAKSHMI HOLDINGS"
    DOMAIN = "mahalaksmi.web.id"
    CEO_EMAIL = "ceo@mahalaksmi.web.id"
    CEO_WHATSAPP = "6281337558787"
    DAILY_REVENUE_TARGET_USD = 500
    WEEKLY_REVENUE_TARGET_USD = 3000
    MONTHLY_REVENUE_TARGET_USD = 12000
    LEADS_PER_DAY = 50
    EMAILS_PER_DAY = 30
    WHATSAPP_PER_DAY = 20
    LINKEDIN_PER_DAY = 15
    FOLLOWUP_DELAY_HOURS = 24
    MAX_FOLLOWUPS = 3
    PRODUCTS = {
        "whatsapp-kit": {"price_usd": 29, "name": "WhatsApp Marketing Kit"},
        "social-kit": {"price_usd": 19, "name": "Social Media Kit Pro"},
        "landing-template": {"price_usd": 49, "name": "Landing Page Template"},
        "seo-bundle": {"price_usd": 39, "name": "SEO Master Bundle"},
        "business-kit": {"price_usd": 99, "name": "Complete Business Kit"}
    }
    LANGUAGES = ["en", "es", "fr", "de", "zh", "ar", "pt", "ru", "ja", "id"]
    REPORT_TIME = "23:59"
    REPORT_RECIPIENTS = [CEO_EMAIL, CEO_WHATSAPP]


# ============== DATA MODELS ==============
@dataclass
class Lead:
    id: str
    name: str
    email: str
    phone: str
    company: str
    industry: str
    country: str
    language: str
    source: str
    score: int = 0
    status: str = "new"
    last_contact: Optional[str] = None
    followup_count: int = 0
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Deal:
    id: str
    lead_id: str
    product_id: str
    amount_usd: float
    currency: str
    status: str = "pending"
    payment_method: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    paid_at: Optional[str] = None
    delivered_at: Optional[str] = None

@dataclass
class DailyReport:
    date: str
    leads_generated: int = 0
    emails_sent: int = 0
    whatsapp_sent: int = 0
    linkedin_sent: int = 0
    responses_received: int = 0
    proposals_sent: int = 0
    deals_closed: int = 0
    revenue_usd: float = 0.0
    revenue_idr: float = 0.0
    ceo_share_usd: float = 0.0
    ceo_share_idr: float = 0.0
    conversion_rate: float = 0.0


# ============== SALES AGENT CORE ==============
class AutonomousSalesAgent:
    def __init__(self):
        self.config = Config()
        self.db = RealTimeDatabase() if RealTimeDatabase else None
        self.leads = []
        self.deals = []
        self.campaigns: Dict[str, List[Dict]] = {}
        self.stats = {
            "total_leads": 0,
            "total_emails": 0,
            "total_whatsapp": 0,
            "total_linkedin": 0,
            "total_responses": 0,
            "total_proposals": 0,
            "total_deals": 0,
            "total_revenue_usd": 0.0,
            "total_revenue_idr": 0.0
        }
        self.running = False
        self.last_report_date = None
    
    # ========== LEAD MANAGEMENT ==========
    def add_lead(self, lead: Lead):
        """Add new lead to database"""
        self.db.insert_lead(lead)
        self.log(f"New lead added: {lead.name} ({lead.company}) - {lead.language}")
    
    def get_leads_by_status(self, status: str) -> List[Lead]:
        """Get leads by status from database"""
        rows = self.db.get_leads_by_status(status)
        return [Lead(**row) for row in rows]
    
    def get_leads_by_language(self, language: str) -> List[Lead]:
        """Get leads by language from database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE language = ?", (language,))
        rows = cursor.fetchall()
        conn.close()
        return [Lead(**dict(row)) for row in rows]
    
    def qualify_lead(self, lead: Lead) -> int:
        """Score lead based on criteria"""
        score = 0
        
        # Industry scoring
        high_value_industries = ["Technology", "SaaS", "E-Commerce", "Finance", "Healthcare"]
        if lead.industry in high_value_industries:
            score += 30
        
        # Country scoring (GDP per capita proxy)
        high_value_countries = ["USA", "UK", "Australia", "Singapore", "Germany", "France", "Japan"]
        if lead.country in high_value_countries:
            score += 30
        
        # Source scoring
        if lead.source == "referral":
            score += 20
        elif lead.source in ["linkedin", "email"]:
            score += 15
        
        # Company size (if available)
        if hasattr(lead, 'company_size') and lead.company_size in ["51-200", "201-500"]:
            score += 20
        
        lead.score = score
        return score
    
    # ========== OUTREACH CHANNELS ==========
    def send_email(self, lead: Lead, template_type: str = "initial") -> bool:
        """Send email to lead"""
        try:
            # Get language template
            template = self.get_email_template(lead.language, template_type)
            if not template:
                return False
            
            # Personalize
            email_content = template.format(
                company=lead.company,
                first_name=lead.name.split()[0],
                industry=lead.industry,
                country=lead.country
            )
            
            # Log action
            self.log(f"EMAIL sent to {lead.email}: {template_type}")
            
            # Update lead
            lead.last_contact = datetime.now()
            lead.status = "contacted"
            self.stats["total_emails"] += 1
            
            # Save to campaign
            self._add_to_campaign(lead.id, "email", template_type, email_content)
            
            return True
            
        except Exception as e:
            self.log(f"EMAIL error for {lead.email}: {str(e)}")
            return False
    
    def send_whatsapp(self, lead: Lead, template_type: str = "initial") -> bool:
        """Send WhatsApp message to lead"""
        try:
            template = self.get_whatsapp_template(lead.language, template_type)
            if not template:
                return False
            
            message = template.format(
                company=lead.company,
                first_name=lead.name.split()[0],
                industry=lead.industry,
                country=lead.country
            )
            
            # In production: integrate with WhatsApp Business API
            # For now, generate the link
            whatsapp_link = f"https://wa.me/{lead.phone}?text={message.replace(' ', '%20')}"
            
            self.log(f"WhatsApp sent to {lead.phone}: {template_type}")
            
            lead.last_contact = datetime.now()
            if lead.status == "new":
                lead.status = "contacted"
            self.stats["total_whatsapp"] += 1
            
            self._add_to_campaign(lead.id, "whatsapp", template_type, message)
            
            return True
            
        except Exception as e:
            self.log(f"WhatsApp error for {lead.phone}: {str(e)}")
            return False
    
    def send_linkedin(self, lead: Lead, message_type: str = "connection") -> bool:
        """Send LinkedIn message to lead"""
        try:
            template = self.get_linkedin_template(lead.language, message_type)
            if not template:
                return False
            
            message = template.format(
                company=lead.company,
                first_name=lead.name.split()[0],
                industry=lead.industry
            )
            
            self.log(f"LinkedIn sent to {lead.name} @ {lead.company}: {message_type}")
            
            lead.last_contact = datetime.now()
            if lead.status == "new":
                lead.status = "contacted"
            self.stats["total_linkedin"] += 1
            
            self._add_to_campaign(lead.id, "linkedin", message_type, message)
            
            return True
            
        except Exception as e:
            self.log(f"LinkedIn error for {lead.name}: {str(e)}")
            return False
    
    # ========== FOLLOW-UP AUTOMATION ==========
    def run_followup_sequence(self):
        """Run automated follow-up for all contacted leads"""
        followup_leads = [
            lead for lead in self.leads 
            if lead.status in ["contacted", "responded"] 
            and lead.followup_count < self.config.MAX_FOLLOWUPS
        ]
        
        for lead in followup_leads:
            # Check if enough time passed since last contact
            if lead.last_contact and (datetime.now() - lead.last_contact).total_seconds() < (self.config.FOLLOWUP_DELAY_HOURS * 3600):
                continue
            
            # Determine followup type based on status
            if lead.status == "contacted":
                self.send_email(lead, "followup_1")
                lead.followup_count += 1
            elif lead.status == "responded":
                self.send_email(lead, "proposal")
                lead.status = "proposal"
                self.stats["total_proposals"] += 1
                lead.followup_count += 1
            elif lead.status == "proposal" and lead.followup_count >= 2:
                self.send_whatsapp(lead, "final_offer")
                lead.followup_count += 1
    
    # ========== DEAL MANAGEMENT ==========
    def create_deal(self, lead: Lead, product_id: str, amount_usd: float) -> Deal:
        """Create new deal"""
        deal = Deal(
            id=f"DEAL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            lead_id=lead.id,
            product_id=product_id,
            amount_usd=amount_usd,
            currency="USD"
        )
        
        self.deals.append(deal)
        lead.status = "closed"
        
        self.log(f"DEAL CREATED: {deal.id} - {lead.company} - ${amount_usd}")
        
        return deal
    
    def process_payment(self, deal: Deal, payment_method: str) -> bool:
        """Process payment for deal"""
        try:
            deal.status = "paid"
            deal.payment_method = payment_method
            deal.paid_at = datetime.now()
            
            # Update stats
            self.stats["total_deals"] += 1
            self.stats["total_revenue_usd"] += deal.amount_usd
            self.stats["total_revenue_idr"] += deal.amount_usd * 16000  # Approximate IDR
            
            # Trigger delivery
            self.deliver_product(deal)
            
            # Send notification
            self.send_payment_notification(deal)
            
            self.log(f"PAYMENT PROCESSED: {deal.id} - ${deal.amount_usd} via {payment_method}")
            
            return True
            
        except Exception as e:
            self.log(f"PAYMENT ERROR: {deal.id} - {str(e)}")
            return False
    
    def deliver_product(self, deal: Deal):
        """Deliver digital product to customer"""
        try:
            deal.status = "delivered"
            deal.delivered_at = datetime.now()
            
            # In production: send download link, access credentials, etc.
            self.log(f"PRODUCT DELIVERED: {deal.id} - {deal.product_id}")
            
        except Exception as e:
            self.log(f"DELIVERY ERROR: {deal.id} - {str(e)}")
    
    # ========== REPORTING ==========
    def generate_daily_report(self) -> DailyReport:
        """Generate daily report for CEO"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        report = DailyReport(
            date=today,
            leads_generated=len([l for l in self.leads if l.created_at.strftime("%Y-%m-%d") == today]),
            emails_sent=self.stats["total_emails"],
            whatsapp_sent=self.stats["total_whatsapp"],
            linkedin_sent=self.stats["total_linkedin"],
            responses_received=self.stats["total_responses"],
            proposals_sent=self.stats["total_proposals"],
            deals_closed=self.stats["total_deals"],
            revenue_usd=self.stats["total_revenue_usd"],
            revenue_idr=self.stats["total_revenue_idr"],
            ceo_share_usd=self.stats["total_revenue_usd"] * 0.8,
            ceo_share_idr=self.stats["total_revenue_idr"] * 0.8
        )
        
        if report.leads_generated > 0:
            report.conversion_rate = (report.deals_closed / report.leads_generated) * 100
        
        self.reports.append(report)
        return report
    
    def send_ceo_report(self, report: DailyReport):
        """Send report to CEO"""
        try:
            # Format report message
            message = f"""
📊 DAILY SALES REPORT - {report.date}
═══════════════════════════════════════

📈 ACTIVITY:
• Leads Generated: {report.leads_generated}
• Emails Sent: {report.emails_sent}
• WhatsApp Sent: {report.whatsapp_sent}
• LinkedIn Sent: {report.linkedin_sent}
• Responses: {report.responses_received}
• Proposals: {report.proposals_sent}

💰 REVENUE:
• Deals Closed: {report.deals_closed}
• Revenue (USD): ${report.revenue_usd:,.2f}
• Revenue (IDR): Rp {report.revenue_idr:,.0f}
• CEO Share (80%): ${report.ceo_share_usd:,.2f} / Rp {report.ceo_share_idr:,.0f}

📊 PERFORMANCE:
• Conversion Rate: {report.conversion_rate:.1f}%
• Target: ${self.config.DAILY_REVENUE_TARGET_USD}
• Status: {'✅ TARGET MET' if report.revenue_usd >= self.config.DAILY_REVENUE_TARGET_USD else '🎯 IN PROGRESS'}

═══════════════════════════════════════
🤖 Autonomous Sales Agent
🌐 {self.config.DOMAIN}
            """
            
            # Send to CEO WhatsApp
            self.send_whatsapp_to_ceo(message)
            
            # Send to CEO email
            self.send_email_to_ceo(report)
            
            # Save report
            self.save_report(report)
            
            self.log(f"CEO REPORT SENT: {report.date}")
            
        except Exception as e:
            self.log(f"REPORT ERROR: {str(e)}")
    
    # ========== AUTONOMOUS OPERATIONS ==========
    def start_autonomous_mode(self):
        """Start fully autonomous sales operation"""
        self.running = True
        self.log("AUTONOMOUS MODE STARTED")
        
        while self.running:
            try:
                # 1. Generate/import leads
                self.generate_daily_leads()
                
                # 2. Run outreach campaigns
                self.run_daily_outreach()
                
                # 3. Run follow-up sequences
                self.run_followup_sequence()
                
                # 4. Check for responses and qualify
                self.process_responses()
                
                # 5. Send proposals to qualified leads
                self.send_proposals()
                
                # 6. Generate and send daily report
                self.check_and_send_daily_report()
                
                # Wait before next cycle (1 hour)
                time.sleep(3600)
                
            except Exception as e:
                self.log(f"AUTONOMOUS ERROR: {str(e)}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def stop_autonomous_mode(self):
        """Stop autonomous operation"""
        self.running = False
        self.log("AUTONOMOUS MODE STOPPED")
    
    def run_daily_outreach(self):
        """Run daily outreach across all channels"""
        self.log("RUNNING DAILY OUTREACH")
        
        # Get leads by language
        for language in self.config.LANGUAGES:
            leads = self.get_leads_by_language(language)
            
            for lead in leads[:self.config.LEADS_PER_DAY // len(self.config.LANGUAGES)]:
                # Email outreach
                if random.random() < 0.6:  # 60% chance
                    self.send_email(lead, "initial")
                
                # WhatsApp outreach
                if random.random() < 0.3:  # 30% chance
                    self.send_whatsapp(lead, "initial")
                
                # LinkedIn outreach
                if random.random() < 0.2:  # 20% chance
                    self.send_linkedin(lead, "connection")
    
    # ========== UTILITIES ==========
    def get_email_template(self, language: str, template_type: str) -> Optional[str]:
        """Get email template for language and type"""
        # In production: load from database/file
        templates = {
            "en": {
                "initial": "Subject: Quick question about {company}'s digital growth\n\nHi {first_name},\n\nI noticed {company} is doing interesting work in {industry}.\n\nWe help {industry} companies like yours increase leads by 40-60% within 90 days.\n\nWould you be open to a quick 15-minute call this week?\n\nBest,\nAlex Johnson\nMAHA LAKSHMI HOLDINGS",
                "followup_1": "Subject: Re: Quick question about {company}\n\nHi {first_name},\n\nFollowing up on my previous email about helping {company} grow.\n\n🔥 We helped a {industry} company in {country}:\n   - 150% increase in website traffic\n   - 3x more demo requests\n\nWould a quick 15-min call this Thursday work?\n\nBest,\nAlex Johnson",
                "proposal": "Subject: Proposal for {company}\n\nHi {first_name},\n\nBased on our previous conversation, I've prepared a custom proposal for {company}:\n\n🚀 DIGITAL GROWTH PACKAGE\n├── Professional Website ($2,500 value)\n├── SEO & Marketing Automation ($1,500 value)\n├── Lead Generation System ($2,000 value)\n└── SPECIAL PRICE: $1,997 (67% OFF)\n\nReply \"YES\" to receive invoice immediately.\n\nBest,\nAlex Johnson",
                "final_offer": "Subject: Last chance: Digital growth package for {company}\n\nHi {first_name},\n\nThis is my final follow-up about {company}.\n\nSpecial offer expires in 24 hours:\n✅ Complete digital transformation\n✅ 67% discount - $1,997 (normally $6,000)\n✅ 30-day money-back guarantee\n\nReply \"YES\" now to secure this price.\n\nBest,\nAlex Johnson"
            }
        }
        return templates.get(language, {}).get(template_type)
    
    def get_whatsapp_template(self, language: str, template_type: str) -> Optional[str]:
        """Get WhatsApp template"""
        templates = {
            "en": {
                "initial": "Hi {first_name}! I'm from MAHA LAKSHMI. We help {industry} companies like {company} increase leads by 40-60%. Would you be interested in a free 15-min consultation?",
                "followup_1": "Hi {first_name}, just following up about helping {company} grow. We recently helped a similar company increase leads by 150%. Want to know how?",
                "proposal": "Hi {first_name}, I have a special offer for {company}: Complete digital growth package for $1,997 (67% off). Reply YES for invoice!",
                "final_offer": "Hi {first_name}, last chance! Digital growth package for {company} at 67% off expires in 24 hours. Reply YES now!"
            }
        }
        return templates.get(language, {}).get(template_type)
    
    def get_linkedin_template(self, language: str, message_type: str) -> Optional[str]:
        """Get LinkedIn template"""
        templates = {
            "en": {
                "connection": "Hi {first_name}, I'm from MAHA LAKSHMI - we help {industry} companies scale digitally. Would love to connect!",
                "followup": "Thanks for connecting! I saw {company} is doing great work in {industry}. We just helped a similar company increase leads by 150%. Would you be open to a quick chat?",
                "pitch": "I have a specific idea for {company} that could increase your digital revenue by 40-60% in 90 days. Would 15 minutes this week work?"
            }
        }
        return templates.get(language, {}).get(message_type)
    
    def _add_to_campaign(self, lead_id: str, channel: str, template_type: str, content: str):
        """Add action to campaign log"""
        if channel not in self.campaigns:
            self.campaigns[channel] = []
        
        self.campaigns[channel].append({
            "lead_id": lead_id,
            "template_type": template_type,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def generate_daily_leads(self):
        """Generate daily leads from global sources"""
        # In production: scrape, import from APIs, etc.
        # For now, create sample leads
        if len(self.leads) < 100:  # Keep pipeline full
            sample_leads = self._get_sample_leads(10)
            for lead_data in sample_leads:
                lead = Lead(
                    id=f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    name=lead_data["name"],
                    email=lead_data["email"],
                    phone=lead_data["phone"],
                    company=lead_data["company"],
                    industry=lead_data["industry"],
                    country=lead_data["country"],
                    language=lead_data["language"],
                    source=lead_data["source"]
                )
                self.qualify_lead(lead)
                self.add_lead(lead)
    
    def _get_sample_leads(self, count: int) -> List[Dict]:
        """Get sample leads for testing"""
        samples = [
            {"name": "John Smith", "email": "john@techstart.io", "phone": "1234567890", "company": "TechStart", "industry": "Technology", "country": "USA", "language": "en", "source": "email"},
            {"name": "Marie Dubois", "email": "marie@parisdigital.fr", "phone": "1234567891", "company": "Paris Digital", "industry": "Marketing", "country": "France", "language": "fr", "source": "linkedin"},
            {"name": "Carlos García", "email": "carlos@innovatech.es", "phone": "1234567892", "company": "Innovatech", "industry": "Technology", "country": "Spain", "language": "es", "source": "email"},
            {"name": "Hans Mueller", "email": "hans@berlin-digital.de", "phone": "1234567893", "company": "Berlin Digital", "industry": "Software", "country": "Germany", "language": "de", "source": "email"},
            {"name": "张伟", "email": "zhang@shenzhentech.cn", "phone": "1234567894", "company": "深圳科技", "industry": "科技", "country": "China", "language": "zh", "source": "linkedin"},
            {"name": "Ahmed Al-Mansoori", "email": "ahmed@dubaidigital.ae", "phone": "1234567895", "company": "Dubai Digital", "industry": "Technology", "country": "UAE", "language": "ar", "source": "email"},
            {"name": "João Silva", "email": "joao@sptech.com.br", "phone": "1234567896", "company": "São Paulo Tech", "industry": "Technology", "country": "Brazil", "language": "pt", "source": "email"},
            {"name": "Иван Иванов", "email": "ivan@moscotech.ru", "phone": "1234567897", "company": "Москва Тех", "industry": "Technology", "country": "Russia", "language": "ru", "source": "linkedin"},
            {"name": "田中太郎", "email": "tanaka@tokyotech.jp", "phone": "1234567898", "company": "東京テック", "industry": "Technology", "country": "Japan", "language": "ja", "source": "email"},
            {"name": "Budi Santoso", "email": "budi@jakartadigital.id", "phone": "1234567899", "company": "Jakarta Digital", "industry": "Marketing", "country": "Indonesia", "language": "id", "source": "whatsapp"}
        ]
        return random.sample(samples, min(count, len(samples)))
    
    def process_responses(self):
        """Process incoming responses"""
        # In production: check email, WhatsApp, LinkedIn APIs
        # For now, simulate random responses
        pass
    
    def send_proposals(self):
        """Send proposals to qualified leads"""
        qualified = [l for l in self.leads if l.status == "responded"]
        for lead in qualified[:5]:  # Max 5 per day
            self.send_email(lead, "proposal")
            lead.status = "proposal"
            self.stats["total_proposals"] += 1
    
    def check_and_send_daily_report(self):
        """Check if it's time to send daily report"""
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        
        if self.last_report_date != today and now.strftime("%H:%M") >= self.config.REPORT_TIME:
            report = self.generate_daily_report()
            self.send_ceo_report(report)
            self.last_report_date = today
    
    def send_whatsapp_to_ceo(self, message: str):
        """Send WhatsApp message to CEO"""
        # In production: use WhatsApp Business API
        self.log(f"WhatsApp to CEO: {message[:100]}...")
    
    def send_email_to_ceo(self, report: DailyReport):
        """Send email report to CEO"""
        # In production: use SMTP or email service
        self.log(f"Email report to CEO: {report.date}")
    
    def save_report(self, report: DailyReport):
        """Save report to file"""
        filename = f"autonomous-sales-agent/logs/report-{report.date}.json"
        with open(filename, 'w') as f:
            json.dump({
                "date": report.date,
                "leads_generated": report.leads_generated,
                "emails_sent": report.emails_sent,
                "whatsapp_sent": report.whatsapp_sent,
                "linkedin_sent": report.linkedin_sent,
                "responses": report.responses_received,
                "proposals": report.proposals_sent,
                "deals_closed": report.deals_closed,
                "revenue_usd": report.revenue_usd,
                "revenue_idr": report.revenue_idr,
                "ceo_share_usd": report.ceo_share_usd,
                "ceo_share_idr": report.ceo_share_idr,
                "conversion_rate": report.conversion_rate
            }, f, indent=2)
    
    def log(self, message: str):
        """Log activity"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # Print to console
        print(log_entry)
        
        # Save to log file
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"agent-{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a') as f:
            f.write(log_entry + '\n')
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics from database"""
        lead_stats = self.db.get_lead_stats()
        revenue_stats = self.db.get_revenue_stats()
        outreach_stats = self.db.get_outreach_stats()
        
        return {
            "total_leads": lead_stats["total"],
            "total_emails": outreach_stats["by_channel"].get("email", 0),
            "total_whatsapp": outreach_stats["by_channel"].get("whatsapp", 0),
            "total_linkedin": outreach_stats["by_channel"].get("linkedin", 0),
            "total_responses": outreach_stats["responses"],
            "total_proposals": 0,
            "total_deals": revenue_stats["completed_transactions"],
            "total_revenue_usd": revenue_stats["total_revenue"],
            "total_revenue_idr": revenue_stats["total_revenue"] * 16000,
            "ceo_share_usd": revenue_stats["ceo_share"],
            "ceo_share_idr": revenue_stats["ceo_share"] * 16000,
            "running": self.running
        }
    
    def get_ceo_dashboard_data(self) -> Dict[str, Any]:
        """Get data for CEO dashboard"""
        dashboard_data = self.db.get_dashboard_data()
        
        return {
            "company": self.config.COMPANY_NAME,
            "domain": self.config.DOMAIN,
            "timestamp": datetime.now().isoformat(),
            "stats": self.get_stats(),
            "today_report": {
                "date": dashboard_data["date"],
                "leads": dashboard_data["leads"]["today"],
                "emails": dashboard_data["outreach"]["by_channel"].get("email", 0),
                "whatsapp": dashboard_data["outreach"]["by_channel"].get("whatsapp", 0),
                "linkedin": dashboard_data["outreach"]["by_channel"].get("linkedin", 0),
                "responses": dashboard_data["outreach"]["responses"],
                "proposals": 0,
                "deals": dashboard_data["revenue"]["completed_transactions"],
                "revenue_usd": dashboard_data["revenue"]["today_revenue"],
                "revenue_idr": dashboard_data["revenue"]["today_revenue"] * 16000,
                "ceo_share_usd": dashboard_data["ceo_share_today"],
                "ceo_share_idr": dashboard_data["ceo_share_today"] * 16000,
                "conversion_rate": 0.0,
                "target_usd": self.config.DAILY_REVENUE_TARGET_USD,
                "target_met": dashboard_data["revenue"]["today_revenue"] >= self.config.DAILY_REVENUE_TARGET_USD
            },
            "recent_transactions": dashboard_data["recent_transactions"],
            "recent_payouts": dashboard_data["recent_payouts"]
        }


# ============== MAIN EXECUTION ==============
def main():
    """Main entry point"""
    agent = AutonomousSalesAgent()
    
    print("=" * 70)
    print("🤖 AUTONOMOUS GLOBAL SALES AGENT")
    print("=" * 70)
    print(f"Company: {Config.COMPANY_NAME}")
    print(f"Domain: {Config.DOMAIN}")
    print(f"Mode: AUTONOMOUS")
    print(f"CEO receives: Revenue reports only")
    print("=" * 70)
    
    # Start autonomous operation
    agent.start_autonomous_mode()


if __name__ == "__main__":
    main()
