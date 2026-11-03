---
name: web-automation
description: 智能网页自动化解决方案，整合 Playwright 浏览器控制、browser-use LLM 交互、PaddleOCR 图像识别、MinerU 文档处理；支持浏览、交互、信息提取、OCR 识别、PDF 解析、反爬对抗；选择性安装、环境检测、统一配置管理
dependency:
  python:
    - playwright==1.58.0
    - browser-use==0.12.2
    - langchain==1.0.3
    - langchain-core==1.2.20
    - langchain-openai==1.0.1
    - langchain-anthropic==1.3.1
    - langchain-google-genai==4.2.1
    - requests==2.32.5
    - aiohttp==3.13.3
    - httpx==0.28.1
    - beautifulsoup4==4.14.3
    - lxml==6.0.2
    - PyYAML==6.0.3
    - numpy==2.4.3
    - openai==2.16.0
    - anthropic==0.76.0
    - google-genai==1.65.0
    - pydantic==2.12.5
    - pillow==12.1.0
    # 可选依赖 - OCR
    # paddleocr
    # paddlepaddle>=2.6.0
    # opencv-python
    # 可选依赖 - PDF
    # pypdf==6.6.2
    # python-docx==1.2.0
  system:
    - playwright install chromium
---

# Web Automation Skill

## 概览

本 Skill 提供智能化的网页自动化能力，整合浏览器控制、OCR 识别、文档处理等核心技术，支持复杂网页交互和数据提取场景。

**重要说明**：
- 核心功能（浏览器自动化）只需基础依赖即可使用
- OCR 和 PDF 功能为可选模块，按需安装
- 安装脚本支持选择性安装，避免依赖冲突

### 核心能力矩阵

| 能力模块 | 工作场景 | 核心功能 | 脚本 | 依赖要求 |
|---------|---------|---------|------|---------|
| **智能浏览器自动化** | AI Agent 任务执行、自然语言驱动的复杂任务 | `browser_use_agent.py` | 核心 |
| **增强版浏览器操作** | 超时优化、重试机制、反爬增强、证书处理 | `enhanced_playwright_cli.py` | 核心 |
| **页面交互** | 网页导航、元素操作 | `browser_wrapper.py` | 核心 |
| **图像识别** | 验证码/文字识别 | `ocr_service.py` | OCR（可选） |
| **增强版PDF处理** | URL下载PDF、断点续传、进度显示 | `enhanced_mineru_service.py` | PDF（可选） |
| **PDF 处理** | 文档解析、表格提取 | `mineru_service.py` | PDF（可选） |
| **文档转换** | 格式转换 | `document_converter.py` | LibreOffice（可选） |

### 整体数据流

```
用户输入 → 智能体决策 → 脚本执行 → 外部服务 → 数据输出 → 智能体处理 → 用户结果
```

---

## 快速开始

### 手动使用指南

**第一步：环境准备**

1. 运行环境检测：
```bash
python scripts/check_env.py
```

2. 查看检测结果，根据提示安装缺失的依赖

**第二步：选择安装模式**

```bash
# Linux/macOS
./install.sh

# Windows
install.bat
```

安装脚本提供四种模式：
- **模式 1**：基础安装（仅浏览器自动化）
- **模式 2**：包含 OCR
- **模式 3**：包含 PDF
- **模式 4**：完整安装

**第三步：验证安装**

```bash
python scripts/check_env.py
```

### 一键安装

```bash
# Linux/macOS
./install.sh

# Windows
install.bat
```

### 环境检测

```bash
python scripts/check_env.py
```

### 使用启动脚本

```bash
# Linux/macOS
./bin/web-automation

# Windows
bin\web-automation.bat
```

详细安装和使用指南：见 [references/quickstart.md](references/quickstart.md)

---

## 核心模块

### 模块 0：智能浏览器自动化（Browser-Use AI Agent）

**工作场景**：AI Agent 任务执行、自然语言驱动的复杂任务、与 LLM 集成、智能决策

**核心功能**：
- **自然语言任务描述**：用自然语言描述任务，Agent 自动规划和执行
- **LLM 集成**：支持 OpenAI、Anthropic、Google 等多种 LLM
- **智能决策**：根据页面状态自动决定下一步操作
- **多步规划**：自动拆分复杂任务为多个步骤
- **结构化数据提取**：智能提取表格、表单等结构化数据
- **表单填写**：自动识别和填写表单
- **搜索与收集**：智能搜索并收集信息

**与 Playwright 的区别**：
- **Playwright**：底层浏览器控制，适合精细操作和测试场景
- **Browser-Use**：AI Agent 层，适合复杂任务和智能决策场景

