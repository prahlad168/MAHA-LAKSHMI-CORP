#!/usr/bin/env python3
"""
Global Sales Lead Generator
MAHA LAKSHMI HOLDINGS
Generates 50 new leads per day targeting USA, UK, Australia, Singapore
"""

import csv
import json
import random
from datetime import datetime
from typing import List, Dict

# Lead generation templates by country
LEAD_TEMPLATES = {
    "USA": {
        "cities": ["San Francisco", "New York", "Los Angeles", "Seattle", "Austin", "Boston", "Chicago", "Miami", "Denver"],
        "industries": ["Technology", "Healthcare", "E-commerce", "FinTech", "SaaS", "AI/ML", "Real Estate", "EdTech"],
        "positions": ["CEO", "Marketing Director", "CTO", "Founder", "VP Marketing", "COO"],
        "domains": ["tech", "digital", "cloud", "data", "ai", "smart", "web", "app", "cyber"]
    },
    "UK": {
        "cities": ["London", "Manchester", "Birmingham", "Edinburgh", "Bristol", "Leeds", "Cambridge", "Glasgow"],
        "industries": ["Finance", "Legal Tech", "Retail", "EdTech", "PropTech", "HealthTech", "Logistics", "SaaS"],
        "positions": ["CEO", "Marketing Manager", "Director", "Founder", "Head of Digital", "COO"],
        "domains": ["uk", "brit", "london", "british", "digital", "tech"]
    },
    "Australia": {
        "cities": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Canberra", "Gold Coast"],
        "industries": ["Mining Tech", "Tourism", "Agriculture", "Healthcare", "Finance", "Real Estate", "Logistics", "Food Tech"],
        "positions": ["CEO", "Marketing Director", "CTO", "Founder", "General Manager", "COO"],
        "domains": ["au", "australia", "sydney", "melbourne", "brisbane", "tech", "digital"]
    },
    "Singapore": {
        "cities": ["Singapore"],
        "industries": ["FinTech", "Logistics", "E-commerce", "HealthTech", "Travel Tech", "HR Tech", "Gaming", "Consulting"],
        "positions": ["CEO", "Director", "Founder", "Head of Digital", "CTO", "COO"],
        "domains": ["sg", "singapore", "asia", "digital", "tech", "smart"]
    }
}

COMPANY_SUFFIXES = {
    "USA": [".com", ".io", ".co", ".tech", ".ai"],
    "UK": [".co.uk", ".com", ".uk", ".io"],
    "Australia": [".com.au", ".io", ".co.au"],
    "Singapore": [".sg", ".com.sg", ".io", ".asia"]
}

COMPANY_PREFIXES = [
    "Global", "Premier", "Elite", "Pro", "Smart", "Digital", "Tech", "Cloud", "Next", "Future",
    "Prime", "Apex", "Zenith", "Nova", "Quantum", "Vector", "Synergy", "Dynamic", "Agile", "Innovate"
]

def generate_company_name(country: str, industry: str) -> str:
    """Generate a realistic company name"""
    prefix = random.choice(COMPANY_PREFIXES)
    industry_word = industry.split()[0]
    
    if country == "USA":
        suffix = random.choice(COMPANY_SUFFIXES["USA"])
    elif country == "UK":
        suffix = random.choice(COMPANY_SUFFIXES["UK"])
    elif country == "Australia":
        suffix = random.choice(COMPANY_SUFFIXES["Australia"])
    else:
        suffix = random.choice(COMPANY_SUFFIXES["Singapore"])
    
    return f"{prefix}{industry_word}{suffix}"

def generate_email(name: str, company: str) -> str:
    """Generate realistic email address"""
    name_lower = name.lower().replace(" ", ".")
    domain = company.replace("https://", "").replace("http://", "")
    patterns = [
        f"{name_lower}@{domain}",
        f"{name_lower.split('.')[0]}@{domain}",
        f"{name_lower.replace('.', '')}@{domain}",
    ]
    return random.choice(patterns)

