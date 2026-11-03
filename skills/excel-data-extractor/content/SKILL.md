---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: be58c8d94f10bcb0bab42a4ca0513098
    PropagateID: be58c8d94f10bcb0bab42a4ca0513098
    ReservedCode1: 304402206e4dff6ac246d6e3093301d73af9e03c726f78d5af519a7a7052cadda6c502a8022078fc900e8cfc7785a237899b7b3549552d22892c16c8d9e8e2372ad2212078f8
    ReservedCode2: 3046022100df83879d3db92dbd80d0057c3f7033867a389f3cce2c397c66e06bc1bf3f0318022100b2b795a4adc94628ce240964f8b6c254ae09582d4dccc953dc701adc3e7c2174
---

---
name: excel-data-extractor
description: "从Excel文件中提取非结构化数据，生成标准化JSON。适用于电梯维修询价单、报价单等业务Excel表格的数据提取。当用户提供Excel文件并要求提取全部信息、识别数据字段、生成JSON时，使用此技能。"
---

# Excel 数据提取器

## 概述

将Excel中的非结构化业务数据（如维修询价单、报价单等）提取为标准化JSON格式。支持公式单元格识别、手动计算、维修编号提取、费用一致性校验。

## 最佳案例

提取数据时，参考以下两个案例的JSON结构和字段命名规范：

1. **询价单案例** — `references/case_inquiry.json`：键值对型表格（标题行+1行数据），36个字段扁平结构
2. **报价单案例** — `references/case_quotation.json`：混合结构型表格（正文段落+费用核算+部件明细列表17项），含公式计算、大写金额转换、费用一致性校验

## 工作流程

### 第1步：读取原始数据

使用 `scripts/extract_excel.py` 读取Excel文件的所有单元格数据（含公式），获取完整的工作表结构。

```bash
python scripts/extract_excel.py <excel_file> --mode structured
```

对于不同结构的Excel：
- **键值对型**（如询价单，标题行+1行数据）：使用 `--mode kv`
- **混合结构型**（如报价单，含文字段落+明细表格）：使用 `--mode structured`
- **自动检测**（默认）：使用 `--mode auto`

### 第2步：提取文件元信息

1. **维修编号**：从文件名中提取 `WX` 开头的编号（如 `WX2603018B`），使用脚本中的 `extract_wx_number()` 函数
2. **工作表信息**：记录工作表名称、行数、列数

### 第3步：识别与提取数据

按以下规则提取数据：

- **字段名称**：沿用表格内原始字段名，不做翻译或改写
- **空值**：保留为 `null`
- **公式单元格**：
  - 记录原始公式字符串
  - 使用 `Decimal` 类型手动计算结果（避免浮点精度丢失）
  - 将计算结果填入JSON
  - 在对应的"说明"字段中标注 `(公式计算)` 或 `计算说明`

#### 特殊公式处理

- **乘法公式**（如 `=X61*Z61` 含税小计）：使用 `calculate_formula_product()` 计算
- **求和公式**（如 `=SUM(AE61:AI78)`）：遍历范围内的单元格，逐项使用 Decimal 累加
- **ROUND公式**（如 `=ROUND(...,0)`）：计算后四舍五入
- **大写金额**：忽略原公式，使用 `number_to_chinese()` 函数自行转换

### 第4步：费用一致性校验

提取完成后，比较以下两个字段：
1. **费用核算中的"部件费"**：报价单正文区域的部件费金额
2. **附件部件明细的"部件费小计"**：明细表格中各部件含税小计之和

使用 `compare_totals(cost_part_fee, detail_subtotal)` 函数进行比较：

```python
from scripts.extract_excel import compare_totals
result = compare_totals(140754.35, 159052.41)
# 返回差异信息或 None（无差异时）
```

### 第5步：生成JSON并提醒用户

生成JSON文件后，**必须**执行以下检查并提醒：

1. 如果费用核算中的部件费与部件明细小计存在差异，在输出结果末尾追加以下提醒：

```
⚠️ 费用一致性提醒：
- 费用核算中的部件费：XXX 元
- 部件明细含税小计合计：XXX 元
- 差额：XXX 元
差异原因可能为税费口径不同或存在未列入明细的附加费用，请核实。
```

2. 如果存在公式单元格缓存值为0（未经Excel重新计算），在JSON的 `计算说明` 字段中标注："原文件公式单元格缓存值为0，此处为手动计算值。"

## JSON结构规范

参考 `references/case_inquiry.json` 和 `references/case_quotation.json` 中的结构：

### 询价单JSON结构
```json
{
  "文件信息": {
    "原始文件名": "...",
    "维修编号": "WXXXXX 或 null",
    "说明": "文件名中不包含WX开头的维修编号（仅当为null时）",
    "工作表": "...",
    "数据行数": N,
    "数据列数": N
  },
  "询价单数据": {
    "<字段名>": "<值>",
    ...
  }
}
```

### 报价单JSON结构
```json
{
  "文件信息": {
    "原始文件名": "...",
    "维修编号": "WXXXXX",
    "工作表": "...",
    "数据行数": N,
    "数据列数": N
  },
  "报价单基本信息": { ... },
  "询价内容": { ... },
  "报价内容": { ... },
  "费用核算": {
    "部件费": N,
    "包装费": N,
    "运输费": N,
    ...
  },
  "报价合计": {
    "公式": "=ROUND(...)",
    "计算说明": "...",
    "计算结果": N
  },
  "大写金额": {
    "原文": "=ROUND(...)",
    "数值": N,
    "大写金额": "壹拾X万X仟X佰X拾X圆整"
  },
  "交货期": { ... },
  "支付条件": "...",
  "交货方式": "...",
  "说明事项": { ... },
  "报价方信息": { ... },
  "附件_部件明细": {
    "附件标题": "部件明细",
    "列定义": { "序号": "A列", ... },
    "部件列表": [
      {
        "序号": N,
        "品目": "...",
        "部件名称": "...",
        "型号": "... 或 null",
        "图号": "... 或 null",
        "G番": "... 或 null",
        "L番": "... 或 null",
        "参数": "... 或 null",
        "数量": N,
        "含税单价_元": N,
        "含税小计_元": N,
        "含税小计说明": "N × N = N（公式计算）",
        "备注": "... 或 null"
      }
    ],
    "部件费小计": {
      "公式": "=SUM(...)",
      "计算结果": N,
      "计算说明": "...",
      "差异说明": "仅当与费用核算中的部件费不一致时添加此字段"
    }
  }
}
```

## 脚本参考

### scripts/extract_excel.py

提供以下工具函数：

| 函数 | 用途 |
|------|------|
| `read_all_cells(path)` | 读取所有单元格（含公式） |
| `extract_kv_table(path)` | 提取键值对型表格 |
| `extract_structured_sheet(path)` | 提取结构化混合表格 |
| `safe_decimal(val)` | 安全转换为Decimal |
| `calculate_formula_product(formula, cells_map)` | 计算乘法公式 |
| `number_to_chinese(num)` | 数字转大写中文金额 |
| `extract_wx_number(filename)` | 从文件名提取WX编号 |
| `compare_totals(a, b)` | 比较两个金额，返回差异信息 |

## 重要注意事项

- **禁用浮点数累加**：所有金额计算必须使用 `Decimal` 类型，绝不可使用 `float`，避免精度丢失
- **公式计算结果需验证**：手动计算的公式结果应在JSON中标注计算过程
- **保留原始信息**：JSON中应同时保留原始公式字符串和计算后的值
