# 🌐 Setup Subdomain - MAHA LAKSHMI HOLDINGS

## 📅 Tanggal: 18 Juli 2026
## 🎯 Tujuan: Subdomain untuk masing-masing 10 usaha

---

## 🏢 DAFTAR SUBDOMAIN

| # | Perusahaan | Subdomain | Fungsi | Status |
|---|-----------|-----------|--------|--------|
| 1 | Payangan Hospital | `payangan.mahalaksmi.web.id` | RS Management System | 🔴 |
| 2 | Gianyar Tech | `tech.mahalaksmi.web.id` | Software House | 🔴 |
| 3 | Bali Digital Agency | `digital.mahalaksmi.web.id` | Digital Marketing | 🔴 |
| 4 | Gianyar E-Commerce | `toko.mahalaksmi.web.id` | Online Store | 🔴 |
| 5 | Bali EdTech | `kursus.mahalaksmi.web.id` | Online Courses | 🔴 |
| 6 | Gianyar Finance | `uang.mahalaksmi.web.id` | Fintech | 🔴 |
| 7 | Bali Logistics | `kirim.mahalaksmi.web.id` | Delivery Platform | 🔴 |
| 8 | Bali Travel | `travel.mahalaksmi.web.id` | Tour & Travel | 🔴 |
| 9 | Gianyar Property | `rumah.mahalaksmi.web.id` | Property | 🔴 |
| 10 | Gianyar FoodTech | `makan.mahalaksmi.web.id` | Food Delivery | 🔴 |

---

## 🔧 STEP 1: Setup DNS di Indowebhost

### Login ke Panel
1. Buka: https://panel.indowebhost.com
2. Login dengan akun Pak Pur
3. Pilih domain: `mahalaksmi.web.id`

### Tambah DNS Records (CNAME untuk masing-masing subdomain)

Tambah record **UNTUK SETIAP SUBDOMAIN**:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | payangan | prahlad168.github.io | 3600 |
| CNAME | tech | prahlad168.github.io | 3600 |
| CNAME | digital | prahlad168.github.io | 3600 |
| CNAME | toko | prahlad168.github.io | 3600 |
| CNAME | kursus | prahlad168.github.io | 3600 |
| CNAME | uang | prahlad168.github.io | 3600 |
| CNAME | kirim | prahlad168.github.io | 3600 |
| CNAME | travel | prahlad168.github.io | 3600 |
| CNAME | rumah | prahlad168.github.io | 3600 |
| CNAME | makan | prahlad168.github.io | 3600 |

### Cara Tambah DNS Record:
1. Buka **DNS Records** / **Zone Editor**
2. Klik **Add Record**
3. Pilih Type: **CNAME**
4. Isi Name: (nama subdomain, contoh: `travel`)
5. Isi Value: `prahlad168.github.io`
6. TTL: **3600**
7. Klik **Save**
8. Ulangi untuk setiap subdomain

---

## 🔧 STEP 2: Setup GitHub Pages per Subdomain

### Metode A: GitHub Pages (Gratis)

#### 2a. Buat GitHub Repository untuk masing-masing usaha

**Contoh untuk Bali Travel:**

```bash
# 1. Buat repo baru di GitHub:
# Nama: Bali-Travel

# 2. Clone repo
git clone https://github.com/prahlad168/Bali-Travel.git
cd Bali-Travel

# 3. Copy landing page files
cp /path/to/bali-travel/* .

# 4. Push ke GitHub
git add -A
git commit -m "Initial commit - Bali Travel landing page"
git push origin main
```

#### 2b. Enable GitHub Pages
1. Buka: https://github.com/prahlad168/Bali-Travel/settings/pages
2. Source: **Deploy from branch** → **main**
3. Custom Domain: `travel.mahalaksmi.web.id`
4. Centang ✅ **Enforce HTTPS**
5. Klik **Save**

#### 2c. Ulangi untuk semua subdomain

| Repository | Subdomain |
|------------|-----------|
| Payangan-Hospital | payangan.mahalaksmi.web.id |
| Gianyar-Tech | tech.mahalaksmi.web.id |
| Bali-Digital | digital.mahalaksmi.web.id |
| Gianyar-Ecommerce | toko.mahalaksmi.web.id |
| Bali-EdTech | kursus.mahalaksmi.web.id |
| Gianyar-Finance | uang.mahalaksmi.web.id |
| Bali-Logistics | kirim.mahalaksmi.web.id |
| Bali-Travel | travel.mahalaksmi.web.id |
| Gianyar-Property | rumah.mahalaksmi.web.id |
| Gianyar-FoodTech | makan.mahalaksmi.web.id |

---

### Metode B: Subdirectory (Lebih Simple)

Jika ingin satu repository saja, buat subdirectory:

```
MAHA-LAKSHMI-CORP/
├── index.html          (main page)
├── payangan/           (RS Payangan)
├── tech/               (Gianyar Tech)
├── digital/            (Bali Digital)
├── toko/               (E-Commerce)
├── kursus/             (EdTech)
├── uang/               (Finance)
├── kirim/              (Logistics)
├── travel/             (Bali Travel)
├── rumah/              (Property)
└── makan/              (FoodTech)
```

#### Konfigurasi CNAME per folder:
1. Buat file `CNAME` di masing-masing folder
2. Isi dengan subdomain yang sesuai

**Contoh: travel/CNAME**
```
travel.mahalaksmi.web.id
```

3. Enable GitHub Pages dengan folder yang berbeda

