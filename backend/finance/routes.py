"""
MAHA LAKSHMI CORP - Finance Routes
Finance and accounting dashboard endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

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


@router.get("/overview", tags=["Finance"])
async def get_finance_overview(current_user: Dict = Depends(get_current_user)):
    """Get finance overview"""
    try:
        today = datetime.now().date().isoformat()
        month_start = datetime.now().replace(day=1).date().isoformat()
        
        # Revenue
        revenue_today = execute_query(
            "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE type = 'revenue' AND DATE(created_at) = ?",
            (today,),
            fetch="one"
        )
        
        revenue_month = execute_query(
            "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE type = 'revenue' AND DATE(created_at) >= ?",
            (month_start,),
            fetch="one"
        )
        
        # Expenses
        expense_today = execute_query(
            "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE type = 'expense' AND DATE(created_at) = ?",
            (today,),
            fetch="one"
        )
        
        expense_month = execute_query(
            "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE type = 'expense' AND DATE(created_at) >= ?",
            (month_start,),
            fetch="one"
        )
        
        # Cash balance
        cash_balance = execute_query(
            "SELECT COALESCE(SUM(CASE WHEN type = 'revenue' THEN amount ELSE -amount END), 0) as balance FROM transactions",
            fetch="one"
        )
        
        return {
            "revenue": {
                "today": revenue_today["total"] if revenue_today else 0,
                "month": revenue_month["total"] if revenue_month else 0
            },
            "expenses": {
                "today": expense_today["total"] if expense_today else 0,
                "month": expense_month["total"] if expense_month else 0
            },
            "cash_balance": cash_balance["balance"] if cash_balance else 0,
            "profit_today": (revenue_today["total"] if revenue_today else 0) - (expense_today["total"] if expense_today else 0),
            "profit_month": (revenue_month["total"] if revenue_month else 0) - (expense_month["total"] if expense_month else 0)
        }
    
    except Exception as e:
        logger.error(f"Failed to load finance overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to load finance data")


@router.get("/transactions", tags=["Finance"])
async def get_transactions(
    limit: int = 100,
    offset: int = 0,
    current_user: Dict = Depends(get_current_user)
):
    """Get transactions"""
    try:
        transactions = execute_query(
            """
            SELECT * FROM transactions
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
            fetch="all"
        )
        
        total = execute_query(
            "SELECT COUNT(*) as count FROM transactions",
            fetch="one"
        )
        
        return {
            "transactions": transactions or [],
            "total": total["count"] if total else 0,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Failed to fetch transactions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch transactions")


@router.get("/cash-flow", tags=["Finance"])
async def get_cash_flow(current_user: Dict = Depends(get_current_user)):
    """Get cash flow data"""
    try:
        cash_flow = execute_query(
            """
            SELECT 
                DATE(created_at) as date,
                SUM(CASE WHEN type = 'revenue' THEN amount ELSE -amount END) as net
            FROM transactions
            WHERE created_at >= DATE('now', '-30 days')
            GROUP BY DATE(created_at)
            ORDER BY date ASC
            """,
            fetch="all"
        )
        
        return {
            "cash_flow": cash_flow or [],
            "period": "last_30_days"
        }
    except Exception as e:
        logger.error(f"Failed to fetch cash flow: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch cash flow")
