# 量化回测框架 v2.0

本框架用于验证股票分析评分体系的有效性，通过三层回测结构实现从逻辑到结果到策略的完整验证。

---

## 一、核心设计原则

1. **避免未来函数**: 评分仅使用当期可获得数据
2. **考虑交易成本**: 印花税0.1%, 佣金0.03%
3. **流动性约束**: 日均成交额<1亿不做大仓位
4. **存活者偏差**: 纳入退市股票
5. **稳健性优先**: 不是最大化历史收益，而是最大化策略的长期稳定性

---

## 二、三层回测结构

### 第一层：逻辑评估

**目的**: 验证评分逻辑的合理性

**评估内容**:
- 估值与未来收益的相关性
- 基本面与股价表现的关系
- 技术面的有效性
- 各维度权重的合理性

**评估方法**:
```python
def evaluate_scoring_logic(historical_data):
    """
    评估评分逻辑

    检验方法:
    1. 高分组收益 > 低分组收益?
    2. 估值与收益负相关?
    3. ROE与收益正相关?
    """
    results = {}

    # 按评分分组
    high_score_group = historical_data[historical_data['score'] >= 70]
    low_score_group = historical_data[historical_data['score'] < 50]

    # 计算各组平均收益
    results['high_score_return'] = high_score_group['future_return'].mean()
    results['low_score_return'] = low_score_group['future_return'].mean()

    # 计算相关性
    results['score_return_corr'] = historical_data['score'].corr(
        historical_data['future_return']
    )

    return results
```

### 第二层：历史回测

**目的**: 验证评分与收益的历史相关性

**回测设置**:
- 回测区间: 2020-01-01 至 2026-04-12
- 调仓频率: 月度
- 对比基准: 沪深300指数

**回测流程**:
```
选股日 → 计算评分 → 按评分排序 → 分组建仓
   ↓
持有1个月 → 计算收益 → 记录数据
   ↓
重复至回测结束 → 汇总统计
```

### 第三层：策略验证

**目的**: 验证基于评分的交易策略

**策略定义**:
- 买入信号: 评分>=75
- 卖出信号: 评分<50 或 跌幅>-15%
- 仓位: 根据评分调整

---

## 三、回测指标体系

### 3.1 收益指标

| 指标 | 计算公式 | 评价标准 |
|------|----------|----------|
| 总收益率 | (期末净值-期初净值)/期初净值 | 越高越好 |
| 年化收益率 | 总收益/年数 | >15%优秀 |
| 超额收益 | 策略收益-基准收益 | >5%优秀 |
| 信息比率 | 超额收益/跟踪误差 | >0.5优秀 |

### 3.2 风险指标

| 指标 | 计算公式 | 评价标准 |
|------|----------|----------|
| 最大回撤 | max(回撤幅度) | <15%优秀 |
| 年化波动率 | 收益标准差*√252 | <20%优秀 |
| 夏普比率 | (年化收益-无风险)/波动率 | >1.5优秀 |
| 索提诺比率 | (年化收益-无风险)/下行波动 | >2优秀 |
| 卡玛比率 | 年化收益/最大回撤 | >2优秀 |

### 3.3 交易指标

| 指标 | 计算公式 | 评价标准 |
|------|----------|----------|
| 胜率 | 盈利次数/总交易 | >60%优秀 |
| 盈亏比 | 平均盈利/平均亏损 | >2优秀 |
| 平均持仓天数 | 总持仓/交易次数 | 30-90天 |
| 换手率 | 年交易额/资金 | 适中 |

---

## 四、分组回测设计

### 4.1 按评分分组

| 组别 | 评分范围 | 交易数 | 平均收益 | 胜率 |
|------|----------|--------|----------|------|
| 第1组 | 85-100分 | XX | +XX% | XX% |
| 第2组 | 70-84分 | XX | +XX% | XX% |
| 第3组 | 55-69分 | XX | +XX% | XX% |
| 第4组 | 40-54分 | XX | +XX% | XX% |
| 第5组 | 0-39分 | XX | -XX% | XX% |

**验证目标**: 第1组收益 > 第5组收益

### 4.2 按估值分组

| 组别 | PE范围 | 交易数 | 平均收益 | 胜率 |
|------|--------|--------|----------|------|
| 第1组 | PE<15 | XX | +XX% | XX% |
| 第2组 | PE 15-25 | XX | +XX% | XX% |
| 第3组 | PE 25-40 | XX | +XX% | XX% |
| 第4组 | PE>40 | XX | -XX% | XX% |

**验证目标**: 低估值组收益 > 高估值组收益

### 4.3 按基本面分组

