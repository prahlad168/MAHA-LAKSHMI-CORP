from __future__ import annotations

import argparse
from pathlib import Path

from research.recheck import ResearchRecheckAgent


def main() -> int:
    parser = argparse.ArgumentParser(description="Recheck stale/incomplete MAHA CRM research")
    parser.add_argument("--db", type=Path, default=Path("db/maha_sales_engine.db"))
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    agent = ResearchRecheckAgent(args.db)
    results = agent.recheck_required(limit=args.limit)
    print(f"rechecked={len(results)}")
    for result in results:
        print(
            result["lead_id"],
            result["status"],
            result.get("maha_hot_score", "-"),
            result.get("evidence_added", 0),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
