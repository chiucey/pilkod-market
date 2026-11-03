---
name: template-doc-generator
description: 基于模板生成格式一致的 Word 文档（CV、简历、报告等）。当用户提供模板文件（.docx）和需要填充的数据时，自动复制模板并填入数据，验证结构一致性。适用于 CV、简历、申请表、报告等任何需要保持固定格式的文档场景。如果用户提到"按模板生成"、"填表"、"CV"、"简历"、"格式要一致"、"不要格式错"、"复制模板"等关键词，使用此技能。
---

# Template Document Generator

基于模板文件生成格式一致的 Word 文档。

## 核心原则

**永远先复制模板再填充数据，不要从零构造 docx。** 从零构造无法保证格式一致（字体、样式、表格结构、段落顺序），用户会反馈"格式不对"。

## 技术栈

- `shutil.copy` — 复制模板文件
- `python-docx` — 读取和修改文档结构
- `docx2txt` — 快速提取模板文本做初步分析（可选）

## 工作流程

### Step 1: 分析模板结构

在修改之前，先完整读取模板，记录以下元数据：

```python
from docx import Document

doc = Document('template.docx')

# 1. 段落分析
for i, p in enumerate(doc.paragraphs):
    print(f"Para {i}: style='{p.style.name}', text='{p.text[:80]}'")

# 2. 表格分析
for ti, table in enumerate(doc.tables):
    print(f"\nTable {ti}: {len(table.rows)} rows x {len(table.columns)} cols")
    for ri, row in enumerate(table.rows):
        cells = [cell.text for cell in row.cells]
        print(f"  Row {ri}: {cells}")

# 3. 样式分析
for style in doc.styles:
    if style.name.startswith(('Heading', 'Normal', 'Bold')):
        print(f"Style: {style.name}")
```

**记录清单：**
- [ ] 段落总数及每个段落的 style、前 80 字符
- [ ] 表格总数及每个表格的行列数
- [ ] 每个表格的标签列/字段名（用于定位填充位置）
- [ ] 特殊格式：制表符位置、混合格式（同一段落内 Bold + 普通）、标点符号
- [ ] 段落顺序（标题 → 表格 → 段落 的排列）

### Step 2: 收集并确认数据

如果用户提供的信息不完整或分散：

- **即时确认**：每批信息立即结构化输出确认（表格形式）
- **完整性追踪**：维护 ✅/❌ 检查表，每次回复末尾明确列出"仍缺少的信息"
- **图片信息处理**：通过 OCR 提取后，结构化输出逐条核对（时间、IF 值、作者排序等关键数据）
- **单一事实来源**：最终生成 `.md` 汇总文件作为完整记录，方便后续查询和修改

**数据收集模板：**
```
收到，已记录以下信息：

| 作者 | 项目 | 内容 |
|------|------|------|

---
### ❌ 仍缺少的信息
| 作者 | 缺失内容 |
|------|---------|
```

### Step 3: 复制模板并填充

```python
import shutil
from docx import Document

# 3a. 复制模板
shutil.copy('template.docx', 'output.docx')

# 3b. 打开副本
doc = Document('output.docx')
```

#### 填充策略 A：按段落文本定位

适用于段落包含唯一标签的情况：

```python
for para in doc.paragraphs:
    if '姓名' in para.text:
        for run in para.runs:
            if '姓名' in run.text:
                run.text = run.text.replace('姓名', '姓名\t俞佳')
```

#### 填充策略 B：按表格定位

适用于表格填充（最常见场景）：

```python
target_table = doc.tables[0]  # 或遍历查找

# 填充单元格 — 用 clear() + add_run() 保留格式
for cell in target_table.rows[1].cells:
    if cell.paragraphs:
        cell.paragraphs[0].clear()
        cell.paragraphs[0].add_run('新数据')
```

#### 填充策略 C：插入新行/段落

适用于数据量超过模板预设行数的情况：

