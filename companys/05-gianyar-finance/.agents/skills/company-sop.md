# SOP Perusahaan - Payangan Hospital Digital

## 🏢 Informasi Perusahaan

| Field | Value |
|-------|-------|
| **Nama Perusahaan** | Payangan Hospital |
| **Tipe** | Rumah Sakit Pemerintah Daerah |
| **Lokasi** | Gianyar, Bali, Indonesia |
| **Website** | https://payanganhospital.gianyarkab.go.id |
| **Sistem** | Sistem Informasi Manajemen Rumah Sakit (SIMRS) |

---

## 📋 SOP Utama

### 1. SOP Development

#### 1.1 Workflow Pengembangan
```
1. Planning → Analysis → Design → Development → Testing → Deployment → Maintenance
```

#### 1.2 Commit Message Convention
```
<type>(<scope>): <description>

Types:
- feat:     New feature
- fix:      Bug fix
- docs:     Documentation
- style:    Formatting
- refactor: Refactoring
- test:     Testing
- chore:    Maintenance

Examples:
- feat(dashboard): add patient statistics chart
- fix(registration): resolve validation error
- docs(api): update endpoint documentation
```

#### 1.3 Code Review Process
```
1. Developer creates branch from main
2. Make changes and commit
3. Push to remote
4. Create Pull Request
5. Code review by team
6. Address feedback
7. Approve and merge
8. Delete branch
```

---

### 2. SOP Deployment

#### 2.1 Deployment Pipeline
```
GitHub Push
    │
    ▼
GitHub Webhook Trigger
    │
    ▼
Hosting Server (Idwebhost)
    │
    ▼
Git Pull to Live
    │
    ▼
Website Updated ✅
```

#### 2.2 Deployment Checklist
- [ ] Code sudah di-test locally
- [ ] Commit message sesuai convention
- [ ] Branch sudah di-merge ke main
- [ ] Webhook test successful
- [ ] Live site verified

#### 2.3 Rollback Procedure
```bash
# If deployment fails:
1. Check git log for last good commit
2. Run: git revert <commit_hash>
3. Push reverted commit
4. Verify rollback successful
```

---

### 3. SOP Reporting

#### 3.1 Laporan Harian Otomatis

**Jadwal:** Setiap hari jam 6:00 pagi WIB

**Format:**
```markdown
# Laporan Progress Harian
## Tanggal: YYYY-MM-DD

## Progress Hari Ini
- [Task yang dikerjakan]
- [Hasil yang dicapai]

## Task Sedang Dikerjakan
- [Task in progress]
- [Percentage completion]

## Rencana Besok
- [Plan for next day]

## Blocker/Issues
- [Any blockers]

## Catatan Tambahan
- [Additional notes]
```

#### 3.2 Laporan Mingguan

**Jadwal:** Setiap hari Senin jam 9:00 pagi WIB

**Format:**
```markdown
# Laporan Mingguan
## Minggu ke-X, Bulan YYYY

## Ringkasan Minggu Ini
- Total task selesai: X
- Total task baru: Y
- Overall progress: Z%

## Highlight
- Achievement minggu ini

## Challenge
- Kendala yang dihadapi

##下周 (Minggu Depan) Plan
- Plan untuk minggu depan
```

---

### 4. SOP Komunikasi

#### 4.1 Escalation Process
```
Level 1: Self-troubleshoot (15 menit)
    │
    ▼ (if unresolved)
Level 2: Team discussion (30 menit)
    │
    ▼ (if unresolved)
Level 3: Lead escalation
    │
    ▼ (if unresolved)
Level 4: Management escalation
```

#### 4.2 Response Time SLA
| Priority | Response Time | Resolution Time |
|----------|---------------|------------------|
| Critical | 15 menit | 1 jam |
| High | 1 jam | 4 jam |
| Medium | 4 jam | 24 jam |
| Low | 24 jam | 72 jam |

---

### 5. SOP Keamanan

#### 5.1 Credential Management
- ❌ Jangan pernah hardcode credentials
- ❌ Jangan commit .env files
- ✅ Gunakan environment variables
- ✅ Gunakan GitHub Secrets untuk CI/CD
- ✅ Rotate credentials setiap 90 hari

#### 5.2 Access Control
```
Production Access
    │
    ├── Read-only untuk developer
    ├── Write-access untuk lead
    └── Admin access untuk admin

Staging Access
    ├── Full access untuk developer
    └── Limited access untuk stakeholder
```

#### 5.3 Security Checklist
- [ ] No secrets in code
- [ ] SSL/TLS enabled
- [ ] Webhook secret configured
- [ ] API keys secured
- [ ] Database credentials rotated
- [ ] Backup verified

---

### 6. SOP Quality Assurance

