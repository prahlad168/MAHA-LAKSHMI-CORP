#!/usr/bin/env python3
"""
Global Sales Deals Pipeline
MAHA LAKSHMI HOLDINGS
Manages active deals from proposal to close
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class DealStage(Enum):
    PROSPECT = "prospect"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"

class DealPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class Deal:
    deal_id: str
    client_name: str
    company: str
    email: str
    phone: str
    service: str
    value: float  # in USD
    currency: str  # USDT, USD, etc.
    stage: str
    priority: str
    created_date: str
    updated_date: str
    expected_close: str
    notes: str
    payment_address: str  # USDT TRC20 address

class DealsPipeline:
    def __init__(self, db_file: str = "outreach/deals.json"):
        self.db_file = db_file
        self.deals: List[Deal] = []
        self.load()
    
    def load(self):
        """Load deals from file"""
        try:
            with open(self.db_file, 'r') as f:
                data = json.load(f)
                self.deals = [Deal(**d) for d in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.deals = []
    
    def save(self):
        """Save deals to file"""
        with open(self.db_file, 'w') as f:
            json.dump([asdict(d) for d in self.deals], f, indent=2)
    
    def generate_id(self) -> str:
        """Generate unique deal ID"""
        count = len(self.deals) + 1
        return f"DEAL-{datetime.now().strftime('%Y%m%d')}-{count:03d}"
    
    def add_deal(self, deal: Deal) -> str:
        """Add new deal"""
        if not deal.deal_id:
            deal.deal_id = self.generate_id()
        deal.created_date = datetime.now().strftime("%Y-%m-%d")
        deal.updated_date = datetime.now().strftime("%Y-%m-%d")
        self.deals.append(deal)
        self.save()
        return deal.deal_id
    
    def update_deal(self, deal_id: str, updates: Dict) -> bool:
        """Update deal"""
        for deal in self.deals:
            if deal.deal_id == deal_id:
                for key, value in updates.items():
                    if hasattr(deal, key):
                        setattr(deal, key, value)
                deal.updated_date = datetime.now().strftime("%Y-%m-%d")
                self.save()
                return True
        return False
    
    def move_stage(self, deal_id: str, new_stage: str) -> bool:
        """Move deal to new stage"""
        for deal in self.deals:
            if deal.deal_id == deal_id:
                deal.stage = new_stage
                deal.updated_date = datetime.now().strftime("%Y-%m-%d")
                self.save()
                return True
        return False
    
    def get_by_stage(self, stage: str) -> List[Deal]:
        """Get deals by stage"""
        return [d for d in self.deals if d.stage == stage]
    
    def get_active_deals(self) -> List[Deal]:
        """Get all active deals"""
        return [d for d in self.deals if d.stage not in ["closed_won", "closed_lost"]]
    
    def get_pipeline_value(self) -> Dict:
        """Calculate pipeline value by stage"""
        pipeline = {}
        for stage in DealStage:
            deals = self.get_by_stage(stage.value)
            value = sum(d.value for d in deals)
            pipeline[stage.value] = {
                "count": len(deals),
                "value": value
            }
        return pipeline
    
    def close_won(self, deal_id: str) -> bool:
        """Mark deal as won"""
        return self.move_stage(deal_id, DealStage.CLOSED_WON.value)
    
    def close_lost(self, deal_id: str) -> bool:
        """Mark deal as lost"""
        return self.move_stage(deal_id, DealStage.CLOSED_LOST.value)
    
    def get_weekly_target(self) -> Dict:
        """Calculate weekly targets"""
        active = self.get_active_deals()
        this_week = [d for d in active if d.stage in ["proposal", "negotiation"]]
        
        return {
            "active_deals": len(active),
            "ready_to_close": len(this_week),
            "target_closes": 2,
            "target_value": 2000,
            "projected_value": sum(d.value for d in this_week)
        }
    
    def generate_invoice(self, deal_id: str) -> Optional[Dict]:
        """Generate invoice for deal"""
        for deal in self.deals:
            if deal.deal_id == deal_id:
                invoice = {
                    "invoice_number": f"INV-GLOBAL-{datetime.now().strftime('%Y%m%d')}-{deal.deal_id.split('-')[-1]}",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "client": {
                        "name": deal.client_name,
                        "company": deal.company,
                        "email": deal.email
                    },
                    "service": deal.service,
                    "amount": deal.value,
                    "currency": deal.currency,
                    "payment_address": deal.payment_address,
                    "notes": f"Payment for {deal.service} - {deal.company}"
                }
                return invoice
        return None
    
    def generate_report(self) -> str:
        """Generate deals pipeline report"""
        pipeline = self.get_pipeline_value()
        target = self.get_weekly_target()
        
        total_value = sum(d.value for d in self.deals)
        won_value = sum(d.value for d in self.deals if d.stage == "closed_won")
        active_value = sum(d.value for d in self.get_active_deals())
        
        report = f"""
# 💼 GLOBAL SALES DEALS PIPELINE REPORT
**Date:** {datetime.now().strftime("%Y-%m-%d")}
**Generated:** {datetime.now().strftime("%H:%M")}

---

## 📊 PIPELINE SUMMARY

| Metric | Value |
|--------|-------|
| Total Deals | {len(self.deals)} |
| Active Deals | {len(self.get_active_deals())} |
| **Total Pipeline Value** | **${active_value:,.2f}** |
| Closed Won | {len(self.get_by_stage('closed_won'))} (${won_value:,.2f}) |
| Closed Lost | {len(self.get_by_stage('closed_lost'))} |

---

## 📈 PIPELINE BY STAGE

