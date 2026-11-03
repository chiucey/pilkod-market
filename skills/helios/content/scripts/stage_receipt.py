#!/usr/bin/env python3
"""Stage a receipt image to the receipts staging folder with proper naming."""

import argparse
import json
import shutil
import sys
from pathlib import Path

STAGING_DIR = Path.home() / "Desktop" / "receipts_staging" / "renamed"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    i = 2
    while True:
        candidate = path.with_name(f"{path.stem}_{i}{path.suffix}")
        if not candidate.exists():
            return candidate
        i += 1


def main():
    parser = argparse.ArgumentParser(description="Stage a receipt to the Helios staging folder.")
    parser.add_argument("--image", required=True, help="Path to source image")
    parser.add_argument("--project", required=True, help="Project code (e.g. PJ_Q)")
    parser.add_argument("--month", help="Month abbreviation (Jan, Feb, ...)")
    parser.add_argument("--day", help="Day number")
    parser.add_argument("--year", help="Four-digit year")
    parser.add_argument("--amount", help="Amount (e.g. 68.00)")
    parser.add_argument("--unknown", action="store_true", help="Mark as unknown date/amount")
    args = parser.parse_args()

    try:
        src = Path(args.image).expanduser().resolve()
        if not src.exists():
            print(json.dumps({"ok": False, "error": f"Image not found: {src}"}))
            sys.exit(1)

        STAGING_DIR.mkdir(parents=True, exist_ok=True)

        if args.unknown:
            filename = f"{args.project}_Expense_UNKNOWN_DATE_UNKNOWN.jpg"
        else:
            missing = [f for f, v in [("--month", args.month), ("--day", args.day),
                                       ("--year", args.year), ("--amount", args.amount)] if not v]
            if missing:
                print(json.dumps({"ok": False, "error": f"Missing required args: {', '.join(missing)} (or use --unknown)"}))
                sys.exit(1)
            filename = f"{args.project}_Expense_{args.month}_{args.day}_{args.year}_{args.amount}.jpg"

        dest = unique_path(STAGING_DIR / filename)
        shutil.copy2(str(src), str(dest))
        print(json.dumps({"ok": True, "staged_path": str(dest), "filename": dest.name}))

    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
