---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 2fb9ba9b14b9da55ea6cb92a9219bc74
    PropagateID: 2fb9ba9b14b9da55ea6cb92a9219bc74
    ReservedCode1: 3046022100c4063f6868b0e3d69b60c41c12acced415b4d86693e64df9fc059e7818399e04022100f832eb884efc9b402f3976ac27809417171a0aec0f5e475b4c18907af0ac8ec7
    ReservedCode2: 3046022100d50d3f3707067b212d60b91fa8e57e8c05961012e478434bca5fac858a15ee7a022100efe733ed9f07b279ac421abc27acfbebe200200fcc57c7e75bcc0cbc162edc15
description: 处理公司基本信息Excel表格的工具。当用户上传"公司基本信息查询.xlsx"文件并要求按照固定规则处理时使用此技能。处理规则：1）筛选O列（一级类别），仅保留"协鑫能科"的行；2）仅保留D至I列（共6列：选择【现】组织分类、选择业务类别、选择业务细类、SAP编码、NC编码、主账套所在系统）和Z至AA列（共2列：公司全称中文、公司名称英文）；3）输出新的Excel文件供下载。
name: company-info-excel-processor
---

# 公司基本信息Excel处理器

## 触发条件

当用户上传包含"公司基本信息查询"字样的Excel文件，并要求按照固有规则处理时激活此技能。

## 输入要求

- **文件格式**：Excel文件（.xlsx）
- **文件结构**：包含80列的公司基本信息表
- **关键列**：
  - O列（索引14）：一级类别
  - D-I列（索引3-8）：组织分类信息
  - Z-AA列（索引25-26）：公司名称信息

## 处理流程

### 步骤1：读取Excel文件

使用 pandas 读取上传的Excel文件：

```python
import pandas as pd
df = pd.read_excel(file_path)
```

### 步骤2：筛选数据

筛选O列（一级类别）中内容为"协鑫能科"的行：

```python
o_column_name = df.columns[14]  # 获取O列列名
filtered_df = df[df[o_column_name] == '协鑫能科']
```

### 步骤3：选择列

保留指定的8列：

- **D至I列**（6列）：
  - 选择【现】组织分类
  - 选择业务类别
  - 选择业务细类（先选业务类别）
  - SAP编码
  - NC编码
  - 主账套所在系统

- **Z至AA列**（2列）：
  - 公司全称（中文）
  - 公司名称（英文）

```python
columns = list(df.columns)
selected_columns = columns[3:9] + columns[25:27]
result_df = filtered_df[selected_columns].copy()
```

### 步骤4：生成输出文件

- 重置DataFrame索引
- 保存为新的Excel文件
- 文件命名格式：`协鑫能科_公司基本信息_处理结果.xlsx`

## 输出产物

- **文件格式**：Excel (.xlsx)
- **行数**：筛选后的行数（通常约1458行）
- **列数**：8列（固定）
- **保存位置**：`output/` 目录

## 执行脚本

完整的处理脚本位于 `scripts/process_company_info.py`。

执行方式：

```bash
python scripts/process_company_info.py <输入文件路径>
```

## 验收标准

1. ✅ 输出文件包含且仅包含指定的8列
2. ✅ 仅保留"协鑫能科"相关数据行
3. ✅ 输出文件可正常打开并包含正确数据
4. ✅ 数据行数与筛选条件匹配

## 注意事项

- 保持原始数据的完整性，不修改数据内容
- 输出时移除pandas默认索引列
- 确保输出目录存在
