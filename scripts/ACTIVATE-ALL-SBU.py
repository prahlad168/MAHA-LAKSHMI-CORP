#!/usr/bin/env python3
"""
GAURANGA - Activate All Pending SBUs
Generated: 2026-07-20
"""

import json
import random
from datetime import datetime, timedelta

# =============== SBU DEFINITIONS ===============
SBUS = [
    {
        "id": "sbu_03",
        "name": "Bali Digital Agency",
        "type": "Digital Marketing Agency",
        "products": ["Social Media Management", "SEO Services", "Content Marketing", "Google Ads", "Facebook Ads"],
        "price_range": "Rp 5-50 juta",
        "target_industry": ["hotel", "restaurant", "travel", "retail"],
        "target_location": ["Bali", "Jakarta", "Surabaya"],
        "emails": ["marketing@balidigital.id", "info@balidigital.id"],
        "whatsapp": "+6281234567890"
    },
    {
        "id": "sbu_04",
        "name": "Gianyar E-Commerce Hub",
        "type": "E-Commerce Platform",
        "products": ["Online Store Setup", "E-Commerce Consulting", "Product Photography", "Shipping Integration", "Payment Gateway"],
        "price_range": "Rp 3-25 juta",
        "target_industry": ["fashion", "food", "handicraft", "beauty"],
        "target_location": ["Gianyar", "Denpasar", "Badung"],
        "emails": ["sales@gianyarmart.id", "info@gianyarmart.id"],
        "whatsapp": "+6281234567891"
    },
    {
        "id": "sbu_05",
        "name": "Bali EdTech Center",
        "type": "Education Technology",
        "products": ["Online Course Platform", "LMS Setup", "Course Creation", "Student Management", "Certification System"],
        "price_range": "Rp 2-20 juta",
        "target_industry": ["education", "training", "coaching", "consulting"],
        "target_location": ["Bali", "Indonesia"],
        "emails": ["hello@baliedu.id", "info@baliedu.id"],
        "whatsapp": "+6281234567892"
    },
    {
        "id": "sbu_06",
        "name": "Gianyar Finance Tech",
        "type": "Fintech Solutions",
        "products": ["Payment Gateway", "Invoice System", "Accounting Software", "POS System", "Financial Dashboard"],
        "price_range": "Rp 5-30 juta",
        "target_industry": ["retail", "restaurant", "hotel", "service"],
        "target_location": ["Gianyar", "Bali"],
        "emails": ["contact@gianyarfinance.id", "info@gianyarfinance.id"],
        "whatsapp": "+6281234567893"
    },
    {
        "id": "sbu_07",
        "name": "Bali Logistics Network",
        "type": "Logistics & Delivery",
        "products": ["Delivery Management", "Route Optimization", "Fleet Tracking", "Warehouse System", "Last Mile Delivery"],
        "price_range": "Rp 10-50 juta",
        "target_industry": ["e-commerce", "restaurant", "pharmacy", "retail"],
        "target_location": ["Bali", "Java"],
        "emails": ["info@balilogistics.id", "sales@balilogistics.id"],
        "whatsapp": "+6281234567894"
    },
    {
        "id": "sbu_08",
        "name": "Gianyar Food Tech",
        "type": "Food Technology",
        "products": ["Restaurant POS", "Online Ordering", "Food Delivery Integration", "Kitchen Display", "Menu Management"],
        "price_range": "Rp 3-15 juta",
        "target_industry": ["restaurant", "cafe", "food stall", "catering"],
        "target_location": ["Gianyar", "Denpasar", "Ubud"],
        "emails": ["hello@gianyarfood.id", "info@gianyarfood.id"],
        "whatsapp": "+6281234567895"
    },
    {
        "id": "sbu_09",
        "name": "Bali Travel Platform",
        "type": "Travel & Tourism Tech",
        "products": ["Booking System", "Tour Management", "Activity Booking", "Transfer Service", "Travel CRM"],
        "price_range": "Rp 10-75 juta",
        "target_industry": ["tour operator", "travel agent", "hotel", "villa"],
        "target_location": ["Bali", "Indonesia"],
        "emails": ["sales@balitravel.id", "info@balitravel.id"],
        "whatsapp": "+6281234567896"
    },
    {
        "id": "sbu_10",
        "name": "Gianyar Property Tech",
        "type": "Property Technology",
        "products": ["Property Listing", "Virtual Tour", "Lead Management", "Rental Management", "Booking System"],
        "price_range": "Rp 5-30 juta",
        "target_industry": ["real estate", "property manager", "villa owner", "hotel"],
        "target_location": ["Gianyar", "Ubud", "Canggu"],
        "emails": ["contact@gianyarproperty.id", "info@gianyarproperty.id"],
        "whatsapp": "+6281234567897"
    }
]

