#!/usr/bin/env python3
"""
Helios Expense Automation Bot
==============================
Parses receipt filenames for date/amount, connects to an already-authenticated
Helios browser session, and submits expenses automatically.

Two flows:
  - Flow A: receipts <= expense cap (standard submission)
  - Flow B: receipts >  expense cap (COS Meal procedure)

Usage:
    # Step 1: Launch browser, log in, navigate to the expense report
    python scripts/helios_bot.py --login

    # Dry run — parse files only, don't touch Helios
    python scripts/helios_bot.py --run --receipts ~/helios-staging --dry-run

Requirements:
    pip install playwright
    playwright install chromium

Configuration:
    Edit ~/.helios/config.json (created by setup.sh)
"""

import os
import re
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

from playwright.sync_api import sync_playwright, Page

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("helios")


# ── Config ───────────────────────────────────────────────────
def load_config() -> dict:
    """Load ~/.helios/config.json, return empty dict if missing or invalid."""
    config_path = Path.home() / ".helios" / "config.json"
    try:
        with open(config_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


_CONFIG = load_config()

HELIOS_URL = _CONFIG.get("helios_url", "https://console.huilianyi.com/")
EXPENSE_CAP = _CONFIG.get("expense_cap", 115.00)
RECEIPT_FOLDER = _CONFIG.get("staging_dir", "~/helios-staging")

# Month name lookup for the date picker grid
MONTH_ABBR = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}

# Delays (milliseconds) — increase these if Helios is slow
DELAY_SHORT = 1000
DELAY_MEDIUM = 2000
DELAY_LONG = 3000


# ── Data Model ───────────────────────────────────────────────
@dataclass
class Receipt:
    filepath: str
    filename: str
    date: datetime
    amount: float

    @property
    def is_over_cap(self) -> bool:
        return self.amount > EXPENSE_CAP

    @property
    def date_str(self) -> str:
        return self.date.strftime("%Y-%m-%d")

    @property
    def date_display(self) -> str:
        return self.date.strftime("%b %d, %Y")

    @property
    def day(self) -> int:
        return self.date.day

    @property
    def month(self) -> int:
        return self.date.month

    @property
    def year(self) -> int:
        return self.date.year

    @property
    def amount_str(self) -> str:
        if self.amount == int(self.amount):
            return str(int(self.amount))
        return f"{self.amount:.2f}"


# ── Filename Parser ──────────────────────────────────────────
def parse_filename(filepath: str) -> Receipt | None:
    """
    Parse: {ProjectCode}_Expense_{Month}_{Day}_{Year}_{Amount}.jpg
    Example: PROJ_Expense_Aug_19_2025_68.00.jpg
    """
    filename = Path(filepath).stem
    pattern = r"^.+_Expense_([A-Za-z]+)_(\d{1,2})_(\d{4})_([\d.]+)$"
    match = re.match(pattern, filename)

    if not match:
        log.warning(f"Skipping — doesn't match format: {filename}")
        return None

    month_str, day_str, year_str, amount_str = match.groups()

    try:
        date = datetime.strptime(f"{month_str} {day_str} {year_str}", "%b %d %Y")
        amount = float(amount_str)
    except (ValueError, TypeError) as e:
        log.warning(f"Skipping — parse error in {filename}: {e}")
        return None

    return Receipt(
        filepath=filepath,
        filename=Path(filepath).name,
        date=date,
        amount=amount,
    )


def load_receipts(folder: str) -> list[Receipt]:
    """Load and parse all receipt images, sorted by date."""
    folder = os.path.expanduser(folder)
    if not os.path.isdir(folder):
        log.error(f"Folder not found: {folder}")
        sys.exit(1)

    receipts = []
    for f in sorted(Path(folder).iterdir()):
        if f.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            r = parse_filename(str(f))
            if r:
                receipts.append(r)

    receipts.sort(key=lambda r: r.date)

    standard = sum(1 for r in receipts if not r.is_over_cap)
    over_cap = sum(1 for r in receipts if r.is_over_cap)
    log.info(f"Loaded {len(receipts)} receipts ({standard} standard, {over_cap} over-cap)")
    return receipts


