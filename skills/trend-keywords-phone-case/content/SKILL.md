---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 48f9ac102e3ca4db95e6f4bbedb628ad
    PropagateID: 48f9ac102e3ca4db95e6f4bbedb628ad
    ReservedCode1: 3045022100f9a5e01d39f92bc28deaa56bdbd14d13a9c58d0e0b523542ae136f7ae1a3d15e02201589de20632b1b34ba9b4bb652af857fc3561027e22e936241969c07a1d94b17
    ReservedCode2: 3045022100ff07ff279dc517afc854d7bd491a699f9c6d01c11326bf0c65510a490d84de9f02202d01b2e000a6d66fbf3508479593620a34265cb011f78ed7b190b3e6559729ce
description: Search and analyze trending keywords from Google, Facebook, TikTok and other platforms related to phone cases, then generate an Excel report saved to desktop with today's date as filename. Use when users request social media trend analysis, hot search keywords for phone cases, or market research reports.
name: trend-keywords-phone-case
---

# Trend Keywords Phone Case Skill

## Feature Overview

This skill searches trending keywords from Google, Facebook, TikTok, Instagram and Pinterest platforms, filters phone case related trends, and generates an Excel report saved to the user's desktop with today's date as the filename.

## Execution Steps

### Step 1: Search Platform Trends

Use `batch_web_search` tool to search for trending keywords from each platform:

**Google Trends Search:**
```
Google Trends trending keywords phone case 2026
Google hot search phone case accessories
```

**TikTok Trends Search:**
```
TikTok trending hashtags phone case 2026 viral
TikTok hot topics phone case
```

**Facebook Trends Search:**
```
Facebook trending topics phone case 2026
Facebook popular discussions phone accessories
```

**Instagram Trends Search:**
```
Instagram trending phone case keywords 2026
Instagram hot hashtags phone case
```

**Pinterest Trends Search:**
```
Pinterest trending phone case ideas 2026
Pinterest popular phone case designs
```

### Step 2: Filter Phone Case Related Keywords

From search results, extract and filter keywords that are relevant to phone cases:
- Product types: clear case, shockproof case, silicone case, wallet case, etc.
- Features: MagSafe, waterproof, drop-proof, custom, personalized, etc.
- Styles: minimalist, aesthetic, vintage, artistic, etc.
- Materials: silicone, TPU, PC, leather, eco-friendly, etc.
- Popular hashtags and tags from each platform

### Step 3: Analyze and Categorize Trends

Organize filtered keywords by platform:
| Platform | Data Points |
|----------|-------------|
| Google Trends | Search keywords, trend direction, popularity score |
| TikTok | Hashtags, estimated views, content type |
| Facebook | Discussion topics, engagement level, user demographics |
| Instagram | Visual hashtags, aesthetic categories, interaction rate |
| Pinterest | Design trends, search growth rate, pin count |

### Step 4: Generate Excel Report

Use Python with openpyxl to create Excel workbook:

**Required Python Libraries:**
```python
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
from datetime import datetime
```

**Excel Structure:**
1. **Cover Sheet** - Report title, date, data sources
2. **Summary Sheet** - All platforms combined overview
3. **Google Trends Sheet** - Google-specific keywords
4. **TikTok Trends Sheet** - TikTok hashtags and topics
5. **Facebook Trends Sheet** - Facebook discussions
6. **Instagram Trends Sheet** - Instagram hashtags
7. **Pinterest Trends Sheet** - Pinterest design trends

### Step 5: Save to Desktop with Today's Date

**Generate filename:**
```python
today = datetime.now().strftime('%Y-%m-%d')
filename = f"phone_case_trends_{today}.xlsx"
```

**Desktop paths by OS:**
- Windows: `C:\\Users\\{username}\\Desktop\\{filename}`
- Mac: `/Users/{username}/Desktop/{filename}`
- Linux: `/home/{username}/Desktop/{filename}`

**Save Excel:**
```python
wb.save(desktop_path + filename)
```

### Step 6: Report Results

After completion, report to the user:
- Total keywords analyzed
- Platforms covered
- File save location (full path)
- File name

## Excel Column Structure

### Summary Sheet
| Column | Header |
|--------|--------|
| A | Platform |
| B | Trend Keyword |
| C | Search Trend |
| D | Relevance Score |
| E | Notes |

### Platform-Specific Sheets
| Column | Header |
|--------|--------|
| A | Chinese Keyword |
| B | English Keyword |
| C | Trend Direction |
| D | Popularity Index |
| E | Category |
| F | Analysis |

## Important Notes

1. **Data Freshness**: Use recent search queries (past 30 days) for up-to-date trends
2. **Relevance Filter**: Only include keywords directly related to phone cases
3. **Multi-language**: Include both Chinese and English keywords for comprehensive coverage
4. **Trend Indicators**: Mark trend direction (rising, stable, declining)
5. **File Organization**: Create separate subfolders if needed (e.g., by date or category)

## Example Output

**Filename:** `phone_case_trends_2026-03-28.xlsx`

**File Location:** `/Users/username/Desktop/phone_case_trends_2026-03-28.xlsx`

**Report Content:**
- 50+ trending keywords across 5 platforms
- Categories: Product Types, Features, Styles, Materials
- Trend indicators with popularity scores

## Use Triggers

- "Search trending phone case keywords"
- "Analyze platform trend keywords"
- "Generate phone case trend report to desktop"
- "Export today's trending keywords to Excel"
- "Research phone case market trends"
- "Hot selling phone case trends analysis"
- "Social media trending keywords for phone cases"
