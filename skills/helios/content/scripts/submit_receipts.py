#!/usr/bin/env python3
"""Submit staged receipts to Helios non-interactively."""

import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

HELIOS_URL = "https://console.huilianyi.com/"
SESSION_DIR = "~/.helios/session"
STAGING_DIR = Path.home() / "helios-staging"

sys.path.insert(0, SCRIPT_DIR)


def emit(obj):
    print(json.dumps(obj), flush=True)


def main():
    parser = argparse.ArgumentParser(description="Submit staged receipts to Helios.")
    parser.add_argument("--claim", type=int, required=True, help="1-based claim index from get_claims.py")
    parser.add_argument("--reasons", default="{}", help='JSON dict mapping filename -> reason string')
    parser.add_argument("--staging-dir", help="Override staging directory path")
    parser.add_argument("--session-dir", help="Override session directory path")
    parser.add_argument("--dry-run", action="store_true", help="Parse and list receipts without submitting")
    args = parser.parse_args()

    staging = Path(args.staging_dir).expanduser() if args.staging_dir else STAGING_DIR
    session_dir = args.session_dir or SESSION_DIR

    try:
        reasons = json.loads(args.reasons)
    except json.JSONDecodeError as e:
        emit({"event": "done", "succeeded": 0, "failed": 0, "total": 0, "errors": [f"Invalid --reasons JSON: {e}"]})
        sys.exit(1)

    try:
        from helios_bot import (
            load_receipts, flow_standard, flow_over_cap,
            recover_to_expense_list, dismiss_modals,
            load_progress, save_progress, clear_progress,
            DELAY_SHORT, DELAY_MEDIUM, DELAY_LONG,
        )
    except ImportError as e:
        emit({"event": "done", "succeeded": 0, "failed": 0, "total": 0, "errors": [f"helios_bot import error: {e}"]})
        sys.exit(1)

    receipts = load_receipts(str(staging))
    total = len(receipts)

    if args.dry_run:
        for i, r in enumerate(receipts, 1):
            emit({"event": "progress", "index": i, "total": total, "filename": r.filename, "status": "dry-run"})
        emit({"event": "done", "succeeded": 0, "failed": 0, "total": total, "errors": []})
        return

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        emit({"event": "done", "succeeded": 0, "failed": 0, "total": total, "errors": [f"playwright not installed: {e}"]})
        sys.exit(1)

    submitted = load_progress()
    errors_list = []
    succeeded = 0
    failed = 0

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=os.path.expanduser(session_dir),
            headless=False,
            viewport={"width": 1280, "height": 900},
        )
        page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto(HELIOS_URL)

            try:
                page.wait_for_load_state("networkidle", timeout=30000)
            except Exception:
                pass

            if "login" in page.url.lower() or "signin" in page.url.lower():
                context.close()
                emit({"event": "done", "succeeded": 0, "failed": 0, "total": total, "errors": ["auth_required"]})
                sys.exit(1)

            # Navigate to Expense Claim
            page.wait_for_timeout(5000)
            page.locator("span.text-ellipsis", has_text="Expense Claim").click()
            page.wait_for_timeout(DELAY_LONG)

            # Wait for table
            table_body = page.locator(".ant-table-body .ant-table-tbody")
            table_body.wait_for(state="visible", timeout=15000)
            page.wait_for_timeout(1000)

            rows = table_body.locator("tr.ant-table-row")
            row_count = rows.count()

            if args.claim < 1 or args.claim > row_count:
                context.close()
                emit({"event": "done", "succeeded": 0, "failed": 0, "total": total,
                      "errors": [f"Claim index {args.claim} out of range (1-{row_count})"]})
                sys.exit(1)

            # Click into the selected claim (0-based indexing)
            row = rows.nth(args.claim - 1)
            row.locator("td").nth(6).click()
            page.wait_for_timeout(DELAY_LONG)

            # Wait for expense report to load
            page.get_by_role("button", name="Add Expense").wait_for(state="visible", timeout=15000)

            # Process receipts — standard batch first, then over-cap
            batch = [r for r in receipts if not r.is_over_cap] + [r for r in receipts if r.is_over_cap]

            for i, receipt in enumerate(batch, 1):
                if receipt.filename in submitted:
                    succeeded += 1
                    emit({"event": "progress", "index": i, "total": total,
                          "filename": receipt.filename, "status": "skipped"})
                    continue

                dismiss_modals(page)
                reason = reasons.get(receipt.filename, "")

                success = False
                for attempt in range(2):
                    try:
                        if receipt.is_over_cap:
                            flow_over_cap(page, receipt, reason)
                        else:
                            flow_standard(page, receipt)
                        success = True
                        submitted.add(receipt.filename)
                        save_progress(submitted)
                        break
                    except Exception as e:
                        if attempt == 0:
                            recover_to_expense_list(page)
                        else:
                            errors_list.append(f"{receipt.filename}: {e}")

                if success:
                    succeeded += 1
                    emit({"event": "progress", "index": i, "total": total,
                          "filename": receipt.filename, "status": "ok"})
                else:
                    failed += 1
                    emit({"event": "progress", "index": i, "total": total,
                          "filename": receipt.filename, "status": "failed"})
                    recover_to_expense_list(page)

        finally:
            try:
                context.close()
            except Exception:
                pass

    # Clear staging for successfully submitted receipts
    if not args.dry_run:
        for f in staging.iterdir():
            if f.suffix.lower() in {".jpg", ".jpeg", ".png"} and f.name in submitted:
                try:
                    f.unlink()
                except Exception:
                    pass
        if failed == 0:
            clear_progress()

    emit({"event": "done", "succeeded": succeeded, "failed": failed,
          "total": total, "errors": errors_list})


if __name__ == "__main__":
    main()
