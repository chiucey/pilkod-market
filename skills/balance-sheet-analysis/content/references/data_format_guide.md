# 财务数据格式参考指南

## API返回数据结构

### stocks_financial_data 返回格式

```json
{
  "symbol": "601001",
  "annual": [
    {
      "year": "2024",
      "financial_statements": {
        "balance_sheet": {
          "cash_equivalents": 166.10,
          "financial_assets": 0.0,
          "accounts_receivable": 23.45,
          "contract_assets": 0.0,
          "inventories": 15.32,
          "accounts_payable": 45.67,
          "fixed_assets": 120.50,
          "property_plant_equipment": 100.30,
          "short_term_borrowings": 10.00,
          "long_term_borrowings": 13.92,
          "current_assets": 250.50,
          "non_current_assets": 350.80,
          "total_assets": 601.30,
          "total_liabilities": 367.02
        },
        "cash_flow": {
          "operating_cash_flow": 29.94,
          "capital_expenditure": 9.20,
          "investing_cash_flow": -15.30,
          "financing_cash_flow": -10.50
        },
        "income_statement": {
          "revenue": 150.50,
          "gross_profit": 75.25,
          "operating_income": 45.30,
          "net_income": 35.80,
          "total_comprehensive_income": 36.20
        }
      }
    }
  ],
  "quarterly": [
    {
      "period": "2025-Q1",
      "financial_statements": { ... }
    }
  ]
}
```

## 数据字段映射

### 资产负债表 (Balance Sheet)

| 指标名称 | API字段 | 说明 | 单位 |
|---------|---------|------|------|
| 类现金 | cash_equivalents + financial_assets | 现金及等价物 + 交易性金融资产 | 亿元 |
| 应收账款 | accounts_receivable | 应收票据及应收账款 | 亿元 |
| 合同资产及存货 | contract_assets + inventories | 合同资产 + 存货 | 亿元 |
| 应付账款 | accounts_payable | 应付票据及应付账款 | 亿元 |
| 固定资产 | fixed_assets + property_plant_equipment | 固定资产净值 | 亿元 |
| 有息负债 | short_term_borrowings + long_term_borrowings | 短期借款 + 长期借款 | 亿元 |
| 流动资产 | current_assets | 流动资产合计 | 亿元 |
| 非流动资产 | non_current_assets | 非流动资产合计 | 亿元 |
| 总资产 | total_assets | 资产总计 | 亿元 |
| 负债总额 | total_liabilities | 负债合计 | 亿元 |

### 现金流量表 (Cash Flow)

| 指标名称 | API字段 | 说明 | 单位 |
|---------|---------|------|------|
| 经营性净现金流 | operating_cash_flow | 经营活动产生的现金流量净额 | 亿元 |
| 资本开支 | capital_expenditure | 购建固定资产、无形资产等支付的现金 | 亿元 |
| 投资性现金流 | investing_cash_flow | 投资活动产生的现金流量净额 | 亿元 |
| 融资性现金流 | financing_cash_flow | 筹资活动产生的现金流量净额 | 亿元 |

### 利润表 (Income Statement)

| 指标名称 | API字段 | 说明 | 单位 |
|---------|---------|------|------|
| 营业收入 | revenue | 营业总收入 | 亿元 |
| 净利润 | net_income | 净利润 | 亿元 |
| 全口径利润 | total_comprehensive_income | 综合收益总额 | 亿元 |

## 衍生指标计算公式

### 1. 营运资金
```
营运资金 = 应收账款 + 合同资产及存货 - 应付账款
        = accounts_receivable + contract_assets + inventories - accounts_payable
```

### 2. 净现金
```
净现金 = 类现金 - 有息负债
      = (cash_equivalents + financial_assets) - (short_term_borrowings + long_term_borrowings)
```

### 3. 资产负债率
```
资产负债率 = 负债总额 / 总资产 × 100%
          = total_liabilities / total_assets × 100%
```

### 4. 自由现金流
```
自由现金流 = 经营性净现金流 - 资本开支
          = operating_cash_flow - capital_expenditure
```

### 5. 自由现金流占利润比重
```
自由现金流占利润比重 = 自由现金流 / 全口径利润 × 100%
                    = free_cash_flow / total_comprehensive_income × 100%
```

### 6. 可清算资产
```
可清算资产 = 流动资产 - 负债总额
          = current_assets - total_liabilities
```

### 7. 每股净资产 (BVPS)
```
每股净资产 = (总资产 - 负债总额) / 总股本
          = (total_assets - total_liabilities) / total_shares
```

## 数据获取最佳实践

### 1. 年度数据 vs 季度数据
- **年度数据**：用于长期趋势分析，至少获取最近5年
- **季度数据**：用于最新一期财务状况分析
- **注意**：年度和季度数据可能存在口径差异，需要说明

### 2. 数据单位统一
- API返回数据通常为"元"或"万元"
- 表格展示统一转换为"亿元"（除以100000000）
- 保持所有年份数据单位一致

### 3. 数据缺失处理
```python
def get_safe_value(data: dict, key: str, default: float = 0.0) -> float:
    """安全获取数据，避免None或缺失"""
    value = data.get(key, default)
    if value is None:
        return default
    return float(value)
```

### 4. 季度数据标注
```
2025Q1 - 表示2025年第一季度
2024H1 - 表示2024年上半年
2024H2 - 表示2024年下半年（通常从三季报推算）
```

## 示例数据

### 晋控煤业（601001）示例数据

| 年份 | 类现金 | 有息负债 | 净现金 | 资产负债率 |
|------|--------|----------|--------|------------|
| 2020 | 45.23 | 35.50 | 9.73 | 58.32% |
| 2021 | 52.18 | 32.80 | 19.38 | 56.18% |
| 2022 | 68.45 | 28.90 | 39.55 | 53.25% |
| 2023 | 85.32 | 26.50 | 58.82 | 51.47% |
| 2024 | 166.10 | 23.92 | 142.18 | 49.02% |

（数据为示例，实际使用时请通过API获取）
