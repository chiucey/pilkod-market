---
name: tavily-search
description: AI-optimized web search skill designed for agents. Use when users need web search with automatic noise filtering, structured results, supporting basic/deep search, news search, domain filtering, and content extraction. Perfect for daily queries, research, and fact-checking.
---

# Tavily Search

AI-optimized web search skill designed for agents, featuring automatic noise filtering and structured results.

## Overview

Tavily Search is an intelligent search API that returns well-organized, context-rich search results optimized for AI applications. It supports multiple search modes, domain filtering, and content extraction capabilities.

## Features

### Search Modes

- **Basic Search**: Fast search (1-2 seconds, consumes 1 quota)
- **Advanced Search**: Comprehensive deep search (5-10 seconds, consumes 2 quotas)

### Search Topics

- **General**: Universal content across all time periods
- **News**: Latest content from the past 7 days

### Core Capabilities

- Automatic noise filtering
- Structured search results
- AI-generated answer summaries
- Domain inclusion/exclusion filters
- Raw content extraction for deep analysis
- Related images search

## Usage

### Basic Search

```
query: "your search query"
search_depth: "basic" | "advanced"
max_results: 1-20
```

### News Search

```
query: "breaking news topic"
search_depth: "basic" | "advanced"
topic: "news"
max_results: 1-20
```

### Domain Filtering

```
query: "programming question"
include_domains: ["developer.mozilla.org", "typescriptlang.org"]
exclude_domains: ["example.com"]
```

## Configuration

### Required Environment Variables

- `TAVILY_API_KEY`: Your Tavily API key (get free at https://app.tavily.com)

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| query | string | required | Search query (supports natural language) |
| search_depth | string | "basic" | "basic" or "advanced" |
| topic | string | "general" | "general" or "news" |
| max_results | integer | 10 | Results count (1-20) |
| include_domains | array | [] | Limit search to specific domains |
| exclude_domains | array | [] | Exclude specific domains from search |
| include_answer | boolean | true | Include AI-generated answer summary |
| include_raw_content | boolean | false | Include raw page content for deep extraction |
| include_images | boolean | false | Include related image results |

## API Response

```json
{
  "results": [
    {
      "title": "Result Title",
      "url": "https://example.com",
      "content": "Result snippet...",
      "score": 0.95
    }
  ],
  "answer": "AI-generated answer summary",
  "images": ["image URLs if requested"]
}
```

## Use Cases

- Daily information queries
- Academic and market research
- Fact-checking and verification
- News monitoring and tracking
- Technical documentation search
- Competitive analysis
