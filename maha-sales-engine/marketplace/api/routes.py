#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketplace REST API
REST endpoints for marketplace platform.
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.engine import ConfigManager, DatabaseManager
from marketplace.sdk.base import BaseMarketplaceProvider, PublicationStatus, ProductMapping, MarketplaceConfig
from marketplace.core.registry import ProviderRegistry
from core.state_machine import StatusManager
from marketplace.security.credentials import CredentialManager
from marketplace.engines.publishing import PublishingEngine, SynchronizationEngine
from marketplace.events.bus import event_bus, MarketplaceEvents
from marketplace.queue.manager import JobQueue, RetryManager

app = FastAPI(
    title="MAHA Sales Engine - Marketplace Platform API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Initialize components
BASE_DIR = Path(__file__).parent.parent.parent.parent
CONFIG = ConfigManager(BASE_DIR / "config/engine.yaml")
DB = DatabaseManager(Path(CONFIG.get("database.path")))

registry = ProviderRegistry()
credential_manager = CredentialManager()
publishing_engine = PublishingEngine(DB, registry, credential_manager, event_bus)
sync_engine = SynchronizationEngine(DB, registry, credential_manager, event_bus)
job_queue = JobQueue(max_workers=5)
job_queue.start()
retry_manager = RetryManager()


# ============ MODELS ============

class MarketplaceCreate(BaseModel):
    name: str
    provider: str
    version: str = "1.0.0"
    capabilities: List[str] = []
    auth_type: str = "api_key"
    config: Dict[str, Any] = {}


class ProductPublish(BaseModel):
    marketplace_id: str
    product_id: str
    product_data: Dict[str, Any] = {}


class CredentialStore(BaseModel):
    marketplace_id: str
    credential_type: str
    credentials: Dict[str, Any]


# ============ MARKETPLACE MANAGEMENT ============

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "module": "marketplace",
        "providers_registered": len(registry.list_providers()),
        "queue_stats": job_queue.get_stats()
    }


