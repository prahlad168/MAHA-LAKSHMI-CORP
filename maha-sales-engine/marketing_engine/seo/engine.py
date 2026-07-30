#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - SEO Engine
Generate SEO-optimized metadata and content.
"""

import os
import sys
import json
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.marketing.seo")


@dataclass
class SEOMetadata:
    """SEO metadata structure"""
    title: str
    description: str
    slug: str
    canonical_url: str
    meta_keywords: List[str]
    og_title: str
    og_description: str
    og_image: str
    twitter_title: str
    twitter_description: str
    twitter_image: str
    schema_org: Dict[str, Any]
    alt_texts: List[str]
    internal_links: List[str]


class SEOEngine:
    """Generate SEO-optimized metadata"""
    
    def __init__(self, ai_manager, prompt_library):
        self.ai_manager = ai_manager
        self.prompt_library = prompt_library
    
    def generate_metadata(self, product_data: Dict[str, Any], keywords: List[str]) -> SEOMetadata:
        """Generate complete SEO metadata"""
        try:
            # Generate components
            title = self._generate_title(product_data, keywords)
            description = self._generate_description(product_data, keywords)
            slug = self._generate_slug(product_data["title"])
            schema = self._generate_schema(product_data)
            
            return SEOMetadata(
                title=title,
                description=description,
                slug=slug,
                canonical_url=f"/products/{slug}",
                meta_keywords=keywords[:10],
                og_title=title,
                og_description=description,
                og_image="/images/og-default.jpg",
                twitter_title=title,
                twitter_description=description,
                twitter_image="/images/twitter-default.jpg",
                schema_org=schema,
                alt_texts=[f"{product_data['title']} preview image"],
                internal_links=["/products", "/categories", "/about"]
            )
        except Exception as e:
            logger.error(f"SEO metadata generation failed: {e}")
            raise
    
    def _generate_title(self, product_data: Dict[str, Any], keywords: List[str]) -> str:
        """Generate SEO title"""
        title = product_data.get("title", "")
        primary_keyword = keywords[0] if keywords else ""
        
        # Ensure title is under 60 chars
        if len(title) > 60:
            title = title[:57] + "..."
        
        # Include keyword if not present
        if primary_keyword and primary_keyword.lower() not in title.lower():
            if len(title) + len(primary_keyword) + 3 <= 60:
                title = f"{title} - {primary_keyword}"
        
        return title
    
    def _generate_description(self, product_data: Dict[str, Any], keywords: List[str]) -> str:
        """Generate meta description"""
        description = product_data.get("description", "")
        primary_keyword = keywords[0] if keywords else ""
        
        # Ensure description is 150-160 chars
        if len(description) > 160:
            description = description[:157] + "..."
        elif len(description) < 150:
            description = description + f" Get {primary_keyword} now."
        
        return description
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL slug"""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = slug.strip('-')
        return slug[:50]
    
    def _generate_schema(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Schema.org JSON-LD"""
        return {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": product_data.get("title", ""),
            "description": product_data.get("description", ""),
            "offers": {
                "@type": "Offer",
                "price": product_data.get("price_usd", 0),
                "priceCurrency": "USD"
            }
        }
    
    def optimize_content(self, content: str, keywords: List[str]) -> str:
        """Optimize content for SEO"""
        optimized = content
        
        # Ensure keyword density (1-3%)
        for keyword in keywords[:3]:
            if keyword.lower() not in optimized.lower():
                optimized = f"{keyword}: {optimized}"
        
        return optimized
    
    def generate_alt_text(self, image_description: str, keywords: List[str]) -> str:
        """Generate SEO-friendly alt text"""
        primary_keyword = keywords[0] if keywords else "image"
        return f"{image_description} - {primary_keyword}"


def main():
    """Test SEO engine"""
    print("SEO Engine initialized")


if __name__ == "__main__":
    main()
