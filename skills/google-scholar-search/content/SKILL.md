---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502203d4e592f8c71c039da4348ae2eafa436a45849800720f173a1b25f8c05f12aab022100b2ef84c7c2e47b47fb008d06586bf6bd1d012e255c0822d4732272ad6e99c1bd
    ReservedCode2: 3045022100b59c64b2ad185087c8b9439d8273145221563ce6cc6b81520dd5763377ee722b022042cc7e333c68e3659c73c5b9fcdf941d2629f60f03e92ae22be3c8c1cb671fdd
description: Search Google Scholar for academic literature and research papers. Use when users ask to search academic papers, research articles, find scholarly materials, look up citations, or need academic research data. Supports year range filtering, result count control, and language settings.
name: google-scholar-search
---

# Google Scholar Search Skill

Search Google Scholar for academic literature and research materials.

## Core Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | Yes | Search keywords/query string |
| num_results | integer | No | Number of results to return, default 10 |
| start_year | integer | No | Filter start year |
| end_year | integer | No | Filter end year |
| file_path | string | No | CSV file save path |
| hl | string | No | Interface language, e.g., "en", "zh-CN" |

## Output Format

Returns CSV file with the following fields:
- title: Paper title
- url: Paper link
- authors: Authors
- publication: Publication/Journal
- year: Publication year
- citations: Citation count
- abstract: Abstract

## Execution Flow

1. Receive search parameters
2. Build Google Scholar search URL
3. Extract search results
4. Save to CSV file (if path specified)

## Usage Example

```
Search query: "machine learning optimization"
num_results: 20
start_year: 2023
end_year: 2026
hl: "en"
```
