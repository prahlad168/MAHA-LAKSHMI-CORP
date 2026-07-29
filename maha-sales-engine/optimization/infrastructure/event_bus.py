#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Optimization Event Bus
Event bus for optimization events.
"""

import os
import sys
import json
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.optimization.event_bus")


@dataclass
class Event:
    event_id: str
    event_type: str
    source: str
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class EventBus:
    """
    Event bus for optimization events.
    """
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._history: List[Event] = []
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event type"""
        self._handlers[event_type].append(handler)
        logger.info(f"Handler subscribed to: {event_type}")
    
    def publish(self, event_type: str, source: str, data: Dict[str, Any]):
        """Publish event"""
        event = Event(
            event_id=f"evt-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            source=source,
            data=data
        )
        
        self._history.append(event)
        
        # Notify handlers
        for handler in self._handlers.get(event_type, []):
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Event handler error: {e}")
        
        logger.info(f"Event published: {event_type} from {source}")
    
    def get_history(self, event_type: Optional[str] = None) -> List[Event]:
        """Get event history"""
        if event_type:
            return [e for e in self._history if e.event_type == event_type]
        return self._history.copy()


def main():
    print("Event Bus loaded")


if __name__ == "__main__":
    main()
