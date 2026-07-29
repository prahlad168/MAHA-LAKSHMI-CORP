#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Payment Provider SDK
Base classes and interfaces for payment providers.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.commerce.payments")


class PaymentStatus(Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    VOIDED = "voided"
    EXPIRED = "expired"


class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    CRYPTO = "crypto"
    BANK_TRANSFER = "bank_transfer"
    E_WALLET = "e_wallet"


@dataclass
class PaymentRequest:
    amount: float
    currency: str
    method: str
    customer_id: str
    order_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PaymentResponse:
    success: bool
    transaction_id: str
    status: str
    amount: float
    currency: str
    provider: str
    raw_response: Dict[str, Any]
    error_message: Optional[str] = None


class BasePaymentProvider(ABC):
    """Base class for payment providers"""
    
    PROVIDER_NAME: str = ""
    VERSION: str = "1.0.0"
    SUPPORTED_METHODS: List[str] = []
    SUPPORTED_CURRENCIES: List[str] = []
    
    def __init__(self, config: Dict[str, Any], credential_manager):
        self.config = config
        self.credential_manager = credential_manager
        self.provider_name = config.get("provider_name", self.PROVIDER_NAME)
        self.logger = logging.getLogger(f"maha-sales-engine.commerce.payments.{self.provider_name}")
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize provider connection"""
        pass
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with payment provider"""
        pass
    
    @abstractmethod
    async def authorize(self, request: PaymentRequest) -> PaymentResponse:
        """Authorize payment"""
        pass
    
    @abstractmethod
    async def capture(self, transaction_id: str, amount: float) -> PaymentResponse:
        """Capture authorized payment"""
        pass
    
    @abstractmethod
    async def refund(self, transaction_id: str, amount: float, reason: str) -> PaymentResponse:
        """Refund payment"""
        pass
    
    @abstractmethod
    async def verify(self, transaction_id: str) -> PaymentResponse:
        """Verify payment status"""
        pass
    
    @abstractmethod
    async def webhook(self, payload: Dict[str, Any], signature: str) -> PaymentResponse:
        """Process webhook"""
        pass
    
    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Check provider health"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """Cleanup and shutdown"""
        pass


class PaymentProviderRegistry:
    """Registry for payment providers"""
    
    def __init__(self):
        self._providers: Dict[str, BasePaymentProvider] = {}
        self._configs: Dict[str, Dict[str, Any]] = {}
    
    def register(self, provider: BasePaymentProvider, config: Dict[str, Any]):
        self._providers[provider.PROVIDER_NAME] = provider
        self._configs[provider.PROVIDER_NAME] = config
        logger.info(f"Payment provider registered: {provider.PROVIDER_NAME}")
    
    def get_provider(self, provider_name: str) -> Optional[BasePaymentProvider]:
        return self._providers.get(provider_name)
    
    def get_all_providers(self) -> List[str]:
        return list(self._providers.keys())


def main():
    print("Payment Provider SDK initialized")


if __name__ == "__main__":
    main()
