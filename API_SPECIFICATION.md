# API SPECIFICATION - MAHA SALES ENGINE V1

**Version:** 1.0.0  
**Status:** Approved  
**Parent Document:** MASTER_BLUEPRINT.md, SYSTEM_ARCHITECTURE.md  
**Created:** 2026-07-27

---

## 1. API Overview

The MAHA Sales Engine exposes two types of APIs:

1. **Node → Dashboard API** - Encrypted HTTPS API for reporting to `mahalaksmi.web.id`
2. **Local Health API** - Local HTTP endpoint for health checks

All external communication uses **HTTPS only** with **mTLS** and **JWT** authentication.

---

## 2. Node → Dashboard API

### Base URL
```
https://mahalaksmi.web.id/api/v1/sales-node
```

### Authentication
- **Method:** mTLS + JWT
- **Header:** `Authorization: Bearer <JWT_TOKEN>`
- **Header:** `X-Node-ID: <node_id>`
- **Certificate:** Client certificate required

### Common Headers
```
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>
X-Node-ID: node-1
X-Timestamp: 2026-07-27T09:00:00Z
X-Signature: <HMAC_SHA256>
```

---

## 3. Endpoints

### 3.1 Heartbeat

**Purpose:** Report node health and liveness.

**Endpoint:** `POST /heartbeat`

**Request:**
```json
{
  "node_id": "node-1",
  "status": "running",
  "timestamp": "2026-07-27T09:00:00Z",
  "metrics": {
    "cpu_usage": 0.0,
    "memory_usage": 8.5,
    "disk_usage": 45.2,
    "uptime": 3600,
    "active_modules": ["core", "scheduler", "products"],
    "errors_count": 0,
    "warnings_count": 0
  }
}
```

**Response (200 OK):**
```json
{
  "status": "received",
  "timestamp": "2026-07-27T09:00:05Z"
}
```

**Schedule:** Every 60 seconds

---

### 3.2 Daily Report

**Purpose:** Transmit daily sales and performance metrics.

**Endpoint:** `POST /report`

**Request:**
```json
{
  "node_id": "node-1",
  "report_date": "2026-07-26",
  "metrics": {
    "leads_generated": 45,
    "outreach_sent": 120,
    "responses_received": 18,
    "proposals_sent": 8,
    "deals_closed": 3,
    "revenue_usd": 350.00,
    "revenue_idr": 5600000,
    "ceo_share_usd": 280.00,
    "ceo_share_idr": 4480000,
    "conversion_rate": 2.5
  },
  "products": [
    {
      "product_id": "social-media-kit",
      "sales": 2,
      "revenue": 38.00
    }
  ],
  "channels": [
    {
      "channel": "whatsapp",
      "sent": 60,
      "responses": 15,
      "conversion_rate": 0.18
    }
  ],
  "countries": [
    {
      "country": "Indonesia",
      "leads": 20,
      "revenue": 200.00,
      "deals": 2
    }
  ],
  "insights": {
    "best_channel": "whatsapp",
    "best_market": "Indonesia",
    "best_product": "Social Media Kit Pro",
    "best_time": "09:00-11:00 WIB",
    "response_rate": 0.15
  },
  "recommendations": [
    "Increase WhatsApp outreach by 20%",
    "Focus on E-Commerce segment"
  ],
  "sync_log": [
    {
      "timestamp": "2026-07-27T09:00:00Z",
      "operation": "daily_report",
      "status": "success"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "status": "received",
  "report_id": "RPT-20260726-node1",
  "actions": [
    "increase_whatsapp_outreach",
    "focus_on_ecommerce_segment"
  ]
}
```

**Schedule:** Every 23:59 local time

---

### 3.3 Get Commands

**Purpose:** Receive commands from dashboard.

**Endpoint:** `GET /commands`

**Query Parameters:**
- `since` - ISO timestamp of last command check

**Request:**
```
GET /api/v1/sales-node/commands?since=2026-07-27T08:00:00Z
```

**Response (200 OK):**
```json
{
  "commands": [
    {
      "command_id": "CMD-001",
      "type": "pause_outreach",
      "params": {
        "duration": 3600
      },
      "priority": "high",
      "timestamp": "2026-07-27T08:30:00Z"
    },
    {
      "command_id": "CMD-002",
      "type": "adjust_pricing",
      "params": {
        "product_id": "social-media-kit",
        "new_price": 249000
      },
      "priority": "medium",
      "timestamp": "2026-07-27T08:35:00Z"
    }
  ]
}
```

**Schedule:** Every 30 seconds

---

