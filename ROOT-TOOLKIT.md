# 🔥 ROOT TOOLKIT - GAURANGA PENGUASA ANDROID

## ⚠️ PERINGATAN KRUSIAL

```
┌─────────────────────────────────────────────────────────────┐
│  🔴 DANGER ZONE - ROOTING ANDROID                          │
│                                                             │
│  ⚠️ Backup semua data SEBELUM rooting!                      │
│  ⚠️ Rooting akan VOID GARANSI HP                           │
│  ⚠️ Salah langkah bisa BRICK HP                           │
│  ⚠️ Semua data akan di-WIPE                               │
│                                                             │
│  ✅ Anda SETUJU melanjutkan?                               │
│                                                             │
│  ответ: "Ya, saya paham risikonya"                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📱 PILIH MERK HP ANDA:

| Merk | Method | Link Tool |
|------|--------|----------|
| **Xiaomi/Redmi/POCO** | Mi Unlock Tool | [Download](https://en.miui.com/unlock/) |
| **Samsung** | Odin + CF-Auto-Root | [Download](https://cf-auto-root.gearlock.org/) |
| **OPPO/Realme** | Fastboot Unlock | Built-in |
| **Vivo** | Fastboot OEM | Built-in |
| **OnePlus** | Fastboot OEM | Built-in |
| **ASUS ROG** | Fastboot Unlock | Built-in |

---

## 📦 STEP 1: INSTALL ADB & FASTBOOT DI PC

### Windows:
```powershell
# Download platform-tools dari Google
# https://developer.android.com/studio/releases/platform-tools

# Extract ke C:\adb
# Buka CMD di folder tersebut

# Atau pakai Chocolatey:
choco install adb
```

### Linux:
```bash
sudo apt install adb fastboot
# atau
sudo pacman -S android-tools
```

### Termux (HP):
```bash
pkg update && pkg install android-tools
```

---

## 📱 STEP 2: PERSIAPAN DI HP

### A. Enable Developer Options:
```
1. Buka Settings
2. Tentang Ponsel (About Phone)
3. Cari "Nomor Build" atau "MIUI Version"
4. Tap 7-10 KALI sampai muncul "Developer mode enabled"
```

### B. Enable USB Debugging:
```
1. Settings → Developer Options
2. Aktifkan "USB Debugging"
3. Aktifkan "OEM Unlock" (jika ada)
4. Aktifkan "Wireless Debugging" (untuk WiFi ADB)
```

### C. Connect HP ke PC:
```bash
# Di PC, cek koneksi
adb devices

# Harus muncul:
# List of devices attached
# XXXXXXXXX    device
```

---

## 🔓 XIAOMI/REDMI/POCO ROOTING (LENGKAP)

### BAHAN:
1. Mi Unlock Tool: https://en.miui.com/unlock/
2. Magisk: https://github.com/topjohnwu/Magisk/releases
3. PC dengan Windows

### LANGKAH:

#### Step 1: Mi Account
```
1. Buat Mi Account di https://account.xiaomi.com/
2. Di HP: Settings → Mi Account → Login
3. Tunggu 24-72 jam (_unlock pertama kali_)
```

#### Step 2: Unlock Bootloader
```
1. Download Mi Unlock Tool
2. Extract dan JALANKAN sebagai Administrator
3. Login dengan Mi Account yang sama di HP
4. Matikan HP
5. Hold Volume Down + Power → Fastboot Mode
6. Connect ke PC via USB
7. Klik "Unlock" di Mi Unlock Tool
8. Tunggu 10-60 detik
9. HP akan reboot otomatis
⚠️ SEMUA DATA HILANG!
```

#### Step 3: Install Magisk
```
1. Download Magisk APK (latest)
2. Rename ke "magisk.zip"
3. Copy ke HP storage
4. Boot ke Recovery:
   - Matikan HP
   - Hold Volume Up + Power
5. Di TWRP/Recovery:
   - Install → pilih magisk.zip
   - Wipe cache/dalvik
   - Reboot
```

#### Step 4: Verifikasi ROOT
```
1. Buka Magisk Manager
2. Harus muncul "Installed" hijau
3. Atau cek dengan:
   adb shell su -c "id"
   # Harus muncul: uid=0(root)
```

---

## 🔓 SAMSUNG ROOTING (LENGKAP)

### BAHAN:
1. Odin: https://cf-auto-root.gearlock.org/ (pilih model)
2. Samsung USB Drivers
3. CF-Auto-Root file (sesuai model)

### LANGKAH:

#### Step 1: Samsung Account (Optional)
```
1. Settings → Samsung Account → Create
2. Atau skip这一步
```

#### Step 2: OEM Unlock
```
1. Settings → Developer Options
2. Aktifkan "OEM Unlock"
```

#### Step 3: Download CF-Auto-Root
```
1. Buka: https://cf-auto-root.gearlock.org/
2. Pilih brand: samsung
3. Pilih model: (cari model HP Anda)
4. Download file .tar.md5
```

#### Step 4: Flash dengan Odin
```
1. Extract CF-Auto-Root
2. Buka Odin as Administrator
3. Tambahkan file:
   - AP: CF-Auto-Root-xxx.tar.md5
