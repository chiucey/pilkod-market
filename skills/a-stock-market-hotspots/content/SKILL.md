---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 29e39af5049a40fb46bb702f57b1868b
    PropagateID: 29e39af5049a40fb46bb702f57b1868b
    ReservedCode1: 3045022029b7bb6339240a2413c910a006b43ad3f70e5bdbde8f60fd11dec7f6a8d0b44f022100e63e0c9342774a211fde508b78d5bf5992b04ab19954e2da11adb38657109348
    ReservedCode2: 3046022100b3c04fde96b5a899f7a376f140b9f5973d0f81eb9a0804d9fa7c7ceeea728aec022100d884abd0679d62c02a4448308362c5c6e52bde9b9397a9ba56ae7cc7287c88a0
description: A-stock market hotspot information collection skill. Used when users need to obtain A-share market hotspot information, collect daily market news, analyze market dynamics on trading days. Executes at 8:30 AM daily to fetch key news from Jin10 and CLS Telegrap.
name: a-stock-market-hotspots
---

# A-Stock Market Hotspot Information Collection

## Trigger Conditions

Triggered when user requests:
- Collect A-stock market hotspot information
- Obtain daily market news
- Analyze market dynamics
- Trading day market updates

## Execution Flow

### Step 1: Access Information Sources

Use `extract_content_from_websites` tool to access both websites simultaneously:

1. **Jin10 Data**: https://www.jin10.com/
2. **CLS Telegrap**: https://www.cls.cn/telegraph

### Step 2: Extract Information

Extract the following content from both websites:
- News title
- Publication time (convert to yyyy-MM-dd HH:mm:ss format)
- News body content

### Step 3: Information Integration and Deduplication

1. **Merge Duplicate Messages**: If two messages are highly similar (>80% similarity), keep the newer one
2. **Message Summary**: Simplify each message to within 100 characters, preserving core information
3. **Sorting**: Sort by publication time in descending order (newest first)

### Step 4: Output Limits

- If key messages exceed 20, keep only the most critical 20
- Each message format:

```markdown
# Title
# Time (yyyy-MM-dd HH:mm:ss)
# Message Content (within 100 characters)
```

## Output Format

Final output is a structured market hotspot information report containing:

1. Report title and generation time
2. Message list (each with title, time, content)
3. If messages are merged, explain the merge reason

## Quality Requirements

- Ensure time format is unified as yyyy-MM-dd HH:mm:ss
- Message content is concise, not exceeding 100 characters
- Prioritize messages directly related to A-stock market
- Filter out entertainment/lifestyle news unrelated to markets
