from __future__ import annotations

import argparse
import json
import sys
import urllib.request


def check(url: str) -> int:
    request = urllib.request.Request(url, headers={"User-Agent": "MAHA-Smoke/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = response.read().decode("utf-8", errors="replace")
            if response.status != 200:
                print(f"FAIL status={response.status}")
                return 1
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                print("FAIL non-json response")
                return 1
            print(json.dumps({"status": response.status, "payload": data}, indent=2))
            return 0 if data.get("status") == "healthy" else 1
    except Exception as exc:
        print(f"FAIL {exc}")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="MAHA HTTP health smoke test")
    parser.add_argument("url", help="Absolute URL to /health")
    return check(parser.parse_args().url)


if __name__ == "__main__":
    raise SystemExit(main())