# ── Date Picker Navigation ───────────────────────────────────
def navigate_date_picker(page: Page, target_year: int, target_month: int, target_day: int):
    """
    Helios uses Ant Design date picker. Scopes all actions to the
    currently visible calendar panel. Handles years outside the
    visible decade by clicking prev/next decade arrows.
    """
    month_name = MONTH_ABBR[target_month]

    # Scope to the visible calendar popup
    picker = page.locator(".ant-calendar-panel:visible").first
    picker.wait_for(state="visible", timeout=5000)

    # Step 1: Select year
    picker.locator("a.ant-calendar-year-select").click()
    page.wait_for_timeout(500)

    # Navigate decades if target year isn't visible
    for _ in range(5):  # Max 5 decade jumps
        year_cell = picker.locator("a.ant-calendar-year-panel-year", has_text=str(target_year))
        if year_cell.count() > 0:
            break
        try:
            header_text = picker.locator(".ant-calendar-year-panel-decade-select").inner_text(timeout=1000)
            start_year = int(header_text.split("-")[0])
            if target_year < start_year:
                picker.locator("a.ant-calendar-year-panel-prev-decade-btn").click()
            else:
                picker.locator("a.ant-calendar-year-panel-next-decade-btn").click()
        except Exception:
            picker.locator("a.ant-calendar-year-panel-prev-decade-btn").click()
        page.wait_for_timeout(500)

    picker.locator("a.ant-calendar-year-panel-year", has_text=str(target_year)).click()
    page.wait_for_timeout(500)

    # Step 2: Select month
    picker.locator("a.ant-calendar-month-select").click()
    page.wait_for_timeout(500)
    picker.locator("a.ant-calendar-month-panel-month", has_text=month_name).click()
    page.wait_for_timeout(500)

    # Step 3: Select day — only current month cells
    picker.locator("td.ant-calendar-cell:not(.ant-calendar-last-month-cell):not(.ant-calendar-next-month-btn-day)").get_by_text(str(target_day), exact=True).click()
    page.wait_for_timeout(DELAY_SHORT)

    log.info(f"    Date → {target_year}-{target_month:02d}-{target_day:02d}")


