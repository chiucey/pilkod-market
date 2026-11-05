# Cache System

## Directory Structure

```
C:\Users\Jinpeng Wang\Desktop\.sisyphus\cache\
├── skill_nameA\
│   ├── <hash1>.json
│   └── <hash2>.json
├── skill_nameB\
│   └── <hash.json>
└── manifest.json
```

## Cache Entry Format

```json
{
  "query": "original user request",
  "query_hash": "semantic hash",
  "result_summary": "brief summary of result",
  "result_full": "path to full result if large",
  "timestamp": "ISO 8601",
  "skill_used": "skill name",
  "ttl_hours": 24
}
```

## Cache Key Generation

Use semantic hashing:

```python
import hashlib
import re

def normalize_query(query):
    # Remove extra whitespace
    query = re.sub(r'\s+', ' ', query.strip())
    # Lowercase for consistency
    query = query.lower()
    # Remove common variations
    query = query.replace('please ', '').replace('could you ', '')
    return query

def get_cache_key(query):
    normalized = normalize_query(query)
    # Use MD5 for speed (collision risk acceptable for local cache)
    return hashlib.md5(normalized.encode()).hexdigest()[:12]
```

## Cache Lookup Flow

1. Generate hash from query
2. Check `cache/<skill>/<hash>.json` exists
3. If exists and not expired → return cached result
4. If expired → treat as miss

## Cache Invalidation

- Manual: Delete specific entry
- TTL-based: Default 24 hours
- Force refresh: User explicitly asks

## Manifest

`manifest.json` tracks all cached entries:

```json
{
  "last_updated": "2024-01-01T00:00:00Z",
  "total_entries": 42,
  "skills": {
    "pdf": 15,
    "xlsx": 20,
    "docx": 7
  }
}
```