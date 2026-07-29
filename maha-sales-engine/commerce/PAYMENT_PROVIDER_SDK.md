# MAHA SALES ENGINE V1 - Payment Provider SDK Documentation

## Overview

Provider-agnostic payment processing SDK.

## Provider Interface

```python
class BasePaymentProvider(ABC):
    PROVIDER_NAME: str
    VERSION: str
    SUPPORTED_METHODS: List[str]
    SUPPORTED_CURRENCIES: List[str]
    
    async def initialize() -> bool
    async def authenticate() -> bool
    async def authorize(request: PaymentRequest) -> PaymentResponse
    async def capture(transaction_id: str, amount: float) -> PaymentResponse
    async def refund(transaction_id: str, amount: float, reason: str) -> PaymentResponse
    async def verify(transaction_id: str) -> PaymentResponse
    async def webhook(payload: Dict, signature: str) -> PaymentResponse
    async def health() -> Dict[str, Any]
    async def shutdown() -> bool
```

## Supported Providers

- Stripe
- PayPal
- Paddle
- Lemon Squeezy
- Gumroad
- Midtrans
- Xendit
- Coinbase Commerce
- Crypto
- Custom Provider

## Payment Flow

```
Request → Router → Provider → Authorize → Capture → Verify → Webhook
```

## Security

- Credential encryption
- Webhook signature validation
- Idempotency keys
- Replay protection