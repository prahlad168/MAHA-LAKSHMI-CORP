#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Sales Automation REST API
REST endpoints for sales automation engine.
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.engine import ConfigManager, DatabaseManager
from core.engine import AutomationCore
from workflow.engine import WorkflowEngine, WorkflowBuilder, WorkflowNodeType
from campaign.engine import CampaignEngine, CampaignType
from queue.engine import QueueEngine, JobPriority
from approval.engine import ApprovalEngine
from rules.engine import RulesEngine
from health.monitor import HealthMonitor
from metrics.collector import MetricsCollector
from audit.engine import AuditEngine

app = FastAPI(
    title="MAHA Sales Engine - Sales Automation API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

BASE_DIR = Path(__file__).parent.parent.parent.parent
CONFIG = ConfigManager(BASE_DIR / "config/engine.yaml")
DB = DatabaseManager(Path(CONFIG.get("database.path")))

automation = AutomationCore(BASE_DIR)


# ============ MODELS ============

class WorkflowCreate(BaseModel):
    name: str
    description: str = ""
    nodes: List[Dict[str, Any]]
    entry_node: str
    exit_node: str


class CampaignCreate(BaseModel):
    name: str
    campaign_type: str
    product_ids: List[str]
    marketplace_ids: List[str]
    schedule: Dict[str, Any] = {}


class PublishRequest(BaseModel):
    marketplace_id: str
    product_id: str
    product_data: Dict[str, Any] = {}


class ApprovalAction(BaseModel):
    approved: bool
    feedback: str = ""


class RuleCreate(BaseModel):
    name: str
    description: str
    condition: Dict[str, Any]
    action: Dict[str, Any]
    priority: int = 100


# ============ HEALTH ============

@app.get("/health")
async def health():
    return automation.health_monitor.get_overall_health()


@app.get("/health/components")
async def health_components():
    return automation.health_monitor.get_overall_health()


# ============ WORKFLOWS ============

@app.post("/api/v1/workflows")
async def create_workflow(workflow: WorkflowCreate):
    try:
        workflow_id = f"wf-{uuid.uuid4().hex[:12]}"
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO automation_workflows 
            (workflow_id, name, description, version, nodes, entry_node, exit_node, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            workflow_id, workflow.name, workflow.description, "1.0.0",
            json.dumps(workflow.nodes), workflow.entry_node, workflow.exit_node,
            json.dumps({}), datetime.now().isoformat(), datetime.now().isoformat()
        ))
        conn.commit()
        return {"workflow_id": workflow_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/workflows")
async def list_workflows():
    try:
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM automation_workflows")
        rows = cursor.fetchall()
        return {"workflows": [dict(row) for row in rows], "count": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, context: Dict[str, Any]):
    execution_id = automation.workflow_engine.start_workflow(workflow_id, context)
    if not execution_id:
        raise HTTPException(status_code=400, detail="Failed to start workflow")
    return {"execution_id": execution_id, "status": "running"}


# ============ PUBLICATION ============

@app.post("/api/v1/publish")
async def publish_product(request: PublishRequest):
    result = automation.publication_engine.publish_single(
        request.marketplace_id, request.product_id, request.product_data
    )
    return result


@app.post("/api/v1/publish/bulk")
async def publish_bulk(marketplace_id: str, product_ids: List[str]):
    result = automation.publication_engine.publish_bulk(marketplace_id, product_ids, {})
    return result


@app.post("/api/v1/sync/product")
async def sync_product(marketplace_id: str, product_id: str):
    result = automation.sync_engine.sync_product(marketplace_id, product_id)
    return result


@app.post("/api/v1/sync/marketplace/{marketplace_id}")
async def sync_marketplace(marketplace_id: str):
    result = automation.sync_engine.sync_marketplace(marketplace_id)
    return result


# ============ APPROVALS ============

@app.post("/api/v1/approvals/{request_id}/approve")
async def approve_request(request_id: str, action: ApprovalAction):
    success = automation.approval_engine.approve(request_id, "admin", action.feedback) if action.approved else automation.approval_engine.reject(request_id, "admin", action.feedback)
    return {"success": success}


@app.get("/api/v1/approvals")
async def list_approvals(status: str = "pending"):
    return {"approvals": [], "count": 0}


# ============ RULES ============

@app.post("/api/v1/rules")
async def create_rule(rule: RuleCreate):
    rule_id = automation.rules_engine.add_rule(
        rule.name, rule.description, rule.condition, rule.action, rule.priority
    )
    return {"rule_id": rule_id, "status": "created"}


@app.get("/api/v1/rules")
async def list_rules():
    return {"rules": [], "count": 0}


# ============ CAMPAIGNS ============

@app.post("/api/v1/campaigns")
async def create_campaign(campaign: CampaignCreate):
    campaign_id = automation.campaign_engine.create_campaign(
        campaign.name, campaign.campaign_type, campaign.product_ids,
        campaign.marketplace_ids, campaign.schedule
    )
    return {"campaign_id": campaign_id, "status": "created"}


@app.post("/api/v1/campaigns/{campaign_id}/start")
async def start_campaign(campaign_id: str):
    success = automation.campaign_engine.start_campaign(campaign_id)
    return {"success": success}


@app.get("/api/v1/campaigns")
async def list_campaigns():
    return {"campaigns": [], "count": 0}


# ============ QUEUE ============

@app.get("/api/v1/queue/stats")
async def queue_stats():
    return automation.queue_engine.get_stats()


@app.post("/api/v1/queue/jobs")
async def enqueue_job(job_type: str, payload: Dict[str, Any], priority: str = "normal"):
    job_id = automation.queue_engine.enqueue(job_type, payload, JobPriority[priority.upper()])
    return {"job_id": job_id, "status": "queued"}


@app.get("/api/v1/queue/jobs/{job_id}")
async def get_job(job_id: str):
    job = automation.queue_engine.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# ============ METRICS ============

@app.get("/api/v1/metrics")
async def get_metrics(metric_name: str = None):
    return automation.metrics_collector.get_metrics(metric_name)


# ============ AUDIT ============

@app.get("/api/v1/audit")
async def query_audit(resource_type: str = None, resource_id: str = None, limit: int = 100):
    logs = automation.audit_engine.query(resource_type, resource_id, limit=limit)
    return {"logs": logs, "count": len(logs)}


# ============ NOTIFICATIONS ============

@app.post("/api/v1/notifications")
async def send_notification(channel: str, recipient: str, subject: str, body: str):
    notification_id = automation.notification_engine.send_notification(
        channel, recipient, subject, body
    )
    return {"notification_id": notification_id}


# ============ WEBHOOKS ============

@app.post("/api/v1/webhooks/{marketplace_id}")
async def receive_webhook(marketplace_id: str, payload: Dict[str, Any], signature: str = ""):
    result = await automation.webhook_gateway.process_webhook(marketplace_id, payload, signature)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
