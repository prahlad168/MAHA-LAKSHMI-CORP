# 🎯 Setup Domain mahalaksmi.web.id ke GitHub Pages

## STEP 1: Set DNS di INDOWEBHOST

### Login ke Panel
1. Buka: https://panel.indowebhost.com
2. Login dengan akun [CEO]

### Tambah DNS Record
1. Cari menu **"DNS Records"** atau **"Zone Editor"**
2. Klik **"Add Record"**
3. Isi:

```
Type: CNAME
Name: mahalaksmi (atau @)
Value: prahlad168.github.io
TTL: 3600 (atau Auto)
```

4. Klik **Save**

---

## STEP 2: Set Custom Domain di GitHub

### Buka Repository Settings
1. Buka: https://github.com/prahlad168/MAHA-LAKSHMI-CORP/settings/pages
2. Login dengan akun GitHub

### Konfigurasi
1. Di bagian **Custom Domain** → ketik: `mahalaksmi.web.id`
2. Klik **Save**
3. Centang ✅ **Enforce HTTPS** (untuk SSL otomatis)
4. Tunggu 5-10 menit untuk SSL certificate

---

## STEP 3: Verifikasi

Buka browser → ketik: **https://mahalaksmi.web.id**

Seharusnya muncul website kegiatan MAHA LAKSHMI!

---

## 📋 Ringkasan

| Langkah | Lokasi | Aksi |
|---------|--------|------|
| DNS CNAME | Indowebhost Panel | Set ke prahlad168.github.io |
| Custom Domain | GitHub Settings | Ketik mahalaksmi.web.id |
| HTTPS | GitHub (auto) | Centang Enforce HTTPS |

---

## ⏱️ Estimasi Waktu

- DNS propagate: **5-30 menit**
- SSL certificate: **5-10 menit**
- Total: **~15-30 menit**

---

## 🆘 Jika Gagal

### Error "Custom domain not available"
→ Domain belum di-unlock di Indowebhost, coba unlock dulu

### Error SSL
→ Tunggu 10 menit, refresh halaman

### Website tidak muncul
→ Clear cache browser, coba incognito mode

---

**Created:** 2026-07-17
