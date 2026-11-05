---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502200b1662a0ca0a01db77dcac02bea8575a9755294074b32f1925e11aadc1fb70f4022100be5e561d57c93393b71c22b4a2a6c5f27a669a2a5156e15cbd85afa9f28901a3
    ReservedCode2: 30450220336569a7fb908365bcc6747fb2ab589a83e935b734157611dcb393341114e022022100975742029701df27583b999f0cd55f110caf711edfddbded348ab2fed0c136d5
description: 搜索国资资料库中的归档文档，支持关键词搜索、标签过滤和分类导航。当用户要求搜索归档文件、查询数据库文档、过滤标签浏览、分类查找文件时使用。
name: file-search-retrieve
---

# file-search-retrieve - State-Owned Asset Archive Search Skill

## Overview

Search archived documents in the state-owned asset management database by keywords, tags, and categories. Provides Web UI and command-line interface with direct file opening support.

## Directory Structure

```
file-search-retrieve/
├── SKILL.md
├── _meta.json
├── app.py                      # Flask Web service
├── build_index.py              # Index builder
├── config.py                   # Configuration
├── requirements.txt
├── templates/
│   └── index.html              # Web frontend
└── references/
    └── search-examples.md       # Usage examples
```

## Quick Start

### Prerequisites

1. Run Skill 1 (archive-manager) to create database structure
2. Run Skill 2 (archive-processor) to archive files to database
3. Database file: `data/file_meta.db`

### Start Service

```bash
cd /workspace/temp-skills/file-search-retrieve
pip install -r requirements.txt
python app.py
```

Service starts at `http://127.0.0.1:5050`, browser auto-opens.

## Core Features

### 1. Keyword Search
- Search in file names and content (first 5000 chars)
- Whoosh full-text index with fuzzy matching
- Search result highlighting

### 2. Tag Filtering
- AND logic for multiple tags
- Hot tags display (top 20 by usage)
- Click to add/remove filters

### 3. Category Filtering
- Filter by secondary category codes
- Category tree consistent with Skill 1
- Expand/collapse category hierarchy

### 4. File Opening
- Click filename to open with system default app
- Windows: `os.startfile`
- macOS: `open`
- Linux: `xdg-open`
- Supports UNC paths and mapped drives

## API Endpoints

| Endpoint | Method | Parameters | Description |
|----------|--------|-------------|-------------|
| `/api/search` | GET | `q`, `tags`, `categories`, `page`, `limit` | Search files |
| `/api/hot_tags` | GET | - | Get hot tags |
| `/api/categories` | GET | - | Get category tree |
| `/api/open` | GET | `path` | Open file |

### Response Formats

**Search Results**
```json
{
  "success": true,
  "total": 100,
  "page": 1,
  "limit": 20,
  "results": [{
    "id": "file_001",
    "file_name": "14th Five-Year Plan.pdf",
    "file_path": "\\\\server\\archive\\C\\C01\\file.pdf",
    "category1": "C",
    "category2": "C01",
    "category_path": "C_Strategic Planning/C01_Five-Year Plan",
    "tags": ["#14thFiveYear", "#Strategic"],
    "processed_time": "2026-04-20 10:30",
    "highlight": "...matching <em>keyword</em> snippet..."
  }]
}
```

**Hot Tags**
```json
{
  "success": true,
  "hot_tags": [
    { "name": "#14thFiveYearPlan", "count": 23 },
    { "name": "#SOEReform", "count": 18 }
  ]
}
```

## Integration with Skill 2

### Incremental Index Updates

After archiving new files, Skill 2 calls these endpoints:

```python
import requests

# Add new file
requests.post("http://127.0.0.1:5050/api/index/add", json={
    "id": "file_xxx",
    "file_name": "Document.pdf",
    "file_path": "/path/to/file.pdf",
    "content": "File content (first 5000 chars)...",
    "tags": ["#Tag1", "#Tag2"],
    "category1": "C",
    "category2": "C01"
})

# Update file
requests.put("http://127.0.0.1:5050/api/index/update", json={...})

# Delete file
requests.delete("http://127.0.0.1:5050/api/index/delete", json={"id": "file_xxx"})
```

### Scheduled Sync

To periodically sync new database records, start with `--rebuild`:

```bash
python app.py --rebuild
```

## Database Schema

Dependent on Skill 2's `files` table:

```sql
CREATE TABLE files (
    id TEXT PRIMARY KEY,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    category1 TEXT,
    category2 TEXT,
    tags TEXT,           -- JSON array string
    content TEXT,        -- First 5000 chars
    processed_time TEXT
);
```

## Category Structure

Consistent with Skill 1:

| Category 1 | Category 2 Code | Category 2 Name |
|------------|-----------------|-----------------|
| A_General Management | A01 | General Affairs |
| A_General Management | A02 | Admin Services |
| B_HR Management | B01 | Org Structure |
| B_HR Management | B02 | Personnel |
| C_Strategic Planning | C01 | Five-Year Plan |
| C_Strategic Planning | C02 | Reform & Restructuring |
| D_Finance | D01 | Budget |
| D_Finance | D02 | Treasury |
| E_Compliance & Risk | E01 | Risk Management |
| E_Compliance & Risk | E02 | Internal Audit |
| F_IT | F01 | IT Planning |
| F_IT | F02 | System Development |

## Path Compatibility

### Windows Support
- Local: `C:\archive\file.pdf`
- UNC: `\\192.168.1.100\share\file.pdf`
- Mapped: `Z:\archive\file.pdf`

### Path Escaping
API receives URL-encoded paths, backend decodes automatically.

## Troubleshooting

### Database Not Found
```
Error: Database not found at data/file_meta.db
```
Solution: Run Skill 1 and Skill 2 first.

### Index Corruption
```bash
# Rebuild index
python build_index.py --rebuild
```

### Port In Use
Modify `PORT` in `config.py`, or:
```bash
python app.py --port 5051
```

## Reference

See <filepath>references/search-examples.md</filepath> for detailed API examples.
