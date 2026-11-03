---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 30460221009fc4db564b823d3469b7a83526ea8111ef7eee6a8da2257fc1cadf19087c43c60221008006ce6e956a6413f3f94d108d61eba8c875f5e5b830942b7600460f400728bb
    ReservedCode2: 304502210096db71f2c15ea135037760560f2a828f7bb24339c3af9b439c5e452e5ba04ad502207d861fab28d3604d91ba40ae0756609b600f164ed4b64596a29d6ddb8e281004
---

# Douyin Skill Error Codes Reference

## Error Code Taxonomy

### Category 1: Search Errors
| Code | Name | Severity | Auto-Recoverable |
|------|------|----------|------------------|
| `SEARCH_NO_RESULTS` | No Results Found | Medium | Yes |
| `SEARCH_BLOCKED` | Keyword Blocked | High | Partial |
| `SEARCH_TIMEOUT` | Search Timeout | Medium | Yes |
| `SEARCH_RATE_LIMIT` | Rate Limited | High | Yes |

### Category 2: Extraction Errors
| Code | Name | Severity | Auto-Recoverable |
|------|------|----------|------------------|
| `EXTRACT_LOGIN_REQUIRED` | Login Required | Medium | No |
| `EXTRACT_DYNAMIC_EMPTY` | Empty Dynamic Content | High | Partial |
| `EXTRACT_NOT_EXIST` | Content Not Exist | Medium | No |
| `EXTRACT_TIMEOUT` | Extraction Timeout | Medium | Yes |
| `EXTRACT_BLOCKED` | Extraction Blocked | High | No |

### Category 3: Workflow Errors
| Code | Name | Severity | Auto-Recoverable |
|------|------|----------|------------------|
| `URL_TYPE_UNKNOWN` | Unknown URL Type | Low | Yes |
| `WORKFLOW_AMBIGUOUS` | Ambiguous Workflow | Low | Yes |
| `TOOL_DENIED` | Tool Access Denied | High | No |

---

## Detailed Error Specifications

### SEARCH_NO_RESULTS

**Trigger**: `batch_web_search` returns 0 results for all query variants

**Root Causes**:
1. Search engine doesn't index Douyin content well
2. Keyword too specific or niche
3. Content is new (not yet indexed)
4. Content removed from search engines

**Detection Logic**:
```javascript
if (searchResults.length === 0) {
    return {
        code: "SEARCH_NO_RESULTS",
        message: "未找到相关抖音内容",
        suggestions: [
            "尝试更通用的关键词",
            "使用中文关键词而非英文",
            "尝试同义词或相关话题"
        ]
    };
}
```

**Recovery Strategies**:
1. Try alternative query formats (Chinese, English, site: filter)
2. Extract from user's partial URL
3. Return partial success with available info

---

### SEARCH_BLOCKED

**Trigger**: `batch_web_search` returns filtered/blocked results

**Root Causes**:
1. Keyword contains sensitive terms
2. Content policy filtering
3. Regional restrictions

**Detection Logic**:
```javascript
if (result.filtered === true || result.count < expected) {
    return {
        code: "SEARCH_BLOCKED",
        message: "部分搜索结果被过滤",
        safeResults: result.items,
        blockedCount: result.blockedCount
    };
}
```

**Recovery Strategies**:
1. Sanitize query to remove sensitive terms
2. Use broader, safer keywords
3. Fall back to alternative sources

---

### EXTRACT_LOGIN_REQUIRED

**Trigger**: Engagement data (views, likes, comments) missing from extraction

**Root Causes**:
1. Douyin requires login for engagement metrics
2. User not logged in to Douyin
3. Session expired

**Detection Logic**:
```javascript
const hasEngagementData =
    result.views && result.views !== "[需要登录]" &&
    result.likes && result.likes !== "[需要登录]";

if (!hasEngagementData && result.title) {
    return {
        code: "EXTRACT_LOGIN_REQUIRED",
        availableFields: {
            title: result.title,
            author: result.author,
            hashtags: result.hashtags
        },
        missingFields: {
            views: result.views || "[需要登录]",
            likes: result.likes || "[需要登录]",
            comments: result.comments || "[需要登录]"
        }
    };
}
```

**Recovery Strategies**:
1. Return partial data with clear indicators
2. Suggest QR code login for full access
3. Offer to extract creator profile instead

---

### EXTRACT_DYNAMIC_EMPTY

**Trigger**: Page content is mostly empty HTML without JS-rendered content

**Root Causes**:
1. `browser_only` mode not working properly
2. Page uses advanced JS rendering
3. Network timeout before content loads

**Detection Logic**:
```javascript
const hasMinimalContent =
    result.html && result.html.length < 1000 &&
    !result.html.includes('video') &&
    !result.html.includes('title');

if (hasMinimalContent) {
    return {
        code: "EXTRACT_DYNAMIC_EMPTY",
        message: "页面内容未完整加载",
        suggestions: [
            "等待更长时间让JS渲染完成",
            "检查网络连接",
            "使用二维码登录态尝试"
        ]
    };
}
```

**Recovery Strategies**:
1. Retry with longer wait time
2. Try alternative extraction approach
3. Use search results as fallback

---

