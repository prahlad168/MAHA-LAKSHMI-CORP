"""
MAHA LAKSHMI CORP - Extended Dashboard Routes
Home, Revenue, Sales, Finance, Accounting endpoints for CEO Dashboard.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

from backend.db.connection import get_db, execute_query
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


@router.get("/home", tags=["Dashboard"])
async def get_home_dashboard(current_user: Dict = Depends(get_current_user)):
    """Get home dashboard with real revenue and business metrics"""
    try:
        today = datetime.now().date().isoformat()
        month_start = datetime.now().replace(day=1).date().isoformat()
        year_start = datetime.now().replace(month=1, day=1).date().isoformat()
        
        # Revenue metrics
        revenue_today = execute_query(
            """
            SELECT COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE type = 'revenue' AND DATE(created_at) = ?
            """,
            (today,),
            fetch="one"
        )
        
        revenue_month = execute_query(
            """
            SELECT COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE type = 'revenue' AND DATE(created_at) >= ?
            """,
            (month_start,),
            fetch="one"
        )
        
        revenue_year = execute_query(
            """
            SELECT COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE type = 'revenue' AND DATE(created_at) >= ?
            """,
            (year_start,),
            fetch="one"
        )
        
        # Expense metrics
        expense_today = execute_query(
            """
            SELECT COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE type = 'expense' AND DATE(created_at) = ?
            """,
            (today,),
            fetch="one"
        )
        
        # Product metrics
        products_generated = execute_query(
            "SELECT COUNT(*) as count FROM products",
            fetch="one"
        )
        
        products_published = execute_query(
            "SELECT COUNT(*) as count FROM marketplace_products WHERE status = 'published'",
            fetch="one"
        )
        
        products_sold = execute_query(
            "SELECT COUNT(*) as count FROM marketplace_sales",
            fetch="one"
        )
        
        # Marketplace status
        marketplace_accounts = execute_query(
            "SELECT COUNT(*) as count FROM marketplace_accounts WHERE status = 'active'",
            fetch="one"
        )
        
        marketplace_products = execute_query(
            "SELECT COUNT(*) as count FROM marketplace_products",
            fetch="one"
        )
        
        # AI Agents
        ai_agents = execute_query(
            "SELECT COUNT(*) as count FROM ai_workers WHERE status = 'running'",
            fetch="one"
        )
        
        # Pending jobs
        pending_jobs = execute_query(
            "SELECT COUNT(*) as count FROM product_generation_jobs WHERE status = 'queued'",
            fetch="one"
        )
        
        failed_jobs = execute_query(
            "SELECT COUNT(*) as count FROM product_generation_jobs WHERE status = 'failed'",
            fetch="one"
        )
        
        # Recent activity
        recent_activity = execute_query(
            """
            SELECT a.*, u.name as user_name 
            FROM audit_logs a 
            LEFT JOIN users u ON a.user_id = u.id 
            ORDER BY a.created_at DESC 
            LIMIT 10
            """,
            fetch="all"
        )
        
        return {
            "revenue": {
                "today": revenue_today["total"] if revenue_today else 0,
                "month": revenue_month["total"] if revenue_month else 0,
                "year": revenue_year["total"] if revenue_year else 0,
                "expense_today": expense_today["total"] if expense_today else 0,
                "profit_today": (revenue_today["total"] if revenue_today else 0) - (expense_today["total"] if expense_today else 0)
            },
            "products": {
                "generated": products_generated["count"] if products_generated else 0,
                "published": products_published["count"] if products_published else 0,
                "sold": products_sold["count"] if products_sold else 0
            },
            "marketplace": {
                "accounts": marketplace_accounts["count"] if marketplace_accounts else 0,
                "products": marketplace_products["count"] if marketplace_products else 0
            },
            "ai_agents": {
                "running": ai_agents["count"] if ai_agents else 0
            },
            "jobs": {
                "pending": pending_jobs["count"] if pending_jobs else 0,
                "failed": failed_jobs["count"] if failed_jobs else 0
            },
            "recent_activity": recent_activity or []
        }
    
    except Exception as e:
        logger.error(f"Failed to load home dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to load dashboard data")


@router.get("/revenue", tags=["Dashboard"])
async def get_revenue_dashboard(current_user: Dict = Depends(get_current_user)):
    """Get revenue dashboard with charts data"""
    try:
        # Daily revenue for last 30 days
        daily_revenue = execute_query(
            """
            SELECT 
                DATE(created_at) as date,
                SUM(amount) as total,
                COUNT(*) as transactions
            FROM transactions
            WHERE type = 'revenue' 
                AND created_at >= DATE('now', '-30 days')
            GROUP BY DATE(created_at)
            ORDER BY date ASC
            """,
            fetch="all"
        )
        
        # Revenue by marketplace
        marketplace_revenue = execute_query(
            """
            SELECT 
                m.provider as marketplace,
                SUM(t.amount) as total,
                COUNT(*) as transactions
            FROM transactions t
            LEFT JOIN marketplace_sales ms ON t.reference_id = ms.gumroad_purchase_id
            LEFT JOIN marketplace_accounts m ON ms.account_id = m.id
            WHERE t.type = 'revenue' 
                AND t.created_at >= DATE('now', '-30 days')
            GROUP BY m.provider
            ORDER BY total DESC
            """,
            fetch="all"
        )
        
        # Revenue by product
        product_revenue = execute_query(
            """
            SELECT 
                p.name as product_name,
                SUM(t.amount) as total,
                COUNT(*) as sales
            FROM transactions t
            LEFT JOIN products p ON json_extract(t.metadata, '$.product_id') = p.id
            WHERE t.type = 'revenue' 
                AND t.created_at >= DATE('now', '-30 days')
            GROUP BY p.name
            ORDER BY total DESC
            LIMIT 10
            """,
            fetch="all"
        )
        
        return {
            "daily_revenue": daily_revenue or [],
            "marketplace_revenue": marketplace_revenue or [],
            "product_revenue": product_revenue or [],
            "period": "last_30_days",
            "currency": "USD"
        }
    
    except Exception as e:
        logger.error(f"Failed to load revenue dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to load revenue data")


@router.get("/finance", tags=["Dashboard"])
async def get_finance_dashboard(current_user: Dict = Depends(get_current_user)):
    """Get finance dashboard"""
    try:
        # Cash flow
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
        
        # Expense breakdown
        expenses = execute_query(
            """
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE type = 'expense' 
                AND created_at >= DATE('now', '-30 days')
            GROUP BY category
            ORDER BY total DESC
            """,
            fetch="all"
        )
        
        # Revenue breakdown
        revenues = execute_query(
            """
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE type = 'revenue' 
                AND created_at >= DATE('now', '-30 days')
            GROUP BY category
            ORDER BY total DESC
            """,
            fetch="all"
        )
        
        return {
            "cash_flow": cash_flow or [],
            "expenses": expenses or [],
            "revenues": revenues or [],
            "period": "last_30_days"
        }
    
    except Exception as e:
        logger.error(f"Failed to load finance dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to load finance data")


@router.get("/sales", tags=["Dashboard"])
async def get_sales_dashboard(current_user: Dict = Depends(get_current_user)):
    """Get sales dashboard"""
    try:
        # Sales pipeline
        pipeline = execute_query(
            """
            SELECT status, COUNT(*) as count, COALESCE(SUM(value), 0) as total
            FROM deals
            GROUP BY status
            """,
            fetch="all"
        )
        
        # Recent deals
        recent_deals = execute_query(
            """
            SELECT d.*, c.name as customer_name
            FROM deals d
            LEFT JOIN customers c ON d.customer_id = c.id
            ORDER BY d.created_at DESC
            LIMIT 20
            """,
            fetch="all"
        )
        
        return {
            "pipeline": pipeline or [],
            "recent_deals": recent_deals or []
        }
    
    except Exception as e:
        logger.error(f"Failed to load sales dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to load sales data")


@router.get("/accounting", tags=["Dashboard"])
async def get_accounting_dashboard(current_user: Dict = Depends(get_current_user)):
    """Get accounting dashboard"""
    try:
        # Recent accounting entries
        entries = execute_query(
            """
            SELECT * FROM accounting_entries
            ORDER BY entry_date DESC
            LIMIT 50
            """,
            fetch="all"
        )
        
        # Account balances
        balances = execute_query(
            """
            SELECT account_code, account_name, entry_type, SUM(amount) as total
            FROM accounting_entries
            GROUP BY account_code, account_name, entry_type
            ORDER BY account_code
            """,
            fetch="all"
        )
        
        return {
            "entries": entries or [],
            "balances": balances or [],
            "message": "No Data" if not entries else None
        }
    
    except Exception as e:
        logger.error(f"Failed to load accounting dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to load accounting data")


@router.get("/reports/financial", tags=["Dashboard"])
async def get_financial_reports(
    period: str = "month",
    current_user: Dict = Depends(get_current_user)
):
    """Get financial reports"""
    try:
        if period == "week":
            date_filter = "AND created_at >= DATE('now', '-7 days')"
        elif period == "month":
            date_filter = "AND created_at >= DATE('now', '-30 days')"
        elif period == "year":
            date_filter = "AND created_at >= DATE('now', '-1 year')"
        else:
            date_filter = ""
        
        # Revenue summary
        revenue = execute_query(
            f"""
            SELECT 
                SUM(amount) as total,
                COUNT(*) as transactions,
                AVG(amount) as average
            FROM transactions
            WHERE type = 'revenue' {date_filter}
            """,
            fetch="one"
        )
        
        # Expense summary
        expenses = execute_query(
            f"""
            SELECT 
                SUM(amount) as total,
                COUNT(*) as transactions,
                AVG(amount) as average
            FROM transactions
            WHERE type = 'expense' {date_filter}
            """,
            fetch="one"
        )
        
        # Refund summary
        refunds = execute_query(
            f"""
            SELECT 
                SUM(ABS(amount)) as total,
                COUNT(*) as count
            FROM transactions
            WHERE type = 'refund' {date_filter}
            """,
            fetch="one"
        )
        
        return {
            "period": period,
            "revenue": revenue or {"total": 0, "transactions": 0, "average": 0},
            "expenses": expenses or {"total": 0, "transactions": 0, "average": 0},
            "refunds": refunds or {"total": 0, "count": 0},
            "profit": (revenue["total"] if revenue else 0) - (expenses["total"] if expenses else 0)
        }
    
    except Exception as e:
        logger.error(f"Failed to load financial reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to load financial reports")
