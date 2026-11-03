# Suzhou Library API Reference

## System Overview

Suzhou Library uses the Interlib library management system. Web version URL: `https://reader.szlib.com`

## Search API

### Base Search URL
```
https://reader.szlib.com/opac/search
```

### GET Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| q | Search keyword | q=three-body |
| searchType | Search type | 1=title, 2=author, 3=ISBN |
| matchFlag | Match mode | 0=prefix, 1=exact, 2=fuzzy |
| library | Location filter | Specify branch |
| pageSize | Results per page | 10-100 |
| pageNo | Page number | 1, 2, 3... |

### Search Type Values
- `1`: Any word
- `2`: Title
- `3`: ISBN/ISSN
- `4`: Author
- `5`: Subject
- `6`: Classification

### Match Modes
- `0`: Prefix match
- `1`: Exact match
- `2`: Fuzzy match

## Collection Information

### Single Book Detail URL
```
https://reader.szlib.com/opac/item/{control_no}
```

### Collection Fields

| Field | Description |
|-------|-------------|
| callno | Call number |
| location | Collection location |
| barcode | Barcode |
| status | Available/Checked out |
| collcetionCount | Available count |
| totalCount | Total copies |
| dueDate | Due date (if checked out) |

## Branch List

Main branches:
- Main Library (SZLib)
- Gusu Branch
- Industrial Park Branch
- High-Tech District Branch
- Kunshan Branch
- Changshu Branch
- Zhangjiagang Branch
- Taicang Branch
- Wujiang Branch

## Response Format

System returns HTML pages. Parse these key elements:
- Search result list
- Basic book information
- Collection detail links
- Pagination controls