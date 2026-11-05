---
name: portfolio-optimizer
description: 资产组合优化技能。基于马科维茨有效前沿、风险平价、目标波动率等现代投资组合理论，构建股票、基金、ETF、债券等大类资产的最优配置方案。当用户要求进行资产配置、组合优化、计算有效前沿、风险平价权重、目标波动率权重、大类资产配置、组合波动率计算、最优权重计算时使用。提供相关性分析、分散化效果评估、组合绩效预测（年化收益、夏普比率、最大回撤）、约束条件处理及再平衡建议。仅为模型计算工具，不构成任何投资理财建议。
---

# 资产组合优化技能

## 技能概述

本技能提供专业的投资组合优化计算服务，基于诺贝尔经济学奖获得者哈里·马科维茨开创的现代投资组合理论（MPT），结合风险平价、目标波动率等先进配置方法，帮助用户构建科学的大类资产配置方案。

**核心功能**：
- 多资产相关性分析与分散化效果评估
- 马科维茨有效前沿计算与最优组合筛选
- 风险平价（Risk Parity）权重配置
- 目标波动率（Target Volatility）权重优化
- 组合绩效指标计算与预测
- 各类约束条件处理
- 再平衡策略建议

**重要声明**：本技能仅提供模型计算服务，不构成任何形式的投资理财建议。所有计算结果仅供参考，用户需自行承担投资决策风险。

## 输入参数

### 必需参数

| 参数名称 | 类型 | 说明 | 示例 |
|---------|------|------|------|
| asset_pool | list | 资产池列表，包含资产代码和类型 | [{"code": "000001", "name": "沪深300", "type": "stock"}, {"code": "510300", "name": "沪深300ETF", "type": "etf"}] |
| expected_returns | dict | 各资产预期年化收益率 | {"000001": 0.12, "510300": 0.10, "Bond": 0.04} |
| covariance_matrix | dict | 收益率协方差矩阵（嵌套字典） | {"000001": {"000001": 0.04, "510300": 0.02}} |
| risk_preference | string | 风险偏好等级 | "conservative" / "moderate" / "aggressive" |

### 可选参数

| 参数名称 | 类型 | 说明 | 默认值 |
|---------|------|------|--------|
| target_return | float | 目标收益率 | 无约束 |
| target_volatility | float | 目标波动率 | 无约束 |
| max_weight | dict | 单资产权重上限 | 0.3 |
| min_weight | dict | 单资产权重下限 | 0.0 |
| rebalance_threshold | float | 再平衡触发阈值 | 0.05 |
| correlation_matrix | dict | 相关系数矩阵（可从协方差矩阵推导） | 自动计算 |

### 风险偏好等级定义

- **conservative（保守型）**：追求本金安全，偏好低波动资产，允许牺牲部分收益
- **moderate（平衡型）**：追求风险收益平衡，在可控风险下追求合理收益
- **aggressive（激进型）**：追求高收益，接受较大波动，适合长期投资

## 执行流程

### 第一阶段：数据准备与预处理

#### 1.1 资产数据解析

解析用户提供的资产池信息，验证资产类型和数量：

```python
# 输入验证
assert len(asset_pool) >= 2, "资产池至少需要包含2个资产"
assert len(asset_pool) <= 50, "资产池最多支持50个资产"

# 资产类型统计
asset_types = {}
for asset in asset_pool:
    asset_type = asset.get("type", "unknown")
    asset_types[asset_type] = asset_types.get(asset_type, 0) + 1
```

#### 1.2 协方差矩阵构建与验证

确保协方差矩阵的正定性（半正定性）和对称性：

```python
import numpy as np

# 转换为numpy矩阵
n = len(asset_pool)
cov_matrix = np.zeros((n, n))

for i, asset_i in enumerate(asset_pool):
    for j, asset_j in enumerate(asset_pool):
        cov_matrix[i, j] = covariance_matrix.get(asset_i["code"], {}).get(asset_j["code"], 0)

# 验证对称性
assert np.allclose(cov_matrix, cov_matrix.T), "协方差矩阵必须对称"

# 验证正定性（特征值检查）
eigenvalues = np.linalg.eigvalsh(cov_matrix)
assert np.all(eigenvalues >= -1e-10), "协方差矩阵必须半正定"
```

