---
name: stock-holder-add
description: A股大股东/高管增持价值分析工具。当用户提到"近N天增持执行公告"、"股东增持溢价"、"高管增持筛选"、"哪些公司大股东在增持"、"增持溢价率"时触发此技能。调用Tushare Pro的stk_holdertrade接口，筛选近7个自然日内发布增持公告（且增持主体为大股东或高管）的上市公司，汇总本次增持方案数据，计算增持均价与当日股价的溢价率（增持均价/当日股价），筛选溢价率>1的标的，并生成Excel报告。
version: 1.0.0
requirements:
  python: 3.7+
  environment_variables:
    - name: TUSHARE_TOKEN
      sensitive: true
      description: Tushare Pro API Token，不设置则读token.env
  network_access: true
---

# A股大股东/高管增持价值分析工具 v1.0

## 核心目标

通过调用Tushare数据库（`stk_holdertrade`接口），筛选近7天内发布增持公告、且增持主体为**大股东（公司）或高管（个人）**的上市公司，汇总本次增持方案的全部执行数据，计算增持均价与当日股价的溢价率，**仅输出溢价率>1**（增持均价高于当日股价）的标的，为投资决策提供依据。

---

## 触发词

- "近7天增持" / "近7日增持公告"
- "股东增持溢价"
- "高管增持筛选"
- "哪些公司在增持"
- "增持溢价率"
- "大股东增持"

---

## 数据来源与接口

| 数据 | Tushare接口 | 参数/说明 |
|------|------------|---------|
| 增持公告 | `stk_holdertrade` | start_date/end_date + trade_type=IN + holder_type in {G,C} |
| 股票名称 | `stock_basic` | 批量获取 |
| 当日股价 | `daily` | 最近交易日收盘价 |
| 交易日 | `trade_cal` | 确定股价基准日 |

**增持主体分类：**
- `holder_type=G`：高管（个人）
- `holder_type=C`：公司大股东

---

## 筛选与匹配规则

**步骤1：拉取近7日增持公告**
- `stk_holdertrade` 接口，`trade_type=IN`（增持），`holder_type` 筛选 G/C
- ann_date 用 start_date / end_date 参数

**步骤2：过滤**
- 仅 `in_de=IN` 且 `change_vol > 0`
- `avg_price` 缺失的记录：单独标注，不参与均价计算

**步骤3：按公司聚合**
- 同一公司同一次增持方案的所有记录汇总

**步骤4：计算增持均价与溢价率**

| 指标 | 计算 |
|------|------|
| 累计增持股数 | Σchange_vol（单位：股） |
| 累计增持金额 | Σ(change_vol × avg_price)，avg_price缺失则不纳入金额合计 |
| 增持均价 | 有金额记录时：总金额÷总股数 |
| 当日股价 | 最近交易日收盘价 |
| 溢价率 | 增持均价 ÷ 当日股价 |

**筛选：溢价率 > 1 → 纳入；否则剔除**

---

## 输出字段

| 字段 | 说明 |
|------|------|
| 股票代码 | A股标准代码 |
| 股票名称 | 全称 |
| 增持主体 | 大股东/高管 |
| 增持主体名称 | 股东全称或高管姓名 |
| 本次增持累计股数 | 单位：股 |
| 本次增持累计金额 | 单位：元（仅计算有均价记录的股份） |
| 增持均价 | 单位：元/股，保留4位小数 |
| 当日股价 | 单位：元/股 |
| 溢价率 | 增持均价÷当日股价，保留4位小数 |
| 是否纳入 | 纳入(溢价>1) / 剔除 |
| 备注 | 均价缺失说明；股价日期；增持价格区间 |

---

## 依赖说明

- 使用纯标准库（urllib, json, zipfile），无需 pip install
- Token：环境变量 `TUSHARE_TOKEN` → 同目录 `token.env`
- 输出：`/workspace/增持溢价分析报告_YYYYMMDD.xlsx`