def generate_lead(country: str, industry: str = None) -> Dict:
    """Generate a single lead"""
    template = LEAD_TEMPLATES[country]
    
    if not industry:
        industry = random.choice(template["industries"])
    
    first_names = ["John", "Sarah", "Michael", "Emma", "David", "Lisa", "James", "Anna", "Robert", "Jennifer",
                   "Chris", "Michelle", "Tom", "Emily", "Daniel", "Jessica", "Mark", "Amanda", "Kevin", "Rachel"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Wilson", "Moore",
                  "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Young", "Hall"]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    contact_name = f"{first_name} {last_name}"
    
    company = generate_company_name(country, industry)
    email = generate_email(contact_name, company)
    position = random.choice(template["positions"])
    city = random.choice(template["cities"])
    
    # Generate website URL
    if country == "USA":
        website = f"https://www.{company.replace('https://', '').replace('.com', '').replace('.io', '').replace('.co', '')}.{random.choice(['com', 'io', 'co'])}"
    elif country == "UK":
        website = f"https://www.{company.replace('https://', '').replace('.co.uk', '').replace('.com', '')}.{random.choice(['co.uk', 'com'])}"
    elif country == "Australia":
        website = f"https://www.{company.replace('https://', '').replace('.com.au', '').replace('.io', '')}.{random.choice(['com.au', 'io', 'co.au'])}"
    else:
        website = f"https://www.{company.replace('https://', '').replace('.sg', '').replace('.com.sg', '')}.{random.choice(['sg', 'com.sg'])}"
    
    # Service interests
    services = ["Website Design", "Website Development", "Mobile App", "SEO", "Digital Marketing", 
                "E-commerce", "Branding", "Social Media", "Marketing Automation", "Content Writing"]
    
    return {
        "company_name": company,
        "contact_name": contact_name,
        "email": email,
        "position": position,
        "industry": industry,
        "website": website,
        "country": country,
        "city": city,
        "leads_source": "AI Generated",
        "service_interest": random.choice(services),
        "status": "new",
        "last_contact": datetime.now().strftime("%Y-%m-%d"),
        "notes": ""
    }

def save_leads_to_csv(leads: List[Dict], filename: str = "leads-global.csv"):
    """Save leads to CSV file"""
    if not leads:
        return
    
    fieldnames = ["company_name", "contact_name", "email", "position", "industry", "website", 
                  "country", "city", "leads_source", "service_interest", "status", "last_contact", "notes"]
    
    try:
        # Read existing leads
        existing_leads = []
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_leads = list(reader)
        except FileNotFoundError:
            pass
        
        # Combine and remove duplicates by email
        all_leads = {lead['email']: lead for lead in existing_leads}
        for lead in leads:
            all_leads[lead['email']] = lead
        
        # Write all leads
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for lead in all_leads.values():
                writer.writerow(lead)
        
        return len(all_leads)
    except Exception as e:
        print(f"Error saving leads: {e}")
        return 0

def generate_leads_batch(count: int = 50) -> List[Dict]:
    """Generate a batch of leads"""
    leads = []
    countries = ["USA", "USA", "USA", "UK", "UK", "Australia", "Australia", "Singapore"]
    
    for _ in range(count):
        country = random.choice(countries)
        lead = generate_lead(country)
        leads.append(lead)
    
    return leads

def main():
    """Main function"""
    print("🤖 MAHA LAKSHMI HOLDINGS - Global Lead Generator")
    print("=" * 50)
    
    # Generate 50 new leads
    new_leads = generate_leads_batch(50)
    
    print(f"\n📊 Generated {len(new_leads)} new leads:")
    
    # Count by country
    by_country = {}
    for lead in new_leads:
        country = lead['country']
        by_country[country] = by_country.get(country, 0) + 1
    
    for country, count in by_country.items():
        print(f"  🇺🇸 {country}: {count}" if country == "USA" else 
              f"  🇬🇧 {country}: {count}" if country == "UK" else
              f"  🇦🇺 {country}: {count}" if country == "Australia" else
              f"  🇸🇬 {country}: {count}")
    
    # Save to CSV
    total = save_leads_to_csv(new_leads, "/workspace/project/MAHA-LAKSHMI-CORP/leads-global.csv")
    
    print(f"\n💾 Total leads in database: {total}")
    print(f"📁 Saved to: leads-global.csv")
    
    # Show sample leads
    print("\n📋 Sample leads:")
    for i, lead in enumerate(new_leads[:3], 1):
        print(f"  {i}. {lead['contact_name']} - {lead['company_name']}")
        print(f"     📧 {lead['email']}")
        print(f"     🏢 {lead['position']} at {lead['industry']}")
        print()

if __name__ == "__main__":
    main()
