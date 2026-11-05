---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 30440220643b692a30f5f42bc8e7a526cc0db01803934d68e3a882b324eb9dc5f476804e0220188bd0dc2e63c4463807fc44a1762469370b9616db16a82388cf08cf3d9bb9a0
    ReservedCode2: 3046022100d54b6b164113d057aaeb2de6550dcc3196e8d4eff12ff39893b4ef7bea0c45b4022100bacd9e0ba67f18df4531d5a0e8830fbf65b0d416de49d1ed8014152f4d55c108
description: Logistics tracking expert skill. Use when users ask to track packages, trace deliveries, check package status, query express logistics. User provides express company name and tracking number. Uses interactive web browsing to query Kuaidi100, Cainiao, 17Track, and official express websites to get complete delivery progress with visual timeline. Supports WorkBuddy and Claude Code platforms.
name: express-tracking-master
---

# Express Tracking Master (Express Logistics Expert)

## Core Functions

This skill queries express logistics information through **interactive web browsing**. It identifies the express company from user input, navigates to the appropriate tracking website, fills in the tracking number, and retrieves complete delivery progress with visual timeline display.

## Technical Approach

### Why Interactive Web Browsing?

Most express tracking websites (Kuaidi100, express company official sites) require JavaScript interactions:
1. Select express company from dropdown
2. Enter tracking number in input field
3. Click query/track button
4. Wait for results to load dynamically

This skill uses `interact_with_website` tool to simulate real user behavior on these websites.

## Supported Express Companies

| Company Name | Official Website | Alternative Query |
|-------------|------------------|-------------------|
| Shunfeng | https://www.sf-express.com | Kuaidi100 |
| YTO | https://www.yto.net.cn | Kuaidi100 |
| ZTO | https://www.zto.com | Kuaidi100 |
| Yunda | https://www.yundaex.com | Kuaidi100 |
| STO | https://www.sto.cn | Kuaidi100 |
| EMS | https://www.ems.com.cn | Kuaidi100 |
| JD Logistics | https://www.jdwl.com | Kuaidi100 |
| Debang | https://www.deppon.com | Kuaidi100 |
| J&T Express | https://www.jtexpress.com.cn | Kuaidi100 |
| Yunexpress | https://www.yuntrack.com | 17Track |
| 4PX | https://www.4px.com | 17Track |
| Zto56 | https://www.zto56.com | Kuaidi100 |

## Query Channels (Priority Order)

### 1. Baidu Search (Primary - Most Reliable)
- **URL**: https://www.baidu.com/s?wd={tracking_number}+{company_name}
- **Best for**: All express companies, provides complete tracking info
- **Success Rate**: Highest - works well for Chinese express
- **Example URL**: https://www.baidu.com/s?wd=JT5475523871856+极兔速递+物流

**Why Baidu Search First?**
- No API restrictions
- Automatically retrieves tracking info from search results
- Works with all Chinese express companies
- Provides complete timeline from pickup to delivery

### 2. Kuaidi100 (Secondary)
- **URL**: https://www.kuaidi100.com
- **Note**: API may be unreliable, use Baidu Search instead

### 3. Express Official Websites (Tertiary)
- Navigate directly to express company website
- May require JavaScript interactions
- Best as fallback

### 4. 17Track (Quaternary)
- **URL**: https://www.17track.net
- **Best for**: International express

### 5. Cainiao (Quinary)
- **URL**: https://www.cainiao.com
- **Best for**: Alibaba/Taobao orders

## Execution Flow

### Step 1: Parse User Input

Extract from user message:
- Express company name (if provided)
- Tracking number

**Supported Input Formats**:
```
- "Track STO 1234567890123"
- "Shunfeng SF1234567890 tracking"
- "Check 9815491874877"
- "Yunda 777398524745366 logistics"
- "ZTO 78595053399309"
- "极兔速递 JT5475523871856"
- "J&T Express JT123456789"
```

### Step 2: Identify Query Website

Based on company name, determine query website:

| Company Keywords | Query Website |
|-----------------|---------------|
| Shunfeng, SF, 顺丰 | kuaidi100 |
| YTO, yto, 圆通 | kuaidi100 |
| ZTO, zto, 中通 | kuaidi100 |
| Yunda, yunda, 韵达 | baidu |
| STO, sto, 申通 | baidu |
| EMS, ems, 邮政 | baidu |
| JD, jd, 京东 | baidu |
| Debang, debang, 德邦 | baidu |
| J&T, jt, 极兔 | baidu |
| Yunexpress, Yun | 17track |
| 4PX, 4px | 17track |
| Zto56, 中通快运 | baidu |

### Step 3: Web Query via Baidu Search (Primary)

Use `extract_content_from_websites` tool with Baidu Search:

**Query URL Pattern**:
```
https://www.baidu.com/s?wd={tracking_number}+{company_name}+物流
```

**Example**:
```
https://www.baidu.com/s?wd=JT5475523871856+极兔速递+物流
```

