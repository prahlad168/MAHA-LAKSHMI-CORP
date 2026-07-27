#!/usr/bin/env python3
"""
KILO SALES NODE - Node Implementation Template
This is the base template for all sales nodes.
Copy this directory to create node-1, node-2, node-3, etc.
"""

import os
import sys
from pathlib import Path

# Node configuration
NODE_ID = "node-template"
NODE_NAME = "Template Sales Node"
REGION = "us"
MARKET = "USA"
CURRENCY = "USD"
LANGUAGE = "en"

# Paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
DB_DIR = BASE_DIR / "db"
LOG_DIR = BASE_DIR / "logs"

# Create directories
for directory in [CONFIG_DIR, DB_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True)

# Create default config
config_content = f"""node:
  id: "{NODE_ID}"
  name: "{NODE_NAME}"
  region: "{REGION}"
  market: "{MARKET}"
  currency: "{CURRENCY}"
  language: "{LANGUAGE}"
  
  dashboard:
    url: "https://mahalaksmi.web.id"
    api_endpoint: "/api/v1/nodes/report"
    auth_token: "YOUR_JWT_TOKEN_HERE"
    cert_path: "/etc/ssl/{NODE_ID}.crt"
    key_path: "/etc/ssl/{NODE_ID}.key"
    ca_path: "/etc/ssl/ca.crt"
  
  sales:
    daily_leads_target: 50
    daily_outreach_target: 100
    daily_revenue_target: 100  # USD
    products:
      - "social-media-kit"
      - "seo-bundle"
      - "whatsapp-marketing"
  
  channels:
    email:
      enabled: true
      smtp_host: "smtp.gmail.com"
      smtp_port: 587
      username: "your-email@gmail.com"
      password: "your-app-password"
    whatsapp:
      enabled: false
      api_url: "https://api.whatsapp.com"
      token: "YOUR_WHATSAPP_TOKEN"
    linkedin:
      enabled: false
      api_url: "https://api.linkedin.com"
      token: "YOUR_LINKEDIN_TOKEN"
  
  database:
    path: "./db/{NODE_ID}.db"
    backup_interval: 86400
  
  logging:
    level: "INFO"
    max_size: "10MB"
    backup_count: 5
  
  features:
    auto_followup: true
    auto_pricing: true
    auto_optimization: true
    ai_recommendations: true
"""

config_path = CONFIG_DIR / "node.yaml"
if not config_path.exists():
    with open(config_path, "w") as f:
        f.write(config_content)
    print(f"✅ Created config: {config_path}")

# Create requirements.txt
requirements = """requests>=2.31
pyyaml>=6.0
psutil>=5.9
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
sqlalchemy>=2.0
python-dotenv>=1.0
cryptography>=41.0
pyjwt>=2.8
"""

requirements_path = BASE_DIR / "requirements.txt"
if not requirements_path.exists():
    with open(requirements_path, "w") as f:
        f.write(requirements)
    print(f"✅ Created requirements: {requirements_path}")

# Create README
readme = f"""# KILO SALES NODE - {NODE_NAME}

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure node:**
   ```bash
   cp config/node.yaml config/node.yaml
   # Edit with your credentials
   ```

3. **Generate SSL certificates:**
   ```bash
   openssl req -x509 -newkey rsa:4096 -keyout {NODE_ID}.key -out {NODE_ID}.crt -days 90
   ```

4. **Register with dashboard:**
   ```bash
   python3 core/node.py register
   ```

5. **Start node:**
   ```bash
   python3 core/node.py start
   ```

## Node Information

- **Node ID:** {NODE_ID}
- **Name:** {NODE_NAME}
- **Region:** {REGION}
- **Market:** {MARKET}
- **Currency:** {CURRENCY}
- **Language:** {LANGUAGE}

## Directory Structure

```
{NODE_ID}/
├── core/
│   ├── node.py              # Main orchestrator
│   ├── sales-agent.py       # Sales logic
│   ├── finance-agent.py     # Payment tracking
│   ├── market-analyzer.py   # Market analysis
│   └── reporter.py          # Report to dashboard
├── api/
│   ├── client.py            # HTTPS API client
│   └── webhook.py           # Webhook handler
├── db/
│   └── {NODE_ID}.db         # Local SQLite database
├── logs/
│   ├── node.log
│   ├── sales.log
│   └── errors.log
├── config/
│   └── node.yaml            # Node configuration
└── README.md
```

## API Endpoints

- Register: `POST /api/v1/nodes/register`
- Heartbeat: `POST /api/v1/nodes/heartbeat`
- Report: `POST /api/v1/nodes/report`
- Commands: `GET /api/v1/nodes/commands`

## Security

- mTLS with client certificates
- JWT authentication
- Encrypted HTTPS (TLS 1.3)
- Request signing

## Monitoring

- Health check: `GET /health`
- Dashboard: `https://mahalaksmi.web.id/nodes/{NODE_ID}`

---

**Version:** 1.0.0  
**Created:** 2026-07-27
"""

readme_path = BASE_DIR / "README.md"
if not readme_path.exists():
    with open(readme_path, "w") as f:
        f.write(readme)
    print(f"✅ Created README: {readme_path}")

print(f"\n🚀 Node template ready: {NODE_ID}")
print(f"📁 Directory: {BASE_DIR}")
print(f"\nNext steps:")
print(f"1. Edit config/node.yaml with your credentials")
print(f"2. Generate SSL certificates")
print(f"3. Register with dashboard: python3 core/node.py register")
print(f"4. Start node: python3 core/node.py start")
