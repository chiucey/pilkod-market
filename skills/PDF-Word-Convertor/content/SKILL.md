---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100e90e98f4c1e894575c3239eb6d8a8a08dd7b99ee028cbe3a33c319d66c673585022100ac01661c21bcbfeed04e2fa2f90d0326b3274c5f44bbc0c4953b7d9a3f4cfd78
    ReservedCode2: 3046022100ae500927324a97ae213322c5d7394fb09de684c90c26b5dee7578cc0a24bf36a022100a2ac2d1dd0a59abdb3f2bc689558dbd047e793e8586d872e600633263e5c7cda
description: 一个强大的文档转换器。支持将文字转PDF，文字转word，word转PDF，支持互转。当用户说"转pdf"、"转word"、"生成pdf"、"导出word"，或要求将文本转word、文本转pdf、word转pdf、txt转word、txt转pdf、word转txt、pdf转word、pdf转txt时使用。
name: PDF-Word-Convertor
---

# PDF-Word-Convertor 文档转换器

## 核心能力

**技术实现**：使用Python脚本实现转换，基于reportlab、python-docx、pypdf和LibreOffice。

**依赖环境**：
- `reportlab` - 文本转PDF
- `python-docx` - 文本/Word处理
- `pypdf` - PDF文本提取
- `libreoffice` - Word转PDF

支持以下文档格式之间的互转：

| 源格式 | 目标格式 | 说明 |
|--------|----------|------|
| txt | doc/docx | 文本转Word |
| txt | pdf | 文本转PDF |
| doc/docx | txt | Word转文本 |
| doc/docx | pdf | Word转PDF |
| pdf | txt | PDF转文本 |
| pdf | doc/docx | PDF转Word |

同时支持**纯文本输入**直接转换为目标格式（用户输入文字内容，要求生成对应格式文档）。

## 触发关键词组合

### 简化触发条件（两个关键词即可）

当以下两个关键词同时出现（不考虑顺序）时自动触发：

- **转换词**：`转`、`转换成`、`转为`、`转成`、`转换为`、`变`、`变成`、`生成`、`导出`
- **目标格式词**：`pdf`、`word`、`doc`、`docx`

**简化触发示例**：
- "转pdf" ✓
- "转word" ✓
- "生成pdf" ✓
- "导出word" ✓
- "帮我转pdf" ✓
- "转成pdf格式" ✓

### 完整触发条件（三个关键词）

当需要明确指定源格式时，使用三个关键词组合：

- **转换方向词**：`转`、`转换成`、`转为`、`转成`、`转换为`、`变`、`变成`
- **目标格式词**：`word`、`doc`、`docx`、`pdf`、`txt`
- **来源词**（可选）：`文本`、`文件`、`文档`、`txt`、`word`、`pdf`

**完整触发示例**：
- "把文本转成word" ✓
- "txt转pdf" ✓
- "帮我把word转pdf" ✓
- "上传文件转pdf" ✓
- "文本转换成docx" ✓
- "这个文档转成txt" ✓
- "帮我转成word格式" ✓

### 触发优先级

1. **最高优先级**：关键词 `转pdf`、`转word`、`生成pdf`、`导出word` → 直接触发
2. **次优先级**：包含转换方向词 + 目标格式词 → 触发
3. **最低优先级**：需要三个关键词明确匹配 → 触发

## 执行流程

### ⚠️ 强制执行规则

**必须使用Python脚本执行转换，禁止使用其他方式！**

❌ **禁止使用以下方式**：
- `html_to_pdf` - 禁止使用HTML转PDF
- `minimax-pdf` 技能 - 禁止调用
- 手动创建HTML/其他中间格式再转换

✅ **必须使用脚本转换**：
- 必须使用 `scripts/convert.py` 执行所有转换
- 脚本位于技能目录的 `scripts/` 文件夹下

### 步骤1：输入识别与格式检测

1. **如果是纯文本输入**：
   - 将文本内容写入临时 .txt 文件（如 `/tmp/input.txt`）
   - 识别用户要求的目标格式
   - 使用 `python scripts/convert.py /tmp/input.txt -o output.pdf` 执行转换

2. **如果是上传文档**：
   - 检测文件扩展名（.txt, .doc, .docx, .pdf）
   - 识别用户要求的目标格式
   - 使用 `python scripts/convert.py input.xxx -o output.yyy` 执行转换

### 步骤2：格式验证

**支持的格式**：txt、word(doc/docx)、pdf

