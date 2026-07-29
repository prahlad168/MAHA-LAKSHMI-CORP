"""
MAHA LAKSHMI CORP - AI Factory Routes
AI Factory and automation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List
import logging

from backend.db.connection import get_db, execute_query
from backend.shared.security import verify_jwt_token
from backend.shared.rate_limiter import rate_limit

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


@router.get("/status", tags=["AI Factory"])
async def get_ai_factory_status(current_user: Dict = Depends(get_current_user)):
    """Get AI Factory status"""
    try:
        # Queue stats
        queue = execute_query(
            """
            SELECT status, COUNT(*) as count
            FROM product_generation_jobs
            GROUP BY status
            """,
            fetch="all"
        )
        
        # Workers
        workers = execute_query(
            """
            SELECT worker_id, status, last_heartbeat, tasks_processed
            FROM ai_workers
            ORDER BY last_heartbeat DESC
            """,
            fetch="all"
        )
        
        return {
            "queue": queue or [],
            "workers": workers or [],
            "status": "operational"
        }
    except Exception as e:
        logger.error(f"Failed to fetch AI factory status: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch status")


@router.get("/queue", tags=["AI Factory"])
async def get_ai_queue(current_user: Dict = Depends(get_current_user)):
    """Get AI generation queue"""
    try:
        jobs = execute_query(
            """
            SELECT * FROM product_generation_jobs
            ORDER BY created_at DESC
            LIMIT 50
            """,
            fetch="all"
        )
        
        return {
            "jobs": jobs or [],
            "total": len(jobs) if jobs else 0
        }
    except Exception as e:
        logger.error(f"Failed to fetch AI queue: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch queue")


@router.get("/workers", tags=["AI Factory"])
async def get_ai_workers(current_user: Dict = Depends(get_current_user)):
    """Get AI workers status"""
    try:
        workers = execute_query(
            """
            SELECT * FROM ai_workers
            ORDER BY last_heartbeat DESC
            """,
            fetch="all"
        )
        
        return {
            "workers": workers or [],
            "total": len(workers) if workers else 0
        }
    except Exception as e:
        logger.error(f"Failed to fetch AI workers: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch workers")
