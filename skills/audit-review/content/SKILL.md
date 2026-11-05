---
name: audit-review
description: "Use this skill when the user wants to analyze whether the review explanations (审核说明) in a spreadsheet adequately explain the review prompts/issues (审核提示). This skill is designed for quality audit scenarios where an Excel table contains columns for review prompts (问题/提示) and corresponding explanations (说明/解释), and the user needs to evaluate whether each explanation clearly and adequately addresses the issue raised. Trigger when the user asks to: check if explanations match prompts, evaluate review quality, find unclear or insufficient explanations, generate a list of poorly explained items, or create a new document with items that need re-review. The input must be a spreadsheet (.xlsx/.xlsm/.csv/.tsv). The deliverable is typically a new spreadsheet containing only the rows where explanations are unclear, with an additional column providing detailed analysis opinions (研判意见)."
license: Proprietary. LICENSE.txt has complete terms
---

# 审核匹配度分析技能 (Audit Review Matching Analysis)

## 概述

本技能用于分析电子表格中**审核提示**（问题列）与**审核说明**（解释列）之间的匹配度，判断每行审核说明是否能够清楚、充分地解释审核提示中提出的问题。

## 适用场景

- 统计调查数据质量审核
- 财务审计问题核实
- 合规检查问题反馈
- 任何包含"问题-说明"对应关系的表格审核

## 核心工作流程

### 第一步：读取与理解表格结构

```python
import pandas as pd
import openpyxl

file_path = '<input_file>'
wb = openpyxl.load_workbook(file_path)
df = pd.read_excel(file_path, sheet_name='<sheet_name>', header=None)

# 识别关键列
# 用户需指定：审核提示列（问题列）和审核说明列（解释列）
# 常见表头关键词：
#   审核提示列：审核提示、问题内容、审核问题、提示内容、问题描述
#   审核说明列：审核说明、说明、解释、核实说明、处理说明
```

**CRITICAL**: 必须先与用户确认哪一列是"审核提示"（问题列），哪一列是"审核说明"（解释列）。

### 第二步：逐行分析匹配度

对每一行数据，从以下 **6个维度** 进行分析评估：

#### 维度1：问题识别准确性
- 审核说明是否准确理解了审核提示中提出的问题？
- 是否存在对问题的误解或偏题？

#### 维度2：因果解释充分性
- 是否说明了问题产生的根本原因？
- 是否仅罗列现象而未解释原因？

#### 维度3：数据一致性
- 审核说明中提到的数据（金额、数量、编码等）是否与审核提示中的数据一致？
- 如果存在差异，是否做了解释？

#### 维度4：逻辑自洽性
- 审核说明的论述是否逻辑自洽？
- 是否存在与审核提示矛盾的说法？

#### 维度5：完整性
- 是否回答了审核提示中的所有关键问题？
- 是否遗漏了重要信息（如编码正确性、指标更新需求等）？

#### 维度6：可操作性
- 是否明确了问题是否需要修改？
- 是否指出了具体的修改方向或处理方式？

### 第三步：判定标准

| 判定结果 | 条件 |
|---------|------|
| **解释清楚** | 审核说明在所有6个维度上均表现良好，能够充分解释审核提示中的问题 |
| **解释不清楚** | 审核说明在1个或多个维度上存在明显不足，无法充分解释审核提示中的问题 |

#### 常见的"解释不清楚"问题类型

1. **说明与提示矛盾**：审核说明中的描述与审核提示的判断直接矛盾
2. **金额/数据不匹配**：说明中引用的数据与提示中的数据不一致且未解释差异
3. **解释过于简略**：仅一句话概括，未展开说明具体原因
4. **未涉及编码/指标正确性**：说明了情况但未说明编码或指标是否需要修改
5. **未说明指标更新需求**：有新增收入/支出但未说明问卷指标是否需更新
6. **回答与问题不对应**：说明内容与提示关注点不完全匹配
7. **解释不够具体**：未说明具体费用构成、品名、编码含义等
8. **仅列举未解释**：仅列举已有数据但未说明为什么数据偏低/偏高的原因
9. **缺少关键信息**：未说明人员去向、居住地、从业状态等关键背景信息

### 第四步：生成输出文档

使用 `scripts/audit_review.py` 脚本生成结果文档：

