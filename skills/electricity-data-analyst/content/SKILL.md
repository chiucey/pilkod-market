---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: d2dded7acfe497a8c2649b5f2bf28f59
    PropagateID: d2dded7acfe497a8c2649b5f2bf28f59
    ReservedCode1: 30460221009eaebcfaf3b2c14c24ceb2cf251e0af2874df505b785388d455fff559b174d00022100e29db0bee6f08c3cebf3a4dcdcd211001c8930f71a890557a19c32ff031ece21
    ReservedCode2: 3045022100fa31f88dd9a37b71d23d1af3d9ea7a8c5980f13a9da9fb067909ae9dea319e0f02203e6a6f9dd4a4b0437feb69d7ff710e17f6a9818b0a9cd5950fe431f7d725535e
description: Electricity customer consumption data analysis skill. Use when users ask to analyze electricity bills, calculate time-of-use electricity fees (peak/shoulder/flat/valley periods), generate consumption statistics reports, or visualize usage trends. Triggers include "analyze bills", "consumption statistics", "time-of-use pricing", "peak-valley", "usage trends", "electricity analysis", "power data".
name: electricity-data-analyst
---

# 电力客户用电数据分析师

## 技能概述

本技能用于分析电力客户的用电数据，从客户每月的账单中提取信息，统计分时段用电量及电费，并可视化展示用电变化趋势。

## 数据结构理解

### 输入数据结构

```
账单文件/
├── 2024-01账单.xlsx (或CSV/PDF)
├── 2024-02账单.xlsx
└── ...

每个账单文件包含：
├── 分界室1
│   ├── 户号: "***"
│   ├── 户名: "***"
│   ├── 集团户名: "***"
│   ├── 用电类别: "大工业"
│   ├── 市场化属性: "市场化用户"
│   ├── 计量点1
│   │   └── 电表号: "***"
│   └── 计量点2
│       └── 电表号: "***"
└── 分界室2
    └── ...
```

### 分时段电价结构

| 时段 | 标识 |
|------|------|
| 尖段 | peak |
| 峰段 | shoulder |
| 平段 | flat |
| 谷段 | valley |

## 工作流程

### 阶段一：数据统计

1. **读取账单文件**
   - 支持格式：Excel (.xlsx, .xls)、CSV、PDF
   - 从文件名提取月份信息（如"2024-01账单"）
   - 递归扫描账单目录

2. **解析账单内容**
   - 遍历所有分界室（billing_point）
   - 遍历每个分界室下的计量点（meter_point）
   - 汇总同一分界室的全部计量点数据

3. **数据提取字段映射**

   | 目标字段 | 说明 |
   |----------|------|
   | 户号 | customer_id |
   | 户名 | customer_name |
   | 集团户名 | group_name |
   | 用电类别 | usage_category |
   | 市场化属性 | market_attribute |
   | 本期电量 | total_power_kwh |
   | 本期电费 | total_cost_yuan |
   | 平均电价 | avg_price |
   | 尖段_计费电量 | peak_kwh |
   | 尖段_计费标准 | peak_rate |
   | 尖段_电费 | peak_cost |
   | 峰段_计费电量 | shoulder_kwh |
   | 峰段_计费标准 | shoulder_rate |
   | 峰段_电费 | shoulder_cost |
   | 平段_计费电量 | flat_kwh |
   | 平段_计费标准 | flat_rate |
   | 平段_电费 | flat_cost |
   | 谷段_计费电量 | valley_kwh |
   | 谷段_计费标准 | valley_rate |
   | 谷段_电费 | valley_cost |
   | 输配容需量电费 | capacity_cost |
   | 功率因数调整电费 | power_factor_cost |

4. **生成统计表格**
   - 按月份汇总
   - 计算各时段小计
   - 输出CSV/Excel格式

### 阶段二：数据可视化

1. **趋势图绘制**
   - 横轴：月份
   - 纵轴：对应数值
   - 每张图仅展示一个指标

2. **需绘制图表列表**

   ```
   本期电量趋势图
   本期电费趋势图
   平均电价趋势图
   尖段_计费电量趋势图
   尖段_计费标准趋势图
   尖段_电费趋势图
   峰段_计费电量趋势图
   峰段_计费标准趋势图
   峰段_电费趋势图
   平段_计费电量趋势图
   平段_计费标准趋势图
   平段_电费趋势图
   谷段_计费电量趋势图
   谷段_计费标准趋势图
   谷段_电费趋势图
   输配容需量电费趋势图
   功率因数调整电费趋势图
   ```

3. **图表格式**
   - 格式：PNG
   - 尺寸：建议 1920x1080 或 1280x720
   - 保存路径：`charts/` 目录

## 执行脚本

### 数据统计脚本 (analyze_bills.py)

```python
# 主要功能：
# 1. 扫描账单目录
# 2. 解析账单文件（支持xlsx/csv/pdf）
# 3. 提取分时段电量电费数据
# 4. 按月汇总生成表格
# 5. 输出统计结果
```

### 数据可视化脚本 (visualize_trends.py)

```python
# 主要功能：
# 1. 读取统计结果
# 2. 使用matplotlib绑定趋势图
# 3. 保存为PNG文件
```

## 输出目录结构

```
output/
├── statistics/
│   └── monthly_summary.csv
└── charts/
    ├── total_power_trend.png
    ├── total_cost_trend.png
    ├── avg_price_trend.png
    ├── peak_kwh_trend.png
    ├── peak_rate_trend.png
    ├── peak_cost_trend.png
    ├── shoulder_kwh_trend.png
    ├── shoulder_rate_trend.png
    ├── shoulder_cost_trend.png
    ├── flat_kwh_trend.png
    ├── flat_rate_trend.png
    ├── flat_cost_trend.png
    ├── valley_kwh_trend.png
    ├── valley_rate_trend.png
    ├── valley_cost_trend.png
    ├── capacity_cost_trend.png
    └── power_factor_cost_trend.png
```

## 使用示例

### 示例1：基础统计

```
用户：请分析 /data/customer_bills 目录下的所有账单，生成用电统计表
助手：[执行数据统计脚本，生成 monthly_summary.csv]
```

### 示例2：带可视化

```
用户：请分析账单并生成统计表和趋势图
助手：[执行统计脚本生成报表] → [执行可视化脚本生成17张趋势图]
```

## 错误处理

1. **文件读取失败**
   - 记录错误日志
   - 跳过该文件继续处理其他文件
   - 在最终报告中标注失败的文件

2. **字段缺失**
   - 使用默认值（0或空字符串）
   - 在日志中记录警告

3. **数据格式错误**
   - 尝试数值转换
   - 转换失败时标记为无效数据

## 依赖要求

- Python 3.8+
- pandas
- openpyxl (Excel支持)
- matplotlib
- pdfplumber 或 camelot (PDF支持)