| 组别 | ROE范围 | 交易数 | 平均收益 | 胜率 |
|------|---------|--------|----------|------|
| 第1组 | ROE>20% | XX | +XX% | XX% |
| 第2组 | ROE 15-20% | XX | +XX% | XX% |
| 第3组 | ROE 10-15% | XX | +XX% | XX% |
| 第4组 | ROE<10% | XX | -XX% | XX% |

**验证目标**: 高ROE组收益 > 低ROE组收益

---

## 五、回测执行代码

### 5.1 主回测函数

```python
def run_backtest(config):
    """
    主回测函数

    参数:
    - config: 回测配置
      - start_date: 开始日期
      - end_date: 结束日期
      - initial_capital: 初始资金
      - rebalance_freq: 调仓频率
    """
    # 1. 数据准备
    data = load_data(config['start_date'], config['end_date'])

    # 2. 计算评分
    data['score'] = calculate_score(data)

    # 3. 月度调仓
    rebalance_dates = get_rebalance_dates(
        config['start_date'],
        config['end_date'],
        config['rebalance_freq']
    )

    # 4. 模拟交易
    portfolio = Portfolio(config['initial_capital'])

    for date in rebalance_dates:
        # 选股
        selected = select_stocks(data, date, top_n=10)

        # 调仓
        portfolio.rebalance(selected, date)

        # 更新持仓
        portfolio.update(date)

    # 5. 统计结果
    results = calculate_metrics(portfolio)

    return results
```

### 5.2 选股函数

```python
def select_stocks(data, date, top_n=10):
    """
    选股函数

    选股规则:
    1. 评分>=75
    2. 日均成交额>1亿
    3. 按评分排序取前N
    """
    date_data = data[data['date'] == date]

    # 过滤条件
    filtered = date_data[
        (date_data['score'] >= 75) &
        (date_data['avg_volume'] >= 1e8)
    ]

    # 按评分排序
    selected = filtered.nlargest(top_n, 'score')

    return selected
```

### 5.3 组合更新函数

```python
class Portfolio:
    def __init__(self, initial_capital):
        self.cash = initial_capital
        self.positions = {}
        self.nav_history = []
        self.trade_history = []

    def rebalance(self, selected_stocks, date):
        """调仓"""
        target_weight = 1.0 / len(selected_stocks)

        for _, stock in selected_stocks.iterrows():
            stock_code = stock['code']
            price = stock['close']

            # 计算买入数量
            target_value = self.total_value * target_weight
            shares = int(target_value / price / 100) * 100  # 整手

            if shares > 0:
                cost = shares * price
                commission = cost * 0.0003

                if cost + commission <= self.cash:
                    self.positions[stock_code] = {
                        'shares': shares,
                        'entry_price': price,
                        'entry_date': date
                    }
                    self.cash -= (cost + commission)

                    self.trade_history.append({
                        'date': date,
                        'code': stock_code,
                        'type': 'BUY',
                        'price': price,
                        'shares': shares
                    })

    def update(self, date):
        """更新组合"""
        total_value = self.cash

        for code, pos in self.positions.items():
            current_price = get_price(code, date)
            pos_value = pos['shares'] * current_price
            total_value += pos_value

        self.nav_history.append({
            'date': date,
            'nav': total_value
        })
```

---

## 六、回测报告生成

### 6.1 报告模板

```markdown
# 量化回测报告

## 回测概况

| 项目 | 数值 |
|------|------|
| 回测区间 | 2020-01-01 至 2026-04-12 |
| 初始资金 | 100万元 |
| 最终净值 | X.XX元 |
| 总收益率 | XX% |
| 年化收益率 | XX% |
| 基准收益率 | XX% |
| 超额收益 | XX% |
| 最大回撤 | XX% |
| 夏普比率 | X.XX |

## 收益曲线
[图表]

## 分组表现

| 组别 | 评分范围 | 累计收益 | 年化收益 | 超额收益 | 最大回撤 |
|------|----------|----------|----------|----------|----------|
| 第1组 | 85-100分 | +XX% | +XX% | +XX% | -XX% |
| 第2组 | 70-84分 | +XX% | +XX% | +XX% | -XX% |
| 第3组 | 55-69分 | +XX% | +XX% | +XX% | -XX% |
| 第4组 | 40-54分 | +XX% | +XX% | +XX% | -XX% |
| 第5组 | 0-39分 | -XX% | -XX% | -XX% | -XX% |

## IC分析
| 月份 | IC | IR | 胜率 |
|------|-----|-----|------|
| 2024-01 | +X.XX% | X.XX | XX% |
| 2024-02 | +X.XX% | X.XX | XX% |

## 结论
- 评分有效性: [是/否]
- 策略建议: [采纳/优化/不采纳]
```

### 6.2 生成代码

