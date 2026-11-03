# PubMed Search Patterns Reference

## NCBI Entrez API Endpoints

### ESearch - Literature Search

```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
```

**Parameters**:
- `db`: Database name (pubmed)
- `term`: Search query
- `retmax`: Maximum number of results
- `retmode`: Response format (json/xml)
- `sort`: Sort order (date/relevance/author)
- `datetype`: Date type (pdat=Publication Date, edat=Entry Date)
- `reldate`: Relative date filter (e.g., "30" means within 30 days)

### EFetch - Fetch Article Details

```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi
```

**Parameters**:
- `db`: Database name
- `id`: Comma-separated PMID list
- `rettype`: Return type (abstract/medline/full)
- `retmode`: Response format (xml/json)

### ESummary - Get Summaries

```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi
```

## Common Search Patterns

### By Research Area

```
# Oncology
(cancer[Title/Abstract] OR oncology[MeSH Terms])

# Cardiovascular Disease
(cardiovascular[Title/Abstract] OR heart disease[MeSH Terms])

# Neurological Disease
(neurology[MeSH Terms] OR neurodegenerative[Title/Abstract])

# Immunology
(immunology[MeSH Terms] OR autoimmune[Title/Abstract])
```

### By Article Type

```
# Clinical Trial
clinical trial[Publication Type]

# Guideline
guideline[Publication Type] OR practice guideline[Publication Type]

# Review
review[Publication Type] OR systematic review[Publication Type]

# Case Report
case reports[Publication Type]
```

### By Journal Impact Factor (via ISSN)

```
# High Impact Journals Examples
(Nature Medicine[Journal] OR NEJM[Journal] OR Lancet Oncology[Journal])
```

### By Date Range

```
# Past 30 days
("2024-03-01"[Date - Publication] : "2024-03-31"[Date - Publication])

# Using relative date
reldate=30
```

### By Author

```
# Specific author
(Smith J[Author] OR "Smith, John"[Author])
```

### Boolean Logic Combinations

```
# AND - Both conditions must be met
(immunotherapy[Title/Abstract]) AND (lung cancer[Title/Abstract])

# OR - Either condition must be met
(cardiomyopathy[Title/Abstract] OR heart failure[Title/Abstract])

# NOT - Exclude specific condition
(stroke[Title/Abstract]) NOT (hemorrhagic[Title/Abstract])
```

## Medical Team Monitoring Templates

### Oncology Team

```
# Comprehensive Cancer Treatment
((cancer[Title/Abstract] OR oncology[MeSH Terms]))
AND (treatment[Title/Abstract] OR therapy[Title/Abstract] OR chemotherapy[Title/Abstract])
AND ("2024"[Date - Publication] : "2025"[Date - Publication])
```

### CSCO Guideline Tracking

```
# Chinese Society of Clinical Oncology Guidelines
(CSCO[Title/Abstract] OR "Chinese Society of Clinical Oncology"[MeSH Terms])
AND (guideline[Title/Abstract] OR consensus[Title/Abstract] OR recommendation[Title/Abstract])
```

### Precision Medicine

```
# Genomics and Precision Medicine
(genomics[MeSH Terms] OR precision medicine[Title/Abstract] OR "personalized medicine"[MeSH Terms])
AND (biomarker[Title/Abstract] OR "targeted therapy"[Title/Abstract])
```

### Immunotherapy

```
# Immune Checkpoint Inhibitors
(immune checkpoint inhibitor[Title/Abstract] OR PD-1[Title/Abstract] OR PD-L1[Title/Abstract])
AND (cancer[Title/Abstract] OR oncology[MeSH Terms])
```

### Biomarkers

```
# Diagnostic and Prognostic Biomarkers
(biomarker[Title/Abstract] OR "tumor marker"[Title/Abstract])
AND (diagnosis[Title/Abstract] OR prognosis[Title/Abstract] OR "predictive factor"[Title/Abstract])
```

## API Rate Limits

- **Standard users**: 1 request/second, 3000/day
- **API Key users**: 3 requests/second, 10000/day

> Recommendation: Add `time.sleep(0.34)` in scripts to comply with rate limits

## Error Handling

| HTTP Status | Meaning | Handling |
|-------------|---------|----------|
| 200 | Success | Parse response |
| 400 | Request error | Check query syntax |
| 429 | Rate limit | Wait and retry |
| 500 | Server error | Retry later |

## Related Resources

- [NCBI Entrez API Documentation](https://www.ncbi.nlm.nih.gov/home/develop/api/)
- [PubMed Search Help](https://pubmed.ncbi.nlm.nih.gov/help/)
- [MeSH Vocabulary Database](https://www.ncbi.nlm.nih.gov/mesh/)
