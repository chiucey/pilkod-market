# Tushare Pro API Reference

## API List

### 1. income (Income Statement)
**Function**: Get income statement data

**Required Parameters**:
- `ts_code`: Stock code (e.g., 600519.SH)

**Optional Parameters**:
- `ann_date`: Announcement date
- `start_date`: Report period start
- `end_date`: Report period end
- `period`: Report period (YYYYMM)
- `report_type`: Report type

**Return Fields**:
| Field Name | Description |
|------------|-------------|
| ts_code | Stock code |
| ann_date | Announcement date |
| f_ann_date | Actual announcement date |
| end_date | Report period end date |
| report_type | Report type |
| basic_eps | Basic EPS |
| diluted_eps | Diluted EPS |
| total_revenue | Total operating revenue |
| revenue | Operating revenue |
| int_income | Interest income |
| prem_earned | Premiums earned |
| comm_income | Commission income |
| net_profit | Net profit |
| parent_netprofit | Net profit attributable to parent |

### 2. balancesheet (Balance Sheet)
**Function**: Get balance sheet data

**Return Fields**:
| Field Name | Description |
|------------|-------------|
| ts_code | Stock code |
| ann_date | Announcement date |
| end_date | Report period end date |
| total_assets | Total assets |
| total_liab | Total liabilities |
| total_hldr_eqy_exc_min_int | Total shareholders equity |
| equities_parent_company_owners | Equity attributable to parent |
| liab_eqy_exc_min_int | Total liabilities and equity |

### 3. fina_indicator (Financial Indicators)
**Function**: Get financial indicator data

**Return Fields**:
| Field Name | Description |
|------------|-------------|
| ts_code | Stock code |
| ann_date | Announcement date |
| end_date | Report period end date |
| gross_profit_margin | Gross profit margin |
| net_profit_margin | Net profit margin |
| roe | Return on equity (ROE) |
| roa | Return on assets (ROA) |
| debt_to_assets | Debt-to-asset ratio |
| current_ratio | Current ratio |
| quick_ratio | Quick ratio |
| netprofit_to_operate_q | Operating net profit / total profit |
| eps | Earnings per share |

### 4. daily_basic (Daily Fundamentals)
**Function**: Get daily trading indicators

**Return Fields**:
| Field Name | Description |
|------------|-------------|
| ts_code | Stock code |
| trade_date | Trading date |
| close | Closing price |
| turnover_rate | Turnover rate |
| pe | P/E ratio |
| pe_ttm | P/E ratio TTM |
| pb | P/B ratio |
| ps | P/S ratio |
| ps_ttm | P/S ratio TTM |
| total_mv | Total market cap |
| circ_mv | Circulating market cap |

## Usage Examples

```python
import tushare as ts

# Initialize
pro = ts.pro_api('your_token')

# Get income statement (annual)
df = pro.income(ts_code='600519.SH', start_date='20230101', end_date='20240331')

# Get financial indicators
df = pro.fina_indicator(ts_code='600519.SH', start_date='20230101', end_date='20240331')

# Get latest valuation
df = pro.daily_basic(ts_code='600519.SH', trade_date='20240322')
```

## Notes

1. **Credit Requirements**: Some APIs require corresponding credits
2. **Rate Limits**: API has calling frequency limits
3. **Data Updates**: Annual report data typically released in April of following year
4. **Adjustment**: Use `adj` parameter for adjustment handling
