---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100e861ae56c75e74029dd28740b853bac5371bffc153ea5c6640e04fd19778bf20022100910c0ac72a253dd76e6e9b509478f8d55689e1688a47516169207aff40111e42
    ReservedCode2: 3046022100efd2bb3733c00c41d87b941a56432efe2bc325fba309605be436206130d4a8f3022100b87971c473ebe894e3f7396497f403efe7f14141c0da372e916467de83dcd6e7
---

# Douyin Video Search - Technical Reference

## Douyin Platform Analysis

### Why Direct Scraping Fails

| Issue | Technical Cause | Result |
|-------|-----------------|--------|
| Empty HTML Response | Server-side rendering returns minimal HTML | `curl_only` mode extracts nothing |
| JS-Rendered Content | React/Vue SPA architecture | Content loads after JS execution |
| Auth Required | Personalized content behind login | Engagement metrics inaccessible |
| DRM Protected | Video streams encrypted | Cannot download/stream video |

### Douyin Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Douyin Architecture                  │
├─────────────────────────────────────────────────────┤
│  Browser → HTML Shell (fast, minimal)               │
│         → JS Bundle Load                            │
│         → API Calls (auth-required)                  │
│         → Content Render (React)                    │
└─────────────────────────────────────────────────────┘
```

## Extraction Strategy

### Tier 1: Search Results (Most Reliable)

Web search engines cache and index Douyin content. This is the most reliable source:

```bash
# Search queries that work well
"抖音 [topic] 视频"
"douyin trending [category]"
"site:douyin.com [keyword]"
```

### Tier 2: Third-Party Aggregators

Some sites summarize Douyin content:

- 蝉妈妈 (chanmama.com) - Douyin analytics platform
- 抖查查 (douchacha.com) - Video data lookup
- 新榜 (newrank.cn) - Content ranking

### Tier 3: Browser Mode (Limited)

Even with `browser_only` mode:

- May extract partial metadata
- Engagement data still missing
- Video player content unavailable

## Data Availability Matrix

| Data Type | Search Results | Direct Page | Browser Mode |
|-----------|---------------|-------------|--------------|
| Title | ✅ Available | ⚠️ Partial | ⚠️ Partial |
| Author | ✅ Available | ❌ Hidden | ⚠️ Partial |
| Hashtags | ✅ Available | ⚠️ Partial | ⚠️ Partial |
| Views | ❌ Not indexed | ❌ Hidden | ❌ Hidden |
| Likes | ❌ Not indexed | ❌ Hidden | ❌ Hidden |
| Comments | ❌ Not indexed | ❌ Hidden | ❌ Hidden |
| Video URL | ✅ Available | ✅ Available | ✅ Available |

## Realistic Output Example

```
## Douyin Search Results: 美食教程

**Keyword**: 美食教程 抖音
**Results Source**: Web Search (2024-03-20)

### Videos Found

1. **家常菜做法大全 | 简单易学**
   作者: 美食达人小王 (implied from search)
   话题: #美食教程 #家常菜 #简单易学
   链接: https://www.douyin.com/video/xxxxx

2. **10分钟搞定早餐 | 上班族必备**
   话题: #早餐 #快手菜 #上班族
   链接: https://www.douyin.com/video/yyyyy

### ⚠️ Limitations Notice
- View counts, likes, and comments NOT available (requires login)
- Full author profiles require Douyin authentication
- Video playback requires Douyin app or website
- For detailed analytics, use 蝉妈妈 or similar platforms
```

## Recommended Workflow

```
1. User Request: "搜索抖音美食教程"
       ↓
2. batch_web_search with "抖音 美食教程"
       ↓
3. Parse search snippets for titles/authors/hashtags
       ↓
4. Present results with direct links
       ↓
5. Include limitations disclaimer
       ↓
6. User opens links manually in Douyin
```

## When Users Need More

If users request features this skill cannot provide:

| User Request | Reality | Alternative |
|--------------|---------|-------------|
| "获取播放量" | Login required | Use 蝉妈妈 |
| "抓取评论区" | Not possible | Manual viewing |
| "下载视频" | DRM protected | Screen record |
| "实时数据" | API restricted | Official partner API |