**调用规范**：见 [references/browser-use-integration.md](references/browser-use-integration.md)

**使用示例**：
```python
import asyncio
from scripts.browser_use_agent import BrowserUseAgent

async def ai_automation():
    # 创建 Agent
    agent = BrowserUseAgent(model_name="gpt-4o", headless=False)
    
    # 执行自然语言任务
    result = await agent.run_task(
        task="搜索 Python 教程并提取前 5 个链接",
        url="https://www.google.com",
    )
    
    print(result)
    await agent.close()

asyncio.run(ai_automation())
```

**命令行使用**：
```bash
# 基础用法
python scripts/browser_use_agent.py "搜索 Python 教程"

# 指定 URL
python scripts/browser_use_agent.py "提取页面标题和价格" --url "https://example.com"

# 指定模型
python scripts/browser_use_agent.py "搜索信息" --model "gpt-4o-mini"

# 无头模式
python scripts/browser_use_agent.py "搜索信息" --headless
```

### 模块 1：增强版浏览器操作（推荐）

**工作场景**：需要超时优化、重试机制、反爬增强、证书处理的场景

**核心功能**：
- **超时策略**：预设超时策略（fast/normal/slow/download），可自定义超时时间
- **重试机制**：自动重试失败操作，指数退避策略，可配置重试次数
- **反爬增强**：代理IP支持、随机User-Agent、随机视口和时区
- **证书处理**：支持忽略HTTPS证书错误
- **智能等待**：自适应等待策略
- **统计信息**：操作统计、重试统计

**调用规范**：见 [references/optimization-guide.md](references/optimization-guide.md)

**使用示例**：
```python
import asyncio
from scripts.enhanced_playwright_cli import EnhancedAsyncPlaywrightBrowser

async def enhanced_browsing():
    browser = EnhancedAsyncPlaywrightBrowser(
        headless=True,
        timeout_strategy="slow",  # 使用慢速策略
        max_retries=3,  # 最大重试3次
        proxy={"server": "http://proxy.example.com:8080"},  # 代理
        random_ua=True,  # 随机UA
        ignore_https_errors=False,  # 证书处理
    )
    
    await browser.start()
    await browser.goto("https://example.com")
    
    # 获取统计信息
    stats = browser.get_stats()
    print(f"操作统计: {stats}")
    
    await browser.close()

asyncio.run(enhanced_browsing())
```

**命令行使用**：
```bash
# 使用预设超时策略
python scripts/enhanced_playwright_cli.py "https://example.com" --timeout-strategy slow

# 配置重试和代理
python scripts/enhanced_playwright_cli.py "https://example.com" \
  --max-retries 5 \
  --proxy "http://proxy.example.com:8080" \
  --ignore-https-errors

# 无头模式 + 截图
python scripts/enhanced_playwright_cli.py "https://example.com" \
  --headless \
  --screenshot "screenshot.png"
```

### 模块 2：浏览器管理（Playwright CLI 最佳实践）

**工作场景**：创建/关闭浏览器、截图、配置代理和 UA

**核心功能**：
- 创建浏览器实例（支持代理、自定义 UA、无头模式）
- 使用 Playwright CLI 工具（代码生成、测试运行、浏览器安装）
- 异步浏览器操作（性能更优、智能等待）
- 全页截图和元素截图
- 关闭浏览器释放资源

**与 Browser-Use 的配合**：
- **Browser-Use** 处理智能任务
- **Playwright** 处理底层操作（如登录、基础导航）

**实现方式**：
- **Playwright CLI 工具**：`scripts/playwright_cli.py` - 封装 Playwright CLI 命令
- **异步浏览器操作**：`AsyncPlaywrightBrowser` 类 - 基于异步 API 的浏览器操作
- **智能等待策略**：支持 load、domcontentloaded、networkidle 等等待模式

**调用规范**：见 [references/browser-management.md](references/browser-management.md)
- Playwright CLI 使用：见 [references/playwright-cli-guide.md](references/playwright-cli-guide.md)

**使用示例**：
```python
import asyncio
from scripts.playwright_cli import AsyncPlaywrightBrowser

async def scrape_website(url):
    browser = AsyncPlaywrightBrowser(headless=True)
    await browser.start()
    await browser.goto(url, wait_until="networkidle")
    await browser.wait_for_selector("#content", state="visible")
    await browser.screenshot("screenshot.png")
    await browser.close()

asyncio.run(scrape_website("https://example.com"))
```

### 模块 2：页面交互

**工作场景**：网页导航、元素点击、文本输入、内容提取、异步动态页面处理

