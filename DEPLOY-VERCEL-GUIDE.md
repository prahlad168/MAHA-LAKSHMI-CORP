# 🚀 Deploy ke Vercel - Panduan Lengkap

## Apa yang Sudah Dibuat

Saya sudah membuat:
1. ✅ `vercel.json` - Konfigurasi Vercel untuk static files
2. ✅ `.github/workflows/deploy-vercel.yml` - GitHub Actions untuk auto-deploy

---

## 📋 Langkah-Langkah Deploy

### Step 1: Buat Account Vercel

1. Buka [vercel.com](https://vercel.com)
2. Klik **Sign Up**
3. Pilih **Continue with GitHub**
4. Authorize Vercel untuk akses GitHub

### Step 2: Import Repository

1. Di Vercel Dashboard, klik **Add New...** → **Project**
2. Pilih repository **prahlad168/MAHA-LAKSHMI-CORP**
3. Klik **Import**

### Step 3: Configure Project

1. **Framework Preset:** Pilih **Other**
2. **Root Directory:** Biarkan default ( `./` )
3. **Build Command:** Kosongkan
4. **Output Directory:** Biarkan default
5. Klik **Deploy**

### Step 4: Tunggu Deploy Selesai

1. Vercel akan build dan deploy otomatis
2. Tunggu 1-2 menit
3. Dapat URL seperti: `maha-lakshmi-corp.vercel.app`

---

## 🔄 Auto-Deploy Setup

Setelah deploy pertama, setiap push ke GitHub akan auto-deploy!

### Untuk Production Deploy (Pakai secrets):

1. Buka **Project Settings** → **Environment Variables**
2. Add:
   - `VERCEL_TOKEN` → dari vercel.com/account/tokens
   - `VERCEL_ORG_ID` → dari Settings → General
   - `VERCEL_PROJECT_ID` → dari Settings → General

3. GitHub Actions akan auto-trigger setiap push ke main

---

## 🌐 URL Aplikasi Setelah Deploy

| App | URL Pattern |
|-----|-------------|
| Main Dashboard | `https://maha-lakshmi-corp.vercel.app/maha-lakshmi/` |
| MAHA Command Center | `https://maha-lakshmi-corp.vercel.app/maha-command-center/` |
| Progress | `https://maha-lakshmi-corp.vercel.app/progress/` |
| DigiMart | `https://maha-lakshmi-corp.vercel.app/digimart/` |
| Airdrop | `https://maha-lakshmi-corp.vercel.app/airdrop/` |
| MicroTask | `https://maha-lakshmi-corp.vercel.app/microtask/` |
| Survey | `https://maha-lakshmi-corp.vercel.app/survey/` |

---

## 🔧 Custom Domain (Optional)

### Untuk Domain: maha-lakshmi.com

1. Buka **Project Settings** → **Domains**
2. Add: `maha-lakshmi.com`
3. Vercel akan kasih DNS records
4. Tambahkan ke domain registrar:
   ```
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   
   Type: A
   Name: @
   Value: 76.76.21.21
   ```

---

## 📱 Landing Pages per Province

Semua landing pages sudah siap di-deploy:

| Product | Provinces |
|---------|-----------|
| DigiMart | 38 provinces |
| AirdropHunter | 38 provinces |
| MicroTask Pro | 38 provinces |
| SurveyPro | 38 provinces |

---

## ✅ Checklist

- [ ] Buat Vercel account
- [ ] Import repo dari GitHub
- [ ] Deploy pertama selesai
- [ ] Dapat URL production
- [ ] Test semua pages
- [ ] (Optional) Setup custom domain

---

## 🆘 Troubleshooting

### Build Failed?
```
Pastikan vercel.json sudah benar dan root directory sesuai
```

### 404 Error?
```
Cek vercel.json routes configuration
Pastikan file paths benar
```

### Timeout?
```
Vercel free tier: 10s build, 100MB output
Upgrade ke Pro jika perlu
```

---

## 💰 Estimasi Biaya

| Plan | Price | Limit |
|------|-------|-------|
| **Hobby (Free)** | $0 | 100GB bandwidth, 100 deployments |
| Pro | $20/mo | Unlimited |

Untuk awal, **Hobby plan** sudah cukup!

---

**Waktu estimasi deploy:** 5-10 menit
