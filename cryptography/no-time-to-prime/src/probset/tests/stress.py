#!/usr/bin/env python3
"""Verify freshly generated instances."""
import argparse
import json
from pathlib import Path
import statistics
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "probset/generator"))
from generate import build, read_json
from verify import verify_instance

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.count < 1:
        parser.error("count must be positive")
    reports = []
    config = read_json(ROOT / "probset/generator/config.json")
    for i in range(args.count):
        with tempfile.TemporaryDirectory(prefix="nttp-test-") as work:
            root = Path(work)
            build(root / "challenge", root / "secrets", "COMPFEST18{stress_instance_only}", config)
            reports.append(verify_instance(root / "challenge", root / "secrets"))
        print(f"[{i+1}/{args.count}] PASS", flush=True)
    summary = {"status": "PASS", "instances": args.count, "retries": 0,
               "sage": reports[0]["sage"],
               "seconds": {m: {"median": statistics.median(r["seconds"][m] for r in reports),
                               "max": max(r["seconds"][m] for r in reports)} for m in reports[0]["seconds"]}}
    if args.report:
        args.report.write_text(json.dumps(summary,indent=2) + "\n")
    print(json.dumps(summary,indent=2))

if __name__ == "__main__":
    main()
