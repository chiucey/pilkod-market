# MCP 工具参考

## 可用工具列表

### 1. get_top_news
获取今日最重要新闻

**输出格式**:
```json
[
  {
    "title": "新闻标题",
    "summary": "新闻摘要",
    "time": "发布时间"
  }
]
```

### 2. get_macro_news
获取宏观政策新闻

**输出格式**: 同 get_top_news

### 3. get_industry_news
获取特定行业新闻

**输入参数**:
```json
{
  "sector": "行业名称，如 tech, healthcare, energy"
}
```

**输出格式**: 同 get_top_news

## RSS 兜底实现

当 MCP 工具不可用时，可使用以下 RSS 源：

### 国内新闻源
- 人民日报: https://paper.people.com.cn/rss/rss.xml
- 新华社: http://www.xinhuanet.com/politics/news_politics.xml
- 央视新闻: http://www.cctv.com/rss/index.xml

### 财经新闻源
- 第一财经: https://www.yicai.com/rss/
- 东方财富: https://feed.eastmoney.com/
- 同花顺: https://www.10jqka.com.cn/

### 实现示例

```python
import feedparser

def get_news(url):
    feed = feedparser.parse(url)
    return [
        {
            "title": entry.title,
            "summary": entry.summary,
            "time": entry.published
        }
        for entry in feed.entries[:10]
    ]

def get_china_macro_news():
    sources = [
        "https://paper.people.com.cn/rmrb/rss.xml",
        "http://www.xinhuanet.com/politics/news_politics.xml"
    ]
    all_news = []
    for url in sources:
        all_news.extend(get_news(url))
    return all_news
```
