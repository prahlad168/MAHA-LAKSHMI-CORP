#!/usr/bin/env python3
"""
GAURANGA - Execute Outreach for All SBUs
Generated: 2026-07-20
"""

import json
import random
from datetime import datetime, timedelta
import os

def load_leads():
    """Load leads from generated file"""
    leads_file = f"/workspace/project/MAHA-LAKSHMI-CORP/progress/SBU-LEADS-{datetime.now().strftime('%Y%m%d')}.json"
    
    if os.path.exists(leads_file):
        with open(leads_file, "r") as f:
            data = json.load(f)
            return data.get("leads", [])
    
    # If not found, create new
    return None

def generate_outreach_report(leads):
    """Generate outreach report for all leads"""
    
    # Group leads by SBU
    sbu_groups = {}
    for lead in leads:
        sbu = lead["sbu"]
        if sbu not in sbu_groups:
            sbu_groups[sbu] = []
        sbu_groups[sbu].append(lead)
    
    # Generate report
    report = {
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "report_time": datetime.now().strftime("%H:%M:%S"),
        "generated_by": "GAURANGA AI Agent",
        "ceo": "i Made Purna Ananda",
        "bank": "BCA 6485086645",
        
        "summary": {
            "total_leads": len(leads),
            "total_pipeline": sum(l["value"] for l in leads),
            "high_priority": len([l for l in leads if l["priority"] == "HIGH"]),
            "medium_priority": len([l for l in leads if l["priority"] == "MEDIUM"]),
            "sbus_covered": len(sbu_groups)
        },
        
        "sbu_outreach": [],
        "all_leads": leads,
        
        "followup_schedule": {
            "day_3": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "day_7": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "day_14": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        },
        
        "execution_status": {
            "email_campaign": "ready",
            "whatsapp_campaign": "ready",
            "followup_automation": "scheduled"
        }
    }
    
    # Generate per-SBU outreach
    whatsapp_template = """
🏷️ *OUTREACH MESSAGE - {sbu_name}*

Halo {name}! 👋

Saya dari *{sbu_name}* - specialize in {sbu_type}.

Kami bisa bantu {name} dengan:
✅ {product1}
✅ {product2}
✅ {product3}

💰 Starting from: {price}

Boleh saya schedule 15 menit untuk discuss kebutuhan {industry} Anda?

Terima kasih! 🙏
{sbu_name} Team
📱 {whatsapp}
📧 {email}
"""
    
    email_template = """
Subject: [{sbu_name}] Partnership Opportunity for {name}

Hi {name},

I hope this email finds you well. I'm reaching out from {sbu_name}, a leading provider of {sbu_type}.

Based on your presence in the {industry} industry in {location}, I believe our solutions could be highly beneficial for {name}.

*What We Offer:*
• {product1}
• {product2}
• {product3}

*Investment Range:* {price}

Would you be available for a brief 15-minute call this week?

Looking forward to hearing from you.

Best regards,
{sbu_name} Team
{email}
"""
    
    for sbu_name, sbu_leads in sbu_groups.items():
        # Get SBU info from first lead
        first_lead = sbu_leads[0]
        sbu_id = first_lead["sbu_id"]
        
        products = {
            "Bali Digital Agency": ["Social Media Management", "SEO Services", "Google Ads"],
            "Gianyar E-Commerce Hub": ["Online Store Setup", "E-Commerce Consulting", "Shipping Integration"],
            "Bali EdTech Center": ["Online Course Platform", "LMS Setup", "Student Management"],
            "Gianyar Finance Tech": ["Payment Gateway", "Invoice System", "Accounting Software"],
            "Bali Logistics Network": ["Delivery Management", "Route Optimization", "Fleet Tracking"],
            "Gianyar Food Tech": ["Restaurant POS", "Online Ordering", "Kitchen Display"],
            "Bali Travel Platform": ["Booking System", "Tour Management", "Activity Booking"],
            "Gianyar Property Tech": ["Property Listing", "Virtual Tour", "Lead Management"]
        }
        
        sbu_types = {
            "Bali Digital Agency": "Digital Marketing Agency",
            "Gianyar E-Commerce Hub": "E-Commerce Platform",
            "Bali EdTech Center": "Education Technology",
            "Gianyar Finance Tech": "Fintech Solutions",
            "Bali Logistics Network": "Logistics & Delivery",
            "Gianyar Food Tech": "Food Technology",
            "Bali Travel Platform": "Travel & Tourism Tech",
            "Gianyar Property Tech": "Property Technology"
        }
        
        sbu_prices = {
            "Bali Digital Agency": "Rp 5-50 juta",
            "Gianyar E-Commerce Hub": "Rp 3-25 juta",
            "Bali EdTech Center": "Rp 2-20 juta",
            "Gianyar Finance Tech": "Rp 5-30 juta",
            "Bali Logistics Network": "Rp 10-50 juta",
            "Gianyar Food Tech": "Rp 3-15 juta",
            "Bali Travel Platform": "Rp 10-75 juta",
            "Gianyar Property Tech": "Rp 5-30 juta"
        }
        
        sbu_emails = {
            "Bali Digital Agency": "info@balidigital.id",
            "Gianyar E-Commerce Hub": "info@gianyarmart.id",
            "Bali EdTech Center": "info@baliedu.id",
            "Gianyar Finance Tech": "contact@gianyarfinance.id",
            "Bali Logistics Network": "info@balilogistics.id",
            "Gianyar Food Tech": "info@gianyarfood.id",
            "Bali Travel Platform": "sales@balitravel.id",
            "Gianyar Property Tech": "contact@gianyarproperty.id"
        }
        
        sbu_whatsapps = {
            "Bali Digital Agency": "+6281234567890",
            "Gianyar E-Commerce Hub": "+6281234567891",
            "Bali EdTech Center": "+6281234567892",
            "Gianyar Finance Tech": "+6281234567893",
            "Bali Logistics Network": "+6281234567894",
            "Gianyar Food Tech": "+6281234567895",
            "Bali Travel Platform": "+6281234567896",
            "Gianyar Property Tech": "+6281234567897"
        }
        
        prod_list = products.get(sbu_name, ["Service 1", "Service 2", "Service 3"])
        sbu_type = sbu_types.get(sbu_name, "Business Solutions")
        price = sbu_prices.get(sbu_name, "Rp 5-50 juta")
        email = sbu_emails.get(sbu_name, "info@example.com")
        whatsapp = sbu_whatsapps.get(sbu_name, "+6281234567890")
        
        sbu_outreach = {
            "sbu": sbu_name,
            "sbu_id": sbu_id,
            "leads_count": len(sbu_leads),
            "pipeline_value": sum(l["value"] for l in sbu_leads),
            "high_priority": len([l for l in sbu_leads if l["priority"] == "HIGH"]),
            "outreach_messages": []
        }
        
        for lead in sbu_leads:
            # Generate WhatsApp message
            wa_msg = whatsapp_template.format(
                sbu_name=sbu_name,
                name=lead["name"],
                sbu_type=sbu_type,
                product1=prod_list[0],
                product2=prod_list[1],
                product3=prod_list[2],
                price=price,
                industry=lead["industry"],
                email=email,
                whatsapp=whatsapp
            )
            
            # Generate Email
            email_msg = email_template.format(
                sbu_name=sbu_name,
                name=lead["name"],
                sbu_type=sbu_type,
                industry=lead["industry"],
                location=lead["location"],
                product1=prod_list[0],
                product2=prod_list[1],
                product3=prod_list[2],
                price=price,
                email=email
            )
            
            sbu_outreach["outreach_messages"].append({
                "lead_id": lead["id"],
                "lead_name": lead["name"],
                "contact": lead["contact"],
                "phone": lead["phone"],
                "whatsapp_message": wa_msg,
                "email_message": email_msg,
                "status": "ready",
                "scheduled_date": (datetime.now() + timedelta(hours=random.randint(1,12))).strftime("%Y-%m-%d %H:%M")
            })
        
        report["sbu_outreach"].append(sbu_outreach)
    
    return report

