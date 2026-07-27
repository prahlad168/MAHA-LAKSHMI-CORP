# KILO SALES NODE - MASTER SPECIFICATION

## Architecture Overview

```
KILO SALES NODE #1  ─┐
KILO SALES NODE #2  ─┤
KILO SALES NODE #3  ─┤
         ...          │
KILO SALES NODE #N  ─┘
         │
         │ Encrypted HTTPS API (mTLS + JWT)
         ▼
mahalaksmi.web.id
(Mission Control Dashboard)
```

---

## NODE RESPONSIBILITIES

Each KILO SALES NODE is a **self-contained sales unit** responsible for:

1. **Lead Generation** - Find and qualify leads in assigned market
2. **Outreach** - Send emails, WhatsApp, LinkedIn messages
3. **Follow-up** - Automated follow-up sequences
4. **Deal Closing** - Negotiate and close deals
5. **Payment Processing** - Handle transactions
6. **Reporting** - Send metrics to central dashboard
7. **Learning** - Improve based on performance data

---

## NODE STRUCTURE

```
kilo-sales-nodes/node-{N}/
├── core/
│   ├── node.py                 # Main node orchestrator
│   ├── sales-agent.py          # Sales logic
│   ├── finance-agent.py        # Payment/revenue tracking
│   ├── market-analyzer.py      # Market-specific analysis
│   └── reporter.py             # Report to dashboard
├── db/
│   ├── node.db                 # Local SQLite database
│   └── schema.sql              # Database schema
├── products/
│   ├── listings.json           # Product listings
│   └── pricing.json            # Market-specific pricing
├── channels/
│   ├── email/
│   ├── whatsapp/
│   ├── linkedin/
│   └── sms/
├── api/
│   ├── client.py               # HTTPS client to dashboard
│   ├── auth.py                 # JWT + mTLS authentication
│   └── webhook.py              # Receive commands from dashboard
├── logs/
│   ├── node.log                # Main log
│   ├── sales.log               # Sales activities
│   └── errors.log              # Errors only
├── config/
│   └── node.yaml               # Node configuration
└── README.md                   # Node documentation
```

---

## NODE CONFIGURATION (node.yaml)

```yaml
node:
  id: "node-1"
  name: "Indonesia Market Node"
  region: "id"
  market: "Indonesia"
  currency: "IDR"
  language: "id"
  
  dashboard:
    url: "https://mahalaksmi.web.id"
    api_endpoint: "/api/v1/nodes/report"
    auth_token: "JWT_TOKEN_HERE"
    cert_path: "/etc/ssl/node-1.crt"
    key_path: "/etc/ssl/node-1.key"
    ca_path: "/etc/ssl/ca.crt"
  
  sales:
    daily_leads_target: 50
    daily_outreach_target: 100
    daily_revenue_target: 500000  # IDR
    products:
      - "social-media-kit"
      - "business-kit"
      - "whatsapp-marketing"
  
  channels:
    email:
      enabled: true
      smtp_host: "smtp.gmail.com"
      smtp_port: 587
      username: "node-1@mahalaksmi.web.id"
      password: "APP_PASSWORD"
    whatsapp:
      enabled: true
      api_url: "https://api.whatsapp.com"
      token: "WHATSAPP_TOKEN"
    linkedin:
      enabled: false
      api_url: "https://api.linkedin.com"
      token: "LINKEDIN_TOKEN"
  
  database:
    path: "./db/node.db"
    backup_interval: 86400  # 24 hours
  
  logging:
    level: "INFO"
    max_size: "10MB"
    backup_count: 5
  
  features:
    auto_followup: true
    auto_pricing: true
    auto_optimization: true
    ai_recommendations: true
```

---

## ENCRYPTED HTTPS API SPECIFICATION

### Authentication Flow

```
1. Node → Dashboard: POST /api/v1/auth/login
   Body: { "node_id": "node-1", "secret": "NODE_SECRET" }
   
2. Dashboard → Node: 200 OK
   Body: { "token": "JWT_TOKEN", "expires_in": 86400 }
   
3. Node → Dashboard: All subsequent requests
   Header: Authorization: Bearer JWT_TOKEN
   Header: X-Node-ID: node-1
   TLS: mTLS with client certificate
```

### API Endpoints

#### 1. Node Registration
```
POST /api/v1/nodes/register
Headers: Authorization: Bearer <token>
Body: {
  "node_id": "node-1",
  "name": "Indonesia Market Node",
  "region": "id",
  "market": "Indonesia",
  "capabilities": ["email", "whatsapp", "linkedin"],
  "products": ["social-media-kit", "business-kit"],
  "version": "1.0.0"
}
Response: 201 Created
{
  "node_id": "node-1",
  "status": "registered",
  "dashboard_url": "https://mahalaksmi.web.id",
  "next_report_at": "2026-07-27T10:00:00Z"
}
```

#### 2. Heartbeat
```
POST /api/v1/nodes/heartbeat
Headers: Authorization: Bearer <token>
Body: {
  "node_id": "node-1",
  "status": "running",
  "timestamp": "2026-07-27T09:00:00Z",
  "metrics": {
    "cpu_usage": 0.0,
    "memory_usage": 8.5,
    "active_leads": 45,
    "queue_size": 12
  }
}
Response: 200 OK
```

