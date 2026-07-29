#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Commerce Core
Main orchestrator for commerce operations.
"""

import os
import sys
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine import ConfigManager, DatabaseManager

logger = logging.getLogger("maha-sales-engine.commerce.core")


class CommerceCore:
    """Main orchestrator for commerce operations"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_dir = base_dir / "commerce" / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        config_path = base_dir / "config" / "engine.yaml"
        self.config = ConfigManager(config_path)
        self.db = DatabaseManager(Path(self.config.get("database.path")))
        
        # Initialize engines
        from customers.engine import CustomerEngine
        from orders.engine import OrderEngine
        from cart.engine import CartEngine
        from checkout.engine import CheckoutEngine
        from payments.providers import PaymentProviderRegistry
        from payments.router import PaymentRouter
        from licenses.engine import LicenseEngine
        from subscriptions.engine import SubscriptionEngine
        from delivery.engine import DigitalDeliveryEngine
        from invoices.engine import InvoiceEngine
        from receipts.engine import ReceiptEngine
        from coupons.engine import CouponEngine
        from promotions.engine import PromotionEngine
        from tax.engine import TaxEngine
        from refunds.engine import RefundEngine
        from wallets.engine import WalletEngine
        from payouts.engine import PayoutEngine
        from fraud.engine import FraudDetectionEngine
        from events.bus import EventBus
        from queue.engine import CommerceQueue
        from audit.engine import AuditEngine
        from metrics.engine import MetricsEngine
        from health.monitor import HealthMonitor
        
        self.event_bus = EventBus()
        self.queue = CommerceQueue(self.db, max_workers=5)
        self.queue.start()
        
        self.customer_engine = CustomerEngine(self.db)
        self.order_engine = OrderEngine(self.db, self.event_bus)
        self.cart_engine = CartEngine(self.db)
        self.checkout_engine = CheckoutEngine(self.db, self.event_bus)
        self.payment_registry = PaymentProviderRegistry()
        self.payment_router = PaymentRouter(self.db, self.payment_registry)
        self.license_engine = LicenseEngine(self.db)
        self.subscription_engine = SubscriptionEngine(self.db, self.event_bus)
        self.delivery_engine = DigitalDeliveryEngine(self.db, self.output_dir)
        self.invoice_engine = InvoiceEngine(self.db, self.output_dir)
        self.receipt_engine = ReceiptEngine(self.db, self.output_dir)
        self.coupon_engine = CouponEngine(self.db)
        self.promotion_engine = PromotionEngine(self.db)
        self.tax_engine = TaxEngine(self.db)
        self.refund_engine = RefundEngine(self.db, self.event_bus)
        self.wallet_engine = WalletEngine(self.db)
        self.payout_engine = PayoutEngine(self.db, self.wallet_engine)
        self.fraud_engine = FraudDetectionEngine(self.db)
        self.audit_engine = AuditEngine(self.db, self.event_bus)
        self.metrics_engine = MetricsEngine(self.db)
        self.health_monitor = HealthMonitor(self.db, self.event_bus)
        
        logger.info("Commerce Core initialized")
    
    def start(self):
        logger.info("Commerce Platform started")
    
    def stop(self):
        self.queue.stop()
        logger.info("Commerce Platform stopped")
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "module": "commerce",
            "status": "running",
            "queue_stats": self.queue.get_stats(),
            "health": self.health_monitor.get_overall_health()
        }


def main():
    from pathlib import Path
    base_dir = Path(__file__).parent.parent.parent
    core = CommerceCore(base_dir)
    print("Commerce Core Test")
    print(f"Status: {core.get_status()}")
    core.stop()


if __name__ == "__main__":
    main()