#### 1.3 相关性分析

计算资产间的相关系数矩阵：

```python
def calculate_correlation_matrix(cov_matrix, std_devs):
    """从协方差矩阵推导相关系数矩阵"""
    n = len(std_devs)
    corr_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if std_devs[i] > 0 and std_devs[j] > 0:
                corr_matrix[i, j] = cov_matrix[i, j] / (std_devs[i] * std_devs[j])
    return corr_matrix
```

### 第二阶段：组合优化计算

#### 2.1 马科维茨有效前沿

使用二次规划求解有效前沿：

```python
from scipy.optimize import minimize
import scipy.stats as stats

def portfolio_return(weights, expected_returns):
    """计算组合预期收益"""
    return np.dot(weights, expected_returns)

def portfolio_volatility(weights, cov_matrix):
    """计算组合波动率"""
    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

def portfolio_sharpe_ratio(weights, expected_returns, cov_matrix, risk_free_rate=0.03):
    """计算组合夏普比率"""
    ret = portfolio_return(weights, expected_returns)
    vol = portfolio_volatility(weights, cov_matrix)
    return (ret - risk_free_rate) / vol if vol > 0 else 0

def efficient_frontier(expected_returns, cov_matrix, n_portfolios=100, risk_free_rate=0.03):
    """计算有效前沿"""
    n_assets = len(expected_returns)

    # 收益范围
    min_return = np.min(expected_returns)
    max_return = np.max(expected_returns)
    target_returns = np.linspace(min_return, max_return, n_portfolios)

    results = []

    for target_ret in target_returns:
        # 优化目标：最小化波动率
        constraints = [
            {"type": "eq", "fun": lambda w, r=target_ret: np.sum(w) - 1},
            {"type": "eq", "fun": lambda w, r=target_ret: portfolio_return(w, expected_returns) - r}
        ]

        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_weights = np.array([1.0 / n_assets] * n_assets)

        result = minimize(
            portfolio_volatility,
            initial_weights,
            args=(cov_matrix,),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints
        )

        if result.success:
            results.append({
                "weights": result.x,
                "return": target_ret,
                "volatility": result.fun,
                "sharpe_ratio": (target_ret - risk_free_rate) / result.fun if result.fun > 0 else 0
            })

    return results
```

#### 2.2 风险平价权重计算

风险平价的核心思想是让每个资产对组合总风险的贡献相等：

```python
def risk_contribution(weights, cov_matrix):
    """计算各资产的风险贡献"""
    portfolio_vol = portfolio_volatility(weights, cov_matrix)
    marginal_contrib = np.dot(cov_matrix, weights)
    risk_contrib = weights * marginal_contrib / portfolio_vol
    return risk_contrib

def risk_parity_weights(expected_returns, cov_matrix, risk_target=None):
    """风险平价优化"""
    n_assets = len(expected_returns)

    def risk_parity_objective(weights):
        """风险平价目标函数：最小化风险贡献方差"""
        rc = risk_contribution(weights, cov_matrix)
        target_rc = np.sum(rc) / n_assets
        return np.sum((rc - target_rc) ** 2)

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]

    bounds = tuple((0.01, 1) for _ in range(n_assets))
    initial_weights = np.array([1.0 / n_assets] * n_assets)

    result = minimize(
        risk_parity_objective,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )

    if result.success:
        return result.x
    else:
        # 如果优化失败，返回等权重
        return initial_weights
```

#### 2.3 目标波动率权重优化

在目标波动率约束下最大化预期收益：

