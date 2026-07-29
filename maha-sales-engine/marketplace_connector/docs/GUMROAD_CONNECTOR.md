# MAHA SALES ENGINE V1 - Gumroad Connector

Gumroad marketplace provider implementation for MAHA SALES ENGINE V1.

## Configuration

```python
config = {
    "api_key": "your-gumroad-api-key"
}
provider = GumroadProvider(config)
```

## Supported Operations

- `connect()` - Connect to Gumroad API
- `validate()` - Validate credentials
- `upload_file()` - Upload product files
- `upload_thumbnail()` - Upload thumbnail images
- `create_listing()` - Create product listing
- `update_listing()` - Update existing listing
- `publish()` - Publish listing
- `archive()` - Archive listing
- `delete()` - Delete listing
- `sync()` - Sync product data
- `health()` - Check provider health

## Payload Format

```json
{
  "name": "Product Name",
  "description": "Product description",
  "price": 29.99,
  "currency": "USD",
  "tags": ["digital", "product"],
  "is_published": true,
  "file_url": "https://example.com/product.zip",
  "thumbnail_url": "https://example.com/thumb.png"
}
```

## Publication Status

- draft
- queued
- validating
- uploading
- processing
- published
- hidden
- archived
- deleted
- failed
- retrying
- cancelled

## Rate Limits

Gumroad API rate limits apply. The connector implements:
- Exponential backoff for retries
- Circuit breaker pattern
- Request queuing

## Error Handling

Errors are classified as:
- `PROVIDER_ERROR` - Gumroad API errors
- `VALIDATION_ERROR` - Package validation failures
- `PUBLICATION_ERROR` - Publication failures
- `NETWORK_ERROR` - Network connectivity issues
