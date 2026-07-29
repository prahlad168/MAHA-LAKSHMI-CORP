#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Optimization Database Manager
Database operations for optimization engine.
"""

import os
import sys
import json
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.optimization.db")


class OptimizationDatabaseManager:
    """Database manager for optimization engine"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure optimization tables exist"""
        schema_path = Path(__file__).parent / "schema.sql"
        if schema_path.exists():
            schema = schema_path.read_text()
            self.db.execute(schema)
            logger.info("Optimization tables created/verified")
    
    def save_optimization_job(self, job_data: Dict[str, Any]) -> bool:
        """Save optimization job"""
        try:
            query = """
                INSERT OR REPLACE INTO optimization_jobs 
                (job_id, optimization_id, category, target_metric, current_value, expected_value, mode, status, confidence, risk_score, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                job_data.get("job_id"),
                job_data.get("optimization_id"),
                job_data.get("category"),
                job_data.get("target_metric"),
                job_data.get("current_value"),
                job_data.get("expected_value"),
                job_data.get("mode"),
                job_data.get("status"),
                job_data.get("confidence"),
                job_data.get("risk_score"),
                job_data.get("created_at"),
                job_data.get("updated_at"),
                json.dumps(job_data.get("metadata", {}))
            )
            self.db.execute(query, params)
            return True
        except Exception as e:
            logger.error(f"Failed to save optimization job: {e}")
            return False
    
    def save_recommendation(self, recommendation: Dict[str, Any]) -> bool:
        """Save recommendation"""
        try:
            query = """
                INSERT OR REPLACE INTO recommendations 
                (recommendation_id, optimization_id, category, title, description, evidence, expected_impact, confidence, risk_score, mode, status, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                recommendation.get("recommendation_id"),
                recommendation.get("optimization_id"),
                recommendation.get("category"),
                recommendation.get("title"),
                recommendation.get("description"),
                json.dumps(recommendation.get("evidence", {})),
                json.dumps(recommendation.get("expected_impact", {})),
                recommendation.get("confidence"),
                recommendation.get("risk_score"),
                recommendation.get("mode"),
                recommendation.get("status"),
                recommendation.get("created_at"),
                json.dumps(recommendation.get("metadata", {}))
            )
            self.db.execute(query, params)
            return True
        except Exception as e:
            logger.error(f"Failed to save recommendation: {e}")
            return False
    
    def save_decision(self, decision: Dict[str, Any]) -> bool:
        """Save decision"""
        try:
            query = """
                INSERT OR REPLACE INTO decision_history 
                (decision_id, optimization_id, reason, evidence, confidence, risk_score, expected_impact, rollback_plan, related_metrics, status, created_at, decided_at, decided_by, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                decision.get("decision_id"),
                decision.get("optimization_id"),
                decision.get("reason"),
                json.dumps(decision.get("evidence", {})),
                decision.get("confidence"),
                decision.get("risk_score"),
                json.dumps(decision.get("expected_impact", {})),
                json.dumps(decision.get("rollback_plan", {})),
                json.dumps(decision.get("related_metrics", [])),
                decision.get("status"),
                decision.get("created_at"),
                decision.get("decided_at"),
                decision.get("decided_by"),
                json.dumps(decision.get("metadata", {}))
            )
            self.db.execute(query, params)
            return True
        except Exception as e:
            logger.error(f"Failed to save decision: {e}")
            return False
    
    def save_approval_request(self, request: Dict[str, Any]) -> bool:
        """Save approval request"""
        try:
            query = """
                INSERT OR REPLACE INTO approval_requests 
                (request_id, optimization_id, decision_id, requester, approver, status, reason, context, expires_at, created_at, decided_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                request.get("request_id"),
                request.get("optimization_id"),
                request.get("decision_id"),
                request.get("requester"),
                request.get("approver"),
                request.get("status"),
                request.get("reason"),
                json.dumps(request.get("context", {})),
                request.get("expires_at"),
                request.get("created_at"),
                request.get("decided_at"),
                json.dumps(request.get("metadata", {}))
            )
            self.db.execute(query, params)
            return True
        except Exception as e:
            logger.error(f"Failed to save approval request: {e}")
            return False
    
    def save_rollback_record(self, record: Dict[str, Any]) -> bool:
        """Save rollback record"""
        try:
            query = """
                INSERT OR REPLACE INTO rollback_history 
                (rollback_id, optimization_id, reason, before_state, after_state, rollback_steps, verification_checks, status, created_at, executed_at, completed_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                record.get("rollback_id"),
                record.get("optimization_id"),
                record.get("reason"),
                json.dumps(record.get("before_state", {})),
                json.dumps(record.get("after_state", {})),
                json.dumps(record.get("rollback_steps", [])),
                json.dumps(record.get("verification_checks", [])),
                record.get("status"),
                record.get("created_at"),
                record.get("executed_at"),
                record.get("completed_at"),
                json.dumps(record.get("metadata", {}))
            )
            self.db.execute(query, params)
            return True
        except Exception as e:
            logger.error(f"Failed to save rollback record: {e}")
            return False


def main():
    print("Optimization Database Manager loaded")


if __name__ == "__main__":
    main()
