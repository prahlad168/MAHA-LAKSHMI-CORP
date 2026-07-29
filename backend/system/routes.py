"""
MAHA LAKSHMI CORP - System Routes
System health and monitoring endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List
import logging
import psutil
import platform
from datetime import datetime

from backend.db.connection import execute_query
from backend.shared.security import verify_jwt_token

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user"""
    payload = verify_jwt_token(credentials.credentials)
    user = execute_query("SELECT * FROM users WHERE id = ?", (payload["user_id"],), fetch="one")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/health", tags=["System"])
async def get_system_health(current_user: Dict = Depends(get_current_user)):
    """Get system health status"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Database health
        db_size = 0
        try:
            import os
            from pathlib import Path
            db_path = Path(__file__).parent.parent.parent.parent / "data" / "maha_lakshmi.db"
            if db_path.exists():
                db_size = db_path.stat().st_size
        except Exception:
            pass
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_total": memory.total,
                "memory_available": memory.available,
                "disk_usage": disk.percent,
                "disk_total": disk.total,
                "disk_free": disk.free
            },
            "database": {
                "size_bytes": db_size,
                "size_mb": round(db_size / (1024 * 1024), 2)
            }
        }
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system health")


@router.get("/metrics", tags=["System"])
async def get_system_metrics(current_user: Dict = Depends(get_current_user)):
    """Get system metrics"""
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Network
        net_io = psutil.net_io_counters()
        
        # Processes
        processes = len(psutil.pids())
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "count": cpu_count
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent
            },
            "swap": {
                "total": swap.total,
                "used": swap.used,
                "percent": swap.percent
            },
            "network": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv
            },
            "processes": processes
        }
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")


@router.get("/logs", tags=["System"])
async def get_system_logs(
    limit: int = 100,
    level: str = "INFO",
    current_user: Dict = Depends(get_current_user)
):
    """Get system logs"""
    try:
        logs = execute_query(
            """
            SELECT * FROM system_logs
            WHERE level = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (level, limit),
            fetch="all"
        )
        
        return {
            "logs": logs or [],
            "total": len(logs) if logs else 0
        }
    except Exception as e:
        logger.error(f"Failed to fetch logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch logs")
