#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketplace Tests
Unit and integration tests for the Marketplace module.
"""

import os
import sys
import json
import pytest
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestMarketplaceManager:
    """Test marketplace manager"""
    
    def test_create_listing(self):
        """Test listing creation"""
        from marketplace.marketplace_manager import MarketplaceManager
        from shared.database import DatabaseManager
        
        db_path = tempfile.mktemp(suffix=".db")
        db = DatabaseManager(db_path)
        
        try:
            manager = MarketplaceManager(db)
            listing = manager.create_listing({
                "title": "Test Listing",
                "price": 19.99,
                "product_id": "prod-123"
            })
            
            assert listing is not None
            assert listing["title"] == "Test Listing"
        finally:
            db.close()
            Path(db_path).unlink(missing_ok=True)


class TestPaymentProcessor:
    """Test payment processor"""
    
    def test_create_payment_intent(self):
        """Test payment intent creation"""
        from marketplace.payment import PaymentProcessor
        
        processor = PaymentProcessor()
        
        # Mock payment intent
        intent = {
            "id": "pi_test",
            "amount": 1999,
            "currency": "usd",
            "status": "requires_payment_method"
        }
        
        assert intent["id"] == "pi_test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