**核心功能**：
- 导航到指定 URL
- 点击、输入、滚动等基本交互
- 提取文本、HTML、属性
- **异步动态页面处理**：支持多种加载策略
  - DOMContentLoaded 事件
  - 网络空闲检测 (networkidle)
  - 滚动触发懒加载
  - 动态内容稳定检测

**调用规范**：见 [references/page-interaction.md](references/page-interaction.md)

**异步动态页面处理示例**：
```python
# 多策略内容加载
1. 等待 DOMContentLoaded 事件
2. 检测网络是否空闲
3. 滚动页面触发懒加载
4. 监测页面文本长度变化
5. 连续3次长度不变认为内容稳定
```

### 模块 6：GPU 自动检测（新增）

**工作场景**：自动检测 GPU 并配置加速策略

**核心功能**：
- GPU 可用性检测
- GPU 性能测试
- 使用建议生成
- 自动回退机制

**调用规范**：所有 OCR 脚本已内置 GPU 自动检测，无需手动配置

**使用示例**：
```bash
# 检测 GPU
python scripts/gpu_detector.py

# 测试 GPU 性能
python scripts/gpu_detector.py --test-performance

# 获取使用建议
python scripts/gpu_detector.py --recommendation
```

### 模块 7：文档类型自动识别（新增）

**工作场景**：自动识别发票、合同、身份证等文档类型

**核心功能**：
- 文档类型识别
- 版面分析
- 批量处理
- 置信度评估

**支持类型**：发票、合同、身份证、营业执照、驾驶证、护照、银行卡、票据、收据、菜单、证书、表单、通用文档

**调用规范**：见 [references/document-classifier-guide.md](references/document-classifier-guide.md)

### 模块 8：复杂工作流引擎

**工作场景**：多步骤自动化处理流程

**核心功能**：
- 文档理解工作流（OCR → 分类 → 提取 → 问答 → 摘要）
- 表格提取工作流（检测 → 识别 → 提取 → 导出）
- 网页抓取工作流（导航 → 截图 → OCR → 提取 → 分析）- **已集成 Playwright CLI 最佳实践**
- 自定义工作流

**网页抓取工作流改进**：
- 使用 `AsyncPlaywrightBrowser` 实现异步浏览器操作
- 智能等待策略（load、domcontentloaded、networkidle）
- 动态内容加载支持（滚动加载、懒加载）
- 更好的错误处理和资源管理

**调用规范**：见 [references/workflow-guide.md](references/workflow-guide.md)
- Playwright CLI 使用：见 [references/playwright-cli-guide.md](references/playwright-cli-guide.md)

---

### 模块 5：反爬增强与复杂页面处理（整合 PaddleOCR 3.x）

**工作场景**：绕过网站反爬机制、处理复杂页面（Canvas/SVG/混淆DOM）、验证码识别

**核心功能**：
- **验证码识别**：
  - 图形验证码识别（数字、字母、混合）
  - 验证码预处理（去噪、二值化、增强）
  - 干扰线和干扰点处理
  - 带重试的智能识别

- **Canvas 页面处理**：
  - Canvas 内容截图
  - OCR 提取 Canvas 中的文本
  - 版面分析识别 Canvas 结构
  - 表格数据提取

- **图片文本提取**：
  - 页面中图片的文本识别
  - 正则表达式过滤
  - 批量处理支持

- **复杂页面布局分析**：
  - 混淆 DOM 结构的版面分析
  - 标题、段落、图片、表格区域识别
  - 阅读顺序识别
  - 结构化内容提取

- **智能降级策略**：
  - DOM 提取失败 → OCR 提取
  - 自动选择最佳提取方法
  - 多种参数组合尝试

**调用规范**：
- 验证码识别：见 [references/complex-page-processing.md](references/complex-page-processing.md)
- 复杂页面处理：见 [references/complex-page-processing.md](references/complex-page-processing.md)
- 基础反爬增强：见 [references/anti-scraping-advanced.md](references/anti-scraping-advanced.md)

**使用示例**：
```python
import asyncio
from scripts.playwright_cli import AsyncPlaywrightBrowser
from scripts.captcha_recognition_service import CaptchaRecognitionService
from scripts.complex_page_processor import ComplexPageProcessor

async def complex_scraping():
    # 1. 验证码识别
    captcha_service = CaptchaRecognitionService(use_gpu=True)
    captcha_result = captcha_service.recognize_with_retry("captcha.png")

    # 2. 复杂页面处理
    browser = AsyncPlaywrightBrowser(headless=True)
    await browser.start()
    processor = ComplexPageProcessor(browser, use_gpu=True)

    # Canvas 内容提取
    canvas_result = await processor.extract_from_canvas("#canvas-element")

    # 智能提取（DOM 失败则 OCR）
    smart_result = await processor.smart_extraction(
        "https://example.com/complex-page",
        fallback_to_ocr=True
    )

    await browser.close()

asyncio.run(complex_scraping())
```

