# 🏠 MAHA LAKSHMI AIOS - Hosting Setup Guide

## 📋 Overview

Setup guide untuk deploy MAHA AIOS ke hosting Anda (Idwebhost/cPanel).

---

## 🚀 Quick Setup (3 Steps)

### Step 1: SSH ke Server

```bash
ssh payangan@payanganhospital.gianyarkab.go.id
# atau
ssh payangan@YOUR_HOSTING_IP
```

### Step 2: Download & Run Setup Script

```bash
cd /home/payangan/public_html

# Download setup script (atau copy manual)
# Upload setup-hosting.sh ke server

# Run setup
chmod +x setup-hosting.sh
./setup-hosting.sh
```

### Step 3: Setup GitHub Webhook

1. Buka GitHub: `https://github.com/prahlad168/Bot_Molty5`
2. Settings → Webhooks → Add webhook
3. Payload URL: `https://payanganhospital.gianyarkab.go.id/webhook.php?secret=gauranga-deploy-2026`
4. Content type: `application/json`
5. Events: ✅ Just the push event
6. Active: ✅

---

## 📁 Manual Setup (Alternative)

### Step 1: Clone Repository

```bash
cd /home/payangan/public_html
git clone https://github.com/prahlad168/Bot_Molty5.git .
```

### Step 2: Create Webhook

```bash
cat > webhook.php << 'EOF'
<?php
$secret = 'gauranga-deploy-2026';
if (isset($_GET['secret']) && $_GET['secret'] === $secret) {
    $output = shell_exec('cd ' . __DIR__ . ' && git pull origin main 2>&1');
    echo "OK: $output";
}
EOF
```

### Step 3: Setup Cron

```bash
crontab -e
# Tambahkan baris ini:
0 6 * * * /usr/bin/php /home/payangan/public_html/MAHA-OS/notifications/api/send-report.php >> /home/payangan/public_html/cron.log 2>&1
```

---

## 🔗 URLs After Setup

| Page | URL |
|------|-----|
| Login | `https://payanganhospital.gianyarkab.go.id/MAHA-OS/auth/login.php` |
| Dashboard | `https://payanganhospital.gianyarkab.go.id/MAHA-OS/dashboard/` |
| Daily Report API | `https://payanganhospital.gianyarkab.go.id/MAHA-OS/notifications/api/send-report.php` |
| Webhook | `https://payanganhospital.gianyarkab.go.id/webhook.php` |

---

## 📧 Email & WhatsApp Configuration

| Channel | Target |
|---------|--------|
| Email | `ceo@mahalakshmi.id` |
| WhatsApp | `081337558787` |

### Test Email & WhatsApp

```bash
# Via browser
curl "https://payanganhospital.gianyarkab.go.id/MAHA-OS/notifications/api/send-report.php"
```

### WhatsApp Link Format
```
https://wa.me/6281337558787?text=[formatted message]
```

---

## ⏰ Cron Job Schedule

| Time | Task |
|------|------|
| 06:00 WIB | Daily Report to Email & WhatsApp |

---

## 🔐 Security

### Webhook Secret
```
gauranga-deploy-2026
```

### File Permissions
```bash
chmod 644 *.php
chmod 755 logs temp
```

---

## 📊 Test Deployment

### Manual Git Pull
```bash
cd /home/payangan/public_html
git pull origin main
```

### Manual Cron Run
```bash
/usr/bin/php /home/payangan/public_html/MAHA-OS/notifications/api/send-report.php
```

### Check Logs
```bash
tail -f /home/payangan/public_html/cron.log
tail -f /home/payangan/public_html/deploy.log
```

---

## 🐛 Troubleshooting

### Git Pull Fails
```bash
cd /home/payangan/public_html
git status
git reset --hard origin/main
git pull origin main
```

### Cron Not Working
```bash
# Check crontab
crontab -l

# Check PHP path
which php

# Manual test
/usr/bin/php -f /home/payangan/public_html/MAHA-OS/notifications/api/send-report.php
```

### Email Not Sending
```bash
# Check PHP mail logs
tail -f /var/log/php-mail.log

# Or use SMTP directly
```

---

## 📁 File Structure After Setup

```
/home/payangan/public_html/
├── MAHA-OS/
│   ├── auth/
│   │   ├── Auth.php
│   │   └── login.php
│   ├── database/
│   │   └── 002-auth.sql
│   ├── notifications/
│   │   ├── DailyReportSender.php
│   │   └── api/
│   │       └── send-report.php
│   └── dashboard/
│       └── index.html
├── webhook.php
├── cron.log
└── deploy.log
```

---

## ✅ Checklist

- [ ] SSH access verified
- [ ] Repository cloned
- [ ] webhook.php created
- [ ] Cron job added
- [ ] GitHub webhook configured
- [ ] Test manual report sent
- [ ] Email received
- [ ] WhatsApp link works

---

## 📞 Contact

- **CEO:** Prahlad
- **Email:** ceo@mahalakshmi.id
- **WhatsApp:** 081337558787
- **Bank:** BCA 6485086645

---

**Version:** 1.0.0
**Updated:** 2026-07-03