### EXTRACT_NOT_EXIST

**Trigger**: Page shows "video not exist" or equivalent message

**Root Causes**:
1. Video deleted by author
2. Video set to private
3. Video requires login to view
4. Invalid URL

**Detection Logic**:
```javascript
const notExistPhrases = [
    "视频不存在",
    "视频已删除",
    "作品已下架",
    "该视频仅对",
    "video not exist",
    "this video is unavailable"
];

const isNotExist = notExistPhrases.some(phrase =>
    result.text && result.text.includes(phrase)
);

if (isNotExist) {
    return {
        code: "EXTRACT_NOT_EXIST",
        message: "视频不存在或已被删除",
        possibleReasons: [
            "视频作者已删除该视频",
            "视频设为私密",
            "视频仅对特定用户可见",
            "需要登录才能查看"
        ]
    };
}
```

**Recovery Strategies**:
1. Report clearly that content not accessible
2. Distinguish between deleted/private/login-required
3. No fallback possible - content genuinely unavailable

---

### URL_TYPE_UNKNOWN

**Trigger**: Cannot determine URL type from pattern

**Root Causes**:
1. Non-standard URL format
2. Short URL not expanded
3. New URL pattern not recognized

**Detection Logic**:
```javascript
function detectUrlType(url) {
    // ... detection logic
    // If no pattern matches
    return 'unknown';
}

if (result.type === 'unknown') {
    return {
        code: "URL_TYPE_UNKNOWN",
        message: "无法识别的链接类型",
        suggestions: [
            "请提供完整的抖音链接",
            "或描述您想查看的内容类型"
        ]
    };
}
```

**Recovery Strategies**:
1. Try multiple extraction strategies
2. Treat as search query
3. Ask user for clarification

---

### WORKFLOW_AMBIGUOUS

**Trigger**: Multiple possible workflows, unclear which to use

**Root Causes**:
1. User request vague
2. Both URL and keyword provided
3. Multiple URL types in input

**Resolution Logic**:
```javascript
if (hasUrl && hasKeyword) {
    // Prefer URL extraction
    return extractFromUrl(url);
}

if (!hasUrl && !hasKeyword) {
    return {
        code: "WORKFLOW_AMBIGUOUS",
        message: "请提供抖音链接或搜索关键词",
        examples: {
            url: "https://www.douyin.com/video/...",
            keyword: "美食教程"
        }
    };
}
```

**Recovery Strategies**:
1. Establish clear priority (URL > Keyword)
2. Ask user to clarify ambiguous requests
3. Use decision tree to resolve

---

### TOOL_DENIED

**Trigger**: Tool access blocked by configuration

**Root Causes**:
1. `openclaw.json` restricts `web_search` or `web_fetch`
2. Tool not available in current environment
3. Permission issues

**Detection Logic**:
```javascript
try {
    await batch_web_search({ queries: [...] });
} catch (error) {
    if (error.code === 'TOOL_DENIED' || error.message.includes('denied')) {
        return {
            code: "TOOL_DENIED",
            message: "搜索工具被禁用",
            suggestions: [
                "检查 openclaw.json 配置",
                "使用替代工具"
            ]
        };
    }
}
```

**Recovery Strategies**:
1. Use alternative extraction method
2. Inform user of configuration issue
3. Provide manual instructions

---

## Error Response Templates

### Partial Success Template
```javascript
{
    success: true,
    partial: true,
    error: {
        code: "EXTRACT_LOGIN_REQUIRED",
        message: "部分数据需要登录才能查看"
    },
    data: {
        title: "...",
        author: "...",
        hashtags: [...]
    },
    missing: {
        views: "[需要登录]",
        likes: "[需要登录]"
    },
    suggestions: [
        "登录后可获取完整数据"
    ]
}
```

### Full Failure Template
```javascript
{
    success: false,
    error: {
        code: "EXTRACT_NOT_EXIST",
        message: "视频不存在或已被删除",
        details: "...",
        possibleReasons: [
            "..."
        ],
        suggestions: [
            "..."
        ]
    }
}
```

---

## User-Facing Messages

| Code | Chinese Message | English Message |
|------|----------------|-----------------|
| `SEARCH_NO_RESULTS` | 未找到相关视频，请尝试其他关键词 | No results found, try different keywords |
| `SEARCH_BLOCKED` | 部分搜索结果被过滤，请调整关键词 | Some results filtered, please adjust keywords |
| `EXTRACT_LOGIN_REQUIRED` | 查看完整数据需要登录抖音账号 | Login required to view complete data |
| `EXTRACT_DYNAMIC_EMPTY` | 页面加载超时，请稍后重试 | Page load timeout, please retry |
| `EXTRACT_NOT_EXIST` | 视频不存在、已删除或设为私密 | Video not found, deleted, or private |
| `URL_TYPE_UNKNOWN` | 无法识别的链接，请提供完整的抖音链接 | Unrecognized link, please provide full Douyin URL |
| `WORKFLOW_AMBIGUOUS` | 请提供抖音链接或描述您想找的内容 | Please provide a Douyin URL or describe what you're looking for |
| `TOOL_DENIED` | 搜索功能暂时不可用 | Search feature temporarily unavailable |