#### 6.1 Testing Requirements
```markdown
Before any deployment:
1. Unit Test - all functions
2. Integration Test - API endpoints
3. UI/UX Test - user flows
4. Performance Test - load testing
5. Security Scan - vulnerability check
```

#### 6.2 Code Quality Standards
```
✅ Use meaningful variable names
✅ Add comments for complex logic
✅ Follow language style guide
✅ Keep functions small (< 50 lines)
✅ No code duplication
✅ Proper error handling
```

#### 6.3 Documentation Requirements
- [ ] README.md untuk project baru
- [ ] API documentation untuk endpoints
- [ ] Inline comments untuk complex code
- [ ] Update CHANGELOG.md

---

### 7. SOP Project Management

#### 7.1 Task Lifecycle
```
Backlog → To Do → In Progress → In Review → Done
```

#### 7.2 Definition of Done
```
✅ Code complete
✅ Tests written and passing
✅ Documentation updated
✅ Code review approved
✅ Deployed to staging
✅ Stakeholder sign-off
```

#### 7.3 Sprint Process
```
Weekly Sprint:
- Monday: Sprint planning
- Daily: Standup meeting
- Thursday: Sprint review
- Friday: Retrospective
```

---

### 8. SOP Incident Management

#### 8.1 Incident Response
```
1. Identify - Deteksi masalah
2. Contain - Isolasi dampak
3. Investigate - Analisis root cause
4. Resolve - Perbaiki masalah
5. Recover - Restore services
6. Review - Document learnings
```

#### 8.2 Incident Severity
| Severity | Description | Example |
|----------|-------------|---------|
| P1 | Complete outage | Website down |
| P2 | Major feature broken | Login not working |
| P3 | Minor feature broken | Report export fails |
| P4 | Cosmetic issue | UI misalignment |

---

### 9. SOP Backup & Recovery

#### 9.1 Backup Schedule
| Type | Frequency | Retention |
|------|-----------|-----------|
| Code | On every push | Forever (Git) |
| Database | Daily | 30 days |
| Files | Weekly | 90 days |

#### 9.2 Recovery Procedures
```
Database Recovery:
1. Identify backup point
2. Stop services
3. Restore from backup
4. Verify integrity
5. Restart services
6. Monitor for issues

File Recovery:
1. Identify backup point
2. Copy from backup
3. Verify files
4. Update references
```

---

## 📊 Metrics & KPIs

### Development Metrics
| Metric | Target | Current |
|--------|--------|---------|
| Deployment Frequency | Daily | - |
| Lead Time for Changes | < 1 day | - |
| Mean Time to Recovery | < 1 hour | - |
| Change Failure Rate | < 5% | - |

### Quality Metrics
| Metric | Target |
|--------|--------|
| Test Coverage | > 80% |
| Code Review Time | < 24 hours |
| Bug Escape Rate | < 5% |
| Technical Debt | < 5% of codebase |

---

## 📝 Templates

### Bug Report Template
```markdown
## Bug Description
[Describe the bug]

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
[What should happen]

## Actual Behavior
[What happens instead]

## Screenshots
[If applicable]

## Environment
- Browser:
- OS:
- Version:
```

### Feature Request Template
```markdown
## Feature Summary
[One sentence summary]

## Problem Statement
[What problem does this solve?]

## Proposed Solution
[How should it work?]

## User Stories
- As a [type of user], I want [goal] so that [benefit].

## Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2
- [ ] Criteria 3

## Technical Notes
[Any technical considerations]
```

---

## 🎯 Priorities Framework

### Priority 1: Critical
- System down
- Data loss
- Security breach
- Critical business process blocked

### Priority 2: High
- Major feature broken
- Performance degradation
- Important feature missing

### Priority 3: Medium
- Minor bugs
- UI improvements
- Documentation updates

### Priority 4: Low
- Nice to have
- Cosmetic fixes
- Future enhancements

---

## 🔄 Continuous Improvement

### Retrospective Actions
1. Document learnings from each sprint
2. Update SOPs based on feedback
3. Implement process improvements
4. Share best practices across team
5. Track improvement metrics

### Knowledge Sharing
- Weekly sync meetings
- Documentation updates
- Technical brown bags
- Pair programming sessions

---

## 📚 Reference Documents

| Document | Location |
|----------|----------|
| Agent Architecture | `.agents/skills/agent-architecture.md` |
| Webhook Setup | `.agents/skills/webhook-auto-deploy.md` |
| Daily Automation | `.agents/skills/openhands-daily-report.md` |
| Project README | `README.md` |

---

## ✅ Agent Compliance

All agents working on this project MUST:

1. **Read and understand** this SOP document
2. **Follow** all conventions and processes
3. **Report** any deviations or improvements needed
4. **Document** decisions and learnings
5. **Comply** with security policies
6. **Maintain** quality standards

---

**Last Updated:** 2026-07-02
**Version:** 1.0.0
**Next Review:** 2026-08-02
