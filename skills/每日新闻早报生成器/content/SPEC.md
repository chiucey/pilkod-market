---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100c72e1d0dedbaacfba196984e57fe2b4ca7a9dd7e50e1a71b7c9dec406159fbc802206d304b3040208c5537cae952d148befa2029f4c9261a11d23661b990ae1faf46
    ReservedCode2: 3046022100a5a29f67a547cea9efe0721212e3a3c9d1e3ec61aedc69ef41d1d6c8de96fcb2022100b0a0088e0a9fb6d195a3c9cd75fef7e02fd9870b904ce851a942bbcb84da94cc
---

# 每日新闻早报生成技能 - 项目规范

## 1. 项目概述

**项目名称**：Daily News Brief Generator  
**项目类型**：命令行工具 / Python 模块  
**核心功能**：自动收集、整理并生成格式化的每日新闻早报  
**目标用户**：需要快速了解每日要闻的个人或组织

## 2. 功能规范

### 2.1 核心功能

- **新闻源获取**：从多个新闻源获取当日重要新闻
- **内容分类整理**：将新闻按类别（国内、国际、财经、科技、体育、娱乐等）整理
- **摘要生成**：为每条新闻生成简洁的摘要
- **格式化输出**：生成美观的格式化早报，支持多种输出格式（文本、Markdown、HTML）
- **定时任务支持**：支持配置定时任务自动生成早报

### 2.2 输出格式

早报应包含以下部分：
- **日期和星期**：显示报告生成的日期
- **天气信息**（可选）：当日天气概览
- **今日要闻**：当日最重要的3-5条新闻
- **分类新闻**：
  - 国内新闻
  - 国际新闻
  - 财经新闻
  - 科技新闻
  - 体育新闻
- **历史上的今天**（可选）
- **今日名言**（可选）

### 2.3 技术架构

- **编程语言**：Python 3.8+
- **主要依赖**：
  - requests：HTTP 请求
  - feedparser：RSS 订阅解析
  - beautifulsoup4：网页解析
  - markdown：Markdown 生成
- **配置文件**：YAML 格式
- **模块化设计**：便于扩展和维护

## 3. 文件结构

```
daily_news/
├── main.py                 # 主程序入口
├── config/
│   └── settings.yaml       # 配置文件
├── modules/
│   ├── __init__.py
│   ├── news_fetcher.py     # 新闻获取模块
│   ├── news_formatter.py   # 格式化输出模块
│   └── config_loader.py    # 配置加载模块
├── templates/
│   └── news_template.md    # Markdown 模板
├── output/                  # 输出目录
├── requirements.txt         # 依赖列表
└── README.md               # 使用说明
```

## 4. 使用方式

### 4.1 命令行使用

```bash
# 生成今日早报
python main.py

# 指定输出格式
python main.py --format html

# 指定输出文件
python main.py --output custom_news.md
```

### 4.2 Python 模块使用

```python
from modules.news_fetcher import NewsFetcher
from modules.news_formatter import NewsFormatter

fetcher = NewsFetcher()
news = fetcher.get_today_news()
formatter = NewsFormatter()
report = formatter.format(news)
print(report)
```

## 5. 验收标准

- ✅ 能够从多个新闻源获取新闻
- ✅ 能够正确分类整理新闻内容
- ✅ 生成格式化的 Markdown 早报
- ✅ 生成格式化的 HTML 早报
- ✅ 支持命令行参数配置
- ✅ 配置文件易于修改和扩展
- ✅ 代码结构清晰，模块化良好
- ✅ 包含详细的使用说明
