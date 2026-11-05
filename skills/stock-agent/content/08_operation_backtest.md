# 个股操作建议与回测优化 v1.0

本文档定义个股操作建议生成、回测执行、稳健优化的完整流程。

---

## 一、核心工作流

```
┌─────────────────────────────────────────────────────────────────────┐
│                        个股 → 操作建议 → 回测 → 稳健优化             │
└─────────────────────────────────────────────────────────────────────┘
```

### 流程说明

1. **个股分析**: 基于八维度评分体系分析股票
2. **操作建议**: 根据评分生成具体买入/卖出/持有建议
3. **回测验证**: 用历史数据验证操作建议的有效性
4. **稳健优化**: 基于回测结果优化操作策略

---

## 二、操作建议生成

### 2.1 评级到操作的映射

| 综合评分 | 评级 | 操作信号 | 仓位建议 | 持有期限 |
|----------|------|----------|----------|----------|
| 85-100 | 🟢🟢强力买入 | BUY | 15-20% | 6-12月 |
| 70-84 | 🟢买入 | BUY | 10-15% | 3-6月 |
| 55-69 | 🟡🟡中性偏强 | HOLD | 5-10% | 1-3月 |
| 40-54 | 🟡持有 | HOLD | 3-5% | 1月 |
| 25-39 | 🟠减配 | REDUCE | 0-3% | 即时减持 |
| 0-24 | 🔴卖出 | SELL | 0% | 立即清仓 |

### 2.2 操作建议模板

```markdown
# 个股操作建议

## 基础信息
- 股票代码: 000333.SZ
- 股票名称: 美的集团
- 当前价格: ¥72.50
- 评级时间: 2026-04-12

## 操作信号
| 项目 | 数值 |
|------|------|
| 综合评分 | 88分 |
| 投资评级 | 🟢🟢强力买入 |
| 操作信号 | BUY |
| 建议仓位 | 15-20% |

## 买入策略
### 建仓区间
- 理想买入区间: ¥68-72
- 可接受买入区间: ¥65-75
- 建议分批建仓:
  - 首次建仓: 50%仓位 (¥72附近)
  - 回调加仓: 30%仓位 (¥68附近)
  - 极端回调: 20%仓位 (¥65附近)

### 目标价与空间
| 目标 | 价格 | 空间 |
|------|------|------|
| 1年目标价 | ¥95 | +31% |
| 阶段目标价 | ¥85 | +17% |

## 止损策略
| 止损类型 | 价格 | 幅度 | 说明 |
|----------|------|------|------|
| 硬止损 | ¥61 | -15% | 绝对止损线 |
| 移动止损 | 成本价-10% | -10% | 跌破即出 |
| 跟踪止损 | 最高点-12% | -12% | 保护利润 |

## 止盈策略
| 目标 | 价格 | 空间 | 建议 |
|------|------|------|------|
| 第一止盈 | ¥85 | +17% | 减仓30% |
| 第二止盈 | ¥95 | +31% | 再减仓30% |
| 持有到期 | ¥95+ | +31%+ | 持有待涨 |

## 持有期间管理
### 定期检查
- 周度: 检查价格和量能
- 月度: 评估基本面变化
- 季度: 复核评级调整

### 预警阈值
| 预警类型 | 阈值 | 应对 |
|----------|------|------|
| 基本面恶化 | 评分下降>10分 | 减仓50% |
| 趋势破位 | 跌破重要均线 | 减仓观察 |
| 估值泡沫 | PE>40 | 逐步止盈 |
```

---

## 三、回测框架

### 3.1 回测信号定义

```json
{
  "backtest_signal": {
    "report_id": "rpt_001",
    "signal_date": "2026-04-12",
    "stock_code": "000333.SZ",
    "signal": "BUY",
    "signal_strength": 4,
    "entry_price": 72.50,
    "stop_loss": 61.00,
    "target_price": 95.00,
    "expected_return": 31.0,
    "expected_duration": 180,
    "comprehensive_score": 88
  }
}
```

### 3.2 回测参数设置

| 参数 | 数值 | 说明 |
|------|------|------|
| 回测区间 | 2020-01-01 至 2026-04-12 | 最近6年 |
| 初始资金 | 100万 | 模拟账户 |
| 印花税 | 0.1% | 单边征收 |
| 佣金 | 0.03% | 买卖双向 |
| 滑点 | 0.1% | 模拟成交偏差 |
| 最大持仓 | 10只 | 分散风险 |
| 单票仓位 | 10-20% | 根据评分 |

