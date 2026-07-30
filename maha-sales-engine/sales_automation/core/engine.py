#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Automation Core
Main orchestrator for the Sales Automation Engine.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine import ConfigManager, DatabaseManager

logger = logging.getLogger("maha-sales-engine.sales-automation.core")


class AutomationCore:
    """Main orchestrator for Sales Automation Engine"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_dir = base_dir / "sales-automation" / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        config_path = base_dir / "config" / "engine.yaml"
        self.config = ConfigManager(config_path)
        self.db = DatabaseManager(Path(self.config.get("database.path")))
        
        # Initialize components
        from marketplace.events.bus import EventBus
        from sales_automation.workflow.engine import WorkflowEngine
        from sales_automation.queue.engine import QueueEngine
        from sales_automation.retry.manager import RetryManager
        from sales_automation.publication.engine import PublicationEngine
        from sales_automation.sync.engine import SynchronizationEngine
        from sales_automation.approval.engine import ApprovalEngine
        from sales_automation.rules.engine import RulesEngine
        from sales_automation.policy.engine import PolicyEngine
        from sales_automation.notification.engine import NotificationEngine, EmailProvider, SlackProvider
        from sales_automation.webhooks.gateway import WebhookGateway
        from sales_automation.health.monitor import HealthMonitor
        from sales_automation.audit.engine import AuditEngine
        from sales_automation.metrics.collector import MetricsCollector
        from sales_automation.campaign.engine import CampaignEngine
        
        self.event_bus = EventBus()
        self.queue_engine = QueueEngine(self.db, max_workers=5)
        self.queue_engine.start()
        self.retry_manager = RetryManager(self.db)
        self.workflow_engine = WorkflowEngine(self.db, self.event_bus, None, None)
        self.publication_engine = PublicationEngine(self.db, None, None, self.event_bus, self.workflow_engine, None, None)
        self.sync_engine = SynchronizationEngine(self.db, None, None, self.event_bus)
        self.approval_engine = ApprovalEngine(self.db, self.event_bus, None)
        self.rules_engine = RulesEngine(self.db, self.event_bus)
        self.policy_engine = PolicyEngine(self.db)
        self.notification_engine = NotificationEngine(self.db, self.event_bus)
        self.webhook_gateway = WebhookGateway(self.db, self.event_bus)
        self.health_monitor = HealthMonitor(self.db, self.event_bus)
        self.audit_engine = AuditEngine(self.db, self.event_bus)
        self.metrics_collector = MetricsCollector(self.db)
        self.campaign_engine = CampaignEngine(self.db, self.workflow_engine, self.publication_engine, self.event_bus)
        
        # Register notification providers
        self.notification_engine.register_provider("email", EmailProvider())
        self.notification_engine.register_provider("slack", SlackProvider())
        
        # Register default rules
        self._register_default_rules()
        
        logger.info("Sales Automation Core initialized")
    
    def _register_default_rules(self):
        self.rules_engine.add_rule(
            name="Minimum Quality Score",
            description="Block publication if quality score below threshold",
            condition={"field": "quality_score", "operator": "lt", "value": 0.8},
            action={"block": True, "require_approval": True},
            priority=10
        )
        
        self.rules_engine.add_rule(
            name="Require Marketing Approval",
            description="Require approval for marketing content",
            condition={"field": "content_type", "operator": "eq", "value": "marketing"},
            action={"require_approval": True},
            priority=20
        )
    
    def start(self):
        logger.info("Sales Automation Engine started")
    
    def stop(self):
        self.queue_engine.stop()
        logger.info("Sales Automation Engine stopped")
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "module": "sales-automation",
            "status": "running",
            "queue_stats": self.queue_engine.get_stats(),
            "health": self.health_monitor.get_overall_health()
        }


def main():
    from pathlib import Path
    base_dir = Path(__file__).parent.parent.parent
    core = AutomationCore(base_dir)
    print("Sales Automation Core Test")
    print(f"Status: {core.get_status()}")
    core.stop()


if __name__ == "__main__":
    main()
