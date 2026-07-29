#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Knowledge Versioning
Manages versioning for knowledge artifacts.
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

logger = logging.getLogger("maha-sales-engine.knowledge.versioning")


@dataclass
class KnowledgeVersion:
    version_id: str
    knowledge_id: str
    version: int
    title: str
    content: Dict[str, Any]
    author: str
    change_reason: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class KnowledgeVersioning:
    """
    Knowledge versioning system.
    Every knowledge artifact must support version, history, author, timestamp, and change reason.
    """
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._versions: Dict[str, List[KnowledgeVersion]] = {}
    
    def create_version(self, knowledge_id: str, title: str, content: Dict[str, Any], author: str, change_reason: str) -> KnowledgeVersion:
        """Create new version of knowledge"""
        version_id = f"ver-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        
        # Get current version number
        existing = self._versions.get(knowledge_id, [])
        version = len(existing) + 1
        
        version_obj = KnowledgeVersion(
            version_id=version_id,
            knowledge_id=knowledge_id,
            version=version,
            title=title,
            content=content,
            author=author,
            change_reason=change_reason
        )
        
        if knowledge_id not in self._versions:
            self._versions[knowledge_id] = []
        self._versions[knowledge_id].append(version_obj)
        
        logger.info(f"Version created: {knowledge_id} v{version}")
        return version_obj
    
    def get_history(self, knowledge_id: str) -> List[KnowledgeVersion]:
        """Get version history"""
        return self._versions.get(knowledge_id, [])
    
    def get_latest(self, knowledge_id: str) -> Optional[KnowledgeVersion]:
        """Get latest version"""
        versions = self._versions.get(knowledge_id, [])
        return versions[-1] if versions else None


def main():
    print("Knowledge Versioning loaded")


if __name__ == "__main__":
    main()
