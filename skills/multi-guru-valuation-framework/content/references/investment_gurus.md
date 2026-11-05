# 投资大师方法论详解

## 1. 巴菲特估值体系

### 内在价值计算
巴菲特的内在价值法基于未来自由现金流的折现:

```python
def buffett_intrinsic_value(fcf, growth_rate, discount_rate, years=10):
    """
    计算内在价值
    fcf: 当前自由现金流
    growth_rate: 永续增长率
    discount_rate: 折现率(通常用9-10%)
    """
    value = 0
    for i in range(1, years + 1):
        value += fcf * (1 + growth_rate) ** i / (1 + discount_rate) ** i

    # 永续价值
    terminal_value = fcf * (1 + growth_rate) ** years * (1 + growth_rate) / (discount_rate - growth_rate)
    terminal_value /= (1 + discount_rate) ** years

    return value + terminal_value
```

### 护城河评估标准
- **无形资产**: 品牌、专利、特许经营权
- **转换成本**: 客户更换竞品的难度
- **网络效应**: 用户越多价值越大
- **成本优势**: 规模经济、流程优化

### 巴菲特选股标准
- ROE > 15%
- 长期债务少或无
- 管理层诚实有能力
- 简单可理解的业务
- 稳定持续的盈利

---

## 2. 格雷厄姆估值体系

### 格雷厄姆数
```
格雷厄姆数 = sqrt(22.5 × EPS × BVPS)
```

### Net-Net 估值
格雷厄姆的Net-Net法适用于困境公司:
```
Net-Net = max(0, 流动资产 - 全部负债) × 0.75
```

### 格雷厄姆选股标准
- PE < 15
- PB < 1.5
- 流动比率 > 2
- 债务/资产 < 50%
- 过去10年连续分红

---

## 3. 彼得·林奇估值体系

### PEG 法则
```python
def peg_ratio(pe, eps_growth):
    """PEG = PE / 盈利增长率"""
    return pe / eps_growth if eps_growth > 0 else float('inf')

# 判断标准
# PEG < 0.75: 极低估值
# PEG < 1: 合理低估
# PEG = 1: 合理估值
# PEG > 1.5: 偏高估
# PEG > 2: 严重高估
```

### 林奇六种股票分类
1. **稳定增长股**: 日用消费品，年增8-12%
2. **缓慢增长股**: 成熟行业，年增2-4%
3. **快速增长股**: 小型成长公司，年增25%+
4. **周期股**: 跟随经济周期
5. **资产型**: 隐藏资产被低估
6. **困境股**: 遇到暂时困难

---

## 4. 约翰·邓普顿估值体系

### 逆向投资原则
- 最悲观时买入，最乐观时卖出
- 与共识相反的勇气
- 长期投资的耐心

### 估值比较法
```python
def templeton_valuation(pe, historical_pe_avg, risk_free_rate):
    """
    比较当前PE与历史均值的偏离
    同时考虑国债收益率作为基准
    """
    pe_percentile = calculate_percentile(pe, historical_pe_avg)
    earnings_yield = 1 / pe

    return {
        'pe_vs_history': pe < historical_pe_avg,
        'pe_percentile': pe_percentile,
        'earnings_yield_vs_bond': earnings_yield > risk_free_rate
    }
```

---

## 5. 格林布拉特神奇公式

### 资本回报率 (ROC)
```python
def calculate_roc(ebit, working_capital, fixed_assets):
    """ROC = EBIT / (净营运资本 + 净固定资产)"""
    invested_capital = working_capital + fixed_assets
    return ebit / invested_capital if invested_capital > 0 else 0
```

### EBIT 收益率
```python
def ebit_yield(ebit, market_cap, net_debt):
    """EBIT收益率 = EBIT / 企业价值"""
    enterprise_value = market_cap + net_debt
    return ebit / enterprise_value
```

### 神奇公式排名
1. 对所有股票按ROC排名(从高到低)
2. 对所有股票按EBIT收益率排名(从高到低)
3. 综合排名 = ROC排名 + EBIT收益率排名
4. 选择综合排名最靠前的股票

---

## 6. CAN SLIM 系统

### 七要素评分
| 字母 | 要素 | 优秀标准 | 权重 |
|------|------|---------|------|
| C | 当季每股收益 | 同比增长≥20% | 20% |
| A | 年度每股收益 | 增长加速 | 15% |
| N | 新变化 | 新产品/管理层/市场 | 10% |
| S | 供给需求 | 量价配合突破 | 15% |
| L | 行业龙头 | 相对强弱指数>80 | 15% |
| I | 机构认可 | 机构持仓增加 | 10% |
| M | 市场方向 | 顺应大盘趋势 | 15% |

### 技术面要点
- 突破基部时买入
- 止损设置8%以内
- 成交量确认趋势
- 避免追高

---

## 7. 索罗斯反身性理论

### 核心概念
```
均衡点 = 基本趋势 + 主流偏向
```

### 反身性反馈循环
- **正反馈**: 趋势加强趋势(泡沫)
- **负反馈**: 偏离回归均衡

### 拐点识别
1. 基本面与价格严重背离
2. 主流偏见达到极端
3. 流动性枯竭信号
4. 政策干预预期

### 应用步骤
1. 识别宏观趋势
2. 寻找反身性迹象
3. 评估拐点概率
4. 风险管理优先

---

## 权重配置建议

### 成长股加权
```
巴菲特: 25%, 格雷厄姆: 10%, 林奇: 30%, 邓普顿: 10%
格林布拉特: 15%, 奥尼尔: 5%, 索罗斯: 5%
```

### 价值股加权
```
巴菲特: 30%, 格雷厄姆: 30%, 林奇: 5%, 邓普顿: 15%
格林布拉特: 15%, 奥尼尔: 0%, 索罗斯: 5%
```

### 周期股加权
```
巴菲特: 15%, 格雷厄姆: 20%, 林奇: 10%, 邓普顿: 15%
格林布拉特: 25%, 奥尼尔: 5%, 索罗斯: 10%
```

### 困境股加权
```
巴菲特: 10%, 格雷厄姆: 35%, 林奇: 5%, 邓普顿: 25%
格林布拉特: 15%, 奥尼尔: 0%, 索罗斯: 10%
```
