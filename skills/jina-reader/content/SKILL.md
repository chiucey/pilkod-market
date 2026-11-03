---
name: jina-reader
description: 使用 Jina AI Reader 将任意网页转换为 AI 友好的 Markdown 格式。当用户需要抓取网页内容、提取干净的文章文本、获取 AI 可读的 Markdown 内容、转换网页为 Markdown 时使用此技能。
---

# Jina AI Reader

将任意网页转换为干净、AI 友好的 Markdown 格式内容。

## 核心用法

**使用方式极其简单**：在任何网址前面加上 `https://r.jina.ai/` 前缀即可。

### 基础语法

```
https://r.jina.ai/<目标网址>
```

### 示例

| 原始网址 | 转换后的访问地址 |
|---------|-----------------|
| `https://example.com/article` | `https://r.jina.ai/https://example.com/article` |
| `https://news.example.com/story/123` | `https://r.jina.ai/https://news.example.com/story/123` |
| `https://docs.example.com/guide` | `https://r.jina.ai/https://docs.example.com/guide` |

## 使用场景

1. **网页内容提取**：获取任意网页的主要内容文本
2. **AI 友好格式**：获取干净的 Markdown 格式，便于 AI 处理和分析
3. **去除噪音**：自动移除广告、导航栏、页脚等干扰内容
4. **长文本处理**：适合处理长篇文章、文档、教程等内容

## 实际应用

### 配合工具使用

此技能可与以下工具配合使用：

- **网页内容提取** (`extract_content_from_websites`)：直接使用转换后的 URL 获取 Markdown 内容
- **搜索增强**：将搜索结果页面转换为可读的 Markdown
- **文档处理**：将网页文档转换为 Markdown 进行进一步处理

### 示例工作流

```
用户请求：帮我抓取 https://example.com/blog/article 的内容

操作步骤：
1. 将 URL 转换为：https://r.jina.ai/https://example.com/blog/article
2. 使用 extract_content_from_websites 工具访问该 URL
3. 返回的结果即为干净的 Markdown 格式内容
```

## 注意事项

- 目标网址需要包含完整的协议头 (`https://` 或 `http://`)
- 如果目标网站有反爬措施，可能会返回错误或限制访问
- 返回的内容是纯 Markdown 格式，不包含原始 HTML 结构

## 技术原理

Jina Reader 通过 AI 技术解析网页 DOM 结构，智能识别主要内容区域，去除导航、广告、页脚等噪音元素，输出纯净的 Markdown 格式文本。这种格式保留了原文的标题层级、列表、代码块等结构化信息，非常适合后续的 AI 处理和分析。
