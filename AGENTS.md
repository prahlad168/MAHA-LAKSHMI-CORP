# 🏢 GAURANGA - Digital Company Ecosystem

## 📋 Overview

Master agent system untuk mengelola 10 perusahaan digital dengan target **Rp 1.000.000.000/bulan**.

---

## 🏗️ Architecture

```
                    ╔═══════════════════════════════╗
                    ║      👑 GAURANGA CEO          ║
                    ║   Master Orchestrator         ║
                    ║   Target: Rp 1B/bulan        ║
                    ╚═══════════════════════════════╝
                                    │
           ┌──────────┬──────────┬─┴──┬──────────┬──────────┐
           │          │          │    │          │          │
           ▼          ▼          ▼    ▼          ▼          ▼
    ┌──────────┐┌──────────┐┌──────┐┌──────────┐┌──────────┐┌──────────┐
    │Company 1 ││Company 2 ││ ...  ││Company 9 ││Company 10││ HQ Ops  │
    │Payangan  ││Gianyar   ││      ││Property  ││Consulting││         │
    │Hospital  ││Tech      ││      ││Tech      ││Group     ││         │
    └──────────┘└──────────┘└──────┘└──────────┘└──────────┘└──────────┘
           │          │          │    │          │          │
           ▼          ▼          ▼    ▼          ▼          ▼
    ┌──────────────────────────────────────────────────────────────┐
    │              SUB-AGENTS (6 per company = 60 agents)         │
    │  Daily Report │ Sales │ Marketing │ SEO │ CS │ Finance       │
    └──────────────────────────────────────────────────────────────┘
```

### 📂 Detail arsitektur: `.agents/skills/agent-architecture.md`

---

## 🏥 PAYANGAN HOSPITAL DIGITAL

| Field | Value |
|-------|-------|
| **Project** | Payangan Hospital Management System |
| **Repository** | `prahlad168/Payangan-Hospital` |
| **Domain** | `https://payanganhospital.gianyarkab.go.id/` |
| **Status** | ✅ ACTIVE |
| **Agents** | 6 Active |

---

## 🏢 10 COMPANY ECOSYSTEM

| # | Company | Type | Target | Status |
|---|---------|------|--------|--------|
| 1 | Payangan Hospital Digital | Healthcare SaaS | Rp 100M/mo | ✅ ACTIVE |
| 2 | Gianyar Tech Solutions | IT Services | Rp 100M/mo | 📋 READY |
| 3 | Bali Digital Agency | Digital Marketing | Rp 100M/mo | 📋 READY |
| 4 | Gianyar E-Commerce Hub | E-Commerce | Rp 100M/mo | 📋 READY |
| 5 | Bali EdTech Center | Education | Rp 100M/mo | 📋 READY |
| 6 | Gianyar Finance Tech | Fintech | Rp 100M/mo | 📋 READY |
| 7 | Bali Logistics Network | Logistics | Rp 100M/mo | 📋 READY |
| 8 | Gianyar Food Tech | Food Tech | Rp 100M/mo | 📋 READY |
| 9 | Bali Travel Platform | Travel | Rp 100M/mo | 📋 READY |
| 10 | Gianyar Property Tech | Property | Rp 100M/mo | 📋 READY |

### 📁 All Companies Setup: `companys/` folder

---

## 📁 Project Structure

```
├── index.html              # Homepage
├── about.html              # About page
├── dokter.html             # Doctor list
├── igd.html                # IGD/Emergency
├── kontak.html             # Contact page
├── progress/
│   └── index.html         # Progress dashboard
├── img/                    # Images folder
├── webhook.php             # Auto-deploy webhook script
└── ... (other hospital pages)
```

---

## 🤖 Available Skills

### 1. Webhook Auto-Deploy
**File:** `.agents/skills/webhook-auto-deploy.md`

Setup webhook untuk auto-deploy dari GitHub ke hosting Idwebhost.

**Yang sudah configured:**
- ✅ Webhook URL: `https://payanganhospital.gianyarkab.go.id/webhook.php`
- ✅ GitHub webhook active
- ✅ Auto-deploy working

### 2. OpenHands Daily Report
**File:** `.agents/skills/openhands-daily-report.md`

Automation untuk laporan progress harian otomatis jam 6 pagi WIB.

**Yang sudah configured:**
- ✅ Automation ID: `2e4d4f38-1c7c-4437-b25b-7d52f35d0ab7`
- ✅ Schedule: `0 6 * * *` (Asia/Jakarta)
- ✅ Output: `progress/daily-report-YYYY-MM-DD.md`

---

## 🚀 Deployment Flow

```
┌─────────────────┐
│  GitHub Push    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GitHub         │
│  Webhook        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐
│  Idwebhost      │────▶│  Website Updated │
│  webhook.php    │     │  ✅ Success      │
└─────────────────┘     └──────────────────┘
```

---

## 📅 Automation Schedule

| Task | Schedule | Output |
|------|----------|--------|
| Daily Progress Report | Setiap jam 6:00 pagi WIB | `progress/daily-report-*.md` |
| Progress Dashboard | Setiap push | `progress/index.html` |

---

## 🔧 Quick Commands

### Test Webhook:
```
https://payanganhospital.gianyarkab.go.id/webhook.php
```

### Trigger Automation Manually:
```bash
curl -X POST "https://app.all-hands.dev/api/automation/v1/2e4d4f38-1c7c-4437-b25b-7d52f35d0ab7/dispatch" \
  -H "Authorization: Bearer ${OPENHANDS_API_KEY}"
```

### Check Automation Status:
```bash
curl "https://app.all-hands.dev/api/automation/v1/2e4d4f38-1c7c-4437-b25b-7d52f35d0ab7" \
  -H "Authorization: Bearer ${OPENHANDS_API_KEY}"
```

---

## 📝 For Future Development

### Adding New Pages:
1. Create HTML file di repository
2. Push ke GitHub
3. Hosting auto-update via webhook

### Modifying Automation:
1. Edit prompt di OpenHands dashboard
2. Atau update via API

### Checking Logs:
- Webhook log: `/home/payangan/public_html/webhook.log`
- OpenHands runs: Via dashboard

---

## 🔒 Security Notes

- Webhook secret: Tidak dipakai (kosong) untuk simplicity
- Untuk production: Tambahkan secret verification
- GitHub token: Gunakan read-only access jika memungkinkan

---

## 📞 Contact

- **GitHub Owner:** prahlad168
- **Domain Admin:** Team Idwebhost

---

## ✅ Status

| Component | Status |
|-----------|--------|
| GitHub Repository | ✅ Active |
| Hosting Connected | ✅ Connected |
| Webhook | ✅ Working |
| Daily Automation | ✅ Active |
| Auto-Deploy | ✅ Ready |

---

**Last Updated:** 2026-07-02
