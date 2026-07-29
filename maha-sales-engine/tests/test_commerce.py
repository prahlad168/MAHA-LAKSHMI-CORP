#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Commerce Platform Tests
Unit and integration tests for the Commerce & Payment Platform module.
"""

import os
import sys
import json
import pytest
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestPaymentGateway:
    """Test payment gateway"""
    
    def test_create_payment(self):
        """Test payment creation"""
        from commerce.payment_gateway import PaymentGateway
        
        gateway = PaymentGateway()
        payment = gateway.create_payment({
            "amount": 29.99,
            "currency": "USD",
            "method": "card"
        })
        
        assert payment is not None
        assert "id" in payment


class TestOrderManager:
    """Test order manager"""
    
    def test_create_order(self):
        """Test order creation"""
        from commerce.order_manager import OrderManager
        from shared.database import DatabaseManager
        
        db_path = tempfile.mktemp(suffix=".db")
        db = DatabaseManager(db_path)
        
        try:
            manager = OrderManager(db)
            order = manager.create_order({
                "customer_id": "cust-123",
                "items": [{"product_id": "prod-123", "quantity": 1}],
                "total": 29.99
            })
            
            assert order is not None
            assert order["total"] == 29.99
        finally:
            db.close()
            Path(db_path).unlink(missing_ok=True)


class TestInvoiceManager:
    """Test invoice manager"""
    
    def test_generate_invoice(self):
        """Test invoice generation"""
        from commerce.invoice import InvoiceManager
        
        manager = InvoiceManager()
        invoice = manager.generate_invoice({
            "order_id": "order-123",
            "amount": 29.99,
            "due_date": "2024-12-31"
        })
        
        assert invoice is not None
        assert "invoice_number" in invoice


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