# ── Modal Cleanup ────────────────────────────────────────────
def dismiss_modals(page: Page):
    """
    Dismiss any blocking modals/dialogs that might be open.
    Call this before starting each receipt to ensure a clean state.
    """
    for attempt in range(10):
        try:
            ok_btn = page.locator(
                ".ant-modal-confirm .ant-btn-primary, "
                ".ant-modal-content .ant-btn-primary, "
                ".expense-check-result .ant-btn-primary, "
                ".ant-modal-confirm .ant-btn-primary"
            ).first
            if ok_btn.is_visible(timeout=1000):
                ok_btn.click()
                log.info(f"    Dismissed modal (attempt {attempt + 1})")
                page.wait_for_timeout(DELAY_SHORT)
            else:
                break
        except Exception:
            break

    try:
        close_btn = page.locator(".ant-modal-close").first
        if close_btn.is_visible(timeout=500):
            close_btn.click()
            page.wait_for_timeout(DELAY_SHORT)
    except Exception:
        pass

    try:
        page.locator(".ant-modal-wrap").wait_for(state="hidden", timeout=5000)
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════
#  FLOW A: Standard submission (amount <= expense cap)
# ══════════════════════════════════════════════════════════════
def flow_standard(page: Page, receipt: Receipt):
    """
    Submit a receipt within the expense cap.
    Assumes you're inside the expense report, seeing "Add Expense".
    """
    log.info(f"  Flow A: {receipt.filename} — HKD ${receipt.amount:.2f}, {receipt.date_display}")

    # 1. Wait for page to be ready, then Add Expense → Working Meal
    page.get_by_role("button", name="Add Expense").wait_for(state="visible", timeout=15000)
    page.wait_for_timeout(DELAY_MEDIUM)
    page.get_by_role("button", name="Add Expense").click()
    page.wait_for_timeout(DELAY_LONG)

    working_meal = page.locator(".expense-type-card-name", has_text="Working Meal").first
    try:
        working_meal.wait_for(state="visible", timeout=5000)
    except Exception:
        log.info("    Retrying Add Expense click...")
        page.get_by_role("button", name="Add Expense").click()
        page.wait_for_timeout(DELAY_LONG)
        working_meal.wait_for(state="visible", timeout=10000)

    working_meal.click()
    page.wait_for_timeout(DELAY_SHORT)

    # 2. Add invoice
    page.locator(".new-invoice .default-add-button").click()
    page.wait_for_timeout(DELAY_SHORT)

    page.get_by_role("tab", name="Non-Mainland China").wait_for(state="visible", timeout=10000)
    page.get_by_role("tab", name="Non-Mainland China").click()
    page.wait_for_timeout(DELAY_SHORT)

    page.get_by_text("Manually Add Invoice Info").click()
    page.wait_for_timeout(DELAY_SHORT)

    page.get_by_text("International Receipts").click()
    page.wait_for_timeout(DELAY_SHORT)

    # 3. Upload receipt image
    page.locator("input[type='file'][accept*='.jpg,.heic,.png,.jpeg,.pdf,.ofd']").set_input_files(receipt.filepath)
    page.wait_for_timeout(DELAY_MEDIUM)

    # 4. Set date
    page.get_by_role("textbox", name="Select").click()
    page.wait_for_timeout(DELAY_SHORT)
    navigate_date_picker(page, receipt.year, receipt.month, receipt.day)

    # 5. Fill amount
    amount_field = page.get_by_role("spinbutton", name="Amount (tax included) *")
    amount_field.click()
    amount_field.fill(receipt.amount_str)
    page.wait_for_timeout(500)

    # 6. Confirm invoice
    page.get_by_role("button", name="OK").click()
    page.wait_for_timeout(DELAY_MEDIUM)

    # 7. Set Date of Expense on main form
    page.locator("#createdDate > div > .anticon > svg").click()
    page.wait_for_timeout(DELAY_SHORT)
    navigate_date_picker(page, receipt.year, receipt.month, receipt.day)

    # 8. Location → Hong Kong
    page.locator(".travel-location > .fake-input").click()
    page.wait_for_timeout(DELAY_SHORT)
    page.get_by_text("C", exact=True).nth(1).click()
    page.wait_for_timeout(500)
    page.locator("div").filter(has_text=re.compile(r"^China$")).first.click()
    page.wait_for_timeout(500)
    page.get_by_text("Hong KongNext Level").click()
    page.wait_for_timeout(DELAY_SHORT)

    # 9. Dining companion
    page.get_by_text("用餐人不包含自己").click()
    page.wait_for_timeout(500)
    page.locator(".value-list-item > .name").first.click()
    page.wait_for_timeout(500)
    page.get_by_role("button", name="OK").click()
    page.wait_for_timeout(DELAY_SHORT)

    # 10. Save
    page.get_by_role("button", name="Save").click()
    page.wait_for_timeout(DELAY_LONG * 2)

    log.info(f"  ✓ Saved: {receipt.filename}")


