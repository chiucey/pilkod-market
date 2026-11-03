---
name: arxiv-paper-searcher
description: Use when users ask to search for papers on arXiv, find academic research articles, look up scholarly literature, export research papers to CSV format, or need information about specific research topics from arXiv.
---

# ArXiv Paper Searcher

Search and export academic papers from arXiv.org using the official API.

## Workflow

1. **Parse User Query**
   - Extract search keywords from user request
   - Determine result limit (default: 10, max recommended: 50)
   - Identify date range if specified
   - Confirm output file path for CSV export

2. **Execute ArXiv Search**
   - Use arXiv API: `http://export.arxiv.org/api/query`
   - Construct search query with proper format
   - Fetch results with pagination if needed

3. **Process Results**
   - Parse XML response from arXiv API
   - Extract key fields: title, authors, abstract, published date, arXiv ID, categories, PDF link

4. **Export to CSV**
   - Save results to specified CSV file
   - Include columns: arxiv_id, title, authors, abstract, published, categories, pdf_url

## Example Usage

**Request Format:**
```json
{
  "data_source_name": "arxiv",
  "api_name": "search_papers",
  "params": {
    "query": "object counting vision language",
    "max_results": 15,
    "date_from": "2023-01-01",
    "file_path": "/mnt/okcomputer/output/arxiv_counting_new.csv"
  }
}
```

## ArXiv API Details

- **Endpoint**: `http://export.arxiv.org/api/query`
- **Search Parameters**:
  - `search_query`: Keywords with optional prefixes (ti: title, au: author, abs: abstract, all: all fields)
  - `start`: Pagination offset
  - `max_results`: Maximum number of results
  - `sortBy`: relevance, lastUpdatedDate, submittedDate
  - `sortOrder`: ascending, descending
  - `datefrom`: Filter by submission date (YYYY-MM-DD format)
  - `dateto`: Filter by submission date (YYYY-MM-DD format)

## Output Format

CSV file with the following columns:
- `arxiv_id`: Unique arXiv identifier (e.g., "2301.12345")
- `title`: Paper title
- `authors`: Comma-separated author names
- `abstract`: Paper abstract text
- `published`: Publication date (YYYY-MM-DD)
- `updated`: Last updated date (YYYY-MM-DD)
- `categories`: arXiv categories
- `pdf_url`: Direct link to PDF
- `doi`: DOI if available
