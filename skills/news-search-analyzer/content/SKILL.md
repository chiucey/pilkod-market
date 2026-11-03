---
name: news-search-analyzer
description: Search and analyze recent news. Use when users want to search news, analyze news events, find latest information, understand industry trends, track hot topics, or get news in specific fields. Supports multi-source news search, content extraction, key information extraction, and news summary generation.
---

# News Search Analyzer

## Core Features

This skill provides comprehensive news search and analysis capabilities:

- **Multi-source News Search**: Use web search to gather news from multiple sources
- **Deep Content Extraction**: Extract complete content from news pages
- **Key Information Identification**: Extract titles, sources, timestamps, key figures, events, etc.
- **News Summary Generation**: Automatically generate concise news summaries

## Workflow

### Step 1: News Search

Use `batch_web_search` tool for multi-source news search:

- **Search Strategy**: Use time-sensitive keyword combinations
- **Search Volume**: 8-10 results per topic
- **Source Coverage**: Prioritize authoritative news sources

```python
batch_web_search(queries=[
    {"query": "<topic keywords> latest news 2026", "num_results": 10, "data_range": "m"},
    {"query": "<topic keywords> today's headlines", "num_results": 8, "data_range": "m"}
])
```

### Step 2: Content Extraction

Use `extract_content_from_websites` tool to extract detailed news content:

- **Extraction Target**: Extract top-ranked news pages from search results
- **Extraction Content**: Full article content, publication time, source info
- **Processing Strategy**: Batch processing, maximum 10 tasks

```python
extract_content_from_websites(tasks=[
    {"url": "<news_url>", "prompt": "Extract news title, source, time, and body content", "task_name": "news_1"}
])
```

### Step 3: Information Analysis

Analyze extracted news content:

- **Key Information Extraction**: Title, source, publication time, core events
- **Topic Clustering**: Group related news articles
- **Trend Identification**: Identify news development trends

### Step 4: Result Presentation

Present analysis results in structured format:

- **News List**: News summaries sorted by time/relevance
- **Detailed Analysis**: In-depth analysis of key news
- **Source Attribution**: All information points must cite sources

## Trigger Scenarios

| User Request | Trigger Action |
|--------------|----------------|
| "Search for news about XXX" | Execute news search + content extraction |
| "Analyze recent news about XXX" | Execute news search + deep analysis |
| "Get the latest updates on XXX" | Execute news search + summary generation |
| "Track hot topics about XXX" | Multi-round news search + trend analysis |
| "Learn about XXX industry news" | Execute news search + categorization |

## Output Format

### News Summary Format

```
## <Topic> News Overview

**Search Time**: <timestamp>
**News Count**: <number> articles
**Time Range**: <time range>

### Key News

1. **<News Title>**
   - Source: <media name>
   - Time: <publication time>
   - Summary: <2-3 sentence summary>
   - Link: <URL>

[...more news...]

### News Analysis

<Comprehensive analysis based on multiple news articles, including trends, key events, impact, etc.>
```

### Source Attribution Standard

All facts extracted from search results must be cited:

```
<citation>{{index}}</citation>
```

Where index is the number from the search result.

## Quality Standards

1. **Timeliness**: Prioritize recently published content
2. **Accuracy**: All facts must come from reliable sources
3. **Completeness**: Cover major news sources
4. **Traceability**: Provide original links for user verification
5. **Objectivity**: Present facts objectively, avoid speculation

## Error Handling

- If search fails, provide alternative search suggestions
- If content extraction fails, mark and continue processing other sources
- If safety issues are encountered, refuse extraction and log the reason

## Tool Usage Guidelines

| Tool | Purpose | Limit |
|------|---------|-------|
| batch_web_search | News search | Maximum 10 queries/call |
| extract_content_from_websites | Content extraction | Maximum 10 tasks/call |
| mcp__matrix__look_picture | Image verification | Use when necessary |

## Example Workflow

**User Request**: "Search for the latest news about artificial intelligence"

1. Search: `"artificial intelligence latest news 2026"` + `"AI technology today's headlines"`
2. Extract: Select 5-8 high-quality sources for content extraction
3. Analyze: Identify major events, trends, and impacts
4. Present: Generate structured news summary