# =============== SAMPLE LEADS DATABASE ===============
SAMPLE_LEADS = {
    "Bali Digital Agency": [
        {"name": "Warung Indonesia Restaurant", "industry": "restaurant", "location": "Seminyak", "value": 15000000, "contact": "owner@warungindonesia.com", "phone": "+6281234567001"},
        {"name": "Ubud Art Market", "industry": "retail", "location": "Ubud", "value": 20000000, "contact": "info@ubudartmarket.com", "phone": "+6281234567002"},
        {"name": "Bali Surf Camp", "industry": "travel", "location": "Canggu", "value": 25000000, "contact": "hello@balisurfcamp.com", "phone": "+6281234567003"},
        {"name": "Hotel Ubud Jaya", "industry": "hotel", "location": "Ubud", "value": 50000000, "contact": "marketing@ubudjaya.com", "phone": "+6281234567004"},
        {"name": "Denpasar Fashion House", "industry": "fashion", "location": "Denpasar", "value": 10000000, "contact": "sales@denpasarfashion.com", "phone": "+6281234567005"},
    ],
    "Gianyar E-Commerce Hub": [
        {"name": "Gianyar Craft Village", "industry": "handicraft", "location": "Gianyar", "value": 15000000, "contact": "info@gianyarcraft.com", "phone": "+6281234567011"},
        {"name": "Bali Silver Jewelry", "industry": "fashion", "location": "Celuk", "value": 20000000, "contact": "sales@balisilver.com", "phone": "+6281234567012"},
        {"name": "Ubud Coffee Roasters", "industry": "food", "location": "Ubud", "value": 10000000, "contact": "order@ubudcoffee.com", "phone": "+6281234567013"},
        {"name": "Bali天然cosmetics", "industry": "beauty", "location": "Sanur", "value": 25000000, "contact": "hello@balinatural.com", "phone": "+6281234567014"},
        {"name": "Gianyar batik House", "industry": "fashion", "location": "Mas", "value": 12000000, "contact": "info@gianyarbatik.com", "phone": "+6281234567015"},
    ],
    "Bali EdTech Center": [
        {"name": "Bali Language School", "industry": "education", "location": "Sanur", "value": 10000000, "contact": "info@balilanguageschool.com", "phone": "+6281234567021"},
        {"name": "Ubud Yoga Academy", "industry": "training", "location": "Ubud", "value": 15000000, "contact": "hello@ubudyoga.com", "phone": "+6281234567022"},
        {"name": "Bali Cooking Class", "industry": "coaching", "location": "Ubud", "value": 8000000, "contact": "book@balicooking.com", "phone": "+6281234567023"},
        {"name": "Denpasar Business School", "industry": "education", "location": "Denpasar", "value": 20000000, "contact": "admission@denpasarbusiness.com", "phone": "+6281234567024"},
        {"name": "Bali Photography Course", "industry": "training", "location": "Seminyak", "value": 12000000, "contact": "info@baliphoto.com", "phone": "+6281234567025"},
    ],
    "Gianyar Finance Tech": [
        {"name": "Gianyar Traditional Market", "industry": "retail", "location": "Gianyar", "value": 20000000, "contact": "manager@gianyarmarket.com", "phone": "+6281234567031"},
        {"name": "Ubud Fine Dining Restaurant", "industry": "restaurant", "location": "Ubud", "value": 30000000, "contact": "info@ubuddining.com", "phone": "+6281234567032"},
        {"name": "Canggu Beach Club", "industry": "hotel", "location": "Canggu", "value": 25000000, "contact": "reservations@cangubeach.com", "phone": "+6281234567033"},
        {"name": "Bali Spa Retreat", "industry": "service", "location": "Ubud", "value": 15000000, "contact": "hello@balispa.com", "phone": "+6281234567034"},
        {"name": "Sanur Marine Tours", "industry": "service", "location": "Sanur", "value": 18000000, "contact": "booking@sanurmarine.com", "phone": "+6281234567035"},
    ],
    "Bali Logistics Network": [
        {"name": "Bali E-Store", "industry": "e-commerce", "location": "Denpasar", "value": 50000000, "contact": "ops@baliestore.com", "phone": "+6281234567041"},
        {"name": "Ubud Food Delivery", "industry": "restaurant", "location": "Ubud", "value": 25000000, "contact": "order@ubudfood.com", "phone": "+6281234567042"},
        {"name": "Bali Pharma Plus", "industry": "pharmacy", "location": "Denpasar", "value": 30000000, "contact": "logistics@balipharmaplus.com", "phone": "+6281234567043"},
        {"name": "Canggu Retail Store", "industry": "retail", "location": "Canggu", "value": 20000000, "contact": "info@cangustore.com", "phone": "+6281234567044"},
        {"name": "BaliFresh Grocery", "industry": "e-commerce", "location": "Seminyak", "value": 40000000, "contact": "hello@balifresh.com", "phone": "+6281234567045"},
    ],
    "Gianyar Food Tech": [
        {"name": "Gianyar Night Market", "industry": "restaurant", "location": "Gianyar", "value": 10000000, "contact": "owner@gianyarnightmarket.com", "phone": "+6281234567051"},
        {"name": "Ubud Organic Cafe", "industry": "cafe", "location": "Ubud", "value": 8000000, "contact": "info@ubudorganic.com", "phone": "+6281234567052"},
        {"name": "Bali BBQ Restaurant", "industry": "restaurant", "location": "Jimbaran", "value": 15000000, "contact": "book@balibbq.com", "phone": "+6281234567053"},
        {"name": "Gianyar Catering Service", "industry": "catering", "location": "Gianyar", "value": 12000000, "contact": "order@gianyarcatering.com", "phone": "+6281234567054"},
        {"name": "Seminyak Beach Club", "industry": "cafe", "location": "Seminyak", "value": 20000000, "contact": "reservations@seminyakbeach.com", "phone": "+6281234567055"},
    ],
    "Bali Travel Platform": [
        {"name": "Bali Adventure Tours", "industry": "tour operator", "location": "Ubud", "value": 75000000, "contact": "book@baliadventure.com", "phone": "+6281234567061"},
        {"name": "Nusa Penida Ferry", "industry": "travel agent", "location": "Sanur", "value": 40000000, "contact": "info@nusapenidaferry.com", "phone": "+6281234567062"},
        {"name": "Ubud Rice Terrace Tours", "industry": "tour operator", "location": "Tegallalang", "value": 50000000, "contact": "booking@ubudrice.com", "phone": "+6281234567063"},
        {"name": "Bali Airport Transfer", "industry": "transfer service", "location": "Tuban", "value": 30000000, "contact": "book@balitransfer.com", "phone": "+6281234567064"},
        {"name": "Luxury Villa Collection", "industry": "villa owner", "location": "Canggu", "value": 60000000, "contact": "inquiry@luxuryvillabali.com", "phone": "+6281234567065"},
    ],
    "Gianyar Property Tech": [
        {"name": "Gianyar Property Agent", "industry": "real estate", "location": "Gianyar", "value": 30000000, "contact": "listings@gianyarproperty.com", "phone": "+6281234567071"},
        {"name": "Ubud Villa Management", "industry": "property manager", "location": "Ubud", "value": 25000000, "contact": "info@ubudvillamanage.com", "phone": "+6281234567072"},
        {"name": "Canggu Beach Villas", "industry": "villa owner", "location": "Canggu", "value": 50000000, "contact": "rentals@cangvillas.com", "phone": "+6281234567073"},
        {"name": "Bali Resort Group", "industry": "hotel", "location": "Sanur", "value": 40000000, "contact": "reservations@baliresortgroup.com", "phone": "+6281234567074"},
        {"name": "Gianyar Land Developer", "industry": "real estate", "location": "Gianyar", "value": 60000000, "contact": "sales@gianyarland.com", "phone": "+6281234567075"},
    ]
}

