"""
MAHA LAKSHMI CORP - Sales Routes
Sales automation and CRM endpoints.
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


@router.get("/leads", tags=["Sales"])
async def get_leads(
    limit: int = 50,
    offset: int = 0,
    current_user: Dict = Depends(get_current_user)
):
    """Get sales leads"""
    try:
        leads = execute_query(
            """
            SELECT * FROM leads
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
            fetch="all"
        )
        
        total = execute_query(
            "SELECT COUNT(*) as count FROM leads",
            fetch="one"
        )
        
        return {
            "leads": leads or [],
            "total": total["count"] if total else 0,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Failed to fetch leads: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch leads")


@router.get("/pipeline", tags=["Sales"])
async def get_sales_pipeline(current_user: Dict = Depends(get_current_user)):
    """Get sales pipeline"""
    try:
        pipeline = execute_query(
            """
            SELECT status, COUNT(*) as count, COALESCE(SUM(value), 0) as total
            FROM deals
            GROUP BY status
            """,
            fetch="all"
        )
        
        return {
            "pipeline": pipeline or [],
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to fetch pipeline: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch pipeline")


@router.get("/deals", tags=["Sales"])
async def get_deals(
    limit: int = 50,
    current_user: Dict = Depends(get_current_user)
):
    """Get recent deals"""
    try:
        deals = execute_query(
            """
            SELECT d.*, c.name as customer_name
            FROM deals d
            LEFT JOIN customers c ON d.customer_id = c.id
            ORDER BY d.created_at DESC
            LIMIT ?
            """,
            (limit,),
            fetch="all"
        )
        
        return {
            "deals": deals or [],
            "total": len(deals) if deals else 0
        }
    except Exception as e:
        logger.error(f"Failed to fetch deals: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch deals")
