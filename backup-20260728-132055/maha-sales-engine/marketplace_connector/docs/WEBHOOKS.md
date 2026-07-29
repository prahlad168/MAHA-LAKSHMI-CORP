# MAHA SALES ENGINE V1 - Webhooks

Webhook processing engine for Gumroad marketplace events.

## Supported Events

- `product_updated` - Product information changed
- `product_deleted` - Product removed from marketplace
- `purchase` - New sale completed
- `refund` - Refund issued
- `chargeback` - Chargeback received

## Security

### Signature Verification

All webhooks are verified using HMAC-SHA256 signatures:

```python
def _verify_signature(self, payload, signature, provider):
    expected = hmac.new(
        self.webhook_secret.encode(),
        json.dumps(payload).encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### Replay Protection

Each webhook event has a unique ID. Processed events are tracked to prevent replay attacks.

## Processing Flow

1. Receive webhook payload
2. Verify signature
3. Check for duplicate (replay protection)
4. Parse event type
5. Route to handler
6. Update internal state
7. Log audit entry
8. Return acknowledgment

## Configuration

```python
webhook_engine = WebhookEngine(
    provider=provider,
    audit=audit_engine,
    secret="your-webhook-secret"
)
```

## Error Handling

Invalid webhooks are rejected with:
- 400 Bad Request - Invalid signature
- 409 Conflict - Duplicate event
- 500 Internal Server Error - Processing failure

## Audit Logging

Every webhook is logged with:
- Event ID
- Event type
- Provider
- Payload hash
- Processing status
- Timestamp
