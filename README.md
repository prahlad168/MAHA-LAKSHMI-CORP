# 🚀 Crypto Payment System - Deployment Guide

## Quick Deploy Options

### Option 1: Railway (Recommended)

1. **Login to Railway**
   ```
   https://railway.app
   ```

2. **Connect GitHub Repository**
   - Push this folder to GitHub
   - Connect repo to Railway
   - Railway auto-detects Python app

3. **Deploy**
   - Click "Deploy"
   - Done!

### Option 2: Vercel

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Deploy**
   ```bash
   vercel
   ```

### Option 3: Render

1. **Create Web Service**
   - Go to https://render.com
   - Connect GitHub repo
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `python app.py`

### Option 4: Docker (Own Server)

```bash
# Build
docker build -t crypto-payment .

# Run
docker run -d -p 5000:5000 crypto-payment
```

## Configuration

### Update Wallet Addresses

Edit `app.py` line ~70-75:

```python
wallets_db = {
    "TRC20": {"address": "YOUR_TRC20_ADDRESS", ...},
    "ERC20": {"address": "YOUR_ERC20_ADDRESS", ...},
    ...
}
```

### Update Products

Edit `app.py` line ~20-25:

```python
products_db = {
    "prod_1": {"id": "prod_1", "name": "Your Product", "price": 99.99},
    ...
}
```

## Environment Variables

For production, add:
- `FLASK_ENV=production`
- `DATABASE_URL` (if using PostgreSQL)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/orders` | POST | Create order |
| `/api/v1/orders/{id}` | GET | Get order |
| `/api/v1/products` | GET | List products |
| `/api/v1/currencies` | GET | Get currencies |
| `/api/v1/admin/dashboard` | GET | Dashboard |

## Supported Networks

- USDT (TRC20, ERC20, BEP20)
- BTC
- ETH

## Status

✅ API Server: Running
✅ Checkout Page: Ready
✅ Dashboard: Ready
✅ Blockchain Verification: Ready (needs real API keys for production)
