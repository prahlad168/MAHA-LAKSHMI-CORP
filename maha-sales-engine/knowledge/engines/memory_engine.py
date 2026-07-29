#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Memory Engine
Manages short-term, long-term, decision, operational, business rules, experiment, and customer insights memory.
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
from datetime import datetime, timedelta
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.knowledge.memory")


class MemoryType(Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    DECISION = "decision"
    OPERATIONAL = "operational"
    BUSINESS_RULE = "business_rule"
    EXPERIMENT = "experiment"
    CUSTOMER_INSIGHT = "customer_insight"


@dataclass
class MemoryItem:
    memory_id: str
    memory_type: str
    key: str
    value: Any
    expires_at: Optional[str]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    accessed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemoryEngine:
    """
    Memory engine that manages different types of memory.
    """
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._memory: Dict[str, Dict[str, MemoryItem]] = {}
        self._initialize_memory_stores()
    
    def _initialize_memory_stores(self):
        """Initialize memory stores for each type"""
        for memory_type in MemoryType:
            self._memory[memory_type.value] = {}
    
    def store(self, memory_type: MemoryType, key: str, value: Any, ttl: Optional[int] = None, metadata: Dict[str, Any] = None) -> MemoryItem:
        """Store item in memory"""
        memory_id = f"mem-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        
        expires_at = None
        if ttl:
            expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()
        
        item = MemoryItem(
            memory_id=memory_id,
            memory_type=memory_type.value,
            key=key,
            value=value,
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        self._memory[memory_type.value][key] = item
        logger.info(f"Memory stored: {memory_type.value}:{key}")
        return item
    
    def retrieve(self, memory_type: MemoryType, key: str) -> Optional[MemoryItem]:
        """Retrieve item from memory"""
        store = self._memory.get(memory_type.value, {})
        item = store.get(key)
        
        if item:
            # Check expiry
            if item.expires_at and datetime.now() > datetime.fromisoformat(item.expires_at):
                del store[key]
                return None
            
            # Update access stats
            item.access_count += 1
            item.accessed_at = datetime.now().isoformat()
        
        return item
    
    def delete(self, memory_type: MemoryType, key: str):
        """Delete item from memory"""
        store = self._memory.get(memory_type.value, {})
        if key in store:
            del store[key]
            logger.info(f"Memory deleted: {memory_type.value}:{key}")
    
    def clear(self, memory_type: Optional[MemoryType] = None):
        """Clear memory"""
        if memory_type:
            self._memory[memory_type.value] = {}
        else:
            for store in self._memory.values():
                store.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        stats = {}
        for memory_type, store in self._memory.items():
            stats[memory_type] = {
                "size": len(store),
                "keys": list(store.keys())
            }
        return stats


def main():
    print("Memory Engine loaded")


if __name__ == "__main__":
    main()
