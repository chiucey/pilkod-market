---
name: excel-group-summary
description: "Excel多维度分组汇总技能。基于Excel数据源，按指定维度（项目类别、项目名称等）进行分组统计汇总，支持同类单元格自动合并、货币格式化、OpenXML合规性验证。触发词：分组汇总、分类统计、按类别汇总"
license: MIT
metadata:
  version: "1.0"
  category: productivity
---

# Excel 多维度分组汇总技能

> 基于 Excel 数据源，按指定维度（项目类别、项目名称等）进行分组统计汇总，支持同类单元格合并

## 功能概述

本技能可将 Excel 原始数据快速转换为专业级分组汇总表：
- 按指定列分组统计求和
- 自动计算小计和总计
- 同类别单元格智能合并
- 自动格式化（货币格式、表头样式）
- OpenXML 合规性验证

## 核心参数

| 参数 | 说明 | 必填 |
|-----|------|-----|
| `source_file` | 源 Excel 文件路径 | 是 |
| `source_sheet` | 源工作表名称 | 是 |
| `group_cols` | 分组维度列名（逗号分隔） | 是 |
| `sum_col` | 需要汇总的金额列名 | 是 |
| `output_file` | 输出文件路径 | 是 |
| `merge_cols` | 需要合并单元格的列名（逗号分隔） | 否 |

## 工作流程

### Phase 1 - 数据读取与验证

```python
import pandas as pd
from openpyxl import load_workbook

def read_source_data(source_file, source_sheet):
    """读取源 Excel 数据"""
    df = pd.read_excel(source_file, sheet_name=source_sheet)
    return df
```

### Phase 2 - 分组汇总计算

```python
def group_and_sum(df, group_cols, sum_col):
    """执行分组汇总"""
    grouped = df.groupby(group_cols)[sum_col].sum().reset_index()
    return grouped
```

### Phase 3 - 生成带合并的汇总表

```python
def create_summary_with_merges(df, merge_cols):
    """创建汇总表并合并同类单元格"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils.dataframe import dataframe_to_rows

    wb = Workbook()
    ws = wb.active
    ws.title = "分组汇总"

    # 写入表头
    # 写入数据
    # 应用单元格合并
    # 应用格式化

    return wb
```

### Phase 4 - OpenXML 合规性验证

```bash
./scripts/MiniMaxXlsx check output.xlsx
```

## 使用示例

### 示例1：基础分组汇总

**输入数据 (source.xlsx)**:

| 项目类别 | 项目名称 | 金额 |
|---------|---------|------|
| 办公用品 | 打印机 | 2500 |
| 办公用品 | 复印纸 | 500 |
| 电子设备 | 笔记本电脑 | 8000 |
| 电子设备 | 显示器 | 3000 |

**执行命令**:

```python
source_file = "source.xlsx"
source_sheet = "Sheet1"
group_cols = ["项目类别"]
sum_col = "金额"
output_file = "summary_output.xlsx"

# 调用分组汇总逻辑
```

**输出结果 (summary_output.xlsx)**:

| 项目类别 | 金额汇总 |
|---------|---------|
| 办公用品 | 3,000 |
| 电子设备 | 11,000 |
| **总计** | **14,000** |

### 示例2：多维度分组汇总

**输入数据**:

| 项目类别 | 项目名称 | 金额 |
|---------|---------|------|
| 办公用品 | 打印机 | 2500 |
| 办公用品 | 复印纸 | 500 |
| 电子设备 | 笔记本电脑 | 8000 |
| 电子设备 | 显示器 | 3000 |

**执行命令**:

```python
group_cols = ["项目类别", "项目名称"]
merge_cols = ["项目类别"]
```

**输出结果**:

| 项目类别 | 项目名称 | 金额 |
|---------|---------|------|
| 办公用品 | 打印机 | 2,500 |
| | 复印纸 | 500 |
| | **小计** | **3,000** |
| 电子设备 | 笔记本电脑 | 8,000 |
| | 显示器 | 3,000 |
| | **小计** | **11,000** |
| | **总计** | **14,000** |

## 格式化规范

### 表头样式
- 字体：微软雅黑 12pt 加粗
- 背景色：#4472C4（蓝色）
- 文字颜色：白色
- 居中对齐

### 货币格式
- 格式代码：`¥#,##0`
- 负数格式：`¥-#,##0`

### 合并单元格规则
- 仅合并同一列中相邻的相同值
- 合并后居中显示
- 边框保持完整

## 验证清单

- [ ] 数据完整性检查（无空行、无重复键）
- [ ] 汇总数值准确性（抽样验证）
- [ ] 单元格合并正确性
- [ ] 货币格式化一致性
- [ ] OpenXML 合规性验证通过

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 文件不存在 | 提示用户检查文件路径 |
| Sheet 不存在 | 列出可用 Sheet 供选择 |
| 列名不匹配 | 提示正确列名 |
| 空数据 | 提示并终止执行 |

## 最佳实践

1. **数据预处理**：确保源数据干净无空值
2. **列名规范**：使用清晰的列名便于识别
3. **备份原文件**：汇总操作前备份源数据
4. **验证结果**：抽样检查汇总结果准确性