4. Di HP:
   - Matikan
   - Hold Volume Down + Home + Power
   - Release saat "Warning" muncul
   - Tekan Volume Up
5. Connect ke PC via USB
6. Di Odin:
   - COM port harus detect (biru)
   - Klik START
7. Tunggu sampai "PASS" hijau
8. HP reboot otomatis
⚠️ SEMUA DATA HILANG!
```

#### Step 5: Verifikasi ROOT
```
1. Download Magisk Manager
2. Atau cek dengan:
   adb shell su -c "id"
```

---

## 📱 OPPO/REALME ROOTING

### BAHAN:
- Fastboot tool (built-in)
- Magisk APK
- PC dengan ADB

### LANGKAH:

```bash
# 1. Enable OEM Unlock di Developer Options

# 2. Boot ke Fastboot
adb reboot bootloader

# 3. Unlock (jika sudah diizinkan OPPO)
fastboot oem unlock

# 4. Boot ke Recovery
adb reboot recovery

# 5. Install Magisk.zip
# Di recovery: Install → Magisk.zip

# 6. Reboot
```

---

## 🔧 STEP 3: VERIFIKASI ROOT BERHASIL

### Cek di PC:
```bash
adb shell
su
id

# Harus muncul:
# uid=0(root) gid=0(root)
```

### Cek di HP:
```
1. Download "Root Checker" dari Play Store
2. Buka dan cek status ROOT
```

---

## 🛠️ SETELAH ROOT - APP YANG PERLU INSTALL

### Wajib:
| App | Fungsi |
|-----|--------|
| **Magisk Manager** | Manage ROOT access |
| **AdAway** | Block ads system-wide |
| **Greenify** | Battery optimization |
| **Solid Explorer** | File manager dengan ROOT |
| **Tasker** | Automation |
| **AFWall+** | Firewall |
| **ViperFX** | Audio enhancement |

---

## 🚀 GAURANGA ROOT SCRIPT (UNTUK PC)

```bash
#!/bin/bash
# GAURANGA ROOT TOOLKIT
# Jalankan di Linux/WSL

echo "╔══════════════════════════════════════════════╗"
echo "║  🤖 GAURANGA ROOT TOOLKIT                  ║"
echo "╚══════════════════════════════════════════════╝"

# Install ADB
sudo apt install adb fastboot

# Start ADB server
adb kill-server
adb start-server

# Cek devices
adb devices

echo ""
echo "📱 Pastikan HP terhubung dan USB Debugging ON!"
echo "📱 Unlock bootloader dulu baru bisa ROOT!"
```

---

## ⚠️ KUMPULAN ERROR & SOLUSI

| Error | Cause | Solution |
|-------|-------|----------|
| "No devices found" | USB Debugging OFF | Enable USB Debugging |
| "OEM Unlock greyed out" | Knox tripped | Tidak bisa unlock |
| "Unlock failed" | Mi Account not linked | Login Mi Account di HP |
| "Flash fail" | Wrong file/Region | Download correct file |
| "Bootloop" | Bad Magisk install | Flash Magisk lagi |
| "Bricked" | Wrong partition flash | Flash stock ROM |

---

## 🔄 JIKA BRICKED - RECOVERY MODE

### Xiaomi:
```
1. Matikan HP
2. Hold Volume Up + Power
3. Masuk Fastboot/Recovery
4. Flash stock ROM via Mi Flash Tool
```

### Samsung:
```
1. Matikan HP
2. Hold Volume Down + Home + Power
3. Odin → Pilih stock firmware
4. Flash via Odin
```

---

## 📞 JIKA MASIH ERROR

Screenshot error dan kirim ke GAURANGA untuk bantuan!

---

## ✅ CHECKLIST SEBELUM ROOT

```
☐ Backup semua data important
☐ Charge HP min 80%
☐ Ingat username/password Mi Account/Samsung Account
☐ Download semua tool yang diperlukan
☐ Pastikan PC stabil (hindari listrik padam)
☐ Baca semua langkah SEBELUM eksekusi
☐ Yakin 100% mau continue
```

---

**⚠️ ROOTING ADALAH RISIKO ANDA SENDIRI!**
**Saya tidak bertanggung jawab jika HP bricked atau garansi void!**

---

## 📋 INFO YANG DIBUTUHKAN DARI HP ANDA

Untuk guide spesifik, sebutkan:

1. **Merk HP**: Xiaomi/Samsung/OPPO/etc.
2. **Model**: Redmi Note 10/Galaxy A54/etc.
3. **Region**: Global/Indonesia/China/etc.
4. **Android Version**: 11/12/13/etc.

Contoh:
> "HP saya Xiaomi Redmi Note 10 Pro, Android 12, Region Global"