### 3.4 Get Products

**Purpose:** Sync product catalog from dashboard.

**Endpoint:** `GET /products`

**Query Parameters:**
- `market` - Optional market filter
- `language` - Optional language filter

**Request:**
```
GET /api/v1/sales-node/products?market=id&language=id
```

**Response (200 OK):**
```json
{
  "products": [
    {
      "product_id": "social-media-kit",
      "name": "Social Media Kit Pro",
      "price_usd": 19.00,
      "price_idr": 285000,
      "description": "500+ templates...",
      "features": ["instagram", "facebook", "tiktok"],
      "url": "https://mahalaksmi.web.id/products/social-media-kit"
    }
  ],
  "updated_at": "2026-07-27T00:00:00Z"
}
```

**Schedule:** Daily or on-demand

---

### 3.5 Node Registration

**Purpose:** Register node with dashboard on first run.

**Endpoint:** `POST /register`

**Request:**
```json
{
  "node_id": "node-1",
  "name": "Indonesia Market Node",
  "region": "id",
  "market": "Indonesia",
  "capabilities": ["email", "whatsapp", "linkedin"],
  "products": ["social-media-kit", "business-kit"],
  "version": "1.0.0"
}
```

**Response (201 Created):**
```json
{
  "node_id": "node-1",
  "status": "registered",
  "dashboard_url": "https://mahalaksmi.web.id",
  "next_report_at": "2026-07-27T10:00:00Z"
}
```

---

## 4. Local Health API

### 4.1 Health Check

**Purpose:** Local health monitoring.

**Endpoint:** `GET /health`

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "MAHA Sales Engine V1",
  "node_id": "node-1",
  "timestamp": "2026-07-27T09:00:00Z",
  "version": "1.0.0",
  "uptime": 3600,
  "modules": {
    "core": "running",
    "scheduler": "running",
    "products": "running",
    "market-intelligence": "running",
    "marketplaces": "running",
    "content": "running",
    "analytics": "running",
    "reporter": "running"
  }
}
```

---

## 5. Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "node_id",
      "reason": "required"
    },
    "timestamp": "2026-07-27T09:00:00Z"
  }
}
```

### HTTP Status Codes
| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Continue |
| 201 | Created | Registration successful |
| 400 | Bad Request | Fix request format |
| 401 | Unauthorized | Re-authenticate |
| 404 | Not Found | Check endpoint |
| 429 | Rate Limited | Retry after delay |
| 500 | Server Error | Retry with backoff |
| 503 | Unavailable | Retry later |

---

## 6. Rate Limiting

- **Heartbeat:** 1 request per 60 seconds per node
- **Report:** 1 request per 86400 seconds per node
- **Commands:** 1 request per 30 seconds per node
- **Products:** 1 request per 86400 seconds per node
- **Registration:** 3 retries, then manual intervention

---

## 7. Security

### TLS Configuration
- Protocol: TLS 1.3
- Cipher Suites: TLS_AES_256_GCM_SHA384, TLS_CHACHA20_POLY1305_SHA256
- Certificate: ECDSA P-256 or RSA 2048+
- mTLS: Required
- Certificate Rotation: Every 90 days

### JWT Token Structure
```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "node-1-key"
  },
  "payload": {
    "sub": "node-1",
    "name": "Indonesia Market Node",
    "region": "id",
    "iat": 1690000000,
    "exp": 1690086400,
    "scope": ["report", "heartbeat", "commands"]
  },
  "signature": "RS256_SIGNATURE"
}
```

### Request Signing
All POST requests include HMAC-SHA256 signature:
```python
signature = hmac.new(
    node_secret.encode(),
    json.dumps(payload, sort_keys=True).encode(),
    hashlib.sha256
).hexdigest()
```

---

## 8. Data Encryption

- **In Transit:** TLS 1.3 with mTLS
- **At Rest:** SQLite with optional SQLCipher
- **Logs:** AES-256-GCM encrypted
- **Config:** Encrypted with age or GPG

---

## 9. Timeouts and Retries

| Operation | Timeout | Retries | Backoff |
|-----------|---------|---------|---------|
| Heartbeat | 10s | 3 | 30s |
| Daily Report | 30s | 2 | 60s |
| Commands | 10s | 3 | 30s |
| Products | 30s | 2 | 60s |

---

## 10. Versioning

- API Version: `v1`
- Backward compatibility required
- Breaking changes require new version
- Deprecation notices: 30 days minimum

---

**Approved By:** CEO / Lead Architect  
**Date:** 2026-07-27  
**Next Review:** 2026-08-27