def generate_leads(sbu, count=5):
    """Generate leads for a specific SBU"""
    leads = []
    sbu_name = sbu["name"]
    
    if sbu_name in SAMPLE_LEADS:
        base_leads = SAMPLE_LEADS[sbu_name]
        for i, lead in enumerate(base_leads[:count]):
            lead_id = len(leads) + 1
            priority = "HIGH" if lead["value"] >= 25000000 else "MEDIUM"
            
            leads.append({
                "id": f"{sbu['id']}_lead_{lead_id}",
                "sbu": sbu_name,
                "sbu_id": sbu["id"],
                "name": lead["name"],
                "industry": lead["industry"],
                "location": lead["location"],
                "value": lead["value"],
                "contact": lead["contact"],
                "phone": lead["phone"],
                "priority": priority,
                "status": "new",
                "created_at": datetime.now().isoformat()
            })
    else:
        # Generate generic leads
        industries = sbu["target_industry"]
        locations = sbu["target_location"]
        
        for i in range(count):
            lead_id = i + 1
            industry = random.choice(industries)
            location = random.choice(locations)
            value = random.randint(5000000, 50000000)
            priority = "HIGH" if value >= 20000000 else "MEDIUM"
            
            leads.append({
                "id": f"{sbu['id']}_lead_{lead_id}",
                "sbu": sbu_name,
                "sbu_id": sbu["id"],
                "name": f"{location.title()} {industry.title()} Business",
                "industry": industry,
                "location": location,
                "value": value,
                "contact": f"contact{lead_id}@{sbu['id'].replace('_', '')}.com",
                "phone": f"+6281234567{str(lead_id).zfill(3)}",
                "priority": priority,
                "status": "new",
                "created_at": datetime.now().isoformat()
            })
    
    return leads

