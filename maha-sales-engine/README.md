# 🚀 MAHA SALES ENGINE V1

**Autonomous Digital Sales Engine** - Operates 24/7 to generate sustainable digital product sales through compliant, measurable, and scalable automation.

---

## 🏗️ Architecture

```
Windows Service / Linux Daemon
        ↓
    Core Engine
        ↓
    Scheduler
        ↓
Business Modules
    ├── Product Manager
    ├── Market Intelligence
    ├── Marketplace Manager
    ├── Content Engine
    ├── Analytics
    └── Performance Reporter
        ↓
    Local Database (SQLite)
        ↓
Encrypted HTTPS API (mTLS + JWT)
        ↓
mahalaksmi.web.id
(Mission Control Dashboard)
```

---

## 📦 Modules

### Module 1: Core Engine
- Application lifecycle
- Configuration management
- Dependency management
- Logging
- Health monitoring

### Module 2: Scheduler
- Job scheduling
- Retry logic
- Queue management
- Background processing
- 24/7 operation

### Module 3: Product Manager
- Digital product management
- Categories
- Pricing
- Versions
- Media
- Status

### Module 4: Market Intelligence
- Country research
- Demand research
- Competitor monitoring
- Keyword discovery
- Market ranking
- Opportunity scoring

### Module 5: Marketplace Manager
- Marketplace integrations
- Listing management
- Product synchronization
- Listing updates
- Publication status

### Module 6: Content Engine
- Titles
- Descriptions
- SEO keywords
- Marketing copy
- Localization-ready content

### Module 7: Analytics
- Traffic
- Sales
- Revenue
- Conversion
- Top products
- Top countries
- Marketplace performance
- Trend analysis

### Module 8: Performance Reporter
- Secure connection to mahalaksmi.web.id
- Transmit node status
- Revenue, sales, system health
- AI recommendations
- Synchronization logs

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Windows 10/11 (for Windows Service)
- Or Linux/macOS (for console mode)

### Installation

1. **Clone repository:**
   ```bash
   git clone https://github.com/prahlad168/MAHA-LAKSHMI-CORP.git
   cd MAHA-LAKSHMI-CORP/maha-sales-engine
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # OR
   source venv/bin/activate  # Linux/macOS
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure engine:**
   ```bash
   cp config/engine.yaml config/engine.yaml
   # Edit with your settings
   ```

5. **Initialize database:**
   ```bash
   python main.py
   # This creates the local database
   ```

---

## 🖥️ Windows Service Installation

### Install as Windows Service
```bash
# From maha-sales-engine directory
python installer/install_service.py install
```

### Start Service
```bash
python installer/install_service.py start
```

### Stop Service
```bash
python installer/install_service.py stop
```

### Remove Service
```bash
python installer/install_service.py remove
```

### Alternative: Use Windows built-in tools
```bash
# Install
python installer/windows_service.py install

# Start
net start MahaSalesEngine

# Stop
net stop MahaSalesEngine

# Remove
python installer/windows_service.py remove
```

---

## 🐧 Linux/macOS Console Mode

### Run in console (for testing):
```bash
python main.py
```

### Run as daemon (Linux):
```bash
# Create systemd service file
sudo nano /etc/systemd/system/maha-sales-engine.service
```

```ini
[Unit]
Description=MAHA Sales Engine V1
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/maha-sales-engine
ExecStart=/path/to/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable maha-sales-engine
sudo systemctl start maha-sales-engine

# Check status
sudo systemctl status maha-sales-engine

# View logs
sudo journalctl -u maha-sales-engine -f
```

---

## ⚙️ Configuration

Edit `config/engine.yaml`:

```yaml
engine:
  node_id: "node-1"  # Unique node ID
  environment: "production"

dashboard:
  url: "https://mahalaksmi.web.id"
  heartbeat_interval: 60  # seconds

sales:
  daily_leads_target: 50
  daily_outreach_target: 100
  daily_revenue_target_usd: 100

channels:
  email:
    enabled: true
    username: "your-email@gmail.com"
    password: "your-app-password"
  whatsapp:
    enabled: true
    token: "YOUR_WHATSAPP_TOKEN"
```

---

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Dashboard
```
https://mahalaksmi.web.id/nodes/{node_id}
```

### Logs
```
logs/
├── engine.log      # Main engine log
├── scheduler.log   # Job scheduler log
├── sales.log       # Sales activities
├── errors.log      # Errors only
└── api.log         # API communications
```

---

## 🔧 Development

### Run tests
```bash
pytest tests/ -v
```

### Code formatting
```bash
black .
ruff check .
```

### Type checking
```bash
mypy .
```

---

## 📁 Project Structure

```
maha-sales-engine/
├── main.py                    # Entry point
├── core/
│   └── engine.py             # Core engine
├── scheduler/
│   └── scheduler.py          # Job scheduler
├── products/
│   └── product-manager.py    # Product management
├── market-intelligence/
│   └── analyzer.py           # Market analysis
├── marketplaces/
│   └── manager.py            # Marketplace integrations
├── content/
│   └── engine.py             # Content generation
├── analytics/
│   └── engine.py             # Analytics
├── reporter/
│   └── reporter.py           # Dashboard reporting
├── db/
│   ├── schema.sql            # Database schema
│   └── maha_sales_engine.db  # SQLite database
├── config/
│   └── engine.yaml           # Configuration
├── logs/                      # Log files
├── installer/
│   ├── windows_service.py    # Windows service
│   └── install_service.py    # Service installer
├── requirements.txt
└── README.md
```

---

## 🔒 Security

- HTTPS only
- JWT authentication
- mTLS for node-dashboard communication
- Encrypted sensitive configuration
- Structured logging
- Never expose secrets

---

## 📈 Performance Targets

- CPU: < 5%
- Memory: < 100 MB
- Disk: < 1 GB
- Uptime: 99.9%
- Response time: < 100ms

---

## 🎯 Success Criteria

Version 1 is successful when:

1. ✅ Application starts automatically after Windows boots
2. ✅ System operates continuously
3. ✅ Digital products are managed successfully
4. ✅ Market research executes automatically
5. ✅ Content generation works
6. ✅ Marketplace synchronization functions
7. ✅ Performance reports reach mahalaksmi.web.id
8. ✅ Application can be installed easily on another Windows computer

---

## 📝 Development Phases

- **Phase 1:** Foundation ✅
- **Phase 2:** Product Management ✅
- **Phase 3:** Market Intelligence ✅
- **Phase 4:** Marketplace Integration ⬜
- **Phase 5:** Content Engine ✅
- **Phase 6:** Automation Engine ⬜
- **Phase 7:** Analytics ✅
- **Phase 8:** Mission Control ⬜
- **Phase 9:** Deployment ⬜
- **Phase 10:** Production Validation ⬜

---

## 📄 License

Copyright © 2026 MAHA LAKSHMI HOLDINGS. All rights reserved.

---

**Version:** 1.0.0  
**Created:** 2026-07-27  
**Status:** 🚀 Foundation Complete
