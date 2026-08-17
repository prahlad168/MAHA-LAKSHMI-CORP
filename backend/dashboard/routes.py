"""
MAHA LAKSHMI CORP - Dashboard Routes
Additional dashboard-specific routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List
import json
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


@router.get("/reports", tags=["Dashboard"])
async def get_reports(current_user: Dict = Depends(get_current_user)):
    """Get available reports"""
    try:
        reports = execute_query(
            """
            SELECT * FROM reports
            ORDER BY created_at DESC
            LIMIT 20
            """,
            fetch="all"
        )
        
        return {
            "reports": reports or [],
            "total": len(reports) if reports else 0
        }
    except Exception as e:
        logger.error(f"Failed to fetch reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch reports")


@router.get("/reports/{report_id}", tags=["Dashboard"])
async def get_report(report_id: str, current_user: Dict = Depends(get_current_user)):
    """Get specific report"""
    try:
        report = execute_query(
            "SELECT * FROM reports WHERE id = ?",
            (report_id,),
            fetch="one"
        )
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch report: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch report")


@router.get("/knowledge", tags=["Dashboard"])
async def get_knowledge_base(current_user: Dict = Depends(get_current_user)):
    """Get knowledge base entries"""
    try:
        documents = execute_query(
            """
            SELECT category, COUNT(*) as count
            FROM knowledge_documents
            GROUP BY category
            """,
            fetch="all"
        )
        
        return {
            "documents": documents or [],
            "total": sum(d["count"] for d in documents) if documents else 0
        }
    except Exception as e:
        logger.error(f"Failed to fetch knowledge base: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch knowledge base")


@router.get("/notifications", tags=["Dashboard"])
async def get_notifications(
    limit: int = 50,
    current_user: Dict = Depends(get_current_user)
):
    """Get user notifications"""
    try:
        notifications = execute_query(
            """
            SELECT * FROM notifications
            WHERE user_id = ? OR user_id IS NULL
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (current_user["id"], limit),
            fetch="all"
        )
        
        unread_count = execute_query(
            "SELECT COUNT(*) as count FROM notifications WHERE user_id = ? AND read = 0",
            (current_user["id"],),
            fetch="one"
        )
        
        return {
            "notifications": notifications or [],
            "unread_count": unread_count["count"] if unread_count else 0,
            "total": len(notifications) if notifications else 0
        }
    except Exception as e:
        logger.error(f"Failed to fetch notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch notifications")


