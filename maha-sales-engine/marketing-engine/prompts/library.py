#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Prompt Library
Reusable prompt templates with versioning and categories.
"""

import os
import sys
import json
import uuid
import logging
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.marketing.prompts")


@dataclass
class PromptTemplate:
    """Prompt template structure"""
    prompt_id: str
    name: str
    category: str
    version: str
    content: str
    variables: List[str]
    description: str
    tags: List[str]
    created_at: str
    updated_at: str
    author: str = "system"
    parent_id: Optional[str] = None
    is_active: bool = True
    usage_count: int = 0
    success_rate: float = 0.0


class PromptLibrary:
    """Manage prompt templates"""
    
    def __init__(self, db_manager, prompts_dir: Path):
        self.db = db_manager
        self.prompts_dir = prompts_dir
        self.prompts_dir.mkdir(exist_ok=True)
        self._cache: Dict[str, PromptTemplate] = {}
    
    def create_prompt(self, name: str, category: str, content: str, 
                      variables: List[str] = None, description: str = "",
                      tags: List[str] = None) -> Optional[str]:
        """Create new prompt template"""
        try:
            prompt_id = f"prpt-{uuid.uuid4().hex[:12]}"
            now = datetime.now().isoformat()
            
            prompt = PromptTemplate(
                prompt_id=prompt_id,
                name=name,
                category=category,
                version="1.0.0",
                content=content,
                variables=variables or [],
                description=description,
                tags=tags or [],
                created_at=now,
                updated_at=now
            )
            
            # Save to database
            self._save_prompt(prompt)
            
            # Cache
            self._cache[prompt_id] = prompt
            
            logger.info(f"Prompt created: {prompt_id} - {name}")
            return prompt_id
            
        except Exception as e:
            logger.error(f"Failed to create prompt: {e}")
            return None
    
    def get_prompt(self, prompt_id: str) -> Optional[PromptTemplate]:
        """Get prompt by ID"""
        if prompt_id in self._cache:
            return self._cache[prompt_id]
        
        prompt = self._load_prompt(prompt_id)
        if prompt:
            self._cache[prompt_id] = prompt
        return prompt
    
    def list_prompts(self, category: Optional[str] = None, tags: Optional[List[str]] = None) -> List[PromptTemplate]:
        """List prompts with optional filters"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM prompt_library WHERE is_active = 1"
            params = []
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            prompts = []
            for row in rows:
                prompt = PromptTemplate(
                    prompt_id=row["prompt_id"],
                    name=row["name"],
                    category=row["category"],
                    version=row["version"],
                    content=row["content"],
                    variables=json.loads(row.get("variables", "[]")),
                    description=row.get("description", ""),
                    tags=json.loads(row.get("tags", "[]")),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    author=row.get("author", "system"),
                    parent_id=row.get("parent_id"),
                    is_active=bool(row.get("is_active", 1)),
                    usage_count=row.get("usage_count", 0),
                    success_rate=row.get("success_rate", 0.0)
                )
                prompts.append(prompt)
            
            return prompts
        except Exception as e:
            logger.error(f"Failed to list prompts: {e}")
            return []
    
    def get_prompt_content(self, prompt_id: str, variables: Dict[str, str] = None) -> Optional[str]:
        """Get prompt content with variables substituted"""
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            return None
        
        content = prompt.content
        if variables:
            for key, value in variables.items():
                content = content.replace(f"{{{key}}}", str(value))
        
        return content
    
    def _save_prompt(self, prompt: PromptTemplate):
        """Save prompt to database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO prompt_library 
                (prompt_id, name, category, version, content, variables, description, tags,
                 created_at, updated_at, author, parent_id, is_active, usage_count, success_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prompt.prompt_id,
                prompt.name,
                prompt.category,
                prompt.version,
                prompt.content,
                json.dumps(prompt.variables),
                prompt.description,
                json.dumps(prompt.tags),
                prompt.created_at,
                prompt.updated_at,
                prompt.author,
                prompt.parent_id,
                prompt.is_active,
                prompt.usage_count,
                prompt.success_rate
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save prompt: {e}")
    
    def _load_prompt(self, prompt_id: str) -> Optional[PromptTemplate]:
        """Load prompt from database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prompt_library WHERE prompt_id = ?", (prompt_id,))
            row = cursor.fetchone()
            
            if row:
                return PromptTemplate(
                    prompt_id=row["prompt_id"],
                    name=row["name"],
                    category=row["category"],
                    version=row["version"],
                    content=row["content"],
                    variables=json.loads(row.get("variables", "[]")),
                    description=row.get("description", ""),
                    tags=json.loads(row.get("tags", "[]")),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    author=row.get("author", "system"),
                    parent_id=row.get("parent_id"),
                    is_active=bool(row.get("is_active", 1)),
                    usage_count=row.get("usage_count", 0),
                    success_rate=row.get("success_rate", 0.0)
                )
            return None
        except Exception as e:
            logger.error(f"Failed to load prompt: {e}")
            return None


