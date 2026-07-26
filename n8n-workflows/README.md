# 🤖 n8n AUTOMATION SETUP GUIDE
## MAHA LAKSHMI - mahalaksmi.web.id

**Version:** 1.0  
**Date:** 2026-07-26  
**Status:** READY TO DEPLOY

---

## 📋 WORKFLOWS INCLUDED

| # | Workflow | Purpose | Trigger |
|---|----------|---------|---------|
| 1 | Lead Follow-Up | Auto follow-up leads | Webhook |
| 2 | Daily Revenue Report | Send daily report to CEO | Daily 23:59 |
| 3 | Customer Onboarding | Welcome new customers | Payment webhook |
| 4 | Abandoned Cart Recovery | Recover lost sales | Every 9am/3pm/8pm |

---

## 🚀 INSTALLATION STEPS

### Step 1: Install n8n
```bash
npm install -g n8n
```

### Step 2: Start n8n
```bash
n8n start
```

Access at: http://localhost:5678

### Step 3: Import Workflows
```
1. Open http://localhost:5678
2. Click "Workflows" → "Import from File"
3. Select each JSON file from n8n-workflows/
4. Activate each workflow
```

---

## ⚙️ CREDENTIALS NEEDED

### Twilio (WhatsApp)
```
Account SID: [TWILIO_ACCOUNT_SID]
Auth Token: [TWILIO_AUTH_TOKEN]
WhatsApp Number: [TWILIO_WHATSAPP_NUMBER]
```

### Gmail/Email
```
Email: info@mahalaksmi.web.id
Password: [APP_PASSWORD]
```

### Google Sheets
```
Sheet ID: [GOOGLE_SHEET_ID]
Service Account: [GOOGLE_SERVICE_ACCOUNT]
```

### Telegram (Optional)
```
Bot Token: [TELEGRAM_BOT_TOKEN]
Chat ID: [CEO_CHAT_ID]
```

---

## 🔗 WEBHOOK ENDPOINTS

### Lead Webhook
```
POST https://mahalaksmi.web.id/api/webhooks/lead
Body:
{
  "name": "Customer Name",
  "phone": "628123456789",
  "email": "customer@example.com",
  "interest": "Website Development",
  "source": "whatsapp"
}
```

### Payment Webhook
```
POST https://mahalaksmi.web.id/api/webhooks/payment
Body:
{
  "order_id": "ORD-001",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "628123456789",
  "amount": 2500000,
  "status": "paid",
  "product": "Website Company Profile",
  "delivery_time": "3 days"
}
```

### Cart Webhook
```
POST https://mahalaksmi.web.id/api/webhooks/cart
Body:
{
  "cart_id": "CART-001",
  "customer_name": "Jane Doe",
  "customer_phone": "628123456789",
  "total": 1500000,
  "items": "Website Template + Hosting",
  "abandoned_at": "2026-07-26T10:00:00Z"
}
```

---

## 📱 WHATSAPP AUTOMATION

### Templates to Create in Twilio:
1. **Follow-up 1:** "Halo {name}, terima kasih menghubungi..."
2. **Follow-up 2:** "Follow-up: proposal untuk {interest}..."
3. **Welcome:** "Selamat datang! Pembayaran confirmed..."
4. **Cart Reminder:** "Keranjang Anda masih menunggu..."
5. **Final Offer:** "Penawaran terakhir + diskon 10%..."

---

## 📧 EMAIL TEMPLATES

### Welcome Email
```
Subject: Payment Confirmed - Welcome to MAHA LAKSHMI!

Halo {name},

Pembayaran Anda sebesar Rp {amount} telah dikonfirmasi!

Tim kami akan segera memproses pesanan Anda.
Estimasi penyelesaian: {delivery_time}

Hubungi kami:
WhatsApp: wa.me/6281337558787

Terima kasih!
MAHA LAKSHMI
```

### Daily Report Email
```
Subject: Daily Revenue Report - {date}

DAILY REVENUE REPORT
====================
Date: {date}
Total Revenue: Rp {total_revenue}
CEO Share (80%): Rp {ceo_share}
Ops Share (20%): Rp {ops_share}

Please transfer 80% to BCA: 6485086645

MAHA LAKSHMI AIOS
```

---

## 🎯 SUCCESS METRICS

| Metric | Target |
|--------|--------|
| Lead Response Rate | 20% |
| Email Open Rate | 30% |
| Cart Recovery Rate | 15% |
| Daily Reports Sent | 100% |
| Automation Uptime | 99% |

---

## 🔧 TROUBLESHOOTING

### n8n won't start
```bash
# Check Node.js version
node --version  # Should be 18+

# Reinstall n8n
npm uninstall -g n8n
npm install -g n8n
```

### Workflow not triggering
```bash
# Check webhook URL
# Verify credentials
# Check execution logs in n8n UI
```

### WhatsApp not sending
```bash
# Verify Twilio credentials
# Check WhatsApp sandbox setup
# Verify phone number format
```

---

## 📞 SUPPORT

- **n8n Docs:** https://docs.n8n.io
- **Twilio Docs:** https://www.twilio.io
- **MAHA LAKSHMI:** info@mahalaksmi.web.id

---

**DEPLOY TODAY - AUTOMATE TOMORROW!**
