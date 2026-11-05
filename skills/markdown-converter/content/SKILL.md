---
name: markdown-converter
description: 多格式转Markdown工具，支持PDF、Word、PPT、Excel、图片、音频、ZIP、YouTube等20+种格式。当用户要求转换文档格式、提取PDF内容、转换Word/PPT/Excel为Markdown、处理扫描件、进行OCR识别、转录音频、提取YouTube字幕时使用。
---

# Markdown Converter

多格式转Markdown工具，支持20+种文件格式的智能转换，自动提取核心内容，保留文档结构，输出专为LLM优化的结构化Markdown。

## 核心功能

### 支持的格式

| 类别 | 格式 |
|------|------|
| 文档 | PDF、DOCX、DOC、TXT、RTF、ODT |
| 演示 | PPTX、PPTX、ODP |
| 表格 | XLSX、XLS、CSV、ODS |
| 图片 | JPG、PNG、GIF、BMP、WebP（支持OCR） |
| 音频 | MP3、WAV、AAC、FLAC（支持语音转录） |
| 视频 | YouTube链接（提取字幕） |
| 压缩 | ZIP（自动解压并转换内部文件） |
| 其他 | HTML、EPUB、Markdown源文件 |

### 转换规则

1. **结构保留**：自动识别并保留标题层级（H1-H6）、表格、列表、链接
2. **噪声过滤**：自动过滤广告、页眉页脚、冗余代码、无关内容
3. **表格处理**：保留表格结构，使用Markdown表格语法
4. **图片处理**：可选择提取图片或保留图片引用
5. **链接处理**：保留原始链接，转换为Markdown链接格式

### 高级功能

#### OCR文字识别
- 自动检测图片中的文字
- 支持中英文混合识别
- 自动过滤背景噪声

#### 语音转录
- 支持MP3、WAV等音频格式
- 自动转录为文本
- 保留标点和段落结构

#### Azure Document Intelligence增强
- 适合扫描版PDF
- 低质量文档增强提取
- 提供API密钥和端点配置

#### YouTube字幕提取
- 自动获取视频字幕
- 支持多语言字幕
- 转换为结构化Markdown

## 使用方法

### 基础转换

```
file: "document.pdf"
```

### 带图片提取

```
file: "document.pdf"
include_images: true
```

### Azure增强模式

```
file: "scanned_document.pdf"
use_azure_enhance: true
```

### 指定输出路径

```
file: "document.pdf"
output_path: "/path/to/output.md"
```

### YouTube视频转换

```
file: "https://www.youtube.com/watch?v=xxxxx"
```

## 处理流程

### 1. 格式识别
自动识别输入文件的格式类型，选择对应的提取引擎

### 2. 内容提取
- PDF：提取文本和结构
- 图片：执行OCR
- 音频：语音转录
- ZIP：递归处理内部文件

### 3. 结构优化
- 过滤噪声内容
- 重建标题层级
- 格式化表格和列表

### 4. 输出生成
生成结构化Markdown，保留关键信息

## 环境变量

| 变量名 | 说明 | 必填 |
|--------|------|------|
| AZURE_DOCUMENT_INTELLIGENCE_KEY | Azure API密钥 | 否 |
| AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT | Azure端点地址 | 否 |

## 输出示例

```markdown
# 文档标题

## 第一章

这是正文内容...

### 小节

- 列表项1
- 列表项2

| 列1 | 列2 |
|------|------|
| 数据1 | 数据2 |
```

## 最佳实践

1. **批量处理**：ZIP文件支持批量自动转换
2. **清晰优先**：优先保证内容准确性，其次结构完整性
3. **图片优化**：需要提取图片时设置 `include_images: true`
4. **扫描件处理**：扫描版PDF建议启用Azure增强模式
