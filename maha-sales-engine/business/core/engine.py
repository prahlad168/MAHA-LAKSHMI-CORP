#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Business Execution Core
Autonomous business execution pipeline.
"""

import sys
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine import ConfigManager, DatabaseManager

logger = logging.getLogger("maha-sales-engine.business.core")


@dataclass
class DailyReport:
    """Daily business report"""
    report_date: str
    products_generated: int = 0
    products_published: int = 0
    marketing_content_created: int = 0
    leads_generated: int = 0
    sales_count: int = 0
    revenue_usd: float = 0.0
    revenue_idr: float = 0.0
    cogs_usd: float = 0.0
    net_profit_usd: float = 0.0
    net_profit_idr: float = 0.0
    ceo_share_usd: float = 0.0
    ceo_share_idr: float = 0.0
    reinvestment_usd: float = 0.0
    reinvestment_idr: float = 0.0
    operational_usd: float = 0.0
    operational_idr: float = 0.0
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class BusinessExecutionEngine:
    """Main business execution orchestrator"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_dir = base_dir / "business" / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        config_path = base_dir / "config" / "engine.yaml"
        self.config = ConfigManager(config_path)
        self.db = DatabaseManager(Path(self.config.get("database.path")))
        
        self._init_database()
        logger.info("Business Execution Engine initialized")
    
    def _init_database(self):
        """Initialize business tables"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_reports (
                id TEXT PRIMARY KEY,
                report_date TEXT NOT NULL,
                products_generated INTEGER DEFAULT 0,
                products_published INTEGER DEFAULT 0,
                marketing_content_created INTEGER DEFAULT 0,
                leads_generated INTEGER DEFAULT 0,
                sales_count INTEGER DEFAULT 0,
                revenue_usd REAL DEFAULT 0.0,
                revenue_idr REAL DEFAULT 0.0,
                cogs_usd REAL DEFAULT 0.0,
                net_profit_usd REAL DEFAULT 0.0,
                net_profit_idr REAL DEFAULT 0.0,
                ceo_share_usd REAL DEFAULT 0.0,
                ceo_share_idr REAL DEFAULT 0.0,
                reinvestment_usd REAL DEFAULT 0.0,
                reinvestment_idr REAL DEFAULT 0.0,
                operational_usd REAL DEFAULT 0.0,
                operational_idr REAL DEFAULT 0.0,
                status TEXT DEFAULT 'pending',
                created_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS revenue_transactions (
                id TEXT PRIMARY KEY,
                report_id TEXT NOT NULL,
                product_id TEXT,
                marketplace_id TEXT,
                amount_usd REAL NOT NULL,
                amount_idr REAL NOT NULL,
                cogs_usd REAL DEFAULT 0.0,
                net_profit_usd REAL DEFAULT 0.0,
                net_profit_idr REAL DEFAULT 0.0,
                transaction_date TEXT NOT NULL,
                created_at TEXT
            )
        """)
        
        conn.commit()
        logger.info("Business tables initialized")
    
    def generate_daily_report(self, report_date: Optional[str] = None) -> DailyReport:
        """Generate daily business report"""
        if not report_date:
            report_date = datetime.now().strftime("%Y-%m-%d")
        
        report = DailyReport(report_date=report_date)
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Count products generated
            cursor.execute("""
                SELECT COUNT(*) FROM pf_generation_jobs 
                WHERE DATE(created_at) = ?
            """, (report_date,))
            row = cursor.fetchone()
            report.products_generated = row[0] if row else 0
            
            # Count products published
            cursor.execute("""
                SELECT COUNT(*) FROM pf_products 
                WHERE status = 'published' AND DATE(updated_at) = ?
            """, (report_date,))
            row = cursor.fetchone()
            report.products_published = row[0] if row else 0
            
            # Calculate revenue
            cursor.execute("""
                SELECT SUM(amount_usd), SUM(amount_idr), SUM(cogs_usd), SUM(net_profit_usd), SUM(net_profit_idr)
                FROM revenue_transactions 
                WHERE DATE(transaction_date) = ?
            """, (report_date,))
            row = cursor.fetchone()
            if row and row[0]:
                report.revenue_usd = float(row[0])
                report.revenue_idr = float(row[1])
                report.cogs_usd = float(row[2])
                report.net_profit_usd = float(row[3])
                report.net_profit_idr = float(row[4])
            
            # Calculate profit distribution
            report.ceo_share_usd = report.net_profit_usd * 0.8
            report.ceo_share_idr = report.net_profit_idr * 0.8
            report.reinvestment_usd = report.net_profit_usd * 0.25
            report.reinvestment_idr = report.net_profit_idr * 0.25
            report.operational_usd = report.net_profit_usd * 0.15
            report.operational_idr = report.net_profit_idr * 0.15
            
            report.status = "completed"
            
            # Save report
            report_id = f"RPT-{report_date}-{uuid.uuid4().hex[:8].upper()}"
            cursor.execute("""
                INSERT INTO daily_reports (
                    id, report_date, products_generated, products_published,
                    marketing_content_created, leads_generated, sales_count,
                    revenue_usd, revenue_idr, cogs_usd, net_profit_usd, net_profit_idr,
                    ceo_share_usd, ceo_share_idr, reinvestment_usd, reinvestment_idr,
                    operational_usd, operational_idr, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report_id, report.report_date, report.products_generated, report.products_published,
                report.marketing_content_created, report.leads_generated, report.sales_count,
                report.revenue_usd, report.revenue_idr, report.cogs_usd, report.net_profit_usd,
                report.net_profit_idr, report.ceo_share_usd, report.ceo_share_idr,
                report.reinvestment_usd, report.reinvestment_idr, report.operational_usd,
                report.operational_idr, report.status, report.created_at
            ))
            conn.commit()
            
            logger.info(f"Daily report generated: {report_date}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate daily report: {e}")
            report.status = "failed"
            return report
    
    def record_revenue(self, product_id: str, marketplace_id: str, amount_usd: float, amount_idr: float, cogs_usd: float = 0.0) -> bool:
        """Record revenue transaction"""
        try:
            net_profit_usd = amount_usd - cogs_usd
            net_profit_idr = amount_idr - (cogs_usd * 16000)
            
            transaction_id = f"REV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO revenue_transactions (
                    id, product_id, marketplace_id, amount_usd, amount_idr,
                    cogs_usd, net_profit_usd, net_profit_idr, transaction_date, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_id, product_id, marketplace_id, amount_usd, amount_idr,
                cogs_usd, net_profit_usd, net_profit_idr,
                datetime.now().isoformat(), datetime.now().isoformat()
            ))
            conn.commit()
            
            logger.info(f"Revenue recorded: {amount_usd} USD / {amount_idr} IDR")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record revenue: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get module status"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM daily_reports")
            total_reports = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM revenue_transactions")
            total_transactions = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(amount_usd), SUM(amount_idr) FROM revenue_transactions")
            row = cursor.fetchone()
            total_revenue_usd = float(row[0]) if row and row[0] else 0.0
            total_revenue_idr = float(row[1]) if row and row[1] else 0.0
            
            return {
                "module": "business",
                "status": "running",
                "total_reports": total_reports,
                "total_transactions": total_transactions,
                "total_revenue_usd": total_revenue_usd,
                "total_revenue_idr": total_revenue_idr
            }
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"module": "business", "status": "error", "error": str(e)}


def main():
    """Test business engine"""
    from pathlib import Path
    base_dir = Path(__file__).parent.parent.parent
    engine = BusinessExecutionEngine(base_dir)
    
    report = engine.generate_daily_report()
    print(f"Daily Report: {report.report_date}")
    print(f"  Products Generated: {report.products_generated}")
    print(f"  Revenue: ${report.revenue_usd:.2f} / Rp {report.revenue_idr:,.0f}")
    print(f"  CEO Share: ${report.ceo_share_usd:.2f} / Rp {report.ceo_share_idr:,.0f}")


if __name__ == "__main__":
    main()