### 模块 6：图像识别（OCR）- PaddleOCR 3.x 全新能力

**工作场景**：验证码识别、文字提取、表格提取、版面分析、文档理解、印章检测与识别、复杂页面处理

**核心功能**：
- **新版 OCR 识别（PaddleOCR 3.x）**：
  - 中英文文字识别（精度更高、速度更快）
  - 多语言识别（支持 80+ 语言）
  - 方向分类（自动检测图像方向）
  - 轻量级模型（适合边缘设备）

- **版面识别（PP-StructureV3）**：
  - 文档区域检测（标题、段落、图片、表格、公式）
  - 版面结构分析
  - 阅读顺序识别
  - 复杂版面处理
  - **反爬应用**：解析混淆的 DOM 结构

- **表格识别（PP-StructureV3）**：
  - 表格结构识别（行、列、合并单元格）
  - 表格内容提取
  - 无线表格识别
  - 复杂表格结构处理
  - **反爬应用**：提取复杂表格布局中的数据

- **印章识别（PaddleOCR 3.x 新增）**：
  - 圆形/方形/椭圆印章检测
  - 印章文字识别
  - 印章类型分类（公章、财务章、合同章等）
  - 印章真伪判断（基于特征分析）
  - **反爬应用**：验证文档真实性，绕过印章验证

- **VL 能力（PaddleOCR-VL）**：
  - 图像问答（基于视觉语言模型）
  - 场景分析和图像描述
  - 关键信息提取
  - 多模态理解

- **文档理解增强**：
  - 关键信息提取（发票、合同、身份证等）
  - 文档摘要生成
  - 语义理解

**调用规范**：
- OCR 基础：见 [references/ocr-service.md](references/ocr-service.md)
- 版面识别：见 [references/paddlestructure-guide.md](references/paddlestructure-guide.md)
- 印章识别：见 [references/paddleocr-stamp-guide.md](references/paddleocr-stamp-guide.md)
- VL 能力：见 [references/paddleocr-vl-guide.md](references/paddleocr-vl-guide.md)

**使用示例**：
```python
from scripts.ocr_service import OCRService
from scripts.paddlestructure_service import PaddleStructureService
from scripts.stamp_recognition_service import StampRecognitionService
from scripts.vision_language_service import VisionLanguageService

# 1. 基础 OCR 识别
ocr = OCRService()
result = ocr.recognize_image("image.png")
print(result["text"])

# 2. 版面识别
structure = PaddleStructureService()
layout = structure.analyze_layout("document.png")
print(layout["regions"])  # 标题、段落、图片、表格等

# 3. 表格识别
tables = structure.recognize_tables("table.png")
print(tables[0]["data"])  # 表格内容

# 4. 印章识别
stamp = StampRecognitionService()
stamps = stamp.detect_and_recognize("document.png")
for s in stamps:
    print(f"印章类型: {s['type']}, 文字: {s['text']}")

# 5. VL 能力（图像问答）
vl = VisionLanguageService()
answer = vl.ask_image("image.png", "这张图片展示了什么内容？")
print(answer)
```

### 模块 7：增强版 PDF 处理（推荐）

**工作场景**：从 URL 下载 PDF、断点续传、进度显示、批量处理

**核心功能**：
- **URL 直接下载**：从 URL 直接下载并解析 PDF
- **下载进度显示**：实时显示下载进度、速度、剩余时间
- **断点续传**：下载中断后自动从断点继续
- **大文件优化**：分块下载，内存友好
- **自动重试**：下载失败自动重试
- **批量处理**：批量下载并解析多个 PDF

**调用规范**：见 [references/optimization-guide.md](references/optimization-guide.md)

**使用示例**：
```python
import asyncio
from scripts.enhanced_mineru_service import EnhancedMinerUService

async def download_and_parse():
    service = EnhancedMinerUService()
    
    # 从 URL 下载并解析 PDF
    result = await service.download_and_parse_pdf(
        url="https://example.com/document.pdf",
        output_format="markdown",
        timeout=600,  # 10分钟超时
    )
    
    if result["success"]:
        print(f"解析成功: {result['output_dir']}")

asyncio.run(download_and_parse())
```

