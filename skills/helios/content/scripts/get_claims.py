#!/usr/bin/env python3
"""Scrape expense claim list from Helios and output JSON."""

import argparse
import json
import os
import sys

HELIOS_URL = "https://console.huilianyi.com/"
SESSION_DIR = "~/.helios/session"
DELAY_LONG = 3000


def main():
    parser = argparse.ArgumentParser(description="List Helios expense claims.")
    parser.add_argument("--timeout", type=int, default=30, help="Dashboard load timeout in seconds")
    parser.add_argument("--session-dir", help="Override session directory path")
    args = parser.parse_args()

    session_dir = args.session_dir or SESSION_DIR

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(json.dumps({"ok": False, "error": "playwright not installed"}))
        sys.exit(1)

    try:
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
                    page.wait_for_load_state("networkidle", timeout=args.timeout * 1000)
                except Exception:
                    pass

                # Check for login page
                if "login" in page.url.lower() or "signin" in page.url.lower():
                    context.close()
                    print(json.dumps({"ok": False, "error": "auth_required"}))
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

                claims = []
                for i in range(row_count):
                    row = rows.nth(i)
                    cells = row.locator("td")
                    try:
                        row_num = cells.nth(2).inner_text(timeout=2000).strip()
                        reason = cells.nth(6).locator("span.popover-wrap span").inner_text(timeout=2000).strip()
                        if reason:
                            claims.append({"index": i + 1, "num": row_num, "reason": reason})
                    except Exception:
                        continue

                context.close()
                print(json.dumps({"ok": True, "claims": claims}))

            except Exception as e:
                try:
                    context.close()
                except Exception:
                    pass
                raise e

    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