### 3.3 回测收益计算

```python
def calculate_returns(entry_price, exit_price, holding_days):
    """
    计算单笔交易收益

    公式:
    - 绝对收益 = (卖出价 - 买入价) / 买入价
    - 年化收益 = 绝对收益 / (持有天数 / 365)
    - 夏普比率 = (平均收益 - 无风险收益) / 收益标准差
    """
    absolute_return = (exit_price - entry_price) / entry_price
    annualized_return = absolute_return / (holding_days / 365)

    # 扣除交易成本
    trading_cost = 0.001 + 0.0003 * 2  # 印花税 + 佣金
    net_return = absolute_return - trading_cost

    return {
        "absolute_return": net_return,
        "annualized_return": net_return / (holding_days / 365),
        "holding_days": holding_days
    }
```

---

## 四、回测指标体系

### 4.1 收益类指标

| 指标 | 计算方式 | 评价标准 |
|------|----------|----------|
| 总收益率 | (期末-期初)/期初 | 越高越好 |
| 年化收益率 | 总收益/年数 | >15%优秀 |
| 超额收益 | 策略收益-基准收益 | >5%优秀 |
| 胜率 | 盈利交易/总交易 | >60%优秀 |

### 4.2 风险类指标

| 指标 | 计算方式 | 评价标准 |
|------|----------|----------|
| 最大回撤 | 最大浮亏比例 | <15%优秀 |
| 波动率 | 收益标准差 | <20%优秀 |
| 夏普比率 | (收益-无风险)/波动率 | >1.5优秀 |
| 卡玛比率 | 年化收益/最大回撤 | >2优秀 |

### 4.3 交易类指标

| 指标 | 计算方式 | 评价标准 |
|------|----------|----------|
| 交易次数 | 总交易笔数 | 适中 |
| 平均持仓 | 总持仓/交易次数 | 30-90天 |
| 换手率 | 年交易额/资金 | 适中 |
| 盈亏比 | 平均盈利/平均亏损 | >2优秀 |

---

## 五、回测报告模板

```markdown
# 操作回测报告

## 回测概况
| 项目 | 数值 |
|------|------|
| 回测区间 | 2020-01-01 至 2026-04-12 |
| 初始资金 | 100万元 |
| 期末资金 | XX万元 |
| 总收益率 | XX% |
| 年化收益 | XX% |
| 基准收益 | XX% |
| 超额收益 | XX% |

## 收益表现
| 指标 | 策略 | 基准 | 差异 |
|------|------|------|------|
| 总收益 | +85.6% | +45.2% | +40.4% |
| 年化收益 | +12.3% | +6.8% | +5.5% |
| 最大回撤 | -12.5% | -25.8% | +13.3% |

## 风险指标
| 指标 | 数值 | 评级 |
|------|------|------|
| 最大回撤 | -12.5% | 优秀 |
| 夏普比率 | 1.85 | 优秀 |
| 卡玛比率 | 0.98 | 良好 |
| 波动率 | 15.2% | 良好 |

## 交易统计
| 指标 | 数值 |
|------|------|
| 总交易次数 | 156次 |
| 盈利交易 | 98次 |
| 亏损交易 | 58次 |
| 胜率 | 62.8% |
| 平均盈利 | +8.5% |
| 平均亏损 | -4.2% |
| 盈亏比 | 2.02 |

## 按评级分析
| 评级 | 交易数 | 胜率 | 平均收益 |
|------|--------|------|----------|
| 强力买入 | 35 | 78% | +15.2% |
| 买入 | 45 | 65% | +10.5% |
| 中性偏强 | 40 | 52% | +3.2% |
| 持有 | 36 | 38% | -2.1% |

## 按评分区间分析
| 评分区间 | 交易数 | 胜率 | 平均收益 |
|----------|--------|------|----------|
| 85-100分 | 30 | 80% | +16.5% |
| 70-84分 | 50 | 67% | +11.2% |
| 55-69分 | 45 | 55% | +4.5% |
| 40-54分 | 31 | 35% | -3.5% |

## 典型案例
### 成功案例: 美的集团
- 买入日期: 2025-06-15
- 买入价格: ¥62.50
- 信号评分: 88分
- 评级: 强力买入
- 卖出日期: 2026-02-20
- 卖出价格: ¥92.00
- 持有天数: 250天
- 收益率: +47.2%

### 失败案例: XX股票
- 买入日期: 2025-03-10
- 买入价格: ¥45.00
- 信号评分: 72分
- 评级: 买入
- 止损日期: 2025-04-15
- 止损价格: ¥38.25
- 持有天数: 36天
- 收益率: -15.0%

## 结论与建议
### 主要发现
1. 高评分(85+)信号胜率显著高于低评分
2. 持有期限与收益正相关
3. 止损纪律对保护本金至关重要

### 策略优化建议
1. 提高高评分信号仓位
2. 延长优质标的持有期限
3. 严格执行止损纪律
```

