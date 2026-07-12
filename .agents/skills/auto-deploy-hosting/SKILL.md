# 🚀 AUTO-DEPLOY HOSTING SKILL

## "Deploy to Any Hosting with One Command"

**Version:** 1.0.0
**Created:** 2026-07-06
**Trigger:** User says "deploy hosting" or "auto deploy"

---

## 🎯 PURPOSE

Deploy websites to multiple hosting platforms automatically.

**When user says "deploy hosting" or "auto deploy":**
1. Analyze target project
2. Choose best hosting platform
3. Deploy automatically
4. Return live URL

---

## 📋 REPOSITORIES

| Repo | Path | Purpose |
|------|------|---------|
| Payangan-Hospital | `/workspace/project/payangan-hospital-live` | Hospital website |
| MAHA-LAKSHMI-CORP | `/workspace/project/MAHA-LAKSHMI-CORP` | Enterprise management |

---

## 🌐 HOSTING PLATFORMS

### Platform Comparison:

| Platform | Bandwidth | Price | Auto-Deploy | Setup |
|----------|-----------|-------|-------------|-------|
| **Vercel** | 100GB/mo | FREE | ✅ GitHub | 1 min |
| **Cloudflare Pages** | Unlimited | FREE | ✅ GitHub | 2 min |
| **Netlify** | 100GB/mo | FREE | ✅ GitHub | 1 min |
| **GitHub Pages** | 100GB/mo | FREE | ✅ Built-in | 1 min |

---

## ⚡ QUICK DEPLOY COMMANDS

### Deploy Payangan Hospital to Vercel:

```bash
# 1. Push to GitHub (auto-deploys)
cd /workspace/project/payangan-hospital-live
git add -A
git commit -m "Deploy update"
git push origin main

# 2. Or trigger via API
curl -X POST "https://api.vercel.com/v2/deployments" \
  -H "Authorization: Bearer $VERCEL_API_KEY" \
  -d '{"projectId": "PROJECT_ID", "gitSource": {"ref": "main", "repo": "prahlad168/Payangan-Hospital"}}'
```

### Deploy to Cloudflare Pages:

```bash
# 1. Using wrangler
wrangler pages deploy ./dist --project-name=payangan-hospital

# 2. Or via GitHub Actions (already configured)
# Push to main → auto-deploy
```

---

## 🔄 AUTO-DEPLOY WORKFLOW

### When "deploy hosting" command is given:

```
USER: "deploy hosting"
    │
    ▼
STEP 1: Identify Project
├── Check git remote
├── Determine repo name
└── Identify main files
    │
    ▼
STEP 2: Push to GitHub
├── git add -A
├── git commit -m "Deploy update"
└── git push origin main
    │
    ▼
STEP 3: Trigger Platform Deploy
├── Vercel: Auto-deploys from GitHub
├── Cloudflare: Check workflow
└── Netlify: Auto-deploys from GitHub
    │
    ▼
STEP 4: Verify & Return URL
├── Check HTTP status
├── Verify files present
└── Return live URL
```

---

## 📁 DEPLOYMENT STEPS BY PLATFORM

### VERCEL (Active ✅)

```bash
# Method 1: GitHub Push (Recommended)
cd /workspace/project/REPO_NAME
git push origin main
# Vercel auto-deploys in ~1 min

# Method 2: CLI
npx vercel --prod

# Method 3: API
curl -X POST "https://api.vercel.com/v2/deployments" \
  -H "Authorization: Bearer $VERCEL_TOKEN"
```

**Vercel Project:** `payangan-hospital`
**Live URL:** `https://payangan-hospital-*.vercel.app`

---

### CLOUDFLARE PAGES

```bash
# Install wrangler
npm install -g wrangler

# Login
wrangler login

# Deploy
wrangler pages deploy ./dist --project-name=PROJECT_NAME

# Or use GitHub Actions (already in .github/workflows/)
```

**GitHub Workflow:** `.github/workflows/cloudflare-deploy.yml`

---

### NETLIFY

```bash
# Install CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=./dist

# Or GitHub integration
# Connect repo in Netlify dashboard
```

---

### GITHUB PAGES

```bash
# Enable in repo settings
# Settings → Pages → Source: main branch

# Or via API
curl -X PUT "https://api.github.com/repos/OWNER/REPO/pages" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -d '{"source": {"branch": "main"}}'
```

---

## 🎯 USAGE EXAMPLES

### Example 1: Deploy Hospital Website
```
User: "deploy hosting payangan hospital"
Agent:
1. cd /workspace/project/payangan-hospital-live
2. git add -A && git commit -m "Deploy"
3. git push origin main
4. Wait for Vercel deploy
5. Return URL
```

### Example 2: Deploy Any Project
```
User: "auto deploy"
Agent:
1. Detect current directory/project
2. Push to GitHub
3. Trigger deploy
4. Return live URL
```

### Example 3: Deploy to Specific Platform
```
User: "deploy to cloudflare"
Agent:
1. Check Cloudflare credentials
2. Run wrangler deploy
3. Return URL
```

---

## 📊 ACTIVE DEPLOYMENTS

| Project | Platform | URL | Status |
|---------|----------|-----|--------|
| Payangan Hospital | Vercel | payangan-hospital-*.vercel.app | ✅ Live |

---

## 🔐 CREDENTIALS NEEDED

| Platform | Credential | Status |
|----------|-----------|--------|
| Vercel | `$VERCEL_API_KEY` | 🔄 Check |
| GitHub | `$GITHUB_TOKEN` | ✅ Available |
| Cloudflare | `$CLOUDFLARE_API_TOKEN` | ⏳ Setup |

---

## 🚀 SKILL COMMANDS

| Command | Action |
|---------|--------|
| "deploy hosting" | Deploy current project |
| "deploy [name]" | Deploy specific project |
| "deploy to vercel" | Deploy to Vercel |
| "deploy to cloudflare" | Deploy to Cloudflare |
| "auto deploy" | Deploy + auto-detect platform |
| "check deploy status" | Check deployment status |

---

## 📝 IMPLEMENTATION

### To deploy, run:

```bash
#!/bin/bash
# Auto-deploy script

PROJECT_DIR="/workspace/project/payangan-hospital-live"
GIT_REMOTE="https://github.com/prahlad168/Payangan-Hospital.git"

cd $PROJECT_DIR
git remote set-url origin "https://$GITHUB_TOKEN@github.com/prahlad168/Payangan-Hospital.git"
git add -A
git commit -m "Auto-deploy: $(date)"
git push origin main

echo "✅ Deploy triggered! Check Vercel dashboard."
```

---

## ✅ VERIFICATION

After deploy:
```bash
# Check if live
curl -sI "https://payangan-hospital-live.vercel.app/index.html" | head -1
# Should return: HTTP/2 200
```

---

## 📋 DEPLOYMENT CHECKLIST

- [ ] Project files exist
- [ ] Git remote configured
- [ ] GitHub token available
- [ ] Platform credentials set
- [ ] Push to main branch
- [ ] Verify deployment

---

**Last Updated:** 2026-07-06
**Version:** 1.0.0
**Author:** GAURANGA AI Agent

---

*"Deploy Anywhere with One Command"* 🚀
