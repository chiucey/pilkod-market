# 估值方法说明

## 一、PE（市盈率）评估

### 1.1 基本计算

```python
PE = 当前股价 / 每股收益(EPS)
静态PE = 当前股价 / 上年度EPS
滚动PE(TTM) = 当前股价 / 近4季度EPS
```

### 1.2 PE评估标准

| PE区间 | 评价 | 适用场景 |
|--------|------|----------|
| < 10 | 低估值 | 价值陷阱 or 价值投资 |
| 10 - 20 | 合理偏低 | 推荐关注 |
| 20 - 30 | 合理 | 正常水平 |
| 30 - 50 | 偏高 | 成长股正常溢价 |
| > 50 | 高估值 | 谨慎对待 |

### 1.3 行业PE对比

```python
# 计算PE行业分位
pe_percentile = percentile(股票PE, 行业PE列表) × 100%

# 低于行业中位数即有相对优势
if pe < industry_median_pe:
    relative_advantage = True
```

### 1.4 PE历史分位

```python
# 计算当前PE在历史中的分位
pe_percentile_5y = percentile(当前PE, [PE_5y_history]) × 100%

# 评估
if pe_percentile_5y < 30:  # 历史低位
    valuation_score = "低位"
elif pe_percentile_5y < 70:
    valuation_score = "中等"
else:
    valuation_score = "高位"
```

## 二、PB（市净率）评估

### 2.1 基本计算

```python
PB = 当前股价 / 每股净资产(BPS)
```

### 2.2 PB评估标准

| PB区间 | 评价 | 说明 |
|--------|------|------|
| < 1 | 破净 | 资产价值被低估 or 资产质量存疑 |
| 1 - 2 | 合理偏低 | 价值投资区间 |
| 2 - 5 | 合理 | 正常水平 |
| 5 - 10 | 偏高 | 轻资产或高成长 |
| > 10 | 高估值 | 谨慎 |

### 2.3 行业PB对比

```python
pb_percentile = percentile(股票PB, 行业PB列表) × 100%

if pb < industry_median_pb:
    relative_advantage = True
```

## 三、股息率相对估值

### 3.1 股息率计算

```python
股息率 = 最近12个月分红总额 / 当前股价 × 100%
```

### 3.2 股息率行业对比

```python
# 计算股息率行业分位
yield_percentile = percentile(股票股息率, 行业股息率列表) × 100%

# 高股息优势
if 股息率 > 行业股息率中位数:
    dividend_advantage = True
```

### 3.3 历史股息率分位

```python
# 当前股息率在历史中的分位
yield_percentile_3y = percentile(当前股息率, [股息率_3y_history]) × 100%

# 评估
if yield_percentile_3y > 70:  # 较高分位，股价可能相对低
    position_score = "有利"
```

## 四、估值综合评分

```python
def valuation_score(stock, industry_median_pe, industry_median_pb, industry_median_yield):
    score = 0
    details = {}

    # PE评估 (30分)
    if stock.pe < industry_median_pe:
        score += 20
        details["pe"] = "低于行业中位数"
    else:
        score += 10
        details["pe"] = "高于或等于行业中位数"

    if stock.pe_percentile_5y < 30:
        score += 10
        details["pe_history"] = "处于近5年低位"
    elif stock.pe_percentile_5y < 70:
        score += 5
        details["pe_history"] = "处于近5年中位"
    else:
        details["pe_history"] = "处于近5年高位"

    # PB评估 (25分)
    if stock.pb < industry_median_pb:
        score += 15
        details["pb"] = "低于行业中位数"
    else:
        score += 8
        details["pb"] = "高于或等于行业中位数"

    if stock.pb_percentile_5y < 30:
        score += 10
        details["pb_history"] = "处于近5年低位"
    else:
        score += 5
        details["pb_history"] = "处于近5年中高位"

    # 股息率评估 (25分)
    if stock.dividend_yield > industry_median_yield:
        score += 15
        details["yield"] = "高于行业中位数"
    else:
        score += 5
        details["yield"] = "低于行业中位数"

    if stock.yield_percentile_3y > 60:
        score += 10
        details["yield_history"] = "处于近3年较高分位"
    else:
        score += 5
        details["yield_history"] = "处于近3年中低分位"

    # 安全边际 (20分)
    if stock.pe < 15 and stock.dividend_yield > 4:
        score += 20
        details["safety_margin"] = "显著安全边际"
    elif stock.pe < 20 and stock.dividend_yield > 3:
        score += 10
        details["safety_margin"] = "有一定安全边际"
    else:
        score += 5
        details["safety_margin"] = "安全边际有限"

    return score, details
```

## 五、估值陷阱识别

### 5.1 价值陷阱特征

- PE极低（< 5）但行业夕阳
- 利润主要来自非经常性损益
- 应收账款和存货异常高
- 分红依赖一次性收益

### 5.2 合理低估值识别

真正的低估应该具备：
- 盈利稳定或增长
- 现金流健康
- 行业前景不过度悲观
- 无重大财务问题

### 5.3 估值检查清单

```python
def check_valuation_trap(stock):
    warnings = []

    # 利润质量检查
    if stock扣非净利润 < 净利润 × 0.8:
        warnings.append("利润质量存疑")

    # 分红来源检查
    if stock.dividend > stock.operating_cash_flow:
        warnings.append("分红依赖非经营现金流")

    # 资产质量检查
    if stock.pb < 0.8 and stock.goodwill_ratio > 30:
        warnings.append("低PB可能因高商誉")

    # 行业前景检查
    if stock.行业增速 < -5% and stock.pe > 15:
        warnings.append("行业下行期估值偏高")

    return warnings
```

## 六、综合位置评分

```python
def position_score(stock):
    score = 0

    # 股价历史分位 (30分)
    if stock.price_percentile_5y < 30:
        score += 30
        position = "历史低位"
    elif stock.price_percentile_5y < 50:
        score += 20
        position = "偏低"
    elif stock.price_percentile_5y < 70:
        score += 10
        position = "中等"
    else:
        score += 0
        position = "偏高"

    # 股息率分位 (30分)
    if stock.yield_percentile_3y > 70:
        score += 30
        yield_position = "较高分位（有利）"
    elif stock.yield_percentile_3y > 50:
        score += 20
        yield_position = "中等分位"
    else:
        score += 10
        yield_position = "较低分位"

    # 基本面趋势 (40分)
    if stock.基本面无明显恶化 and stock.估值处于历史低位:
        score += 40
        fundamentals = "良好"
    elif stock.基本面稳定:
        score += 25
        fundamentals = "稳定"
    else:
        score += 10
        fundamentals = "需关注"

    return {
        "score": score,
        "position": position,
        "yield_position": yield_position,
        "fundamentals": fundamentals
    }
```