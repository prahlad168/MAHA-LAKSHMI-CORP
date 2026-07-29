"""
MAHA LAKSHMI CORP - Audit Logging
Comprehensive audit trail for all actions.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class AuditLog:
    """Audit log entry"""
    id: str
    user_id: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_method: Optional[str]
    request_path: Optional[str]
    status_code: Optional[int]
    details: Dict[str, Any]
    created_at: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditLog':
        return cls(**data)


class AuditLogger:
    """Audit logging system"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path
    
    def log_action(
        self,
        action: str,
        user_id: Optional[str] = None,
        resource_type: str = "system",
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_method: Optional[str] = None,
        request_path: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log audit action"""
        log_id = f"audit-{datetime.now().strftime('%Y%m%d%H%M%S')}-{id(self)}"
        
        log_entry = AuditLog(
            id=log_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_path=request_path,
            status_code=status_code,
            details=details or {},
            created_at=datetime.now().isoformat()
        )
        
        # Store in database
        self._store_log(log_entry)
        
        # Also log to application logger
        logger.info(
            f"AUDIT: {action} | user={user_id} | resource={resource_type}:{resource_id} | "
            f"status={status_code} | ip={ip_address}"
        )
        
        return log_id
    
    def _store_log(self, log_entry: AuditLog):
        """Store log in database"""
        try:
            from backend.db.connection import execute_query
            
            execute_query(
                """
                INSERT INTO audit_logs 
                (id, user_id, action, resource_type, resource_id, ip_address, user_agent, 
                 request_method, request_path, status_code, details, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    log_entry.id,
                    log_entry.user_id,
                    log_entry.action,
                    log_entry.resource_type,
                    log_entry.resource_id,
                    log_entry.ip_address,
                    log_entry.user_agent,
                    log_entry.request_method,
                    log_entry.request_path,
                    log_entry.status_code,
                    json.dumps(log_entry.details),
                    log_entry.created_at
                ),
                fetch="none"
            )
        except Exception as e:
            logger.error(f"Failed to store audit log: {e}")
    
    def get_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Get audit logs with filtering"""
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        if action:
            query += " AND action = ?"
            params.append(action)
        if resource_type:
            query += " AND resource_type = ?"
            params.append(resource_type)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        results = execute_query(query, tuple(params), fetch="all")
        return [AuditLog.from_dict(row) for row in results]
    
    def get_user_activity(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get user activity summary"""
        from datetime import timedelta
        since = datetime.now() - timedelta(days=days)
        
        results = execute_query(
            """
            SELECT action, resource_type, COUNT(*) as count, MAX(created_at) as last_occurrence
            FROM audit_logs
            WHERE user_id = ? AND created_at > ?
            GROUP BY action, resource_type
            ORDER BY last_occurrence DESC
            """,
            (user_id, since.isoformat()),
            fetch="all"
        )
        
        return results


# Global audit logger instance
audit_logger = AuditLogger()
