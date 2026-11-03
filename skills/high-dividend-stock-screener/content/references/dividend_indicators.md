# 股息指标详解

## 一、股息率相关指标

### 1.1 近12个月股息率 (Dividend Yield TTM)
```
股息率 TTM = 近4个季度分红总额 / 当前股价 × 100%
```

**评估标准**：
- 优秀：> 5%
- 良好：4% - 5%
- 一般：3% - 4%
- 较差：< 3%

### 1.2 近3年平均股息率
```
平均股息率 = (近3年每年股息率之和) / 3
```

**评估标准**：
- 稳定高息：持续 > 3% 且波动小
- 周期高息：波动大，部分年份 > 5%
- 不稳定：波动剧烈，无法预期

### 1.3 股息率稳定性指标
```python
# 计算股息率波动系数
volatility = std(annual_dividend_yields) / mean(annual_dividend_yields)
# 波动系数 < 0.3 为稳定
```

## 二、分红历史指标

### 2.1 连续分红年数
- 连续5年以上：优秀（稳定型）
- 连续3-5年：良好（成长型）
- 不足3年：不满足要求

### 2.2 分红次数
- 每年分红1次：标准
- 每年分红2次：优秀（更稳定现金流）

### 2.3 分红金额趋势
```
# 近3年分红金额变化
dividend_growth = (最新年分红 - 3年前分红) / 3年前分红 × 100%
```
- 稳定或小幅增长：优秀
- 大幅波动：需谨慎
- 持续下降：风险信号

## 三、股利支付率指标

### 3.1 股利支付率 (Payout Ratio)
```
股利支付率 = 分红总额 / 净利润 × 100%
```

**评估区间**：
| 支付率区间 | 评价 | 说明 |
|-----------|------|------|
| < 20% | 过低 | 未充分利用盈利回馈股东 |
| 20% - 40% | 适中偏低 | 留有发展资金 |
| 40% - 60% | 适中 | 平衡回报与发展 |
| 60% - 70% | 适中偏高 | 回报较高但需监控 |
| > 70% | 过高 | 分红可能不可持续 |

### 3.2 近3年平均支付率
```python
avg_payout = mean([payout_ratio_year1, payout_ratio_year2, payout_ratio_year3])
```
- 稳定在20%-70%区间：优秀
- 波动但均值合理：良好
- 持续上升接近或超过100%：风险

### 3.3 支付率趋势
```
# 判断支付率是否可持续
if avg_payout < 70% and trend != "increasing":
    sustainable = True
else:
    sustainable = False
```

## 四、分红可持续性评估

### 4.1 现金流覆盖倍数
```
股息保障倍数 = 经营现金流净额 / 分红总额
```

**标准**：
- > 2倍：优秀（覆盖充裕）
- 1.5-2倍：良好（覆盖充足）
- 1-1.5倍：一般（勉强覆盖）
- < 1倍：风险（现金流不足以分红）

### 4.2 自由现金流覆盖
```
FCF覆盖倍数 = 自由现金流 / 分红总额
自由现金流 = 经营现金流 - 资本支出
```

**标准**：
- FCF > 分红且有余额：优秀
- FCF ≈ 分红（80%-100%）：良好
- FCF < 分红（<80%）：风险信号

### 4.3 盈利与分红匹配度
```python
# 净利润与经营现金流匹配度
matching_ratio = min(净利润, 经营现金流) / max(净利润, 经营现金流) × 100%
```
- > 80%：优秀（盈利真实）
- 60%-80%：良好
- < 60%：需关注（盈利质量存疑）

## 五、特殊分红识别

### 5.1 一次性分红识别
```python
def detect_special_dividend(stock):
    # 检查是否为一次性大额分红
    if (latest_dividend > 3 * avg_dividend and
        current_pe < industry_pe * 0.5):
        return True  # 可能存在虚高股息率
    return False
```

### 5.2 正常化股息率计算
```
正常股息率 = 正常年份分红金额 / 当前股价
# 排除特殊情况：期终分红、资产出售分红等
```

## 六、综合股息质量评分

```python
def dividend_quality_score(stock):
    # 股息率得分 (30分)
    if yield_ttm > 5: yield_score = 30
    elif yield_ttm > 4: yield_score = 25
    elif yield_ttm > 3: yield_score = 15
    else: yield_score = 0

    # 稳定性得分 (25分)
    if dividend_years >= 5 and volatility < 0.3:
        stability_score = 25
    elif dividend_years >= 3 and volatility < 0.5:
        stability_score = 20
    else:
        stability_score = 10

    # 可持续性得分 (25分)
    if payout_ratio_3y_avg <= 70 and fcf_coverage >= 1:
        sustainability_score = 25
    elif payout_ratio_3y_avg <= 80:
        sustainability_score = 15
    else:
        sustainability_score = 5

    # 分红增长得分 (20分)
    if dividend_growth >= 0 and dividend_growth <= 20:
        growth_score = 20
    elif dividend_growth > 20:
        growth_score = 15
    else:
        growth_score = 5

    return yield_score + stability_score + sustainability_score + growth_score
```

## 七、行业对比调整

不同行业的天然股息率水平不同，需要对比行业均值：

| 行业 | 平均股息率 | 高股息门槛 |
|------|-----------|-----------|
| 银行 | 4-5% | > 5% |
| 保险 | 3-4% | > 4% |
| 煤炭 | 5-8% | > 6% |
| 钢铁 | 3-5% | > 4% |
| 电力 | 3-5% | > 4% |
| 高速公路 | 4-6% | > 5% |
| 白酒 | 1-3% | > 2% |
| 医药 | 1-2% | > 1.5% |