**命令行使用**：
```bash
# 下载 PDF
python scripts/enhanced_mineru_service.py download-pdf \
  --url "https://example.com/document.pdf"

# 下载并解析
python scripts/enhanced_mineru_service.py download-and-parse \
  --url "https://example.com/document.pdf" \
  --output-format markdown

# 批量处理
python scripts/enhanced_mineru_service.py batch-process \
  --urls "https://example.com/doc1.pdf" "https://example.com/doc2.pdf"
```

### 模块 8：PDF 处理（基础版）

**工作场景**：PDF 解析、表格提取、布局分析

**核心功能**：
- 解析扫描版 PDF（支持 OCR）
- 高质量表格提取
- 文档布局分析

**调用规范**：见 [references/pdf-processing.md](references/pdf-processing.md)

### 模块 9：文档转换

**工作场景**：Word/PPT/Excel 转 PDF

**核心功能**：
- 多格式转 PDF
- 批量转换
- 环境检测和自动安装

**调用规范**：见 [references/document-conversion.md](references/document-conversion.md)

---

## 数据流总览

### 完整数据处理流程

```
┌─────────────┐
│  用户输入   │
│  (URL/文件) │
└──────┬──────┘
       ↓
┌─────────────┐
│ 智能体决策  │
│ (选择模块)  │
└──────┬──────┘
       ↓
┌──────────────────────────────────────────────┐
│              脚本执行层                        │
│ 浏览器管理 | 页面交互 | OCR 识别 | 文档处理  │
└──────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────┐
│              外部服务层                        │
│ Playwright | PaddleOCR | MinerU | LibreOffice│
└──────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────┐
│              资源层                            │
│ 浏览器 | 网络 | 图片 | 文件                    │
└──────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────┐
│              数据输出                          │
│ 文本 | 结构化数据 | 图片 | PDF                 │
└──────────────────────────────────────────────┘
       ↓
┌─────────────┐
│ 智能体处理  │
└──────┬──────┘
       ↓
┌─────────────┐
│  用户结果   │
└─────────────┘
```

### 数据来源与去向

| 数据类型 | 来源 | 去向 |
|---------|------|------|
| URL | 用户输入 | Playwright 浏览器 |
| 文本 | 用户输入 | 页面输入框 |
| 文件 | 用户上传 | OCR/MinerU/转换器 |
| 截图 | 浏览器渲染 | OCR 引擎 |
| 网页内容 | Playwright 拉取 | 智能体分析 |
| 识别结果 | OCR 引擎 | 智能体处理 |
| 解析内容 | MinerU 引擎 | 智能体处理 |
| 转换文件 | LibreOffice | 用户下载 |

---

## 资源索引

### 必要脚本

