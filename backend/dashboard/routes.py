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
