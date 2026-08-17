# MAHA LAKSHMI CORP - Deployment Guide
## Production Deployment Instructions

---

## Prerequisites

- Server with macOS or Linux
- Python 3.8+
- Domain: `mahalaksmi.web.id` pointing to your server
- SSL certificate (Let's Encrypt recommended)

---

## Option 1: macOS Production (Launchd)

### 1.1 Install Service
```bash
cd "/Users/macpayanganhospital/MY PROJECT/MAHA-LAKSHMI-CORP/deployment"
cp com.mahalakshmi.backend.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.mahalakshmi.backend.plist
```

### 1.2 Manage Service
```bash
# Start
launchctl start com.mahalakshmi.backend

# Stop
launchctl stop com.mahalakshmi.backend

# Restart
launchctl stop com.mahalakshmi.backend && launchctl start com.mahalakshmi.backend

# View logs
tail -f logs/server.log
tail -f logs/server-error.log

# Uninstall
launchctl unload ~/Library/LaunchAgents/com.mahalakshmi.backend.plist
rm ~/Library/LaunchAgents/com.mahalakshmi.backend.plist
```

---

## Option 2: Linux Production (Systemd)

### 2.1 Install Service
```bash
sudo cp deployment/systemd/mahalakshmi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mahalakshmi
sudo systemctl start mahalakshmi
```

### 2.2 Manage Service
```bash
# Start
sudo systemctl start mahalakshmi

# Stop
sudo systemctl stop mahalakshmi

# Restart
sudo systemctl restart mahalakshmi

# Status
sudo systemctl status mahalakshmi

# Logs
sudo journalctl -u mahalakshmi -f
```

---

## Option 3: Docker Production

### 3.1 Build and Run
```bash
docker build -t mahalakshmi-backend .
docker run -d \
  --name mahalakshmi \
  -p 8000:8000 \
  --env-file deployment/.env.production \
  -v $(pwd)/data:/app/data \
  mahalakshmi-backend
```

---

## Nginx Reverse Proxy (Recommended)

### 4.1 Install Nginx
```bash
# macOS
brew install nginx

# Ubuntu/Debian
sudo apt update && sudo apt install nginx
```

### 4.2 Configure
```bash
# Copy nginx config
sudo cp deployment/nginx/mahalaksmi.conf /etc/nginx/sites-available/mahalaksmi
sudo ln -s /etc/nginx/sites-available/mahalaksmi /etc/nginx/sites-enabled/

# Test and reload
sudo nginx -t
sudo systemctl reload nginx  # Linux
sudo nginx -s reload         # macOS
```

---

## SSL Certificate (Let's Encrypt)

### 5.1 Install Certbot
```bash
# macOS
brew install certbot

# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx
```

### 5.2 Generate Certificate
```bash
# Stop nginx first
sudo systemctl stop nginx  # Linux
sudo nginx -s stop         # macOS

# Generate certificate
sudo certbot certonly --standalone -d mahalaksmi.web.id -d www.mahalaksmi.web.id

# Start nginx
sudo systemctl start nginx  # Linux
sudo nginx                  # macOS
```

### 5.3 Auto-renewal
```bash
# Test renewal
sudo certbot renew --dry-run

# Add to crontab (Linux)
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet

# Add to crontab (macOS)
crontab -e
# Add: 0 12 * * * /usr/local/bin/certbot renew --quiet
```

---

## Environment Configuration

### 6.1 Production .env
```bash
# Copy production environment
cp deployment/.env.production .env

# IMPORTANT: Change these values!
# - JWT_SECRET_KEY: Generate a strong random string
# - DATABASE_URL: Use PostgreSQL in production
# - SMTP_*: Configure your email service
```

### 6.2 Generate JWT Secret
```bash
# Generate a secure random secret
openssl rand -hex 32

# Or use Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Database Migration (Production)

### 7.1 Switch to PostgreSQL (Recommended)
```bash
# Install PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql -c "CREATE DATABASE maha_lakshmi;"
sudo -u postgres psql -c "CREATE USER maha_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE maha_lakshmi TO maha_user;"

# Update .env
DATABASE_URL=postgresql://maha_user:your_password@localhost/maha_lakshmi
```

### 7.2 Run Migrations
```bash
# Migrations run automatically on startup
# Or manually:
python3 -c "from backend.db.connection import init_db; init_db()"
```

---

## Firewall Configuration

### 8.1 macOS
```bash
# Allow port 8000
sudo pfctl -f /etc/pf.conf
sudo pfctl -e

# Or use macOS Firewall in System Preferences
```

### 8.2 Linux (UFW)
```bash
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

---

## Monitoring

### 9.1 Check Server Status
```bash
# Health check
curl https://mahalaksmi.web.id/health

# API docs
curl https://mahalaksmi.web.id/api/docs

# Server logs
tail -f logs/server.log
tail -f logs/server-error.log
```

### 9.2 Process Monitoring
```bash
# Check if server is running
ps aux | grep uvicorn

# Check port
lsof -i :8000
```

---

## Troubleshooting

### Server won't start
```bash
# Check logs
tail -f logs/server-error.log

# Check port availability
lsof -i :8000

# Check Python environment
python3 -c "import uvicorn; print('uvicorn OK')"
```

### 502 Bad Gateway
```bash
# Check if backend is running
curl http://127.0.0.1:8000/health

# Check nginx config
sudo nginx -t

# Reload nginx
sudo nginx -s reload
```

### SSL Issues
```bash
# Check certificate
sudo certbot certificates

# Renew manually
sudo certbot renew
```

---

## Production Checklist

- [ ] Server is running on port 8000
- [ ] Nginx reverse proxy configured
- [ ] SSL certificate installed and auto-renewing
- [ ] Domain `mahalaksmi.web.id` pointing to server IP
- [ ] Firewall configured (ports 22, 80, 443)
- [ ] JWT_SECRET_KEY changed to random value
- [ ] Database migrated to PostgreSQL
- [ ] SMTP configured for email notifications
- [ ] Redis configured for rate limiting
- [ ] Logs directory created and writable
- [ ] Backup strategy in place
- [ ] Monitoring set up

---

## Quick Start

```bash
# 1. Clone/update code
cd "/Users/macpayanganhospital/MY PROJECT/MAHA-LAKSHMI-CORP"
git pull origin main

# 2. Install dependencies
cd backend && pip3 install -r requirements.txt && cd ..

# 3. Configure environment
cp deployment/.env.production .env
# Edit .env with your production values

# 4. Start server
./start-server.sh

# 5. Test
curl http://localhost:8000/health
```

---

**Status: Production Ready** 🚀
