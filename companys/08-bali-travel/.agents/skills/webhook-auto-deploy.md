# Webhook Auto-Deploy Skill

## Overview
Panduan lengkap untuk setup webhook auto-deploy dari GitHub ke hosting (Idwebhost/cPanel).

---

## 🎯 Tujuan
Ketika ada push/commit di GitHub, hosting otomatis ter-update tanpa perlu manual upload.

---

## 📋 Prerequisites

### Yang Sudah Dibuat:
- ✅ Repository GitHub: `prahlad168/Payangan-Hospital`
- ✅ Hosting: Idwebhost (cPanel)
- ✅ Domain: `payanganhospital.gianyarkab.go.id`
- ✅ Username cPanel: `payangan`
- ✅ Repository sudah di-clone di hosting: `/home/payangan/public_html`

---

## 🔧 Setup Steps

### Step 1: Buat File webhook.php di Hosting

1. Buka **cPanel** → **File Manager** → `public_html`
2. Buat file baru: **webhook.php**
3. Isi dengan script berikut:

```php
<?php
// Webhook untuk auto-pull dari GitHub

// Git pull
$output = shell_exec('cd /home/payangan/public_html && git pull 2>&1');

// Log hasil
file_put_contents('/home/payangan/public_html/webhook.log', date('Y-m-d H:i:s') . " - Pull result: $output\n", FILE_APPEND);

echo "OK: $output";
```

4. **Save**

### Step 2: Setup GitHub Webhook

1. Buka repository GitHub: `https://github.com/prahlad168/Payangan-Hospital`
2. Klik **Settings** → **Webhooks** → **Add webhook**

3. Isi form:

| Field | Value |
|-------|-------|
| **Payload URL** | `https://payanganhospital.gianyarkab.go.id/webhook.php` |
| **Content type** | `application/json` |
| **Secret** | *(kosongkan)* |
| **SSL verification** | ✅ Enable SSL verification |
| **Events** | ✅ Just the push event |
| **Active** | ✅ Centang |

4. Klik **Add webhook**

### Step 3: Test Webhook

1. Di GitHub → **Settings** → **Webhooks**
2. Klik webhook → **Test** → **Test delivery**
3. Harus muncul: `OK: Already up to date.`

### Step 4: Verify Auto-Deploy

1. Edit file di GitHub
2. Commit & Push
3. Buka hosting: `https://payanganhospital.gianyarkab.go.id/`
4. File harus sudah ter-update otomatis

---

## 📁 File Locations

| Komponen | Lokasi |
|----------|--------|
| Repository | GitHub: `prahlad168/Payangan-Hospital` |
| Hosting | `/home/payangan/public_html/` |
| Webhook script | `/home/payangan/public_html/webhook.php` |
| Webhook log | `/home/payangan/public_html/webhook.log` |

---

## 🔒 Security Notes

### Untuk Production (Optional):
Tambahkan secret verification jika perlu:

```php
<?php
$secret = 'your_secret_here';
$payload = file_get_contents('php://input');
$signature = $_SERVER['HTTP_X_HUB_SIGNATURE_256'] ?? '';

if (!empty($secret)) {
    $hash = 'sha256=' . hash_hmac('sha256', $payload, $secret);
    if (!hash_equals($hash, $signature)) {
        http_response_code(403);
        die('Invalid signature');
    }
}

// Git pull
$output = shell_exec('cd /home/payangan/public_html && git pull 2>&1');

// Log hasil
file_put_contents('/home/payangan/public_html/webhook.log', date('Y-m-d H:i:s') . " - Pull result: $output\n", FILE_APPEND);

echo "OK: $output";
```

---

## 🐛 Troubleshooting

### Error: "Invalid signature"
**Solusi:** Kosongkan field Secret di GitHub webhook, atau samakan dengan script PHP.

### Error: "git not found"
**Solusi:** Pastikan git terinstall di server. Hubungi hosting provider.

### Error: "Permission denied"
**Solusi:** Pastikan path `/home/payangan/public_html` benar dan owned oleh user yang benar.

### Webhook tidak ter-trigger
**Solusi:** 
1. Cek webhook sudah Active ✅
2. Cek SSL certificate valid
3. Test dengan "Test delivery" button

---

## 📝 Maintenance

### Cek Log:
```bash
cat /home/payangan/public_html/webhook.log
```

### Manual Pull (Jika perlu):
```bash
cd /home/payangan/public_html
git pull origin main
```

---

## 📚 Referensi Tambahan

### Hosting Idwebhost Info:
- Login cPanel: `https://payanganhospital.gianyarkab.go.id:2083`
- File Manager: cPanel → File Manager → public_html
- Terminal: cPanel → Terminal

### GitHub Webhook Events:
- `push` - Setiap push ke repository
- `create` - Branch/tag baru dibuat
- `delete` - Branch/tag dihapus

---

## ✅ Checklist

- [x] File webhook.php dibuat di hosting
- [x] GitHub webhook configured
- [x] SSL verification enabled
- [x] Test delivery successful
- [x] Auto-deploy working

---

**Created:** 2026-07-02
**Last Updated:** 2026-07-02