```python
def target_volatility_weights(expected_returns, cov_matrix, target_vol, max_weights=None, min_weights=None):
    """目标波动率优化"""
    n_assets = len(expected_returns)

    def neg_sharpe(weights):
        """负夏普比率（最大化夏普比率）"""
        ret = portfolio_return(weights, expected_returns)
        vol = portfolio_volatility(weights, cov_matrix)
        return -(ret - 0.03) / vol if vol > 0 else 0

    constraints = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1},
        {"type": "ineq", "fun": lambda w: target_vol - portfolio_volatility(w, cov_matrix)}
    ]

    bounds = []
    for _ in range(n_assets):
        if max_weights:
            upper = max_weights.get(_, 1.0)
        else:
            upper = 1.0
        if min_weights:
            lower = min_weights.get(_, 0.0)
        else:
            lower = 0.0
        bounds.append((lower, upper))

    initial_weights = np.array([1.0 / n_assets] * n_assets)

    result = minimize(
        neg_sharpe,
        initial_weights,
        method="SLSQP",
        bounds=tuple(bounds),
        constraints=constraints
    )

    return result.x if result.success else initial_weights
```

#### 2.4 最优组合选择

根据风险偏好选择最优组合：

```python
def select_optimal_portfolio(frontier_results, risk_preference):
    """根据风险偏好选择最优组合"""
    if not frontier_results:
        return None

    if risk_preference == "conservative":
        # 保守型：选择波动率最低的组合
        return min(frontier_results, key=lambda x: x["volatility"])
    elif risk_preference == "aggressive":
        # 激进型：选择夏普比率最高的组合
        return max(frontier_results, key=lambda x: x["sharpe_ratio"])
    else:
        # 平衡型：选择最大夏普比率
        return max(frontier_results, key=lambda x: x["sharpe_ratio"])
```

### 第三阶段：绩效评估与预测

#### 3.1 核心绩效指标

```python
def calculate_maximum_drawdown(weights, expected_returns, cov_matrix, n_scenarios=10000):
    """蒙特卡洛模拟估算最大回撤"""
    n_assets = len(weights)
    annual_returns = np.random.multivariate_normal(expected_returns, cov_matrix, n_scenarios)
    portfolio_returns = np.dot(annual_returns, weights)

    # 计算累积收益路径
    cumulative = np.cumprod(1 + portfolio_returns)
    running_max = np.maximum.accumulate(cumulative)
    drawdowns = (cumulative - running_max) / running_max

    return np.min(drawdowns)

def calculate_sortino_ratio(weights, expected_returns, cov_matrix, target_return=0, risk_free_rate=0.03):
    """计算索提诺比率（下行波动率）"""
    n_assets = len(weights)
    portfolio_ret = portfolio_return(weights, expected_returns)

    # 下行偏差
    std_devs = np.sqrt(np.diag(cov_matrix))
    returns_std = np.random.normal(0, 1, 10000)
    downside_returns = returns_std[returns_std < (target_return - portfolio_ret) / 100]
    downside_deviation = np.std(downside_returns) if len(downside_returns) > 0 else 0

    return (portfolio_ret - risk_free_rate) / downside_deviation if downside_deviation > 0 else 0

def portfolio_performance_report(weights, expected_returns, cov_matrix, risk_free_rate=0.03):
    """生成完整的绩效报告"""
    annual_return = portfolio_return(weights, expected_returns)
    annual_volatility = portfolio_volatility(weights, cov_matrix)
    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
    max_drawdown = calculate_maximum_drawdown(weights, expected_returns, cov_matrix)

    return {
        "annual_return": annual_return,
        "annual_volatility": annual_volatility,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "information_ratio": annual_return / annual_volatility if annual_volatility > 0 else 0
    }
```

#### 3.2 分散化效果评估