---

## 📋 QUICK SETUP COMMAND (Metode A)

```bash
#!/bin/bash
# Setup semua subdomain

REPOS=(
  "Payangan-Hospital:payangan"
  "Gianyar-Tech:tech"
  "Bali-Digital:digital"
  "Gianyar-Ecommerce:toko"
  "Bali-EdTech:kursus"
  "Gianyar-Finance:uang"
  "Bali-Logistics:kirim"
  "Bali-Travel:travel"
  "Gianyar-Property:rumah"
  "Gianyar-FoodTech:makan"
)

for repo in "${REPOS[@]}"; do
  IFS=':' read -r name sub <<< "$repo"
  echo "Setting up $name -> $sub.mahalaksmi.web.id"
  
  # Clone repo
  git clone https://github.com/prahlad168/$name.git
  cd $name
  
  # Create CNAME file
  echo "$sub.mahalaksmi.web.id" > CNAME
  
  # Push
  git add CNAME
  git commit -m "Add CNAME for $sub.mahalaksmi.web.id"
  git push origin main
  
  cd ..
done
```

---

## 🌐 TARGET SUBDOMAIN URLs

Setelah setup selesai, akses akan seperti ini:

| # | Perusahaan | URL Target | Landing Page |
|---|-----------|-----------|--------------|
| 1 | Payangan Hospital | `https://payangan.mahalaksmi.web.id` | ✅ |
| 2 | Gianyar Tech | `https://tech.mahalaksmi.web.id` | 🔨 |
| 3 | Bali Digital | `https://digital.mahalaksmi.web.id` | 🔨 |
| 4 | Gianyar E-Commerce | `https://toko.mahalaksmi.web.id` | 🔨 |
| 5 | Bali EdTech | `https://kursus.mahalaksmi.web.id` | 🔨 |
| 6 | Gianyar Finance | `https://uang.mahalaksmi.web.id` | 🔨 |
| 7 | Bali Logistics | `https://kirim.mahalaksmi.web.id` | 🔨 |
| 8 | Bali Travel | `https://travel.mahalaksmi.web.id` | 🔨 |
| 9 | Gianyar Property | `https://rumah.mahalaksmi.web.id` | 🔨 |
| 10 | Gianyar FoodTech | `https://makan.mahalaksmi.web.id` | 🔨 |

---

## ⏱️ ESTIMASI WAKTU

| Task | Waktu |
|------|-------|
| Setup DNS (10 records) | 15 menit |
| Buat 10 GitHub repos | 30 menit |
| Enable GitHub Pages | 5 menit/repo |
| DNS Propagation | 5-30 menit |
| SSL Certificate | 5-10 menit |
| **Total** | **~2 jam** |

---

## ✅ CHECKLIST

### DNS Setup
- [ ] Login Indowebhost Panel
- [ ] Tambah CNAME: payangan → prahlad168.github.io
- [ ] Tambah CNAME: tech → prahlad168.github.io
- [ ] Tambah CNAME: digital → prahlad168.github.io
- [ ] Tambah CNAME: toko → prahlad168.github.io
- [ ] Tambah CNAME: kursus → prahlad168.github.io
- [ ] Tambah CNAME: uang → prahlad168.github.io
- [ ] Tambah CNAME: kirim → prahlad168.github.io
- [ ] Tambah CNAME: travel → prahlad168.github.io
- [ ] Tambah CNAME: rumah → prahlad168.github.io
- [ ] Tambah CNAME: makan → prahlad168.github.io

### GitHub Pages Setup
- [ ] Buat repo Payangan-Hospital
- [ ] Buat repo Gianyar-Tech
- [ ] Buat repo Bali-Digital
- [ ] Buat repo Gianyar-Ecommerce
- [ ] Buat repo Bali-EdTech
- [ ] Buat repo Gianyar-Finance
- [ ] Buat repo Bali-Logistics
- [ ] Buat repo Bali-Travel
- [ ] Buat repo Gianyar-Property
- [ ] Buat repo Gianyar-FoodTech
- [ ] Enable GitHub Pages masing-masing
- [ ] Set custom domain
- [ ] Enforce HTTPS

### Landing Pages
- [ ] Deploy payangan landing page
- [ ] Deploy tech landing page
- [ ] Deploy digital landing page
- [ ] Deploy toko landing page
- [ ] Deploy kursus landing page
- [ ] Deploy uang landing page
- [ ] Deploy kirim landing page
- [ ] Deploy travel landing page
- [ ] Deploy rumah landing page
- [ ] Deploy makan landing page

---

## 🆘 TROUBLESHOOTING

### Subdomain tidak resolve
```bash
# Cek DNS propagation
nslookup travel.mahalaksmi.web.id

# Atau gunakan:
# https://dnschecker.org/#CNAME/travel.mahalaksmi.web.id
```

### SSL Error
- Tunggu 5-10 menit setelah enable HTTPS
- Clear browser cache
- Force refresh: Ctrl+Shift+R

### GitHub Pages Error
- Pastikan CNAME file ada di root repo
- Pastikan custom domain sudah di-set di GitHub settings
- Pastikan enforce HTTPS dicentang

---

## 📞 KONTAK

**CEO:** i Made Purna Ananda
**WhatsApp:** 081337558787
**Domain:** mahalaksmi.web.id
**Hosting:** Indowebhost
**Code Hosting:** GitHub

---

**Created:** 2026-07-18
**Version:** 1.0.0
**Status:** 🚀 READY TO SETUP
