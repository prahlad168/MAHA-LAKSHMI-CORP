#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketing REST API
REST endpoints for marketing engine.
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.engine import ConfigManager, DatabaseManager
from core.engine import MarketingEngine
from ai.provider import AIProviderManager, AIConfig, AIMessage
from prompts.library import PromptLibrary, PromptTemplateFactory
from pipeline.state_machine import ContentPipeline, ContentStatus
from seo.engine import SEOEngine
from keywords.engine import KeywordEngine
from quality.engine import ContentQualityEngine
from brand.engine import BrandEngine
from localization.engine import LocalizationEngine
from ab_testing.engine import ABTestingEngine
from assets.engine import AssetGenerationEngine
from events.bus import event_bus, MarketingEvents
from queue.manager import MarketingJobQueue, JobPriority

app = FastAPI(
    title="MAHA Sales Engine - Marketing Engine API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Initialize components
BASE_DIR = Path(__file__).parent.parent.parent.parent
CONFIG = ConfigManager(BASE_DIR / "config/engine.yaml")
DB = DatabaseManager(Path(CONFIG.get("database.path")))

marketing_engine = MarketingEngine(BASE_DIR)
job_queue = MarketingJobQueue(max_workers=3)
job_queue.start()


# ============ MODELS ============

class MarketingGenerate(BaseModel):
    product_id: str
    content_types: List[str]
    locale: str = "en"
    ab_test: bool = False


class ContentApprove(BaseModel):
    content_id: str
    approved: bool
    feedback: str = ""


class BrandRulesCreate(BaseModel):
    brand_name: str
    voice: str
    tone: str
    writing_style: str
    forbidden_terms: List[str] = []
    preferred_terms: Dict[str, str] = {}
    target_audience: str = ""
    value_proposition: str = ""
    usp: str = ""


class ABTestCreate(BaseModel):
    product_id: str
    content_type: str
    variants: List[Dict[str, Any]]


class LocalizationRequest(BaseModel):
    content_id: str
    target_language: str
    content: str
    region: str = "global"
    currency: str = "USD"


# ============ HEALTH ============

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "module": "marketing-engine",
        "providers": marketing_engine.ai_manager.get_available_providers()
    }


# ============ MARKETING GENERATION ============