```python
def calculate_diversification_metrics(corr_matrix, weights, cov_matrix):
    """评估组合分散化效果"""
    # 加权平均相关系数
    n = len(weights)
    weighted_corr = 0
    for i in range(n):
        for j in range(i + 1, n):
            weighted_corr += weights[i] * weights[j] * corr_matrix[i, j]

    # 加权平均波动率
    std_devs = np.sqrt(np.diag(cov_matrix))
    weighted_avg_vol = np.dot(weights, std_devs)

    # 实际组合波动率
    actual_vol = portfolio_volatility(weights, cov_matrix)

    # 分散化比率
    diversification_ratio = weighted_avg_vol / actual_vol if actual_vol > 0 else 1

    return {
        "weighted_correlation": weighted_corr,
        "diversification_ratio": diversification_ratio,
        "weighted_avg_volatility": weighted_avg_vol,
        "actual_volatility": actual_vol,
        "diversification_benefit": weighted_avg_vol - actual_vol
    }
```

### 第四阶段：约束处理

#### 4.1 常见约束条件

```python
class PortfolioConstraints:
    """组合约束处理器"""

    def __init__(self, max_weight=0.3, min_weight=0, max_sector_weight=0.5):
        self.max_weight = max_weight
        self.min_weight = min_weight
        self.max_sector_weight = max_sector_weight

    def apply_weight_constraints(self, weights):
        """应用权重上下限约束"""
        return np.clip(weights, self.min_weight, self.max_weight)

    def apply_sector_constraints(self, weights, sector_mapping):
        """应用行业集中度约束"""
        n_assets = len(weights)
        adjusted_weights = weights.copy()

        sector_weights = {}
        for i, (code, sector) in enumerate(sector_mapping.items()):
            sector_weights[sector] = sector_weights.get(sector, 0) + weights[i]

        for sector, total_weight in sector_weights.items():
            if total_weight > self.max_sector_weight:
                scale = self.max_sector_weight / total_weight
                for i, (code, sec) in enumerate(sector_mapping.items()):
                    if sec == sector:
                        adjusted_weights[i] *= scale

        return adjusted_weights / np.sum(adjusted_weights)

    def apply_liquidity_constraints(self, weights, liquidity_scores):
        """应用流动性约束"""
        adjusted_weights = weights.copy()
        for i, score in enumerate(liquidity_scores):
            if score < 0.3:  # 流动性不足
                adjusted_weights[i] = min(adjusted_weights[i], 0.05)
        return adjusted_weights

def optimize_with_constraints(expected_returns, cov_matrix, constraints, method="risk_parity"):
    """带约束的优化"""
    if method == "risk_parity":
        base_weights = risk_parity_weights(expected_returns, cov_matrix)
    elif method == "max_sharpe":
        base_weights = max_sharpe_weights(expected_returns, cov_matrix)
    else:
        base_weights = np.array([1.0 / len(expected_returns)] * len(expected_returns))

    # 应用约束
    weights = constraints.apply_weight_constraints(base_weights)

    return weights
```

### 第五阶段：再平衡建议

#### 5.1 再平衡策略

```python
def generate_rebalance_suggestions(current_weights, target_weights, threshold=0.05):
    """生成再平衡建议"""
    suggestions = []

    for i, (curr, tgt) in enumerate(zip(current_weights, target_weights)):
        deviation = abs(curr - tgt)

        if deviation > threshold:
            action = "买入" if tgt > curr else "卖出"
            change_pct = (tgt - curr) * 100

            suggestions.append({
                "asset_index": i,
                "current_weight": curr,
                "target_weight": tgt,
                "deviation": deviation,
                "action": action,
                "change_percentage": abs(change_pct),
                "priority": "high" if deviation > 0.1 else "medium"
            })

    # 按偏离度排序
    suggestions.sort(key=lambda x: x["deviation"], reverse=True)

    return suggestions

def calculate_rebalance_cost(current_weights, target_weights, turnover_cost=0.001):
    """估算再平衡交易成本"""
    total_turnover = np.sum(np.abs(np.array(current_weights) - np.array(target_weights)))
    cost = total_turnover * turnover_cost
    return {
        "total_turnover": total_turnover,
        "estimated_cost": cost,
        "cost_percentage": cost * 100
    }
```

## 输出格式

### 标准输出结构