**验证规则**：
```
IF 文件扩展名 NOT IN [txt, doc, docx, pdf]:
    返回错误："此技能仅支持 txt、word(doc/docx)、pdf 三种格式的转换，暂不支持 [实际格式] 格式"
    结束
```

### 步骤3：文件大小验证

**阈值**：5MB

```
IF 文件大小 > 5MB:
    提示用户确认："当前文件大小为 [X] MB，转换可能需要较长时间。是否继续转换？"
    IF 用户取消:
        结束
    ELSE:
        继续转换
```

### 步骤4：格式转换（必须使用脚本）

#### 4.1 文本转Word (txt → docx)

- 保留文本段落格式
- 使用通用字体和字号
- 创建标准的docx文档

#### 4.2 文本转PDF (txt → pdf)

- 保留文本段落格式
- 设置合适的页边距
- 使用适合阅读的字体

#### 4.3 Word转PDF (doc/docx → pdf)

- 尽可能保留原始样式
- 保留图片和表格
- 保持页面布局

#### 4.4 Word转Txt (doc/docx → txt)

- 提取纯文本内容
- 移除格式和图片
- 保留段落结构

#### 4.5 PDF转Word (pdf → docx)

- 尽可能恢复原始布局
- 提取文本内容
- 尝试保留表格结构

#### 4.6 PDF转Txt (pdf → txt)

- 提取所有文本内容
- 移除图片
- 保持阅读顺序

### 步骤5：输出交付

1. **确认文件生成成功**：检查脚本返回的输出文件是否存在
2. **使用正确的文件路径**：脚本输出路径即最终交付路径
3. **使用 `<deliver_assets>` 标签返回文件**
4. **禁止修改文件名**：保持脚本生成的文件名不变

**⚠️ 重要：交付时必须使用脚本实际生成的文件路径！**

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| 不支持的格式 | 明确告知支持的格式列表 |
| 文件损坏 | 提示用户检查文件后重试 |
| 文件过大 | 提示大小限制并请求确认 |
| 转换失败 | 说明原因并提供替代方案 |

## 不支持的情况

- 扫描版PDF（无文字层）转其他格式 → 提示："该PDF为扫描件，无法提取文字内容"
- 加密/受保护的文档 → 提示："加密文档需要先解除保护"
- 超出技能范围的格式（如xlsx、ppt等）→ 明确拒绝并说明原因

## 使用限制

- 单个文件大小限制：建议不超过50MB
- 转换时间预估：每10MB约需30秒（视服务器负载而定）
- 文件大于5MB时需要用户二次确认

## 输出示例

### 成功示例

```
文档转换完成！

- 源文件：document.txt
- 目标格式：Word文档 (.docx)
- 状态：✓ 转换成功

[下载链接或文件交付]
```

### 错误示例

```
抱歉，无法执行此转换。

原因：该技能仅支持 txt、word(doc/docx)、pdf 三种格式的互转，暂不支持 xlsx 格式。

如需转换 xlsx 文件，建议使用专门的表格转换工具。
```

## 脚本执行

### 基本用法

```bash
# 安装依赖
pip install python-docx pypdf reportlab

# 转换文件
python scripts/convert.py input.txt -o output.pdf
python scripts/convert.py input.txt -o output.docx
python scripts/convert.py input.pdf -o output.docx
python scripts/convert.py input.docx -o output.pdf

# 自动检测并转换（输出文件名自动生成）
python scripts/convert.py input.txt
```

### 验证依赖

```bash
python scripts/quick_validate.py
```

### 支持的转换命令

| 命令 | 功能 |
|------|------|
| `convert.py input.txt -o output.pdf` | 文本转PDF |
| `convert.py input.txt -o output.docx` | 文本转Word |
| `convert.py input.pdf -o output.txt` | PDF转文本 |
| `convert.py input.pdf -o output.docx` | PDF转Word |
| `convert.py input.docx -o output.pdf` | Word转PDF |
| `convert.py input.docx -o output.txt` | Word转文本 |
| `convert.py input.doc -o output.docx` | 旧版Word转新版 |
| `convert.py input.doc -o output.pdf` | 旧版Word转PDF |

### 纯文本输入转换

当用户提供纯文本内容时，直接使用脚本生成目标格式：

```bash
# 用户输入的文本内容写入临时文件后转换
echo "用户的文本内容" | python scripts/convert.py /dev/stdin -o output.pdf
```
