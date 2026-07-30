#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketing Core
Main orchestrator for marketing engine.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine import ConfigManager, DatabaseManager
from marketing_engine.ai.provider import AIProviderManager
from marketing_engine.prompts.library import PromptLibrary
from marketing_engine.pipeline.state_machine import ContentPipeline
from marketing_engine.seo.engine import SEOEngine
from marketing_engine.keywords.engine import KeywordEngine
from marketing_engine.quality.engine import ContentQualityEngine
from marketing_engine.brand.engine import BrandEngine
from marketing_engine.localization.engine import LocalizationEngine
from marketing_engine.ab_testing.engine import ABTestingEngine
from marketing_engine.assets.engine import AssetGenerationEngine

logger = logging.getLogger("maha-sales-engine.marketing")


class MarketingEngine:
    """Main orchestrator for marketing engine"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_dir = base_dir / "marketing-engine" / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        config_path = base_dir / "config" / "engine.yaml"
        self.config = ConfigManager(config_path)
        self.db = DatabaseManager(Path(self.config.get("database.path")))
        
        # Initialize engines
        self.ai_manager = AIProviderManager()
        self.prompt_library = PromptLibrary(self.db, self.output_dir / "prompts")
        self.seo_engine = SEOEngine(self.ai_manager, self.prompt_library)
        self.keyword_engine = KeywordEngine(self.ai_manager)
        self.quality_engine = ContentQualityEngine(None)  # BrandEngine injected later
        self.brand_engine = BrandEngine(self.db)
        self.quality_engine.brand_engine = self.brand_engine
        self.localization_engine = LocalizationEngine(self.db, self.ai_manager)
        self.ab_testing_engine = ABTestingEngine(self.db)
        self.asset_engine = AssetGenerationEngine(self.db, self.ai_manager)
        
        self.pipeline = ContentPipeline(
            self.db, self.ai_manager, self.prompt_library,
            self.seo_engine, self.keyword_engine, self.quality_engine
        )
        
        logger.info("Marketing Engine initialized")
    
    async def generate_marketing_package(self, product_id: str, locale: str = "en") -> Dict[str, Any]:
        """Generate complete marketing package"""
        try:
            content_types = [
                "seo_title",
                "seo_metadata",
                "product_description",
                "social_media",
                "email_campaign",
                "landing_page",
                "faq",
                "competitor_analysis"
            ]
            
            result = await self.pipeline.generate_marketing_content(product_id, content_types, locale)
            return result
        except Exception as e:
            logger.error(f"Marketing package generation failed: {e}")
            return {"error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get engine status"""
        return {
            "module": "marketing-engine",
            "status": "running",
            "providers": self.ai_manager.get_available_providers(),
            "output_dir": str(self.output_dir)
        }


def main():
    """Test marketing engine"""
    from pathlib import Path
    
    base_dir = Path(__file__).parent.parent.parent
    engine = MarketingEngine(base_dir)
    
    print("Marketing Engine Test")
    print(f"Status: {engine.get_status()}")


if __name__ == "__main__":
    main()
