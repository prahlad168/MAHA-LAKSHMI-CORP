#!/usr/bin/env python3
"""
🚀 AUTONOMOUS SALES ORCHESTRATOR - MAHA LAKSHMI
Central brain that coordinates all agents
CEO receives ONLY: Daily revenue reports
"""

import sys
import os
import importlib.util
import time
import threading
from datetime import datetime

# Load modules directly from files
def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

agent_dir = os.path.dirname(os.path.abspath(__file__))

# Load modules
sales_core = load_module("sales_agent_core", os.path.join(agent_dir, "core", "sales-agent-core.py"))
market_analysis = load_module("market_analysis", os.path.join(agent_dir, "core", "market-analysis.py"))
finance_agent = load_module("finance_agent", os.path.join(agent_dir, "finance", "finance-agent.py"))
ceo_reporter = load_module("ceo_reporter", os.path.join(agent_dir, "reporting", "ceo-reporter.py"))

AutonomousSalesAgent = sales_core.AutonomousSalesAgent
MarketAnalyzer = market_analysis.MarketAnalyzer
AutonomousFinanceAgent = finance_agent.AutonomousFinanceAgent
CEOReporter = ceo_reporter.CEOReporter

class AutonomousSalesOrchestrator:
    def __init__(self):
        self.sales_agent = AutonomousSalesAgent()
        self.finance_agent = AutonomousFinanceAgent()
        self.market_analyzer = MarketAnalyzer()
        self.ceo_reporter = CEOReporter()
        
        self.running = False
        self.start_time = None
        self.cycle_count = 0
        
        # Ensure log directory exists
        os.makedirs(os.path.join(agent_dir, "logs"), exist_ok=True)
    
    def start(self):
        """Start autonomous operation"""
        self.running = True
        self.start_time = datetime.now()
        
        print("=" * 70)
        print("👑 MAHA LAKSHMI - AUTONOMOUS SALES ORCHESTRATOR")
        print("=" * 70)
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Domain: mahalaksmi.web.id")
        print(f"Mode: FULLY AUTONOMOUS")
        print(f"CEO Receives: Revenue reports only")
        print("=" * 70)
        
        # Start background threads
        self._start_background_threads()
        
        # Run main loop
        self._run_main_loop()
    
    def _start_background_threads(self):
        """Start background agent threads"""
        sales_thread = threading.Thread(target=self._run_sales_agent, daemon=True)
        sales_thread.start()
        
        finance_thread = threading.Thread(target=self._run_finance_agent, daemon=True)
        finance_thread.start()
        
        market_thread = threading.Thread(target=self._run_market_analysis, daemon=True)
        market_thread.start()
        
        print("✅ All agents started in background")
    
    def _run_sales_agent(self):
        """Run sales agent loop"""
        while self.running:
            try:
                self.sales_agent.run_daily_outreach()
                self.sales_agent.run_followup_sequence()
                time.sleep(3600)  # 1 hour
            except Exception as e:
                print(f"Sales Agent Error: {e}")
                time.sleep(300)
    
    def _run_finance_agent(self):
        """Run finance agent loop"""
        while self.running:
            try:
                self.finance_agent.run_daily_cycle()
                time.sleep(86400)  # 24 hours
            except Exception as e:
                print(f"Finance Agent Error: {e}")
                time.sleep(3600)
    
    def _run_market_analysis(self):
        """Run market analysis loop"""
        while self.running:
            try:
                self.market_analyzer.analyze_digital_product_trends()
                self.market_analyzer.optimize_templates()
                self.market_analyzer.optimize_targeting()
                time.sleep(86400)  # 24 hours
            except Exception as e:
                print(f"Market Analysis Error: {e}")
                time.sleep(3600)
    
    def _run_main_loop(self):
        """Main orchestrator loop"""
        while self.running:
            try:
                self.cycle_count += 1
                self._generate_and_send_ceo_report()
                self._log_orchestrator_status()
                time.sleep(3600)  # 1 hour
            except Exception as e:
                print(f"Orchestrator Error: {e}")
                time.sleep(300)
    
    def _generate_and_send_ceo_report(self):
        """Generate and send CEO report"""
        try:
            sales_stats = self.sales_agent.get_stats()
            finance_stats = self.finance_agent.get_financial_summary()
            market_insights = self.market_analyzer.analyze_response_rates_by_segment()
            
            report = self.ceo_reporter.generate_executive_summary(
                sales_stats, finance_stats, market_insights
            )
            
            self.ceo_reporter.save_report({
                "timestamp": datetime.now().isoformat(),
                "sales_stats": sales_stats,
                "finance_stats": finance_stats,
                "market_insights": market_insights,
                "report": report
            })
            
            print("\n" + "=" * 70)
            print("👑 CEO DAILY REPORT")
            print("=" * 70)
            print(report)
            print("=" * 70)
            
        except Exception as e:
            print(f"Report Generation Error: {e}")
    
    def _log_orchestrator_status(self):
        """Log orchestrator status"""
        uptime = datetime.now() - self.start_time
        print(f"\n🔄 Orchestrator Cycle #{self.cycle_count}")
        print(f"⏰ Uptime: {uptime}")
        print(f"📊 Sales Stats: {self.sales_agent.get_stats()}")
        print(f"💰 Finance Stats: {self.finance_agent.get_financial_summary()}")
    
    def stop(self):
        """Stop autonomous operation"""
        self.running = False
        print("\n🛑 Autonomous operation stopped")


def main():
    """Main entry point"""
    orchestrator = AutonomousSalesOrchestrator()
    
    try:
        orchestrator.start()
    except KeyboardInterrupt:
        print("\n\nKeyboard interrupt received...")
        orchestrator.stop()
    except Exception as e:
        print(f"\nFatal Error: {e}")
        orchestrator.stop()


if __name__ == "__main__":
    main()
