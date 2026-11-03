---
name: law-exam-analyzer
description: Law exam error analysis skill. Used when users request to analyze bar exam error PDFs (including scanned/image PDFs), generate knowledge summaries, create subject mind maps, or produce error distribution charts (pie charts). This skill supports OCR recognition for scanned PDFs, automatically identifies legal subject categories, classifies error reasons, evaluates knowledge mastery, and outputs Word documents, Markdown mind maps, and PNG charts.
---

# 法考错题分析技能

## 核心功能

本技能将法考错题集PDF转化为结构化的学习资料：

1. **PDF解析** - 从法考错题集PDF中提取题目信息（单选题、多选题、案例分析题）
2. **OCR识别** - 支持扫描版PDF的OCR文字识别（基于Tesseract）
3. **智能分类** - 自动识别法律科目归属和错误原因
4. **知识归纳** - 按科目、错误类型整理知识点
5. **文档生成** - 输出格式化的Word文档（宋体、四号字、26磅行距、首行缩进）
6. **可视化输出** - 生成Markdown思维导图和PNG饼状图

## 触发条件

当用户提到以下场景时触发：
- "分析法考错题"
- "生成错题总结"
- "制作法律科目思维导图"
- "错题分布图表"
- "法考复习资料"
- "扫描版PDF识别"
- "图片PDF文字提取"

## 执行流程

### 步骤1：接收PDF文件
用户上传法考错题集PDF文件，支持文本型PDF和扫描版PDF。

### 步骤2：解析PDF内容
- 首先尝试普通文本提取（pdfplumber）
- 若提取失败或为空，自动切换到OCR模式
- 支持手动指定 `--ocr` 参数强制使用OCR

### 步骤3：知识点分析与分类
调用 `extract_knowledge_points()` 进行：
- 法律科目分类（民法、刑法、行政法等16个科目）
- 错误原因分类（概念混淆、重点遗漏、粗心失误等）
- 掌握程度评估

### 步骤4：生成输出文档
- Word文档：`create_summary_document()` - 格式化知识点总结
- 思维导图：`generate_mindmap_markdown()` - Markdown树形结构
- 饼状图：`generate_pie_charts()` - 三张分布图表

## 依赖要求

```bash
pip install pdfplumber python-docx matplotlib numpy pytesseract Pillow pdf2image
```

**OCR额外依赖：**
- Tesseract OCR引擎 + 中文语言包
- 详情请参考 `references/implementation.md`

## 输出文件

| 文件类型 | 说明 |
|---------|------|
| Word文档 (.docx) | 知识点总结，含统计概览、科目分布、错误原因分析 |
| Markdown (.md) | 思维导图格式，便于快速把握整体框架 |
| PNG图表 (.png) | 三张饼状图：科目分布、错误原因、掌握程度 |

## 详细参考

- **完整代码实现**：请参考 `references/implementation.md`
- **法律科目分类表**：请参考 `references/subject_classification.json`
- **输出格式规范**：请参考 `references/format_spec.md`
- **使用示例**：请参考 `references/usage_examples.md`

## 注意事项

1. PDF可为文本型或扫描版，自动检测并选择合适的提取方式
2. 扫描版PDF识别需要安装Tesseract OCR及中文语言包
3. 题目格式需规范（选项清晰分隔、答案标记明确）
4. 自动分类结果仅供参考，专业法律问题请以官方解释为准
