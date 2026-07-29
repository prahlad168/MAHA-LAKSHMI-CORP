#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketplace Event Bus
Event system for marketplace operations.
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger("maha-sales-engine.marketplace.events")


class Event:
    """Event data structure"""
    
    def __init__(self, event_type: str, data: Dict[str, Any], source: str = "marketplace"):
        self.event_type = event_type
        self.data = data
        self.source = source
        self.timestamp = datetime.now().isoformat()
        self.event_id = f"evt-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source": self.source,
            "timestamp": self.timestamp,
            "data": self.data
        }
    
    def __repr__(self):
        return f"Event({self.event_type}, source={self.source})"


class EventBus:
    """Internal event system for marketplace operations"""
    
    def __init__(self, max_history: int = 1000):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_history: List[Event] = []
        self._max_history = max_history
        self._middleware: List[Callable] = []
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event type"""
        self._handlers[event_type].append(handler)
        logger.debug(f"Handler subscribed to {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from event type"""
        if event_type in self._handlers:
            self._handlers[event_type] = [h for h in self._handlers[event_type] if h != handler]
    
    def add_middleware(self, middleware: Callable):
        """Add event middleware"""
        self._middleware.append(middleware)
    
    def publish(self, event: Event) -> bool:
        """Publish event to all subscribers"""
        try:
            # Run middleware
            for middleware in self._middleware:
                try:
                    result = middleware(event)
                    if result is False:
                        logger.debug(f"Event blocked by middleware: {event.event_type}")
                        return False
                except Exception as e:
                    logger.error(f"Middleware error: {e}")
            
            # Store in history
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
            
            # Dispatch to handlers
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
    
    def clear_history(self):
        """Clear event history"""
        self._event_history.clear()
        logger.info("Event history cleared")


# Global event bus instance
event_bus = EventBus()


# ============ EVENT TYPES ============

class MarketplaceEvents:
    """Marketplace event types"""
    
    # Marketplace lifecycle
    MARKETPLACE_REGISTERED = "marketplace.registered"
    MARKETPLACE_REMOVED = "marketplace.removed"
    MARKETPLACE_ENABLED = "marketplace.enabled"
    MARKETPLACE_DISABLED = "marketplace.disabled"
    
    # Publication lifecycle
    PUBLISH_STARTED = "publish.started"
    PUBLISH_COMPLETED = "publish.completed"
    PUBLISH_FAILED = "publish.failed"
    
    UPDATE_STARTED = "update.started"
    UPDATE_COMPLETED = "update.completed"
    UPDATE_FAILED = "update.failed"
    
    ARCHIVE_COMPLETED = "archive.completed"
    DELETE_COMPLETED = "delete.completed"
    
    # Synchronization
    SYNC_STARTED = "sync.started"
    SYNC_COMPLETED = "sync.completed"
    SYNC_FAILED = "sync.failed"
    
    # Webhooks
    WEBHOOK_RECEIVED = "webhook.received"
    WEBHOOK_PROCESSED = "webhook.processed"
    WEBHOOK_FAILED = "webhook.failed"
    
    # Retry
    RETRY_STARTED = "retry.started"
    RETRY_COMPLETED = "retry.completed"
    RETRY_FAILED = "retry.failed"
    
    # Health
    HEALTH_CHECK = "health.check"
    PROVIDER_ERROR = "provider.error"


def main():
    """Test event bus"""
    bus = EventBus()
    
    # Subscribe
    def handler(event):
        print(f"Received: {event.event_type}")
    
    bus.subscribe(MarketplaceEvents.PUBLISH_STARTED, handler)
    
    # Publish
    event = Event(MarketplaceEvents.PUBLISH_STARTED, {"product_id": "test-123"})
    bus.publish(event)
    
    # History
    history = bus.get_history()
    print(f"History: {len(history)} events")


if __name__ == "__main__":
    main()
