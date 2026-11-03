# PDF文档校对工具使用指南

## 功能概述

本工具用于比对PDF源文档与OCR/解析后的文本内容，精确检测内容层面的差异。

## 支持的场景

1. **OCR结果校对**：比对PDF扫描件与OCR识别结果
2. **文本提取验证**：比对PDF原文与提取后的文本
3. **文档转换校验**：比对转换前后的文档内容
4. **批量报告审核**：支持100页以上的大型报告

## 使用方法

### 方法1：命令行执行

```bash
python scripts/compare_documents.py <源文件> <解析文件> [-o 输出报告] [-c 分块大小]
```

**示例**：
```bash
# 基本用法
python scripts/compare_documents.py original.txt parsed.txt -o report.md

# 自定义分块大小（用于超大文档）
python scripts/compare_documents.py original.pdf.txt parsed.txt -o report.md -c 8000
```

### 方法2：作为模块导入

```python
from scripts.compare_documents import compare_files, DocumentComparator

# 方式1：直接比对文件
report = compare_files('original.txt', 'parsed.txt', 'report.md')

# 方式2：使用比对器（自定义处理）
comparator = DocumentComparator(chunk_size=6000)
differences, identical = comparator.compare_texts(original_text, parsed_text)
```

## 差异类型说明

| 类型 | 标记 | 说明 |
|------|------|------|
| 文字错误 | `[文字错误]` | 错别字、字符替换等 |
| 数字错误 | `[数字错误]` | 数值差异、小数点位置错误 |
| 遗漏内容 | `[遗漏内容]` | 原文有，解析无 |
| 多余内容 | `[多余内容]` | 解析有，原文无 |

## 输出报告示例

```markdown
# 文档校对报告

## 文档信息
- 源文件：annual_report_2024.pdf
- 解析文件：annual_report_2024.txt
- 比对时间：2024-01-15 10:30:00

---

## 差异详情

### 第1处差异

**位置**：块 3, 第15行
**类型**：数字错误

| | 内容 |
|---|---|
| **原文** | 净利润：1,234.56万元 |
| **解析后** | 净利润：1,2345.6万元 |

**描述**：数值 1234.56 → 12345.6，差异 10110.04

---

## 无差异区域

1. 本公司主要从事电子产品研发...
2. 2024年度实现营业收入...
...
```

## 性能特性

- **内存优化**：采用分块处理，内存占用恒定
- **上下文保持**：块之间有重叠区域，保持上下文连贯性
- **大文档支持**：理论上支持无限长度的文档
- **中文优化**：特别处理中文标点、空格等格式差异

## 注意事项

1. 输入文件应为纯文本格式（.txt）
2. 如果是PDF文件，请先使用PDF转文本工具提取内容
3. 对于超大文档，建议增加分块大小（-c参数）
4. 报告中的"位置"信息是相对于分块的位置，可能需要结合原文定位
