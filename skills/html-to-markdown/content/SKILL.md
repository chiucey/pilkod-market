---
name: html-to-markdown
description: 智能网页内容提取与 Markdown 转换工具。当用户要求将网页、HTML文件或URL转换为Markdown格式时使用，包括提取微信公众号文章、批量转换、搜索微信文章等场景。
---

# HTML to Markdown Skill

## 快速开始

### 安装依赖

```bash
cd /workspace/temp-skills/html-to-markdown
python3 -m venv venv
source venv/bin/activate
pip install html2text requests
```

### 基本用法

```bash
# 转换 URL 为 Markdown
python html_to_markdown.py -u "https://example.com/article"

# 转换本地 HTML 文件
python html_to_markdown.py -f document.html -o output.md

# 搜索微信公众号文章
python html_to_markdown.py --search-wechat "人工智能"
```

---

## 功能特性

### 1. URL 转 Markdown

```bash
# 单个 URL
python html_to_markdown.py -u "https://blog.csdn.net/article/details/123456"

# 批量 URL
python html_to_markdown.py -u "url1,url2,url3" -o output_dir/

# 带调试信息
python html_to_markdown.py -u "https://example.com" --verbose
```

### 2. 本地文件转换

```bash
# 转换 HTML 文件
python html_to_markdown.py -f article.html -o output.md

# 批量转换
python html_to_markdown.py -f file1.html file2.html file3.html -d output_dir/
```

### 3. 微信公众号文章处理

```bash
# 智能检测并提取微信文章
python html_to_markdown.py -u "https://mp.weixin.qq.com/s/xxxxx"

# 搜索微信公众号文章
python html_to_markdown.py --search-wechat "MiniMax AI Skills"
```

### 4. 提取策略选择

```bash
# 自动选择最佳策略（默认）
python html_to_markdown.py -u "https://example.com" --strategy auto

# 快速提取（不渲染 JS）
python html_to_markdown.py -u "https://example.com" --strategy fast

# 完整提取（支持 JS 渲染）
python html_to_markdown.py -u "https://react.example.com" --strategy full

# 认证模式（处理登录页面）
python html_to_markdown.py -u "https://example.com" --strategy auth
```

---

## Python API 使用

### 基础转换

```python
from html_to_markdown import HTMLToMarkdownConverter

# 创建转换器
converter = HTMLToMarkdownConverter({
    'body_width': 0,      # 行宽，0 表示不换行
    'ignore_images': False,
    'timeout': 30
})

# 转换 URL
markdown = converter.convert_url("https://example.com/article")

# 转换本地文件
markdown = converter.convert_file("document.html", "output.md")

# 转换 HTML 字符串
markdown = converter.convert_raw_html("<h1>标题</h1><p>内容</p>")
```

### 智能提取器

```python
from html_to_markdown import SmartExtractor, StrategyType

# 创建智能提取器
extractor = SmartExtractor({
    'strategy': 'auto',       # auto, fast, full, auth
    'js_rendering': True,
    'auth_support': True,
    'debug': False,
    'verbose': False
})

# 执行智能提取
result = extractor.smart_extract("https://example.com/article")

# 检查结果
if result.success:
    print(f"质量评分: {result.quality_score}")
    print(f"使用策略: {result.strategy_used.value}")
    print(f"Markdown 内容:\n{result.markdown}")
else:
    print(f"错误: {result.errors}")
```

### 微信公众号处理

```python
from html_to_markdown import HTMLToMarkdownConverter

converter = HTMLToMarkdownConverter()

# 检测是否为微信公众号 URL
is_wechat = converter.is_wechat_url("https://mp.weixin.qq.com/s/xxxxx")
print(f"是否为微信文章: {is_wechat}")  # True

# 搜索微信文章
articles = converter.search_wechat_articles("人工智能", max_results=5)
for article in articles:
    print(f"标题: {article['title']}")
    print(f"作者: {article['author']}")
    print(f"摘要: {article['description']}")
    print(f"链接: {article['url']}")
```

### 批量处理

```python
from html_to_markdown import SmartExtractor

extractor = SmartExtractor()

# 批量提取
urls = [
    "https://example.com/article1",
    "https://example.com/article2",
    "https://mp.weixin.qq.com/s/xxxxx"
]

results = extractor.batch_extract(urls)

for url, result in results.items():
    status = "成功" if result.success else "失败"
    print(f"{url}: {status} (质量: {result.quality_score:.2f})")
```

---

## 返回值说明

### ExtractionResult

| 字段 | 类型 | 说明 |
|------|------|------|
| success | bool | 是否提取成功 |
| markdown | str | 转换后的 Markdown 内容 |
| raw_content | str | 原始提取内容 |
| strategy_used | StrategyType | 使用的提取策略 |
| quality_score | float | 质量评分 (0.0-1.0) |
| steps | List[str] | 执行步骤记录 |
| errors | List[str] | 错误信息列表 |
| metadata | dict | 元数据信息 |
| is_wechat_extraction | bool | 是否为微信文章提取 |
| wechat_fallback_used | bool | 是否使用了微信降级处理 |

### 质量评分标准

| 评分 | 说明 |
|------|------|
| 0.8-1.0 | 优秀，内容完整 |
| 0.6-0.8 | 良好，可能有少量噪音 |
| 0.4-0.6 | 一般，建议检查结果 |
| 0.0-0.4 | 较差，可能提取失败 |

---

## 微信公众号文章处理