| Stage | Deals | Value |
|-------|-------|-------|
"""
        
        for stage, data in pipeline.items():
            stage_name = stage.replace("_", " ").title()
            report += f"| {stage_name} | {data['count']} | ${data['value']:,.2f} |\n"
        
        report += f"""
---

## 🎯 WEEKLY TARGET

| Metric | Target | Projected |
|--------|--------|-----------|
| Ready to Close | 2 | {target['ready_to_close']} |
| Target Value | $2,000 | ${target['projected_value']:,.2f} |

---

## 🔥 ACTIVE DEALS

"""
        
        for deal in self.get_active_deals():
            stage_emoji = {
                "prospect": "🔍",
                "qualified": "✅",
                "proposal": "📋",
                "negotiation": "🤝",
                "closed_won": "🎉",
                "closed_lost": "❌"
            }.get(deal.stage, "📌")
            
            priority_color = {
                "low": "🟢",
                "medium": "🟡",
                "high": "🟠",
                "urgent": "🔴"
            }.get(deal.priority, "⚪")
            
            report += f"""
### {stage_emoji} {deal.client_name} - {deal.company}
- **Deal ID:** {deal.deal_id}
- **Service:** {deal.service}
- **Value:** ${deal.value:,.2f} ({deal.currency})
- **Stage:** {deal.stage.replace('_', ' ').title()}
- **Priority:** {priority_color} {deal.priority.upper()}
- **Expected Close:** {deal.expected_close}
- **Updated:** {deal.updated_date}
- **Notes:** {deal.notes or 'N/A'}
"""
        
        report += f"""
---

## 💰 USDT PAYMENT

**Wallet Address:** TNFs1SP2C8HxGSJkSH3hJamf8ukgtnW7U6
**Network:** TRC20 (Tron)

---

## 📋 NEXT ACTIONS

1. Follow up with {len([d for d in self.get_active_deals() if d.stage == 'proposal'])} proposal-stage deals
2. Push {len([d for d in self.get_active_deals() if d.stage == 'negotiation'])} deals to close
3. Create invoices for closed-won deals

"""
        
        return report

def create_sample_deals(pipeline: DealsPipeline):
    """Create sample deals for demonstration"""
    sample_deals = [
        Deal(
            deal_id="",
            client_name="Sarah Johnson",
            company="Melbourne Digital Agency",
            email="sarah@melbdigital.au",
            phone="+61 400 123 456",
            service="SEO Optimization Package",
            value=800,
            currency="USDT",
            stage="proposal",
            priority="high",
            created_date="",
            updated_date="",
            expected_close="2026-07-25",
            notes="Interested in ongoing SEO services",
            payment_address="TNFs1SP2C8HxGSJkSH3hJamf8ukgtnW7U6"
        ),
        Deal(
            deal_id="",
            client_name="David Chen",
            company="SG Digital Solutions",
            email="david@sgdigital.sg",
            phone="+65 9000 1234",
            service="Website Development",
            value=1500,
            currency="USDT",
            stage="negotiation",
            priority="high",
            created_date="",
            updated_date="",
            expected_close="2026-07-22",
            notes="Final contract review",
            payment_address="TNFs1SP2C8HxGSJkSH3hJamf8ukgtnW7U6"
        ),
        Deal(
            deal_id="",
            client_name="Michael Park",
            company="HealthTech Pro",
            email="michael@healthtechpro.com",
            phone="+1 555 123 4567",
            service="Mobile App Development",
            value=2000,
            currency="USDT",
            stage="qualified",
            priority="medium",
            created_date="",
            updated_date="",
            expected_close="2026-07-30",
            notes="Discovery call completed - needs proposal",
            payment_address="TNFs1SP2C8HxGSJkSH3hJamf8ukgtnW7U6"
        ),
        Deal(
            deal_id="",
            client_name="Emma Wilson",
            company="London EdTech",
            email="emma@lonedtech.co.uk",
            phone="+44 20 1234 5678",
            service="Platform Development",
            value=3000,
            currency="USDT",
            stage="proposal",
            priority="urgent",
            created_date="",
            updated_date="",
            expected_close="2026-07-21",
            notes="Quick turnaround needed",
            payment_address="TNFs1SP2C8HxGSJkSH3hJamf8ukgtnW7U6"
        ),
    ]
    
    for deal in sample_deals:
        pipeline.add_deal(deal)

def main():
    pipeline = DealsPipeline()
    
    print("💼 MAHA LAKSHMI HOLDINGS - Global Sales Deals Pipeline")
    print("=" * 60)
    
    # Create sample deals if empty
    if len(pipeline.deals) == 0:
        print("\n📦 Creating sample deals...")
        create_sample_deals(pipeline)
        print(f"✅ Created {len(pipeline.deals)} sample deals")
    
    # Show pipeline
    pipeline_summary = pipeline.get_pipeline_value()
    print("\n📈 PIPELINE SUMMARY:")
    for stage, data in pipeline_summary.items():
        if data['count'] > 0:
            print(f"   {stage.replace('_', ' ').title()}: {data['count']} deals (${data['value']:,.2f})")
    
    # Show target
    target = pipeline.get_weekly_target()
    print(f"\n🎯 WEEKLY TARGET:")
    print(f"   Active Deals: {target['active_deals']}")
    print(f"   Ready to Close: {target['ready_to_close']}")
    print(f"   Projected Value: ${target['projected_value']:,.2f}")
    
    # Generate and save report
    report = pipeline.generate_report()
    with open("/workspace/project/MAHA-LAKSHMI-CORP/outreach/deals-report.md", 'w') as f:
        f.write(report)
    print(f"\n📁 Report saved to: outreach/deals-report.md")

if __name__ == "__main__":
    main()