class PromptTemplateFactory:
    """Factory for creating common prompt templates"""
    
    @staticmethod
    def create_seo_title_prompt() -> str:
        return """Generate an SEO-optimized title for the following product.

Product: {product_title}
Description: {product_description}
Keywords: {keywords}
Target Audience: {target_audience}

Requirements:
- Maximum 60 characters
- Include primary keyword
- Compelling and click-worthy
- No clickbait

Generate 3 variations:"""
    
    @staticmethod
    def create_product_description_prompt() -> str:
        return """Write a compelling product description for:

Product: {product_title}
Category: {category}
Features: {features}
Benefits: {benefits}
Target Audience: {target_audience}
Tone: {tone}

Requirements:
- 150-300 words
- Focus on benefits, not features
- Include social proof elements
- Strong call-to-action
- Easy to scan with bullet points

Description:"""
    
    @staticmethod
    def create_seo_meta_prompt() -> str:
        return """Generate SEO metadata for:

Product: {product_title}
Description: {product_description}
Keywords: {keywords}

Generate:
1. Meta Title (50-60 chars)
2. Meta Description (150-160 chars)
3. URL Slug (kebab-case)
4. OpenGraph Title
5. OpenGraph Description
6. Twitter Card Description
7. Schema.org JSON-LD

Format as JSON:"""
    
    @staticmethod
    def create_social_media_prompt() -> str:
        return """Create social media posts for:

Product: {product_title}
Description: {product_description}
Platform: {platform}
Tone: {tone}
Hashtags: {hashtags}

Create 3 variations for {platform}:"""
    
    @staticmethod
    def create_email_campaign_prompt() -> str:
        return """Write an email campaign for:

Product: {product_title}
Offer: {offer}
Deadline: {deadline}
Target Audience: {target_audience}

Create:
1. Subject line (3 variations)
2. Preview text
3. Email body (HTML format)
4. Call-to-action button text

Email:"""
    
    @staticmethod
    def create_landing_page_prompt() -> str:
        return """Write a landing page for:

Product: {product_title}
Features: {features}
Benefits: {benefits}
Price: {price}
CTA: {cta}

Create:
1. Hero headline
2. Hero subheadline
3. Feature sections (3-5)
4. Benefits section
5. Social proof section
6. FAQ section (5 questions)
7. Final CTA section

Landing Page:"""
    
    @staticmethod
    def create_faq_prompt() -> str:
        return """Generate Frequently Asked Questions for:

Product: {product_title}
Description: {product_description}
Features: {features}

Generate 8-10 questions with detailed answers covering:
- Product functionality
- Pricing and payments
- Support and updates
- Compatibility
- Usage scenarios

Format as JSON array:"""
    
    @staticmethod
    def create_competitor_analysis_prompt() -> str:
        return """Analyze competitors for:

Product: {product_title}
Category: {category}
Target Market: {target_market}

Provide:
1. Top 5 competitors
2. Their pricing strategies
3. Their strengths and weaknesses
4. Market gaps we can exploit
5. Our unique advantages

Analysis:"""


def main():
    """Test prompt library"""
    print("Prompt Library initialized")
    factory = PromptTemplateFactory()
    print(f"Available templates: {len([m for m in dir(factory) if not m.startswith('_')])}")


if __name__ == "__main__":
    main()
