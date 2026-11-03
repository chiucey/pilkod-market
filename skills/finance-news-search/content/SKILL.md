---
name: finance-news-search
description: 财经新闻搜索技能。整合财联社、证券时报、韭研公社、英为财情、东方财富等主流财经网站，一键搜索最新资讯、快讯、事件日历、市场分析。当用户提到「财经新闻」「最新利好」「市场消息」「财经快讯」或具体网站名称时激活。
---

# 财经新闻搜索

## 使用方式

```bash
uv run finance_news_search.py "AI 算力"                    # 搜索所有网站
uv run finance_news_search.py "新能源" --sites cls,stcn      # 指定网站
uv run finance_news_search.py --type telegraph              # 只看快讯
uv run finance_news_search.py "半导体" --limit 10 --json    # JSON 输出
```

## 网站代码

| 代码 | 网站 | 特点 |
|------|------|------|
| cls | 财联社 | 电报快讯、事件日历、深度报道 |
| stcn | 证券时报 | 上市公司资讯、e 公司快讯 |
| jiuyan | 韭研公社 | 题材挖掘、个股研究、热点复盘 |
| investing | 英为财情 | 全球行情、财经日历、市场分析 |
| eastmoney | 东方财富 | 综合财经门户、研报、数据 |

## 参数说明

- `keyword`: 搜索关键词（可选）
- `--sites`: 指定网站，逗号分隔，默认全部
- `--type`: 内容类型 (all/telegraph/news/calendar/research)
- `--limit`: 每站返回数量，默认 5
- `--json`: 输出 JSON 格式