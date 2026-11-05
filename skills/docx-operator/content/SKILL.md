---
name: docx-operator
description: DOCX document operation expert. Use when users request creating Word documents, editing DOCX files, formatting documents, generating contracts/reports/resumes, adding tables/images, or applying styles to documents.
---

# DOCX文档操作专家

## 核心能力

基于 OpenXML SDK 实现，专注于「创建/编辑/格式化」DOCX 文件，支持合同、报告、简历等多种文档类型。

## 支持的文档类型

| 类型 | 示例 | 特点 |
|------|------|------|
| 合同 | 软件开发合同、租赁合同 | 条款完整、格式规范 |
| 报告 | 工作报告、分析报告 | 结构清晰、数据准确 |
| 简历 | 个人简历、求职信 | 简洁专业、排版精美 |
| 方案 | 项目方案、商业计划 | 逻辑清晰、图文并茂 |
| 函件 | 公函、通知、邀请函 | 格式正式、语言规范 |

## 支持的操作

| 操作类型 | 说明 | 示例 |
|----------|------|------|
| 创建 | 新建空白文档或模板 | 创建合同模板 |
| 编辑 | 修改现有文档内容 | 更新条款、更新数据 |
| 格式化 | 调整排版和样式 | 标题层级、段落缩进 |
| 插入 | 添加表格/图片/目录 | 插入数据表格 |
| 样式 | 应用预设样式 | 标题1、正文、引用 |

## 工作流程

### 步骤 1：需求收集

主动确认以下要素（使用 GenUI 表单）：

| 字段 | 说明 | 示例 |
|------|------|------|
| 操作类型 | 具体任务 | 创建 / 编辑 / 格式化 |
| 文档类型 | 文档分类 | 合同 / 报告 / 简历 |
| 具体内容 | 详细需求 | "创建软件开发合同" |
| 格式要求 | 排版偏好 | "A4纸、1.5倍行距" |
| 现有文件 | 编辑时提供 | "template.docx" |

**触发表单**：多页 GenUI 表单，收集以上信息。

### 步骤 2：执行操作

**使用 MiniMax Docx CLI 工具**：

```bash
# 创建新文档
minimax-docx create --type contract --output contract.docx

# 添加标题
minimax-docx heading --file contract.docx --level 1 --text "软件开发合同"

# 添加段落
minimax-docx paragraph --file contract.docx --text "甲乙双方经友好协商..."

# 插入表格
minimax-docx table --file contract.docx --rows 5 --cols 3

# 应用样式
minimax-docx style --file contract.docx --style "Heading1"
```

**支持的格式化选项**：

| 类型 | 选项 |
|------|------|
| 字体 | 字体名称、大小、加粗、斜体、下划线 |
| 段落 | 对齐、缩进、行距、段前/段后间距 |
| 页面 | 纸张大小、页边距、页眉页脚 |
| 表格 | 边框、对齐、单元格合并 |

### 步骤 3：结果交付

**输出内容**：

```
## 操作结果

### 文件信息
- 文件路径：[路径]
- 文档类型：[类型]
- 页数：[X]

### 操作日志
- [已完成] 创建文档结构
- [已完成] 添加标题 "文档标题"
- [已完成] 插入数据表格 (5行3列)
- [已完成] 应用样式 "正文"
- [已完成] 添加页眉页脚

### 内容预览
[文档内容摘要]
```

## 文档模板结构

### 合同模板

```
# [合同标题]

## 第一条 [条款名称]
[条款内容]

## 第二条 [条款名称]
[条款内容]

## 附则
[其他约定]
```

### 报告模板

```
# [报告标题]

## 执行摘要
[核心结论]

## 背景
[背景介绍]

## 分析
[详细分析]

## 结论与建议
[结论建议]
```

## 交付物

完成后输出：

```xml
<genui-skill-card name="docx-operator" desc="DOCX文档操作专家" skill-id="xxx"></genui-skill-card>
```

**Summary**: Word文档已生成
**Description**: 已创建 [文档类型] 文档，保存至 [路径]，包含 [页数] 页内容

<deliver_assets>
<item>
<path>output/document.docx</path>
<name>Word文档</name>
</item>
<item>
<path>output/operation-log.md</path>
<name>操作日志</name>
</item>
</deliver_assets>

## 质量标准

| 标准 | 要求 |
|------|------|
| 格式正确 | 标题层级清晰、段落缩进一致 |
| 内容准确 | 符合用户需求、条款完整 |
| 兼容性强 | 兼容 Word 2016+ |
| 无错误 | 无格式错误、无乱码 |

## 限制与注意事项

1. **文件状态**：不处理加密或损坏文件
2. **文档隐私**：不泄露敏感信息
3. **模板支持**：复杂模板需用户提供或详细说明
4. **内容核实**：重要数据需用户核实确认

## 技术工具

- **MiniMax Docx CLI**：文档创建、编辑、格式化
- **Python (python-docx)**：复杂文档处理
- **pandoc**：格式转换（DOCX/Markdown）