```python
# 在表格末尾添加新行（复制第一行格式）
source_row = target_table.rows[1]
new_row = target_table.add_row()
for i, cell in enumerate(source_row.cells):
    new_row.cells[i].text = cell.text
```

### Step 4: 验证结构

生成后**必须**逐项验证：

```python
def verify(template_path, output_path):
    t = Document(template_path)
    o = Document(output_path)
    
    checks = []
    checks.append(('段落数', len(t.paragraphs), len(o.paragraphs)))
    checks.append(('表格数', len(t.tables), len(o.tables)))
    for i, (tt, ot) in enumerate(zip(t.tables, o.tables)):
        checks.append((f'Table {i} 行数', len(tt.rows), len(ot.rows)))
        checks.append((f'Table {i} 列数', len(tt.columns), len(ot.columns)))
    return checks
```

**验证输出格式：**

| 检查项 | 模板值 | 生成值 | 状态 |
|--------|--------|--------|------|
| 段落数 | X | X | ✅ |
| 表格数 | X | X | ✅ |
| Table 0 行列 | X×Y | X×Y | ✅ |
| Table 1 行列 | X×Y | X×Y | ✅ |
| 段落顺序 | ... | ... | ✅ |
| 标题样式 | ... | ... | ✅ |

### Step 5: 双语处理（如需要）

如果需要中英双语版本：

1. 先建立完整数据结构（统一的中英映射表）
2. 中文版本填充并确认内容无误
3. 翻译为英文（保留专业术语准确性）
4. 复用同一模板生成英文版本
5. 英文版本同样执行 Step 4 验证

**翻译注意事项：**
- 人名：拼音格式（姓全大写或首字母大写，名连写或首字母大写）
- 职称：主管护师 → Senior Nurse / 主治医师 → Attending Physician
- 学历：本科 → Bachelor's Degree / 硕士 → Master's Degree
- 论文标题：准确翻译，保留期刊名原文
- 认证状态：如不确定填 "Pending" 或 "Verified"

## 常见陷阱与修复

| # | 陷阱 | 原因 | 正确做法 |
|---|------|------|----------|
| 1 | **格式不对** | 从零构造 docx | 永远 `shutil.copy` 复制模板再填充 |
| 2 | **缺少表格** | 只填充了段落，忽略了表格 | 完整分析并复制所有表格结构 |
| 3 | **表格行列错** | 手动构造表格，行列不匹配 | 复制模板表格结构，只修改单元格内容 |
| 4 | **段落顺序错** | 按数据逻辑顺序写，不按模板顺序 | 严格按模板段落顺序填充 |
| 5 | **格式丢失** | 样式未继承，run 被覆盖 | 复制模板后只修改文本内容，不改样式 |
| 6 | **制表符丢失** | 用空格代替制表符 | 保留原始 `\t` 字符位置 |
| 7 | **混合格式断裂** | 同一段落内 Bold + 普通文字被拆开 | 操作 run 级别，不整体替换段落 |
| 8 | **单元格样式丢失** | 直接设 `cell.text` 清除格式 | 用 `cell.paragraphs[0].clear()` + `add_run()` |
| 9 | **新增行格式不一致** | 新行没有继承模板行样式 | 从模板行复制格式后添加新行 |
| 10 | **论文段落格式错** | 论文编号、标题、期刊混合格式错误 | 复制模板论文段落的格式指纹，逐 run 匹配 |

## 快速参考：python-docx 常用操作

```python
from docx import Document
from docx.shared import Pt, RGBColor

# 读取文档
doc = Document('file.docx')

# 访问段落
doc.paragraphs[0].text          # 获取文本
doc.paragraphs[0].style.name    # 获取样式名
for run in doc.paragraphs[0].runs:
    run.text = 'new'            # 修改 run 文本

# 访问表格
table = doc.tables[0]
table.rows[0].cells[0].text     # 访问单元格
table.add_row()                 # 添加新行

# 添加新段落
p = doc.add_paragraph('text')
p.style = doc.styles['Heading 2']
run = p.add_run('bold text')
run.bold = True

# 保存
doc.save('output.docx')
```
