#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Event Bus

Centralized event bus for Mission Control and system-wide event distribution.
"""

import sys
import json
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.logging_utils import get_logger

logger = get_logger("maha-sales-engine.mission-control.events")


@dataclass
class Event:
    """Event data structure"""
    event_type: str
    data: Dict[str, Any]
    source: str = "mission-control"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    event_id: str = field(default_factory=lambda: f"mc-evt-{datetime.now().strftime('%Y%m%d%H%M%S%f')}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source": self.source,
            "timestamp": self.timestamp,
            "data": self.data
        }


class EventBus:
    """
    Thread-safe event bus for Mission Control.
    
    Provides publish-subscribe pattern for internal and external events.
    """
    
    def __init__(self, max_history: int = 1000):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_history: List[Event] = []
        self._max_history = max_history
        self._lock = threading.Lock()
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to event type"""
        with self._lock:
            self._handlers[event_type].append(handler)
            logger.debug(f"Handler subscribed to {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe from event type"""
        with self._lock:
            if event_type in self._handlers:
                self._handlers[event_type] = [h for h in self._handlers[event_type] if h != handler]
    
    def publish(self, event: Event) -> bool:
        """
        Publish event to all subscribers.
        
        Args:
            event: Event to publish
            
        Returns:
            True if published successfully, False otherwise
        """
        try:
            with self._lock:
                self._event_history.append(event)
                if len(self._event_history) > self._max_history:
                    self._event_history.pop(0)
                
                handlers = list(self._handlers.get(event.event_type, []))
            
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Event handler failed for {event.event_type}: {e}")
            
            logger.debug(f"Event published: {event.event_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False
    
    def get_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get event history.
        
        Args:
            event_type: Optional event type filter
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        with self._lock:
            events = self._event_history
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            return [e.to_dict() for e in events[-limit:]]


class MissionControlEvents:
    """Mission Control event types"""
    MISSION_CREATED = "mission.created"
    MISSION_STARTED = "mission.started"
    MISSION_COMPLETED = "mission.completed"
    MISSION_FAILED = "mission.failed"
    METRIC_RECORDED = "metric.recorded"
    ALERT_CREATED = "alert.created"
    ALERT_ACKNOWLEDGED = "alert.acknowledged"
    HEALTH_CHECK = "health.check"
    SYSTEM_HEALTH = "system.health"
    INTEGRATION_CONNECTED = "integration.connected"
    INTEGRATION_FAILED = "integration.failed"


# Global event bus instance
event_bus = EventBus()
