import json
import uuid

from backend.db.connection import execute_query, init_db
from backend.products.worker import ProductGenerationWorker, utc_now


def test_product_worker_claims_job_and_creates_draft():
    init_db()
    user_id = f"worker-user-{uuid.uuid4().hex}"
    job_id = f"worker-job-{uuid.uuid4().hex}"
    now = utc_now()
    execute_query(
        "INSERT INTO users (id, email, password_hash, name, role, created_at, updated_at) VALUES (?, ?, 'hash', 'Worker Test', 'admin', ?, ?)",
        (user_id, f"{user_id}@example.test", now, now), fetch="none",
    )
    execute_query(
        "INSERT INTO product_generation_jobs (id, product_data, status, created_by, created_at, updated_at) VALUES (?, ?, 'queued', ?, ?, ?)",
        (job_id, json.dumps({"name": "Sprint 3 Guide", "description": "A real queued product.", "price": 19, "tags": ["guide"]}), user_id, now, now), fetch="none",
    )

    result = ProductGenerationWorker(worker_id=f"test-worker-{uuid.uuid4().hex}").process_next()

    assert result and result["status"] == "draft"
    job = execute_query("SELECT status, result FROM product_generation_jobs WHERE id = ?", (job_id,), fetch="one")
    product = execute_query("SELECT name, status, price FROM products WHERE id = ?", (result["product_id"],), fetch="one")
    assert job["status"] == "completed"
    assert json.loads(job["result"])["product_id"] == result["product_id"]
    assert product == {"name": "Sprint 3 Guide", "status": "draft", "price": 19.0}
