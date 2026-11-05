---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 30450220348fb293686b429673c4d644207b910687064eb0bfc765c52efe3b2dcecfc8f20221008108f22ffc3a09c6d4a4330e7625deee57a91c843fcd3f877f9c412daa4ec226
    ReservedCode2: 304402205af7763abfce97ab80c36adf5cfaf68ea4d481eb8fb23df468b58b9ea03bb91702203ba3ed0b776e965d911652184bbaa5118553e13fd8a2edabcda7900f53fa98fc
---

# Search Examples and API Reference

## Quick Start

### Start Service

```bash
cd /workspace/temp-skills/file-search-retrieve
pip install -r requirements.txt
python app.py
```

Browser auto-opens `http://127.0.0.1:5050`

### Health Check

```bash
curl http://127.0.0.1:5050/health
```

Response:
```json
{
  "status": "healthy",
  "index_initialized": true,
  "database_exists": true
}
```

---

## Web UI Usage

### Keyword Search
1. Enter keyword in search box (e.g., "14th Five-Year")
2. Press Enter or click Search
3. Results display with keyword highlighting

### Tag Filtering
1. Click tags in Hot Tags section
2. Tags added to filter
3. Results update in real-time
4. Click X to remove filter

### Category Filtering
1. Click "Select Categories" to expand
2. Check desired secondary categories
3. Click "Apply" to search
4. Multi-select uses OR logic between categories

### Open File
1. Click filename in results
2. System default app opens the file

---

## API Examples

### Basic Search

```bash
# Keyword search
curl "http://127.0.0.1:5050/api/search?q=14thFiveYear"

# With pagination
curl "http://127.0.0.1:5050/api/search?q=plan&page=2&limit=10"
```

### Tag Filtering

```bash
# Single tag
curl "http://127.0.0.1:5050/api/search?tags=%2314thFiveYear"

# Multiple tags (AND logic)
curl "http://127.0.0.1:5050/api/search?tags=%2314thFiveYear,%23Strategic"
```

### Category Filtering

```bash
# Single category
curl "http://127.0.0.1:5050/api/search?categories=C01"

# Multiple categories
curl "http://127.0.0.1:5050/api/search?categories=C01,C02"
```

### Combined Filters

```bash
curl "http://127.0.0.1:5050/api/search?q=plan&tags=%23Strategic&categories=C01,C02&page=1&limit=20"
```

### Get Hot Tags

```bash
curl "http://127.0.0.1:5050/api/hot_tags"
```

Response:
```json
{
  "success": true,
  "hot_tags": [
    { "name": "#14thFiveYearPlan", "count": 23 },
    { "name": "#SOEReform", "count": 18 }
  ]
}
```

### Get Category Tree

```bash
curl "http://127.0.0.1:5050/api/categories"
```

### Open File

```bash
# Windows local path
curl "http://127.0.0.1:5050/api/open?path=C%3A%5Carchive%5Cfile.pdf"

# Windows UNC path
curl "http://127.0.0.1:5050/api/open?path=%5C%5C192.168.1.100%5Carchive%5Cfile.pdf"

# Linux/macOS path
curl "http://127.0.0.1:5050/api/open?path=%2Farchive%2Ffile.pdf"
```

---

## Skill 2 Integration

Skill 2 calls these endpoints after archiving files:

### Add Document

```python
import requests

requests.post("http://127.0.0.1:5050/api/index/add", json={
    "id": "file_20260420_001",
    "file_name": "14th Five-Year Plan.pdf",
    "file_path": "\\\\server\\archive\\C01\\file.pdf",
    "content": "First 5000 characters of file content...",
    "tags": ["#14thFiveYear", "#Strategic"],
    "category1": "C_Strategic Planning",
    "category2": "C01"
})
```

### Update Document

```python
requests.put("http://127.0.0.1:5050/api/index/update", json={
    "id": "file_20260420_001",
    "file_name": "14th Five-Year Plan v2.pdf",
    "content": "Updated content...",
    "tags": ["#14thFiveYear", "#Strategic", "#Updated"],
    "category1": "C_Strategic Planning",
    "category2": "C01"
})
```

### Delete Document

```python
requests.delete("http://127.0.0.1:5050/api/index/delete", json={
    "id": "file_20260420_001"
})
```

### Rebuild Index

```bash
curl -X POST "http://127.0.0.1:5050/api/index/rebuild"
```

---

## CLI Tools

### Rebuild Index

```bash
# Normal rebuild
python build_index.py

# Force rebuild
python build_index.py --rebuild
```

### Startup Options

```bash
# Custom port
python app.py --port 5051

# Rebuild on startup
python app.py --rebuild

# Bind to all interfaces
python app.py --host 0.0.0.0 --port 5050
```

---

## Search Syntax

### Whoosh Query Syntax

| Syntax | Example | Description |
|--------|---------|-------------|
| Exact phrase | `"14th Five Year"` | Exact match |
| OR search | `14th OR 13th` | Match either |
| AND search | `14th AND plan` | Match both |
| Wildcard | `14th*` | Prefix match |
| Exclude | `plan NOT finance` | Exclude term |

### Common Search Scenarios

```bash
# 1. Find all planning documents
curl "http://127.0.0.1:5050/api/search?q=plan&categories=C01"

# 2. Find audit files with risk tags
curl "http://127.0.0.1:5050/api/search?tags=%23Risk&categories=E02"

# 3. Find recent strategic cooperation files
curl "http://127.0.0.1:5050/api/search?q=strategic cooperation&tags=%23Strategic"

# 4. Find HR related general files
curl "http://127.0.0.1:5050/api/search?q=HR&categories=B01,B02"

# 5. Find all files (no filter)
curl "http://127.0.0.1:5050/api/search?q=*"
```

---

## Troubleshooting

### Database Not Found

```
Error: Database not found at data/file_meta.db
```

Solution: Run Skill 2 to archive files.

### Empty Index

```bash
python build_index.py --rebuild
```

### Cannot Open File

1. Check file path exists
2. Verify user has access permissions
3. Windows: check UNC path format

### Inaccurate Results

1. Confirm files properly archived
2. Rebuild index: `python build_index.py --rebuild`
3. Check database content

---

## Performance Tips

### Index Optimization
- Max content length: 5000 chars (configurable in `config.py`)
- Regular index rebuilds maintain query efficiency

### Query Optimization
- Use category filters to reduce scope
- Prefer hot tags
- Use pagination instead of fetching all
