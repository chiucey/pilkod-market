---
name: helios
description: Process receipt photos and submit expenses to the Helios expense system. Use when a user sends a receipt photo (any image), asks to check the expense queue (/status or "how many receipts"), or asks to submit expenses to Helios (/submit or "submit my receipts"). Handles OCR via vision, staging receipts, and Playwright-based submission.
---

# Helios Expense Skill

## Notes

- **Staging dir**: `~/helios-staging/` (override with `~/.helios/config.json` → `staging_dir`)
- **Session dir**: `~/.helios/session/` (override with `~/.helios/config.json` → `session_dir`)
- **helios_bot.py**: `scripts/helios_bot.py`
- **EXPENSE_CAP**: Configurable via `~/.helios/config.json` → `expense_cap` (default: HKD 115.00)

---

## 1. Receipt Intake (when a user sends a photo)

Use vision to extract from the receipt image:
- **Date**: month (3-letter abbrev, e.g. `Mar`), day (no leading zero), year (4-digit)
- **Total amount** in HKD (numeric, 2 decimal places)
- Merchant name is optional

**Project code**: Ask once per batch if not already known for this session:
> "What project code for this batch? (e.g. PJ_Q)"

Cache it for the session — only ask again when a new batch starts.

**Stage the receipt:**
```bash
python3 scripts/stage_receipt.py \
  --image <path> --project <code> \
  --month <Jan|Feb|...> --day <N> --year <YYYY> --amount <N.NN>
```

**If OCR fails** (can't read date or amount):
```bash
python3 scripts/stage_receipt.py \
  --image <path> --project <code> --unknown
```

**Reply format after staging:**
> ✅ Got it — HKD $68.00, Mar 14 2026. Staged. (3 in queue)

Get the queue count from the `count` field in `list_queue.py` output, or from the `stage_receipt.py` success response.

---

## 2. Check Queue (`/status` or "how many receipts")

```bash
python3 scripts/list_queue.py
```

Output the results formatted as a table. Example response:
> **Queue: 3 receipts — HKD $214.00 total**
>
> | # | File | Date | Amount | Note |
> |---|------|------|--------|------|
> | 1 | PJ_Q_Expense_Mar_12_2026_68.00.jpg | Mar 12 2026 | $68.00 | |
> | 2 | PJ_Q_Expense_Mar_14_2026_120.00.jpg | Mar 14 2026 | $120.00 | ⚠️ over cap |
> | 3 | PJ_Q_Expense_Mar_18_2026_26.00.jpg | Mar 18 2026 | $26.00 | |

---

## 3. Submit Receipts (`/submit` or "submit my receipts")

### Step 1 — Show queue
Run `list_queue.py` and display what will be submitted.

### Step 2 — Handle over-cap receipts
If `over_cap_count > 0`, ask upfront:
> "You have N receipt(s) over the expense cap. What's the reason? (e.g. 'client entertainment')"

Collect one reason that applies to all over-cap receipts, or ask per-receipt if different reasons are needed.

### Step 3 — Get claim list
```bash
python3 scripts/get_claims.py
```

Present the claims:
> **Which expense claim?**
> 1. Q2 2026 Expenses
> 2. Q1 2026 Expenses

Ask the user to pick one by number.

### Step 4 — Submit
Build the `--reasons` JSON (only needed for over-cap receipts):
```bash
python3 scripts/submit_receipts.py \
  --claim <index> \
  --reasons '{"PJ_Q_Expense_Mar_14_2026_120.00.jpg": "client entertainment"}'
```

### Step 5 — Stream progress
As JSON lines arrive on stdout, relay updates:
> ✅ 1/3 — PJ_Q_Expense_Mar_12_2026_68.00.jpg
> ✅ 2/3 — PJ_Q_Expense_Mar_14_2026_120.00.jpg
> ✅ 3/3 — PJ_Q_Expense_Mar_18_2026_26.00.jpg

### Step 6 — Final summary
When `{"event": "done", ...}` arrives, show:
> **Done! 3/3 submitted.** Staging folder cleared.

If there were failures:
> **3 submitted, 1 failed.** Failed: PJ_Q_Expense_Mar_18_2026_26.00.jpg

---

## 4. Helios Login (session expired)

If `get_claims.py` or `submit_receipts.py` returns `{"ok": false, "error": "auth_required"}`:

Tell the user:
> "Helios session expired. Run this to log in:
> ```
> python3 scripts/helios_bot.py --login
> ```
> Log in manually in the browser that opens, then try again."

---

## Script Reference

| Script | Purpose | Key args |
|--------|---------|----------|
| `stage_receipt.py` | Copy + rename receipt to staging | `--image --project --month --day --year --amount` or `--unknown` |
| `list_queue.py` | List staging folder contents | `[--staging-dir]` |
| `get_claims.py` | Scrape Helios claim list | `[--timeout]` |
| `submit_receipts.py` | Submit all staged receipts | `--claim <N> [--reasons JSON] [--dry-run]` |

All scripts output JSON to stdout, errors to stderr.
