# 🚀 AUTO-DEPLOY SKILL

## "Deploy Automatically with Single Command"

**Version:** 1.0.0
**Created:** 2026-07-06
**Trigger:** User says "deploy"

---

## 🎯 PURPOSE

When user says "deploy", this agent will:
1. Analyze target repository and platform
2. Clone/push to GitHub
3. Trigger deployment
4. Return deployment URL

---

## ⚡ DEPLOY PAYANGAN HOSPITAL

```bash
# One-liner to deploy Payangan Hospital to Vercel
curl -X POST "https://api.vercel.com/v13/deployments" \
  -H "Authorization: Bearer $VERCEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "payangan-hospital",
    "gitSource": {
      "type": "github",
      "repo": "prahlad168/Payangan-Hospital",
      "ref": "main"
    },
    "target": "production"
  }'
```

---

## 🔄 FULL DEPLOY FLOW

### Step 1: Clone Repository
```bash
git clone https://github.com/prahlad168/Payangan-Hospital.git /tmp/deploy-temp
```

### Step 2: Modify Files (if needed)
```bash
cd /tmp/deploy-temp
# Add/edit files
git add -A && git commit -m "update"
```

### Step 3: Push to GitHub
```bash
git remote set-url origin "https://$GITHUB_TOKEN@github.com/owner/repo.git"
git push origin main
```

### Step 4: Trigger Vercel Deploy
```bash
curl -X POST "https://api.vercel.com/v13/deployments" \
  -H "Authorization: Bearer $VERCEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "PROJECT-NAME",
    "gitSource": {"type": "github", "repo": "OWNER/REPO", "ref": "main"},
    "target": "production"
  }'
```

### Step 5: Get URL
```bash
# Response contains: {"url": "project-xxx.vercel.app", ...}
```

---

## 🌐 PLATFORMS

### Vercel (Active ✅)
- API Key: `$VERCEL_API_KEY` (auto-injected)
- Deploy via: GitHub integration or API

### Cloudflare Pages (Needs Setup)
1. Create API token at dash.cloudflare.com
2. Save as `CLOUDFLARE_API_TOKEN` secret
3. Run: `wrangler pages deploy ./dist --project-name=NAME`

### Netlify (Needs Setup)
1. Create auth token at app.netlify.com
2. Save as `NETLIFY_AUTH_TOKEN` secret
3. Run: `netlify deploy --prod --dir=./dist`

---

## 📋 COMMON COMMANDS

| Task | Command |
|------|---------|
| Deploy Payangan | `curl POST to Vercel API` |
| Clone repo | `git clone https://github.com/...` |
| Push changes | `git push origin main` |
| Check deploy | `curl GET deployment status` |

---

## 🔐 SECURITY

Credentials are injected via environment variables:
- `$VERCEL_API_KEY` - Vercel token
- `$GITHUB_TOKEN` - GitHub token

Never hardcode secrets in files!

---

## 📊 ACTIVE DEPLOYMENTS

| Project | Platform | URL | Status |
|---------|----------|-----|--------|
| payangan-hospital | Vercel | payangan-hospital-*.vercel.app | ✅ |

---

## 🎯 USAGE

```
User: "deploy payangan hospital"
Agent: Deploys to Vercel, returns URL

User: "deploy to cloudflare"
Agent: Checks credentials, deploys if available

User: "update website"
Agent: Clones, modifies, pushes, deploys
```

---

**Last Updated:** 2026-07-06
