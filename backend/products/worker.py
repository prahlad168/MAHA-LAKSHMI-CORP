"""Durable, single-process worker for the product-generation queue.

The worker creates a real product draft from an approved generation request.
It intentionally does not pretend to call an LLM: an external provider can be
added behind this queue once credentials and the approved prompt policy exist.
"""

import json
import logging
import os
import socket
import uuid
import argparse
from datetime import datetime, timezone
from typing import Any, Optional

from backend.db.connection import get_connection

logger = logging.getLogger(__name__)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProductGenerationWorker:
    def __init__(self, worker_id: Optional[str] = None):
        self.worker_id = worker_id or f"product-worker-{socket.gethostname()}-{os.getpid()}"

    def register(self) -> None:
        now = utc_now()
        conn = get_connection()
        try:
            conn.execute(
                """INSERT INTO ai_workers (id, worker_id, type, status, last_heartbeat, tasks_processed, metadata, created_at)
                   VALUES (?, ?, 'product_generation', 'idle', ?, 0, '{}', ?)
                   ON CONFLICT(worker_id) DO UPDATE SET status = 'idle', last_heartbeat = excluded.last_heartbeat""",
                (f"worker-{uuid.uuid4().hex}", self.worker_id, now, now),
            )
            conn.commit()
        finally:
            conn.close()

    def process_next(self) -> Optional[dict[str, Any]]:
        """Atomically claim and process one queued job, returning its result."""
        self.register()
        conn = get_connection()
        job = None
        try:
            conn.execute("BEGIN IMMEDIATE")
            job = conn.execute(
                "SELECT * FROM product_generation_jobs WHERE status = 'queued' ORDER BY created_at ASC LIMIT 1"
            ).fetchone()
            if job is None:
                conn.commit()
                return None

            started_at = utc_now()
            claimed = conn.execute(
                """UPDATE product_generation_jobs
                   SET status = 'processing', worker_id = ?, started_at = ?, updated_at = ?, attempts = attempts + 1
                   WHERE id = ? AND status = 'queued'""",
                (self.worker_id, started_at, started_at, job["id"]),
            )
            if claimed.rowcount != 1:
                conn.rollback()
                return None
            conn.commit()
        finally:
            conn.close()

        try:
            product = self._build_product(json.loads(job["product_data"]))
            finished_at = utc_now()
            conn = get_connection()
            try:
                conn.execute("BEGIN")
                conn.execute(
                    """INSERT INTO products (id, name, description, price, currency, category, tags, status, content, created_by, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, 'draft', ?, ?, ?, ?)""",
                    (
                        product["id"], product["name"], product["description"], product["price"],
                        product["currency"], product["category"], json.dumps(product["tags"]),
                        product["content"], job["created_by"], finished_at, finished_at,
                    ),
                )
                result = {"product_id": product["id"], "status": "draft"}
                conn.execute(
                    """UPDATE product_generation_jobs SET status = 'completed', result = ?, error = NULL,
                       completed_at = ?, updated_at = ? WHERE id = ?""",
                    (json.dumps(result), finished_at, finished_at, job["id"]),
                )
                conn.execute(
                    """UPDATE ai_workers SET status = 'idle', last_heartbeat = ?, tasks_processed = tasks_processed + 1
                       WHERE worker_id = ?""",
                    (finished_at, self.worker_id),
                )
                conn.commit()
                return result
            finally:
                conn.close()
        except Exception as exc:
            logger.exception("Product generation failed for job %s", job["id"])
            self._mark_failed(job["id"], str(exc))
            raise

    def _mark_failed(self, job_id: str, error: str) -> None:
        now = utc_now()
        conn = get_connection()
        try:
            conn.execute(
                "UPDATE product_generation_jobs SET status = 'failed', error = ?, completed_at = ?, updated_at = ? WHERE id = ?",
                (error[:1000], now, now, job_id),
            )
            conn.execute("UPDATE ai_workers SET status = 'idle', last_heartbeat = ? WHERE worker_id = ?", (now, self.worker_id))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _build_product(data: dict[str, Any]) -> dict[str, Any]:
        name = str(data["name"]).strip()
        description = str(data["description"]).strip()
        if not name or not description:
            raise ValueError("name and description are required")
        return {
            "id": f"product-{uuid.uuid4().hex}", "name": name, "description": description,
            "price": float(data.get("price", 0)), "currency": data.get("currency", "USD"),
            "category": data.get("category"), "tags": data.get("tags", []),
            "content": data.get("content", description),
        }


def main() -> None:
    """Process one queued job; intended for a cron job or process supervisor."""
    parser = argparse.ArgumentParser(description="Process one MAHA product-generation job")
    parser.add_argument("--worker-id", help="Stable worker identifier for operational monitoring")
    args = parser.parse_args()
    result = ProductGenerationWorker(worker_id=args.worker_id).process_next()
    if result:
        logger.info("Generated product draft %s", result["product_id"])
    else:
        logger.info("No queued product-generation jobs")


if __name__ == "__main__":
    main()
