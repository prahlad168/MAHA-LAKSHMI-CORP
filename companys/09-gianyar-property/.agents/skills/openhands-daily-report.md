# OpenHands Daily Report Automation Skill

## Overview
Panduan untuk setup OpenHands automation yang menjalankan laporan harian otomatis setiap jam 6 pagi WIB.

---

## 🎯 Tujuan
Agent OpenHands secara otomatis membuat laporan progress harian dan menyimpannya ke repository GitHub setiap jam 6 pagi WIB (Asia/Jakarta).

---

## 📋 Informasi Automation

| Field | Value |
|-------|-------|
| **Automation ID** | `2e4d4f38-1c7c-4437-b25b-7d52f35d0ab7` |
| **Name** | Daily Progress Report - 6 AM WIB |
| **Schedule** | `0 6 * * *` (setiap hari jam 6:00 pagi) |
| **Timezone** | Asia/Jakarta |
| **Status** | ✅ Active/Enabled |
| **Last Run** | 2026-07-02T00:26:44Z |

---

## 🔧 Setup Details

### Prompt yang Digunakan:
```
Buat laporan progress harian untuk proyek Payangan Hospital dan simpan ke file di folder progress/. 
Laporan harus mencakup: tanggal, ringkasan progress hari ini, task yang sedang dikerjakan, dan rencana untuk besok. 
Format file dengan nama: progress/daily-report-YYYY-MM-DD.md. 
Gunakan GitHub API untuk membuat file baru di repository prahlad168/Payangan-Hospital di branch main.
```

### Repository Target:
- **Owner:** prahlad168
- **Repo:** Payangan-Hospital
- **Branch:** main
- **Output Path:** `progress/daily-report-YYYY-MM-DD.md`

---

## 📁 Output Files

### Laporan Harian:
- **Format:** `progress/daily-report-YYYY-MM-DD.md`
- **Contoh:** `progress/daily-report-2026-07-02.md`

### Halaman Progress:
- **URL:** `progress/index.html`
- **File:** `/progress/index.html` di repository

---

## 🔌 API Endpoints

### Base URL:
```
https://app.all-hands.dev/api/automation/v1
```

### List Automations:
```bash
curl "${OPENHANDS_HOST}/api/automation/v1?limit=20" \
  -H "Authorization: Bearer ${OPENHANDS_API_KEY}"
```

### Get Automation Details:
```bash
curl "${OPENHANDS_HOST}/api/automation/v1/2e4d4f38-1c7c-4437-b25b-7d52f35d0ab7" \
  -H "Authorization: Bearer ${OPENHANDS_API_KEY}"
```

### Trigger Manually:
```bash
curl -X POST "${OPENHANDS_HOST}/api/automation/v1/2e4d4f38-1c7c-4437-b25b-7d52f35d0ab7/dispatch" \
  -H "Authorization: Bearer ${OPENHANDS_API_KEY}"
```

### List Runs:
```bash
curl "${OPENHANDS_HOST}/api/automation/v1/2e4d4f38-1c7c-4437-b25b-7d52f35d0ab7/runs?limit=20" \
  -H "Authorization: Bearer ${OPENHANDS_API_KEY}"
```

### Disable/Enable:
```bash
# Disable
curl -X PATCH "${OPENHANDS_HOST}/api/automation/v1/2e4d4f38-1c7c-4437-b25b-7d52f35d0ab7" \
  -H "Authorization: Bearer ${OPENHANDS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# Enable
curl -X PATCH "${OPENHANDS_HOST}/api/automation/v1/2e4d4f38-1c7c-4437-b25b-7d52f35d0ab7" \
  -H "Authorization: Bearer ${OPENHANDS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

---

## 🔄 Cara Kerja

```
Jam 6:00 pagi WIB (setiap hari)
    ↓
OpenHands Server mendeteksi cron trigger
    ↓
Agent sandbox dijalankan di cloud
    ↓
Agent membuat laporan via GitHub API
    ↓
File tersimpan di repository GitHub
    ↓
Webhook trigger hosting Idwebhost
    ↓
Hosting ter-update otomatis
```

---

## 🕐 Schedule Format

Cron expression: `0 6 * * *`

| Field | Value | Description |
|-------|-------|-------------|
| Minute | 0 | Tepat menit ke-0 |
| Hour | 6 | Jam 6 pagi |
| Day | * | Setiap hari |
| Month | * | Setiap bulan |
| Weekday | * | Setiap hari dalam minggu |

**Timezone:** Asia/Jakarta (WIB, UTC+7)

---

## 📝 Create New Automation

### Basic Prompt Preset:
```bash
curl -X POST "${OPENHANDS_HOST}/api/automation/v1/preset/prompt" \
  -H "Authorization: Bearer ${OPENHANDS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Automation Name",
    "prompt": "Instructions for the agent",
    "trigger": {
      "type": "cron",
      "schedule": "0 6 * * *",
      "timezone": "Asia/Jakarta"
    },
    "repos": ["https://github.com/owner/repo"]
  }'
```

---

## 🐛 Troubleshooting

### Automation tidak jalan:
1. Cek status: `GET /api/automation/v1/{id}` → pastikan `enabled: true`
2. Cek last_triggered_at untuk tahu kapan terakhir running
3. Manual trigger untuk test

### Error saat run:
1. Buka OpenHands dashboard
2. Cek conversation history
3. Lihat error details di `/runs` endpoint

### Laporan tidak muncul:
1. Cek apakah automation sudah running
2. Cek GitHub API rate limit
3. Manual trigger dan lihat logs

---

## 🔒 Notes

### Keamanan:
- Automation API key harus di-set sebagai environment variable
- Jangan expose API key di public
- Repository harus accessible oleh automation service

### Rate Limits:
- GitHub API: 5000 requests/hour
- OpenHands automation: tergantung plan

---

## ✅ Checklist

- [x] Automation created
- [x] Schedule configured (6 AM WIB)
- [x] Repository configured
- [x] Tested manually
- [x] Auto-deploy webhook configured
- [x] Hosting connected

---

## 📚 Referensi

### OpenHands Skills:
- `/openhands-automation` - Skill untuk create/manage automations

### External Resources:
- Cron expression: https://crontab.guru/
- GitHub API: https://docs.github.com/rest

---

**Created:** 2026-07-02
**Last Updated:** 2026-07-02
