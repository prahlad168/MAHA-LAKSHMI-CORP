#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Content Pipeline State Machine
Marketing content generation state management.
"""

import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger("maha-sales-engine.marketing.pipeline")


class ContentStatus(Enum):
    DRAFT = "draft"
    RESEARCHING = "researching"
    GENERATING = "generating"
    REVIEWING = "reviewing"
    OPTIMIZING = "optimizing"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"
    FAILED = "failed"


class ContentPipelineStateMachine:
    """State machine for content generation pipeline"""
    
    VALID_TRANSITIONS = {
        ContentStatus.DRAFT.value: [
            ContentStatus.RESEARCHING.value,
            ContentStatus.GENERATING.value
        ],
        ContentStatus.RESEARCHING.value: [
            ContentStatus.GENERATING.value,
            ContentStatus.DRAFT.value,
            ContentStatus.FAILED.value
        ],
        ContentStatus.GENERATING.value: [
            ContentStatus.REVIEWING.value,
            ContentStatus.FAILED.value
        ],
        ContentStatus.REVIEWING.value: [
            ContentStatus.OPTIMIZING.value,
            ContentStatus.APPROVED.value,
            ContentStatus.REJECTED.value,
            ContentStatus.DRAFT.value,
            ContentStatus.FAILED.value
        ],
        ContentStatus.OPTIMIZING.value: [
            ContentStatus.APPROVED.value,
            ContentStatus.REJECTED.value,
            ContentStatus.FAILED.value
        ],
        ContentStatus.APPROVED.value: [
            ContentStatus.ARCHIVED.value
        ],
        ContentStatus.REJECTED.value: [
            ContentStatus.DRAFT.value,
            ContentStatus.GENERATING.value
        ],
        ContentStatus.ARCHIVED.value: [],
        ContentStatus.FAILED.value: [
            ContentStatus.DRAFT.value,
            ContentStatus.GENERATING.value
        ]
    }
    
    @classmethod
    def can_transition(cls, from_status: str, to_status: str) -> bool:
        valid_targets = cls.VALID_TRANSITIONS.get(from_status, [])
        return to_status in valid_targets
    
    @classmethod
    def get_valid_transitions(cls, from_status: str) -> List[str]:
        return cls.VALID_TRANSITIONS.get(from_status, [])
    
    @classmethod
    def validate_transition(cls, from_status: str, to_status: str) -> Dict[str, Any]:
        valid = cls.can_transition(from_status, to_status)
        return {
            "valid": valid,
            "from_status": from_status,
            "to_status": to_status,
            "valid_targets": cls.get_valid_transitions(from_status),
            "error": None if valid else f"Invalid transition from {from_status} to {to_status}"
        }


class ContentPipeline:
    """Marketing content generation pipeline"""
    
    STAGES = [
        "research",
        "keyword_discovery",
        "audience_analysis",
        "competitor_analysis",
        "content_planning",
        "generation",
        "quality_review",
        "seo_optimization",
        "compliance_review"
    ]
    
    def __init__(self, db_manager, ai_manager, prompt_library, seo_engine, keyword_engine, quality_engine):
        self.db = db_manager
        self.ai_manager = ai_manager
        self.prompt_library = prompt_library
        self.seo_engine = seo_engine
        self.keyword_engine = keyword_engine
        self.quality_engine = quality_engine
        self.state_machine = ContentPipelineStateMachine()
    
    async def generate_marketing_content(self, product_id: str, content_types: List[str], 
                                         locale: str = "en") -> Dict[str, Any]:
        """Generate complete marketing package for product"""
        try:
            results = {}
            
            for content_type in content_types:
                result = await self._generate_content_type(product_id, content_type, locale)
                results[content_type] = result
            
            return {
                "product_id": product_id,
                "locale": locale,
                "generated_at": "",
                "content_types": list(results.keys()),
                "results": results,
                "status": "completed"
            }
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _generate_content_type(self, product_id: str, content_type: str, locale: str) -> Dict[str, Any]:
        """Generate specific content type"""
        try:
            # Get prompt for content type
            prompt_template = self._get_prompt_for_type(content_type)
            if not prompt_template:
                return {"error": f"No prompt for {content_type}"}
            
            # Get product data
            product_data = self._get_product_data(product_id)
            
            # Generate content
            messages = [
                AIMessage(role="system", content="You are a professional marketing copywriter."),
                AIMessage(role="user", content=prompt_template.format(**product_data))
            ]
            
            response = await self.ai_manager.generate(messages)
            
            return {
                "content_type": content_type,
                "content": response.content,
                "provider": response.provider,
                "model": response.model,
                "tokens_used": response.tokens_used,
                "locale": locale
            }
        except Exception as e:
            logger.error(f"Content generation failed for {content_type}: {e}")
            return {"error": str(e)}
    
    def _get_prompt_for_type(self, content_type: str) -> Optional[str]:
        """Get prompt template for content type"""
        prompt_map = {
            "seo_title": PromptTemplateFactory.create_seo_title_prompt(),
            "product_description": PromptTemplateFactory.create_product_description_prompt(),
            "seo_metadata": PromptTemplateFactory.create_seo_meta_prompt(),
            "social_media": PromptTemplateFactory.create_social_media_prompt(),
            "email_campaign": PromptTemplateFactory.create_email_campaign_prompt(),
            "landing_page": PromptTemplateFactory.create_landing_page_prompt(),
            "faq": PromptTemplateFactory.create_faq_prompt(),
            "competitor_analysis": PromptTemplateFactory.create_competitor_analysis_prompt()
        }
        return prompt_map.get(content_type)
    
    def _get_product_data(self, product_id: str) -> Dict[str, Any]:
        """Get product data for content generation"""
        return {
            "product_title": "Sample Product",
            "product_description": "A great product",
            "category": "digital",
            "keywords": ["marketing", "digital"],
            "features": ["Feature 1", "Feature 2"],
            "benefits": ["Benefit 1", "Benefit 2"],
            "target_audience": "Business owners",
            "target_market": "global",
            "price": "$29",
            "tone": "professional",
            "cta": "Buy Now",
            "offer": "50% off",
            "deadline": "2026-08-01",
            "platform": "instagram",
            "hashtags": "#marketing #digital"
        }


def main():
    """Test pipeline"""
    print("Content Pipeline initialized")
    print(f"Stages: {ContentPipeline.STAGES}")


if __name__ == "__main__":
    main()
