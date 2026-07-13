# 📊 DAILY REPORT AGENT - MAHA TUKANG

## Agent ID: `daily-report-agent-v1`

## 🎯 SCHEDULE
- **Daily:** 06:00 WIB
- **Output:** progress/daily-report-YYYY-MM-DD.md

## 📋 REPORT SECTIONS

### 1. Revenue Summary
```markdown
## 💰 Revenue
- Yesterday: Rp X
- MTD: Rp X
- vs Target: X%
- Blockers: [if any]
```

### 2. Tukang Metrics
```markdown
## 🔧 Tukang
- Registered: X
- Active today: X
- New registrations: X
- Avg rating: X
```

### 3. Pelanggan Metrics
```markdown
## 👥 Pelanggan
- New leads: X
- Conversions: X
- Repeat orders: X
- CSAT score: X%
```

### 4. Operations
```markdown
## ⚙️ Operations
- Projects completed: X
- On-time rate: X%
- Quality score: X
- Avg completion: X days
```

### 5. Marketing
```markdown
## 📢 Marketing
- TikTok views: X
- IG reach: X
- WhatsApp broadcast: X sent
- Leads generated: X
```

### 6. Tomorrow Plan
```markdown
## 📅 Tomorrow
- Priority 1: [Task]
- Priority 2: [Task]
- Priority 3: [Task]
```

### 7. Blockers & Solutions
```markdown
## 🚧 Blockers
- [Blocker] → [Solution]
```

## 📤 OUTPUT FILE
Save to: `maha-tukang/progress/daily-report-YYYY-MM-DD.md`

## 🔄 AUTOMATION
```bash
# Cron: 0 6 * * * (every day 6 AM WIB)
curl -X POST "https://app.all-hands.dev/api/automation/v1/[ID]/dispatch" \
  -H "Authorization: Bearer ${OPENHANDS_API_KEY}"
```

**Agent Version:** 1.0.0 | **Status:** 🚀 READY
**Owner:** i Made Purna Ananda (Pak Pur)