@app.post("/api/v1/generate")
async def generate_marketing(request: MarketingGenerate, background_tasks: BackgroundTasks):
    """Generate marketing content"""
    try:
        job_id = job_queue.enqueue(
            "generate_marketing",
            {
                "product_id": request.product_id,
                "content_types": request.content_types,
                "locale": request.locale
            },
            priority=JobPriority.HIGH
        )
        
        async def handle_generate(payload):
            return await marketing_engine.generate_marketing_package(
                payload["product_id"],
                payload["locale"]
            )
        
        job_queue.register_handler("generate_marketing", handle_generate)
        
        return {"job_id": job_id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/generate/seo")
async def generate_seo(product_id: str):
    """Generate SEO assets"""
    try:
        product_data = {"title": "Sample Product", "description": "A great product"}
        keywords = ["marketing", "digital"]
        seo = marketing_engine.seo_engine.generate_metadata(product_data, keywords)
        return seo.__dict__
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/generate/keywords")
async def generate_keywords(product_id: str):
    """Generate keywords"""
    try:
        product_data = {"title": "Sample Product", "category": "digital"}
        keywords = marketing_engine.keyword_engine.discover_keywords(product_data)
        return {
            "primary": marketing_engine.keyword_engine.get_primary_keywords(keywords),
            "secondary": marketing_engine.keyword_engine.get_secondary_keywords(keywords),
            "long_tail": marketing_engine.keyword_engine.get_long_tail_keywords(keywords)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/generate/faq")
async def generate_faq(product_id: str):
    """Generate FAQ"""
    return {"faq": [], "product_id": product_id}


@app.post("/api/v1/generate/landing-page")
async def generate_landing_page(product_id: str):
    """Generate landing page copy"""
    return {"landing_page": {}, "product_id": product_id}


@app.post("/api/v1/generate/email")
async def generate_email(product_id: str):
    """Generate email campaign"""
    return {"email": {}, "product_id": product_id}


@app.post("/api/v1/generate/social")
async def generate_social(product_id: str, platform: str = "instagram"):
    """Generate social media content"""
    return {"social": {}, "platform": platform, "product_id": product_id}


@app.post("/api/v1/generate/metadata")
async def generate_metadata(product_id: str):
    """Generate marketing metadata"""
    return {"metadata": {}, "product_id": product_id}


@app.post("/api/v1/generate/blog")
async def generate_blog(product_id: str):
    """Generate blog article"""
    return {"blog": {}, "product_id": product_id}


@app.post("/api/v1/generate/release-notes")
async def generate_release_notes(product_id: str):
    """Generate release notes"""
    return {"release_notes": {}, "product_id": product_id}


@app.post("/api/v1/generate/persona")
async def generate_persona(product_id: str):
    """Generate customer persona"""
    return {"persona": {}, "product_id": product_id}


@app.post("/api/v1/generate/competitor-analysis")
async def generate_competitor_analysis(product_id: str):
    """Generate competitor analysis"""
    return {"competitors": [], "product_id": product_id}


# ============ CONTENT MANAGEMENT ============

@app.get("/api/v1/assets")
async def list_assets(product_id: Optional[str] = None, content_type: Optional[str] = None):
    """List marketing assets"""
    return {"assets": [], "count": 0}


@app.get("/api/v1/assets/{asset_id}")
async def get_asset(asset_id: str):
    """Get asset details"""
    return {"asset_id": asset_id}


@app.post("/api/v1/assets/{asset_id}/approve")
async def approve_asset(asset_id: str, approval: ContentApprove):
    """Approve or reject content"""
    try:
        event = Event(
            MarketingEvents.CONTENT_APPROVED if approval.approved else MarketingEvents.CONTENT_REJECTED,
            {"asset_id": asset_id, "feedback": approval.feedback}
        )
        event_bus.publish(event)
        return {"status": "approved" if approval.approved else "rejected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/assets/{asset_id}/versions")
async def get_asset_versions(asset_id: str):
    """Get asset version history"""
    return {"versions": [], "asset_id": asset_id}


# ============ BRAND MANAGEMENT ============

@app.post("/api/v1/brand")
async def create_brand_rules(brand: BrandRulesCreate):
    """Create brand rules"""
    try:
        success = marketing_engine.brand_engine.create_brand_rules(
            brand.brand_name,
            brand.dict()
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create brand rules")
        return {"brand_name": brand.brand_name, "status": "created"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/brand/{brand_name}")
async def get_brand_rules(brand_name: str):
    """Get brand rules"""
    brand = marketing_engine.brand_engine.get_brand_rules(brand_name)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return asdict(brand)


# ============ A/B TESTING ============

@app.post("/api/v1/ab-tests")
async def create_ab_test(test: ABTestCreate):
    """Create A/B test"""
    try:
        test_id = marketing_engine.ab_testing_engine.create_test(
            test.product_id,
            test.content_type,
            test.variants
        )
        if not test_id:
            raise HTTPException(status_code=400, detail="Failed to create A/B test")
        return {"test_id": test_id, "status": "created"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ab-tests/{test_id}")
async def get_ab_test(test_id: str):
    """Get A/B test"""
    test = marketing_engine.ab_testing_engine.get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return asdict(test)


# ============ LOCALIZATION ============

@app.post("/api/v1/localize")
async def localize_content(request: LocalizationRequest):
    """Localize content"""
    try:
        result = marketing_engine.localization_engine.localize_content(
            request.content_id,
            request.target_language,
            request.content,
            {
                "product_id": request.content_id,
                "content_type": "marketing",
                "region": request.region,
                "currency": request.currency
            }
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/localize/{content_id}")
async def get_localized_content(content_id: str, language: str):
    """Get localized content"""
    content = marketing_engine.localization_engine.get_localized_content(content_id, language)
    if not content:
        raise HTTPException(status_code=404, detail="Localized content not found")
    return content


# ============ ASSETS ============

@app.post("/api/v1/assets/generate")
async def generate_asset(product_id: str, asset_type: str):
    """Generate asset specification"""
    try:
        product_data = {"title": "Sample Product"}
        asset = marketing_engine.asset_engine.generate_asset_spec(product_id, asset_type, product_data)
        return asdict(asset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ PROMPTS ============

@app.get("/api/v1/prompts")
async def list_prompts(category: Optional[str] = None):
    """List prompt templates"""
    prompts = marketing_engine.prompt_library.list_prompts(category=category)
    return {
        "prompts": [
            {
                "prompt_id": p.prompt_id,
                "name": p.name,
                "category": p.category,
                "version": p.version,
                "description": p.description,
                "tags": p.tags,
                "usage_count": p.usage_count,
                "success_rate": p.success_rate
            }
            for p in prompts
        ],
        "count": len(prompts)
    }


# ============ JOB QUEUE ============

@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status"""
    job = job_queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/v1/jobs/queue/stats")
async def queue_stats():
    """Get queue statistics"""
    return {
        "queue_size": job_queue._queue.qsize(),
        "total_jobs": len(job_queue._jobs),
        "workers": job_queue._max_workers
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
