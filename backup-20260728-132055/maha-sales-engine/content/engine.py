#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Content Engine
Responsibilities:
- Titles
- Descriptions
- SEO keywords
- Marketing copy
- Localization-ready content
"""

import json
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("maha-sales-engine.content")


class ContentEngine:
    """Generate and manage marketing content"""
    
    def __init__(self, config, product_manager):
        self.config = config
        self.product_manager = product_manager
        self.content_templates: Dict[str, Dict[str, Any]] = {}
        self.load_templates()
    
    def load_templates(self):
        """Load content templates"""
        self.content_templates = {
            "email_initial": {
                "subjects": [
                    "Quick question about {company}'s digital growth",
                    "Help {company} increase leads by 40-60%",
                    "I noticed something interesting about {company}"
                ],
                "bodies": [
                    "Hi {first_name},\n\nI noticed {company} is doing interesting work in {industry}.\n\nWe help {industry} companies like yours increase leads by 40-60% within 90 days.\n\nWould you be open to a quick 15-minute call this week?\n\nBest,\nAlex Johnson\nMAHA LAKSHMI HOLDINGS"
                ]
            },
            "email_followup": {
                "subjects": [
                    "Re: Quick question about {company}",
                    "Following up on helping {company} grow"
                ],
                "bodies": [
                    "Hi {first_name},\n\nFollowing up on my previous email about helping {company} grow.\n\nWe recently helped a {industry} company in {country}:\n   - 150% increase in website traffic\n   - 3x more demo requests\n\nWould a quick 15-min call this Thursday work?\n\nBest,\nAlex Johnson"
                ]
            },
            "whatsapp_initial": {
                "templates": [
                    "Hi {first_name}! I'm from MAHA LAKSHMI. We help {industry} companies like {company} increase leads by 40-60%. Would you be interested in a free 15-min consultation?",
                    "Halo {first_name}! Saya dari MAHA LAKSHMI. Kami membantu perusahaan {industry} seperti {company} meningkatkan leads 40-60%. Mau konsultasi gratis 15 menit?"
                ]
            },
            "linkedin_connection": {
                "templates": [
                    "Hi {first_name}, I'm from MAHA LAKSHMI - we help {industry} companies scale digitally. Would love to connect!",
                    "Hi {first_name}, I noticed {company} is doing great work in {industry}. Would you be open to connecting?"
                ]
            }
        }
    
    def generate_email_content(self, template_type: str, lead: Dict[str, Any]) -> Dict[str, str]:
        """Generate personalized email content"""
        templates = self.content_templates.get(template_type, {})
        
        if not templates:
            return {"subject": "", "body": ""}
        
        subject = random.choice(templates.get("subjects", [""])).format(
            company=lead.get("company", ""),
            first_name=lead.get("name", "").split()[0],
            industry=lead.get("industry", ""),
            country=lead.get("country", "")
        )
        
        body = random.choice(templates.get("bodies", [""])).format(
            company=lead.get("company", ""),
            first_name=lead.get("name", "").split()[0],
            industry=lead.get("industry", ""),
            country=lead.get("country", "")
        )
        
        return {"subject": subject, "body": body}
    
    def generate_whatsapp_content(self, template_type: str, lead: Dict[str, Any]) -> str:
        """Generate personalized WhatsApp message"""
        templates = self.content_templates.get(template_type, {})
        template_list = templates.get("templates", [])
        
        if not template_list:
            return ""
        
        return random.choice(template_list).format(
            company=lead.get("company", ""),
            first_name=lead.get("name", "").split()[0],
            industry=lead.get("industry", ""),
            country=lead.get("country", "")
        )
    
    def generate_linkedin_content(self, template_type: str, lead: Dict[str, Any]) -> str:
        """Generate personalized LinkedIn message"""
        templates = self.content_templates.get(template_type, {})
        template_list = templates.get("templates", [])
        
        if not template_list:
            return ""
        
        return random.choice(template_list).format(
            company=lead.get("company", ""),
            first_name=lead.get("name", "").split()[0],
            industry=lead.get("industry", "")
        )
    
    def generate_product_description(self, product_id: str, language: str = "en") -> str:
        """Generate product description"""
        product = self.product_manager.get_product(product_id)
        if not product:
            return ""
        
        descriptions = {
            "en": f"{product.name}\n\n{product.description}\n\nFeatures:\n" + "\n".join([f"- {f}" for f in product.features]),
            "id": f"{product.name}\n\n{product.description}\n\nFitur:\n" + "\n".join([f"- {f}" for f in product.features]),
            "pt": f"{product.name}\n\n{product.description}\n\nRecursos:\n" + "\n".join([f"- {f}" for f in product.features])
        }
        
        return descriptions.get(language, descriptions["en"])
    
    def get_seo_keywords(self, market: str, product: Optional[str] = None) -> List[str]:
        """Get SEO keywords for market and product"""
        keywords_db = {
            "id": {
                "social-media-kit": ["template Instagram bisnis", "desain sosial media", "template Instagram UMKM"],
                "seo-bundle": ["SEO template", "checklist SEO", "tools SEO Indonesia"],
                "whatsapp-marketing": ["WhatsApp marketing", "template WhatsApp bisnis", "automasi WhatsApp"]
            },
            "en": {
                "social-media-kit": ["social media kit", "social media templates", "Instagram templates"],
                "seo-bundle": ["SEO templates", "SEO checklist", "SEO tools"],
                "whatsapp-marketing": ["WhatsApp marketing", "WhatsApp templates", "WhatsApp automation"]
            },
            "pt": {
                "social-media-kit": ["kit mídias sociais", "templates Instagram", "design redes sociais"],
                "seo-bundle": ["templates SEO", "checklist SEO", "ferramentas SEO"],
                "whatsapp-marketing": ["marketing WhatsApp", "templates WhatsApp", "automação WhatsApp"]
            }
        }
        
        if product:
            return keywords_db.get(market, {}).get(product, [])
        
        # Return all keywords for market
        all_keywords = []
        for keywords in keywords_db.get(market, {}).values():
            all_keywords.extend(keywords)
        return list(set(all_keywords))
    
    def generate_landing_page_content(self, product_id: str, market: str) -> Dict[str, str]:
        """Generate landing page content"""
        product = self.product_manager.get_product(product_id)
        if not product:
            return {}
        
        keywords = self.get_seo_keywords(market, product_id)
        primary_keyword = keywords[0] if keywords else product.name.lower()
        
        content = {
            "title": f"{product.name} - {primary_keyword.title()} | MAHA LAKSHMI",
            "meta_description": f"Get {product.name}. {product.description[:150]}... Best price guaranteed.",
            "h1": f"{product.name}",
            "h2": f"Everything you need to succeed with {primary_keyword}",
            "features": "\n".join([f"- {f}" for f in product.features]),
            "price": f"${product.price_usd}",
            "cta": "Get Instant Access",
            "keywords": ", ".join(keywords[:5])
        }
        
        return content
    
    def get_content_calendar(self, days: int = 7) -> List[Dict[str, Any]]:
        """Generate content calendar"""
        calendar = []
        products = self.product_manager.get_active_products()
        
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            product = products[i % len(products)]
            
            calendar.append({
                "date": date,
                "product_id": product.id,
                "product_name": product.name,
                "content_type": random.choice(["social_post", "email", "blog", "ad"]),
                "channel": random.choice(["instagram", "email", "linkedin", "facebook"]),
                "status": "scheduled"
            })
        
        return calendar


import random


def main():
    """Test content engine"""
    from core.engine import ConfigManager, DatabaseManager
    from pathlib import Path
    from products.product_manager import ProductManager
    
    config = ConfigManager(Path("config/engine.yaml"))
    db = DatabaseManager(Path(config.get("database.path")))
    pm = ProductManager(db)
    
    ce = ContentEngine(config, pm)
    
    # Test content generation
    lead = {
        "name": "John Smith",
        "company": "TechStart",
        "industry": "Technology",
        "country": "USA"
    }
    
    email = ce.generate_email_content("email_initial", lead)
    print(f"\nEmail Subject: {email['subject']}")
    print(f"Email Body: {email['body'][:100]}...")
    
    keywords = ce.get_seo_keywords("id", "social-media-kit")
    print(f"\nSEO Keywords (ID): {keywords}")
    
    db.close()


if __name__ == "__main__":
    main()