| 脚本 | 功能 | 详细规范 |
|------|------|----------|
| `scripts/browser_use_agent.py` | Browser-Use AI Agent 封装 | [browser-use-integration.md](references/browser-use-integration.md) |
| `scripts/enhanced_playwright_cli.py` | 增强版浏览器操作（超时、重试、反爬、证书） | [optimization-guide.md](references/optimization-guide.md) |
| `scripts/enhanced_mineru_service.py` | 增强版 PDF 处理（URL下载、断点续传） | [optimization-guide.md](references/optimization-guide.md) |
|------|------|----------|
| `scripts/playwright_cli.py` | Playwright CLI 工具封装 | [playwright-cli-guide.md](references/playwright-cli-guide.md) |
| `scripts/playwright_manager.py` | 浏览器生命周期管理 | [browser-management.md](references/browser-management.md) |
| `scripts/browser_wrapper.py` | 页面交互封装 | [page-interaction.md](references/page-interaction.md) |
| `scripts/ocr_service.py` | OCR 图像识别（PaddleOCR 3.x） | [ocr-service.md](references/ocr-service.md) |
| `scripts/page_parser.py` | 页面解析和版面分析（PP-StructureV3） | [paddlestructure-guide.md](references/paddlestructure-guide.md) |
| `scripts/stamp_recognition_service.py` | 印章识别服务（PaddleOCR 3.x 新增） | [paddleocr-stamp-guide.md](references/paddleocr-stamp-guide.md) |
| `scripts/captcha_recognition_service.py` | 验证码识别服务（PaddleOCR 3.x） | [complex-page-processing.md](references/complex-page-processing.md) |
| `scripts/complex_page_processor.py` | 复杂页面处理器（Canvas/SVG/混淆DOM） | [complex-page-processing.md](references/complex-page-processing.md) |
| `scripts/chat_ocr_service.py` | 文档问答和关键信息提取（PP-ChatOCRv4） | [pp-chatocrv4-guide.md](references/pp-chatocrv4-guide.md) |
| `scripts/vision_language_service.py` | 视觉语言模型服务（PaddleOCR-VL） | [paddleocr-vl-guide.md](references/paddleocr-vl-guide.md) |
| `scripts/gpu_detector.py` | GPU 检测和性能测试工具 | - |
| `scripts/document_classifier.py` | 文档类型自动识别 | [document-classifier-guide.md](references/document-classifier-guide.md) |
| `scripts/workflow_engine.py` | 复杂文档和网页理解工作流引擎 | [workflow-guide.md](references/workflow-guide.md) |
| `scripts/workflow_logger.py` | 工作流日志记录系统 | [workflow-monitoring-guide.md](references/workflow-monitoring-guide.md) |
| `scripts/workflow_monitor.py` | 工作流监控和告警工具 | [workflow-monitoring-guide.md](references/workflow-monitoring-guide.md) |
| `scripts/mineru_service.py` | MinerU 文档处理 | [pdf-processing.md](references/pdf-processing.md) |
| `scripts/document_converter.py` | 文档格式转换 | [document-conversion.md](references/document-conversion.md) |
| `scripts/browser_fingerprint.py` | 浏览器指纹伪装 | [anti-scraping-advanced.md](references/anti-scraping-advanced.md) |
| `scripts/human_simulation.py` | 人类行为模拟 | [anti-scraping-advanced.md](references/anti-scraping-advanced.md) |
| `scripts/user_agent_manager.py` | User-Agent 管理 | [anti-scraping-advanced.md](references/anti-scraping-advanced.md) |
| `scripts/proxy_manager.py` | 代理池管理 | [anti-scraping-advanced.md](references/anti-scraping-advanced.md) |
| `scripts/cookie_manager.py` | Cookie 持久化管理 | [anti-scraping-advanced.md](references/anti-scraping-advanced.md) |
| `scripts/retry_manager.py` | 请求重试管理 | [anti-scraping-advanced.md](references/anti-scraping-advanced.md) |
| `scripts/enhanced_fingerprint.py` | 增强浏览器指纹伪装 | [anti-scraping-advanced.md](references/anti-scraping-advanced.md) |
| `scripts/anti_scraping_manager.py` | 综合反爬虫管理器 | [anti-scraping-advanced.md](references/anti-scraping-advanced.md) |
| `scripts/check_env.py` | 环境检测 | [quickstart.md](references/quickstart.md) |

### 领域参考

| 参考文档 | 用途 | 何时读取 |
|---------|------|----------|
| `references/troubleshooting.md` | **故障排除指南** | **遇到安装或运行问题时** |
| `references/optimization-guide.md` | **优化指南** | **使用超时、重试、反爬、证书处理功能时** |
| `references/browser-use-integration.md` | Browser-Use 集成指南 | 使用 AI Agent 功能时 |
| `references/quickstart.md` | 快速开始 | 首次使用或安装时 |
| `references/browser-management.md` | 浏览器管理规范 | 使用浏览器管理功能时 |
| `references/page-interaction.md` | 页面交互规范 | 使用页面交互功能时 |
| `references/ocr-service.md` | OCR 服务规范 | 使用 OCR 功能时 |
| `references/paddlestructure-guide.md` | PP-StructureV3 使用指南 | 使用表格识别和版面分析时 |
| `references/paddleocr-stamp-guide.md` | 印章识别指南 | 识别和验证印章时 |
| `references/complex-page-processing.md` | **复杂页面与反爬对抗指南** | **处理 Canvas/SVG/混淆DOM/验证码时** |
| `references/pp-chatocrv4-guide.md` | PP-ChatOCRv4 使用指南 | 使用文档问答和信息提取时 |
| `references/paddleocr-vl-guide.md` | PaddleOCR-VL 使用指南 | 使用视觉语言模型时 |
| `references/workflow-guide.md` | 工作流引擎使用指南 | 使用复杂工作流时 |
| `references/workflow-monitoring-guide.md` | 工作流监控和日志系统指南 | 监控工作流执行时 |
| `references/document-classifier-guide.md` | 文档分类器使用指南 | 自动识别文档类型时 |
| `references/pdf-processing.md` | PDF 处理规范 | 处理 PDF 文档时 |
| `references/document-conversion.md` | 文档转换规范 | 格式转换时 |
| `references/anti-scraping-advanced.md` | 高级反爬策略 | 绕过强反爬保护时 |
| `references/playwright-cli-guide.md` | Playwright CLI 使用指南 | 使用 Playwright CLI 工具时 |

### 配置文件

| 配置文件 | 功能 | 路径 |
|---------|------|------|
| `config.yaml` | 统一配置管理 | `assets/templates/config.yaml` |
| `requirements.txt` | Python 依赖列表 | 根目录 |

