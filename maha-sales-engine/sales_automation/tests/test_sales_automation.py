#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Sales Automation Tests
Test suite for sales automation engine.
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

from sales_automation.core.state_machine import AutomationStateMachine, AutomationStatus, AutomationStatusManager
from sales_automation.workflow.engine import WorkflowBuilder, WorkflowEngine
from sales_automation.queue.engine import QueueEngine, JobPriority
from sales_automation.retry.manager import RetryManager, RetryPolicy
from sales_automation.approval.engine import ApprovalEngine
from sales_automation.rules.engine import RulesEngine
from sales_automation.policy.engine import PolicyEngine
from sales_automation.notification.engine import NotificationEngine
from sales_automation.webhooks.gateway import WebhookGateway
from sales_automation.health.monitor import HealthMonitor
from sales_automation.audit.engine import AuditEngine
from sales_automation.metrics.collector import MetricsCollector
from sales_automation.campaign.engine import CampaignEngine


# ============ FIXTURES ============

@pytest.fixture
def temp_dir():
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except:
        pass


@pytest.fixture
def db_manager(temp_dir):
    import importlib.util
    core_engine_path = Path(__file__).parent.parent.parent / "core" / "engine.py"
    spec = importlib.util.spec_from_file_location("core_engine", core_engine_path)
    core_engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core_engine)
    db_path = temp_dir / "test.db"
    return core_engine.DatabaseManager(db_path)


@pytest.fixture
def mock_event_bus():
    return Mock()


@pytest.fixture
def mock_publication_engine():
    return Mock()


# ============ STATE MACHINE TESTS ============

class TestAutomationStateMachine:
    def test_valid_transitions(self):
        assert AutomationStateMachine.can_transition("draft", "ready") is True
        assert AutomationStateMachine.can_transition("draft", "archived") is False
    
    def test_status_manager_transition(self):
        manager = AutomationStatusManager()
        record = {"status": "draft"}
        result = manager.transition(record, "ready")
        assert result["success"] is True
        assert record["status"] == "ready"
    
    def test_can_publish(self):
        manager = AutomationStatusManager()
        record = {"status": "ready"}
        assert manager.can_publish(record) is True


# ============ WORKFLOW TESTS ============

class TestWorkflowBuilder:
    def test_build_workflow(self):
        builder = WorkflowBuilder()
        builder.add_node("start", "validation", "Start", {}, ["end"])
        builder.set_entry("start")
        builder.set_exit("end")
        workflow = builder.build("Test Workflow")
        
        assert workflow.name == "Test Workflow"
        assert workflow.entry_node == "start"
        assert len(workflow.nodes) == 1


# ============ QUEUE TESTS ============

class TestQueueEngine:
    def test_enqueue_job(self, db_manager):
        queue = QueueEngine(db_manager, max_workers=1)
        queue.register_handler("test", lambda payload: {"success": True})
        queue.start()
        job_id = queue.enqueue("test", {"data": "test"}, JobPriority.NORMAL)
        assert job_id is not None
        import time
        time.sleep(0.5)
        job = queue.get_job(job_id)
        assert job["state"] in ["queued", "completed"]
        queue.stop()


# ============ RETRY TESTS ============

class TestRetryManager:
    def test_register_policy(self):
        manager = RetryManager(None)
        manager.register_policy("publish", max_retries=3)
        delay = manager.get_delay("publish", 1)
        assert delay > 0
    
    def test_should_retry(self):
        manager = RetryManager(None)
        manager.register_policy("publish", max_retries=3)
        assert manager.should_retry("publish", 0) is True
        assert manager.should_retry("publish", 3) is False


# ============ APPROVAL TESTS ============

class TestApprovalEngine:
    def test_request_approval(self, db_manager, mock_event_bus):
        engine = ApprovalEngine(db_manager, mock_event_bus, Mock())
        request_id = engine.request_approval("mkt-123", "prod-456", "publication")
        assert request_id is not None


# ============ RULES TESTS ============

class TestRulesEngine:
    def test_add_rule(self, db_manager):
        engine = RulesEngine(db_manager, Mock())
        rule_id = engine.add_rule("Test Rule", "Test", {"field": "score", "operator": "lt", "value": 0.5}, {"block": True})
        assert rule_id is not None
    
    def test_evaluate(self, db_manager):
        engine = RulesEngine(db_manager, Mock())
        engine.add_rule("Test", "Test", {"field": "score", "operator": "lt", "value": 0.5}, {"block": True})
        results = engine.evaluate({"score": 0.3})
        assert len(results) == 1


# ============ HEALTH TESTS ============

class TestHealthMonitor:
    def test_register_and_check(self, db_manager):
        monitor = HealthMonitor(db_manager, Mock())
        monitor.register_component("test")
        health = monitor.check_health("test")
        assert health["name"] == "test"


# ============ METRICS TESTS ============

class TestMetricsCollector:
    def test_increment_and_get(self, db_manager):
        collector = MetricsCollector(db_manager)
        collector.increment("test_metric")
        metrics = collector.get_metrics("test_metric")
        assert metrics["counters"]["test_metric"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
