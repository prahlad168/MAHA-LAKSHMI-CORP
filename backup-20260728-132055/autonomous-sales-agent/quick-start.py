#!/usr/bin/env python3
"""
🚀 QUICK START - Autonomous Sales Agent
Runs immediately with sample data to demonstrate functionality
"""

import sys
import os
import importlib.util

# Add paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
agent_dir = os.path.dirname(os.path.abspath(__file__))

# Load modules directly from files to avoid package naming issues
def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# Load core modules
sales_core = load_module("sales_agent_core", os.path.join(agent_dir, "core", "sales-agent-core.py"))
market_analysis = load_module("market_analysis", os.path.join(agent_dir, "core", "market-analysis.py"))
finance_agent = load_module("finance_agent", os.path.join(agent_dir, "finance", "finance-agent.py"))
ceo_reporter = load_module("ceo_reporter", os.path.join(agent_dir, "reporting", "ceo-reporter.py"))

AutonomousSalesAgent = sales_core.AutonomousSalesAgent
Lead = sales_core.Lead
MarketAnalyzer = market_analysis.MarketAnalyzer
AutonomousFinanceAgent = finance_agent.AutonomousFinanceAgent
CEOReporter = ceo_reporter.CEOReporter
from datetime import datetime

def quick_demo():
    """Run quick demo to show system works"""
    print("=" * 70)
    print("👑 MAHA LAKSHMI - AUTONOMOUS SALES AGENT")
    print("🚀 QUICK START MODE")
    print("=" * 70)
    print()
    
    # Initialize agents
    sales_agent = AutonomousSalesAgent()
    finance_agent = AutonomousFinanceAgent()
    market_analyzer = MarketAnalyzer()
    ceo_reporter = CEOReporter()
    
    print("✅ Agents initialized")
    print("✅ Loading sample data...")
    
    # Load sample leads
    sample_leads = sales_agent._get_sample_leads(10)
    for lead_data in sample_leads:
        lead = Lead(
            id=f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            name=lead_data["name"],
            email=lead_data["email"],
            phone=lead_data["phone"],
            company=lead_data["company"],
            industry=lead_data["industry"],
            country=lead_data["country"],
            language=lead_data["language"],
            source=lead_data["source"]
        )
        sales_agent.qualify_lead(lead)
        sales_agent.add_lead(lead)
    
    print(f"✅ Loaded {len(sales_agent.db.get_leads_by_status('new'))} leads")
    
    # Run outreach
    print("\n📧 Running email outreach...")
    sales_agent.run_daily_outreach()
    
    # Run market analysis
    print("\n📊 Running market analysis...")
    trends = market_analyzer.analyze_digital_product_trends()
    targeting = market_analyzer.optimize_targeting()
    
    # Generate CEO report
    print("\n👑 Generating CEO report...")
    sales_stats = sales_agent.get_stats()
    finance_stats = finance_agent.get_financial_summary()
    market_insights = market_analyzer.analyze_response_rates_by_segment()
    
    report = ceo_reporter.generate_executive_summary(
        sales_stats, finance_stats, market_insights
    )
    
    print("\n" + "=" * 70)
    print("📋 SYSTEM STATUS REPORT")
    print("=" * 70)
    print(report)
    
    # Save report
    os.makedirs("autonomous-sales-agent/logs", exist_ok=True)
    ceo_reporter.save_report({
        "timestamp": datetime.now().isoformat(),
        "sales_stats": sales_stats,
        "finance_stats": finance_stats,
        "market_insights": market_insights,
        "status": "running"
    })
    
    print("\n" + "=" * 70)
    print("✅ SYSTEM READY")
    print("=" * 70)
    print("🌐 Domain: mahalaksmi.web.id")
    print("💰 Payment gateways: Stripe, PayPal, Wise, Crypto, Midtrans")
    print("🤖 Agents: Sales, Finance, Market Analyzer, Self-Improvement")
    print("👑 CEO receives: Daily revenue reports at 23:59")
    print("\n🚀 To run continuously: python3 autonomous-sales-agent/orchestrator.py")
    print("=" * 70)
    
    return sales_agent, finance_agent, market_analyzer, ceo_reporter

if __name__ == "__main__":
    quick_demo()
