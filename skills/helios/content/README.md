# helios-skill

An [OpenClaw](https://openclaw.ai) skill for automating expense submissions to the Helios expense system (console.huilianyi.com) via Playwright browser automation.

Send a receipt photo to your AI assistant → it OCRs the date and amount, stages the file, and submits it to Helios automatically.

---

## Prerequisites

- Python 3.11+
- [OpenClaw](https://openclaw.ai) installed
- A Helios account at [console.huilianyi.com](https://console.huilianyi.com)

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/deeenton-ai/helios-skill.git
cd helios-skill

# 2. Run setup (installs dependencies, creates config)
bash setup.sh

# 3. Edit your config
nano ~/.helios/config.json

# 4. Log in to Helios (saves browser session)
python scripts/helios_bot.py --login
```

---

## Config Reference

Config lives at `~/.helios/config.json`:

```json
{
  "session_dir": "~/.helios/session",
  "staging_dir": "~/helios-staging",
  "expense_cap": 115.00,
  "non_gc_dinner_attendees": [],
  "helios_url": "https://console.huilianyi.com/"
}
```

| Key | Description |
|-----|-------------|
| `session_dir` | Where Playwright stores the persistent browser session (login cookies) |
| `staging_dir` | Where staged receipt images are stored before submission |
| `expense_cap` | Receipts above this amount (HKD) use the COS Meal flow |
| `non_gc_dinner_attendees` | List of names to tick as Non-GC dinner attendees in COS Meal submissions (e.g. `["Alice Smith", "Bob Jones"]`) |
| `helios_url` | Helios console URL (default: `https://console.huilianyi.com/`) |

---

## Install as OpenClaw Skill

Copy the folder to your OpenClaw skills directory:

```bash
cp -r helios-skill ~/.openclaw/skills/helios
```

OpenClaw will detect it automatically on next startup.

---

## Usage

Once installed as an OpenClaw skill:

1. **Send a receipt photo** to your AI assistant (via Telegram, Discord, etc.)  
   → The skill extracts the date and amount via vision OCR  
   → Replies: `✅ Got it — HKD $68.00, Mar 14 2026. Staged. (3 in queue)`

2. **Check your queue** with `/status` or "how many receipts?"  
   → Shows a table of staged receipts with amounts and totals

3. **Submit to Helios** with `/submit` or "submit my receipts"  
   → Picks the claim, handles over-cap receipts, streams progress back

### Manual scripts

```bash
# Stage a receipt manually
python scripts/stage_receipt.py --image receipt.jpg --project PROJ --month Mar --day 14 --year 2026 --amount 68.00

# List staged receipts
python scripts/list_queue.py

# Get available expense claims
python scripts/get_claims.py

# Submit all staged receipts to claim #1
python scripts/submit_receipts.py --claim 1

# Dry run (no browser)
python scripts/submit_receipts.py --claim 1 --dry-run
```

### Rename receipts with Claude OCR

`rename_receipts.py` is a standalone utility that batch-processes a folder of receipt photos using Claude vision — converting HEIC/PNG/MOV, fixing rotation, and renaming files to the `PROJ_Expense_Mon_DD_YYYY_AMOUNT.jpg` format expected by the skill.

```bash
python rename_receipts.py /path/to/raw/receipts
```

Requires `ANTHROPIC_API_KEY` in your environment.

---

## Notes

- Built for the Helios expense system at [console.huilianyi.com](https://console.huilianyi.com)
- Uses Playwright Chromium with a persistent session — you only need to log in once
- Progress is tracked in `scripts/progress.json` so interrupted runs can resume
- Error screenshots are saved to `scripts/errors/` on failure