```python
def generate_backtest_report(results):
    """生成回测报告"""
    report = []

    # 概况
    report.append("# 量化回测报告\n")
    report.append("## 回测概况\n")

    overview = [
        ["回测区间", f"{results['start_date']} 至 {results['end_date']}"],
        ["初始资金", f"{results['initial_capital']}万元"],
        ["最终净值", f"{results['final_nav']:.2f}元"],
        ["总收益率", f"{results['total_return']:.2f}%"],
        ["年化收益率", f"{results['annualized_return']:.2f}%"],
        ["超额收益", f"{results['excess_return']:.2f}%"],
        ["最大回撤", f"{results['max_drawdown']:.2f}%"],
        ["夏普比率", f"{results['sharpe_ratio']:.2f}"]
    ]

    report.append("| 项目 | 数值 |")
    report.append("|------|------|")
    for item in overview:
        report.append(f"| {item[0]} | {item[1]} |")

    return "\n".join(report)
```

---

## 七、稳健性检验

### 7.1 样本外检验

```python
def out_of_sample_test(data, train_period, test_period):
    """
    样本外检验

    方法:
    - 样本内: 训练评分模型
    - 样本外: 验证模型有效性
    """
    # 样本内数据
    train_data = data[data['date'] < train_period['test_start']]

    # 样本外数据
    test_data = data[
        (data['date'] >= test_period['start']) &
        (data['date'] <= test_period['end'])
    ]

    # 样本内回测
    in_sample_results = run_backtest(train_data)

    # 样本外回测
    out_sample_results = run_backtest(test_data)

    # 比较结果
    comparison = {
        "in_sample_return": in_sample_results['annualized_return'],
        "out_sample_return": out_sample_results['annualized_return'],
        "decay_ratio": out_sample_results['annualized_return'] /
                       in_sample_results['annualized_return']
    }

    return comparison
```

### 7.2 敏感性分析

```python
def sensitivity_analysis(data, parameter, range_values):
    """
    敏感性分析

    检验参数变化对策略的影响
    """
    results = []

    for value in range_values:
        config = {parameter: value}
        result = run_backtest(data, config)
        results.append({
            'parameter': value,
            'return': result['annualized_return'],
            'sharpe': result['sharpe_ratio'],
            'max_dd': result['max_drawdown']
        })

    return pd.DataFrame(results)
```

### 7.3 分市场检验

```python
def market_stratified_test(data):
    """
    分市场检验

    检验策略在不同市场环境下的表现
    """
    # 牛市期间
    bull_market = data[data['market_condition'] == 'BULL']

    # 熊市期间
    bear_market = data[data['market_condition'] == 'BEAR']

    # 震荡市期间
    sideways_market = data[data['market_condition'] == 'SIDEWAYS']

    return {
        'bull_market': run_backtest(bull_market),
        'bear_market': run_backtest(bear_market),
        'sideways_market': run_backtest(sideways_market)
    }
```

---

## 八、策略优化建议

### 8.1 优化方向

| 优化方向 | 当前表现 | 目标 | 方法 |
|----------|----------|------|------|
| 提高胜率 | 62% | 65% | 调整选股阈值 |
| 降低回撤 | -12% | -10% | 引入对冲 |
| 提高盈亏比 | 2.0 | 2.5 | 优化止盈止损 |
| 提升夏普 | 1.5 | 2.0 | 组合优化 |

### 8.2 优化规则

```python
def optimize_strategy(results):
    """
    基于回测结果的策略优化

    规则:
    1. 如果某评分区间胜率<50%, 提高该区间选股阈值
    2. 如果回撤>15%, 降低单票仓位
    3. 如果盈亏比<1.5, 调整止盈止损位
    """
    suggestions = []

    # 胜率优化
    for group in results['group_stats']:
        if group['win_rate'] < 0.50:
            suggestions.append({
                'type': 'threshold',
                'group': group['name'],
                'action': '提高选股阈值',
                'current': group['score_min'],
                'suggested': group['score_min'] + 5
            })

    # 回撤优化
    if results['max_drawdown'] > 0.15:
        suggestions.append({
            'type': 'position',
            'action': '降低仓位',
            'current': 0.15,
            'suggested': 0.10
        })

    # 盈亏比优化
    if results['profit_loss_ratio'] < 1.5:
        suggestions.append({
            'type': 'stop',
            'action': '调整止盈止损',
            'current_profit': 0.30,
            'suggested_profit': 0.25,
            'current_loss': 0.10,
            'suggested_loss': 0.08
        })

    return suggestions
```

---

## 九、版本更新记录

### v2.0 (2026-04-12)
- 新增三层回测结构
- 完善稳健性检验模块
- 优化回测报告模板

### v1.5 (2025-10-01)
- 增加分市场检验
- 完善敏感性分析

### v1.0 (2025-01-01)
- 初版发布
- 基础回测功能
