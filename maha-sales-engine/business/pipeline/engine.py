#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Business Pipeline
End-to-end autonomous business execution workflow.
"""

import sys
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine import ConfigManager, DatabaseManager

logger = logging.getLogger("maha-sales-engine.business.pipeline")


@dataclass
class PipelineResult:
    """Pipeline execution result"""
    pipeline_id: str
    started_at: str
    completed_at: Optional[str] = None
    status: str = "running"
    products_created: int = 0
    products_generated: int = 0
    products_published: int = 0
    marketing_content_created: int = 0
    revenue_generated: float = 0.0
    errors: List[str] = field(default_factory=list)


class BusinessPipeline:
    """End-to-end business execution pipeline"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_dir = base_dir / "business" / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        config_path = base_dir / "config" / "engine.yaml"
        self.config = ConfigManager(config_path)
        self.db = DatabaseManager(Path(self.config.get("database.path")))
        
        # Initialize modules
        from product_factory.core.main import ProductFactoryMain
        from marketing_engine.core.engine import MarketingEngine
        from sales_automation.core.engine import AutomationCore
        from business.core.engine import BusinessExecutionEngine
        from scheduler.scheduler import Scheduler, create_daily_report_job
        
        self.product_factory = ProductFactoryMain(base_dir)
        self.marketing_engine = MarketingEngine(base_dir)
        self.sales_automation = AutomationCore(base_dir)
        self.business_engine = BusinessExecutionEngine(base_dir)
        self.scheduler = Scheduler()
        
        # Register daily jobs
        self._register_jobs()
        
        logger.info("Business Pipeline initialized")
    
    def _register_jobs(self):
        """Register scheduled jobs"""
        from scheduler.scheduler import create_daily_report_job, create_market_research_job
        
        # Daily report job
        report_job = create_daily_report_job(self.business_engine)
        self.scheduler.register_job(report_job)
        
        # Market research job
        market_job = create_market_research_job(None)
        self.scheduler.register_job(market_job)
        
        logger.info("Scheduled jobs registered")
    
    async def execute_daily_workflow(self) -> PipelineResult:
        """Execute daily business workflow"""
        pipeline_id = f"PIPE-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        result = PipelineResult(
            pipeline_id=pipeline_id,
            started_at=datetime.now().isoformat()
        )
        
        try:
            logger.info(f"Starting daily workflow: {pipeline_id}")
            
            # 1. Generate products
            logger.info("Step 1: Product Generation")
            products = self._generate_daily_products()
            result.products_created = len(products)
            
            # 2. Generate marketing content
            logger.info("Step 2: Marketing Content Generation")
            marketing_count = await self._generate_marketing_content(products)
            result.marketing_content_created = marketing_count
            
            # 3. Publish products
            logger.info("Step 3: Product Publishing")
            published = self._publish_products(products)
            result.products_published = len(published)
            
            # 4. Generate daily report
            logger.info("Step 4: Daily Report")
            report = self.business_engine.generate_daily_report()
            result.revenue_generated = report.revenue_usd
            
            result.status = "completed"
            result.completed_at = datetime.now().isoformat()
            
            logger.info(f"Daily workflow completed: {pipeline_id}")
            return result
            
        except Exception as e:
            logger.error(f"Daily workflow failed: {e}")
            result.status = "failed"
            result.errors.append(str(e))
            result.completed_at = datetime.now().isoformat()
            return result
    
    def _generate_daily_products(self, count: int = 3) -> List[str]:
        """Generate daily products"""
        products = []
        categories = ["ebook", "template", "prompt_pack", "checklist", "mini_course"]
        
        for i in range(count):
            category = categories[i % len(categories)]
            product_id = self.product_factory.create_product(
                title=f"Daily Product {datetime.now().strftime('%Y%m%d')} #{i+1}",
                category=category,
                description=f"Auto-generated {category} product"
            )
            if product_id:
                products.append(product_id)
        
        return products
    
    async def _generate_marketing_content(self, products: List[str]) -> int:
        """Generate marketing content for products"""
        count = 0
        for product_id in products:
            try:
                result = await self.marketing_engine.generate_marketing_package(product_id)
                if "error" not in result:
                    count += 1
            except Exception as e:
                logger.error(f"Marketing content generation failed for {product_id}: {e}")
        return count
    
    def _publish_products(self, products: List[str]) -> List[str]:
        """Publish products to marketplaces"""
        published = []
        for product_id in products:
            try:
                # Placeholder for actual publishing logic
                logger.info(f"Publishing product: {product_id}")
                published.append(product_id)
            except Exception as e:
                logger.error(f"Publishing failed for {product_id}: {e}")
        return published
    
    def start(self):
        """Start the pipeline"""
        self.scheduler.start()
        logger.info("Business Pipeline started")
    
    def stop(self):
        """Stop the pipeline"""
        self.scheduler.stop()
        logger.info("Business Pipeline stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get pipeline status"""
        return {
            "module": "business-pipeline",
            "status": "running",
            "scheduler": self.scheduler.get_all_jobs(),
            "product_factory": self.product_factory.get_status(),
            "marketing_engine": self.marketing_engine.get_status(),
            "sales_automation": self.sales_automation.get_status(),
            "business_engine": self.business_engine.get_status()
        }


def main():
    """Test business pipeline"""
    from pathlib import Path
    base_dir = Path(__file__).parent.parent.parent
    pipeline = BusinessPipeline(base_dir)
    print("Business Pipeline initialized")
    print(f"Status: {pipeline.get_status()}")


if __name__ == "__main__":
    main()
