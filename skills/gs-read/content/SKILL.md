---
name: gs-read
description: Read and analyze academic papers from Google Scholar. Extracts full-text content from PDFs or publisher pages, provides structured summaries, key findings, and methodology analysis. Use when user wants to read, understand, or analyze a specific paper from Google Scholar.
argument-hint: "[data-cid or result number from previous search]"
---

# Google Scholar Paper Reader

Read and analyze academic papers from Google Scholar. Extracts full-text content and provides structured summaries.

## Arguments

$ARGUMENTS can be:
- A `data-cid` from a previous search result
- A result number (e.g., `3`) referring to a previous search result
- A DOI or direct paper URL

## Prerequisites

1. Use `mcp__chrome-devtools__list_pages` to find open Chrome tabs
2. Use `mcp__chrome-devtools__select_page` to select a Google Scholar tab
3. If no Google Scholar tab exists, use `gs-search` first to find the paper

## Steps

### Step 1: Get Paper Metadata

First, extract paper info from Google Scholar results page:

```javascript
async () => {
  const cid = "DATA_CID_HERE";

  // Find the result item by data-cid
  const item = document.querySelector(`.gs_r.gs_or.gs_scl[data-cid="${cid}"]`);
  if (!item) return { error: 'not_found', message: 'Paper not found on current page.' };

  const titleEl = item.querySelector('.gs_rt a');
  const title = titleEl?.textContent?.trim() || item.querySelector('.gs_rt')?.textContent?.trim() || '';
  const paperUrl = titleEl?.href || '';

  // Full-text PDF/HTML link
  const fullTextEl = item.querySelector('.gs_ggs a') || item.querySelector('.gs_or_ggsm a');
  const fullTextUrl = fullTextEl?.href || '';

  // Meta info
  const meta = item.querySelector('.gs_a')?.textContent || '';
  const parts = meta.split(' - ');
  const authors = parts[0]?.trim() || '';
  const journalYear = parts[1]?.trim() || '';

  // Extract DOI
  let doi = '';
  if (paperUrl.includes('doi.org/')) {
    doi = paperUrl.replace(/^https?:\/\/(dx\.)?doi\.org\//, '');
  }

  // Abstract snippet
  const snippet = item.querySelector('.gs_rs')?.textContent?.trim() || '';

  // Citation count
  const citedByEl = item.querySelector('.gs_fl a[href*="cites"]');
  const citedBy = citedByEl?.textContent?.match(/\d+/)?.[0] || '0';

  return {
    dataCid: cid,
    title,
    authors,
    journalYear,
    doi,
    paperUrl,
    fullTextUrl,
    snippet,
    citedBy
  };
}
```

### Step 2: Get Full Text URL

From the extracted metadata, determine the best full-text source:

| Source | Priority | How to Access |
|--------|----------|---------------|
| Direct PDF (.pdf) | 1 | Open `fullTextUrl` directly |
| Publisher HTML | 2 | Open `paperUrl` if open-access |
| DOI resolver | 3 | Open `https://doi.org/{doi}` |
| Sci-Hub fallback | 4 | Use `https://sci-hub.ru/{doi}` |

### Step 3: Extract Paper Content

**For PDF sources:**
1. Navigate to the PDF URL
2. Use `extract_pdfs_full_content` tool to extract text
3. Parse and structure the content

**For HTML/Publisher sources:**
1. Navigate to the publisher page
2. Use `extract_content_from_websites` to extract the paper content
3. Focus on: abstract, introduction, methods, results, conclusions

### Step 4: Analyze and Structure Content

After extracting content, provide a structured analysis:

```
## Paper Analysis: {title}

**Authors:** {authors}
**Source:** {journalYear}
**Citations:** {citedBy}
**DOI:** {doi}

---

### Abstract Summary
{extracted abstract or key points}

### Key Findings
1. {finding 1}
2. {finding 2}
3. {finding 3}

### Methodology
{brief description of research methods}

### Conclusions
{main conclusions and implications}

### Limitations
{any mentioned limitations}

### Related Papers
- Papers citing this: Use `/gs-cited-by {dataCid}`
- Find related work: Use `/gs-search related keywords`
```

## Example Workflows

### Workflow 1: Read a Known Paper
```
User: Read this paper: TFS2GgoGiNUJ
- Extract metadata from GS
- Find full-text URL
- Extract content
- Present structured analysis
```

### Workflow 2: Read from Search Results
```
User: Read result #3 from the previous search
- Locate result #3 on current page
- Extract data-cid and URLs
- Get full-text
- Present analysis
```

### Workflow 3: Read by DOI
```
User: Read paper with DOI 10.1038/nature12373
- Navigate to doi.org/10.1038/nature12373
- Extract content
- Present analysis
```

## Content Extraction Prompts

### For PDF Extraction
```
Extract: title, authors, abstract, key findings, methodology, conclusions, references count
```

### For Website Extraction
```
Extract the full paper content including: title, authors, abstract, introduction, methods, results, discussion, conclusions, and references. Focus on extracting all substantive text content.
```

## Error Handling

| Error | Solution |
|-------|----------|
| Paper not on page | Re-run `gs-search` to find the paper |
| No full-text available | Offer DOI and Sci-Hub alternatives |
| Paywall blocked | Suggest using `gs-fulltext` for Sci-Hub link |
| CAPTCHA detected | Ask user to verify in browser |

## Notes

- This skill uses 2-4 tool calls depending on paper availability
- Always show citation count - it's Google Scholar's key metric
- Extract and present DOI when available
- Offer follow-up actions: citation tracking, related papers search, Zotero export
- Handle paywalled papers gracefully with alternative access methods