**Tool Call**:
```json
{
  "url": "https://www.baidu.com/s?wd={tracking_number}+{company_name}+物流",
  "prompt": "Extract ALL tracking information, complete timeline, every delivery event, location, timestamp for tracking number {tracking_number}. Show the full shipping route from pickup to delivery."
}
```

### Step 4: Fallback - Kuaidi100 (If Baidu Fails)

If Baidu search does not return complete tracking info, try Kuaidi100:

**URL**: https://www.kuaidi100.com/query?type={company_code}&postid={tracking_number}

**Company Codes**:
| Company | Code |
|---------|------|
| Shunfeng | sf |
| YTO | yto |
| ZTO | zhongtong |
| Yunda | yunda |
| STO | sto |
| EMS | ems |
| JD | jd |
| Debang | debang |
| J&T Express | jtexpress |

### Step 5: Extract Tracking Results

After successful query, extract tracking timeline:

**Extraction Points**:
- Current status (已签收, 派件中, 运输中, 已揽收)
- Timeline events (time, location, description)
- Delivery route information

### Step 6: Display Visual Timeline

Format and display tracking results with visual timeline.

## Output Format

### Success Response with Visual Timeline

```
================================================================================
                    EXPRESS TRACKING - VISUAL TIMELINE
================================================================================

  Company: J&T Express (极兔速递)
  Tracking Number: JT5475523871856
  Current Status: DELIVERED (已签收)

================================================================================
                              DELIVERY PROGRESS
================================================================================

  [==================================================] 100% Complete

  Latest Update: 2026-04-14 02:57:57
  Location: Beijing Chaoyang District

--------------------------------------------------------------------------------
                           TRACKING TIMELINE
--------------------------------------------------------------------------------

  [9] 2026-04-14 02:57:57  <-- DELIVERED
      |
      |--> Package DELIVERED
           Signed by: 家门口l (Home Delivery)
           Location: Beijing Chaoyang District

  [8] 2026-04-13 22:04:04
      |
      |--> Package OUT FOR DELIVERY
           Courier: 温学崇
           Phone: 17718506500
           Location: Beijing Chaoyang Beigongda Branch

  [7] 2026-04-13 22:03:31
      |
      |--> Package arrived at destination branch
           Location: Beijing Chaoyang Beigongda Branch

  [6] 2026-04-13 18:09:11
      |
      |--> Package departed transfer center
           From: Langfang Lingang Transfer Center
           To: Beijing Chaoyang Beigongda Branch

  [5] 2026-04-13 17:27:46
      |
      |--> Package arrived at transfer center
           Location: Langfang Lingang Transfer Center

  [4] 2026-04-13 13:57:05
      |
      |--> Package departed transfer center
           From: Tianjin Transfer Center
           To: Langfang Lingang Transfer Center

  [3] 2026-04-13 13:55:28
      |
      |--> Package arrived at transfer center
           Location: Tianjin Transfer Center

  [2] 2026-04-13 09:47:31
      |
      |--> Package departed pickup location
           From: Langfang Bazhou City Branch
           To: Tianjin Transfer Center

  [1] 2026-04-13 09:19:54  <-- PICKUP
      |
      |--> Package picked up by J&T Express
           Location: Langfang Bazhou City Branch

================================================================================
                           TRANSIT ROUTE
================================================================================

  Langfang Bazhou City Branch
          ↓
  Tianjin Transfer Center
          ↓
  Langfang Lingang Transfer Center
          ↓
  Beijing Chaoyang Beigongda Branch
          ↓
  DELIVERED to 家门口l

--------------------------------------------------------------------------------
  Query Source: Baidu Search (Web Extraction)
  Query Time:   2026-04-15 09:00:00
================================================================================
```

### No Information Response

```
================================================================================
                    EXPRESS TRACKING - NO INFORMATION
================================================================================

  Company: J&T Express
  Tracking Number: JT123456789
  Current Status: NO INFORMATION FOUND

================================================================================

  Query Result: No tracking information available for this number.

  Possible Reasons:
  - Tracking number may be incorrect or incomplete
  - Package not yet scanned into the system
  - Information not yet uploaded by courier
  - Package may be international (customs processing)

--------------------------------------------------------------------------------
  Suggestions:

  1. Verify tracking number with sender
  2. Wait 24-48 hours after shipment
  3. Check with J&T customer service: 956025
  4. Try alternative query channels

--------------------------------------------------------------------------------
  Query Source: Kuaidi100 (Interactive Web Query)
  Query Time:   2026-04-15 09:00:00
================================================================================
```

### Error Response