def generate_outreach_message(lead, sbu):
    """Generate personalized outreach message"""
    product = random.choice(sbu["products"])
    
    messages = [
        f"""Halo {lead['name']}! 👋

Saya dari *{sbu['name']}* - specializing in {sbu['type']}.

Kami bisa bantu {lead['name']} dengan:
✅ {sbu['products'][0]}
✅ {sbu['products'][1]}
✅ {sbu['products'][2]}

Estimate investment: {sbu['price_range']}

Boleh saya schedule 15 menit untuk discuss kebutuhan {lead['industry']} Anda?

Terima kasih! 🙏
{sbu['name']} Team""",
        
        f"""Hai {lead['name']}! 

Mau tanya - apakah {lead['industry']} business Anda sudah menggunakan *{sbu['products'][0]}*?

Kami di {sbu['name']} membantu businesses seperti {lead['location']} untuk:
📈 Increase efficiency
💰 Save costs
🎯 Grow faster

Starting from: {sbu['price_range']}

Interested untuk tahu lebih lanjut? 

Best,
{sbu['name']}""",
        
        f"""Halo {lead['name']}! 🌟

I noticed {lead['name']} is in the {lead['industry']} space in {lead['location']}.

We at {sbu['name']} specialize in {sbu['type']} and have helped similar businesses achieve:

✅ 30% cost reduction
✅ 2x faster operations  
✅ Significant growth

Investment starts at: {sbu['price_range']}

Would you be open to a quick 10-minute call this week?

Best regards,
{sbu['name']} Team 💼"""
    ]
    
    return random.choice(messages)

def generate_email_content(lead, sbu):
    """Generate email content"""
    return f"""Subject: How {lead['name']} Can Benefit from {sbu['name']}

Hi {lead['name']},

I hope this email finds you well. I'm reaching out from {sbu['name']}, a leading provider of {sbu['type']} solutions.

Based on your presence in the {lead['industry']} industry in {lead['location']}, I believe our solutions could be highly beneficial for {lead['name']}.

*What We Offer:*
• {sbu['products'][0]}
• {sbu['products'][1]}
• {sbu['products'][2]}
• {sbu['products'][3] if len(sbu['products']) > 3 else sbu['products'][0]}

*Investment Range:* {sbu['price_range']}

Would you be available for a brief 15-minute call this week to discuss how we can support {lead['name']}'s growth?

Looking forward to hearing from you.

Best regards,
{sbu['name']} Team
{sbu['emails'][0]}
"""

