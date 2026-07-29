#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Knowledge Core
Core orchestration for the Knowledge & Learning Platform.
"""

import os
import sys
import json
import time
import uuid
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.knowledge")


class KnowledgeType(Enum):
    DOCUMENT = "document"
    DECISION = "decision"
    EXPERIMENT = "experiment"
    PATTERN = "pattern"
    RULE = "rule"
    INSIGHT = "insight"
    FEEDBACK = "feedback"


class MemoryType(Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    DECISION = "decision"
    OPERATIONAL = "operational"
    BUSINESS_RULE = "business_rule"
    EXPERIMENT = "experiment"
    CUSTOMER_INSIGHT = "customer_insight"


@dataclass
class KnowledgeContext:
    knowledge_id: str
    knowledge_type: KnowledgeType
    title: str
    content: Dict[str, Any]
    source: str
    version: int
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgeCore:
    """
    Core orchestration for knowledge platform.
    """
    
    def __init__(self, db_manager, learning_engine, memory_engine, knowledge_graph, semantic_search):
        self.db = db_manager
        self.learning_engine = learning_engine
        self.memory_engine = memory_engine
        self.knowledge_graph = knowledge_graph
        self.semantic_search = semantic_search
        self._knowledge: Dict[str, KnowledgeContext] = {}
        self._lock = threading.Lock()
    
    def create_knowledge(self, knowledge_type: KnowledgeType, title: str, content: Dict[str, Any], source: str) -> KnowledgeContext:
        """Create new knowledge item"""
        knowledge_id = f"know-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        
        context = KnowledgeContext(
            knowledge_id=knowledge_id,
            knowledge_type=knowledge_type,
            title=title,
            content=content,
            source=source,
            version=1
        )
        
        with self._lock:
            self._knowledge[knowledge_id] = context
        
        logger.info(f"Knowledge created: {knowledge_id} ({knowledge_type.value})")
        return context
    
    def get_knowledge(self, knowledge_id: str) -> Optional[KnowledgeContext]:
        """Get knowledge by ID"""
        return self._knowledge.get(knowledge_id)
    
    def list_knowledge(self, knowledge_type: Optional[KnowledgeType] = None) -> List[KnowledgeContext]:
        """List knowledge items"""
        items = list(self._knowledge.values())
        if knowledge_type:
            items = [k for k in items if k.knowledge_type == knowledge_type]
        return items


class KnowledgeError(Exception):
    """Knowledge error"""
    pass


def main():
    print("Knowledge Core loaded")


if __name__ == "__main__":
    main()
