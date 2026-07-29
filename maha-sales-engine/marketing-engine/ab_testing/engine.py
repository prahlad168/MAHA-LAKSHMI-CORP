#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - A/B Testing
Marketing variant testing support.
"""

import os
import sys
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.marketing.ab_testing")


class VariantType(Enum):
    A = "variant_a"
    B = "variant_b"
    C = "variant_c"


class ABTestStatus(Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class ContentVariant:
    """Content variant"""
    variant_id: str
    test_id: str
    variant_type: str
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: str


@dataclass
class ABTest:
    """A/B test configuration"""
    test_id: str
    product_id: str
    content_type: str
    status: str
    variants: List[ContentVariant]
    metrics: Dict[str, Any]
    winner: Optional[str]
    created_at: str
    completed_at: Optional[str]


class ABTestingEngine:
    """Manage A/B testing for marketing content"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create_test(self, product_id: str, content_type: str, 
                    variants: List[Dict[str, Any]]) -> Optional[str]:
        """Create A/B test"""
        try:
            test_id = f"abtest-{uuid.uuid4().hex[:12]}"
            now = datetime.now().isoformat()
            
            variant_objects = []
            for i, variant_data in enumerate(variants):
                variant = ContentVariant(
                    variant_id=f"var-{test_id}-{i}",
                    test_id=test_id,
                    variant_type=VariantType(i).value if i < 3 else VariantType.A.value,
                    content=variant_data,
                    metadata={},
                    created_at=now
                )
                variant_objects.append(variant)
            
            test = ABTest(
                test_id=test_id,
                product_id=product_id,
                content_type=content_type,
                status=ABTestStatus.DRAFT.value,
                variants=variant_objects,
                metrics={},
                winner=None,
                created_at=now,
                completed_at=None
            )
            
            self._save_test(test)
            logger.info(f"A/B test created: {test_id}")
            return test_id
        except Exception as e:
            logger.error(f"Failed to create A/B test: {e}")
            return None
    
    def get_test(self, test_id: str) -> Optional[ABTest]:
        """Get A/B test"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ab_tests WHERE test_id = ?", (test_id,))
            row = cursor.fetchone()
            
            if row:
                return ABTest(
                    test_id=row["test_id"],
                    product_id=row["product_id"],
                    content_type=row["content_type"],
                    status=row["status"],
                    variants=json.loads(row.get("variants", "[]")),
                    metrics=json.loads(row.get("metrics", "{}")),
                    winner=row.get("winner"),
                    created_at=row["created_at"],
                    completed_at=row.get("completed_at")
                )
            return None
        except Exception as e:
            logger.error(f"Failed to get test: {e}")
            return None
    
    def _save_test(self, test: ABTest):
        """Save test to database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO ab_tests 
                (test_id, product_id, content_type, status, variants, metrics, winner, created_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test.test_id,
                test.product_id,
                test.content_type,
                test.status,
                json.dumps([asdict(v) for v in test.variants]),
                json.dumps(test.metrics),
                test.winner,
                test.created_at,
                test.completed_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save test: {e}")


def main():
    """Test A/B testing"""
    engine = ABTestingEngine(None)
    print("A/B Testing Engine initialized")


if __name__ == "__main__":
    main()