```
================================================================================
                    EXPRESS TRACKING - QUERY ERROR
================================================================================

  Tracking Number: XXXXXXXXXX
  Error: Unable to complete query

================================================================================

  Error Details:
  - Website may be temporarily unavailable
  - Network connection issue
  - Website structure may have changed

--------------------------------------------------------------------------------
  Actions Taken:

  [x] Kuaidi100 - Failed
  [ ] Express Official Website - Not attempted
  [ ] 17Track - Not attempted
  [ ] Cainiao - Not attempted

--------------------------------------------------------------------------------
  Suggestions:

  1. Try again in a few minutes
  2. Verify tracking number with sender
  3. Call express company customer service
  4. Use express company official website directly

--------------------------------------------------------------------------------
  Customer Service Hotlines:
  - Shunfeng: 95338
  - YTO: 95554
  - ZTO: 95311
  - STO: 95543
  - EMS: 11183
  - JD: 950616
  - Debang: 95353
  - J&T: 956025

================================================================================
```

## Usage Examples

### Example 1: Complete Query with Visual Timeline

**User Input**:
```
Track J&T Express JT5475523871856
```

**Execution**:
1. Parse: Company=J&T Express, Number=JT5475523871856
2. Identify: Use Kuaidi100 for J&T Express
3. Navigate to https://www.kuaidi100.com
4. Select J&T Express from dropdown
5. Enter tracking number
6. Click query button
7. Wait for results
8. Extract and display visual timeline

**Output**: Complete tracking timeline with progress bar

### Example 2: Chinese Input

**User Input**:
```
极兔速递 JT5475523871856
```

**Execution**:
1. Parse: Company=极兔速递 (J&T Express), Number=JT5475523871856
2. Navigate to Kuaidi100
3. Select J&T Express
4. Enter tracking number
5. Query and display results (Chinese format)

### Example 3: Multiple Packages

**User Input**:
```
Track SF123456789, YTO987654321, ZTO555666777
```

**Execution**:
1. Parse all tracking numbers with companies
2. Query each sequentially
3. Display combined timeline results

## Technical Implementation

### Tool Usage: `interact_with_website`

This skill uses the `interact_with_website` tool for all queries.

**Key Parameters**:
```json
{
  "url": "Target website URL",
  "actions": [
    {
      "type": "navigate | click | fill | wait | extract",
      "selector": "CSS selector (for click/fill/extract)",
      "value": "Value to fill (for fill action)",
      "seconds": "Wait time (for wait action)"
    }
  ]
}
```

### Website Interaction Patterns

#### Kuaidi100 Pattern
```json
{
  "url": "https://www.kuaidi100.com",
  "actions": [
    {"type": "navigate", "url": "https://www.kuaidi100.com"},
    {"type": "wait", "seconds": 2},
    {"type": "click", "selector": "select[name='select-com']"},
    {"type": "click", "selector": "option[value='{code}']"},
    {"type": "fill", "selector": "input[name='postid']", "value": "{number}"},
    {"type": "click", "selector": "button.search-btn"},
    {"type": "wait", "seconds": 3}
  ]
}
```

#### J&T Express Official Pattern
```json
{
  "url": "https://www.jtexpress.com.cn/serviceCreate.html",
  "actions": [
    {"type": "navigate", "url": "https://www.jtexpress.com.cn/serviceCreate.html"},
    {"type": "wait", "seconds": 2},
    {"type": "fill", "selector": "input[name='waybillNo']", "value": "{number}"},
    {"type": "click", "selector": "button.search-btn"},
    {"type": "wait", "seconds": 3}
  ]
}
```

### Error Handling

| Error Type | Handling |
|------------|----------|
| Website timeout | Try next channel |
| Element not found | Try alternative selector |
| No results | Display "No Information" |
| Invalid number | Request user confirmation |
| All channels fail | Provide manual query suggestions |

### Channel Fallback Strategy

```
1. Kuaidi100 (Primary)
   |
   +-- Failed --> 2. Express Official Website
                         |
                         +-- Failed --> 3. 17Track
                                            |
                                            +-- Failed --> 4. Cainiao
                                                               |
                                                               +-- Failed --> Error Response
```

## Platform Compatibility

### WorkBuddy
- Use `interact_with_website` tool directly
- Supports Chinese and English inputs
- Returns formatted markdown output

### Claude Code
- Use `interact_with_website` tool directly
- Compatible with all standard tools
- Returns structured output

## Customer Service Hotlines

| Company | Phone |
|---------|-------|
| Shunfeng | 95338 |
| YTO | 95554 |
| ZTO | 95311 |
| Yunda | 95546 |
| STO | 95543 |
| EMS | 11183 |
| JD | 950616 |
| Debang | 95353 |
| J&T | 956025 |
| 17Track | N/A |

## Features

- **Interactive Web Browsing**: Simulates real user behavior on tracking websites
- **Visual Timeline**: Displays delivery progress with graphical timeline
- **Progress Percentage**: Shows completion percentage for delivery
- **Multi-Channel Fallback**: Automatically tries alternative channels if primary fails
- **Complete History**: Shows all tracking events from pickup to delivery
- **Error Recovery**: Gracefully handles errors with suggestions
- **Batch Processing**: Supports querying multiple packages
- **Bilingual Support**: Works with both Chinese and English inputs
