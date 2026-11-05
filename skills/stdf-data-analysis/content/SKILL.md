---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: f6f6e0449327196e0e38a7c224b4c17b
    PropagateID: f6f6e0449327196e0e38a7c224b4c17b
    ReservedCode1: 3044022065010bd66c00ca3eb6916b5961f7166abbaa2683d4d7cea56802db883bff7c6402202c6678e074fa7962fe56574daf6a6724a45de6fd1fdc4b6f1ab3cc0ef48347a6
    ReservedCode2: 3046022100fde6cbd68032e250a96381a71ed13f40700f6521c702937ad15bbac36e0336700221009bbee5a9431b8cdf962963f0b9faa64de5923a161bb671e84ec27b45bffac3e8
name: stdf-data-analysis
version: 1.2.0
description: 解析半导体行业FT测试生成的STDF/STD文件，进行数据统计分析并给出生产评价。当用户询问测试数据分析、良率报告、过程能力（CPK）、根因分析或改进建议时使用。也用于根据ChipID查找特定芯片的测试数据。支持Hard Bin/Soft Bin分布分析，支持FTR功能测试记录解析。
---

# STDF Data Analysis v1.2.0

## 功能概述

解析半导体 FT 测试生成的 STDF/STD 文件，自动计算统计指标并给出生产状态评价。

## 依赖要求

- Python 3.7+
- 无需额外安装第三方库（使用标准库）

## 输入要求

用户提供以下之一：
1. **STDF/STD 文件路径**：二进制格式的测试数据文件
2. **CSV 文件**：已解析的测试数据
3. **ChipID 组合**：用于查找特定芯片 `(id0, id1, id2, id3)`

## 执行流程

### 1. 文件解析

```
STDF 二进制解析 → 提取 PIR/PRR/PTR/FTR 记录 → 转换为 DUT 数据
```

关键记录类型：
- **PIR** (REC_TYP=5, REC_SUB=10): 芯片开始标记
- **PRR** (REC_TYP=5, REC_SUB=20): 芯片结果记录
- **PTR** (REC_TYP=15, REC_SUB=10): 参数测试结果
- **FTR** (REC_TYP=15, REC_SUB=20): 功能测试结果

### 2. 数据统计

对每个测试项计算：
- 最大值 (MAX)
- 最小值 (MIN)
- 均值 (MEAN)
- 中位数 (MEDIAN)
- 样本标准差 (STD) - 使用 n-1 计算
- CPK (过程能力指数) - 需要规格限
- 异常点数量 (超过 3σ)

### 3. Bin 分布分析

- **Hard Bin**：硬件分类，反映失效硬件位置
- **Soft Bin**：软件分类，反映失效测试项

### 4. FTR 功能测试解析

解析功能测试记录，包含：
- 测试名称
- 测试结果 (pass/fail)
- 位图数据
- 循环计数

### 5. ChipID 查找

根据用户提供的 ChipID 组合 `(read_chipid_0, read_chipid_1, read_chipid_2, read_chipid_3)` 匹配芯片。

### 6. 输出报告

```
【整体生产状态评价】
- 批次质量水平
- 良率统计
- 稳定性评价

【关键风险项】
- Cpk < 1.33 的测试项
- 异常点超过 3σ 的项目

【Bin 分布分析】
- Hard Bin 分布统计
- Soft Bin 分布统计
- 失效模式识别

【FTR 功能测试结果】
- 功能测试通过率
- 失败的功能测试项

【可能原因分析】
- 测试设备偏移
- 工艺波动
- 材料问题

【改进建议】
- 具体可执行的行动建议
```

## 输出格式

### 参数测试 CSV 文件格式 (output.csv)

| 列 | 说明 |
|----|------|
| #1 | 行号标识 |
| Part ID | 芯片序号 |
| Head - Site | 测试机台和站点 |
| Hard Bin | 硬件分类 (如 Bin 1, Bin 6) |
| Soft Bin | 软件分类 |
| Pass | Pass/Fail |
| 测试项... | 各测试项的测量值 |

### FTR 功能测试 CSV 文件格式 (output_ftr.csv)

| 列 | 说明 |
|----|------|
| Part ID | 芯片序号 |
| Head | 测试机台 |
| Site | 测试站点 |
| Test Num | 测试编号 |
| Test Name | 测试名称 |
| Result | 结果值 |
| Passed | Pass/Fail |
| Options | 选项标志 |
| Cycles | 循环计数 |
| Bitmap | 位图数据 |

### 分析报告格式

1. **批次概况**：DUT 数量、良率、测试项数
2. **Bin 分布**：Hard Bin 和 Soft Bin 统计
3. **FTR 统计**：功能测试记录数和通过率
4. **风险报告**：高 CPK 风险项清单
5. **改进建议**：可执行的生产优化建议

## 脚本使用

### 解析 STDF 文件

```bash
python stdf_parser.py <input.std> [output.csv] [output_ftr.csv]
```

参数说明：
- `input.std`: 输入的 STDF/STD 文件
- `output.csv`: 输出的参数测试 CSV 文件 (可选)
- `output_ftr.csv`: 输出的功能测试 CSV 文件 (可选)

示例：
```bash
python stdf_parser.py test.std test.csv test_ftr.csv
```

### ChipID 查找

```bash
python chipid_finder.py <input.std> <id0> <id1> <id2> <id3>
```

示例：
```bash
python chipid_finder.py test.std 88 221 88 95
```

### 详细数据分析

```bash
python stdf_analyzer.py <statistics.json>
```

## 触发条件

- 用户上传 .std 或 .stdf 文件
- 用户询问良率/测试数据分析
- 用户需要 CPK 分析或根因分析
- 用户根据 ChipID 查找芯片
- 用户询问 Hard Bin/Soft Bin 分布
- 用户询问功能测试 (FTR) 结果

## 版本历史

- **v1.2.0**: 新增 FTR 功能测试解析，修复标准差计算，使用样本标准差
- **v1.1.0**: 初始版本