### 安装脚本

| 脚本 | 功能 | 平台 |
|------|------|------|
| `install.sh` | 一键安装 | Linux/macOS |
| `install.bat` | 一键安装 | Windows |
| `bin/web-automation` | 统一启动 | Linux/macOS |
| `bin/web-automation.bat` | 统一启动 | Windows |

---

## 注意事项

### 脚本职责划分
- **智能体职责**：策略决策、异常处理、结果分析
- **脚本职责**：技术实现、数据处理、接口调用

### 性能优化
- OCR 操作耗时较长，建议缓存识别结果
- PDF 解析需要大量内存，避免同时处理多个大文件
- 浏览器实例应及时关闭以释放资源

### 错误处理
- 所有脚本返回统一的 JSON 格式结果
- 错误信息包含详细的失败原因
- 智能体应根据错误类型选择恢复策略

### 安全建议
- 不要在脚本中硬编码敏感信息
- 使用环境变量管理配置
- 避免在日志中输出敏感数据

---

## 使用示例

### 示例 1：网页抓取

```bash
# 1. 创建浏览器
python scripts/playwright_manager.py create --headless=False

# 2. 导航到目标网页
python scripts/browser_wrapper.py navigate \
  --url=https://example.com \
  --wait-for-selector=.content

# 3. 提取文本内容
python scripts/browser_wrapper.py extract \
  --selector=.content \
  --type=text

# 4. 关闭浏览器
python scripts/playwright_manager.py close
```

### 示例 2：验证码识别（PP-StructureV3）

```bash
# 1. 创建浏览器并导航
python scripts/playwright_manager.py create
python scripts/browser_wrapper.py navigate --url=https://example.com/login

# 2. 截图验证码
python scripts/playwright_manager.py screenshot \
  --output-path=./screenshots/captcha.png \
  --selector=".captcha"

# 3. OCR 识别（使用 PP-StructureV3）
python scripts/ocr_service.py recognize \
  --image-path=./screenshots/captcha.png \
  --language=ch

# 4. 输入验证码并关闭浏览器
python scripts/browser_wrapper.py fill \
  --selector="#captcha" \
  --text="<识别结果>"
python scripts/playwright_manager.py close
```

### 示例 2.1：表格识别（PP-StructureV3）

```bash
# 识别表格并导出为 HTML
python scripts/ocr_service.py extract-table \
  --image-path=./table.png \
  --output-format=html \
  --output-path=./output/table.html

# 识别表格并导出为二维列表（JSON）
python scripts/ocr_service.py extract-table \
  --image-path=./table.png \
  --output-format=list \
  --output-path=./output/table.json
```

### 示例 2.2：版面分析（PP-StructureV3）

```bash
# 分析页面布局
python scripts/page_parser.py analyze-layout \
  --image-path=./page.png \
  --output-path=./output/layout.json

# 可视化版面分析结果
python scripts/page_parser.py visualize-layout \
  --image-path=./page.png \
  --output-path=./output/layout_visual.png
```

### 示例 2.3：文档问答（PP-ChatOCRv4）

```bash
# 文档问答
python scripts/chat_ocr_service.py qa \
  --image-path=./document.png \
  --question="发票金额是多少？"

# 提取关键信息（发票）
python scripts/chat_ocr_service.py extract \
  --image-path=./invoice.png \
  --info-type=invoice

# 提取关键信息（合同）
python scripts/chat_ocr_service.py extract \
  --image-path=./contract.png \
  --info-type=contract

# 生成文档摘要
python scripts/chat_ocr_service.py summary \
  --image-path=./document.png \
  --max-length=200
```

### 示例 2.4：图像问答（PaddleOCR-VL）

```bash
# 图像问答
python scripts/vision_language_service.py qa \
  --image-path=./image.png \
  --question="图像中有什么内容？"

# 描述图像（简单）
python scripts/vision_language_service.py describe \
  --image-path=./image.png \
  --detail-level=simple

# 分析场景
python scripts/vision_language_service.py analyze \
  --image-path=./document.png

# 提取文字（含版面信息）
python scripts/vision_language_service.py extract \
  --image-path=./image.png \
  --with-layout
```

### 示例 2.5：文档类型自动识别（新增）

```bash
# 识别单个文档
python scripts/document_classifier.py classify document.png

# 批量识别文档
python scripts/document_classifier.py batch ./documents

# 使用 GPU 加速
python scripts/document_classifier.py classify document.png --gpu
```

### 示例 2.6：复杂工作流（新增）

