# MAHA SALES ENGINE V1 - API Reference

REST API for marketplace connector.

## Base URL

```
http://localhost:8000/marketplace
```

## Authentication

All endpoints require API key authentication:

```bash
Authorization: Bearer your-api-key
```

## Endpoints

### Accounts

#### Create Account
```http
POST /marketplace/accounts
Content-Type: application/json

{
  "provider": "gumroad",
  "name": "My Gumroad Account",
  "credentials": {"api_key": "key"},
  "default": true
}
```

#### List Accounts
```http
GET /marketplace/accounts
```

#### Update Account
```http
PUT /marketplace/accounts/{id}
```

#### Delete Account
```http
DELETE /marketplace/accounts/{id}
```

#### Test Connection
```http
POST /marketplace/connect
```

### Publication

#### Publish Product
```http
POST /marketplace/publish
Content-Type: application/json

{
  "product_id": "prod-001",
  "account_id": "acc-001",
  "provider": "gumroad"
}
```

#### Bulk Publish
```http
POST /marketplace/publish/bulk
Content-Type: application/json

[
  {"product_id": "prod-001", "account_id": "acc-001"},
  {"product_id": "prod-002", "account_id": "acc-001"}
]
```

### Synchronization

#### Sync All Products
```http
POST /marketplace/sync
```

#### Sync Single Product
```http
POST /marketplace/sync/{productId}
```

### Data Retrieval

#### List Products
```http
GET /marketplace/products
```

#### List Publications
```http
GET /marketplace/publications
```

#### List Errors
```http
GET /marketplace/errors
```

#### Get Reports
```http
GET /marketplace/reports
```

#### Get Metrics
```http
GET /marketplace/metrics
```

### Health

#### Health Check
```http
GET /marketplace/health
```

## Response Codes

- `200 OK` - Success
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Missing/invalid API key
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Example Response

```json
{
  "publication_id": "pub-1234567890-abc123",
  "success": true,
  "status": "published",
  "marketplace_product_id": "gumroad-abc123",
  "marketplace_url": "https://gumroad.com/l/abc123",
  "message": "Publication successful"
}
```