# ══════════════════════════════════════════════════════════════
#  FLOW B: Over-cap submission (amount > expense cap)
# ══════════════════════════════════════════════════════════════
def flow_over_cap(page: Page, receipt: Receipt, reason: str = ""):
    """
    Submit a receipt that exceeds the expense cap (COS Meal flow).
    Non-GC dinner attendees are read from ~/.helios/config.json
    under the key "non_gc_dinner_attendees".
    """
    log.info(f"  Flow B (over-cap): {receipt.filename} — HKD ${receipt.amount:.2f}, {receipt.date_display}")

    if not reason:
        log.warning(f"  ⏭ SKIPPED: No reason provided for over-cap receipt")
        return

    # 1. Wait for page, then Add Expense → COS Meal
    page.get_by_role("button", name="Add Expense").wait_for(state="visible", timeout=15000)
    page.wait_for_timeout(DELAY_MEDIUM)
    page.get_by_role("button", name="Add Expense").click()
    page.wait_for_timeout(DELAY_LONG)

    cos_meal = page.locator(".expense-type-card-name", has_text="COS Meal").first
    try:
        cos_meal.wait_for(state="visible", timeout=5000)
    except Exception:
        log.info("    Retrying Add Expense click...")
        page.get_by_role("button", name="Add Expense").click()
        page.wait_for_timeout(DELAY_LONG)
        cos_meal.wait_for(state="visible", timeout=10000)

    cos_meal.scroll_into_view_if_needed()
    cos_meal.click()
    page.wait_for_timeout(DELAY_SHORT)

    # 2. Add invoice
    page.locator(".new-invoice .default-add-button").click()
    page.wait_for_timeout(DELAY_SHORT)

    page.get_by_role("tab", name="Non-Mainland China").wait_for(state="visible", timeout=10000)
    page.get_by_role("tab", name="Non-Mainland China").click()
    page.wait_for_timeout(DELAY_SHORT)

    page.get_by_text("Manually Add Invoice Info").click()
    page.wait_for_timeout(DELAY_SHORT)

    page.get_by_text("International Receipts").click()
    page.wait_for_timeout(DELAY_SHORT)

    # 3. Upload receipt image
    page.locator("input[type='file'][accept*='.jpg,.heic,.png,.jpeg,.pdf,.ofd']").set_input_files(receipt.filepath)
    page.wait_for_timeout(DELAY_MEDIUM)

    # 4. Set invoice date
    page.get_by_role("textbox", name="Select").click()
    page.wait_for_timeout(DELAY_SHORT)
    navigate_date_picker(page, receipt.year, receipt.month, receipt.day)

    # 5. Fill amount
    amount_field = page.get_by_role("spinbutton", name="Amount (tax included) *")
    amount_field.click()
    amount_field.fill(receipt.amount_str)
    page.wait_for_timeout(500)

    # 6. Confirm invoice
    page.get_by_role("button", name="OK").click()
    page.wait_for_timeout(DELAY_MEDIUM)

    # 7. Set Date of Expense on main form
    date_icon = page.locator("#createdDate > div > .anticon > svg")
    date_icon.scroll_into_view_if_needed()
    date_icon.wait_for(state="visible", timeout=10000)
    date_icon.click()
    page.wait_for_timeout(DELAY_SHORT)
    navigate_date_picker(page, receipt.year, receipt.month, receipt.day)

    # 8. Location → Hong Kong
    page.locator(".travel-location > .fake-input").click()
    page.wait_for_timeout(DELAY_SHORT)
    page.get_by_text("C", exact=True).nth(1).click()
    page.wait_for_timeout(500)
    page.locator("div").filter(has_text=re.compile(r"^China$")).first.click()
    page.wait_for_timeout(500)
    page.get_by_text("Hong KongNext Level").click()
    page.wait_for_timeout(DELAY_SHORT)

    # 9. GC Dinners — select from list
    page.locator("section:nth-child(5) > .ant-row > .ant-col.ant-form-item-control-wrapper > .ant-form-item-control > .ant-form-item-children > .super-person-selector-bs > .chooser > span > .ant-select > .ant-select-selection > .ant-select-selection__rendered > .ant-select-selection__placeholder").click()
    page.wait_for_timeout(DELAY_SHORT)
    page.locator(".value-list-item > .name").first.click()
    page.wait_for_timeout(500)
    page.get_by_role("button", name="OK").first.click()
    page.wait_for_timeout(DELAY_SHORT)

    # 10. Non-GC Dinners — tick checkboxes from config
    page.locator(".vendor-selector-wrapper > .chooser > span > .ant-select > .ant-select-selection > .ant-select-selection__rendered > .ant-select-selection__placeholder").click()
    page.wait_for_timeout(DELAY_MEDIUM)

    modal_table = page.locator(".ant-modal-body .ant-table-tbody")
    attendees = _CONFIG.get("non_gc_dinner_attendees", [])
    if not attendees:
        log.info("    Skipping Non-GC Dinners — none configured in ~/.helios/config.json")
    else:
        for name in attendees:
            modal_table.locator("tr", has_text=name).first.locator(".ant-checkbox-input").click()
            page.wait_for_timeout(500)

    page.locator(".ant-modal-content .ant-btn-primary", has_text="OK").click()
    page.wait_for_timeout(DELAY_SHORT)

    # 11. Upload same receipt again as Attachment
    try:
        attachment_input = page.locator("input[type='file'][accept*='.zip']").last
        attachment_input.set_input_files(receipt.filepath)
        page.wait_for_timeout(DELAY_MEDIUM)
        log.info("    Attachment uploaded")
    except Exception as e:
        log.warning(f"    Attachment upload failed: {e}")

    # 12. Fill Reason field
    try:
        reason_field = page.get_by_role("textbox", name="Please add names of BCG")
        reason_field.scroll_into_view_if_needed()
        reason_field.wait_for(state="visible", timeout=5000)
        reason_field.click()
        reason_field.fill(reason)
        page.wait_for_timeout(500)
    except Exception:
        try:
            reason_field = page.get_by_role("textbox", name="Enter at most 500 characters")
            reason_field.wait_for(state="visible", timeout=3000)
            reason_field.click()
            reason_field.fill(reason)
            page.wait_for_timeout(500)
        except Exception as e:
            log.warning(f"    Could not fill Reason field: {e}")

    # 13. Save
    page.get_by_role("button", name="Save").click()
    page.wait_for_timeout(DELAY_MEDIUM)

    # 14. Dismiss all post-save dialogs
    dismiss_modals(page)
    page.wait_for_timeout(DELAY_LONG)

    log.info(f"  ✓ Saved: {receipt.filename}")