### 技术限制

由于微信公众号文章的特殊性，无法完全自动化提取：

| 问题 | 说明 |
|------|------|
| 身份验证 | 需要微信登录 Cookie |
| 客户端渲染 | 内容通过 JS 动态加载 |
| URL 加密 | 包含加密用户参数 |

### 解决方案

1. **搜狗搜索**：获取标题、作者、摘要
2. **浏览器访问**：在电脑浏览器打开后保存 HTML
3. **全文复制**：手动复制文章内容

### 示例：处理微信文章

```python
from html_to_markdown import SmartExtractor

extractor = SmartExtractor({'strategy': 'auto'})

# 提取微信文章（会返回处理指南）
result = extractor.smart_extract("https://mp.weixin.qq.com/s/xxxxx")

print(f"是否为微信文章: {result.is_wechat_extraction}")
print(f"使用降级处理: {result.wechat_fallback_used}")
print(f"质量评分: {result.quality_score}")
print(result.markdown)  # 包含处理指南
```

---

## 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-u, --url` | 要提取的 URL | `-u "https://example.com"` |
| `-f, --file` | HTML 文件路径 | `-f article.html` |
| `-o, --output` | 输出路径 | `-o output.md` |
| `-d, --directory` | 批量输出目录 | `-d output/` |
| `-s, --strategy` | 提取策略 | `--strategy fast` |
| `-w, --width` | 行宽 | `-w 80` |
| `-i, --ignore-images` | 忽略图片 | `-i` |
| `-t, --timeout` | 超时秒数 | `-t 60` |
| `--search-wechat` | 搜索微信文章 | `--search-wechat "关键词"` |
| `--debug` | 调试模式 | `--debug` |
| `--verbose` | 详细输出 | `--verbose` |

---

## 使用示例

### 示例 1：提取新闻文章

```bash
python html_to_markdown.py -u "https://news.163.com/article/xxxxx" -o news.md
```

### 示例 2：批量转换电子书

```bash
# 转换多个 HTML 文件
python html_to_markdown.py -f chapter1.html chapter2.html chapter3.html -d chapters/

# 查看结果
ls chapters/
```

### 示例 3：搜索并记录微信文章

```bash
# 搜索 MiniMax 相关文章
python html_to_markdown.py --search-wechat "MiniMax AI" > wechat_articles.txt
```

### 示例 4：Python 脚本集成

```python
#!/usr/bin/env python3
"""批量提取文章并保存"""

from html_to_markdown import SmartExtractor
import json

urls = [
    "https://blog.csdn.net/article1",
    "https://blog.csdn.net/article2",
    "https://zhihu.com/article3"
]

extractor = SmartExtractor({'verbose': True})
results = extractor.batch_extract(urls)

# 保存结果
with open('extraction_results.json', 'w', encoding='utf-8') as f:
    json.dump({
        url: {
            'success': r.success,
            'quality': r.quality_score,
            'markdown': r.markdown
        }
        for url, r in results.items()
    }, f, ensure_ascii=False, indent=2)

print(f"已提取 {len(results)} 篇文章")
```

### 示例 5：处理微信公众号文章

```python
#!/usr/bin/env python3
"""处理微信公众号文章"""

from html_to_markdown import SmartExtractor

# 微信文章 URL
wechat_url = "https://mp.weixin.qq.com/s/xxxxx"

extractor = SmartExtractor({'verbose': True})
result = extractor.smart_extract(wechat_url)

if result.is_wechat_extraction:
    print("检测到微信公众号文章")
    print(f"提取策略: {result.strategy_used.value}")
    print(f"质量评分: {result.quality_score}")

    if result.wechat_fallback_used:
        print("\n由于微信限制，无法直接提取全文")
        print("请参考以下指南获取内容：")
        print("-" * 50)
        print(result.markdown)
```

---

## 故障排除

### 问题：SSL 证书错误

```
SSLCertVerificationError: certificate verify failed
```

**解决方案**：代码已内置 `verify=False`，如仍有问题请检查系统证书。

### 问题：请求超时

```bash
# 增加超时时间
python html_to_markdown.py -u "https://example.com" -t 120
```

### 问题：搜狗微信搜索被限制

```
未找到相关文章，或搜索被限制（可能需要验证码）
```

**解决方案**：
1. 等待一段时间后重试
2. 手动访问 https://weixin.sogou.com/ 进行搜索
3. 使用浏览器访问微信文章后保存 HTML

### 问题：提取质量差

```python
# 检查质量评分
result = extractor.smart_extract(url)
print(f"质量评分: {result.quality_score}")

# 尝试不同策略
result = extractor.smart_extract(url, options={'strategy': 'full'})
```

---

## 文件结构

```
/workspace/temp-skills/html-to-markdown/
├── SKILL.md                 # 技能文档
├── html_to_markdown.py      # 主程序
├── venv/                    # Python 虚拟环境（需手动创建）
│   ├── bin/
│   ├── lib/
│   └── pyvenv.cfg
└── test_results/            # 测试结果目录
```

---

## 更新日志

### v1.1 (2026-04-09)
- 新增微信公众号文章支持
- 新增搜狗微信搜索功能
- 新增智能降级处理
- 新增命令行 `--search-wechat` 参数
- 新增 `WECHAT` 提取策略

### v1.0 (2026-04-09)
- 初始版本
- 支持 URL、文件、HTML 字符串转换
- 支持多种提取策略
- 内置质量评分系统
