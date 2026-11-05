---
name: express-tracker
description: Express tracking assistant. Use when users ask to track packages, trace deliveries, check package status. User provides express company name and tracking number. Query via official websites, Kuaidi100, Cainiao, Baidu and other channels.
---

# Express Tracker

## Core Functions

This skill queries express logistics information through multiple channels based on user-provided express company name and tracking number.

## Supported Express Companies

| Company Name | Company Code | Website |
|--------------|--------------|---------|
| Shunfeng | sf | https://www.sf-express.com |
| YTO | yto | https://www.yto.net.cn |
| ZTO | zto | https://www.zto.com |
| Yunda | yunda | https://www.yundaex.com |
| STO | sto | https://www.sto.cn |
| EMS | ems | https://www.ems.com.cn |
| JD Logistics | jd | https://www.jdwl.com |
| Debang | debang | https://www.deppon.com |
| J&T Express | jt | https://www.jtexpress.com |
| Yunexpress | yunexpress | https://www.yuntrack.com |
| 4PX | 4px | https://www.4px.com |

## Query Channels

### Primary Channels (Priority Order)

1. **Kuaidi100** - https://www.kuaidi100.com
   - URL Pattern: `https://www.kuaidi100.com/query?type={code}&postid={tracking_number}`
   - Best coverage for most express companies

2. **Cainiao** - https://www.cainiao.com
   - Official Alibaba logistics platform
   - Good for Taobao/Tmall orders

3. **Official Websites**
   - Direct query on express company website

4. **Baidu Search**
   - Search query: `{tracking_number} tracking`

5. **17Track** - https://www.17track.net
   - Universal tracking platform
   - Good for international express

## Execution Flow

### Step 1: Extract Information

Extract from user input:
- Express company name (if provided)
- Tracking number

### Step 2: Identify Company Code

Map company name to code:

| Input Keywords | Company | Code |
|----------------|---------|------|
| Shunfeng, SF, shunfeng | Shunfeng | sf |
| YTO, yto, Yuantong | YTO | yto |
| ZTO, zto, Zhongtong | ZTO | zto |
| Yunda, yunda, Yunda | Yunda | yunda |
| STO, sto, Shentong | STO | sto |
| EMS, ems, Post | EMS | ems |
| JD, jd, Jingdong | JD Logistics | jd |
| Debang, debang | Debang | debang |
| J&T, jt, Jitui | J&T Express | jt |
| Yunexpress, Yun | Yunexpress | yunexpress |
| 4PX | 4PX | 4px |

### Step 3: Multi-Channel Query

Query in order of priority:

1. **Kuaidi100 API Query**
   ```
   https://www.kuaidi100.com/query?type={code}&postid={tracking_number}
   ```

2. **Cainiao Query**
   ```
   https://www.cainiao.com (use web scraping)
   ```

3. **Official Website**
   ```
   {company_website}/track (use web scraping)
   ```

4. **Baidu Search**
   ```
   Search: {tracking_number} tracking
   ```

### Step 4: Parse and Format Results

Extract from JSON/text response:
- Tracking events (time, location, description)
- Current status
- Delivery state

## Output Format

### Success Response

```
==============================================
Express Tracking Information
==============================================

Company: STO Express
Tracking Number: 777398524745366
Current Status: In Transit
Latest Location: Langfang, Hebei
Last Updated: 2026-04-09 22:47:36

----------------------------------------------
Tracking History
----------------------------------------------
2026-04-09 22:47:36 | Langfang, Hebei | Package departed for next destination
2026-04-09 22:42:38 | Langfang, Hebei | Package arrived at transit center
2026-04-09 21:24:45 | Langfang, Hebei | Package departed collection point
2026-04-09 21:19:45 | Langfang, Hebei | Package arrived at collection point
2026-04-09 18:58:45 | Langfang, Hebei | Package departed for next destination
2026-04-09 18:58:35 | Langfang, Hebei | Package picked up by courier

----------------------------------------------
Query Source: Kuaidi100
==============================================
```

### No Information Response

```
==============================================
Express Tracking Information
==============================================

Company: EMS
Tracking Number: 9815491874877
Current Status: No Information Available

----------------------------------------------
Query Result
----------------------------------------------
No tracking information found for this number.

Possible Reasons:
- Tracking number does not exist or has expired
- Information not yet uploaded to the system
- Please verify with sender

Query Source: Kuaidi100
==============================================
```

### Error Response

```
==============================================
Query Error
==============================================

Tracking Number: XXXXXXXXXX
Error: Unable to query at this time

Suggestions:
- Please try again in a few minutes
- Verify the tracking number with sender
- Try alternative query channels

Query Source: Kuaidi100 (Failed)
Alternative: Cainiao (Not attempted)
==============================================
```

## Status Codes

| Code | Status |
|------|--------|
| 0 | Pending |
| 1 | Picked Up |
| 2 | In Transit |
| 3 | Out for Delivery |
| 4 | Delivered |
| 5 | Rejected |
| 6 | Returned |
| 7 | Return Received |
| 8 | Abnormal |

## Usage Examples

### Example 1: User provides company and number

**User Input**: "Track STO express 777398524745366"

**Execution**:
1. Extract: Company=STO, Number=777398524745366
2. Map code: STO -> shentong
3. Query Kuaidi100
4. Format and return results

**Output**: Complete tracking information

### Example 2: User provides number only

**User Input**: "Check 9815491874877"

**Execution**:
1. Extract: Number=9815491874877 (13 digits)
2. Attempt auto-identification: 13-digit -> EMS
3. Query Kuaidi100 with EMS
4. Format and return results

### Example 3: Multiple packages

**User Input**: "Track these packages: SF123456789, YT987654321"

**Execution**:
1. Parse all tracking numbers
2. Query each one
3. Return combined results

## Technical Implementation

### Web Scraping Tools

Use `extract_content_from_websites` tool for:
- Kuaidi100 API endpoint
- Cainiao tracking page
- Official express company websites
- Baidu search results

### API Endpoints

```
Kuaidi100 Query:
GET https://www.kuaidi100.com/query?type={code}&postid={number}

Kuaidi100 Response Format (JSON):
{
  "message": "ok",
  "nu": "tracking_number",
  "com": "company_name",
  "status": "200",
  "state": "3",
  "data": [
    {
      "time": "2026-04-09 22:47:36",
      "context": "Event description",
      "location": "Location"
    }
  ]
}
```

### Error Handling Strategy

1. **Primary channel fails**: Try next channel
2. **All channels fail**: Return error with suggestions
3. **No information found**: Return "No Information" response
4. **Invalid input**: Ask user for clarification

### Channel Priority

1. Kuaidi100 (fastest, most reliable)
2. Cainiao (good for Alibaba orders)
3. Official website (most accurate)
4. 17Track (for international)
5. Baidu search (fallback)

## Features

- Multi-channel query with fallback
- Auto-identification of express company from number
- Complete tracking history display
- Current status display
- Query source attribution
- Error handling with suggestions
- Support for batch queries
- International express support