@router.post("/notifications/{notification_id}/read", tags=["Dashboard"])
async def mark_notification_read(
    notification_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Mark notification as read"""
    try:
        execute_query(
            "UPDATE notifications SET read = 1, read_at = ? WHERE id = ? AND user_id = ?",
            (datetime.now().isoformat(), notification_id, current_user["id"]),
            fetch="none"
        )
        
        return {"message": "Notification marked as read"}
    except Exception as e:
        logger.error(f"Failed to mark notification as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to update notification")


@router.get("/settings", tags=["Dashboard"])
async def get_user_settings(current_user: Dict = Depends(get_current_user)):
    """Get user settings"""
    try:
        settings = execute_query(
            "SELECT * FROM user_settings WHERE user_id = ?",
            (current_user["id"],),
            fetch="one"
        )
        
        if not settings:
            # Create default settings
            settings_id = f"settings-{current_user['id']}"
            now = datetime.now().isoformat()
            execute_query(
                """
                INSERT INTO user_settings (id, user_id, theme, notifications, created_at, updated_at)
                VALUES (?, ?, 'dark', 1, ?, ?)
                """,
                (settings_id, current_user["id"], now, now),
                fetch="none"
            )
            settings = {
                "id": settings_id,
                "user_id": current_user["id"],
                "theme": "dark",
                "notifications": 1
            }
        
        return settings
    except Exception as e:
        logger.error(f"Failed to fetch settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch settings")


@router.put("/settings", tags=["Dashboard"])
async def update_user_settings(
    settings_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Update user settings"""
    try:
        # Update or insert settings
        execute_query(
            """
            INSERT INTO user_settings (user_id, theme, notifications, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                theme = excluded.theme,
                notifications = excluded.notifications,
                updated_at = excluded.updated_at
            """,
            (
                current_user["id"],
                settings_data.get("theme", "dark"),
                settings_data.get("notifications", 1),
                datetime.now().isoformat()
            ),
            fetch="none"
        )
        
        return {"message": "Settings updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update settings")


@router.get("/products", tags=["Dashboard"])
async def get_dashboard_products(current_user: Dict = Depends(get_current_user)):
    """Get products dashboard data"""
    try:
        products = execute_query(
            "SELECT * FROM products ORDER BY created_at DESC LIMIT 50",
            fetch="all"
        )
        return {
            "products": products or [],
            "total": len(products) if products else 0
        }
    except Exception as e:
        logger.error(f"Failed to fetch products: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch products")


@router.get("/ai-factory", tags=["Dashboard"])
async def get_dashboard_ai_factory(current_user: Dict = Depends(get_current_user)):
    """Get AI factory dashboard data"""
    try:
        workers = execute_query(
            "SELECT * FROM ai_workers ORDER BY created_at DESC LIMIT 50",
            fetch="all"
        )
        jobs = execute_query(
            "SELECT * FROM product_generation_jobs ORDER BY created_at DESC LIMIT 20",
            fetch="all"
        )
        return {
            "workers": workers or [],
            "jobs": jobs or [],
            "total_workers": len(workers) if workers else 0,
            "total_jobs": len(jobs) if jobs else 0
        }
    except Exception as e:
        logger.error(f"Failed to fetch AI factory data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch AI factory data")


@router.get("/marketplace", tags=["Dashboard"])
async def get_dashboard_marketplace(current_user: Dict = Depends(get_current_user)):
    """Get marketplace dashboard data"""
    try:
        accounts = execute_query(
            "SELECT * FROM marketplace_accounts ORDER BY created_at DESC LIMIT 50",
            fetch="all"
        )
        publications = execute_query(
            "SELECT * FROM marketplace_publications ORDER BY created_at DESC LIMIT 50",
            fetch="all"
        )
        sales = execute_query(
            "SELECT * FROM marketplace_sales ORDER BY created_at DESC LIMIT 50",
            fetch="all"
        )
        return {
            "accounts": accounts or [],
            "publications": publications or [],
            "sales": sales or [],
            "total_accounts": len(accounts) if accounts else 0,
            "total_publications": len(publications) if publications else 0,
            "total_sales": len(sales) if sales else 0
        }
    except Exception as e:
        logger.error(f"Failed to fetch marketplace data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch marketplace data")


@router.get("/marketing", tags=["Dashboard"])
async def get_dashboard_marketing(current_user: Dict = Depends(get_current_user)):
    """Get marketing dashboard data"""
    try:
        campaigns = execute_query(
            "SELECT * FROM marketing_campaigns ORDER BY created_at DESC LIMIT 50",
            fetch="all"
        )
        content = execute_query(
            "SELECT * FROM content_assets ORDER BY created_at DESC LIMIT 50",
            fetch="all"
        )
        ab_tests = execute_query(
            "SELECT * FROM ab_tests ORDER BY created_at DESC LIMIT 20",
            fetch="all"
        )
        return {
            "campaigns": campaigns or [],
            "content": content or [],
            "ab_tests": ab_tests or [],
            "total_campaigns": len(campaigns) if campaigns else 0,
            "total_content": len(content) if content else 0
        }
    except Exception as e:
        logger.error(f"Failed to fetch marketing data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch marketing data")


@router.get("/automation", tags=["Dashboard"])
async def get_dashboard_automation(current_user: Dict = Depends(get_current_user)):
    """Get automation dashboard data"""
    try:
        workflows = execute_query(
            "SELECT * FROM automation_workflows ORDER BY created_at DESC LIMIT 50",
            fetch="all"
        )
        optimizations = execute_query(
            "SELECT * FROM optimizations ORDER BY created_at DESC LIMIT 50",
            fetch="all"
        )
        return {
            "workflows": workflows or [],
            "optimizations": optimizations or [],
            "total_workflows": len(workflows) if workflows else 0,
            "total_optimizations": len(optimizations) if optimizations else 0
        }
    except Exception as e:
        logger.error(f"Failed to fetch automation data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch automation data")


@router.get("/optimization", tags=["Dashboard"])
async def get_dashboard_optimization(current_user: Dict = Depends(get_current_user)):
    """Get optimization dashboard data"""
    try:
        optimizations = execute_query(
            "SELECT * FROM optimizations ORDER BY created_at DESC LIMIT 50",
            fetch="all"
        )
        experiments = execute_query(
            "SELECT * FROM experiments ORDER BY created_at DESC LIMIT 20",
            fetch="all"
        )
        insights = execute_query(
            "SELECT * FROM insights ORDER BY created_at DESC LIMIT 20",
            fetch="all"
        )
        return {
            "optimizations": optimizations or [],
            "experiments": experiments or [],
            "insights": insights or [],
            "total_optimizations": len(optimizations) if optimizations else 0
        }
    except Exception as e:
        logger.error(f"Failed to fetch optimization data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch optimization data")
    except Exception as e:
        logger.error(f"Failed to update settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update settings")
