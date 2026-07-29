#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketplace Tests
Test suite for marketplace platform.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sdk.base import BaseMarketplaceProvider, PublicationStatus, ProductMapping
from core.registry import ProviderRegistry, ProviderLoader
from core.state_machine import StateMachine, StatusManager
from security.credentials import CredentialManager
from events.bus import EventBus, MarketplaceEvents
from queue.manager import JobQueue, RetryManager
from engines.publishing import PublishingEngine, SynchronizationEngine, WebhookEngine


# ============ FIXTURES ============

@pytest.fixture
def temp_dir():
    """Create temporary directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def registry():
    """Create provider registry"""
    return ProviderRegistry()


@pytest.fixture
def credential_manager():
    """Create credential manager"""
    return CredentialManager("test-encryption-key-1234567890123456789012")


@pytest.fixture
def event_bus():
    """Create event bus"""
    return EventBus()


@pytest.fixture
def job_queue():
    """Create job queue"""
    queue = JobQueue(max_workers=2)
    queue.start()
    yield queue
    queue.stop()


# ============ STATE MACHINE TESTS ============

class TestStateMachine:
    """Test state machine"""
    
    def test_valid_transitions(self):
        """Test valid state transitions"""
        assert StateMachine.can_transition("draft", "publishing") is True
        assert StateMachine.can_transition("draft", "deleted") is False
    
    def test_terminal_statuses(self):
        """Test terminal statuses"""
        terminal = StateMachine.get_terminal_statuses()
        assert "deleted" in terminal
    
    def test_status_manager_can_publish(self):
        """Test can publish check"""
        manager = StatusManager()
        mapping = {"publication_status": "draft"}
        assert manager.can_publish(mapping) is True
    
    def test_status_manager_cannot_delete_from_draft(self):
        """Test cannot delete from draft"""
        manager = StatusManager()
        mapping = {"publication_status": "draft"}
        assert manager.can_delete(mapping) is False


# ============ EVENT BUS TESTS ============

class TestEventBus:
    """Test event bus"""
    
    def test_subscribe_and_publish(self, event_bus):
        """Test subscribe and publish"""
        received = []
        
        def handler(event):
            received.append(event)
        
        event_bus.subscribe(MarketplaceEvents.PUBLISH_STARTED, handler)
        event = Event(MarketplaceEvents.PUBLISH_STARTED, {"product_id": "test"})
        event_bus.publish(event)
        
        assert len(received) == 1
        assert received[0].event_type == MarketplaceEvents.PUBLISH_STARTED
    
    def test_event_history(self, event_bus):
        """Test event history"""
        event1 = Event("test.1", {"data": 1})
        event2 = Event("test.2", {"data": 2})
        
        event_bus.publish(event1)
        event_bus.publish(event2)
        
        history = event_bus.get_history()
        assert len(history) == 2
    
    def test_unsubscribe(self, event_bus):
        """Test unsubscribe"""
        received = []
        
        def handler(event):
            received.append(event)
        
        event_bus.subscribe(MarketplaceEvents.PUBLISH_STARTED, handler)
        event_bus.unsubscribe(MarketplaceEvents.PUBLISH_STARTED, handler)
        
        event = Event(MarketplaceEvents.PUBLISH_STARTED, {"product_id": "test"})
        event_bus.publish(event)
        
        assert len(received) == 0


# ============ CREDENTIAL MANAGER TESTS ============

class TestCredentialManager:
    """Test credential manager"""
    
    def test_store_and_retrieve(self, credential_manager):
        """Test store and retrieve"""
        credential_manager.store_credential("test-mkt", "api_key", {"key": "secret123"})
        creds = credential_manager.get_credential("test-mkt", "api_key")
        
        assert creds is not None
        assert creds["key"] == "secret123"
    
    def test_delete_credential(self, credential_manager):
        """Test delete credential"""
        credential_manager.store_credential("test-mkt", "api_key", {"key": "secret123"})
        credential_manager.delete_credential("test-mkt", "api_key")
        
        creds = credential_manager.get_credential("test-mkt", "api_key")
        assert creds is None
    
    def test_rotate_credential(self, credential_manager):
        """Test rotate credential"""
        credential_manager.store_credential("test-mkt", "api_key", {"key": "old"})
        credential_manager.rotate_credential("test-mkt", "api_key", {"key": "new"})
        
        creds = credential_manager.get_credential("test-mkt", "api_key")
        assert creds["key"] == "new"


# ============ JOB QUEUE TESTS ============

class TestJobQueue:
    """Test job queue"""
    
    def test_enqueue_job(self, job_queue):
        """Test enqueue job"""
        job_id = job_queue.enqueue(
            "test_job",
            {"data": "test"},
            priority=JobPriority.HIGH
        )
        
        assert job_id is not None
        job = job_queue.get_job(job_id)
        assert job is not None
        assert job["state"] == JobState.PENDING.value
    
    def test_cancel_job(self, job_queue):
        """Test cancel job"""
        job_id = job_queue.enqueue("test_job", {"data": "test"})
        success = job_queue.cancel_job(job_id)
        
        assert success is True
        job = job_queue.get_job(job_id)
        assert job["state"] == JobState.CANCELLED.value
    
    def test_queue_stats(self, job_queue):
        """Test queue statistics"""
        stats = job_queue.get_stats()
        assert "total_jobs" in stats
        assert "pending" in stats


# ============ PROVIDER REGISTRY TESTS ============

class TestProviderRegistry:
    """Test provider registry"""
    
    def test_register_provider(self, registry):
        """Test register provider"""
        # Create mock provider class
        class MockProvider(BaseMarketplaceProvider):
            PROVIDER_NAME = "mock"
            PROVIDER_VERSION = "1.0.0"
            CAPABILITIES = ["supports_publish"]
            AUTH_TYPE = "api_key"
            
            async def initialize(self):
                return True
            async def authenticate(self):
                return True
            async def validate(self):
                return {"valid": True}
            async def publish(self, *args):
                return {"success": True}
            async def update(self, *args):
                return {"success": True}
            async def archive(self, *args):
                return {"success": True}
            async def delete(self, *args):
                return {"success": True}
            async def sync(self, *args):
                return {"success": True}
            async def health(self):
                return {"status": "healthy"}
            def capabilities(self):
                return self.CAPABILITIES
            async def shutdown(self):
                return True
        
        success = registry.register(MockProvider)
        assert success is True
        assert "mock" in registry.get_registered_providers()
    
    def test_validate_dependencies(self, registry):
        """Test validate dependencies"""
        class InvalidProvider:
            pass
        
        result = registry.validate_dependencies(InvalidProvider)
        assert result["valid"] is False


# ============ INTEGRATION TESTS ============

class TestIntegration:
    """Integration tests"""
    
    def test_full_publication_flow(self):
        """Test full publication flow"""
        # This would require actual database and provider setup
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
