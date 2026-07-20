#!/usr/bin/env python3
"""
Global Sales Outreach Tracker
MAHA LAKSHMI HOLDINGS
Tracks email outreach, responses, and follow-ups
"""

import csv
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class OutreachRecord:
    lead_email: str
    lead_name: str
    company: str
    template_id: str
    subject: str
    sent_date: str
    status: str  # sent, opened, responded, interested, proposal, won, lost
    follow_up_count: int
    response_date: Optional[str]
    notes: str

class OutreachTracker:
    def __init__(self, db_file: str = "outreach/tracker.json"):
        self.db_file = db_file
        self.records: List[OutreachRecord] = []
        self.load()
    
    def load(self):
        """Load outreach records from file"""
        try:
            with open(self.db_file, 'r') as f:
                data = json.load(f)
                self.records = [OutreachRecord(**r) for r in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.records = []
    
    def save(self):
        """Save outreach records to file"""
        with open(self.db_file, 'w') as f:
            json.dump([asdict(r) for r in self.records], f, indent=2)
    
    def add_outreach(self, record: OutreachRecord):
        """Add new outreach record"""
        self.records.append(record)
        self.save()
    
    def get_pending_followups(self) -> List[OutreachRecord]:
        """Get leads that need follow-up"""
        today = datetime.now()
        pending = []
        
        for r in self.records:
            if r.status == "sent":
                sent_date = datetime.strptime(r.sent_date, "%Y-%m-%d")
                days_since = (today - sent_date).days
                
                if days_since >= 3 and r.follow_up_count == 0:
                    pending.append(r)
                elif days_since >= 7 and r.follow_up_count == 1:
                    pending.append(r)
                elif days_since >= 14 and r.follow_up_count == 2:
                    pending.append(r)
        
        return pending
    
    def get_responded_leads(self) -> List[OutreachRecord]:
        """Get leads that responded"""
        return [r for r in self.records if r.status in ["responded", "interested", "proposal", "won"]]
    
    def update_status(self, email: str, new_status: str, notes: str = ""):
        """Update lead status"""
        for r in self.records:
            if r.lead_email == email:
                r.status = new_status
                if new_status == "responded":
                    r.response_date = datetime.now().strftime("%Y-%m-%d")
                if notes:
                    r.notes = notes
                self.save()
                return True
        return False
    
    def get_stats(self) -> Dict:
        """Get outreach statistics"""
        total = len(self.records)
        sent = len([r for r in self.records if r.status == "sent"])
        opened = len([r for r in self.records if r.status == "opened"])
        responded = len([r for r in self.records if r.status in ["responded", "interested"]])
        proposal = len([r for r in self.records if r.status == "proposal"])
        won = len([r for r in self.records if r.status == "won"])
        lost = len([r for r in self.records if r.status == "lost"])
        
        return {
            "total_outreaches": total,
            "sent": sent,
            "opened": opened,
            "responded": responded,
            "proposal": proposal,
            "won": won,
            "lost": lost,
            "response_rate": round((responded / total * 100) if total > 0 else 0, 2),
            "win_rate": round((won / responded * 100) if responded > 0 else 0, 2),
            "pending_followups": len(self.get_pending_followups())
        }
    
    def generate_report(self) -> str:
        """Generate outreach report"""
        stats = self.get_stats()
        pending = self.get_pending_followups()
        hot_leads = self.get_responded_leads()
        
        report = f"""
# 📊 GLOBAL SALES OUTREACH REPORT
**Date:** {datetime.now().strftime("%Y-%m-%d")}
**Generated:** {datetime.now().strftime("%H:%M")}

---

## 📈 OUTREACH STATISTICS

| Metric | Value |
|--------|-------|
| Total Outreach | {stats['total_outreaches']} |
| Sent | {stats['sent']} |
| Opened | {stats['opened']} |
| Responded | {stats['responded']} |
| Proposal Sent | {stats['proposal']} |
| Deals Won | {stats['won']} |
| Deals Lost | {stats['lost']} |
| **Response Rate** | **{stats['response_rate']}%** |
| **Win Rate** | **{stats['win_rate']}%** |

---

## ⏳ PENDING FOLLOW-UPS ({len(pending)})

"""
        
        for p in pending[:10]:
            report += f"""
### {p.lead_name} - {p.company}
- Email: {p.lead_email}
- Template: {p.template_id}
- Sent: {p.sent_date}
- Follow-ups: {p.follow_up_count}
"""
        
        report += f"""
---

## 🔥 HOT LEADS ({len(hot_leads)})

"""
        
        for h in hot_leads[:10]:
            report += f"""
### {h.lead_name} - {h.company}
- Email: {h.lead_email}
- Status: {h.status}
- Response: {h.response_date or 'N/A'}
- Notes: {h.notes}
"""
        
        return report

def simulate_outreach(tracker: OutreachTracker, leads_file: str, count: int = 100):
    """Simulate outreach to random leads"""
    # Read leads
    with open(leads_file, 'r') as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    
    # Get already contacted emails
    contacted = set(r.lead_email for r in tracker.records)
    available = [l for l in leads if l['email'] not in contacted]
    
    # Select random leads
    selected = random.sample(available, min(count, len(available)))
    
    templates = [
        ("T-001", "Quick question about {company}"),
        ("T-002", "Digital transformation for {company}?"),
        ("T-003", "Growth opportunity for {company}"),
        ("T-004", "Technology partnership with {company}"),
        ("T-005", "Increase your {company} sales by 40%"),
    ]
    
    new_records = []
    for lead in selected:
        template_id, subject_template = random.choice(templates)
        subject = subject_template.format(company=lead['company_name'])
        
        record = OutreachRecord(
            lead_email=lead['email'],
            lead_name=lead['contact_name'],
            company=lead['company_name'],
            template_id=template_id,
            subject=subject,
            sent_date=datetime.now().strftime("%Y-%m-%d"),
            status="sent",
            follow_up_count=0,
            response_date=None,
            notes=""
        )
        new_records.append(record)
        tracker.add_outreach(record)
    
    return len(new_records)

def main():
    tracker = OutreachTracker()
    
    print("🤖 MAHA LAKSHMI HOLDINGS - Global Sales Outreach Tracker")
    print("=" * 60)
    
    # Simulate outreach
    leads_file = "/workspace/project/MAHA-LAKSHMI-CORP/leads-global.csv"
    new_count = simulate_outreach(tracker, leads_file, 100)
    print(f"\n📤 Simulated {new_count} new outreach emails")
    
    # Show stats
    stats = tracker.get_stats()
    print(f"\n📊 OUTREACH STATISTICS:")
    print(f"   Total: {stats['total_outreaches']}")
    print(f"   Response Rate: {stats['response_rate']}%")
    print(f"   Win Rate: {stats['win_rate']}%")
    print(f"   Pending Follow-ups: {stats['pending_followups']}")
    
    # Show hot leads
    hot = tracker.get_responded_leads()
    print(f"\n🔥 HOT LEADS: {len(hot)}")
    for h in hot[:5]:
        print(f"   - {h.lead_name} ({h.company}): {h.status}")
    
    # Generate report
    report = tracker.generate_report()
    with open("/workspace/project/MAHA-LAKSHMI-CORP/outreach/report.md", 'w') as f:
        f.write(report)
    print(f"\n📁 Report saved to: outreach/report.md")

if __name__ == "__main__":
    main()
