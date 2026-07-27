# WINDOWS DEPLOYMENT GUIDE - MAHA SALES ENGINE V1

**Version:** 1.0.0  
**Status:** Approved  
**Parent Document:** MASTER_BLUEPRINT.md, SYSTEM_ARCHITECTURE.md  
**Created:** 2026-07-27

---

## 1. Prerequisites

### System Requirements
- **OS:** Windows 10 (1809+) or Windows Server 2016+
- **RAM:** 2 GB minimum, 4 GB recommended
- **Disk:** 1 GB free space
- **Network:** Internet connection for dashboard sync
- **Python:** Python 3.11 or higher

### Required Software
- Python 3.11+ (with pip)
- Visual C++ Redistributable (for pywin32)
- Windows Service permissions

---

## 2. Installation Steps

### Step 1: Install Python

1. Download Python 3.11 from https://www.python.org/downloads/windows/
2. Run installer
3. **Check "Add Python to PATH"**
4. Select "Customize installation"
5. Ensure pip is installed
6. Click "Install"

Verify installation:
```cmd
python --version
pip --version
```

---

### Step 2: Copy Application Files

1. Copy entire `maha-sales-engine` folder to target machine
2. Recommended path: `C:\Program Files\MahaSalesEngine\`
3. Ensure folder structure is preserved:

```
C:\Program Files\MahaSalesEngine\
├── main.py
├── requirements.txt
├── core\
├── scheduler\
├── products\
├── market-intelligence\
├── marketplaces\
├── content\
├── analytics\
├── reporter\
├── db\
├── config\
├── logs\
└── installer\
```

---

### Step 3: Install Dependencies

Open Command Prompt as Administrator:
```cmd
cd "C:\Program Files\MahaSalesEngine"
pip install -r requirements.txt
```

Expected output:
```
Successfully installed pywin32-305 ...
```

---

### Step 4: Configure Engine

Edit `config\engine.yaml`:

```yaml
engine:
  node_id: "node-1"  # Unique ID for this node
  environment: "production"

dashboard:
  url: "https://mahalaksmi.web.id"
  heartbeat_interval: 60
  report_interval: 86400

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
  linkedin:
    enabled: false
    token: "YOUR_LINKEDIN_TOKEN"

security:
  api_key: ""
  encryption_key: ""
  cert_path: ""
  key_path: ""
  ca_path: ""
```

**Important:** Set unique `node_id` for each installation.

---

### Step 5: Initialize Database

```cmd
cd "C:\Program Files\MahaSalesEngine"
python main.py
```

This creates `db\maha_sales_engine.db` with all tables.

Press Ctrl+C to stop after initialization.

---

### Step 6: Install Windows Service

```cmd
cd "C:\Program Files\MahaSalesEngine\installer"
python install_service.py install
```

Expected output:
```
✅ Service installed: MahaSalesEngine
   Display Name: MAHA Sales Engine V1
   Description: Autonomous Digital Sales Engine for MAHA LAKSHMI HOLDINGS

To start the service:
   python install_service.py start
```

---

### Step 7: Start Service

```cmd
python install_service.py start
```

Or via Windows Services:
1. Press `Win + R`
2. Type `services.msc`
3. Find "MAHA Sales Engine V1"
4. Right-click → Start

---

## 3. Verification

### Check Service Status
```cmd
python install_service.py status
```

Or via PowerShell:
```powershell
Get-Service MahaSalesEngine
```

### Check Logs
```
C:\Program Files\MahaSalesEngine\logs\
├── engine.log
├── scheduler.log
├── sales.log
├── errors.log
└── api.log
```

### Check Health Endpoint
```cmd
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "MAHA Sales Engine V1",
  "node_id": "node-1",
  "timestamp": "2026-07-27T09:00:00Z"
}
```

---

## 4. Uninstallation

### Stop Service
```cmd
python install_service.py stop
python install_service.py remove
```

Or via PowerShell:
```powershell
Stop-Service MahaSalesEngine
sc.exe delete MahaSalesEngine
```

### Remove Files
Delete `C:\Program Files\MahaSalesEngine\` folder.

---

## 5. Troubleshooting

### Service Won't Start

1. Check Python installation:
   ```cmd
   python --version
   ```

2. Check dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

3. Check logs:
   ```
   logs\errors.log
   ```

4. Run in console mode for debugging:
   ```cmd
   python main.py
   ```

### Permission Errors

1. Run Command Prompt as Administrator
2. Check folder permissions:
   ```
   icacls "C:\Program Files\MahaSalesEngine" /grant Users:(F)
   ```

### Port Already in Use

Change port in `config\engine.yaml`:
```yaml
server:
  port: 8001
```

### Database Locked

Ensure only one instance is running:
```cmd
tasklist | findstr python
```

Kill duplicate processes:
```cmd
taskkill /F /IM python.exe
```

---

## 6. Updates

### Update Application Files

1. Stop service:
   ```cmd
   python install_service.py stop
   ```

2. Replace files with new version
3. Install new dependencies:
   ```cmd
   pip install -r requirements.txt --upgrade
   ```

4. Start service:
   ```cmd
   python install_service.py start
   ```

### Database Migrations

Migrations run automatically on startup. No manual steps required.

---

## 7. Security Checklist

- [ ] Service runs under dedicated user account (not Administrator)
- [ ] Folder permissions restricted to service account
- [ ] `config\engine.yaml` contains no plaintext secrets
- [ ] Database file is backed up regularly
- [ ] Windows Firewall allows only required ports
- [ ] Service is set to "Automatic" startup
- [ ] Recovery actions configured in Services.msc

---

## 8. Monitoring

### Windows Event Viewer
```
Windows Logs → Application
Source: MahaSalesEngine
```

### Performance Monitor
Counters to monitor:
- Process\% Processor Time (python.exe)
- Process\Working Set (python.exe)
- Process\Thread Count (python.exe)

### Disk Space
Ensure adequate space for:
- Database growth
- Log rotation
- Backups

---

## 9. Backup Strategy

### Automatic Backups
- Daily at 02:00 AM
- Stored in `db\backups\`
- Retention: 90 days

### Manual Backup
```cmd
copy db\maha_sales_engine.db db\backups\maha_sales_engine_%date%.db
```

### Restore
```cmd
copy db\backups\maha_sales_engine_2026-07-27.db db\maha_sales_engine.db
```

---

## 10. Support

### Logs Location
```
C:\Program Files\MahaSalesEngine\logs\
```

### Configuration
```
C:\Program Files\MahaSalesEngine\config\engine.yaml
```

### Database
```
C:\Program Files\MahaSalesEngine\db\maha_sales_engine.db
```

---

**Approved By:** CEO / Lead Architect  
**Date:** 2026-07-27  
**Next Review:** 2026-08-27
