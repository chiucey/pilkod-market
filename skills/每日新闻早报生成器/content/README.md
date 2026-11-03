---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100d1776e744bdc354bcdcbaa48b5eb8d8831793b1888fa39cfee7c3bfd6a6385dc0221008036e5ab3e08ee8f48745a25b7cd4cba50d32ee82650d93c2b2e3322eaed6c41
    ReservedCode2: 3046022100be3256cfc691d553820c8199a40141d9159ad49e5f04c23dd02f0d64d5839d0b022100921d4f22d71614226923b611b4f43c20753d6a2681fbf98e77255e2753dc7b57
---

# 每日新闻早报生成器

## 项目简介

这是一个功能强大的每日新闻早报生成工具，能够自动从多个新闻源收集当日重要新闻，按照分类整理，并生成格式化的早报输出。支持多种输出格式，包括 Markdown、HTML 和纯文本，满足不同场景的使用需求。

该工具采用模块化设计，代码结构清晰，易于扩展和维护。用户可以通过命令行快速生成早报，也可以将其作为 Python 模块集成到其他项目中。此外，工具还支持配置文件自定义，方便用户根据需要调整新闻源和输出格式。

## 核心功能

本工具具备以下核心功能：

**多源新闻获取**：支持从多个新闻源获取新闻内容，包括新浪、网易、腾讯等主流新闻网站的 RSS 订阅源。采用智能去重机制，确保新闻内容的唯一性。同时支持按发布时间排序，让用户第一时间获取最新资讯。

**智能分类整理**：自动将新闻按类别整理，包括国内新闻、国际新闻、财经新闻、科技新闻、体育新闻等多个分类。每个分类的新闻数量可配置，避免信息过载。分类逻辑清晰，用户可以快速定位感兴趣的新闻内容。

**多格式输出**：支持三种输出格式——Markdown 格式适合阅读和笔记整理，HTML 格式适合网页展示，纯文本格式适合终端查看。用户可以根据实际需求选择最适合的输出格式。

**命令行支持**：提供完整的命令行接口，支持多种参数配置，包括输出格式、输出文件、配置文件路径等。配合定时任务工具（如 crontab），可实现每日自动生成早报。

## 安装说明

### 环境要求

使用本工具前，请确保您的系统满足以下要求：

- Python 版本：3.8 或更高版本
- 操作系统：支持 Windows、macOS、Linux 等主流操作系统
- 网络环境：需要能够访问配置的 RSS 新闻源

### 安装步骤

1. **克隆或下载项目**

   首先获取项目代码，您可以克隆 Git 仓库或直接下载项目文件到本地目录。

2. **创建虚拟环境**（推荐）

   为了避免依赖冲突，建议在虚拟环境中运行本工具。使用以下命令创建并激活虚拟环境：

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**

   进入项目目录，执行以下命令安装所需的依赖包：

   ```bash
   pip install -r requirements.txt
   ```

4. **验证安装**

   运行以下命令验证安装是否成功：

   ```bash
   python main.py --version
   ```

## 使用指南

### 命令行使用

工具提供了丰富的命令行参数，以下是常见的使用场景：

**基本用法**：运行以下命令生成今日早报，输出为 Markdown 格式：

```bash
python main.py
```

**指定输出格式**：使用 `--format` 参数指定输出格式，可选值包括 `markdown`、`html`、`text`：

```bash
python main.py --format html
```

**保存到文件**：使用 `--output` 参数将早报保存到指定文件：

```bash
python main.py --output daily_brief.md
```

**自定义配置**：使用 `--config` 参数指定自定义配置文件：

```bash
python main.py --config my_config.yaml
```

**控制可选内容**：使用 `--no-weather`、`--no-quote` 参数控制是否包含天气信息和名言：

```bash
python main.py --no-weather --no-quote
```

**查看帮助信息**：使用 `--help` 参数查看所有可用选项：

```bash
python main.py --help
```

### Python 模块调用

除了命令行使用，本工具还可以作为 Python 模块集成到其他项目中：

```python
from modules.config_loader import ConfigLoader
from modules.news_fetcher import NewsFetcher
from modules.news_formatter import NewsFormatter

# 加载配置
config_loader = ConfigLoader()
config = config_loader.load()

# 获取新闻
fetcher = NewsFetcher(config)
news_data = fetcher.get_today_news()

# 格式化输出
formatter = NewsFormatter(config)
report = formatter.format(news_data, format='markdown')

print(report)
```

## 配置说明

### 配置文件位置

默认配置文件位于 `config/settings.yaml`。您可以修改此文件来自定义新闻源和输出选项。

### 新闻源配置

在配置文件中添加或修改新闻源：

```yaml
news_sources:
  - name: "新闻源名称"
    url: "RSS订阅地址"
    category: "分类名称"
    enabled: true
```

支持的分类包括：`domestic`（国内）、`international`（国际）、`finance`（财经）、`technology`（科技）、`sports`（体育）。

### 输出选项配置

```yaml
output:
  format: "markdown"              # 输出格式
  include_weather: true          # 包含天气信息
  include_quote: true            # 包含今日名言
  include_history: true          # 包含历史上的今天
  max_news_per_category: 10      # 每分类最多新闻数
```

## 项目结构

项目采用清晰的目录结构，便于维护和扩展：

```
daily_news_brief/
├── main.py                    # 主程序入口
├── config/
│   └── settings.yaml         # 配置文件
├── modules/
│   ├── __init__.py           # 模块初始化
│   ├── config_loader.py      # 配置加载模块
│   ├── news_fetcher.py       # 新闻获取模块
│   └── news_formatter.py     # 格式化输出模块
├── templates/                 # 模板目录
├── output/                    # 输出目录
├── requirements.txt          # 依赖列表
├── SPEC.md                   # 项目规范
├── SKILL.md                  # 技能定义
└── README.md                 # 使用说明
```

## 技术栈

本工具使用以下技术：

- **Python 3.8+**：主要编程语言
- **feedparser**：RSS 订阅解析
- **requests**：HTTP 请求处理
- **beautifulsoup4**：HTML 内容解析
- **PyYAML**：配置文件解析

## 常见问题

**Q：新闻获取失败怎么办？**

A：请检查网络连接是否正常，以及配置的 RSS 链接是否有效。部分新闻源可能存在访问限制，建议更换其他新闻源。

**Q：如何添加自定义新闻源？**

A：在配置文件的 `news_sources` 部分添加新的新闻源配置即可。确保提供有效的 RSS 订阅地址。

**Q：如何实现定时自动生成？**

A：在 Linux/macOS 系统中，可以使用 crontab 实现定时任务。例如，每天早上 8 点生成早报：

```bash
0 8 * * * /usr/bin/python3 /path/to/main.py --output /path/to/daily_brief.md
```

## 更新日志

### v1.0.0（当前版本）

- 实现多源新闻获取功能
- 支持 Markdown、HTML、纯文本三种输出格式
- 提供完整的命令行接口
- 支持配置文件自定义
- 包含天气信息、历史上的今天、名言等附加内容

## 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 项目主页：查看 GitHub 仓库
- 问题反馈：提交 Issue

## 许可证

本项目采用 MIT 许可证，您可以自由使用、修改和分发本项目的代码。
