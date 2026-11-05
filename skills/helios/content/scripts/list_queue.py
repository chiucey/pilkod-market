#!/usr/bin/env python3
"""List all staged receipts in the Helios staging folder."""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

STAGING_DIR = Path.home() / "helios-staging"
EXPENSE_CAP_DEFAULT = 115.00


def parse_filename_basic(filepath: str, expense_cap: float = EXPENSE_CAP_DEFAULT):
    """Fallback filename parser when helios_bot is unavailable."""
    filename = Path(filepath).stem
    pattern = r"^.+_Expense_([A-Za-z]+)_(\d{1,2})_(\d{4})_([\d.]+)$"
    match = re.match(pattern, filename)
    if not match:
        return None
    month_str, day_str, year_str, amount_str = match.groups()
    try:
        date = datetime.strptime(f"{month_str} {day_str} {year_str}", "%b %d %Y")
        amount = float(amount_str)
        return {
            "filename": Path(filepath).name,
            "amount": amount,
            "date": date.strftime("%b %d %Y"),
            "date_obj": date,
            "over_cap": amount > expense_cap,
            "path": filepath,
        }
    except ValueError:
        return None


def main():
    parser = argparse.ArgumentParser(description="List staged receipts.")
    parser.add_argument("--staging-dir", help="Override staging directory path")
    args = parser.parse_args()

    staging = Path(args.staging_dir).expanduser() if args.staging_dir else STAGING_DIR

    # Try to import parse_filename from helios_bot (co-located in scripts/)
    parse_fn = None
    expense_cap = EXPENSE_CAP_DEFAULT
    try:
        sys.path.insert(0, SCRIPT_DIR)
        from helios_bot import parse_filename, EXPENSE_CAP
        parse_fn = parse_filename
        expense_cap = EXPENSE_CAP
    except ImportError:
        pass

    if not staging.is_dir():
        print(json.dumps({
            "receipts": [], "total": 0.0, "count": 0,
            "over_cap_count": 0, "staging_dir": str(staging),
        }))
        return

    receipts_out = []
    for f in sorted(staging.iterdir()):
        if f.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue

        if parse_fn:
            r = parse_fn(str(f))
            if r:
                receipts_out.append({
                    "filename": r.filename,
                    "amount": r.amount,
                    "date": r.date_display,
                    "over_cap": r.is_over_cap,
                    "path": str(f),
                })
        else:
            info = parse_filename_basic(str(f), expense_cap)
            if info:
                receipts_out.append({
                    "filename": info["filename"],
                    "amount": info["amount"],
                    "date": info["date"],
                    "over_cap": info["over_cap"],
                    "path": info["path"],
                })

    receipts_out.sort(key=lambda r: r["date"])

    total = sum(r["amount"] for r in receipts_out)
    over_cap_count = sum(1 for r in receipts_out if r["over_cap"])

    print(json.dumps({
        "receipts": receipts_out,
        "total": round(total, 2),
        "count": len(receipts_out),
        "over_cap_count": over_cap_count,
        "staging_dir": str(staging),
    }))


if __name__ == "__main__":
    main()
