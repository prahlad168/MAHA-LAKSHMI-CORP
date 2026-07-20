# 📱 WhatsApp Business API Setup Guide

## 🎯 Tujuan
Setup WhatsApp Business API agar AI agents bisa auto-send messages ke leads.

---

## 📋 Prerequisites

1. **Meta Business Account** (free)
2. **Facebook Business Account** verified
3. **Phone Number** (dedicated untuk WhatsApp Business)
4. **Hosting** (untuk webhook)

---

## 🔧 Step 1: Create Meta Business Account

1. Buka https://business.facebook.com
2. Klik "Create Account"
3. Isi business name: "MAHA LAKSHMI Digital"
4. Isi details (address, etc)
5. Verify email

---

## 🔧 Step 2: Register WhatsApp Business API

1. Buka https://business.facebook.com
2. Navigate to WhatsApp > Getting Started
3. Klik "Register a phone number"
4. Pilih Meta Business Account
5. Masukkan phone number (dedicated, bukan yang sudah dipake)
6. Verify via SMS/Call
7. Set business profile

---

## 🔧 Step 3: Get API Credentials

1. Buka https://developers.facebook.com
2. Create new app > Business
3. Add WhatsApp product
4. Get temporary access token
5. Save credentials:
   - Phone Number ID
   - WhatsApp Business Account ID
   - Access Token

---

## 🔧 Step 4: Setup Webhook (Optional for auto-reply)

Webhook URL: `https://your-domain.com/webhook-whatsapp.php`

---

## 📝 Configuration untuk AI Agent

Create file `config/whatsapp-config.json`:

```json
{
    "phone_number_id": "YOUR_PHONE_NUMBER_ID",
    "access_token": "YOUR_ACCESS_TOKEN",
    "business_account_id": "YOUR_WA_BUSINESS_ACCOUNT_ID",
    "webhook_verify_token": "YOUR_VERIFY_TOKEN",
    "recipient_phone": "6281337558787"
}
```

---

## 🚀 Quick Test - Send Message

```bash
curl -X POST "https://graph.facebook.com/v18.0/YOUR_PHONE_NUMBER_ID/messages" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "messaging_product": "whatsapp",
    "to": "6281337558787",
    "type": "text",
    "text": {
        "body": "Halo dari MAHA LAKSHMI! 🤖"
    }
}'
```

---

## 💡 Alternative: Fonnte API (Simpler)

Jika Meta API terlalu complex, gunakan Fonnte:

1. Daftar di https://fonnte.com
2. Get API token
3. Send via simple curl:

```bash
curl -X POST "https://api.fonnte.com/send" \
-H "Authorization: YOUR_FONNTE_TOKEN" \
-d "target=6281337558787" \
-d "message=Test dari AI Agent" \
-d "countryCode=62"
```

---

## 📞 Contact Setup

| Field | Value |
|-------|-------|
| Phone | +62 813 3755 8787 |
| Business Name | MAHA LAKSHMI Digital |
| Category | Business |
| Description | Digital Solutions Company |

---

## ✅ Checklist

- [ ] Meta Business Account created
- [ ] WhatsApp Business registered
- [ ] Phone number verified
- [ ] API credentials obtained
- [ ] Test message sent successfully
- [ ] Webhook configured (optional)

---

## 🔐 Security Notes

**JANGAN commit config dengan credentials ke GitHub!**

Tambahkan ke `.gitignore`:
```
config/whatsapp*.json
*.env
```

---

## 📞 Help Resources

- Meta Dev: https://developers.facebook.com/docs/whatsapp
- WhatsApp Business: https://business.whatsapp.com
- Fonnte: https://fonnte.com

---

**Last Updated:** 2026-07-20
**Status:** 🔧 Setup Required
