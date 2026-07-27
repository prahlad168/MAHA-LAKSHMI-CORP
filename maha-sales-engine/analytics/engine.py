#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Analytics
Responsibilities:
- Traffic
- Sales
- Revenue
- Conversion
- Top products
- Top countries
- Marketplace performance
- Trend analysis
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from collections import defaultdict

logger = logging.getLogger("maha-sales-engine.analytics")


@dataclass
class DailyMetrics:
    """Daily performance metrics"""
    date: str
    leads_generated: int = 0
    outreach_sent: int = 0
    responses_received: int = 0
    proposals_sent: int = 0
    deals_closed: int = 0
    revenue_usd: float = 0.0
    revenue_idr: float = 0.0
    website_visits: int = 0
    conversion_rate: float = 0.0


class Analytics:
    """Analyze performance data"""
    
    def __init__(self, config, db_manager):
        self.config = config
        self.db = db_manager
        self.metrics_history: List[DailyMetrics] = []
    
    def get_today_metrics(self) -> DailyMetrics:
        """Get today's metrics"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Leads generated today
            cursor.execute("SELECT COUNT(*) FROM leads WHERE date(created_at) = ?", (today,))
            leads_generated = cursor.fetchone()[0]
            
            # Outreach sent today
            cursor.execute("SELECT COUNT(*) FROM outreach_log WHERE date(sent_at) = ?", (today,))
            outreach_sent = cursor.fetchone()[0]
            
            # Responses today
            cursor.execute("SELECT COUNT(*) FROM outreach_log WHERE date(response_at) = ? AND response_received = 1", (today,))
            responses_received = cursor.fetchone()[0]
            
            # Transactions today
            cursor.execute("SELECT COUNT(*), SUM(amount) FROM transactions WHERE date(created_at) = ? AND status = 'completed'", (today,))
            txn_row = cursor.fetchone()
            deals_closed = txn_row[0] or 0
            revenue_usd = txn_row[1] or 0.0
            
            # Conversion rate
            conversion_rate = (deals_closed / outreach_sent * 100) if outreach_sent > 0 else 0.0
            
            return DailyMetrics(
                date=today,
                leads_generated=leads_generated,
                outreach_sent=outreach_sent,
                responses_received=responses_received,
                deals_closed=deals_closed,
                revenue_usd=revenue_usd,
                revenue_idr=revenue_usd * 16000,  # Approximate
                conversion_rate=conversion_rate
            )
            
        except Exception as e:
            logger.error(f"Failed to get today's metrics: {e}")
            return DailyMetrics(date=today)
    
    def get_period_metrics(self, days: int = 7) -> List[DailyMetrics]:
        """Get metrics for past N days"""
        metrics = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            # In production: query database for each day
            metrics.append(DailyMetrics(date=date))
        
        return metrics
    
    def get_product_performance(self) -> List[Dict[str, Any]]:
        """Get performance by product"""
        # In production: query database with JOINs
        return [
            {"product_id": "social-media-kit", "sales": 0, "revenue": 0.0, "conversion_rate": 0.0},
            {"product_id": "seo-bundle", "sales": 0, "revenue": 0.0, "conversion_rate": 0.0},
            {"product_id": "whatsapp-marketing", "sales": 0, "revenue": 0.0, "conversion_rate": 0.0}
        ]
    
    def get_channel_performance(self) -> List[Dict[str, Any]]:
        """Get performance by channel"""
        # In production: aggregate from outreach_log
        return [
            {"channel": "email", "sent": 0, "responses": 0, "conversion_rate": 0.0},
            {"channel": "whatsapp", "sent": 0, "responses": 0, "conversion_rate": 0.0},
            {"channel": "linkedin", "sent": 0, "responses": 0, "conversion_rate": 0.0}
        ]
    
    def get_country_performance(self) -> List[Dict[str, Any]]:
        """Get performance by country"""
        # In production: aggregate from leads and transactions
        return [
            {"country": "Indonesia", "leads": 0, "revenue": 0.0, "deals": 0},
            {"country": "USA", "leads": 0, "revenue": 0.0, "deals": 0},
            {"country": "Brazil", "leads": 0, "revenue": 0.0, "deals": 0}
        ]
    
    def get_revenue_trend(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get revenue trend"""
        trend = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            trend.append({
                "date": date,
                "revenue_usd": 0.0,
                "revenue_idr": 0.0,
                "deals": 0
            })
        return trend
    
    def get_conversion_funnel(self) -> Dict[str, Any]:
        """Get conversion funnel"""
        return {
            "leads_generated": 0,
            "outreach_sent": 0,
            "responses_received": 0,
            "proposals_sent": 0,
            "deals_closed": 0,
            "funnel": {
                "lead_to_outreach": 0.0,
                "outreach_to_response": 0.0,
                "response_to_proposal": 0.0,
                "proposal_to_deal": 0.0
            }
        }
    
    def get_top_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing products"""
        products = self.get_product_performance()
        products.sort(key=lambda x: x["revenue"], reverse=True)
        return products[:limit]
    
    def get_top_countries(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing countries"""
        countries = self.get_country_performance()
        countries.sort(key=lambda x: x["revenue"], reverse=True)
        return countries[:limit]
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary for dashboard"""
        today = self.get_today_metrics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "today": asdict(today),
            "products": self.get_product_performance(),
            "channels": self.get_channel_performance(),
            "countries": self.get_country_performance(),
            "revenue_trend": self.get_revenue_trend(7),
            "conversion_funnel": self.get_conversion_funnel(),
            "top_products": self.get_top_products(),
            "top_countries": self.get_top_countries()
        }
    
    def generate_report(self, report_type: str = "daily") -> Dict[str, Any]:
        """Generate analytics report"""
        if report_type == "daily":
            return {
                "report_type": "daily",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "metrics": asdict(self.get_today_metrics()),
                "summary": self.get_dashboard_summary()
            }
        elif report_type == "weekly":
            return {
                "report_type": "weekly",
                "period": "last_7_days",
                "metrics": [asdict(m) for m in self.get_period_metrics(7)],
                "summary": self.get_dashboard_summary()
            }
        else:
            return {"error": "Invalid report type"}


def main():
    """Test analytics"""
    from core.engine import ConfigManager, DatabaseManager
    from pathlib import Path
    
    config = ConfigManager(Path("config/engine.yaml"))
    db = DatabaseManager(Path(config.get("database.path")))
    
    analytics = Analytics(config, db)
    
    # Get today's metrics
    today = analytics.get_today_metrics()
    print(f"\nToday's Metrics:")
    print(f"  Leads: {today.leads_generated}")
    print(f"  Outreach: {today.outreach_sent}")
    print(f"  Revenue: ${today.revenue_usd:.2f}")
    
    # Get dashboard summary
    summary = analytics.get_dashboard_summary()
    print(f"\nDashboard Summary generated at: {summary['timestamp']}")
    
    db.close()


if __name__ == "__main__":
    main()
