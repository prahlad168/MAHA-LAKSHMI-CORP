# SOP-001: CREATE WEBSITE
## Standard Process for Website Development

**Version:** 1.0.0
**Created:** 2026-07-03
**Category:** Operations

---

## 1. PURPOSE

```
Standar proses untuk pengembangan website dari awal hingga handover.
```

## 2. SCOPE

```
- Landing Page
- Company Profile
- E-commerce
- Custom Web Application
```

## 3. PROCESS FLOW

```
┌──────────────────────────────────────────────────────────────────┐
│                    WEBSITE DEVELOPMENT FLOW                       │
└──────────────────────────────────────────────────────────────────┘

1. CLIENT REQUIREMENTS
         │
         ▼
2. PROPOSAL & QUOTATION
         │
         ▼
3. CONTRACT & DEPOSIT
         │
         ▼
4. DESIGN PHASE
         │
         ▼
5. DEVELOPMENT PHASE
         │
         ▼
6. TESTING PHASE
         │
         ▼
7. DEPLOYMENT
         │
         ▼
8. HANDOVER
```

---

## 4. DETAILED STEPS

### Step 1: Client Requirements

**Tujuan:** Memahami kebutuhan klien secara detail

**Input:**
- Brief form (terisi oleh klien)
- Budget
- Timeline

**Proses:**
1. Schedule kickoff meeting
2. Ajukan pertanyaan berikut:
   - Apa tujuan website?
   - Siapa target audience?
   - Fitur apa yang dibutuhkan?
   - Referensi website lain?
   - Brand guidelines?
   - Competitors?

**Output:**
- Requirements document
- Project scope
- Timeline estimation

**Checklist:**
- [ ] Brief form received
- [ ] Budget confirmed
- [ ] Timeline agreed
- [ ] Requirements documented

---

### Step 2: Proposal & Quotation

**Tujuan:** Membuat proposal dan quotation resmi

**Input:**
- Requirements document
- Timeline

**Proses:**
1. Hitung effort (design, development, testing)
2. Buat quotation dengan breakdown:
   - Design: X%
   - Development: X%
   - Testing: X%
   - Deployment: X%
3. Include PPN 11%
4. Kirim proposal + quotation

**Output:**
- Proposal document
- Quotation document

**Quotation Template:**
```
PROJECT: [Nama Project]
CLIENT: [Nama Client]
DATE: [Tanggal]

| No | Item | Description | Price |
|----|------|-------------|-------|
| 1  |      |             |       |
|    |      | Subtotal    |       |
|    |      | PPN 11%    |       |
|    |      | TOTAL       |       |

Timeline: [X] weeks
Payment Terms:
- 50% upfront
- 50% after completion
```

---

### Step 3: Contract & Deposit

**Tujuan:** Amankan project dengan contract dan deposit

**Input:**
- Approved quotation
- Client confirmation

**Proses:**
1. Buat contract based on quotation
2. Include:
   - Scope of work
   - Timeline
   - Payment terms
   - Revision limits
   - Ownership clause
   - Support period
3. Client tanda tangan
4. Deposit 50% dibayarkan

**Output:**
- Signed contract
- Deposit payment received

**Checklist:**
- [ ] Contract signed
- [ ] 50% deposit received
- [ ] Invoice created
- [ ] Receipt issued

---

### Step 4: Design Phase

**Tujuan:** Hasilkan design yang sesuai ekspektasi klien

**Proses:**

**4.1 Wireframe**
```
- Buat wireframe low-fidelity
- Kirim untuk review
- Collect feedback
- Revisi jika perlu
```

**4.2 Mockup**
```
- Buat high-fidelity mockup
- Pilih 2-3 color scheme
- Kirim untuk review
- Final approval
```

**4.3 Design Spec**
```
- Buat design system (colors, typography, spacing)
- Siapkan assets (images, icons)
- Prepare responsive breakpoints
```

**Output:**
- Approved wireframe
- Approved mockup
- Design assets

**Checklist:**
- [ ] Wireframe approved
- [ ] Mockup approved
- [ ] Assets prepared
- [ ] Design spec complete

---

### Step 5: Development Phase

**Tujuan:** Develop website sesuai design

**Proses:**

**5.1 Setup**
```
- Setup development environment
- Setup version control
- Create repository
- Setup hosting staging
```

