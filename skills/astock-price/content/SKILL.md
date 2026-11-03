---
name: astock-price
description: A 股实时行情查询技能。当用户提到查股价、查行情、看股票价格、A股实时行情、今日股价、涨跌情况时激活。支持：(1) 查询单个股票（输入代码如 600519）(2) 批量查询多个股票 (3) 按股票名称关键词搜索。
---

# A 股实时行情查询

使用 akshare 获取东方财富网实时行情数据，覆盖沪深全市场。

## 触发场景

- "查一下 600519 现在的价格"
- "贵州茅台涨了多少"
- "帮我看几个股票：600519、000858、300750"
- "现在A股涨得最好的是哪些"
- "宁德时代的股价"

## 使用方式

### 单股票查询

```python
exec: python3 /workspace/skills/astock-price/scripts/query_stock.py 600519
```

输出字段：
- `price`：最新价
- `pct_chg`：涨跌幅（%）
- `chg`：涨跌额
- `open / high / low / pre_close`：开盘/最高/最低/昨收
- `volume / turnover`：成交量/成交额
- `turnover_rate`：换手率
- `pe / pb`：市盈率/市净率
- `total_mv / float_mv`：总市值/流通市值
- `pct_60d / pct_ytd`：60日涨跌幅 / 年初至今涨跌幅

### 批量查询

```python
exec: python3 /workspace/skills/astock-price/scripts/query_stock.py 600519 000858 300750
```

### 名称搜索

```python
exec: python3 /workspace/skills/astock-price/scripts/query_stock.py -s 茅台
```

### JSON 格式输出（程序调用时）

```python
exec: python3 /workspace/skills/astock-price/scripts/query_stock.py 600519 -f json
```

## 股票代码规则

- 上证A股：6 开头（如 600519 贵州茅台）
- 深证A股：0 开头（如 000858 五粮液）
- 创业板：3 开头（如 300750 宁德时代）
- 输入时自动补全6位，不区分交易所

## 数据来源

东方财富网，通过 akshare `stock_zh_a_spot_em()` 接口。

## ⚠️ 注意

- 行情数据为实时快照，9:30-11:30 / 13:00-15:00 交易时段内实时更新
- 盘后（非交易时段）数据为收盘价
- 市盈率等指标为动态估值，可能为空值
- 数据仅供参考，不构成投资建议
