# SOP-002: INVOICE GENERATION
## Standard Process for Invoice Generation

**Version:** 1.0.0
**Created:** 2026-07-03
**Category:** Finance

---

## 1. PURPOSE

```
Standar proses untuk generate invoice dari creation hingga payment received.
```

## 2. SCOPE

```
- Project Invoice
- Monthly Retainer Invoice
- Product Sale Invoice
- Service Invoice
```

## 3. INVOICE TYPES

### 3.1 Project Invoice
```
Trigger: Project milestone reached or project completion
Amount: Based on project quotation
```

### 3.2 Monthly Retainer Invoice
```
Trigger: Beginning of month
Amount: Fixed retainer amount
```

### 3.3 Product Invoice
```
Trigger: Product sold
Amount: Product price
```

### 3.4 Service Invoice
```
Trigger: Service delivered
Amount: Based on service agreement
```

---

## 4. PROCESS FLOW

```
┌──────────────────────────────────────────────────────────────────┐
│                    INVOICE LIFECYCLE                             │
└──────────────────────────────────────────────────────────────────┘

INVOICE TRIGGER
         │
         ▼
CREATE INVOICE
         │
         ▼
SEND TO CLIENT
         │
         ▼
TRACK PAYMENT
         │
         ├── Paid → CLOSE INVOICE
         ├── Overdue → FOLLOW UP
         └── Cancelled → ARCHIVE
```

---

## 5. DETAILED STEPS

### Step 1: Invoice Trigger

**Trigger Events:**

| Type | Trigger |
|------|---------|
| Project | Milestone reached / Completion |
| Retainer | 1st of month |
| Product | Sale confirmed |
| Service | Service delivered |

**Checklist:**
- [ ] Verify work completed
- [ ] Verify amount
- [ ] Get internal approval

---

### Step 2: Create Invoice

**Invoice Fields:**

```markdown
INVOICE

Invoice Number: INV-YYYYMMDD-XXX
Date: [Tanggal]
Due Date: [Tanggal + 14 days]

FROM:
[Company Name]
[Address]
[Tax ID]

TO:
[Client Name]
[Client Address]

=================================================================
No | Description | Qty | Unit Price | Amount
-----------------------------------------------------------------
1  |            |     |            |
-----------------------------------------------------------------
                                        Subtotal: Rp XXX
                                        PPN 11%: Rp XXX
                                        TOTAL: Rp XXX
=================================================================

Payment Terms: 14 days
Payment Method: Transfer BCA 6485086645

Notes:
- Payment confirmation: [Email/WhatsApp]
- Late payment: 1% per month
```

**Numbering Convention:**
```
INV-[YYYY][MM][DD]-[SEQ]
Example: INV-20260703-001
```

**Checklist:**
- [ ] Invoice number generated
- [ ] All fields filled correctly
- [ ] PPN 11% calculated
- [ ] Total correct
- [ ] Payment details included

---

### Step 3: Send Invoice

**Send Methods:**

| Priority | Method | When |
|----------|--------|------|
| High | Email + WhatsApp | All invoices |
| Urgent | Direct WhatsApp | Overdue |

**Email Template:**
```
Subject: Invoice [INV-XXX] - [Company Name]

Dear [Client Name],

Attached is invoice [INV-XXX] for [description].

Amount: Rp [Amount]
Due Date: [Date]

Payment to:
Bank: BCA
Account: 6485086645
Account Name: [Owner Name]

Please confirm payment via reply email or WhatsApp.

Best regards,
[Company Name]
```

**Checklist:**
- [ ] Email sent
- [ ] WhatsApp sent (if needed)
- [ ] CC to finance
- [ ] CRM updated

---

### Step 4: Track Payment

**Payment Tracking Schedule:**

| Days | Action |
|------|--------|
| 0 | Invoice sent |
| 7 | Reminder 1 |
| 14 | Due date |
| 17 | Reminder 2 |
| 21 | Reminder 3 |
| 28 | Escalation |

**Reminders:**

**Reminder 1 (Day 7):**
```
Subject: Reminder: Invoice [INV-XXX] due in 7 days

Dear [Client],

This is a friendly reminder that invoice [INV-XXX] 
for Rp [Amount] is due in 7 days.

Due Date: [Date]

Please arrange payment at your earliest convenience.
```

**Reminder 2 (Day 17 - Overdue):**
```
Subject: URGENT: Invoice [INV-XXX] is overdue

Dear [Client],

Invoice [INV-XXX] for Rp [Amount] was due on [Date] 
and is now [X] days overdue.

Please prioritize this payment to avoid late fees.
```

**Reminder 3 (Day 21):**
```
Subject: Final Notice: Invoice [INV-XXX]

Dear [Client],

This is a final notice for overdue invoice [INV-XXX].

If payment is not received within 3 days, we will:
1. Suspend services
2. Add late fee 1%/month
3. Take legal action if necessary

Please contact us immediately to resolve this matter.
```

**Checklist:**
- [ ] Payment status updated
- [ ] Reminders sent on schedule
- [ ] Escalation followed if needed

---

### Step 5: Payment Received

**Upon Payment:**

1. Mark invoice as PAID in CRM
2. Issue receipt
3. Send thank you message
4. Update financial records

**Receipt Template:**
```
RECEIPT

Receipt Number: RCP-YYYYMMDD-XXX
Date: [Tanggal]

Received from: [Client Name]
Amount: Rp [Amount]
For payment of: Invoice [INV-XXX]
Payment Method: [Transfer/Other]

Paid to:
Bank: BCA
Account: 6485086645

Thank you for your payment!

[Company Name]
```

**Checklist:**
- [ ] Invoice marked PAID
- [ ] Receipt issued
- [ ] Financial records updated
- [ ] Client thanked
- [ ] Project status updated

---

## 6. ESCALATION PROCESS

**Day 28+ Overdue:**

```
1. Suspend active services
2. Send legal notice
3. Consider collection agency
4. Document all communication
```

---

## 7. INVOICE ARCHIVE

**Archive Location:** `finance/invoices/`
**Naming:** `INV-YYYYMMDD-XXX.pdf`

---

## 8. RELATED DOCUMENTS

- SOP-001: Website Development
- SOP-003: Client Meeting
- SOP-010: Daily Report
- Template: Invoice
- Template: Receipt

---

## 9. METRICS

| Metric | Target |
|--------|--------|
| Invoice Accuracy | 99.9% |
| On-time Payment | >90% |
| Collection Time | <30 days |

---

**Document Status:** APPROVED
**Version:** 1.0.0
**Created:** 2026-07-03
**Next Review:** 2026-08-03