**5.2 Frontend**
```
- HTML/CSS/JS development
- Responsive implementation
- Performance optimization
- SEO basics
```

**5.3 Backend (if applicable)**
```
- API development
- Database setup
- Authentication
- CMS integration
```

**5.4 Third-party Integrations**
```
- Payment gateway
- Analytics
- Chat widget
- Other integrations
```

**Output:**
- Working website on staging
- Source code in repository

**Checklist:**
- [ ] Development complete
- [ ] Staging deployed
- [ ] Basic testing passed

---

### Step 6: Testing Phase

**Tujuan:** Pastikan website bebas bug sebelum launch

**Testing Checklist:**

**Functional Testing:**
- [ ] All links work
- [ ] Forms submit correctly
- [ ] Validation works
- [ ] Error handling works
- [ ] Loading states work

**Responsive Testing:**
- [ ] Desktop (1920px+)
- [ ] Laptop (1366px)
- [ ] Tablet (768px)
- [ ] Mobile (375px)

**Performance Testing:**
- [ ] PageSpeed > 80
- [ ] Image optimization
- [ ] Caching enabled
- [ ] Minification done

**Security Testing:**
- [ ] HTTPS enabled
- [ ] Forms protected
- [ ] No sensitive data exposed

**Client UAT:**
```
- Deploy to staging
- Kirim test credentials ke client
- Client test dan approve
- Catat feedback
- Fix bugs jika ada
```

**Output:**
- Test report
- Bug fixes (if any)
- Client approval

---

### Step 7: Deployment

**Tujuan:** Launch website ke production

**Proses:**

**7.1 Pre-deployment**
```
- Backup production (if exists)
- Final code review
- DNS update准备好了吗？
- SSL certificate ready
```

**7.2 Deployment**
```
- Deploy to production
- Run post-deployment checks
- Verify all functionality
- Monitor for errors
```

**7.3 Post-deployment**
```
- Client notification
- Training scheduled
- Documentation sent
- Final invoice sent
```

**Output:**
- Live website
- All documentation
- Final invoice issued

---

### Step 8: Handover

**Tujuan:** Serahkan semua asset ke klien

**Handover Checklist:**

**Documentation:**
- [ ] User manual
- [ ] Admin manual
- [ ] API documentation (if applicable)
- [ ] Training video recorded

**Access:**
- [ ] Hosting access shared
- [ ] Domain access shared
- [ ] Source code transferred
- [ ] Admin credentials shared

**Support:**
- [ ] Support period explained (default: 30 days)
- [ ] Bug fix process explained
- [ ] Maintenance options presented

**Payment:**
- [ ] Final payment collected
- [ ] Receipt issued
- [ ] Thank you letter sent

**Output:**
- Project complete
- Client satisfied
- Testimonial requested
- Case study documented

---

## 5. DELIVERABLES

| Deliverable | Format |
|-------------|--------|
| Source Code | Git repository |
| Design Files | Figma/Adobe XD |
| Documentation | PDF/Markdown |
| Admin Manual | PDF/Video |
| Training | Video/Zoom |

---

## 6. TIMELINE

| Website Type | Timeline |
|--------------|----------|
| Landing Page | 1-2 weeks |
| Company Profile | 2-3 weeks |
| E-commerce | 4-8 weeks |
| Custom Web App | 8-16 weeks |

---

## 7. REVISIONS

| Package | Revisions Included |
|---------|-------------------|
| Basic | 2 revisions |
| Standard | 5 revisions |
| Premium | Unlimited |

---

## 8. PRICING REFERENCE

| Type | Basic | Standard | Premium |
|------|-------|----------|---------|
| Landing Page | Rp 1.5jt | Rp 2.5jt | Rp 5jt |
| Company Profile | Rp 3jt | Rp 5jt | Rp 10jt |
| E-commerce | Rp 8jt | Rp 15jt | Rp 25jt+ |
| Custom App | Rp 15jt | Rp 30jt | Rp 50jt+ |

---

## 9. RELATED DOCUMENTS

- SOP-002: Client Meeting
- SOP-003: Invoice Generation
- SOP-010: Daily Report
- Template: Proposal
- Template: Contract
- Template: Quotation

---

**Document Status:** APPROVED
**Version:** 1.0.0
**Created:** 2026-07-03
**Next Review:** 2026-08-03
