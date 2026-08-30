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

import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

logger = logging.getLogger("maha-sales-engine.content")


class ContentEngine:
    """Generate and manage marketing content."""

    def __init__(self, config, product_manager):
        self.config = config
        self.product_manager = product_manager
        self.content_templates: Dict[str, Dict[str, Any]] = {}
        self.load_templates()

    def load_templates(self):
        """Load content templates."""
        self.content_templates = {
            "email_initial": {
                "subjects": [
                    "Quick question about {company}'s digital growth",
                    "Help {company} increase leads by 40-60%",
                    "I noticed something interesting about {company}"
                ],
                "bodies": [
                    "Hi {first_name},\n\nI noticed {company} is doing interesting work in {industry}.\n\nWe help {industry} companies like yours improve lead generation.\n\nWould you be open to a quick 15-minute call this week?\n\nBest,\nMAHA LAKSHMI"
                ]
            },
            "email_followup": {
                "subjects": [
                    "Re: Quick question about {company}",
                    "Following up on helping {company} grow"
                ],
                "bodies": [
                    "Hi {first_name},\n\nFollowing up on my previous email about helping {company} grow.\n\nWould a quick 15-minute conversation this week be useful?\n\nBest,\nMAHA LAKSHMI"
                ]
            },
            "whatsapp_initial": {
                "templates": [
                    "Hi {first_name}! I'm from MAHA LAKSHMI. We help {industry} businesses like {company} improve lead generation. Would you be interested in a free 15-minute consultation?",
                    "Halo {first_name}! Saya dari MAHA LAKSHMI. Kami membantu bisnis {industry} seperti {company} meningkatkan lead generation. Mau konsultasi gratis 15 menit?"
                ]
            },
            "linkedin_connection": {
                "templates": [
                    "Hi {first_name}, I'm from MAHA LAKSHMI - we help {industry} companies scale digitally. Would love to connect!",
                    "Hi {first_name}, I noticed {company} is doing great work in {industry}. Would you be open to connecting?"
                ]
            }
        }

    @staticmethod
    def _first_name(lead: Dict[str, Any]) -> str:
        name = str(lead.get("name", "")).strip()
        return name.split()[0] if name else "there"

    def _format_context(self, lead: Dict[str, Any]) -> Dict[str, str]:
        return {
            "company": str(lead.get("company", "your company")),
            "first_name": self._first_name(lead),
            "industry": str(lead.get("industry", "business")),
            "country": str(lead.get("country", ""))
        }

    def generate_email_content(self, template_type: str, lead: Dict[str, Any]) -> Dict[str, str]:
        """Generate personalized email content."""
        templates = self.content_templates.get(template_type, {})
        if not templates:
            return {"subject": "", "body": ""}

        context = self._format_context(lead)
        subject = random.choice(templates.get("subjects", [""])).format(**context)
        body = random.choice(templates.get("bodies", [""])).format(**context)
        return {"subject": subject, "body": body}

    def generate_whatsapp_content(self, template_type: str, lead: Dict[str, Any]) -> str:
        """Generate personalized WhatsApp message."""
        templates = self.content_templates.get(template_type, {})
        template_list = templates.get("templates", [])
        if not template_list:
            return ""
        return random.choice(template_list).format(**self._format_context(lead))

    def generate_linkedin_content(self, template_type: str, lead: Dict[str, Any]) -> str:
        """Generate personalized LinkedIn message."""
        templates = self.content_templates.get(template_type, {})
        template_list = templates.get("templates", [])
        if not template_list:
            return ""
        return random.choice(template_list).format(**self._format_context(lead))

    def generate_product_description(self, product_id: str, language: str = "en") -> str:
        """Generate product description."""
        product = self.product_manager.get_product(product_id)
        if not product:
            return ""

        descriptions = {
            "en": f"{product.name}\n\n{product.description}\n\nFeatures:\n" + "\n".join(f"- {f}" for f in product.features),
            "id": f"{product.name}\n\n{product.description}\n\nFitur:\n" + "\n".join(f"- {f}" for f in product.features),
            "pt": f"{product.name}\n\n{product.description}\n\nRecursos:\n" + "\n".join(f"- {f}" for f in product.features)
        }
        return descriptions.get(language, descriptions["en"])

    def get_seo_keywords(self, market: str, product: Optional[str] = None) -> List[str]:
        """Get SEO keywords for market and product."""
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

        all_keywords: List[str] = []
        for keywords in keywords_db.get(market, {}).values():
            all_keywords.extend(keywords)
        return list(dict.fromkeys(all_keywords))

    def generate_landing_page_content(self, product_id: str, market: str) -> Dict[str, str]:
        """Generate landing page content."""
        product = self.product_manager.get_product(product_id)
        if not product:
            return {}

        keywords = self.get_seo_keywords(market, product_id)
        primary_keyword = keywords[0] if keywords else product.name.lower()
        return {
            "title": f"{product.name} - {primary_keyword.title()} | MAHA LAKSHMI",
            "meta_description": f"Get {product.name}. {product.description[:150]}...",
            "h1": product.name,
            "h2": f"Everything you need to succeed with {primary_keyword}",
            "features": "\n".join(f"- {f}" for f in product.features),
            "price": f"${product.price_usd}",
            "cta": "Get Instant Access",
            "keywords": ", ".join(keywords[:5])
        }

    def get_content_calendar(self, days: int = 7) -> List[Dict[str, Any]]:
        """Generate content calendar safely."""
        if days < 0:
            raise ValueError("days must be >= 0")

        products = self.product_manager.get_active_products()
        if not products or days == 0:
            return []

        calendar: List[Dict[str, Any]] = []
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
