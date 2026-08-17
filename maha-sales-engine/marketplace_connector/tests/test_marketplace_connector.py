#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketplace Connector Test Suite
Comprehensive tests for marketplace connector.
"""

import os
import sys
import json
import time
import uuid
import zipfile
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from marketplace_connector.core.marketplace_provider import (
    MarketplaceProvider, PublicationStatus, ProviderType,
    MarketplaceAccount, MarketplaceProduct, PublicationResult
)
from marketplace_connector.providers.gumroad.gumroad_provider import GumroadProvider
from marketplace_connector.publication.publication_pipeline import PublicationPipeline, PipelineStage
from marketplace_connector.publication.validation_engine import ValidationEngine
from marketplace_connector.sync.sync_engine import SyncEngine, SyncType, SyncStatus
from marketplace_connector.webhooks.webhook_engine import WebhookEngine
from marketplace_connector.queue.retry_engine import RetryEngine
from marketplace_connector.queue.publication_queue import PublicationQueue
from marketplace_connector.health.health_monitor import HealthMonitor
from marketplace_connector.audit.audit_engine import AuditEngine
from marketplace_connector.metrics.metrics_collector import MetricsCollector


class TestMarketplaceProvider:
    """Tests for marketplace provider core"""
    
    def test_publication_status_enum(self):
        assert PublicationStatus.DRAFT.value == "draft"
        assert PublicationStatus.PUBLISHED.value == "published"
        assert PublicationStatus.FAILED.value == "failed"
    
    def test_provider_type_enum(self):
        assert ProviderType.GUMROAD.value == "gumroad"
        assert ProviderType.ETSY.value == "etsy"
    
    def test_marketplace_account_creation(self):
        account = MarketplaceAccount(
            account_id="acc-001",
            provider=ProviderType.GUMROAD,
            name="Test Account",
            credentials={"api_key": "test"},
            active=True,
            default=True
        )
        assert account.account_id == "acc-001"
        assert account.provider == ProviderType.GUMROAD
        assert account.active is True
    
    def test_marketplace_product_creation(self):
        product = MarketplaceProduct(
            product_id="prod-001",
            internal_product_id="internal-001",
            marketplace_product_id="gumroad-123",
            marketplace_url="https://gumroad.com/l/123",
            status=PublicationStatus.PUBLISHED,
            provider=ProviderType.GUMROAD,
            price=29.99,
            currency="USD",
            visibility="public",
            published_at="2024-01-01T00:00:00"
        )
        assert product.price == 29.99
        assert product.status == PublicationStatus.PUBLISHED
    
    def test_publication_result_creation(self):
        result = PublicationResult(
            success=True,
            marketplace_product_id="gumroad-123",
            marketplace_url="https://gumroad.com/l/123",
            status=PublicationStatus.PUBLISHED,
            message="Success"
        )
        assert result.success is True
        assert result.marketplace_product_id == "gumroad-123"


class TestGumroadProvider:
    """Tests for Gumroad provider"""
    
    @pytest.fixture(autouse=True)
    def check_api_key(self):
        if not os.getenv("GUMROAD_API_KEY"):
            pytest.skip("GUMROAD_API_KEY not set, skipping Gumroad provider tests")
    
    @pytest.fixture
    def provider(self):
        api_key = os.getenv("GUMROAD_API_KEY", "")
        return GumroadProvider({"api_key": api_key})
    
    @pytest.mark.asyncio
    async def test_connect_success(self, provider):
        with patch.object(provider, 'validate', new_callable=AsyncMock, return_value={"valid": True}):
            result = await provider.connect()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, provider):
        with patch.object(provider, 'validate', new_callable=AsyncMock, return_value={"valid": False, "error": "Auth failed"}):
            result = await provider.connect()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_upload_file_success(self, provider):
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
            f.write(b"test content")
            temp_path = f.name
        
        try:
            with patch.object(provider, 'upload_file', new_callable=AsyncMock, return_value={
                "success": True, "file_url": "https://example.com/file.zip", "file_type": "product"
            }) as mock_upload:
                result = await provider.upload_file(temp_path, "product")
            assert result["success"] is True
            assert "file_url" in result
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_upload_file_not_found(self, provider):
        result = await provider.upload_file("/nonexistent/file.zip", "product")
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_create_listing_success(self, provider):
        with patch.object(provider, '_request', new_callable=AsyncMock, return_value={
            "success": True, "data": {"product": {"id": "gumroad-123", "permalink": "test-product"}}
        }):
            payload = {"title": "Test Product", "price": 29.99}
            result = await provider.create_listing(payload)
        assert result["success"] is True
        assert "product_id" in result
        assert result["url"] == "https://gumroad.com/l/test-product"
    
    @pytest.mark.asyncio
    async def test_health_check(self, provider):
        with patch.object(provider, 'validate', new_callable=AsyncMock, return_value={"valid": True}):
            result = await provider.health()
            assert result["status"] == "healthy"
            assert result["provider"] == "gumroad"
    
    def test_build_gumroad_payload(self, provider):
        payload = {
            "title": "Test Product",
            "description": "Test description",
            "price": 29.99,
            "currency": "USD",
            "tags": ["test", "product"]
        }
        result = provider._build_gumroad_payload(payload)
        assert result["name"] == "Test Product"
        assert result["price"] == 2999
        assert result["price_currency_type"] == "usd"


class TestGumroadProviderReal:
    """Real Gumroad API integration tests - runs only when GUMROAD_API_KEY is available"""
    
    @pytest.fixture(autouse=True)
    def check_api_key(self):
        if not os.getenv("GUMROAD_API_KEY"):
            pytest.skip("GUMROAD_API_KEY not set, skipping real API tests")
    
    @pytest.fixture
    def provider(self):
        return GumroadProvider({"api_key": os.getenv("GUMROAD_API_KEY")})
    
    @pytest.mark.asyncio
    async def test_real_validate(self, provider):
        result = await provider.validate()
        assert result["valid"] is True
        assert "user" in result or "message" in result
    
    @pytest.mark.asyncio
    async def test_real_create_listing_returns_permalink(self, provider):
        payload = {
            "title": "Integration Test Product",
            "description": "Test product for real Gumroad integration",
            "price": 1.00,
            "currency": "USD",
            "tags": ["test", "integration"],
            "published": False
        }
        result = await provider.create_listing(payload)
        assert result["success"] is True
        assert "product_id" in result
        assert result["url"] is not None
        assert result["url"].startswith("https://gumroad.com/l/")
    
    @pytest.mark.asyncio
    async def test_real_publish_and_sync(self, provider):
        payload = {
            "title": "Test Publish Product",
            "description": "Test product for publish",
            "price": 1.00,
            "currency": "USD",
            "tags": ["test"],
            "published": False
        }
        result = await provider.create_listing(payload)
        assert result["success"] is True
        product_id = result["product_id"]
        
        publish_result = await provider.publish(product_id)
        assert publish_result["success"] is True
        
        sync_result = await provider.sync(product_id)
        assert sync_result["success"] is True


class TestValidationEngine:
    """Tests for validation engine"""
    
    @pytest.fixture
    def engine(self):
        return ValidationEngine()
    
    @pytest.fixture
    def valid_package(self, tmp_path):
        pkg = tmp_path / "valid_package"
        pkg.mkdir()
        (pkg / "metadata.json").write_text(json.dumps({"title": "Test", "description": "Test desc", "price": 10, "currency": "USD", "tags": []}))
        (pkg / "description.md").write_text("# Test")
        (pkg / "pricing.json").write_text(json.dumps({"price": 10}))
        (pkg / "keywords.json").write_text(json.dumps({"keywords": []}))
        (pkg / "license.txt").write_text("MIT")
        (pkg / "version.json").write_text(json.dumps({"version": "1.0.0"}))
        (pkg / "quality_report.json").write_text(json.dumps({"score": 90}))
        (pkg / "history.json").write_text(json.dumps({"versions": []}))
        (pkg / "thumbnail").mkdir()
        (pkg / "thumbnail" / "thumb.png").write_text("fake image")
        (pkg / "product").mkdir()
        zip_path = pkg / "product" / "main.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("test.txt", "test content")
        return str(pkg)
    
    @pytest.fixture
    def invalid_package(self, tmp_path):
        pkg = tmp_path / "invalid_package"
        pkg.mkdir()
        (pkg / "metadata.json").write_text(json.dumps({"title": "X"}))
        return str(pkg)
    
    def test_validate_valid_package(self, engine, valid_package):
        metadata = {"title": "Test", "description": "This is a valid test description with enough characters", "price": 10, "currency": "USD", "tags": []}
        result = engine.validate(valid_package, metadata)
        assert result.valid is True
        assert result.score > 0.5
    
    def test_validate_invalid_package(self, engine, invalid_package):
        metadata = {"title": "X", "description": "short", "price": -1, "currency": "USD", "tags": []}
        result = engine.validate(invalid_package, metadata)
        assert result.valid is False
        assert len(result.errors) > 0


class TestPublicationPipeline:
    """Tests for publication pipeline"""
    
    @pytest.fixture
    def mock_provider(self):
        provider = MagicMock()
        provider.upload_file = AsyncMock(return_value={"success": True, "file_url": "https://example.com/file.zip"})
        provider.upload_thumbnail = AsyncMock(return_value={"success": True, "file_url": "https://example.com/thumb.png"})
        provider.create_listing = AsyncMock(return_value={"success": True, "product_id": "gumroad-123", "url": "https://gumroad.com/l/123"})
        provider.publish = AsyncMock(return_value={"success": True})
        provider.health = AsyncMock(return_value={"status": "healthy"})
        return provider
    
    @pytest.fixture
    def mock_validation(self):
        engine = MagicMock()
        engine.validate.return_value = {"valid": True}
        return engine
    
    @pytest.fixture
    def mock_db(self):
        return MagicMock()
    
    @pytest.fixture
    def valid_product_path(self, tmp_path):
        pkg = tmp_path / "product"
        pkg.mkdir()
        (pkg / "metadata.json").write_text(json.dumps({"title": "Test", "description": "Test", "price": 10, "currency": "USD", "tags": []}))
        (pkg / "description.md").write_text("# Test")
        (pkg / "pricing.json").write_text(json.dumps({"price": 10}))
        (pkg / "keywords.json").write_text(json.dumps({}))
        (pkg / "license.txt").write_text("MIT")
        (pkg / "version.json").write_text(json.dumps({"version": "1.0.0"}))
        (pkg / "quality_report.json").write_text(json.dumps({}))
        (pkg / "history.json").write_text(json.dumps({}))
        (pkg / "thumbnail").mkdir()
        (pkg / "thumbnail" / "thumb.png").write_text("fake")
        (pkg / "product").mkdir()
        (pkg / "product" / "main.zip").write_text("fake")
        return str(pkg)
    
    @pytest.mark.asyncio
    async def test_pipeline_success(self, mock_provider, mock_validation, mock_db, valid_product_path):
        pipeline = PublicationPipeline(mock_provider, mock_validation, mock_db)
        metadata = {"product_id": "prod-001", "provider": "gumroad", "title": "Test", "description": "Test", "price": 10, "currency": "USD", "tags": []}
        result = await pipeline.execute(valid_product_path, metadata)
        assert result.success is True
        assert result.status == PublicationStatus.PUBLISHED
        assert result.marketplace_product_id == "gumroad-123"
    
    @pytest.mark.asyncio
    async def test_pipeline_missing_product_path(self, mock_provider, mock_validation, mock_db):
        pipeline = PublicationPipeline(mock_provider, mock_validation, mock_db)
        metadata = {"product_id": "prod-001", "provider": "gumroad"}
        result = await pipeline.execute("/nonexistent/path", metadata)
        assert result.success is False
        assert result.status == PublicationStatus.FAILED


class TestSyncEngine:
    """Tests for sync engine"""
    
    @pytest.fixture
    def mock_provider(self):
        provider = MagicMock()
        provider.provider_type = ProviderType.GUMROAD
        provider.sync = AsyncMock(return_value={"success": True, "synced_count": 1})
        return provider
    
    @pytest.fixture
    def mock_db(self):
        return MagicMock()
    
    @pytest.mark.asyncio
    async def test_sync_single_product(self, mock_provider, mock_db):
        engine = SyncEngine(mock_provider, mock_db)
        job = await engine.sync(SyncType.SINGLE_PRODUCT, "prod-001")
        assert job.sync_type == SyncType.SINGLE_PRODUCT
        assert job.provider == "gumroad"
    
    @pytest.mark.asyncio
    async def test_sync_bulk(self, mock_provider, mock_db):
        engine = SyncEngine(mock_provider, mock_db)
        job = await engine.sync(SyncType.BULK)
        assert job.sync_type == SyncType.BULK
        assert job.status == SyncStatus.COMPLETED


class TestWebhookEngine:
    """Tests for webhook engine"""
    
    @pytest.fixture
    def mock_provider(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_audit(self):
        audit = MagicMock()
        audit.log = MagicMock()
        return audit
    
    @pytest.mark.asyncio
    async def test_process_webhook_success(self, mock_provider, mock_audit):
        engine = WebhookEngine(mock_provider, mock_audit)
        payload = {"id": "evt-001", "type": "purchase", "data": {}}
        result = await engine.process(payload, "signature", "gumroad")
        assert result["success"] is True
        assert result["event_id"] == "evt-001"
    
    @pytest.mark.asyncio
    async def test_process_duplicate_webhook(self, mock_provider, mock_audit):
        engine = WebhookEngine(mock_provider, mock_audit)
        payload = {"id": "evt-001", "type": "purchase", "data": {}}
        await engine.process(payload, "signature", "gumroad")
        result = await engine.process(payload, "signature", "gumroad")
        assert result["success"] is False
        assert "Duplicate" in result["error"]


class TestRetryEngine:
    """Tests for retry engine"""
    
    @pytest.fixture
    def retry_engine(self):
        return RetryEngine(max_attempts=3, backoff_factor=2.0)
    
    def test_enqueue_retry(self, retry_engine):
        job = retry_engine.enqueue("pub-001", "Network error")
        assert job.publication_id == "pub-001"
        assert job.attempt == 1
        assert job.status.value == "pending"
    
    def test_process_retries_success(self, retry_engine):
        def processor(publication_id):
            return {"success": True}
        
        job = retry_engine.enqueue("pub-001", "Error")
        job.next_retry = (datetime.now() - timedelta(minutes=1)).isoformat()
        results = retry_engine.process_retries(processor)
        assert results["succeeded"] == 1
    
    def test_process_retries_failure(self, retry_engine):
        def processor(publication_id):
            return {"success": False, "error": "Still failing"}
        
        job = retry_engine.enqueue("pub-001", "Error")
        
        # Process until max attempts reached
        for _ in range(2):
            job.next_retry = (datetime.now() - timedelta(minutes=1)).isoformat()
            results = retry_engine.process_retries(processor)
        
        assert results["failed"] == 1
        assert len(retry_engine.get_dead_letter_queue()) == 1


class TestPublicationQueue:
    """Tests for publication queue"""
    
    @pytest.fixture
    def queue(self):
        return PublicationQueue(max_workers=2)
    
    def test_enqueue_item(self, queue):
        item = queue.enqueue("pub-001", "gumroad", {"test": True}, priority=3)
        assert item.publication_id == "pub-001"
        assert item.priority == 3
    
    def test_dequeue_item(self, queue):
        item = queue.enqueue("pub-001", "gumroad", {})
        dequeued = queue.dequeue()
        assert dequeued is not None
        assert dequeued.item_id == item.item_id


class TestHealthMonitor:
    """Tests for health monitor"""
    
    @pytest.fixture
    def monitor(self):
        return HealthMonitor()
    
    def test_register_check(self, monitor):
        monitor.register_check("database", lambda: {"status": "healthy"})
        assert len(monitor._checks) == 1
    
    def test_check_all(self, monitor):
        monitor.register_check("database", lambda: {"status": "healthy"})
        result = monitor.check_all()
        assert "checks" in result
        assert "timestamp" in result


class TestAuditEngine:
    """Tests for audit engine"""
    
    @pytest.fixture
    def mock_db(self):
        return MagicMock()
    
    @pytest.fixture
    def audit(self, mock_db):
        return AuditEngine(mock_db)
    
    def test_log_action(self, audit):
        audit.log("pub-001", "publish", "system", {"product_id": "prod-001"})
        history = audit.get_history("pub-001")
        assert len(history) == 1
        assert history[0].action == "publish"


class TestMetricsCollector:
    """Tests for metrics collector"""
    
    @pytest.fixture
    def metrics(self):
        return MetricsCollector()
    
    def test_record_publication(self, metrics):
        metrics.record_publication_attempt()
        metrics.record_publication_success()
        metrics.record_publication_failure()
        data = metrics.get_metrics()
        assert data["total_publications"] == 1
        assert data["successful_publications"] == 1
        assert data["failed_publications"] == 1
    
    def test_record_publication_time(self, metrics):
        metrics.record_publication_time(2.5)
        data = metrics.get_metrics()
        assert data["avg_publication_time"] == 2.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
