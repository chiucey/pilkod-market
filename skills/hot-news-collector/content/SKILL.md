---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: e04484ed03e43a90bf73dd34dc265a1c
    PropagateID: e04484ed03e43a90bf73dd34dc265a1c
    ReservedCode1: 304402206d8c03cb4357bd0cb9ab245e25544939fed0e939a442f37fe98c032d8fc74a1c02202ca800adf3b8e3d968e2766e9e9a97725dc736c8a671edb34f2414f39111a044
    ReservedCode2: 3045022008575edecbc659af8ad893c7e99a701e9beb24f90977f117695b7e84c603e30b0221008222af80e4d7bc81d23d3847994ecc9f4d5f355f355e28560af28e9159f29c51
description: 收集并整理当前热点信息。当用户要求获取最新热榜新闻、热点资讯、今日头条榜单、微博热搜、百度贴吧热搜时使用。
name: hot-news-collector
---

# 热点信息收集器

收集并整理来自多个平台的当前实时热搜数据，直接展示新闻标题、来源、分类、内容和链接。

## 支持的数据来源

1. **今日头条** - 获取今日头条热榜榜单
2. **新浪微博** - 获取微博热搜榜
3. **百度贴吧** - 获取百度贴吧热搜

## 数据获取方式

使用 Python 脚本 `scripts/hot_news_collector.py` 获取各平台实时热搜数据。

### 命令行使用

```bash
# 获取所有平台热搜
python scripts/hot_news_collector.py

# 获取指定平台
python scripts/hot_news_collector.py --platforms toutiao
python scripts/hot_news_collector.py --platforms weibo
python scripts/hot_news_collector.py --platforms tieba

# 按来源分组显示
python scripts/hot_news_collector.py --group

# 保存到指定文件
python scripts/hot_news_collector.py --output my_news.json
```

### Python API 使用

```python
from hot_news_collector import HotNewsCollector

collector = HotNewsCollector()

# 获取所有平台热搜
all_news = collector.get_all_platforms()

# 获取指定平台热搜
weibo_news = collector.get_platform("weibo")
toutiao_news = collector.get_platform("toutiao")
tieba_news = collector.get_platform("tieba")
```

## 输出格式

每条新闻包含以下信息：

| 字段 | 说明 |
|------|------|
| title | 新闻标题 |
| source | 来源平台（今日头条/新浪微博/百度贴吧）|
| category | 分类（来自各平台的原始分类）|
| content | 内容摘要 |
| hot_value | 热度值 |
| url | 原文链接 |

### JSON 数据结构

```json
{
  "timestamp": "2024-01-01 12:00:00",
  "news": [
    {
      "title": "多家银行下调存款利率",
      "source": "今日头条",
      "category": "热榜",
      "content": "多家银行下调存款利率",
      "hot_value": "11066739",
      "url": "https://..."
    },
    {
      "title": "泰国女星遭救援人员性侵拍裸照",
      "source": "新浪微博",
      "category": "热搜",
      "content": "泰国女星遭救援人员性侵拍裸照",
      "hot_value": "1485358",
      "url": "https://..."
    }
  ]
}
```

### 文本展示格式

```
======================================================================
  热点热搜数据
  更新时间: 2024-01-01 12:00:00  |  共 150 条
======================================================================

【1】多家银行下调存款利率
    来源: 今日头条  |  分类: 热榜  |  热度: 11,066,739
    内容: 多家银行下调存款利率
    链接: https://...

【2】泰国女星遭救援人员性侵拍裸照
    来源: 新浪微博  |  分类: 热搜  |  热度: 1,485,358
    内容: 泰国女星遭救援人员性侵拍裸照
    链接: https://...

【3】MyGO声优踩红线,柜子乐队要凉?
    来源: 百度贴吧  |  分类: 热帖  |  热度: 1,737,854
    内容: MyGO声优踩红线,柜子乐队要凉?
    链接: https://...
```

### 按来源分组格式

```
======================================================================
  热点热搜数据 (按来源分组)
  更新时间: 2024-01-01 12:00:00  |  共 150 条
======================================================================

【今日头条】(50 条)
--------------------------------------------------
  1. 多家银行下调存款利率
      分类: 热榜  |  热度: 11,066,739
  2. ...

【新浪微博】(50 条)
--------------------------------------------------
  1. 泰国女星遭救援人员性侵拍裸照
      分类: 热搜  |  热度: 1,485,358
  2. ...

【百度贴吧】(50 条)
--------------------------------------------------
  1. MyGO声优踩红线,柜子乐队要凉?
      分类: 热帖  |  热度: 1,737,854
  2. ...
```

## 注意事项

- 获取实时热搜数据
- 展示新闻的完整信息：标题、来源、分类、内容、链接
- 支持按来源平台筛选
- 支持按来源分组展示
- 数据获取失败时记录错误并继续获取其他平台
