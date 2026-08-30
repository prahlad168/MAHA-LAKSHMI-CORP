#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Business Execution Core
Business reporting and revenue transaction persistence.

This module is intentionally kept separate from agent orchestration.
Agents should request business actions through a controlled action layer.
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

# Profit allocation policy. Must total 100%.
CEO_SHARE_RATE = 0.60
REINVESTMENT_RATE = 0.25
OPERATIONAL_RATE = 0.15


@dataclass
class DailyReport:
    """Daily business report."""
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
    """Business reporting and revenue persistence engine."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_dir = base_dir / "business" / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        config_path = base_dir / "config" / "engine.yaml"
        self.config = ConfigManager(config_path)
        self.db = DatabaseManager(Path(self.config.get("database.path")))
        self._init_database()
        logger.info("Business Execution Engine initialized")

    def _init_database(self):
        """Initialize business tables."""
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

        # report_id is retained for compatibility with the existing schema.
        # A revenue record is assigned to a deterministic daily bucket because
        # transactions can be recorded before the daily report is generated.
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

    @staticmethod
    def _allocate_profit(net_profit: float) -> Dict[str, float]:
        """Allocate net profit according to the 60/25/15 policy."""
        if net_profit < 0:
            raise ValueError("net_profit cannot be negative")

        allocations = {
            "ceo_share": net_profit * CEO_SHARE_RATE,
            "reinvestment": net_profit * REINVESTMENT_RATE,
            "operational": net_profit * OPERATIONAL_RATE,
        }
        # Keep the accounting invariant explicit.
        if abs(sum(allocations.values()) - net_profit) > 1e-9:
            raise RuntimeError("profit allocation policy does not total 100%")
        return allocations

    def generate_daily_report(self, report_date: Optional[str] = None) -> DailyReport:
        """Generate and persist a daily business report."""
        report_date = report_date or datetime.now().strftime("%Y-%m-%d")
        report = DailyReport(report_date=report_date)

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Optional product-factory tables may not exist in every deployment.
            for table, column in (("pf_generation_jobs", "created_at"), ("pf_products", "updated_at")):
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                exists = cursor.fetchone() is not None
                if not exists:
                    continue
                if table == "pf_generation_jobs":
                    cursor.execute("SELECT COUNT(*) FROM pf_generation_jobs WHERE DATE(created_at) = ?", (report_date,))
                    report.products_generated = cursor.fetchone()[0]
                else:
                    cursor.execute("SELECT COUNT(*) FROM pf_products WHERE status = 'published' AND DATE(updated_at) = ?", (report_date,))
                    report.products_published = cursor.fetchone()[0]

            cursor.execute("""
                SELECT
                    COUNT(*),
                    COALESCE(SUM(amount_usd), 0),
                    COALESCE(SUM(amount_idr), 0),
                    COALESCE(SUM(cogs_usd), 0),
                    COALESCE(SUM(net_profit_usd), 0),
                    COALESCE(SUM(net_profit_idr), 0)
                FROM revenue_transactions
                WHERE DATE(transaction_date) = ?
            """, (report_date,))
            row = cursor.fetchone()
            report.sales_count = int(row[0] or 0)
            report.revenue_usd = float(row[1] or 0)
            report.revenue_idr = float(row[2] or 0)
            report.cogs_usd = float(row[3] or 0)
            report.net_profit_usd = float(row[4] or 0)
            report.net_profit_idr = float(row[5] or 0)

            usd = self._allocate_profit(report.net_profit_usd)
            idr = self._allocate_profit(report.net_profit_idr)
            report.ceo_share_usd = usd["ceo_share"]
            report.reinvestment_usd = usd["reinvestment"]
            report.operational_usd = usd["operational"]
            report.ceo_share_idr = idr["ceo_share"]
            report.reinvestment_idr = idr["reinvestment"]
            report.operational_idr = idr["operational"]
            report.status = "completed"

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
            logger.info("Daily report generated: %s", report_date)
            return report

        except Exception as exc:
            logger.exception("Failed to generate daily report: %s", exc)
            report.status = "failed"
            return report

    def record_revenue(
        self,
        product_id: str,
        marketplace_id: str,
        amount_usd: float,
        amount_idr: float,
        cogs_usd: float = 0.0,
    ) -> bool:
        """Record a revenue transaction."""
        if amount_usd < 0 or amount_idr < 0 or cogs_usd < 0:
            raise ValueError("amounts and cogs must be non-negative")

        try:
            now = datetime.now()
            transaction_id = f"REV-{now.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
            # Daily bucket; the report itself can be generated later.
            report_id = f"DAY-{now.strftime('%Y-%m-%d')}"
            net_profit_usd = amount_usd - cogs_usd
            net_profit_idr = amount_idr - (cogs_usd * 16000)
            if net_profit_usd < 0 or net_profit_idr < 0:
                raise ValueError("COGS cannot exceed revenue")

            conn = self.db.get_connection()
            conn.execute("""
                INSERT INTO revenue_transactions (
                    id, report_id, product_id, marketplace_id, amount_usd, amount_idr,
                    cogs_usd, net_profit_usd, net_profit_idr, transaction_date, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_id, report_id, product_id, marketplace_id,
                amount_usd, amount_idr, cogs_usd, net_profit_usd, net_profit_idr,
                now.isoformat(), now.isoformat()
            ))
            conn.commit()
            logger.info("Revenue recorded: %s USD / %s IDR", amount_usd, amount_idr)
            return True

        except Exception as exc:
            logger.exception("Failed to record revenue: %s", exc)
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get module status."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM daily_reports")
            total_reports = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM revenue_transactions")
            total_transactions = cursor.fetchone()[0]
            cursor.execute("SELECT SUM(amount_usd), SUM(amount_idr) FROM revenue_transactions")
            row = cursor.fetchone()
            return {
                "module": "business",
                "status": "running",
                "total_reports": total_reports,
                "total_transactions": total_transactions,
                "total_revenue_usd": float(row[0] or 0) if row else 0.0,
                "total_revenue_idr": float(row[1] or 0) if row else 0.0,
                "profit_allocation": {
                    "ceo_share": CEO_SHARE_RATE,
                    "reinvestment": REINVESTMENT_RATE,
                    "operational": OPERATIONAL_RATE,
                },
            }
        except Exception as exc:
            logger.exception("Failed to get status: %s", exc)
            return {"module": "business", "status": "error", "error": str(exc)}
