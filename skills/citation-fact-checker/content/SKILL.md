---
name: citation-fact-checker
description: Verify the authenticity and reliability of cited references in academic papers. Use when users ask to verify citations, check literature authenticity, validate DOIs, verify journal/conference information, confirm author information, check publication year, or validate citation format compliance.
---

# Citation Fact-Checker Skill

## Overview

This skill verifies the authenticity and reliability of cited references in academic papers through multiple channels, helping users identify fake citations, incorrect references, or suspicious literature.

## Verification Dimensions

### 1. DOI Verification
- Parse DOI identifiers from citations
- Verify DOI authenticity via CrossRef API
- Cross-check DOI-title matching

### 2. Basic Information Verification
- **Journal/Conference**: Verify journal name, ISSN, publisher
- **Author Information**: Check author names, affiliations
- **Publication Year**: Verify publication timing (should be before paper publication)
- **Volume/Issue/Pages**: Validate format

### 3. Citation Format Compliance
- Check if citation format meets target journal/conference requirements
- Identify common format errors
- Verify reference list completeness

### 4. Citation Consistency and Completeness
- Match in-text citations with reference list
- Identify unreferenced entries
- Check citation count consistency

## Workflow

```
User Input Citation
       │
       ▼
┌──────────────────┐
│ DOI Parse & Verify│ ← CrossRef API Query
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Info Extraction  │ ← Title, Authors, Journal, Year
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Multi-dimension   │ ← Journal DB, Academic Search
│ Verification      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Report Generation │ ← Flagged Issues, Confidence
└──────────────────┘
```

## Usage

### Basic Usage
Users provide citation information to verify (can be):
- DOI identifier
- Full citation text
- BibTeX entry
- Partial info (title + author)

### Output Format
Returns structured verification report including:
- **Status**: Pass / Warning / Fail
- **Confidence Score**: 0-100%
- **Issue Details**: Specific concerns with suggestions
- **Verification Evidence**: API query citations

## Verification Strategy

### Priority Rules
1. **DOI First**: Papers with DOI verified via DOI lookup
2. **Fuzzy Match**: Without DOI, query by title + author + year
3. **Cross-DB Verification**: Use multiple academic databases when needed

### Confidence Assessment
- **High (80-100%)**: DOI verified + complete info match
- **Medium (50-79%)**: Partial match, requires manual review
- **Low (0-49%)**: Critical info missing or contradictory

## Data Sources

- **CrossRef API**: DOI lookup and metadata
- **OpenAlex**: Academic papers and citation data
- **Semantic Scholar**: Paper metadata and abstracts
- **PubMed**: Biomedical literature verification
- **arXiv**: Preprint verification

## Limitations

- This skill is an auxiliary tool, not a substitute for manual review
- Some historical texts and grey literature may not be fully verifiable
- Results based on public databases may have delays

## Example

**Input**:
```
Smith, J. et al. (2023). A Novel Approach to Machine Learning. Nature, 123(4), 567-580. DOI: 10.1038/s41586-023-01234-5
```

**Output**:
```
✓ DOI Verified
✓ Journal Info Matched (Nature)
✓ Author Count Verified (matches claim)
✓ Publication Year Reasonable
⚠ Recommend checking page format

Confidence: 92%
```