```bash
# 文档理解工作流
python scripts/workflow_engine.py document-understanding document.png

# 文档理解工作流（带问答）
python scripts/workflow_engine.py document-understanding invoice.png \
  --questions "发票金额是多少？" "开票日期？"

# 表格提取工作流
python scripts/workflow_engine.py table-extraction table.png --format html

# JSON 输出
python scripts/workflow_engine.py document-understanding document.png --json
```

### 示例 3：GPU 检测和性能测试（新增）

```bash
# 检测 GPU 状态
python scripts/gpu_detector.py

# 测试 GPU 性能
python scripts/gpu_detector.py --test-performance

# 获取使用建议
python scripts/gpu_detector.py --recommendation
```

### 示例 4：文档类型自动识别（新增）

```bash
# 识别单个文档
python scripts/document_classifier.py classify document.png

# 批量识别文档
python scripts/document_classifier.py batch ./documents

# 使用 GPU 加速
python scripts/document_classifier.py classify document.png --gpu
```

### 示例 5：复杂工作流（新增）

```bash
# 文档理解工作流
python scripts/workflow_engine.py document-understanding document.png

# 文档理解工作流（带问答）
python scripts/workflow_engine.py document-understanding invoice.png \
  --questions "发票金额是多少？" "开票日期？"

# 表格提取工作流
python scripts/workflow_engine.py table-extraction table.png --format html

# JSON 输出
python scripts/workflow_engine.py document-understanding document.png --json
```

### 示例 7：PDF 文档处理

```bash
# 1. 解析 PDF
python scripts/mineru_service.py parse-pdf \
  --pdf-path=./document.pdf \
  --output-format=markdown

# 2. 提取表格
python scripts/mineru_service.py extract-tables \
  --pdf-path=./document.pdf \
  --output-format=json
```

### 示例 4：反爬增强访问（新增）

```bash
# 1. 生成浏览器指纹伪装脚本
python scripts/browser_fingerprint.py \
  --type=all \
  --output=./fingerprint.js

# 2. 生成人类行为模拟脚本
python scripts/human_simulation.py \
  --action=scroll \
  --distance=500 \
  --output=./scroll.js

# 3. 获取随机 User-Agent
python scripts/user_agent_manager.py \
  --action=get \
  --platform=windows

# 4. 使用反爬增强访问网站
# （需要在代码中集成这些脚本，参考 anti-scraping-advanced.md）
```

### 示例 8：文档转换

```bash
# 1. 检查环境
python scripts/document_converter.py check-env

# 2. 转换文档
python scripts/document_converter.py convert \
  --input-file=./document.docx

# 3. 使用转换后的 PDF
python scripts/mineru_service.py parse-pdf \
  --pdf-path=./web-automation/converted/document.pdf
```

### 示例 6：异步动态页面爬取（新增）

```bash
# 使用增强版的测试脚本，支持异步动态页面
python3 full_test_async.py

# 特性：
# - 多策略内容加载
# - 自动检测动态内容
# - 滚动触发懒加载
# - 超时控制机制
# - 三级链接爬取
```

**异步动态页面处理流程**：
```
1. 导航到目标 URL
2. 等待 DOMContentLoaded 完成
3. 检测网络是否空闲
4. 滚动页面触发懒加载
5. 监测页面文本长度变化
6. 连续3次长度不变认为内容稳定
7. 提取页面内容
8. 爬取子页面（递归）
```

更多详细示例：见各模块的调用规范文档

---

## 测试验证

### 完整测试

本 Skill 经过完整测试验证，测试结果详见 `/workspace/full-test/comprehensive-test/TEST_REPORT.md`

**测试覆盖**：
- ✅ PDF 下载和解析（2/2 成功）
- ✅ 网站爬取（8/9 成功）
- ✅ 多级链接爬取（Level 1-3）
- ✅ 异步动态页面处理
- ✅ 反爬虫基础策略

**测试目标**：
1. arXiv PDF - ✅ 成功
2. 团体标准 PDF - ✅ 成功
3. 网易新闻 - ✅ 成功（3级爬取）
4. 中国政府网 - ✅ 成功（3级爬取）
5. 知乎专栏 - ✅ 成功
6. 51CTO 博客 - ❌ 失败（HTTP 567）
7. CSDN - ✅ 成功（3级爬取）
8. 淘宝 - ✅ 成功
9. vLLM 文档 - ✅ 成功（3级爬取）
10. 抖音 - ✅ 成功

**测试脚本**：
- `full_test_async.py` - 完整测试脚本（支持异步动态页面）
- `quick_test_remaining.py` - 快速测试剩余目标

**测试结果**：
- 总目标: 10
- 成功: 9
- 失败: 1
- 成功率: 90.0%
