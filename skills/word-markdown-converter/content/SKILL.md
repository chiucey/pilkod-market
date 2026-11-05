---
name: word-markdown-converter
description: Markdown与Word文档互转技能。当用户要求将Markdown转换为Word、将Word转换为Markdown、md转docx、docx转md、word转md、md转word时使用。
---

# Word-Markdown 转换器

支持 Markdown (.md) 与 Word (.docx/.doc) 文档之间的相互转换。

## 核心能力

**技术实现**：使用 Python 脚本实现转换，基于 `python-docx` 和 `LibreOffice`。

**依赖环境**：
- `python-docx` - Word文档处理
- `libreoffice` - doc格式转换（可选）

**支持格式**：

| 源格式 | 目标格式 | 说明 |
|--------|----------|------|
| .md / .markdown | .docx | Markdown转新版Word |
| .md / .markdown | .doc | Markdown转旧版Word |
| .docx | .md | Word转Markdown |
| .doc | .md | 旧版Word转Markdown |

## 触发关键词

### 主触发词（两个关键词即可）

当以下关键词组合出现时自动触发：

- **转换词**：`转`、`转换成`、`转为`、`转成`、`转换为`、`变`、`变成`、`生成`、`导出`
- **格式词**：`md`、`markdown`、`word`、`docx`、`doc`

**触发示例**：
- "md转word" ✓
- "转docx" ✓
- "markdown转word" ✓
- "docx转md" ✓
- "word转markdown" ✓
- "生成md" ✓
- "导出docx" ✓

## 执行流程

### ⚠️ 强制执行规则

**必须使用Python脚本执行转换！**

### 步骤1：输入识别

1. **纯文本内容**：用户直接提供Markdown或Word内容
2. **文件上传**：用户上传.md/.docx/.doc文件

### 步骤2：格式验证

**支持的格式**：md、markdown、docx、doc

```
IF 文件扩展名 NOT IN [md, markdown, docx, doc]:
    返回错误："此技能仅支持 md、docx、doc 格式的互转"
    结束
```

### 步骤3：执行转换

必须使用 `scripts/convert.py` 脚本执行：

```bash
# Markdown 转 Word
python scripts/convert.py input.md -o output.docx

# Word 转 Markdown
python scripts/convert.py input.docx -o output.md

# 自动检测格式
python scripts/convert.py input.md        # 自动转为 docx
python scripts/convert.py input.docx      # 自动转为 md
```

### 步骤4：输出交付

1. 检查脚本返回的输出文件是否存在
2. 使用 `<deliver_assets>` 标签返回文件
3. 保持脚本生成的文件名不变

## 功能特性

### Markdown → Word 转换
- 标题层级转换（# ~ ###### → Heading 1-6）
- 有序/无序列表转换
- 引用块转换
- 代码块保留
- 加粗/斜体/链接保留

### Word → Markdown 转换
- 标题转 Markdown 标题
- 段落格式保留
- 列表转换
- 粗体/斜体转换

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| 不支持格式 | 明确告知支持的格式列表 |
| 文件损坏 | 提示用户检查文件后重试 |
| 转换失败 | 说明原因并提供替代方案 |

## 不支持情况

- 加密/受保护的文档
- 超出技能范围的格式（如pdf、xlsx等）
- 复杂表格和图片（保留基本结构）

## 验证命令

```bash
# 验证依赖和脚本
python scripts/quick_validate.py
```
