# 量化因子公式參考手冊

## 1. 動量因子 (Momentum Factors)

### 1.1 價格動量
```python
# N月動量
momentum_Nm = (price_current / price_Nm_ago) - 1

# 標準化動量
normalized_momentum = (momentum - momentum_mean) / momentum_std
```

### 1.2 收益率偏度
```python
skewness = ((returns - mean_returns) ** 3).mean() / (returns.std() ** 3)
```

## 2. 價值因子 (Value Factors)

### 2.1 市盈率系列
```python
pe_ttm = price / earnings_per_share_ttm
pe_lYR = price / earnings_per_share_lyr
peg = pe_ttm / (growth_rate * 100)
```

### 2.2 市淨率
```python
pb = price / book_value_per_share
```

### 2.3 股息率
```python
dividend_yield = annual_dividend / price
```

## 3. 質量因子 (Quality Factors)

### 3.1 盈利能力
```python
ROE = net_profit / equity
ROA = net_profit / total_assets
gross_margin = (revenue - cogs) / revenue
net_margin = net_profit / revenue
```

### 3.2 償債能力
```python
current_ratio = current_assets / current_liabilities
quick_ratio = (current_assets - inventory) / current_liabilities
debt_to_equity = total_liabilities / equity
```

### 3.3 運營效率
```python
inventory_turnover = cogs / average_inventory
asset_turnover = revenue / average_total_assets
```

## 4. 成長因子 (Growth Factors)

```python
revenue_growth = (revenue_current - revenue_prev) / revenue_prev
profit_growth = (profit_current - profit_prev) / profit_prev
equity_growth = (equity_current - equity_prev) / equity_prev
earnings_growth = (eps_current - eps_prev) / eps_prev
```

## 5. 技術因子 (Technical Factors)

### 5.1 換手率
```python
turnover_rate = trading_volume / circulating_shares * 100
```

### 5.2 波動率
```python
volatility_Nd = returns.std() * sqrt(252 / N)
```

### 5.3 量價相關性
```python
volume_price_corr = corr(price_changes, volume_changes)
```

### 5.4 相對強度指數
```python
RSI = 100 - (100 / (1 + RS))
RS = avg_gain / avg_loss
```

## 6. Alpha 因子組合

### 6.1 Fama-French 三因子
```python
alpha = portfolio_return - (beta_mkt * market_return +
                           beta_smb * SMB +
                           beta_hml * HML)
```

### 6.2 Barra 四因子
```python
# MKT (市場), SIZE (規模), VALUE (價值), PROFIT (盈利能力)
```

## 7. IC/IR 計算

```python
# Information Coefficient
IC = corr(factor_values, future_returns)

# Information Ratio
IR = IC_mean / IC_std

# 移動窗口 IC
rolling_ic = factor.rolling(window=20).corr(future_returns)
```

## 8. 因子權重計算

### 8.1 IC 加權
```python
weights = factor_ic / factor_ic.sum()
```

### 8.2 風險平價
```python
risk_contribution = weight * factor_volatility
weight = target_risk / factor_volatility
```

### 8.3 等權
```python
weights = 1 / n_factors
```