```json
{
  "status": "success",
  "optimization_result": {
    "optimal_weights": {
      "asset_1": 0.25,
      "asset_2": 0.35,
      "asset_3": 0.40
    },
    "performance_metrics": {
      "expected_annual_return": 0.1085,
      "annual_volatility": 0.1523,
      "sharpe_ratio": 0.516,
      "max_drawdown": -0.1825,
      "sortino_ratio": 0.623
    },
    "diversification_analysis": {
      "weighted_correlation": 0.35,
      "diversification_ratio": 1.23,
      "分散化收益": 0.021
    },
    "efficient_frontier": [
      {"return": 0.08, "volatility": 0.12, "sharpe": 0.42},
      {"return": 0.10, "volatility": 0.15, "sharpe": 0.47}
    ],
    "risk_contributions": {
      "asset_1": 0.30,
      "asset_2": 0.35,
      "asset_3": 0.35
    }
  },
    "rebalance_suggestions": [
      {
        "asset": "asset_1",
        "action": "买入",
        "change_percentage": 5.2,
        "priority": "medium"
      }
    ],
    "warnings": [
      "历史收益不代表未来表现",
      "极端市场条件下组合表现可能与预期不符"
    ]
  }
}
```

## 使用示例

### 示例1：基本资产配置

**用户输入**：
```
帮我进行资产配置，资产池包含：
- 沪深300指数（预期收益10%）
- 创业板指（预期收益15%）
- 国债（预期收益4%）
- 黄金ETF（预期收益8%）

风险偏好为平衡型。
```

**技能处理**：

```python
# 1. 构建协方差矩阵（需用户提供或使用历史数据估算）
covariance_matrix = {
    "HS300": {"HS300": 0.04, "GEM": 0.025, "Bond": -0.002, "Gold": 0.003},
    "GEM": {"HS300": 0.025, "GEM": 0.09, "Bond": -0.001, "Gold": 0.005},
    "Bond": {"HS300": -0.002, "GEM": -0.001, "Bond": 0.0025, "Gold": 0.001},
    "Gold": {"HS300": 0.003, "GEM": 0.005, "Bond": 0.001, "Gold": 0.04}
}

# 2. 执行优化
result = optimize_portfolio(
    asset_pool=["HS300", "GEM", "Bond", "Gold"],
    expected_returns={"HS300": 0.10, "GEM": 0.15, "Bond": 0.04, "Gold": 0.08},
    covariance_matrix=covariance_matrix,
    risk_preference="moderate"
)
```

### 示例2：目标波动率约束

**用户输入**：
```
我想构建一个年化波动率不超过12%的组合。
```

**技能处理**：

```python
result = target_volatility_weights(
    expected_returns=expected_returns,
    cov_matrix=covariance_matrix,
    target_vol=0.12,
    max_weights={"HS300": 0.4, "GEM": 0.3, "Bond": 0.6, "Gold": 0.2}
)
```

## 风险提示

1. **模型局限性**：所有优化模型均基于历史数据和预设假设，实际情况可能与模型预测存在显著差异。

2. **参数敏感性**：优化结果对输入参数（如预期收益、协方差矩阵）高度敏感，微小参数变化可能导致较大权重差异。

3. **尾部风险**：模型主要关注均值-方差优化，无法充分捕捉极端尾部事件风险。

4. **流动性风险**：优化结果可能包含流动性较差的资产，实际交易时可能面临流动性约束。

5. **交易成本**：实际再平衡操作涉及交易成本，可能影响组合实际表现。

6. **市场环境变化**：市场结构性变化可能导致历史相关性、波动率等参数失效。

## 依赖模块

- `numpy`：数值计算和矩阵运算
- `scipy`：优化算法和统计函数
- `pandas`：数据处理和分析

## 使用限制

- 单次优化最多支持50个资产
- 支持的资产类型：股票、基金、ETF、债券、商品、现金
- 所有计算均为单次模型计算，不提供实时数据更新
- 不提供具体投资标的推荐
- 不执行任何实际交易操作
