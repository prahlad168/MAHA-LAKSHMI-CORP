#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Knowledge Database Manager
Database operations for knowledge platform.
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

logger = logging.getLogger("maha-sales-engine.knowledge.db")


class KnowledgeDatabaseManager:
    """Database manager for knowledge platform"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure knowledge tables exist"""
        schema_path = Path(__file__).parent / "schema.sql"
        if schema_path.exists():
            schema = schema_path.read_text()
            self.db.execute(schema)
            logger.info("Knowledge tables created/verified")
    
    def save_knowledge_item(self, item: Dict[str, Any]) -> bool:
        """Save knowledge item"""
        try:
            query = """
                INSERT OR REPLACE INTO knowledge_items 
                (knowledge_id, knowledge_type, title, content, source, version, confidence, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                item.get("knowledge_id"),
                item.get("knowledge_type"),
                item.get("title"),
                json.dumps(item.get("content", {})),
                item.get("source"),
                item.get("version", 1),
                item.get("confidence", 0.0),
                item.get("created_at"),
                item.get("updated_at"),
                json.dumps(item.get("metadata", {}))
            )
            self.db.execute(query, params)
            return True
        except Exception as e:
            logger.error(f"Failed to save knowledge item: {e}")
            return False
    
    def save_decision_memory(self, memory: Dict[str, Any]) -> bool:
        """Save decision memory"""
        try:
            query = """
                INSERT OR REPLACE INTO decision_memory 
                (memory_id, decision_id, optimization_id, category, decision, reason, evidence, confidence, risk_score, outcome, reward, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                memory.get("memory_id"),
                memory.get("decision_id"),
                memory.get("optimization_id"),
                memory.get("category"),
                memory.get("decision"),
                memory.get("reason"),
                json.dumps(memory.get("evidence", {})),
                memory.get("confidence"),
                memory.get("risk_score"),
                json.dumps(memory.get("outcome", {})),
                memory.get("reward"),
                memory.get("created_at")
            )
            self.db.execute(query, params)
            return True
        except Exception as e:
            logger.error(f"Failed to save decision memory: {e}")
            return False
    
    def save_learning_event(self, event: Dict[str, Any]) -> bool:
        """Save learning event"""
        try:
            query = """
                INSERT INTO learning_events 
                (event_id, event_type, source, data, outcome, reward, context, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                event.get("event_id"),
                event.get("event_type"),
                event.get("source"),
                json.dumps(event.get("data", {})),
                json.dumps(event.get("outcome", {})),
                event.get("reward"),
                json.dumps(event.get("context", {})),
                event.get("created_at")
            )
            self.db.execute(query, params)
            return True
        except Exception as e:
            logger.error(f"Failed to save learning event: {e}")
            return False


def main():
    print("Knowledge Database Manager loaded")


if __name__ == "__main__":
    main()
