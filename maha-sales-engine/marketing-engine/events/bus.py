#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketing Event Bus
Event system for marketing operations.
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger("maha-sales-engine.marketing.events")


class Event:
    """Event data structure"""
    
    def __init__(self, event_type: str, data: Dict[str, Any], source: str = "marketing"):
        self.event_type = event_type
        self.data = data
        self.source = source
        self.timestamp = datetime.now().isoformat()
        self.event_id = f"mkt-evt-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source": self.source,
            "timestamp": self.timestamp,
            "data": self.data
        }


class EventBus:
    """Internal event system for marketing operations"""
    
    def __init__(self, max_history: int = 1000):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_history: List[Event] = []
        self._max_history = max_history
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event type"""
        self._handlers[event_type].append(handler)
        logger.debug(f"Handler subscribed to {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from event type"""
        if event_type in self._handlers:
            self._handlers[event_type] = [h for h in self._handlers[event_type] if h != handler]
    
    def publish(self, event: Event) -> bool:
        """Publish event to all subscribers"""
        try:
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
            
            handlers = self._handlers.get(event.event_type, [])
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.create_task(handler(event))
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Event handler failed for {event.event_type}: {e}")
            
            logger.debug(f"Event published: {event.event_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False
    
    def get_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get event history"""
        events = self._event_history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return [e.to_dict() for e in events[-limit:]]


# Global event bus instance
event_bus = EventBus()


class MarketingEvents:
    """Marketing event types"""
    MARKETING_GENERATED = "marketing.generated"
    SEO_COMPLETED = "seo.completed"
    KEYWORD_GENERATED = "keyword.generated"
    CONTENT_APPROVED = "content.approved"
    CONTENT_REJECTED = "content.rejected"
    VARIANT_CREATED = "variant.created"
    LOCALIZATION_COMPLETED = "localization.completed"


def main():
    """Test event bus"""
    bus = EventBus()
    
    def handler(event):
        print(f"Received: {event.event_type}")
    
    bus.subscribe(MarketingEvents.MARKETING_GENERATED, handler)
    event = Event(MarketingEvents.MARKETING_GENERATED, {"product_id": "test-123"})
    bus.publish(event)
    print("Event bus test passed")


if __name__ == "__main__":
    main()
