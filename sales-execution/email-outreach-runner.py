#!/usr/bin/env python3
"""
🤖 AI Email Outreach Script for MAHA LAKSHMI Digital Holdings
Send personalized emails to leads from LEADS-DATABASE.json
"""

import json
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# =======================
# SMTP CONFIGURATION
# =======================
SMTP_CONFIG = {
    'host': 'smtp.gmail.com',
    'port': 587,
    'username': 'mahalakshmiholdings@gmail.com',  # Placeholder
    'password': 'YOUR_APP_PASSWORD',  # Placeholder
    'from_name': 'MAHA LAKSHMI Digital Holdings',
    'from_email': 'mahalakshmiholdings@gmail.com'
}

# =======================
# EMAIL TEMPLATES
# =======================
EMAIL_TEMPLATES = {
    'bali_travel': {
        'subject': 'Partnership Opportunity - Bali Travel Platform',
        'body': """
Halo {name},

Dari **Bali Travel Platform** 🇮🇩

Partner dengan kami untuk tour eksklusif di Bali!

BENEFITS:
✅ Commission 15% per booking
✅ No upfront costs
✅ Professional licensed guides
✅ Real-time booking system
✅ Marketing support included

REVENUE EXAMPLE:
• Tamu rata-rata booking: Rp 1.000.000
• Commission Anda: 15% = Rp 150.000/booking
• Monthly potential: Rp 1.500.000+ (10 bookings)

PARTNER HOTELS & AGENCIES:
• Four Seasons, AYANA, Viceroy
• Local tour operators
• Villa owners

Mau diskusi partnership?
WhatsApp: wa.me/6281337558787

Best regards,
i Made Purna Ananda
CEO, MAHA LAKSHMI Digital Holdings
"""
    },
    'gianyar_tech': {
        'subject': 'Digital Solutions untuk {company}',
        'body': """
Halo {name},

Dari **Gianyar Tech Solutions** 💻

Kami bantu bisnis Anda go-digital!

SERVICES:
✅ Website Company Profile - mulai Rp 2.000.000
✅ Online Shop - mulai Rp 5.000.000
✅ Custom App - mulai Rp 15.000.000
✅ Social Media Management - Rp 3.000.000/bulan

FREE:
✅ Konsultasi 30 menit
✅ Maintenance 3 bulan
✅ Support teknis

WHY US?
✅ Team berpengalaman
✅ 50+ projects completed
✅ Fast delivery
✅ Quality guaranteed

Mau diskusi?
WhatsApp: wa.me/6281337558787

Best regards,
i Made Purna Ananda
CEO, MAHA LAKSHMI Digital Holdings
"""
    },
    'bali_digital': {
        'subject': 'Digital Marketing Partnership - Bali Digital Agency',
        'body': """
Halo {name},

Dari **Bali Digital Agency** 📢

Kami bantu bisnis Anda lebih dikenal secara online!

SERVICES:
✅ Social Media Management - Rp 3.000.000/bulan
✅ SEO Optimization - Rp 5.000.000
✅ Google Ads Management - Rp 2.000.000/bulan
✅ Content Creation - Rp 2.500.000/bulan

BENEFITS:
✅ Monthly report & analytics
✅ Dedicated account manager
✅ ROI guaranteed
✅ 50+ happy clients

FREE AUDIT:
Dapat gratis SEO audit untuk website Anda!

Mau diskusi?
WhatsApp: wa.me/6281337558787

Best regards,
i Made Purna Ananda
CEO, MAHA LAKSHMI Digital Holdings
"""
    },
    'followup': {
        'subject': 'Follow-up: Partnership Opportunity - Bali Travel',
        'body': """
Halo {name}!

Following up dari pesan kami sebelumnya.

Apakah Anda sudah mempertimbangkan partnership dengan kami?

15% commission, zero risk!
No upfront costs.

Kami sudah partner dengan:
• Four Seasons Resort Bali
• AYANA Resort
• 50+ hotels & villas

Pertanyaan apapun, silakan hubungi:
WhatsApp: wa.me/6281337558787

Best regards,
i Made Purna Ananda
MAHA LAKSHMI Digital Holdings
"""
    }
}

def get_category_template(category):
    """Get template based on lead category"""
    if 'travel' in category or 'hotel' in category:
        return 'bali_travel'
    elif 'tech' in category or 'restaurant' in category:
        return 'gianyar_tech'
    elif 'digital' in category or 'marketing' in category:
        return 'bali_digital'
    return 'bali_travel'

def load_leads():
    """Load leads from database"""
    with open('archives/LEADS-DATABASE.json', 'r') as f:
        return json.load(f)

def save_leads(leads_data):
    """Save updated leads database"""
    with open('archives/LEADS-DATABASE.json', 'w') as f:
        json.dump(leads_data, f, indent=2)

def send_email(to_email, subject, body, dry_run=True):
    """Send email via SMTP"""
    if dry_run:
        print(f"   [DRY RUN] Would send to: {to_email}")
        print(f"   Subject: {subject}")
        print(f"   Body preview: {body[:100]}...")
        return True
    
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{SMTP_CONFIG['from_name']} <{SMTP_CONFIG['from_email']}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        with smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port']) as server:
            server.starttls()
            server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def run_outreach(dry_run=True):
    """Main outreach execution"""
    print("🤖 MAHA LAKSHMI Email Outreach System")
    print("=" * 50)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print()
    
    # Load leads
    leads_data = load_leads()
    leads = leads_data['leads']
    
    print(f"📊 Total Leads: {len(leads)}")
    print()
    
    results = {
        'sent': 0,
        'failed': 0,
        'skipped': 0
    }
    
    for lead in leads:
        name = lead.get('name', 'Unknown')
        email = lead.get('email', '')
        company = lead.get('company', '')
        category = lead.get('category', 'bali_travel')
        status = lead.get('status', 'new')
        
        print(f"📧 Lead: {name}")
        print(f"   Company: {company}")
        print(f"   Category: {category}")
        
        if not email or '@' not in email:
            print("   ⚠️ No valid email, skipping")
            results['skipped'] += 1
            continue
        
        # Get template
        template_key = get_category_template(category)
        template = EMAIL_TEMPLATES[template_key]
        
        # Personalize
        first_name = name.split()[0] if name else 'Kak'
        subject = template['subject'].format(name=first_name, company=company)
        body = template['body'].format(name=first_name, company=company)
        
        # Send
        success = send_email(email, subject, body, dry_run)
        
        if success:
            results['sent'] += 1
            # Update lead status
            lead['status'] = 'contacted'
            lead['last_outreach'] = datetime.now().isoformat()
            lead['outreach_count'] = lead.get('outreach_count', 0) + 1
        else:
            results['failed'] += 1
        
        print()
        time.sleep(1)  # Rate limiting
    
    # Save updated leads
    if not dry_run:
        save_leads(leads_data)
    
    # Summary
    print("=" * 50)
    print("📊 OUTREACH SUMMARY")
    print("=" * 50)
    print(f"✅ Sent: {results['sent']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"⚠️ Skipped: {results['skipped']}")
    print()
    print("📝 Next follow-up: 2026-07-23")
    
    return results

if __name__ == '__main__':
    import sys
    dry_run = '--live' not in sys.argv
    run_outreach(dry_run=dry_run)
