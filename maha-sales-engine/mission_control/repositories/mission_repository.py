#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Repositories

Data access layer for the Mission Control system.
"""

import sys
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.database import DatabaseManager
from shared.logging_utils import get_logger

logger = get_logger("maha-sales-engine.mission-control.repositories")


@dataclass
class MissionRecord:
    """Mission Control record data structure"""
    mission_id: str
    name: str
    status: str
    created_at: str
    updated_at: str
    config: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None


class MissionRepository:
    """
    Repository for Mission Control data access.
    
    Provides CRUD operations for mission control records
    and abstracts database interactions.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize mission repository.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        self.logger = get_logger("maha-sales-engine.mission-control.repository")
        self._initialize_schema()
    
    def _initialize_schema(self) -> None:
        """Initialize database schema for mission control"""
        try:
            schema_path = Path(__file__).parent.parent.parent / "mission_control" / "db" / "schema.sql"
            if schema_path.exists():
                with open(schema_path) as f:
                    schema = f.read()
                self.db.create_tables(schema)
                self.logger.info("Mission Control schema initialized")
            else:
                self.logger.warning("Schema file not found, creating basic tables")
                self._create_basic_schema()
        except Exception as e:
            self.logger.error(f"Failed to initialize schema: {e}")
            raise
    
    def _create_basic_schema(self) -> None:
        """Create basic mission control tables"""
        create_tables = """
        CREATE TABLE IF NOT EXISTS missions (
            mission_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            config TEXT NOT NULL,
            result TEXT
        );
        
        CREATE TABLE IF NOT EXISTS mission_metrics (
            metric_id TEXT PRIMARY KEY,
            mission_id TEXT NOT NULL,
            name TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            tags TEXT,
            FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
        );
        
        CREATE TABLE IF NOT EXISTS mission_alerts (
            alert_id TEXT PRIMARY KEY,
            mission_id TEXT NOT NULL,
            severity TEXT NOT NULL,
            message TEXT NOT NULL,
            source TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            acknowledged INTEGER DEFAULT 0,
            metadata TEXT,
            FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
        );
        
        CREATE TABLE IF NOT EXISTS mission_audit (
            audit_id TEXT PRIMARY KEY,
            mission_id TEXT NOT NULL,
            action TEXT NOT NULL,
            user_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            details TEXT,
            FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status);
        CREATE INDEX IF NOT EXISTS idx_missions_created ON missions(created_at);
        CREATE INDEX IF NOT EXISTS idx_metrics_mission ON mission_metrics(mission_id);
        CREATE INDEX IF NOT EXISTS idx_alerts_mission ON mission_alerts(mission_id);
        CREATE INDEX IF NOT EXISTS idx_audit_mission ON mission_audit(mission_id);
        """
        self.db.create_tables(create_tables)
        self.logger.info("Basic mission control schema created")
    
    def create_mission(self, mission: MissionRecord) -> bool:
        """
        Create a new mission record.
        
        Args:
            mission: Mission record to create
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT INTO missions (mission_id, name, status, created_at, updated_at, config, result)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            self.db.execute(
                query,
                (
                    mission.mission_id,
                    mission.name,
                    mission.status,
                    mission.created_at,
                    mission.updated_at,
                    json.dumps(mission.config),
                    json.dumps(mission.result) if mission.result else None
                )
            )
            self.logger.info(f"Mission created: {mission.mission_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create mission {mission.mission_id}: {e}")
            return False
    
    def get_mission(self, mission_id: str) -> Optional[MissionRecord]:
        """
        Get mission by ID.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            Mission record or None if not found
        """
        try:
            query = "SELECT * FROM missions WHERE mission_id = ?"
            result = self.db.execute(query, (mission_id,))
            if result:
                row = result[0]
                return MissionRecord(
                    mission_id=row["mission_id"],
                    name=row["name"],
                    status=row["status"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    config=json.loads(row["config"]) if row["config"] else {},
                    result=json.loads(row["result"]) if row["result"] else None
                )
            return None
        except Exception as e:
            self.logger.error(f"Failed to get mission {mission_id}: {e}")
            return None
    
    def update_mission_status(self, mission_id: str, status: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update mission status and optional result.
        
        Args:
            mission_id: Mission identifier
            status: New status
            result: Optional result data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                UPDATE missions 
                SET status = ?, updated_at = ?, result = ?
                WHERE mission_id = ?
            """
            self.db.execute(
                query,
                (status, datetime.now().isoformat(), json.dumps(result) if result else None, mission_id)
            )
            self.logger.info(f"Mission {mission_id} updated to status: {status}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update mission {mission_id}: {e}")
            return False
    
    def list_missions(self, status: Optional[str] = None, limit: int = 100) -> List[MissionRecord]:
        """
        List missions with optional status filter.
        
        Args:
            status: Optional status filter
            limit: Maximum number of results
            
        Returns:
            List of mission records
        """
        try:
            if status:
                query = "SELECT * FROM missions WHERE status = ? ORDER BY created_at DESC LIMIT ?"
                result = self.db.execute(query, (status, limit))
            else:
                query = "SELECT * FROM missions ORDER BY created_at DESC LIMIT ?"
                result = self.db.execute(query, (limit,))
            
            missions = []
            for row in result:
                missions.append(MissionRecord(
                    mission_id=row["mission_id"],
                    name=row["name"],
                    status=row["status"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    config=json.loads(row["config"]) if row["config"] else {},
                    result=json.loads(row["result"]) if row["result"] else None
                ))
            return missions
        except Exception as e:
            self.logger.error(f"Failed to list missions: {e}")
            return []
    
    def record_metric(self, metric: MissionMetric) -> bool:
        """
        Record a metric for a mission.
        
        Args:
            metric: Metric to record
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT INTO mission_metrics (metric_id, mission_id, name, value, unit, timestamp, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            self.db.execute(
                query,
                (
                    metric.metric_id,
                    metric.metric_id.split("-")[0],
                    metric.name,
                    metric.value,
                    metric.unit,
                    metric.timestamp,
                    json.dumps(metric.tags)
                )
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to record metric {metric.metric_id}: {e}")
            return False
    
    def record_alert(self, alert: MissionAlert) -> bool:
        """
        Record an alert for a mission.
        
        Args:
            alert: Alert to record
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT INTO mission_alerts (alert_id, mission_id, severity, message, source, timestamp, acknowledged, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.db.execute(
                query,
                (
                    alert.alert_id,
                    alert.alert_id.split("-")[0],
                    alert.severity,
                    alert.message,
                    alert.source,
                    alert.timestamp,
                    1 if alert.acknowledged else 0,
                    json.dumps(alert.metadata)
                )
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to record alert {alert.alert_id}: {e}")
            return False
    
    def record_audit(self, mission_id: str, action: str, user_id: str, details: Optional[Dict[str, Any]] = None) -> bool:
        """
        Record an audit entry for a mission.
        
        Args:
            mission_id: Mission identifier
            action: Action performed
            user_id: User who performed the action
            details: Optional details
            
        Returns:
            True if successful, False otherwise
        """
        try:
            audit_id = f"audit-{int(time.time() * 1000)}-{secrets.token_hex(4)}"
            query = """
                INSERT INTO mission_audit (audit_id, mission_id, action, user_id, timestamp, details)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            self.db.execute(
                query,
                (
                    audit_id,
                    mission_id,
                    action,
                    user_id,
                    datetime.now().isoformat(),
                    json.dumps(details) if details else None
                )
            )
            self.logger.info(f"Audit recorded for mission {mission_id}: {action}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to record audit for mission {mission_id}: {e}")
            return False
    
    def list_pending_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List pending alerts that need dispatch.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of pending alert dictionaries
        """
        try:
            query = """
                SELECT * FROM mission_alerts 
                WHERE acknowledged = 0 
                ORDER BY timestamp DESC 
                LIMIT ?
            """
            results = self.db.execute(query, (limit,))
            
            alerts = []
            for row in results:
                alerts.append({
                    "alert_id": row["alert_id"],
                    "mission_id": row["mission_id"],
                    "severity": row["severity"],
                    "message": row["message"],
                    "source": row["source"],
                    "timestamp": row["timestamp"],
                    "acknowledged": bool(row["acknowledged"]),
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                })
            return alerts
        except Exception as e:
            self.logger.error(f"Failed to list pending alerts: {e}")
            return []
    
    def get_mission_metrics(self, mission_id: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get metrics for a mission.
        
        Args:
            mission_id: Mission identifier
            limit: Maximum number of metrics to return
            
        Returns:
            List of metric dictionaries
        """
        try:
            query = """
                SELECT * FROM mission_metrics 
                WHERE mission_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """
            results = self.db.execute(query, (mission_id, limit))
            
            metrics = []
            for row in results:
                metrics.append({
                    "metric_id": row["metric_id"],
                    "mission_id": row["mission_id"],
                    "name": row["name"],
                    "value": row["value"],
                    "unit": row["unit"],
                    "timestamp": row["timestamp"],
                    "tags": json.loads(row["tags"]) if row["tags"] else {}
                })
            return metrics
        except Exception as e:
            self.logger.error(f"Failed to get metrics for mission {mission_id}: {e}")
            return []
