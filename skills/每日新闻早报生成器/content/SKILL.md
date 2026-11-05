---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3044022059db81421c97912e7adeda57eecc63655c1a8d4b988d83d691c6d79c4dbffad50220121db11f72aee70d105d96498e641af18d328da181c530ea6e0c2b12c41804c8
    ReservedCode2: 3046022100f18c176064f06e50abf5daaf1b916ce067119754f5843fb558cef20e0cea9912022100d24b40125620d00dc6f6f900e54694b64feea80b5d09dcb72152bdf7de0a2e5d
author: MiniMax Agent
description: 自动收集、整理并生成格式化的每日新闻早报，支持多种输出格式
features:
    - 多新闻源获取
    - 智能分类整理
    - 多格式输出
    - 命令行支持
    - 定时任务支持
name: 每日新闻早报生成器
tags:
    - 新闻
    - 早报
    - 自动化
    - 信息聚合
version: 1.0.0
---

# 每日新闻早报生成器

## 技能简介

每日新闻早报生成器是一个自动化工具，能够从多个新闻源收集当日重要新闻，按照类别整理，并生成格式化的早报输出。

## 核心功能

### 1. 新闻获取
- 支持多个新闻源的RSS订阅
- 自动去重和筛选
- 按时间排序

### 2. 内容分类
- **国内新闻**：国内重要时政、民生资讯
- **国际新闻**：国际重大事件
- **财经新闻**：股市、经济动态
- **科技新闻**：科技行业资讯
- **体育新闻**：体育赛事报道

### 3. 输出格式
- **Markdown格式**：适合阅读和笔记
- **HTML格式**：适合网页展示
- **纯文本格式**：适合终端查看

## 使用方法

### 命令行使用

```bash
# 生成今日早报（默认Markdown格式）
python main.py

# 生成HTML格式早报
python main.py --format html

# 指定输出文件
python main.py --output my_daily_brief.md

# 获取帮助信息
python main.py --help
```

### 模块调用

```python
from modules.news_fetcher import NewsFetcher
from modules.news_formatter import NewsFormatter

# 获取新闻
fetcher = NewsFetcher()
news = fetcher.get_today_news()

# 格式化输出
formatter = NewsFormatter()
report = formatter.format(news, format='markdown')
print(report)
```

## 配置说明

编辑 `config/settings.yaml` 文件修改新闻源和其他配置：

```yaml
news_sources:
  - name: "国内要闻"
    url: "https://example.com/rss.xml"
    category: "domestic"
  
  - name: "国际新闻"
    url: "https://example.com/world.xml"
    category: "international"

output:
  format: "markdown"
  include_weather: true
  include_quote: true
```

## 技术架构

- **语言**：Python 3.8+
- **依赖库**：
  - `requests`：HTTP请求
  - `feedparser`：RSS解析
  - `beautifulsoup4`：网页解析
  - `pyyaml`：配置管理

## 文件结构

```
daily_news/
├── main.py                 # 主程序
├── config/
│   └── settings.yaml       # 配置文件
├── modules/
│   ├── news_fetcher.py     # 新闻获取
│   ├── news_formatter.py   # 格式化输出
│   └── config_loader.py    # 配置加载
├── templates/
│   └── news_template.md    # 模板文件
└── output/                 # 输出目录
```

## 注意事项

1. 确保网络连接正常
2. 定期更新新闻源配置
3. 检查输出目录权限
4. 根据需要调整新闻源数量