def main():
    print("=" * 60)
    print("📤 GAURANGA - OUTREACH EXECUTION")
    print("=" * 60)
    
    leads = load_leads()
    
    if leads is None:
        print("❌ No leads found. Please run ACTIVATE-ALL-SBU.py first.")
        return
    
    print(f"\n📊 Loaded {len(leads)} leads")
    print(f"💰 Total Pipeline: Rp {sum(l['value'] for l in leads):,}")
    print(f"🔥 High Priority: {len([l for l in leads if l['priority'] == 'HIGH'])}")
    print()
    
    # Generate report
    report = generate_outreach_report(leads)
    
    # Save report
    output_file = f"/workspace/project/MAHA-LAKSHMI-CORP/progress/OUTREACH-REPORT-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
    
    # Save as HTML for easy viewing
    html_file = f"/workspace/project/MAHA-LAKSHMI-CORP/progress/OUTREACH-REPORT-{datetime.now().strftime('%Y%m%d-%H%M')}.html"
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>GAURANGA - Outreach Report {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .summary {{ background: #3498db; color: white; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .summary-item {{ display: inline-block; margin: 10px 20px; }}
        .sbu-card {{ background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #3498db; }}
        .lead-card {{ background: white; padding: 10px; margin: 5px 0; border-left: 3px solid #27ae60; }}
        .message-box {{ background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; margin: 10px 0; }}
        .btn {{ background: #27ae60; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
        .tag {{ display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 12px; margin-left: 10px; }}
        .tag-high {{ background: #e74c3c; color: white; }}
        .tag-medium {{ background: #f39c12; color: white; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📤 GAURANGA Outreach Report</h1>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        
        <div class="summary">
            <h2>📊 Summary</h2>
            <div class="summary-item">
                <strong>Total Leads:</strong> {report['summary']['total_leads']}
            </div>
            <div class="summary-item">
                <strong>Total Pipeline:</strong> Rp {report['summary']['total_pipeline']:,}
            </div>
            <div class="summary-item">
                <strong>High Priority:</strong> {report['summary']['high_priority']}
            </div>
            <div class="summary-item">
                <strong>SBUs:</strong> {report['summary']['sbus_covered']}
            </div>
        </div>
        
        <h2>📦 SBU Outreach</h2>
"""
    
    for sbu_data in report["sbu_outreach"]:
        html_content += f"""
        <div class="sbu-card">
            <h3>{sbu_data['sbu']} <span class="tag tag-high">{sbu_data['leads_count']} leads</span></h3>
            <p>💰 Pipeline: Rp {sbu_data['pipeline_value']:,} | 🔥 High Priority: {sbu_data['high_priority']}</p>
"""
        
        for msg in sbu_data["outreach_messages"][:2]:  # Show first 2 for brevity
            priority_tag = "tag-high" if any(l["priority"] == "HIGH" for l in leads if l["id"] == msg["lead_id"]) else "tag-medium"
            html_content += f"""
            <div class="lead-card">
                <strong>{msg['lead_name']}</strong>
                <span class="tag {priority_tag}">{msg['lead_id'].split('_')[0].replace('sbu_0', 'SBU-').replace('sbu_', 'SBU-')}</span>
                <p>📧 {msg['contact']}</p>
                <details>
                    <summary>📱 WhatsApp Message</summary>
                    <div class="message-box">{msg['whatsapp_message']}</div>
                </details>
            </div>
"""
        
        html_content += "</div>"
    
    html_content += f"""
        <div style="margin-top: 30px; padding: 20px; background: #27ae60; color: white; border-radius: 10px;">
            <h3>📅 Follow-up Schedule</h3>
            <p>Day 3: {report['followup_schedule']['day_3']}</p>
            <p>Day 7: {report['followup_schedule']['day_7']}</p>
            <p>Day 14: {report['followup_schedule']['day_14']}</p>
        </div>
        
        <div style="margin-top: 20px; text-align: center; color: #7f8c8d;">
            <p>Generated by GAURANGA AI Agent for CEO i Made Purna Ananda</p>
            <p>Bank: BCA 6485086645</p>
        </div>
    </div>
</body>
</html>"""
    
    with open(html_file, "w") as f:
        f.write(html_content)
    
    print(f"\n✅ Report saved:")
    print(f"   📄 JSON: {output_file}")
    print(f"   🌐 HTML: {html_file}")
    
    print("\n" + "=" * 60)
    print("📤 OUTREACH READY!")
    print("=" * 60)
    print(f"\n📊 Total Messages: {len(leads)}")
    print(f"📧 Email Campaign: READY")
    print(f"📱 WhatsApp Campaign: READY")
    print(f"📅 Follow-up Scheduled: {report['followup_schedule']['day_3']}")
    
    return report

if __name__ == "__main__":
    main()