#### 3. Sales Report
```
POST /api/v1/nodes/report
Headers: Authorization: Bearer <token>
Body: {
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
    "ceo_share_idr": 4480000
  },
  "top_products": [
    {"product_id": "social-media-kit", "sales": 2, "revenue": 38.00},
    {"product_id": "business-kit", "sales": 1, "revenue": 99.00}
  ],
  "top_channels": [
    {"channel": "whatsapp", "conversion_rate": 0.18},
    {"channel": "email", "conversion_rate": 0.07}
  ],
  "insights": {
    "best_time": "09:00-11:00 WIB",
    "best_segment": "E-Commerce",
    "best_country": "Indonesia"
  }
}
Response: 200 OK
{
  "status": "received",
  "report_id": "RPT-20260726-node1",
  "actions": [
    "increase_whatsapp_outreach",
    "focus_on_ecommerce_segment"
  ]
}
```

#### 4. Command Polling
```
GET /api/v1/nodes/commands?since=2026-07-27T08:00:00Z
Headers: Authorization: Bearer <token>
Response: 200 OK
{
  "commands": [
    {
      "command_id": "CMD-001",
      "type": "pause_outreach",
      "params": {"duration": 3600},
      "priority": "high",
      "timestamp": "2026-07-27T08:30:00Z"
    },
    {
      "command_id": "CMD-002",
      "type": "adjust_pricing",
      "params": {"product_id": "social-media-kit", "new_price": 249000},
      "priority": "medium",
      "timestamp": "2026-07-27T08:35:00Z"
    }
  ]
}
```

#### 5. Product Sync
```
GET /api/v1/products?market=id&language=id
Headers: Authorization: Bearer <token>
Response: 200 OK
{
  "products": [
    {
      "product_id": "social-media-kit",
      "name": "Social Media Kit Pro",
      "price_idr": 285000,
      "price_usd": 19.00,
      "description": "500+ templates...",
      "features": ["instagram", "facebook", "tiktok"],
      "url": "https://mahalaksmi.web.id/products/social-media-kit"
    }
  ],
  "updated_at": "2026-07-27T00:00:00Z"
}
```

---

## ENCRYPTION SPECIFICATION

### TLS Configuration
- **Protocol:** TLS 1.3
- **Cipher Suites:** TLS_AES_256_GCM_SHA384, TLS_CHACHA20_POLY1305_SHA256
- **Certificate:** ECDSA P-256 or RSA 2048+
- **mTLS:** Required - both client and server certificates
- **Certificate Rotation:** Every 90 days

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

### Data Encryption at Rest
- Database: SQLite with SQLCipher encryption
- Logs: Encrypted with AES-256-GCM
- Config: Encrypted with age or GPG

---

## MISSION CONTROL DASHBOARD

### URL Structure
```
https://mahalaksmi.web.id/
├── /                      # Main dashboard
├── /nodes                 # Node management
│   ├── /node-1           # Indonesia node
│   ├── /node-2           # USA node
│   └── /node-3           # Brazil node
├── /revenue              # Revenue dashboard
├── /products             # Product management
├── /reports              # Reports
├── /api/v1/              # REST API
│   ├── /nodes            # Node endpoints
│   ├── /reports          # Report endpoints
│   └── /commands         # Command endpoints
└── /admin                # Admin panel
```

### Dashboard Features
1. **Revenue Dashboard** - Real-time revenue by node, product, channel
2. **Daily Performance** - Daily metrics for all nodes
3. **Marketplace Status** - Product listing status across platforms
4. **Country Performance** - Revenue and conversion by country
5. **Product Performance** - Sales by product
6. **AI Recommendations** - Automated suggestions for each node
7. **Alerts** - Node downtime, low performance, errors
8. **CEO Report** - Daily aggregated report

---

## NODE DEPLOYMENT

### Prerequisites
- Linux server (Ubuntu 22.04+)
- Python 3.11+
- OpenSSL for certificates
- Systemd or Docker

### Deployment Steps
```bash
# 1. Clone node repository
git clone https://github.com/prahlad168/MAHA-LAKSHMI-CORP.git
cd MAHA-LAKSHMI-CORP/kilo-sales-nodes/node-1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate certificates
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 90

# 4. Configure node
cp config/node.example.yaml config/node.yaml
# Edit with your node credentials

# 5. Register node with dashboard
python3 core/node.py register

# 6. Start node
python3 core/node.py start
# OR with systemd:
systemctl enable --now kilo-sales-node-1
```

---

## SCALING PLAN

### Phase 1: Single Node (Current)
- Node 1: Indonesia market
- Manual dashboard
- Local database

### Phase 2: 3 Nodes
- Node 1: Indonesia
- Node 2: USA/English
- Node 3: Brazil/Portuguese
- Central dashboard with basic aggregation

### Phase 3: 5 Nodes
- Node 4: China
- Node 5: UAE/MENA
- Advanced AI recommendations
- Automated product sync

### Phase 4: N Nodes
- Node N: Any new market
- Self-service node deployment
- Auto-scaling based on demand

---

## SECURITY CONSIDERATIONS

1. **mTLS Required** - All nodes must present valid certificates
2. **JWT Tokens** - Short-lived (24h), rotate regularly
3. **Rate Limiting** - Max 100 requests/minute per node
4. **IP Whitelisting** - Nodes can only connect from registered IPs
5. **Audit Logging** - All node activities logged centrally
6. **Secret Management** - Use HashiCorp Vault or similar
7. **Network Segmentation** - Nodes in separate VPCs

---

## MONITORING

### Node Health Metrics
- CPU usage
- Memory usage
- Disk usage
- Network connectivity
- API response time
- Error rate

### Business Metrics
- Leads generated
- Outreach sent
- Responses received
- Deals closed
- Revenue
- Conversion rate

### Alerting
- Node down > 5 minutes
- Error rate > 10%
- Revenue drop > 50% day-over-day
- No heartbeat for > 15 minutes

---

**Document Version:** 1.0.0  
**Created:** 2026-07-27  
**Status:** 🚀 READY FOR IMPLEMENTATION
