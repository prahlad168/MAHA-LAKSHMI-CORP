#!/usr/bin/env python3
"""Run the first real Bali research -> qualification -> CRM -> sales approval flow."""

from pathlib import Path

from agent_runtime.real_research import run_bali_research


if __name__ == "__main__":
    task = run_bali_research(limit=10, db_path=Path("db/maha_sales_engine.db"))
    print(f"Task: {task.id}")
    print(f"Status: {task.status.value}")
    print(f"Approvals created: {len(task.result or [])}")
    for item in task.result or []:
        print(f"- {item['company']} | score={item['score']} | tier={item['tier']} | approval={item['approval_id']}")
