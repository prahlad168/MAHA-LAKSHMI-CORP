# 🚀 CRYPTO PAYMENT SYSTEM - LIVE!

## 🌐 LIVE URL
```
https://defeat-evening-individual-alike.trycloudflare.com
```

---

## 📦 PRODUCTS (4 Digital Products)

| ID | Product | Price | Type |
|----|---------|-------|------|
| prod_1 | AI Agent Pro - Monthly | $99.99 | Subscription |
| prod_2 | AI Agent Enterprise - Yearly | $999.99 | Subscription |
| prod_3 | Custom AI Solution | $499.99 | Service |
| prod_4 | AI Training Course | $149.99 | Course |

---

## 💰 SUPPORTED CRYPTOCURRENCIES

| Currency | Networks | Status |
|----------|----------|--------|
| USDT | TRC20, ERC20, BEP20 | ✅ Ready |
| BTC | Bitcoin | ✅ Ready |
| ETH | Ethereum | ✅ Ready |

---

## 🔧 SETUP WALLETS (MUST DO!)

**Edit `app.py` line 25-30:**

```python
wallets_db = {
    "TRC20": {"address": "YOUR_TRX_WALLET", "currency": "USDT", "network": "TRC20"},
    "ERC20": {"address": "YOUR_ETH_WALLET", "currency": "USDT", "network": "ERC20"},
    "BEP20": {"address": "YOUR_BSC_WALLET", "currency": "USDT", "network": "BEP20"},
    "BTC": {"address": "YOUR_BTC_WALLET", "currency": "BTC", "network": "BTC"},
    "ETH": {"address": "YOUR_ETH_WALLET", "currency": "ETH", "network": "ERC20"},
}
```

---

## 📡 API ENDPOINTS

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products` | List products |
| POST | `/api/v1/orders` | Create order |
| GET | `/api/v1/orders/{id}` | Get order |
| POST | `/api/v1/orders/{id}/verify` | Verify payment |
| GET | `/api/v1/admin/dashboard` | Dashboard |
| GET | `/api/v1/health` | Health check |

---

## 🚀 START SYSTEM

```bash
# Quick start
./setup.sh

# Or Docker
docker build -t crypto-payment . && docker run -d -p 5000:5000 --name crypto-payment crypto-payment
```

---

## 📁 FILES

```
├── app.py           # Flask API (EDIT WALLETS HERE!)
├── index.html       # Checkout page
├── setup.sh        # Quick start script
├── Dockerfile       # Docker container
└── docker-compose.yml
```

---

## 🎯 QUICK TEST

```bash
# Test API
curl https://defeat-evening-individual-alike.trycloudflare.com/api/v1/products

# Create order
curl -X POST https://defeat-evening-individual-alike.trycloudflare.com/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "prod_1", "name": "Test", "email": "test@test.com", "country": "ID", "crypto_currency": "USDT", "network": "TRC20"}'
```

---

## ✅ CHECKLIST

- [x] Docker container running
- [x] Cloudflare tunnel active  
- [x] API working
- [x] Products configured
- [ ] Wallet addresses (UPDATE app.py!)
- [ ] Blockchain verification setup
- [ ] Email receipts
- [ ] Permanent hosting (Railway)

---

**Status: 🚀 LIVE** | **Updated: 2026-07-19**
