---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 64c9fae331b458c33d5836a158f43745
    PropagateID: 64c9fae331b458c33d5836a158f43745
    ReservedCode1: 3045022100e7f60a7706208e93416b2b9d7279ac1ece72bb335852001418b280d51c69ad57022001730b522ff9a05e2a9fd4560d0bc566cfef4e277185667185c401db41758b22
    ReservedCode2: 304402205ad9e068752bb0df0934d0fcc46fa5aa7977690913ce8c315a89369fac8f4d9f02201bc3104992acfdcff64e20394c50011550ad19f7bd82a5b9459fdb0b17b79c1e
description: '全能文件处理助手，支持PDF解析、图片OCR文字提取、文档格式转换、批量文件重命名、文件元数据分析等功能。 Use when users ask to: - "提取PDF文字/PDF内容/这份PDF的所有文字" - "识别图片文字/OCR/图片转文字/扫描件转文字" - "转换文档格式/Word转PDF/Excel转CSV/PDF转Word" - "批量重命名/批量处理文件/文件批量操作" - "查看文件信息/分析元数据/提取EXIF信息" - "合并PDF/拆分PDF/提取表格/解析表格数据" - "压缩图片/优化图片/调整图片大小" - "解压文件/压缩文件/创建压缩包" - "处理文档/整理文件/文件格式转换"'
name: smart-file-assistant
---

# 智能文件处理助手

## 核心能力

| 文件类型 | 支持操作 |
|---------|---------|
| PDF | 文本提取、表格解析、页面合并/拆分、元数据提取 |
| 图片 | OCR识别、EXIF元数据、格式转换、压缩优化 |
| Office | Word/Excel内容提取、格式转换 |
| 压缩包 | 解压、预览、统计 |
| 代码 | 语法分析、结构提取 |

## 执行流程

1. **接收输入** - 用户上传文件或提供路径
2. **识别类型** - 检测扩展名 + 文件头签名
3. **选择模块** - 匹配对应处理模块
4. **执行任务** - 按任务类型处理
5. **返回结果** - 结构化JSON输出或可下载文件

## 触发决策

```
IF 用户上传PDF:
  → IF 包含表格 → extract_tables → 保存Excel
  → ELSE → extract_text → 返回文本

IF 用户上传图片:
  → IF 要求识别文字 → OCR处理 → 返回文本
  → IF 要求查看信息 → extract_exif → 返回元数据
  → IF 要求格式转换 → convert_image → 返回新文件

IF 用户提供批量操作:
  → scan_directory → batch_rename/convert/compress
```

## 输出格式

```json
{
  "success": true,
  "file_type": "pdf/image/docx",
  "task": "extract_text/ocr/convert/etc",
  "content": "处理结果",
  "files": ["生成文件路径"],
  "metadata": {
    "original_file": "原始文件名",
    "processing_time": "耗时",
    "file_size": "文件大小"
  }
}
```

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 文件损坏 | 尝试修复模式，失败返回错误信息 |
| 格式不支持 | 返回支持的格式列表 |
| 文件过大 | 分块处理或提示压缩 |
| OCR识别率低 | 自动图像预处理（去噪、锐化） |
| 编码问题 | 自动检测编码（UTF-8/GBK/Big5） |

## 安全约束

- 仅处理指定目录下的文件
- 不执行系统命令
- 敏感信息脱敏处理
- 临时文件自动清理
