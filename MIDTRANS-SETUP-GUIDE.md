# 💳 MIDTRANS PAYMENT GATEWAY SETUP
## MAHA LAKSHMI HOLDINGS

**Tanggal:** 2026-07-18
**CEO:** [CEO_NAME_REDACTED] ([CEO_ALIAS_REDACTED])
**Bank:** BCA [BANK_ACCOUNT]

---

## 🎯 TUJUAN

Setup Midtrans agar MAHA LAKSHMI bisa menerima pembayaran dari customer secara real-time.

---

## 📋 PILIHAN PAYMENT GATEWAY

| Provider | Biaya | Ease | Recommended |
|----------|-------|------|-------------|
| **Midtrans** | 2.9% + free | Mudah | ✅ BEST |
| **Flip** | Rp 0/kecil | Mudah | ✅ Good |
| **Xendit** | 2.5% | Mudah | Good |
| **DOKU** | 2.5% | Medium | Good |

**Rekomendasi:** Midtrans - Paling populer di Indonesia

---

## 📝 MIDTRANS SETUP STEPS

### STEP 1: DAFTAR MIDTRANS

1. Buka: https://dashboard.midtrans.com
2. Klik **"Daftar Sekarang"**
3. Pilih **"Mitra"** (untuk bisnis)
4. Isi data:
   - Email: [email bisnis]
   - No HP: [PHONE_REDACTED]
   - Nama Toko: MAHA LAKSHMI HOLDINGS
   - Kategori: Digital Products / Services

### STEP 2: VERIFIKASI AKUN

Midtrans akan minta:
- [ ] KTP (foto)
- [ ] Foto selfie dengan KTP
- [ ] NPWP (jika ada)
- [ ] Rekening Bank untuk pencairan

### STEP 3: DAPATKAN CREDENTIALS

Setelah verifikasi, dapat:
```
Client Key: SB-Mid-client-xxxx
Server Key: SB-Mid-server-xxxx
```

### STEP 4: SETUP NOTIFICATION URL

Di dashboard Midtrans:
1. Settings → Configuration
2. Notification URL:
   ```
   https://mahalaksmi.web.id/midtrans/notification.php
   ```

### STEP 5: SETUP VA (Virtual Account)

Pilih bank untuk menerima transfer:
- [ ] BCA
- [ ] Mandiri
- [ ] BNI
- [ ] BRI
- [ ] Permata

---

## 💻 INTEGRASI CODE

### PHP Integration (untuk server)

```php
<?php
// midtrans-config.php

define('MIDTRANS_SERVER_KEY', 'SB-Mid-server-xxxx');
define('MIDTRANS_CLIENT_KEY', 'SB-Mid-client-xxxx');
define('IS_PRODUCTION', false); // true untuk production

require_once 'midtrans/Midtrans.php';

\Midtrans\Config::$serverKey = MIDTRANS_SERVER_KEY;
\Midtrans\Config::$isProduction = IS_PRODUCTION;
\Midtrans\Config::$isSanitized = true;
\Midtrans\Config::$is3ds = true;
?>
```

### Snap Checkout (Simple Integration)

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://app.midtrans.com/snap/snap.js" 
        data-client-key="SB-Mid-client-xxxx"></script>
</head>
<body>
    <button id="pay-button">Bayar Sekarang</button>

    <script>
        document.getElementById('pay-button').addEventListener('click', function() {
            // Get snap token from server
            fetch('get-snap-token.php', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    order_id: 'ORDER-001',
                    amount: 100000,
                    customer_name: 'John Doe'
                })
            })
            .then(res => res.json())
            .then(data => {
                snap.pay(data.snap_token, {
                    onSuccess: function(result) {
                        alert('Payment success!');
                        console.log(result);
                    },
                    onPending: function(result) {
                        alert('Waiting for payment');
                        console.log(result);
                    },
                    onError: function(result) {
                        alert('Payment failed!');
                        console.log(result);
                    }
                });
            });
        });
    </script>
</body>
</html>
```

### Server-side (get-snap-token.php)

```php
<?php
require_once 'midtrans-config.php';

$order_id = $_POST['order_id'];
$gross_amount = $_POST['amount'];
$customer_name = $_POST['customer_name'];

$transaction_details = [
    'order_id' => $order_id,
    'gross_amount' => (int)$gross_amount
];

$customer_details = [
    'first_name' => $customer_name,
    'phone' => '[PHONE_REDACTED]'
];

$credit_card['secure'] = true;

$params = [
    'transaction_details' => $transaction_details,
    'customer_details' => $customer_details,
    'credit_card' => $credit_card
];

$snap_token = \Midtrans\Snap::getSnapToken($params);

echo json_encode(['snap_token' => $snap_token]);
?>
```

---

## 📱 PAYMENT METHODS YANG AKAN TERSEDIA

Setelah Midtrans aktif:

| Metode | Icon | Processing Time |
|-------|------|----------------|
| BCA Virtual Account | 🏦 | 1-2 detik |
| Mandiri Virtual Account | 🏦 | 1-2 detik |
| BNI Virtual Account | 🏦 | 1-2 detik |
| BRI Virtual Account | 🏦 | 1-2 detik |
| Permata Virtual Account | 🏦 | 1-2 detik |
| Credit Card | 💳 | Instant |
| GoPay | 📱 | Instant |
| OVO | 📱 | Instant |
| DANA | 📱 | Instant |
| ShopeePay | 📱 | Instant |
| QRIS | 📱 | Instant |

---

## 💰 BIAYA & PENCAIRAN

### Biaya Transaksi:
| Volume Bulanan | Biaya |
|----------------|------|
| 0-100 transaksi | 2.9% per transaksi |
| 100+ transaksi | Negosiasi |

### Pencairan:
- **Minimum pencairan:** Rp 10,000
- **Waktu pencairan:** D+1 (next business day)
- **Biaya pencairan:** Gratis
- **Target pencairan:** BCA [BANK_ACCOUNT]

---

## 🔧 NEXT STEPS

### Immediately (Hari Ini):
1. [ ] Daftar di https://dashboard.midtrans.com
2. [ ] Upload dokumen verifikasi
3. [ ] Tunggu verifikasi (1-3 hari)

### After Verification:
4. [ ] Dapat Client Key & Server Key
5. [ ] Setup di website
6. [ ] Test transaksi
7. [ ] Activate production mode

### After First Payment:
8. [ ] Setup auto-transfer ke BCA [BANK_ACCOUNT]
9. [ ] Setup profit distribution system
10. [ ] Connect ke GAURANGA AI

---

## 📞 CONTACT MIDTRANS

| Channel | Contact |
|---------|---------|
| Website | https://midtrans.com |
| Dashboard | https://dashboard.midtrans.com |
| Email | support@midtrans.com |
| Phone | 021-567-8123 |
| WhatsApp | https://wa.me/62215778123 |

---

## ✅ CHECKLIST

- [ ] Daftar Midtrans
- [ ] Upload dokumen verifikasi
- [ ] Tunggu approval
- [ ] Dapat credentials
- [ ] Setup di website
- [ ] Test payment
- [ ] Setup pencairan ke BCA

---

**Setup Guide Created:** 2026-07-18
**Status:** 📋 READY TO START

---

*Setiap masalah pasti ada solusinya!*