---

## 六、稳健优化策略

### 6.1 仓位优化

```python
def optimize_position(comprehensive_score, risk_level):
    """
    根据评分和风险优化仓位

    规则:
    - 评分85+: 仓位15-20%
    - 评分70-84: 仓位10-15%
    - 评分55-69: 仓位5-10%
    - 评分<55: 仓位<5%
    """
    if comprehensive_score >= 85:
        base_position = 0.18
    elif comprehensive_score >= 70:
        base_position = 0.12
    elif comprehensive_score >= 55:
        base_position = 0.07
    else:
        base_position = 0.03

    # 根据风险等级调整
    risk_multiplier = {
        "LOW": 1.2,
        "MEDIUM": 1.0,
        "HIGH": 0.8
    }

    final_position = base_position * risk_multiplier.get(risk_level, 1.0)

    return min(final_position, 0.20)  # 最高20%仓位
```

### 6.2 止损优化

```python
def optimize_stop_loss(comprehensive_score, entry_price):
    """
    根据评分优化止损位

    规则:
    - 评分85+: 止损-15%
    - 评分70-84: 止损-12%
    - 评分55-69: 止损-10%
    - 评分<55: 止损-8%
    """
    stop_loss_pct = {
        (85, 100): 0.15,
        (70, 84): 0.12,
        (55, 69): 0.10,
        (0, 54): 0.08
    }

    for (low, high), pct in stop_loss_pct.items():
        if low <= comprehensive_score <= high:
            return entry_price * (1 - pct)

    return entry_price * 0.92
```

### 6.3 止盈优化

```python
def optimize_take_profit(comprehensive_score, entry_price):
    """
    根据评分优化止盈位

    规则:
    - 评分85+: 分批止盈 30%/50%/70%
    - 评分70-84: 分批止盈 20%/35%/50%
    - 评分55-69: 分批止盈 15%/25%/35%
    """
    take_profit_levels = {
        (85, 100): [0.30, 0.50, 0.70],
        (70, 84): [0.20, 0.35, 0.50],
        (55, 69): [0.15, 0.25, 0.35]
    }

    levels = take_profit_levels.get(
        next(k for k in take_profit_levels if k[0] <= comprehensive_score <= k[1]),
        [0.15, 0.25, 0.35]
    )

    return [entry_price * (1 + pct) for pct in levels]
```

---

## 七、动态调整机制

### 7.1 持仓期间调整

```python
def adjust_position(current_position, score_change, price_change):
    """
    持仓期间动态调整

    规则:
    - 评分上升>5分: 可加仓
    - 评分下降>5分: 需减仓
    - 评分下降>10分: 强制减仓50%
    - 价格突破止盈位: 分批减仓
    """
    adjustments = []

    if score_change > 5:
        adjustments.append(("加仓", "+5%"))
    elif score_change < -10:
        adjustments.append(("强制减仓", "-50%"))
    elif score_change < -5:
        adjustments.append(("减仓", "-10%"))

    if price_change > 0.30:
        adjustments.append(("止盈1", "-30%"))
    elif price_change > 0.50:
        adjustments.append(("止盈2", "-30%"))

    return adjustments
```

### 7.2 评分下调应对

```markdown
## 持仓期间评分调整应对

### 评分下降5-10分
- **评估**: 关注变化原因
- **操作**: 观察为主，不急于行动
- **阈值**: 评分<75需警惕

### 评分下降10-20分
- **评估**: 深入分析原因
- **操作**: 减仓50%
- **阈值**: 评分<70考虑清仓

### 评分下降>20分
- **评估**: 立即复核
- **操作**: 至少减仓80%
- **阈值**: 评分<60必须清仓
```

