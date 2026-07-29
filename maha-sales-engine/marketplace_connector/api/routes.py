#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketplace Connector API Routes
REST API for marketplace connector.
"""

import os
import sys
import json
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File
from pydantic import BaseModel, Field

logger = logging.getLogger("maha-sales-engine.marketplace_connector.api")


# Pydantic models
class AccountRequest(BaseModel):
    provider: str
    name: str
    credentials: Dict[str, Any]
    default: bool = False


class PublishRequest(BaseModel):
    product_id: str
    account_id: str
    provider: str = "gumroad"


class SyncRequest(BaseModel):
    sync_type: str = "manual"
    product_id: Optional[str] = None


# Create FastAPI app
app = FastAPI(
    title="MAHA Sales Engine V1 - Marketplace Connector API",
    description="Gumroad Marketplace Connector API",
    version="1.0.0"
)


# Dependency injection
def get_provider():
    from marketplace_connector.providers.gumroad.gumroad_provider import GumroadProvider
    return GumroadProvider({})


def get_validation_engine():
    from marketplace_connector.publication.validation_engine import ValidationEngine
    return ValidationEngine()


def get_publication_pipeline():
    from marketplace_connector.publication.publication_pipeline import PublicationPipeline
    return PublicationPipeline(get_provider(), get_validation_engine(), None)


def get_sync_engine():
    from marketplace_connector.sync.sync_engine import SyncEngine
    return SyncEngine(get_provider(), None)


def get_webhook_engine():
    from marketplace_connector.webhooks.webhook_engine import WebhookEngine
    return WebhookEngine(get_provider(), None)


def get_retry_engine():
    from marketplace_connector.queue.retry_engine import RetryEngine
    return RetryEngine()


def get_metrics_collector():
    from marketplace_connector.metrics.metrics_collector import MetricsCollector
    return MetricsCollector()


def get_db_manager():
    from marketplace_connector.db.marketplace_db import MarketplaceDatabaseManager
    from shared.database import DatabaseManager
    db = DatabaseManager("data/marketplace_connector.db")
    return MarketplaceDatabaseManager(db)


# API Endpoints

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "marketplace_connector", "version": "1.0.0"}


@app.post("/marketplace/accounts")
async def create_account(request: AccountRequest, db = Depends(get_db_manager)):
    """Create marketplace account"""
    from marketplace_connector.core.marketplace_provider import ProviderType
    
    try:
        provider = ProviderType(request.provider)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {request.provider}")
    
    account_id = f"acc-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
    account = {
        "account_id": account_id,
        "provider": request.provider,
        "name": request.name,
        "credentials": request.credentials,
        "active": 1,
        "default": 1 if request.default else 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    db.save_account(account)
    
    return {
        "account_id": account_id,
        "provider": request.provider,
        "name": request.name,
        "active": True,
        "default": request.default
    }


@app.get("/marketplace/accounts")
async def list_accounts(db = Depends(get_db_manager)):
    """List marketplace accounts"""
    accounts = db.db.execute("SELECT * FROM marketplace_accounts")
    return {
        "accounts": [
            {
                "account_id": a.get("account_id"),
                "provider": a.get("provider"),
                "name": a.get("name"),
                "active": bool(a.get("active")),
                "default": bool(a.get("default"))
            }
            for a in accounts
        ]
    }


@app.post("/marketplace/connect")
async def connect_account(account_id: str, provider = Depends(get_provider)):
    """Test connection to marketplace"""
    # In production, load account from DB and initialize provider
    result = await provider.connect()
    return {"connected": result}


@app.post("/marketplace/publish")
async def publish_product(request: PublishRequest, pipeline = Depends(get_publication_pipeline), db = Depends(get_db_manager)):
    """Publish product to marketplace"""
    # Load product package
    product_path = f"data/products/{request.product_id}"
    
    # Load metadata
    metadata_path = Path(product_path) / "metadata.json"
    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail="Product not found")
    
    with open(metadata_path) as f:
        metadata = json.load(f)
    
    metadata["product_id"] = request.product_id
    metadata["provider"] = request.provider
    
    # Execute pipeline
    result = await pipeline.execute(product_path, metadata)
    
    # Save publication record
    publication = {
        "publication_id": result.data.get("publication_id", ""),
        "product_id": request.product_id,
        "account_id": request.account_id,
        "provider": request.provider,
        "status": result.status.value,
        "current_stage": "completed",
        "stages_completed": ["load", "validate_structure", "validate_files", "validate_metadata", "build_payload", "upload_product", "upload_thumbnail", "create_listing", "publish", "store_ids", "generate_report"],
        "errors": [],
        "data": result.data,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "published_at": datetime.now().isoformat() if result.success else None
    }
    db.save_publication(publication)
    
    return {
        "publication_id": result.data.get("publication_id"),
        "success": result.success,
        "status": result.status.value,
        "marketplace_product_id": result.marketplace_product_id,
        "marketplace_url": result.marketplace_url,
        "message": result.message
    }


@app.post("/marketplace/publish/bulk")
async def bulk_publish(requests: List[PublishRequest], background_tasks: BackgroundTasks, pipeline = Depends(get_publication_pipeline)):
    """Bulk publish products"""
    job_id = f"bulk-{int(time.time() * 1000)}"
    
    def bulk_publish_task():
        for req in requests:
            try:
                product_path = f"data/products/{req.product_id}"
                metadata_path = Path(product_path) / "metadata.json"
                if metadata_path.exists():
                    with open(metadata_path) as f:
                        metadata = json.load(f)
                    metadata["product_id"] = req.product_id
                    metadata["provider"] = req.provider
                    import asyncio
                    asyncio.run(pipeline.execute(product_path, metadata))
            except Exception as e:
                logger.error(f"Bulk publish error: {e}")
    
    background_tasks.add_task(bulk_publish_task)
    
    return {
        "job_id": job_id,
        "status": "queued",
        "count": len(requests)
    }


@app.post("/marketplace/sync")
async def sync_all(sync_engine = Depends(get_sync_engine)):
    """Sync all products"""
    from marketplace_connector.sync.sync_engine import SyncType
    
    job = await sync_engine.sync(SyncType.BULK)
    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "products_synced": job.products_synced,
        "products_failed": job.products_failed
    }


@app.post("/marketplace/sync/{product_id}")
async def sync_product(product_id: str, sync_engine = Depends(get_sync_engine)):
    """Sync single product"""
    from marketplace_connector.sync.sync_engine import SyncType
    
    job = await sync_engine.sync(SyncType.SINGLE_PRODUCT, product_id)
    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "product_id": product_id
    }


@app.get("/marketplace/products")
async def list_products(db = Depends(get_db_manager)):
    """List marketplace products"""
    products = db.db.execute("SELECT * FROM marketplace_products")
    return {
        "products": [
            {
                "product_id": p.get("product_id"),
                "internal_product_id": p.get("internal_product_id"),
                "marketplace_product_id": p.get("marketplace_product_id"),
                "marketplace_url": p.get("marketplace_url"),
                "status": p.get("status"),
                "provider": p.get("provider"),
                "price": p.get("price"),
                "currency": p.get("currency")
            }
            for p in products
        ]
    }


@app.get("/marketplace/publications")
async def list_publications(db = Depends(get_db_manager)):
    """List publications"""
    publications = db.db.execute("SELECT * FROM marketplace_publications ORDER BY created_at DESC LIMIT 100")
    return {
        "publications": [
            {
                "publication_id": p.get("publication_id"),
                "product_id": p.get("product_id"),
                "provider": p.get("provider"),
                "status": p.get("status"),
                "current_stage": p.get("current_stage"),
                "created_at": p.get("created_at"),
                "published_at": p.get("published_at")
            }
            for p in publications
        ]
    }


@app.get("/marketplace/errors")
async def list_errors(db = Depends(get_db_manager)):
    """List publication errors"""
    errors = db.db.execute("SELECT * FROM publication_errors WHERE resolved = 0 ORDER BY created_at DESC")
    return {
        "errors": [
            {
                "error_id": e.get("error_id"),
                "publication_id": e.get("publication_id"),
                "stage": e.get("stage"),
                "message": e.get("message"),
                "created_at": e.get("created_at")
            }
            for e in errors
        ]
    }


@app.post("/marketplace/webhooks")
async def process_webhook(payload: Dict[str, Any], signature: str, webhook_engine = Depends(get_webhook_engine)):
    """Process incoming webhook"""
    result = await webhook_engine.process(payload, signature, "gumroad")
    return result


@app.get("/marketplace/reports")
async def get_reports(metrics = Depends(get_metrics_collector)):
    """Get publication reports"""
    return {
        "metrics": metrics.get_metrics(),
        "generated_at": datetime.now().isoformat()
    }


@app.get("/marketplace/metrics")
async def get_metrics(metrics = Depends(get_metrics_collector)):
    """Get connector metrics"""
    return metrics.get_metrics()


@app.get("/marketplace/health")
async def health_check(provider = Depends(get_provider), metrics = Depends(get_metrics_collector)):
    """Health check endpoint"""
    provider_health = await provider.health()
    connector_metrics = metrics.get_metrics()
    
    return {
        "status": "healthy" if provider_health.get("status") == "healthy" else "degraded",
        "provider": provider_health,
        "metrics": connector_metrics,
        "timestamp": datetime.now().isoformat()
    }


def get_db_manager():
    from marketplace_connector.db.marketplace_db import MarketplaceDatabaseManager
    from shared.database import DatabaseManager
    db = DatabaseManager("data/marketplace_connector.db")
    return MarketplaceDatabaseManager(db)


def get_provider():
    from marketplace_connector.providers.gumroad.gumroad_provider import GumroadProvider
    return GumroadProvider({})


def get_validation_engine():
    from marketplace_connector.publication.validation_engine import ValidationEngine
    return ValidationEngine()


def get_publication_pipeline():
    from marketplace_connector.publication.publication_pipeline import PublicationPipeline
    return PublicationPipeline(get_provider(), get_validation_engine(), get_db_manager())


def get_sync_engine():
    from marketplace_connector.sync.sync_engine import SyncEngine
    return SyncEngine(get_provider(), get_db_manager())


def get_webhook_engine():
    from marketplace_connector.webhooks.webhook_engine import WebhookEngine
    return WebhookEngine(get_provider(), get_db_manager())


def get_retry_engine():
    from marketplace_connector.queue.retry_engine import RetryEngine
    return RetryEngine()


def get_metrics_collector():
    from marketplace_connector.metrics.metrics_collector import MetricsCollector
    return MetricsCollector()
