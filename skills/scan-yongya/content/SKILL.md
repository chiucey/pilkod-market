---
name: scan-yongya
description: >
  Naraka: Bladestone Yongya equipment account scanner. Use when users ask to scan Yongya equipment accounts on Jiaoyimao,
  find accounts with 3+ Yongya equipment, or scan Naraka: Bladestone accounts.
  Supports multi-platform scanning (Android/iOS), multiple price tier filtering, infinite scroll loading, CSV export.
  Triggers: Naraka, Yongya, scan_yongya, scan-yongya, Jiaoyimao scan, equipment scan.
---

# Yongya Equipment Scanner

Scan Naraka: Bladestone accounts on Jiaoyimao platform, filtering accounts with 3+ Yongya equipment pieces.

## Execution Flow

### 1. Prerequisites

```bash
cd /workspace/temp-skills/scan-yongya
pip install playwright -q
playwright install chromium --with-deps
```

### 2. Run Scan

Execute scan script using browser CLI:

```bash
cd /workspace/temp-skills/scan-yongya
python scripts/scan_yongya_browser.py
```

### 3. View Results

Scan results saved to `outputs/found_3yongya_browser.csv`

## Scan Configuration

| Parameter | Value |
|-----------|-------|
| Min Yongya Count | 3 pieces |
| Max Scroll Times | 80 |
| Stable Stop Condition | 4 consecutive no-new |

## Platform Coverage

- **Android (Lingxi)**: https://www.jiaoyimao.com/lingxi/g1009207/
- **iOS**: https://www.jiaoyimao.com/lingxi/g1009207-3/

## Price Tier Filtering

| Tier | Filter |
|------|--------|
| 50000+ | price >= 50000 |
| 40000+ | price >= 40000 |
| 30000+ | price >= 30000 |
| 20000+ | price >= 20000 |
| 10000+ | price >= 10000 |
| Unlimited | All prices |

## Output Format

CSV file contains the following fields:
- `item_id`: Product ID
- `platform`: Platform (Android/iOS)
- `url`: Product link
- `price`: Price (CNY)
- `yongya`: Yongya equipment count
- `name`: Account name
- `os_tag`: OS tag
- `tier`: Price tier
- `text`: Account description

## Technical Implementation

- Uses `browser` CLI to control real browser
- Infinite scroll: repeatedly scroll until card count stabilizes
- Anti-crawler: simulates real user behavior
- Search condition: `s3_equip_skill` contains "Yongya"
