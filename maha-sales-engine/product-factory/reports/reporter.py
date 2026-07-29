#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Product Factory Reports
Generate reports about product factory operations.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import defaultdict

logger = logging.getLogger("maha-sales-engine.product-factory.reports")


class ProductFactoryReports:
    """Generate product factory reports"""
    
    def __init__(self, db_manager, output_dir: Path):
        self.db = db_manager
        self.output_dir = output_dir
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily product factory report"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Products created today
            cursor.execute("SELECT COUNT(*) FROM pf_products WHERE date(created_at) = ?", (today,))
            products_created = cursor.fetchone()[0]
            
            # Products by category
            cursor.execute("SELECT category, COUNT(*) FROM pf_products GROUP BY category")
            by_category = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Products by status
            cursor.execute("SELECT status, COUNT(*) FROM pf_products GROUP BY status")
            by_status = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Generation jobs today
            cursor.execute("SELECT COUNT(*) FROM pf_generation_jobs WHERE date(created_at) = ?", (today,))
            jobs_created = cursor.fetchone()[0]
            
            cursor.execute("SELECT status, COUNT(*) FROM pf_generation_jobs WHERE date(created_at) = ? GROUP BY status", (today,))
            jobs_by_status = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Success rate
            total_jobs = sum(jobs_by_status.values())
            success_rate = (jobs_by_status.get("completed", 0) / total_jobs * 100) if total_jobs > 0 else 0
            
            report = {
                "report_date": today,
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "products_created_today": products_created,
                    "total_products": sum(by_status.values()),
                    "jobs_created_today": jobs_created,
                    "jobs_completed_today": jobs_by_status.get("completed", 0),
                    "jobs_failed_today": jobs_by_status.get("failed", 0),
                    "success_rate": success_rate
                },
                "products_by_category": by_category,
                "products_by_status": by_status,
                "jobs_by_status": jobs_by_status,
                "top_categories": sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:5],
                "recommendations": self._generate_recommendations(by_status, jobs_by_status, success_rate)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate daily report: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, by_status: Dict, jobs_by_status: Dict, success_rate: float) -> List[str]:
        """Generate recommendations based on data"""
        recommendations = []
        
        if success_rate < 80:
            recommendations.append("Investigate failed generation jobs to improve success rate")
        
        if by_status.get("review", 0) > by_status.get("packaged", 0):
            recommendations.append("Review and approve pending products")
        
        if jobs_by_status.get("failed", 0) > 0:
            recommendations.append("Fix failed generation jobs")
        
        if not recommendations:
            recommendations.append("Continue current operations")
        
        return recommendations
    
    def get_factory_stats(self) -> Dict[str, Any]:
        """Get overall factory statistics"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Total products
            cursor.execute("SELECT COUNT(*) FROM pf_products")
            total_products = cursor.fetchone()[0]
            
            # Total versions
            cursor.execute("SELECT COUNT(*) FROM pf_product_versions")
            total_versions = cursor.fetchone()[0]
            
            # Total jobs
            cursor.execute("SELECT COUNT(*) FROM pf_generation_jobs")
            total_jobs = cursor.fetchone()[0]
            
            # Average quality score
            cursor.execute("SELECT AVG(overall_score) FROM pf_quality_reports")
            avg_quality = cursor.fetchone()[0] or 0.0
            
            return {
                "total_products": total_products,
                "total_versions": total_versions,
                "total_jobs": total_jobs,
                "average_quality_score": round(avg_quality, 2),
                "output_dir": str(self.output_dir)
            }
            
        except Exception as e:
            logger.error(f"Failed to get factory stats: {e}")
            return {}


def main():
    """Test reports"""
    from core.engine import ConfigManager, DatabaseManager
    from pathlib import Path
    
    config = ConfigManager(Path("config/engine.yaml"))
    db = DatabaseManager(Path(config.get("database.path")))
    
    output_dir = Path("product-factory/output")
    reports = ProductFactoryReports(db, output_dir)
    
    # Generate daily report
    report = reports.generate_daily_report()
    print(f"Daily Report: {json.dumps(report, indent=2)}")
    
    db.close()


if __name__ == "__main__":
    main()