---

## 八、回测数据管理

### 8.1 数据存储结构

```sql
-- 操作信号表
CREATE TABLE trading_signals (
    id INT PRIMARY KEY AUTO_INCREMENT,
    report_id VARCHAR(50),
    stock_code VARCHAR(20),
    signal_date DATE,
    entry_price DECIMAL(10,2),
    target_price DECIMAL(10,2),
    stop_loss DECIMAL(10,2),
    position_ratio DECIMAL(5,2),
    comprehensive_score DECIMAL(5,2),
    rating VARCHAR(20),
    signal_type VARCHAR(10),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 持仓记录表
CREATE TABLE positions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    signal_id INT,
    stock_code VARCHAR(20),
    entry_price DECIMAL(10,2),
    current_price DECIMAL(10,2),
    position_ratio DECIMAL(5,2),
    unrealized_pnl DECIMAL(10,2),
    unrealized_pnl_pct DECIMAL(10,2),
    entry_date DATE,
    status VARCHAR(20),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (signal_id) REFERENCES trading_signals(id)
);

-- 交易记录表
CREATE TABLE trades (
    id INT PRIMARY KEY AUTO_INCREMENT,
    position_id INT,
    trade_type VARCHAR(10),
    price DECIMAL(10,2),
    quantity INT,
    amount DECIMAL(10,2),
    trading_cost DECIMAL(10,2),
    trade_date DATE,
    reason VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (position_id) REFERENCES positions(id)
);
```

### 8.2 回测分析查询

```sql
-- 按评分区间统计收益
SELECT
    CASE
        WHEN comprehensive_score >= 85 THEN '85-100分'
        WHEN comprehensive_score >= 70 THEN '70-84分'
        WHEN comprehensive_score >= 55 THEN '55-69分'
        ELSE '55分以下'
    END AS score_range,
    COUNT(*) AS trade_count,
    AVG(unrealized_pnl_pct) AS avg_return,
    SUM(CASE WHEN unrealized_pnl_pct > 0 THEN 1 ELSE 0 END) / COUNT(*) AS win_rate
FROM trading_signals
WHERE status = 'CLOSED'
GROUP BY score_range;

-- 按年度统计
SELECT
    YEAR(signal_date) AS year,
    COUNT(*) AS trade_count,
    AVG(unrealized_pnl_pct) AS avg_return,
    SUM(unrealized_pnl_pct) AS total_return,
    MAX(unrealized_pnl_pct) AS best_trade,
    MIN(unrealized_pnl_pct) AS worst_trade
FROM trading_signals
GROUP BY YEAR(signal_date)
ORDER BY year;
```

---

## 九、持续优化闭环

```
┌─────────────────────────────────────────────────────────────────────┐
│                      策略执行 → 数据收集 → 分析评估 → 策略优化       │
└─────────────────────────────────────────────────────────────────────┘
```

### 9.1 月度评审

```markdown
## 月度策略评审 (每月5日)

### 评审内容
1. 上月交易统计
2. 策略表现回顾
3. 异常交易分析
4. 参数优化建议

### 评审标准
- 月度收益 > 基准 → 继续执行
- 月度收益 < 基准-5% → 深入分析
- 连续2月表现不佳 → 策略复核
```

### 9.2 季度优化

```markdown
## 季度策略优化 (每季度首月)

### 优化内容
1. 权重调整
2. 阈值优化
3. 规则迭代
4. 新规则引入

### 优化依据
- 回测统计结果
- 实盘表现反馈
- 用户建议收集
```

---

## 十、风险控制要点

### 10.1 硬性规则

1. **单票仓位上限**: 20%
2. **总仓位上限**: 80%
3. **最小止损线**: -15%
4. **日度最大亏损**: -3%
5. **月度最大亏损**: -8%

### 10.2 熔断机制

| 触发条件 | 措施 |
|----------|------|
| 日度回撤>3% | 当日停止开新仓 |
| 月度回撤>8% | 减仓50% |
| 季度回撤>15% | 策略复核 |
| 单票回撤>20% | 强制清仓 |

### 10.3 黑名单制度

```markdown
## 风险标的处理

### 纳入黑名单条件
- 连续2次触发止损
- 突发重大利空
- 财务造假嫌疑
- 流动性枯竭

### 黑名单管理
- 观察期: 3个月
- 解禁条件: 重新覆盖并给出买入评级
```
