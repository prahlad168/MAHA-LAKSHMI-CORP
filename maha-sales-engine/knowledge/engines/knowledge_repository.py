#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Knowledge Repository
Central repository for storing and retrieving knowledge items.
"""

import os
import sys
import json
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.knowledge.repository")


@dataclass
class KnowledgeItem:
    knowledge_id: str
    knowledge_type: str
    title: str
    content: Dict[str, Any]
    source: str
    version: int
    confidence: float
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgeRepository:
    """
    Knowledge repository for storing and retrieving knowledge items.
    """
    
    def __init__(self, db_manager, versioning, audit):
        self.db = db_manager
        self.versioning = versioning
        self.audit = audit
        self._items: Dict[str, KnowledgeItem] = {}
    
    def store(self, knowledge_type: str, title: str, content: Dict[str, Any], source: str, author: str = "system", change_reason: str = "initial") -> KnowledgeItem:
        """Store knowledge item"""
        knowledge_id = f"know-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        
        item = KnowledgeItem(
            knowledge_id=knowledge_id,
            knowledge_type=knowledge_type,
            title=title,
            content=content,
            source=source,
            version=1,
            confidence=content.get("confidence", 0.0)
        )
        
        self._items[knowledge_id] = item
        
        # Create version
        self.versioning.create_version(knowledge_id, title, content, author, change_reason)
        
        # Audit
        self.audit.log(knowledge_id, "create", author, {"title": title, "source": source})
        
        logger.info(f"Knowledge stored: {knowledge_id}")
        return item
    
    def get(self, knowledge_id: str) -> Optional[KnowledgeItem]:
        """Get knowledge item"""
        return self._items.get(knowledge_id)
    
    def update(self, knowledge_id: str, content: Dict[str, Any], author: str = "system", change_reason: str = "update") -> Optional[KnowledgeItem]:
        """Update knowledge item"""
        item = self._items.get(knowledge_id)
        if not item:
            return None
        
        item.content = content
        item.version += 1
        item.updated_at = datetime.now().isoformat()
        item.confidence = content.get("confidence", item.confidence)
        
        # Create new version
        self.versioning.create_version(knowledge_id, item.title, content, author, change_reason)
        
        # Audit
        self.audit.log(knowledge_id, "update", author, {"version": item.version, "reason": change_reason})
        
        logger.info(f"Knowledge updated: {knowledge_id}")
        return item
    
    def search(self, query: str, knowledge_type: Optional[str] = None) -> List[KnowledgeItem]:
        """Search knowledge items"""
        results = []
        query_lower = query.lower()
        
        for item in self._items.values():
            if knowledge_type and item.knowledge_type != knowledge_type:
                continue
            
            if query_lower in item.title.lower():
                results.append(item)
            elif isinstance(item.content, dict) and query_lower in json.dumps(item.content).lower():
                results.append(item)
        
        return results


def main():
    print("Knowledge Repository loaded")


if __name__ == "__main__":
    main()
