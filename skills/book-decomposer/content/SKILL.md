---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 279c009d3b2cefc3357793eacd94be52
    PropagateID: 279c009d3b2cefc3357793eacd94be52
    ReservedCode1: 3046022100bad0ad0aa733133844820e817b4638bf14299e464fdabcf75890bc4811d4a169022100bcda39ebb4cfb8663bc411351eb181f147523db0e61610ec84d2e7b33bd46fe3
    ReservedCode2: 3046022100dbc00cc5d73694a4863d0f29e80a501318acbac5eab9066c0c346209e7f8c0c9022100d40a019163fa65390bf2f698f3712ae51ec390a518f3224d329e260350282490
---

# 拆书博主

Break down book content into short video knowledge blocks.

## Trigger Input (3 ways)

1. Paste text directly → `/book-decomposer` + paste book content
2. File path → `/book-decomposer /path/to/book-notes.md`
3. URL → `/book-decomposer https://zhuanlan.zhihu.com/p/xxxxx`

## Workflow

### Step 0: Input Detection

| Input Type | Detection | Action |
|------------|-----------|--------|
| Text content | Complete paragraphs exist | Process directly |
| File path | Starts with `/` or `~`, contains `.md/.pdf/.txt/.epub` | Read file |
| URL | Starts with `http://` or `https://` | Extract from website |
| Empty | No content or just book title | Request paste |

### Step 1: Objective Book Extraction

#### Author Core Viewpoints
Summarize 3-5 core points, one sentence each.

#### Key Quotes
Extract 3-5 most important quotes verbatim.

#### Insights
Extract 2-4 shareable hook sentences + support + source.

#### Personal Mapping (only if identity provided)
Map viewpoints to user's life: direct connection + counter-intuitive shock + actionable direction.

### Step 2: Recommended Video Clips

Select 2-4 best clips, each with format:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Clip N/N
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hook (One-liner)
A quotable statement with a twist.

Why Worth Telling
What makes this powerful? What's counter-intuitive?

Common Pain Point
What mistakes or anxieties do people have? Be specific.

Solution
What's the fix? Show: old way → new way.

Key Quote
> Direct quote from the book.
```

## Key Rules

- One insight per clip
- Hook must have a twist/reversal
- Quality over quantity - don't pad for numbers
- Start directly with results, no fluff