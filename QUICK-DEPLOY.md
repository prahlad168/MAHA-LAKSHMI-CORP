# 🚀 Quick Deploy Guide

## Option 1: Railway (Recommended - 2 menit)

### Steps:
1. **Push ke GitHub**
```bash
cd /workspace/project/MAHA-LAKSHMI-CORP/crypto-payment-deploy
git init
git add .
git commit -m "Crypto Payment System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/crypto-payment-deploy.git
git push -u origin main
```

2. **Deploy ke Railway**
- Buka https://railway.app
- Login dengan GitHub
- Click **"New Project"** → **"Deploy from GitHub repo"**
- Pilih repository `crypto-payment-deploy`
- Railway auto-detects Python
- Klik **"Deploy"**

3. **Done!** Dapat URL seperti: `https://crypto-payment-deploy.railway.app`

---

## Option 2: Vercel (1 menit)

1. **Push ke GitHub** (same as above)

2. **Install Vercel CLI**
```bash
npm i -g vercel
```

3. **Deploy**
```bash
vercel --prod
```

---

## Option 3: Render (1 menit)

1. Buka https://render.com
2. Login → **"New"** → **"Web Service"**
3. Connect GitHub repo
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
5. **Create Web Service**

---

## Option 4: Manual Server

```bash
# SSH ke server
ssh user@your-server

# Clone repo
git clone https://github.com/YOUR_USERNAME/crypto-payment-deploy.git
cd crypto-payment-deploy

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

---

## 📋 Yang Perlu Diubah

### 1. Update Wallet Addresses
Edit `app.py` line 70-75:

```python
wallets_db = {
    "TRC20": {"address": "YOUR_TRC20_WALLET", ...},
    "ERC20": {"address": "YOUR_ERC20_WALLET", ...},
    # etc...
}
```

### 2. Update Products
Edit `app.py` line 20-30:

```python
products_db = {
    "prod_1": {"name": "AI Agent Pro", "price": 99.99},
    # etc...
}
```

---

## 🌐 Setelah Deploy

Dapat URL seperti:
- https://crypto-payment-deploy.railway.app/
- https://crypto-payment-deploy.vercel.app/
- https://your-domain.com/

### Test API:
```bash
curl https://YOUR_URL/api/v1/products
curl https://YOUR_URL/health
```

---

## ❓ Butuh Help?

```
📱 WhatsApp: [PHONE_REDACTED]
📧 Email: [EMAIL_REDACTED]
```

---

**Status:** ✅ Ready to Deploy
