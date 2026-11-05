---
name: neftegaz2026
description: NEFTEGAZ 2026 exhibition exhibitor database with 763 companies from 8 countries. Use for querying exhibitor lists, searching companies by name/country/letter, generating exhibitor reports, analyzing exhibition statistics, or exporting exhibitor data to Excel/CSV. Triggers on questions about NEFTEGAZ 2026 exhibitors, oil and gas exhibition participants, or requests to look up specific companies at the exhibition.
---

# NEFTEGAZ 2026 Exhibitor Database

Complete exhibitor database for NEFTEGAZ 2026 (25th International Exhibition for Equipment and Technologies for Oil and Gas Industries), Moscow, April 14–17, 2026.

## Quick Facts

- **763 exhibitors** from **8 countries** (Russia 58.7%, China 39.1%, others 2.2%)
- Data includes English name, Russian name (where available), country, and catalog page
- Source: Official NEFTEGAZ 2026 catalog

## Data Access

### Query Script

Use `scripts/query_exhibitors.py` for all data operations:

```bash
# List all exhibitors
python3 scripts/query_exhibitors.py --list

# Search by keyword
python3 scripts/query_exhibitors.py --search "valve"

# Filter by country
python3 scripts/query_exhibitors.py --country "China"

# Filter by first letter
python3 scripts/query_exhibitors.py --letter "S"

# Show statistics
python3 scripts/query_exhibitors.py --stats

# Export to CSV
python3 scripts/query_exhibitors.py --export csv --output /path/to/output.csv

# Export to Excel (formatted)
python3 scripts/query_exhibitors.py --export excel --output /path/to/output.xlsx

# Combine filters
python3 scripts/query_exhibitors.py --country "Russia" --letter "A"
```

### Direct JSON Access

For programmatic access, read `references/exhibitors.json`:

```python
import json
with open('references/exhibitors.json', 'r') as f:
    exhibitors = json.load(f)
# Each entry: {"no", "company_name_en", "company_name_ru", "country", "page"}
```

### Pre-built Excel Template

A formatted Excel file is available at `templates/NEFTEGAZ_2026_Exhibitors_A-Z.xlsx` with:
- Sheet 1: Full A–Z exhibitor list with auto-filter and freeze panes
- Sheet 2: Country summary statistics

## Reference Files

- **Exhibition overview and statistics**: Read `references/overview.md` for event details, country breakdown, section descriptions, and data structure
- **Raw exhibitor data**: `references/exhibitors.json` — JSON array of all 763 exhibitors
- **Excel template**: `templates/NEFTEGAZ_2026_Exhibitors_A-Z.xlsx` — formatted spreadsheet ready for delivery

## Common Tasks

### Look up a specific company
Run `query_exhibitors.py --search "company name"` to find matching entries.

### Generate country-specific exhibitor list
Run `query_exhibitors.py --country "China" --export excel --output china_exhibitors.xlsx`.

### Provide exhibition statistics
Run `query_exhibitors.py --stats` or read `references/overview.md`.

### Deliver the full exhibitor list
Copy `templates/NEFTEGAZ_2026_Exhibitors_A-Z.xlsx` to the working directory and send to user.
