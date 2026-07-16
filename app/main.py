#!/usr/bin/env python3
"""
MAHA LAKSHMI AIOS v2.4.0 - FastAPI Application
===============================================
Alpha Gaurangga Integrated Command Bridge API

This module exposes consolidated endpoints for the frontend
to access the unified operations matrix.

Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.gaurangga_bridge import (
    GauranggaCommandBridge,
    ConsolidatedStatus,
    SyncResult
)

# ============================================================================
# APP CONFIGURATION
# ============================================================================

app = FastAPI(
    title="MAHA LAKSHMI AIOS",
    description="Alpha Gaurangga Integrated Command Bridge API v2.4.0",
    version="2.4.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize bridge
bridge = GauranggaCommandBridge()

# ============================================================================
# RESPONSE MODELS
# ============================================================================

class StatusResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    data: Dict[str, Any]
    message: str = ""

class SyncResponse(BaseModel):
    """Sync operation response"""
    success: bool
    message: str
    audit_log_id: str = None
    daily_report_path: str = None

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/")
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MAHA LAKSHMI AIOS",
        "version": "2.4.0",
        "bridge": "ALPHA GAURANGGA COMMAND BRIDGE"
    }

@app.get("/api/health")
async def api_health():
    """API health check"""
    return {"status": "ok", "api_version": "v1"}

# ============================================================================
# ALPHA GAURANGGA ENDPOINTS
# ============================================================================

@app.get("/api/alpha/gaurangga/consolidated-status", response_model=StatusResponse)
async def get_consolidated_status():
    """
    GET /api/alpha/gaurangga/consolidated-status
    
    Returns the combined operations matrix:
    - Maha Laksmi Offline Ledger (Enterprise Hub)
    - Maha AIOS Live Revenue (Digital Core)
    
    Includes:
    - Enterprise hub status (offline invoices, wire transfers, procurement)
    - Digital core status (Midtrans, SaaS subscriptions, live connections)
    - Total consolidated revenue
    - New 80/20 distribution calculation (CEO/Ops)
    """
    try:
        status = bridge.get_consolidated_status()
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "timestamp": status.timestamp,
                "version": status.version,
                "enterprise_hub": status.enterprise_hub,
                "digital_core": status.digital_core,
                "total_revenue": status.total_revenue,
                "distribution": status.distribution,
                "ceo_share": status.ceo_share,
                "ops_share": status.ops_share,
                "sync_status": status.sync_status
            },
            "message": "Consolidated status retrieved successfully"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/alpha/gaurangga/sync", response_model=SyncResponse)
async def execute_unified_sync():
    """
    POST /api/alpha/gaurangga/sync
    
    Execute unified sync operation:
    - Aggregates data from both domains
    - Calculates 80/20 distribution
    - Writes synchronized daily report
    - Logs to audit trail
    
    Returns:
    - success: bool
    - message: str
    - audit_log_id: str
    - daily_report_path: str
    """
    try:
        result = bridge.execute_unified_sync()
        
        return JSONResponse(content={
            "success": result.success,
            "message": result.message,
            "audit_log_id": result.audit_log_id,
            "daily_report_path": result.daily_report_path
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alpha/gaurangga/sync-status")
async def get_sync_status():
    """
    GET /api/alpha/gaurangga/sync-status
    
    Quick status check for monitoring:
    - Node health status
    - Total revenue
    - Connection status
    """
    try:
        status = bridge.get_sync_status()
        return JSONResponse(content=status)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alpha/gaurangga/nodes")
async def get_nodes_status():
    """
    GET /api/alpha/gaurangga/nodes
    
    Get detailed status of both operational nodes:
    - Enterprise Hub (Maha Laksmi)
    - Digital Core (Maha AIOS)
    """
    try:
        enterprise = bridge.enterprise_hub.fetch_all()
        digital = bridge.digital_core.fetch_all()
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "enterprise_hub": {
                    "status": "ONLINE",
                    "offline_revenue": enterprise.calculate_offline_revenue(),
                    "ledger_entries": len(enterprise.offline_ledger_entries),
                    "wire_transfers": len(enterprise.manual_wire_transfers),
                    "procurement_pipelines": len(enterprise.procurement_pipelines),
                    "last_sync": enterprise.last_sync
                },
                "digital_core": {
                    "status": "ONLINE",
                    "production_revenue": digital.production_revenue,
                    "midtrans_transactions": len(digital.midtrans_webhooks),
                    "saas_subscriptions": len(digital.saas_subscriptions),
                    "live_connections": len(digital.live_client_connections),
                    "last_sync": digital.last_sync
                }
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