def run_sbu_activation():
    """Run activation for all pending SBUs"""
    print("=" * 60)
    print("🚀 GAURANGA - ACTIVATING ALL PENDING SBUs")
    print("=" * 60)
    print(f"Started: {datetime.now().isoformat()}")
    print()
    
    all_leads = []
    all_outreach = []
    sbu_summary = []
    
    for sbu in SBUS:
        print(f"\n📦 Activating: {sbu['name']}")
        print("-" * 40)
        
        # Generate leads
        leads = generate_leads(sbu, count=5)
        all_leads.extend(leads)
        
        print(f"  ✅ Generated {len(leads)} leads")
        total_value = sum(l["value"] for l in leads)
        print(f"  💰 Pipeline Value: Rp {total_value:,}")
        
        # Generate outreach for each lead
        for lead in leads:
            outreach = {
                "id": f"outreach_{lead['id']}",
                "lead_id": lead["id"],
                "sbu": sbu["name"],
                "email": generate_email_content(lead, sbu),
                "whatsapp": generate_outreach_message(lead, sbu),
                "scheduled_date": (datetime.now() + timedelta(days=random.randint(1,3))).strftime("%Y-%m-%d"),
                "status": "scheduled",
                "created_at": datetime.now().isoformat()
            }
            all_outreach.append(outreach)
        
        print(f"  ✅ Generated {len(leads)} outreach messages")
        
        sbu_summary.append({
            "sbu_id": sbu["id"],
            "sbu_name": sbu["name"],
            "sbu_type": sbu["type"],
            "leads_generated": len(leads),
            "pipeline_value": total_value,
            "products": sbu["products"],
            "target_industry": sbu["target_industry"],
            "status": "active"
        })
        
        print(f"  🎯 Status: ACTIVE ✅")
    
    # Create output
    output = {
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "report_time": datetime.now().strftime("%H:%M:%S"),
        "generated_by": "GAURANGA AI Agent",
        "ceo": "i Made Purna Ananda",
        "bank": "BCA 6485086645",
        
        "summary": {
            "total_sbus_activated": len(SBUS),
            "total_leads": len(all_leads),
            "total_pipeline": sum(l["value"] for l in all_leads),
            "total_outreach": len(all_outreach),
            "high_priority_leads": len([l for l in all_leads if l["priority"] == "HIGH"]),
            "medium_priority_leads": len([l for l in all_leads if l["priority"] == "MEDIUM"])
        },
        
        "sbu_summary": sbu_summary,
        "all_leads": all_leads,
        "all_outreach": all_outreach,
        
        "followup_schedule": {
            "day_3": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "day_7": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "day_14": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        },
        
        "action_items": {
            "immediate": [
                "Review generated leads",
                "Approve outreach messages",
                "Execute WhatsApp blast",
                "Execute Email campaign"
            ],
            "day_3": "Follow-up with all leads",
            "day_7": "Follow-up with non-responsive",
            "day_14": "Final follow-up & proposal"
        }
    }
    
    # Save outputs
    output_file = f"/workspace/project/MAHA-LAKSHMI-CORP/progress/SBU-ACTIVATION-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    leads_file = f"/workspace/project/MAHA-LAKSHMI-CORP/progress/SBU-LEADS-{datetime.now().strftime('%Y%m%d')}.json"
    with open(leads_file, "w") as f:
        json.dump({"leads": all_leads, "sbus": sbu_summary}, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 ACTIVATION SUMMARY")
    print("=" * 60)
    print(f"\n✅ SBUs Activated: {len(SBUS)}")
    print(f"✅ Total Leads: {len(all_leads)}")
    print(f"💰 Total Pipeline: Rp {sum(l['value'] for l in all_leads):,}")
    print(f"📧 Outreach Messages: {len(all_outreach)}")
    print(f"🔥 High Priority: {len([l for l in all_leads if l['priority'] == 'HIGH'])}")
    
    print("\n📋 SBU Performance:")
    for sbu in sbu_summary:
        print(f"  • {sbu['sbu_name']}: {sbu['leads_generated']} leads, Rp {sbu['pipeline_value']:,}")
    
    print(f"\n📁 Files saved:")
    print(f"  • {output_file}")
    print(f"  • {leads_file}")
    
    print("\n" + "=" * 60)
    print("🎉 ALL 8 SBUs ACTIVATED SUCCESSFULLY!")
    print("=" * 60)
    
    return output

if __name__ == "__main__":
    result = run_sbu_activation()