# ── Progress Tracking ────────────────────────────────────────
PROGRESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "progress.json")


def load_progress() -> set:
    """Load set of already-submitted filenames from progress file."""
    try:
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
            return set(data.get("submitted", []))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_progress(submitted: set):
    """Save submitted filenames to progress file."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"submitted": sorted(submitted), "last_updated": datetime.now().isoformat()}, f, indent=2)


def clear_progress():
    """Delete progress file to start fresh."""
    try:
        os.remove(PROGRESS_FILE)
    except FileNotFoundError:
        pass


# ── Auto-Recovery ────────────────────────────────────────────
def recover_to_expense_list(page: Page):
    """
    Recover from a broken state back to the expense report view
    where 'Add Expense' is visible.
    """
    log.info("    Attempting auto-recovery...")

    dismiss_modals(page)
    page.wait_for_timeout(DELAY_SHORT)

    try:
        cancel_btn = page.get_by_role("button", name="Cancel")
        if cancel_btn.is_visible(timeout=2000):
            cancel_btn.click()
            page.wait_for_timeout(DELAY_MEDIUM)
            dismiss_modals(page)
    except Exception:
        pass

    try:
        close_btn = page.locator(".ant-drawer-close, .slide-frame-close").first
        if close_btn.is_visible(timeout=1000):
            close_btn.click()
            page.wait_for_timeout(DELAY_MEDIUM)
    except Exception:
        pass

    try:
        page.get_by_role("button", name="Add Expense").wait_for(state="visible", timeout=5000)
        log.info("    ✓ Recovered — Add Expense is visible")
        return True
    except Exception:
        pass

    try:
        back_btn = page.get_by_role("button", name="Back")
        if back_btn.is_visible(timeout=2000):
            back_btn.click()
            page.wait_for_timeout(DELAY_LONG)
            dismiss_modals(page)
            page.get_by_role("button", name="Add Expense").wait_for(state="visible", timeout=10000)
            log.info("    ✓ Recovered via Back button")
            return True
    except Exception:
        pass

    log.warning("    ✗ Auto-recovery failed — manual intervention may be needed")
    return False


# ── Main Loop ────────────────────────────────────────────────
def run_bot(page: Page, receipts: list[Receipt], dry_run: bool = False, reason: str = ""):
    """
    Process all receipts with progress tracking and auto-recovery.
    """
    total_amount = sum(r.amount for r in receipts)
    submitted = load_progress()
    remaining = [r for r in receipts if r.filename not in submitted]
    already_done = len(receipts) - len(remaining)

    print("\n" + "=" * 55)
    print("  HELIOS EXPENSE BOT")
    print("=" * 55)
    print(f"  Total receipts      : {len(receipts)}")
    if already_done > 0:
        print(f"  Already submitted   : {already_done} (from previous run)")
        print(f"  Remaining           : {len(remaining)}")
    print(f"  Standard (≤ ${EXPENSE_CAP:.0f})  : {sum(1 for r in remaining if not r.is_over_cap)}")
    print(f"  Over-cap (> ${EXPENSE_CAP:.0f})  : {sum(1 for r in remaining if r.is_over_cap)}")
    print(f"  Total amount        : HKD ${total_amount:,.2f}")
    if remaining:
        print(f"  Date range          : {remaining[0].date_display} → {remaining[-1].date_display}")
    print(f"  Mode                : {'DRY RUN' if dry_run else 'LIVE'}")
    print("=" * 55)

    if not remaining:
        print("\n  All receipts already submitted! Use 'reset' to start fresh.")
        choice = input("  Type 'reset' to clear progress, or Enter to exit: ").strip()
        if choice.lower() == "reset":
            clear_progress()
            print("  Progress cleared. Run again to resubmit all receipts.")
        return

    if dry_run:
        print("\n  ── WORKING MEALS (Flow A) ──\n")
        for i, r in enumerate([r for r in remaining if not r.is_over_cap], 1):
            print(f"  {i:3d}. {r.filename}")
            print(f"       {r.date_display}  |  HKD ${r.amount:.2f}")
        print(f"\n  ── COS MEALS (Flow B) ──\n")
        for i, r in enumerate([r for r in remaining if r.is_over_cap], 1):
            print(f"  {i:3d}. {r.filename}")
            print(f"       {r.date_display}  |  HKD ${r.amount:.2f}")
        print(f"\n  {len(remaining)} receipts ready.\n")
        return

    input("\n  Press Enter to start submitting... ")

    succeeded = 0
    failed = 0
    errors = []

    batch_standard = [r for r in remaining if not r.is_over_cap]
    batch_over_cap = [r for r in remaining if r.is_over_cap]
    batched = batch_standard + batch_over_cap

    abort = False
    for i, receipt in enumerate(batched, 1):
        if abort:
            break

        flow_name = "Flow B (COS)" if receipt.is_over_cap else "Flow A (Working)"
        log.info(f"[{i}/{len(batched)}] {flow_name}: {receipt.filename}")

        dismiss_modals(page)

        success = False
        for attempt in range(2):
            try:
                if receipt.is_over_cap:
                    flow_over_cap(page, receipt, reason)
                else:
                    flow_standard(page, receipt)

                succeeded += 1
                submitted.add(receipt.filename)
                save_progress(submitted)
                success = True
                break

            except Exception as e:
                if attempt == 0:
                    log.warning(f"  ⚠ Failed (attempt 1): {e}")
                    log.info("  Attempting auto-recovery and retry...")

                    try:
                        error_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "errors")
                        os.makedirs(error_dir, exist_ok=True)
                        page.screenshot(path=os.path.join(error_dir, f"retry_{i}_{receipt.filename}.png"))
                    except Exception:
                        pass

                    if not recover_to_expense_list(page):
                        log.error(f"  ✗ Recovery failed, skipping retry")
                        break
                else:
                    break

        if not success:
            log.error(f"  ✗ FAILED after retry: {receipt.filename}")
            failed += 1
            errors.append((receipt.filename, "Failed after retry"))

            try:
                error_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "errors")
                os.makedirs(error_dir, exist_ok=True)
                page.screenshot(path=os.path.join(error_dir, f"error_{i}_{receipt.filename}.png"))
            except Exception:
                pass

            choice = input(f"\n  Receipt {i} failed. Continue? (y/n): ")
            if choice.strip().lower() != "y":
                save_progress(submitted)
                abort = True
            else:
                recover_to_expense_list(page)

    save_progress(submitted)

    print("\n" + "=" * 55)
    print("  COMPLETE")
    print("=" * 55)
    print(f"  ✓ Succeeded : {succeeded}")
    print(f"  ✗ Failed    : {failed}")
    if errors:
        print(f"\n  Issues:")
        for fname, err in errors:
            print(f"    {fname}: {err}")
    print("=" * 55 + "\n")


# ── Navigate to Expense Report ────────────────────────────────
def navigate_to_expense_report(page: Page):
    """Navigate from dashboard to a specific expense report."""
    print("\n  Navigating to Expense Claim...")
    page.wait_for_timeout(5000)
    page.locator("span.text-ellipsis", has_text="Expense Claim").click()
    page.wait_for_timeout(DELAY_LONG)

    table_body = page.locator(".ant-table-body .ant-table-tbody")
    table_body.wait_for(state="visible", timeout=15000)
    page.wait_for_timeout(DELAY_SHORT)

    rows = table_body.locator("tr.ant-table-row")
    row_count = rows.count()

    if row_count == 0:
        print("  No expense claims found. Please create one first.")
        return False

    print("\n  Available Expense Claims:")
    print("  " + "-" * 55)

    claims = []
    for i in range(row_count):
        row = rows.nth(i)
        cells = row.locator("td")

        try:
            row_num = cells.nth(2).inner_text(timeout=2000).strip()
            reason = cells.nth(6).locator("span.popover-wrap span").inner_text(timeout=2000).strip()

            if reason:
                claims.append({
                    "num": row_num,
                    "reason": reason,
                    "row_element": row,
                })
                print(f"  {row_num}. {reason}")
        except Exception:
            continue

    if not claims:
        print("  Could not extract expense claim names.")
        return False

    print("  " + "-" * 55)

    while True:
        choice = input(f"\n  Select expense claim (enter row number): ").strip()
        selected = None
        for c in claims:
            if c["num"] == choice:
                selected = c
                break
        if selected:
            break
        try:
            idx = int(choice)
            if 1 <= idx <= len(claims):
                selected = claims[idx - 1]
                break
        except ValueError:
            pass
        print(f"  Invalid selection. Enter a number from the list above.")

    print(f"\n  Opening: {selected['reason']}...")

    selected["row_element"].locator("td").nth(6).click()
    page.wait_for_timeout(DELAY_LONG)

    try:
        page.get_by_role("button", name="Add Expense").wait_for(state="visible", timeout=15000)
        print("  ✓ Expense report loaded — ready to add expenses")
    except Exception:
        print("  Waiting for page to fully load...")
        page.wait_for_timeout(DELAY_LONG * 2)

    confirm = input("\n  Press Enter to continue, or type 'return' to go back: ").strip().lower()
    if confirm == "return":
        try:
            page.get_by_role("button", name="Back").click()
            page.wait_for_timeout(DELAY_LONG)
        except Exception:
            page.go_back()
            page.wait_for_timeout(DELAY_LONG)
        return navigate_to_expense_report(page)

    return True


# ── Interactive Session ───────────────────────────────────────
def main():
    """Interactive flow: open browser → auto-login → select expense claim → submit."""
    config = load_config()
    session_dir = os.path.expanduser(config.get("session_dir", "~/.helios/session"))
    staging_dir = os.path.expanduser(config.get("staging_dir", "~/helios-staging"))

    print("\n" + "=" * 55)
    print("  HELIOS EXPENSE BOT")
    print("=" * 55)
    print("  Opening Helios...\n")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=session_dir,
            headless=False,
            viewport={"width": 1280, "height": 900},
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(HELIOS_URL)

        print("  Browser opened. Your saved credentials should auto-login.")
        input("\n  Press Enter once the dashboard has loaded... ")

        if not navigate_to_expense_report(page):
            context.close()
            return

        folder = input(f"\n  Enter receipts folder path [{staging_dir}]: ").strip()
        folder = folder.strip("'\"") or staging_dir

        receipts = load_receipts(folder)
        if not receipts:
            print("  No valid receipts found. Exiting.")
            context.close()
            return

        over_cap_count = sum(1 for r in receipts if r.is_over_cap)
        reason_text = ""
        if over_cap_count > 0:
            print(f"\n  {over_cap_count} receipt(s) are over the expense cap (HKD ${EXPENSE_CAP:.0f}).")
            reason_text = input("  Enter the reason for over-cap expenses: ").strip()
            if not reason_text:
                print("  No reason provided — over-cap receipts will be skipped.")

        input("\n  Press Enter to start adding expenses... ")

        run_bot(page, receipts, reason=reason_text)

        input("\n  Press Enter to close browser... ")
        context.close()


if __name__ == "__main__":
    main()