@app.post("/api/v1/marketplaces")
async def create_marketplace(marketplace: MarketplaceCreate):
    """Register new marketplace"""
    try:
        marketplace_id = f"mkt-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        config = MarketplaceConfig(
            marketplace_id=marketplace_id,
            name=marketplace.name,
            provider=marketplace.provider,
            version=marketplace.version,
            status="active",
            capabilities=marketplace.capabilities,
            auth_type=marketplace.auth_type,
            config=marketplace.config,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO marketplaces (id, name, provider, version, status, capabilities, auth_type, config, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            config.marketplace_id, config.name, config.provider, config.version,
            config.status, json.dumps(config.capabilities), config.auth_type,
            json.dumps(config.config), config.created_at, config.updated_at
        ))
        conn.commit()
        
        return {"marketplace_id": marketplace_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/marketplaces")
async def list_marketplaces(status: Optional[str] = None, provider: Optional[str] = None):
    """List marketplaces"""
    try:
        conn = DB.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM marketplaces"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
        elif provider:
            query += " WHERE provider = ?"
            params.append(provider)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        marketplaces = []
        for row in rows:
            m = dict(row)
            m["capabilities"] = json.loads(m.get("capabilities", "[]"))
            m["config"] = json.loads(m.get("config", "{}"))
            marketplaces.append(m)
        
        return {"marketplaces": marketplaces, "count": len(marketplaces)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/marketplaces/{marketplace_id}")
async def get_marketplace(marketplace_id: str):
    """Get marketplace details"""
    try:
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM marketplaces WHERE id = ?", (marketplace_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Marketplace not found")
        
        marketplace = dict(row)
        marketplace["capabilities"] = json.loads(marketplace.get("capabilities", "[]"))
        marketplace["config"] = json.loads(marketplace.get("config", "{}"))
        
        return marketplace
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/marketplaces/{marketplace_id}")
async def delete_marketplace(marketplace_id: str):
    """Remove marketplace"""
    try:
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM marketplaces WHERE id = ?", (marketplace_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Marketplace not found")
        
        return {"marketplace_id": marketplace_id, "status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ PROVIDER MANAGEMENT ============

@app.get("/api/v1/providers")
async def list_providers():
    """List registered providers"""
    return {
        "providers": registry.list_providers(),
        "count": len(registry.list_providers())
    }


@app.get("/api/v1/providers/{provider_name}/health")
async def provider_health(provider_name: str):
    """Check provider health"""
    try:
        provider_class = registry.get_provider_class(provider_name)
        if not provider_class:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        # Create temporary instance for health check
        temp_config = {"marketplace_id": "health-check", "provider": provider_name}
        instance = registry.create_instance(provider_name, temp_config, credential_manager)
        
        if instance:
            health = await instance.health()
            return health
        else:
            raise HTTPException(status_code=500, detail="Failed to create provider instance")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/providers/{provider_name}/validate")
async def validate_provider(provider_name: str):
    """Validate provider implementation"""
    provider_class = registry.get_provider_class(provider_name)
    if not provider_class:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    validation = registry.validate_dependencies(provider_name)
    return validation


# ============ CREDENTIAL MANAGEMENT ============

@app.post("/api/v1/credentials")
async def store_credential(credential: CredentialStore):
    """Store marketplace credentials"""
    try:
        success = credential_manager.store_credential(
            credential.marketplace_id,
            credential.credential_type,
            credential.credentials
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to store credentials")
        return {"status": "stored"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/credentials/{marketplace_id}")
async def get_credential(marketplace_id: str, credential_type: str = "api_key"):
    """Get marketplace credentials"""
    creds = credential_manager.get_credential(marketplace_id, credential_type)
    if not creds:
        raise HTTPException(status_code=404, detail="Credentials not found")
    return {"marketplace_id": marketplace_id, "credentials": creds}


@app.delete("/api/v1/credentials/{marketplace_id}")
async def delete_credential(marketplace_id: str, credential_type: str = "api_key"):
    """Delete marketplace credentials"""
    success = credential_manager.delete_credential(marketplace_id, credential_type)
    if not success:
        raise HTTPException(status_code=404, detail="Credentials not found")
    return {"status": "deleted"}


# ============ PUBLICATION ============

@app.post("/api/v1/publish")
async def publish_product(publish: ProductPublish, background_tasks: BackgroundTasks):
    """Publish product to marketplace"""
    try:
        # Enqueue job
        job_id = job_queue.enqueue(
            "publish",
            {
                "marketplace_id": publish.marketplace_id,
                "product_id": publish.product_id,
                "product_data": publish.product_data
            },
            priority=JobPriority.HIGH
        )
        
        # Register handler
        async def handle_publish(payload):
            return await publishing_engine.publish(
                payload["marketplace_id"],
                payload["product_id"],
                payload["product_data"]
            )
        
        job_queue.register_handler("publish", handle_publish)
        
        return {"job_id": job_id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/update")
async def update_product(publish: ProductPublish):
    """Update product on marketplace"""
    try:
        result = await publishing_engine.update(
            publish.marketplace_id,
            publish.product_id,
            publish.product_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/archive")
async def archive_product(marketplace_id: str, product_id: str):
    """Archive product"""
    try:
        result = await publishing_engine.archive(marketplace_id, product_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/delete")
async def delete_product(marketplace_id: str, product_id: str):
    """Delete product"""
    try:
        result = await publishing_engine.delete(marketplace_id, product_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ SYNCHRONIZATION ============

@app.post("/api/v1/sync/product")
async def sync_product(marketplace_id: str, product_id: str):
    """Sync single product"""
    try:
        result = await sync_engine.sync_product(marketplace_id, product_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/sync/marketplace/{marketplace_id}")
async def sync_marketplace(marketplace_id: str):
    """Sync entire marketplace"""
    try:
        result = await sync_engine.sync_marketplace(marketplace_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ JOB MANAGEMENT ============

@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status"""
    job = job_queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.post("/api/v1/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel job"""
    success = job_queue.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot cancel job")
    return {"job_id": job_id, "status": "cancelled"}


@app.get("/api/v1/jobs/queue/stats")
async def queue_stats():
    """Get queue statistics"""
    return job_queue.get_stats()


# ============ WEBHOOKS ============

@app.post("/api/v1/webhooks/{marketplace_id}")
async def receive_webhook(marketplace_id: str, payload: Dict[str, Any], signature: str = ""):
    """Receive webhook from marketplace"""
    from marketplace.engines.publishing import WebhookEngine
    webhook_engine = WebhookEngine(DB, event_bus)
    
    result = await webhook_engine.process_webhook(marketplace_id, payload, signature)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@app.post("/api/v1/webhooks/{marketplace_id}/register")
async def register_webhook(marketplace_id: str, webhook_url: str, events: List[str], secret: str = ""):
    """Register webhook endpoint"""
    from marketplace.engines.publishing import WebhookEngine
    webhook_engine = WebhookEngine(DB, event_bus)
    
    success = webhook_engine.register_webhook(marketplace_id, webhook_url, events, secret)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to register webhook")
    return {"status": "registered"}


# ============ SEARCH ============

@app.get("/api/v1/search")
async def search_marketplaces(
    status: Optional[str] = None,
    provider: Optional[str] = None,
    product: Optional[str] = None,
    tag: Optional[str] = None
):
    """Search marketplaces and products"""
    # Implementation depends on search requirements
    return {"results": [], "count": 0}


# ============ STATISTICS ============

@app.get("/api/v1/stats")
async def get_stats():
    """Get marketplace statistics"""
    try:
        conn = DB.get_connection()
        cursor = conn.cursor()
        
        # Total marketplaces
        cursor.execute("SELECT COUNT(*) FROM marketplaces")
        total_marketplaces = cursor.fetchone()[0]
        
        # Active marketplaces
        cursor.execute("SELECT COUNT(*) FROM marketplaces WHERE status = 'active'")
        active_marketplaces = cursor.fetchone()[0]
        
        # Products by status
        cursor.execute("SELECT publication_status, COUNT(*) FROM marketplace_products GROUP BY publication_status")
        by_status = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Jobs stats
        cursor.execute("SELECT state, COUNT(*) FROM publication_jobs GROUP BY state")
        jobs_by_state = {row[0]: row[1] for row in cursor.fetchall()}
        
        return {
            "total_marketplaces": total_marketplaces,
            "active_marketplaces": active_marketplaces,
            "products_by_status": by_status,
            "jobs_by_state": jobs_by_state,
            "queue_stats": job_queue.get_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
