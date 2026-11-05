# 数据源配置参考

## GitHub数据源

### GitHub Trending

```python
# 抓取GitHub趋势页面
TRENDING_URL = "https://github.com/trending?since=daily"

# 筛选AI相关仓库
AI_KEYWORDS = [
    "ai", "llm", "gpt", "langchain", "agent",
    "chatbot", "nlp", "machine-learning",
    "neural-network", "transformer"
]
```

### GitHub Search API

```python
# 使用GitHub API搜索
SEARCH_URL = "https://api.github.com/search/repositories"

# 搜索参数
params = {
    "q": "AI OR LLM OR agent in:name,description,readme",
    "sort": "stars",
    "order": "desc",
    "per_page": 30
}
```

### 高级搜索

```python
# 按语言筛选
"ai topic:python"

# 按时间筛选 (近7天创建)
"ai created:>2024-01-01"

# 按star增长筛选
"llm stars:>100 pushed:>2024-01-01"
```

## Hacker News数据源

### HN API

```python
HN_TOP_STORIES = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{id}.json"

# AI相关关键词
HN_AI_KEYWORDS = [
    "AI", "GPT", "LLM", "OpenAI", "Anthropic",
    "machine learning", "neural", "language model"
]
```

### HN Algolia搜索

```python
HN_SEARCH = "https://hn.algolia.com/api/v1/search"
params = {
    "query": "AI OR machine learning",
    "tags": "story",
    "numericFilters": "points>50"
}
```

## arXiv论文源

```python
ARXIV_API = "http://export.arxiv.org/api/query"

params = {
    "search_query": "cat:cs.AI OR cat:cs.CL OR cat:cs.LG",
    "start": 0,
    "max_results": 20,
    "sortBy": "submittedDate",
    "sortOrder": "descending"
}
```

## AI工具导航站

### 聚合站点

```python
SOURCES = {
    "thereisanaiforthat": "https://theresanaiforthat.com/",
    "aitools": "https://aitools.fyi/",
    "futuretools": "https://www.futuretools.io/",
    "gpts": "https://gptstore.ai/"
}
```

## 自定义数据源

### 添加新源

```python
class DataSource:
    name: str           # 数据源名称
    url: str            # 抓取URL
    keywords: list      # 匹配关键词
    min_score: int      # 最低评分阈值
    priority: int       # 优先级 (1-10)

    def fetch(self) -> list[Item]:
        """获取最新条目"""
        pass

    def parse(self, raw) -> Item:
        """解析原始数据"""
        pass
```

### 配置示例

```python
CUSTOM_SOURCES = [
    DataSource(
        name="Cursor IDE",
        url="https://www.cursor.com/changelog",
        keywords=["ai", "code", "editor"],
        min_score=60,
        priority=8
    ),
    DataSource(
        name="Cloudflare AI",
        url="https://developers.cloudflare.com/ai-gateway/",
        keywords=["ai", "gateway", "deployment"],
        min_score=50,
        priority=7
    )
]
```

## 数据抓取最佳实践

### 频率限制

```python
import time
import requests

class RateLimitedFetcher:
    def __init__(self, calls_per_minute=30):
        self.delay = 60 / calls_per_minute
        self.last_call = 0

    def fetch(self, url):
        elapsed = time.time() - self.last_call
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

        response = requests.get(url)
        self.last_call = time.time()
        return response
```

### 缓存策略

```python
CACHE_CONFIG = {
    "github_trending": 3600,      # 1小时
    "hn_top": 1800,              # 30分钟
    "arxiv": 7200,               # 2小时
    "tool_sites": 3600           # 1小时
}
```

### 错误重试

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def fetch_with_retry(url, headers):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
```
