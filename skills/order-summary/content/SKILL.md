---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 937c3682de698d537c1360b9670bc278
    PropagateID: 937c3682de698d537c1360b9670bc278
    ReservedCode1: 3045022100dd857bd5ae77d57df14ec2cbbbe672a3403a4ecf700b9195233b0ce8a1f5b4a802204598d0c1752297314118b7377cf0ca3d2b99d7dfa257509350fe04eb21211a3a
    ReservedCode2: 304602210088024e4873981fd33a4ea751207724cd244cb428671fbf01ec0cdbec64493fdf02210098248bdb974615b88f784e1e9713a8f1f1b49af21549bc80582db6779a9546b0
description: 采购订单和委外订单汇总技能。当用户上传采购订单列表和委外订单列表，需要按照模板格式汇总数据输出Excel文件时使用。触发词：订单汇总、采购订单、委外订单、供应商汇总、未到货订单汇总
name: order-summary
---

# 订单汇总技能

根据上传的采购订单和委外订单数据，按照标准模板汇总生成Excel文件。

## 工作流程

### 1. 数据收集
收集用户上传的文件：
- 采购订单列表（Excel格式）
- 委外订单列表（Excel格式）

### 2. 数据处理

使用 Python 脚本处理数据：

```python
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from datetime import datetime, timedelta
import pandas as pd

def process_orders(purchase_file, outsource_file, template_file):
    """处理采购和委外订单，生成汇总表"""
    # 读取数据
    purchase_df = pd.read_excel(purchase_file)
    outsource_df = pd.read_excel(outsource_file)

    # 合并数据
    all_orders = pd.concat([purchase_df, outsource_df], ignore_index=True)

    # 计算到货状态
    current_date = datetime.now()
    all_orders['days_until_due'] = (pd.to_datetime(all_orders['要求到货日期']) - current_date).dt.days

    # 风险等级判断
    def get_status(days):
        if days < 0:
            return f"已超期{abs(days)}天"
        elif days == 0:
            return "临期(0天)"
        elif days <= 3:
            return f"临期({days}天)"
        elif days <= 7:
            return f"近期({days}天)"
        else:
            return f"正常({days}天)"

    all_orders['到货状态判断'] = all_orders['days_until_due'].apply(get_status)

    # 按供应商分组
    suppliers = all_orders.groupby('供应商')

    return all_orders, suppliers
```

### 3. 生成Excel输出

按照模板格式生成Excel文件，包含以下工作表：

| 工作表 | 内容 |
|--------|------|
| 📖使用说明 | 使用说明和颜色图例 |
| ⚠️超期临期需跟进 | 已超期和临期的订单 |
| 📋全部未到货汇总 | 所有未到货订单汇总 |
| [供应商名称] | 各供应商的独立订单明细 |

### 4. 数据列规范

| 列名 | 说明 | 数据类型 |
|------|------|----------|
| 订单类型 | 采购订单/委外订单 | 文本 |
| 供应商 | 供应商全称 | 文本 |
| 订单编号 | 采购单号或委外单号 | 文本 |
| 存货编码 | 物料编码 | 文本 |
| 存货名称 | 物料名称 | 文本 |
| 规格型号 | 物料规格 | 文本 |
| 数量 | 订购数量 | 数字 |
| 累计到货数量 | 已到货数量 | 数字 |
| 累计入库数量 | 已入库数量 | 数字 |
| 计划到货日期 | 计划交货日期 | 日期 |
| 承诺到货日期 | 承诺交货日期 | 日期 |
| 要求到货日期 | 要求交货日期 | 日期 |
| 到货状态判断 | 当前状态 | 文本 |
| 预计货期 | 预计到货时间 | 文本 |

### 5. 风险等级颜色

| 状态 | 颜色 | 说明 |
|------|------|------|
| 已超期 | 红色 (#FF6B6B) | 需要立即跟进 |
| 临期 | 橙色 (#FFA94D) | 3天内需关注 |
| 近期 | 黄色 (#FFE066) | 7天内需关注 |
| 正常 | 绿色 (#69DB7C) | 正常跟进 |

## 输出要求

1. 生成 Excel 文件（.xlsx格式）
2. 文件命名：`供应商未到货订单汇总_YYYYMMDD.xlsx`
3. 按要求到货日期升序排列
4. 超期订单显示在前面
5. 为不同风险等级添加颜色标注

## 执行示例

```
用户上传：采购订单.xlsx、委外订单.xlsx
↓
处理数据，合并所有订单
↓
按供应商分组汇总
↓
按模板格式生成Excel
↓
输出：供应商未到货订单汇总_20260414.xlsx
```
