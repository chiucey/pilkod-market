---
name: suzhou-library-search
description: Search Suzhou Library collection for book availability, call numbers, locations, and copy counts. Use when users need to find books, check if items are available, or look up library holdings. Keywords: Suzhou Library, book search, call number, location, available copies, library catalog.
---

# Suzhou Library Collection Search Skill

## Overview

This skill queries the Suzhou Library (szlib.com) catalog for collection information including call numbers, locations, and available copies.

## Query Workflow

### Step 1: Construct Query URL

Suzhou Library uses the Interlib system. Query URL format:
```
https://reader.szlib.com/opac/search?q={book_title}&searchType=1
```

Parameters:
- `q`: Book title to search (URL encoded)
- `searchType=1`: Title search

### Step 2: Fetch and Parse Results

Use `extract_content_from_websites` tool to access the query page and extract collection information.

### Step 3: Extract Collection Details

For each book, extract:
- **Call Number**: Shelf location code
- **Location**: Branch library or reading room
- **Barcode**: Unique book identifier
- **Status**: Available/Checked out/Reserved
- **Available**: Number of available copies
- **Total Copies**: Total collection count

## Important Notes

1. **URL Encoding**: Book titles must be UTF-8 URL encoded
2. **Branch Filter**: Can specify particular branches
3. **Match Mode**: Default is prefix matching
4. **Pagination**: Default 20 results per page

## Example Query

Searching for "Three-Body Problem" should return:
- Call Number: I247.5/3243
- Location: Suzhou Library Main Branch
- Available: 3
- Total Copies: 5