```bash
python scripts/audit_review.py <input_file> --prompt-col <col_name_or_index> --explanation-col <col_name_or_index> --output <output_file>
```

或直接使用 openpyxl 编程生成：

```python
import openpyxl
from openpyxl.styles import Alignment, Font
from copy import copy

# 创建新工作簿，保持原表格式
wb_new = openpyxl.Workbook()
ws_new = wb_new.active

# 复制表头（含原格式）
for col in range(1, max_col + 1):
    src_cell = ws_src.cell(row=1, column=col)
    dst_cell = ws_new.cell(row=1, column=col)
    dst_cell.value = src_cell.value
    dst_cell.font = copy(src_cell.font)
    dst_cell.fill = copy(src_cell.fill)
    dst_cell.border = copy(src_cell.border)
    dst_cell.alignment = copy(src_cell.alignment)

# 新增"研判意见"列
header_cell = ws_new.cell(row=1, column=new_max_col)
header_cell.value = '研判意见'
header_cell.font = Font(bold=True)
header_cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

# 仅复制"解释不清楚"的行
for src_row in unclear_row_indices:
    # 复制数据行（含原格式）
    ...
    # 添加研判意见（红色字体）
    reason_cell = ws_new.cell(row=new_row, column=new_max_col)
    reason_cell.value = analysis_reason
    reason_cell.alignment = Alignment(wrap_text=True, vertical='top')
    reason_cell.font = Font(color='FF0000')
```

## 输出格式规范

### 输出文件要求
- **格式**：与原表格式一致（.xlsx）
- **内容**：仅包含审核说明解释不清楚的行
- **新增列**：末尾新增"研判意见"列，用红色字体详细说明不清楚的具体原因
- **列宽**：自动适配内容长度，长文本列启用自动换行
- **样式迁移**：从源文件复制单元格样式（字体、填充、边框、对齐、数字格式）

### 研判意见撰写规范

每条研判意见应包含以下要素：
1. **引用审核提示的关键内容**：简要复述审核提示的核心问题
2. **指出审核说明的不足**：具体说明哪方面解释不清楚
3. **说明期望的回答方向**：指出审核说明应该补充什么内容

示例：
> 审核提示指出"赡养收入为21000元"，但审核说明称"最近买药买半年量的赡养收入是1万8"，金额（21000 vs 18000）不一致，审核说明未解释3000元的差异来源。

## 分析注意事项

### 关于审核说明质量的判断尺度

- **不要过于严苛**：对于基层调查员填写的说明，应考虑其知识水平和表达习惯，适度宽容
- **关注核心问题**：重点判断审核说明是否回答了审核提示中**最关键**的问题，而非要求面面俱到
- **结合业务常识**：某些说明虽然简略，但结合业务常识可以推断出完整含义的，不应判定为不清楚
- **区分"信息不足"和"表述不清"**：信息不足可能是因为调查员确实不知道更多细节；表述不清则是知道但没写清楚

### 关于特殊情况的判断

- **审核说明为空**：直接判定为解释不清楚，研判意见为"审核说明为空，未对审核提示中的问题进行任何解释"
- **审核说明为"情况属实"等套话**：判定为解释不清楚，研判意见应指出需要具体说明
- **审核说明引用了其他行的说明**：如果引用合理且能解释当前行的问题，可判定为清楚
- **同一问题多行重复说明**：如果说明内容模板化但能解释问题，可判定为清楚

## 完整分析示例代码

