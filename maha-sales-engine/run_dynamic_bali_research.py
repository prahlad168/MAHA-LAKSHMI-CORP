from __future__ import annotations

import argparse
from pathlib import Path

from agent_runtime.real_research import run_bali_research


def main() -> None:
    parser = argparse.ArgumentParser(description="Run dynamic Bali business research through MAHA Agent Runtime")
    parser.add_argument("--limit", type=int, default=10, choices=range(1, 51), metavar="1-50")
    parser.add_argument("--db", type=Path, default=Path("db/maha_sales_engine.db"))
    args = parser.parse_args()

    task = run_bali_research(limit=args.limit, db_path=args.db)
    print(f"task_id={task.id}")
    print(f"status={task.status.value}")
    for item in task.result or []:
        print(f"{item['company']} | score={item['score']} | tier={item['tier']} | approval={item['approval_id']}")


if __name__ == "__main__":
    main()
