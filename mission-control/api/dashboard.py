#!/usr/bin/env python3
"""
KILO SALES NODE - FastAPI Webhook Server
Receives real-time updates from nodes and serves dashboard API.
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import time
import ssl
from datetime import datetime
import uvicorn

# Configuration
DASHBOARD_URL = "https://mahalaksmi.web.id"
API_VERSION = "v1"
NODES_DB = {}  # In-memory node registry (use Redis/PostgreSQL in production)

app = FastAPI(
    title="KILO SALES NODE - Mission Control API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mahalaksmi.web.id", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ MODELS ============

class NodeRegistration(BaseModel):
    node_id: str
    name: str
    region: str
    market: str
    capabilities: list[str]
    products: list[str]
    version: str


class NodeHeartbeat(BaseModel):
    node_id: str
    status: str
    timestamp: str
    metrics: Dict[str, Any]


class NodeReport(BaseModel):
    node_id: str
    report_date: str
    metrics: Dict[str, Any]
    top_products: list[Dict[str, Any]]
    top_channels: list[Dict[str, Any]]
    insights: Dict[str, Any]


class NodeCommand(BaseModel):
    command_id: str
    type: str
    params: Dict[str, Any]
    priority: str
    timestamp: str


# ============ AUTH ============

async def verify_node_auth(request: Request):
    """Verify node authentication via JWT or mTLS"""
    # Check for JWT token
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        # In production: verify JWT signature and expiry
        return token
    
    # Check for mTLS client certificate
    if request.headers.get("X-Node-ID"):
        # In production: verify client certificate
        return request.headers.get("X-Node-ID")
    
    raise HTTPException(status_code=401, detail="Unauthorized")


# ============ ENDPOINTS ============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "KILO SALES NODE Dashboard API",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.post("/api/v1/nodes/register")
async def register_node(node: NodeRegistration, auth: str = Depends(verify_node_auth)):
    """Register a new sales node"""
    node_id = node.node_id
    
    # Store node info
    NODES_DB[node_id] = {
        "info": node.dict(),
        "registered_at": datetime.now().isoformat(),
        "last_heartbeat": None,
        "status": "online"
    }
    
    print(f"✅ Node registered: {node_id} - {node.name}")
    
    return JSONResponse(
        status_code=201,
        content={
            "node_id": node_id,
            "status": "registered",
            "dashboard_url": DASHBOARD_URL,
            "next_report_at": (datetime.now() + timedelta(days=1)).isoformat()
        }
    )


@app.post("/api/v1/nodes/heartbeat")
async def node_heartbeat(heartbeat: NodeHeartbeat, auth: str = Depends(verify_node_auth)):
    """Receive heartbeat from node"""
    node_id = heartbeat.node_id
    
    if node_id not in NODES_DB:
        raise HTTPException(status_code=404, detail="Node not registered")
    
    NODES_DB[node_id]["last_heartbeat"] = heartbeat.timestamp
    NODES_DB[node_id]["status"] = heartbeat.status
    NODES_DB[node_id]["metrics"] = heartbeat.metrics
    
    return {"status": "received"}


@app.post("/api/v1/nodes/report")
async def node_report(report: NodeReport, auth: str = Depends(verify_node_auth)):
    """Receive daily report from node"""
    node_id = report.node_id
    
    if node_id not in NODES_DB:
        raise HTTPException(status_code=404, detail="Node not registered")
    
    # Store report
    report_id = f"RPT-{datetime.now().strftime('%Y%m%d')}-{node_id}"
    
    # In production: save to PostgreSQL/Redis
    print(f"📊 Report received from {node_id}: {report.report_date}")
    print(f"   Revenue: ${report.metrics.get('revenue_usd', 0):.2f}")
    print(f"   Deals: {report.metrics.get('deals_closed', 0)}")
    
    # Generate AI recommendations
    actions = []
    if report.metrics.get("whatsapp_conversion", 0) > 0.15:
        actions.append("increase_whatsapp_outreach")
    if report.metrics.get("revenue_usd", 0) < 100:
        actions.append("focus_on_high_value_products")
    
    return {
        "status": "received",
        "report_id": report_id,
        "actions": actions
    }


@app.get("/api/v1/nodes/commands")
async def get_commands(since: str, auth: str = Depends(verify_node_auth)):
    """Get commands from dashboard for node"""
    node_id = auth
    
    # In production: query commands from database
    # For now, return empty
    return {"commands": []}


@app.get("/api/v1/products")
async def get_products(market: Optional[str] = None):
    """Get product listings"""
    # In production: query from database
    products = [
        {
            "product_id": "social-media-kit",
            "name": "Social Media Kit Pro",
            "price_usd": 19.00,
            "price_idr": 285000,
            "description": "500+ templates for Instagram, Facebook, TikTok",
            "features": ["instagram", "facebook", "tiktok"],
            "url": "https://mahalaksmi.web.id/products/social-media-kit"
        },
        {
            "product_id": "seo-bundle",
            "name": "SEO Master Bundle",
            "price_usd": 39.00,
            "price_idr": 585000,
            "description": "50+ templates, checklists, and Notion workspace",
            "features": ["seo", "templates", "notion"],
            "url": "https://mahalaksmi.web.id/products/seo-bundle"
        },
        {
            "product_id": "whatsapp-marketing",
            "name": "WhatsApp Marketing Kit",
            "price_usd": 29.00,
            "price_idr": 435000,
            "description": "100+ message templates and automation scripts",
            "features": ["whatsapp", "automation", "scripts"],
            "url": "https://mahalaksmi.web.id/products/whatsapp-marketing"
        }
    ]
    
    if market:
        # Filter products by market
        products = products  # In production: filter by market
    
    return {"products": products, "updated_at": datetime.now().isoformat()}


@app.get("/api/v1/nodes")
async def list_nodes():
    """List all registered nodes"""
    return {
        "nodes": [
            {
                "node_id": node_id,
                "name": data["info"]["name"],
                "region": data["info"]["region"],
                "status": data["status"],
                "last_heartbeat": data["last_heartbeat"]
            }
            for node_id, data in NODES_DB.items()
        ]
    }


@app.get("/api/v1/nodes/{node_id}")
async def get_node(node_id: str):
    """Get node details"""
    if node_id not in NODES_DB:
        raise HTTPException(status_code=404, detail="Node not found")
    
    return NODES_DB[node_id]


# ============ DASHBOARD UI ============

@app.get("/")
async def dashboard_ui():
    """Serve dashboard UI"""
    return {
        "service": "KILO SALES NODE - Mission Control",
        "version": "1.0.0",
        "dashboard_url": DASHBOARD_URL,
        "nodes": len(NODES_DB),
        "docs": "/api/docs"
    }


if __name__ == "__main__":
    print("🚀 Starting KILO SALES NODE Dashboard API")
    print(f"📡 Dashboard: {DASHBOARD_URL}")
    print(f"🔒 API: https://mahalaksmi.web.id/api/v1")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        ssl_keyfile="/etc/ssl/node.key",
        ssl_certfile="/etc/ssl/node.crt"
    )