```python
import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, Font
from copy import copy
import json

def analyze_audit_review(file_path, sheet_name, prompt_col, explanation_col, output_path):
    """
    分析审核说明与审核提示的匹配度，生成不清晰问题清单

    Parameters:
        file_path: 输入文件路径
        sheet_name: 工作表名称
        prompt_col: 审核提示列名或索引（从0开始）
        explanation_col: 审核说明列名或索引（从0开始）
        output_path: 输出文件路径
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    wb_src = openpyxl.load_workbook(file_path)
    ws_src = wb_src[sheet_name]

    if isinstance(prompt_col, str):
        prompt_idx = list(df.iloc[0]).index(prompt_col)
    else:
        prompt_idx = prompt_col
    if isinstance(explanation_col, str):
        explanation_idx = list(df.iloc[0]).index(explanation_col)
    else:
        explanation_idx = explanation_col

    unclear_rows = []
    for i in range(1, df.shape[0]):
        prompt = str(df.iloc[i, prompt_idx]).strip() if pd.notna(df.iloc[i, prompt_idx]) else ""
        explanation = str(df.iloc[i, explanation_idx]).strip() if pd.notna(df.iloc[i, explanation_idx]) else ""
        result = evaluate_explanation(prompt, explanation)
        if not result['is_clear']:
            unclear_rows.append({
                'row': i + 1,
                'prompt': prompt,
                'explanation': explanation,
                'reason': result['reason']
            })

    generate_output(wb_src, ws_src, unclear_rows, output_path)
    return unclear_rows


def evaluate_explanation(prompt, explanation):
    """
    评估单行审核说明是否能解释清楚审核提示
    Returns: dict {'is_clear': bool, 'reason': str}
    """
    if not explanation or explanation in ['nan', '']:
        return {'is_clear': False, 'reason': '审核说明为空，未对审核提示中的问题进行任何解释。'}

    issues = []
    # 维度1-6分析逻辑（需根据具体业务场景结合LLM语义分析实现）
    # ...

    if issues:
        return {'is_clear': False, 'reason': '；'.join(issues)}
    return {'is_clear': True, 'reason': ''}


def generate_output(wb_src, ws_src, unclear_rows, output_path):
    """生成保持原表格式的新文档"""
    wb_new = openpyxl.Workbook()
    ws_new = wb_new.active
    ws_new.title = ws_src.title

    max_col = ws_src.max_column
    new_max_col = max_col + 1

    for col in range(1, max_col + 1):
        src_cell = ws_src.cell(row=1, column=col)
        dst_cell = ws_new.cell(row=1, column=col)
        dst_cell.value = src_cell.value
        dst_cell.font = copy(src_cell.font)
        dst_cell.fill = copy(src_cell.fill)
        dst_cell.border = copy(src_cell.border)
        dst_cell.alignment = copy(src_cell.alignment)
        dst_cell.number_format = src_cell.number_format

    header_cell = ws_new.cell(row=1, column=new_max_col)
    header_cell.value = '研判意见'
    header_cell.font = Font(bold=True)
    header_cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    new_row = 2
    for item in unclear_rows:
        src_row = item['row']
        for col in range(1, max_col + 1):
            src_cell = ws_src.cell(row=src_row, column=col)
            dst_cell = ws_new.cell(row=new_row, column=col)
            dst_cell.value = src_cell.value
            dst_cell.font = copy(src_cell.font)
            dst_cell.fill = copy(src_cell.fill)
            dst_cell.border = copy(src_cell.border)
            dst_cell.alignment = copy(src_cell.alignment)
            dst_cell.number_format = src_cell.number_format

        reason_cell = ws_new.cell(row=new_row, column=new_max_col)
        reason_cell.value = item['reason']
        reason_cell.alignment = Alignment(wrap_text=True, vertical='top')
        reason_cell.font = Font(color='FF0000')
        new_row += 1

    for col_idx in range(1, new_max_col + 1):
        max_len = max(
            (len(str(ws_new.cell(row=r, column=col_idx).value or ''))
             for r in range(1, new_row)),
            default=0
        )
        width = min(max(max_len + 2, 8), 60) if col_idx != new_max_col else min(max(max_len + 2, 20), 80)
        ws_new.column_dimensions[get_column_letter(col_idx)].width = width

    for r in range(2, new_row):
        for col_idx in range(1, new_max_col + 1):
            cell = ws_new.cell(row=r, column=col_idx)
            if len(str(cell.value or '')) > 50:
                cell.alignment = Alignment(wrap_text=True, vertical='top')

    wb_new.save(output_path)
```

## 依赖说明

本技能依赖以下Python库（已预装）：
- `openpyxl` — Excel文件读写和格式处理
- `pandas` — 数据分析
- `copy` — 样式复制

## Checklist

完成审核匹配度分析后，确认以下事项：
- [ ] 已正确识别审核提示列和审核说明列
- [ ] 每行分析覆盖了6个评估维度
- [ ] 研判意见包含：问题引用 + 不足指出 + 期望方向
- [ ] 输出文件保持了原表的格式和样式
- [ ] "研判意见"列使用红色字体
- [ ] 列宽已自动适配，长文本已启用换行
