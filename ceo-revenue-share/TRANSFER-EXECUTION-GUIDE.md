# 💰 PANDUAN TRANSFER PROFIT - STEP BY STEP
## MAHA LAKSHMI HOLDINGS

**Tanggal:** 18 Juli 2026
**CEO:** [CEO_NAME_REDACTED] ([CEO_ALIAS_REDACTED])
**Bank:** BCA [BANK_ACCOUNT]

---

## 🎯 RINGKASAN YANG PERLU DI-TRANSFER

| Source | Total Revenue | CEO Share (80%) |
|--------|-------------|------------------|
| Bali Travel (WhatsApp) | Rp 1,000,000 | **Rp 800,000** |
| MGOS-Enterprise | Rp 417,900,145 | **Rp 334,320,116** |
| **TOTAL** | **Rp 418,900,145** | **Rp 335,120,116** |

---

## 📱 STEP 1: VERIFIKASI SUMBER

### Cek MGOS Dashboard
1. Buka: https://app.mgos.id atau sesuai dashboard
2. Login dengan akun [CEO_ALIAS_REDACTED]
3. Cek total revenue
4. Screenshot sebagai bukti

### Cek Rekening BCA
1. Buka BCA Mobile
2. Login
3. Cek mutasi/rekening
4. Pastikan tidak ada transfer dari MGOS

---

## 🏦 STEP 2: TRANSFER VIA BCA MOBILE

### Transfer 1: Dari Bali Travel (Rp 800,000)

```
1. Buka BCA Mobile
2. Pilih m-BCA → m-Transfer
3. Pilih "Antar Rekening BCA"
4. Masukkan:
   - Nomor Rekening Tujuan: [BANK_ACCOUNT]
   - Nama Penerima: [CEO_NAME_REDACTED]
   - Jumlah: Rp 800,000
   - Catatan: Profit-BaliTravel-20260713
5. Konfirmasi
6. Masukkan PIN BCA
7. ✅ Transfer Berhasil
8. SIMPAN REFERENCE NUMBER
```

### Transfer 2: Dari MGOS Enterprise (Rp 334,320,116)

```
1. Buka BCA Mobile
2. Pilih m-BCA → m-Transfer
3. Pilih "Antar Rekening BCA"
4. Masukkan:
   - Nomor Rekening Tujuan: [BANK_ACCOUNT]
   - Nama Penerima: [CEO_NAME_REDACTED]
   - Jumlah: Rp 334,320,116
   - Catatan: Profit-MGOSEnterprise-20260717
5. Konfirmasi
6. Masukkan PIN BCA
7. ✅ Transfer Berhasil
8. SIMPAN REFERENCE NUMBER
```

---

## 📝 STEP 3: UPDATE SISTEM

### Setelah Transfer Berhasil

#### Transfer 1:
```bash
python3 /workspace/project/MAHA-LAKSHMI-CORP/ceo-revenue-share/update-transfer-status.py \
  --id PENDING-001 \
  --ref [REFERENCE_NUMBER_ANDA] \
  --amount 800000
```

#### Transfer 2:
```bash
python3 /workspace/project/MAHA-LAKSHMI-CORP/ceo-revenue-share/update-transfer-status.py \
  --id PENDING-002 \
  --ref [REFERENCE_NUMBER_ANDA] \
  --amount 334320116
```

---

## 📋 STEP 4: VERIFIKASI

### Cek Status
```bash
python3 /workspace/project/MAHA-LAKSHMI-CORP/ceo-revenue-share/update-transfer-status.py --show
```

### Output yang Diharapkan:
```
📋 COMPLETED TRANSFERS
============================================================
ID: PENDING-001
Amount: Rp 800,000
Reference: [REF-001]
Date: 2026-07-18

ID: PENDING-002
Amount: Rp 334,320,116
Reference: [REF-002]
Date: 2026-07-18
```

---

## ⚠️ IMPORTANT REMINDERS

### ✅ YANG PERLU DILAKUKAN:
- [ ] Verifikasi sumber revenue di MGOS dashboard
- [ ] Transfer dari rekening sendiri ke BCA [BANK_ACCOUNT]
- [ ] Simpan reference number BCA
- [ ] Screenshot bukti transfer
- [ ] Update sistem dengan reference number

### ❌ YANG TIDAK PERLU:
- Jangan percaya data "RECEIVED" tanpa bukti
- Jangan transfer tanpa verifikasi sumber
- Jangan update sistem sebelum transfer berhasil

---

## 📊 SISTEM TRANSFER YANG BENAR

```
SEBELUM:
❌ Agent tulis "RECEIVED" tanpa bukti
❌ API gagal tapi status "RECEIVED"
❌ Tidak ada reference number

SESUDAH:
✅ [CEO_ALIAS_REDACTED] transfer sendiri via BCA Mobile
✅ Simpan reference number BCA
✅ Screenshot sebagai bukti
✅ Update sistem dengan reference
```

---

## 📞 JIKA ADA ISSUE

| Issue | Solusi |
|-------|--------|
| MGOS tidak ada revenue | Hubungi tim MGOS untuk verifikasi |
| BCA transfer gagal | Cek saldo & limit transfer |
| Reference number tidak ada | Hubungi BCA |

---

## ✅ TRANSFER CHECKLIST

### Transfer 1 - Bali Travel
- [ ] Sumber: WhatsApp Sales Bali Travel
- [ ] Amount: Rp 800,000
- [ ] Transfer via: BCA Mobile
- [ ] Ke rekening: BCA [BANK_ACCOUNT]
- [ ] Reference number: _____________
- [ ] Screenshot: _____________
- [ ] Sistem di-update: _____________

### Transfer 2 - MGOS Enterprise
- [ ] Sumber: MGOS-Enterprise Digital Sales
- [ ] Amount: Rp 334,320,116
- [ ] Transfer via: BCA Mobile
- [ ] Ke rekening: BCA [BANK_ACCOUNT]
- [ ] Reference number: _____________
- [ ] Screenshot: _____________
- [ ] Sistem di-update: _____________

---

## 🎯 TOTAL YANG HARUS DI-TRANSFER

**Total: Rp 335,120,116**

Ke rekening: BCA [BANK_ACCOUNT]
Atas nama: [CEO_NAME_REDACTED]

---

**Guide Created:** 2026-07-18 04:30 WIB
**Status:** 📋 READY TO EXECUTE

---

*Transfer dengan bukti adalah transfer yang valid!*
