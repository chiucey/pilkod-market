---
name: logistics-tracker
description: Logistics tracking skill. Use when users ask to track packages, trace deliveries, check package status, or provide tracking numbers. Supports automatic identification of major Chinese express companies (SF Express, YTO, ZTO, Yunda, STO, EMS, JD, Debang, J&T Express, etc.) and returns complete logistics tracking information.
---

# Logistics Tracker Skill

## Core Functions

This skill automatically identifies the logistics company based on the provided tracking number and retrieves complete logistics tracking information via API.

## Execution Flow

### Step 1: Tracking Number Identification

Automatically identify the logistics company based on tracking number format:

| Number Pattern | Logistics Company |
|---------------|-------------------|
| SF prefix / 12 digits | SF Express |
| YT/YTO prefix | YTO Express |
| ZTO prefix | ZTO Express |
| YD prefix | Yunda Express |
| STO prefix | STO Express |
| EMS / EB prefix | China Post EMS |
| JD prefix | JD Logistics |
| JDAB/JDAD prefix | JD Express |
| DB prefix | Debang Express |
| JT prefix | J&T Express |
| 95/96 prefix | China Post Standard |
| LP/CP/RP/SU/TK prefix | Other Common Express |

### Step 2: Logistics Information Query

Call logistics API to retrieve tracking information:
- Use Kuaidi100 or Juhe API for real-time queries
- Support major Chinese express companies

### Step 3: Information Display

Return formatted logistics tracking information:
1. **Basic Info**: Express company, tracking number, current status
2. **Recipient/Sender Info** (if API supports)
3. **Tracking History**: All events in reverse chronological order

## Output Format

### Success Response

```
📦 Logistics Tracking Information

🏢 Company: SF Express
🔢 Tracking Number: SF1234567890123
📍 Current Status: In Transit
📍 Latest Location: Pudong New District, Shanghai
📅 Last Updated: 2026-04-10 18:30:00

━━━━━━━━━━━━━━━━━━━━━━
📍 Tracking History
━━━━━━━━━━━━━━━━━━━━━━
🕐 2026-04-10 18:30 | Shanghai Pudong | Package dispatched, en route to destination
🕐 2026-04-10 14:20 | Shanghai Pudong | Package arrived at Shanghai Pudong Transit Center
🕐 2026-04-10 10:05 | Beijing Chaoyang | Package picked up by courier
🕐 2026-04-10 09:30 | Beijing Chaoyang | Sender notified courier for pickup
━━━━━━━━━━━━━━━━━━━━━━
```

### Identification Failed Response

When unable to identify the express company:

```
⚠️ Unable to Identify Express Company

🔢 Tracking Number: XXXXXXXXXXXX
💡 Hint: Could not automatically identify the logistics company for this number

Please manually select the express company or verify the tracking number:
• SF Express
• YTO Express
• ZTO Express
• Yunda Express
• STO Express
• China Post EMS
• JD Logistics
• Debang Express
• Other
```

### Query Failed Response

```
❌ Query Failed

🔢 Tracking Number: XXXXXXXXXXXX
🏢 Express Company: XXX

Possible Reasons:
• Tracking number does not exist or has expired
• Express company system under maintenance
• Tracking information not yet uploaded

💡 Suggestion: Please try again later, or contact sender to verify the number
```

## Express Company Codes Reference

```
SF    - SF Express
YTO   - YTO Express
ZTO   - ZTO Express
YD    - Yunda Express
STO   - STO Express
EMS   - China Post EMS
JD    - JD Logistics
DB    - Debang Express
JTSD  - J&T Express
ZBKY  - ZTO Freight
```

## Error Handling

| Error Type | Handling |
|-----------|----------|
| Invalid number format | Prompt user to check number format |
| Unsupported company | Provide manual selection options |
| API call failed | Prompt user to try again later |
| Number does not exist | Explain possible reasons and suggest verification |

## Usage Examples

**User Input**:
```
Track this package for me: SF1234567890123
```

**Execution Flow**:
1. Identify number: SF prefix → SF Express
2. Call SF Express API for query
3. Format and return logistics information

**Expected Output**:
Complete logistics tracking information (as format above)

## Technical Implementation

- **API-First**: Prioritize reliable APIs like Juhe Data, Kuaidi100
- **Fallback Strategy**: Return friendly prompt when API unavailable
- **Caching**: Avoid repeated queries for same number within short period
- **Timeout Handling**: API response timeout set to 10 seconds
