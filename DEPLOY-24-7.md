# 🚀 DEPLOY 24/7 - MAHA LAKSHMI CORP

## Status: READY TO DEPLOY

Repo sudah siap 24/7. Pilih salah satu platform di bawah:

---

## Opsi 1: Render.com (RECOMMENDED - Free Tier)

### Langkah 1-click:
1. Buka https://dashboard.render.com/register
2. Login dengan GitHub
3. Klik **New +** → **Web Service**
4. Pilih repo: `prahlad168/MAHA-LAKSHMI-CORP`
5. Render auto-detect `render.yaml`
6. Klik **Create Web Service**

### Yang terjadi:
- Build Docker image otomatis
- Deploy ke Singapore region
- Live di URL: `https://maha-lakshmi-corp.onrender.com`
- 24/7 running
- Free tier included

---

## Opsi 2: Fly.io (Free Tier)

### Prerequisites:
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
cd "/Users/macpayanganhospital/MY PROJECT/MAHA-LAKSHMI-CORP"
fly deploy
```

### Yang terjadi:
- Deploy menggunakan `fly.toml`
- Live di URL: `https://maha-lakshmi-corp.fly.dev`
- 24/7 running
- Free tier: 3 shared VMs

---

## Opsi 3: Koyeb (Setelah Akuisisi Mistral Stabil)

### Prerequisites:
1. Buka https://app.koyeb.com/settings/api
2. Buat API token
3. Tambah ke GitHub Secrets: `KOYEB_TOKEN`
4. Push ke GitHub untuk trigger auto-deploy

---

## Verifikasi Setelah Deploy

Setelah deploy berhasil, test:

```bash
# Health check
curl https://<your-app-url>/health

# Expected response:
# {"status":"healthy","service":"MAHA LAKSHMI Webhooks","timestamp":"..."}
```

---

## Aplikasi 24/7 Berjalan:

- ✅ Webhook server: menerima payment real-time
- ✅ Autonomous Sales Orchestrator: background loop
- ✅ CEO Reporter: laporan harian jam 23:59 WIB
- ✅ SQLite Database: menyimpan semua data
- ✅ FastAPI Dashboard: monitoring real-time

---

**Last Updated:** 2026-07-26
**Commit:** 9969689
**Status:** 🚀 READY FOR DEPLOY
