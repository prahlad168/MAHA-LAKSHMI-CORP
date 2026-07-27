# 🚀 KILO SALES NODE - IMPLEMENTATION GUIDE

## Overview

Build MAHA LAKSHMI as a distributed sales system with multiple autonomous nodes, each responsible for a specific market/region. All nodes report to a central Mission Control Dashboard.

---

## Architecture

```
KILO SALES NODE #1 (Indonesia)  ─┐
KILO SALES NODE #2 (USA)        ─┤
KILO SALES NODE #3 (Brazil)     ─┤
         ...                      │
KILO SALES NODE #N (New Market) ─┘
         │
         │ Encrypted HTTPS API (mTLS + JWT)
         ▼
mahalaksmi.web.id
(Mission Control Dashboard)
```

---

## Phase 1: Foundation (Week 1)

### 1.1 Setup Mission Control Dashboard

```bash
# Deploy dashboard to production
cd mission-control
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Generate SSL certificates for dashboard
openssl req -x509 -newkey rsa:4096 -keyout dashboard.key -out dashboard.crt -days 90

# Start dashboard
uvicorn api.dashboard:app --host 0.0.0.0 --port 8000 --ssl-keyfile dashboard.key --ssl-certfile dashboard.crt
```

### 1.2 Deploy Node #1 (Indonesia)

```bash
# Copy node template
cp -r kilo-sales-nodes/node-template kilo-sales-nodes/node-1

# Configure node-1
cd kilo-sales-nodes/node-1
python3 SETUP.py

# Edit config
nano config/node.yaml
# Set:
# - node.id: "node-1"
# - node.name: "Indonesia Market Node"
# - dashboard.url: "https://mahalaksmi.web.id"
# - channels.email.username: "your-email@gmail.com"
# - channels.email.password: "your-app-password"

# Generate node SSL certificate
openssl req -x509 -newkey rsa:4096 -keyout node-1.key -out node-1.crt -days 90

# Register with dashboard
python3 core/node.py register

# Start node
python3 core/node.py start
```

### 1.3 Verify Connection

```bash
# Check node status
curl https://mahalaksmi.web.id/api/v1/nodes

# Check node heartbeat
curl https://mahalaksmi/web.id/nodes/node-1
```

---

## Phase 2: Expansion (Week 2-3)

### 2.1 Deploy Node #2 (USA)

```bash
cp -r kilo-sales-nodes/node-template kilo-sales-nodes/node-2
cd kilo-sales-nodes/node-2

# Configure for USA market
# - node.id: "node-2"
# - node.name: "USA Market Node"
# - node.region: "en"
# - node.market: "USA"
# - currency: "USD"
# - products: ["seo-bundle", "landing-template"]

python3 SETUP.py
# Edit config/node.yaml
python3 core/node.py register
python3 core/node.py start
```

### 2.2 Deploy Node #3 (Brazil)

```bash
cp -r kilo-sales-nodes/node-template kilo-sales-nodes/node-3
cd kilo-sales-nodes/node-3

# Configure for Brazil market
# - node.id: "node-3"
# - node.name: "Brazil Market Node"
# - node.region: "pt"
# - node.market: "Brazil"
# - currency: "BRL"
# - products: ["social-media-kit", "whatsapp-marketing"]

python3 SETUP.py
# Edit config/node.yaml
python3 core/node.py register
python3 core/node.py start
```

---

## Phase 3: Scaling (Week 4+)

### 3.1 Add More Nodes

Repeat the process for each new market:
- Node #4: China
- Node #5: UAE
- Node #6: UK
- Node #7: Australia
- Node #N: Any new market

### 3.2 Automation

Create automated deployment scripts:

```bash
#!/bin/bash
# deploy-node.sh

NODE_ID=$1
MARKET=$2
REGION=$3

cp -r kilo-sales-nodes/node-template kilo-sales-nodes/$NODE_ID
cd kilo-sales-nodes/$NODE_ID

# Auto-configure based on market
python3 SETUP.py --market $MARKET --region $REGION

# Generate SSL
openssl req -x509 -newkey rsa:4096 -keyout $NODE_ID.key -out $NODE_ID.crt -days 90 -nodes -subj "/CN=$NODE_ID"

# Register and start
python3 core/node.py register
python3 core/node.py start

echo "✅ Node $NODE_ID deployed for $MARKET market"
```

---

## Security Checklist

- [ ] mTLS certificates generated for each node
- [ ] Dashboard CA certificate distributed to all nodes
- [ ] JWT tokens configured with 24h expiry
- [ ] Node secrets stored securely (use Vault)
- [ ] Firewall rules: nodes can only reach dashboard API
- [ ] Rate limiting enabled on dashboard
- [ ] Audit logging enabled
- [ ] Certificate rotation reminder set (90 days)

---

## Monitoring Setup

### Dashboard Monitoring
- Node heartbeats: every 60 seconds
- Daily reports: every 23:59 local time
- Alert if node offline > 15 minutes
- Alert if error rate > 10%

### Node Monitoring
- CPU usage alerts
- Memory usage alerts
- Disk space alerts
- API response time monitoring
- Failed request tracking

---

## Troubleshooting

### Node can't connect to dashboard
1. Check SSL certificates: `openssl s_client -connect mahalaksmi.web.id:443`
2. Verify JWT token: `python3 core/node.py status`
3. Check firewall rules
4. Verify dashboard is running: `curl https://mahalaksmi.web.id/health`

### Node not appearing in dashboard
1. Check node logs: `tail -f logs/node.log`
2. Verify registration: `python3 core/node.py register`
3. Check dashboard logs
4. Verify node ID matches in config

### Performance issues
1. Check CPU/memory usage
2. Review database queries
3. Check network latency to dashboard
4. Review outreach queue size

---

## Cost Estimate

### Infrastructure
- Dashboard hosting: $5-20/month (VPS)
- Node hosting: $5-10/month per node (VPS)
- SSL certificates: Free (Let's Encrypt) or $10/year
- Domain: $10/year

### Total for 5 nodes: ~$50-70/month

---

## Next Steps

1. ✅ Deploy dashboard to production
2. ✅ Deploy Node #1 (Indonesia)
3. ✅ Deploy Node #2 (USA)
4. ✅ Deploy Node #3 (Brazil)
5. ⬜ Setup monitoring and alerts
6. ⬜ Create product listings
7. ⬜ Launch first marketing campaign
8. ⬜ Achieve first sale

---

**Document Version:** 1.0.0  
**Created:** 2026-07-27  
**Status:** 🚀 READY FOR DEPLOYMENT
