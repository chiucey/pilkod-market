---
name: excel-operator
description: Excel and spreadsheet operation expert. Use when users request creating Excel files, reading data, editing spreadsheets, adding formulas, creating charts, data analysis, or CSV/TSV file operations.
---

# Excel/电子表格操作专家

## 核心能力

基于 OpenXML SDK 实现，专注于「创建/读取/编辑/分析/验证」Excel 文件（.xlsx/.xlsm/.csv/.tsv）。

## 支持的操作

| 操作类型 | 说明 | 示例 |
|----------|------|------|
| 创建 | 新建工作簿/工作表 | 创建工资表、销售报表 |
| 读取 | 读取单元格数据 | 提取销售数据 |
| 编辑 | 修改/格式化单元格 | 更新价格、调整格式 |
| 公式 | 添加计算公式 | SUM、AVERAGE、VLOOKUP |
| 图表 | 创建数据图表 | 柱状图、折线图、饼图 |
| 验证 | 数据有效性验证 | 下拉列表、数字范围 |

## 支持的文件格式

| 格式 | 说明 | 兼容性 |
|------|------|--------|
| .xlsx | Excel 2007+ | Excel 2016+ |
| .xlsm | 启用宏的Excel | 需启用宏 |
| .csv | 逗号分隔值 | 通用格式 |
| .tsv | 制表符分隔值 | 通用格式 |

## 工作流程

### 步骤 1：需求收集

主动确认以下要素（使用 GenUI 表单）：

| 字段 | 说明 | 示例 |
|------|------|------|
| 操作类型 | 具体任务 | 创建 / 读取 / 编辑 / 分析 |
| 文件路径 | 现有文件路径 | "data/sales.xlsx" |
| 具体要求 | 详细需求描述 | "计算每行总和并添加平均" |
| 输出格式 | 期望的文件格式 | .xlsx / .csv / .pdf |

**触发表单**：多页 GenUI 表单，收集以上信息。

### 步骤 2：执行操作

**使用 MiniMax Xlsx CLI 工具**：

```bash
# 创建工作簿
minimax-xlsx create --output report.xlsx

# 读取数据
minimax-xlsx read --file data.xlsx --sheet Sheet1

# 添加公式
minimax-xlsx formula --file report.xlsx --cell "B10" --formula "=AVERAGE(B2:B9)"
```

**支持的公式类型**：

| 类别 | 函数 | 说明 |
|------|------|------|
| 数学 | SUM, AVERAGE, COUNT, MAX, MIN | 基本统计 |
| 逻辑 | IF, AND, OR, NOT | 条件判断 |
| 查找 | VLOOKUP, HLOOKUP, INDEX, MATCH | 数据查找 |
| 文本 | CONCATENATE, LEFT, RIGHT, MID | 文本处理 |
| 日期 | TODAY, NOW, DATEDIF | 日期计算 |

### 步骤 3：结果交付

**输出内容**：

```
## 操作结果

### 文件信息
- 文件路径：[路径]
- 工作表数量：[X]
- 数据范围：[A1:Z100]

### 操作日志
- [已完成] 创建工作表 "销售数据"
- [已完成] 写入数据 100 行
- [已完成] 添加求和公式 =SUM(B2:B100)
- [已完成] 创建柱状图

### 数据预览
| 列A | 列B | 列C |
|-----|-----|-----|
| 数据1 | 数据2 | 数据3 |

### 分析结果
- 平均值：[X]
- 总和：[Y]
- 最大值：[Z]
```

## 分析功能

当用户请求数据分析时，提供：

| 分析类型 | 输出 |
|----------|------|
| 描述性统计 | 平均值、标准差、极值 |
| 趋势分析 | 月度/季度变化 |
| 数据可视化 | 图表（Mermaid/PNG） |
| 汇总报告 | 分类统计、交叉分析 |

## 交付物

完成后输出：

```xml
<genui-skill-card name="excel-operator" desc="Excel/电子表格操作专家" skill-id="xxx"></genui-skill-card>
```

**Summary**: Excel文件已处理
**Description**: 已完成 [操作类型]，文件已保存至 [路径]，包含 [数据行数] 行数据

<deliver_assets>
<item>
<path>output/result.xlsx</path>
<name>Excel文件</name>
</item>
<item>
<path>output/analysis-report.md</path>
<name>分析报告</name>
</item>
<item>
<path>output/chart.png</path>
<name>数据图表</name>
</item>
</deliver_assets>

## 质量标准

| 标准 | 要求 |
|------|------|
| 准确性 | 公式计算正确 |
| 兼容性 | 兼容 Excel 2016+ |
| 格式规范 | CSV/TSV 符合标准 |
| 数据完整 | 无数据丢失 |

## 限制与注意事项

1. **文件状态**：不处理加密或损坏文件
2. **数据隐私**：不泄露敏感信息
3. **宏操作**：复杂宏需告知用户替代方案
4. **文件大小**：大文件处理可能需要更长的时间

## 技术工具

- **MiniMax Xlsx CLI**：结构化操作、公式验证
- **Python (openpyxl/pandas)**：数据分析处理
- **LibreOffice**：格式转换（CSV→XLSX）
