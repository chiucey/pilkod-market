---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100fc4fbcd86a36dfc64a32e4173e13f59dd670a8499235148201801b5ff358c58c02201cd7b758f9b15e48d704036af56d69e1a9521fcf1646932f78f37938d2567969
    ReservedCode2: 304502201c73825a84378321e3e1cadd67eca7205014b7fb6029da60fc4774c308624ca9022100b6dc5a0e09869d81714576a5b33781ba85b314640058cdc2ba87dc9308f2b5c6
---

# 完整公式推导与模型说明

## 1. 市场容量模型 (TAM/SAM/SOM)

### 基本公式

```
TAM = Total Population × Per Capita Annual Spending

SAM = TAM × Category Penetration Rate

SOM = SAM × Target Market Share
```

### 分层计算详解

#### TAM (Total Addressable Market)
总潜在市场 = 目标区域总人口 × 人均年消费额

```
TAM = Σᵢ (Population_i × Spending_i)
     i = 不同消费层级
```

#### SAM (Serviceable Addressable Market)
可服务市场 = 覆盖商圈人口 × 人均年消费额 × 品类渗透率

```
SAM = Covered_Population × Avg_Spending × Penetration_Rate
```

#### SOM (Serviceable Obtainable Market)
可获得市场 = SAM × 竞争后预期份额

```
SOM = SAM × (1 / (1 + HHI/10000)) × Competitive_Advantage_Factor
```

---

## 2. 竞争强度指标

### POI密度

```
POI_Density = Number_of_Competitors / Area_km²
```

### 最近邻距离

```
d_min = min(√[(x_c - x_i)² + (y_c - y_i)²])
```

其中：
- (x_c, y_c): 候选点坐标
- (x_i, y_i): 第i个竞品坐标

### 赫芬达尔-赫希曼指数 (HHI)

```
HHI = Σᵢ (Market_Share_i)² × 10000

Market_Share_i = Sales_i / Total_Market_Sales
```

#### HHI解读

| HHI范围 | 市场类型 | 特征 |
|---------|----------|------|
| < 1500 | 竞争型 | 无明显头部，市场分散 |
| 1500-2500 | 适度集中 | 开始出现规模效应 |
| > 2500 | 高度集中 | 头部效应明显，后进者压力大 |

### 距离衰减函数

#### 幂函数模型
```
F(d) = k × d^(-α)
```

其中：
- F(d): 距离d处的竞争影响力
- k: 强度系数
- α: 衰减指数（通常1.5-2.5）

#### 指数模型
```
F(d) = k × e^(-βd)
```

---

## 3. 客群匹配度模型

### 综合匹配指数

```
Match_Score = Σⱼ (w_j × M_j)

其中:
- w_j: 第j个维度权重
- M_j: 第j个维度匹配度
```

### 各维度计算

#### 年龄匹配度
```
M_age = 1 - |Target_Age - Actual_Age| / Age_Range
```

#### 收入匹配度
```
M_income = Overlap(Target_Range, Actual_Distribution) / Target_Range
```

#### 消费偏好匹配
```
M_preference = |Target_Preferences ∩ Actual_Top_Categories| / |Target_Preferences|
```

---

## 4. 销量预测模型

### 简化模型

```
Sales = Footfall × Conversion_Rate × AOV × Seasonal_Factor
```

#### 展开形式
```
Monthly_Sales = Daily_Footfall × 30 × r × AOV × (1 + β₁×Holiday + β₂×Promotion)
```

### 多元回归模型

```
Sales = β₀ + β₁×Footfall + β₂×Price + β₃×Promo_Indicator + β₄×Seasonality + ε
```

#### 对数形式（弹性分析）
```
ln(Sales) = β₀ + β₁×ln(Footfall) + β₂×ln(Price) + β₃×Promo + ε
```

解释：
- β₁: 需求价格弹性
- β₂: 客流弹性
- β₃: 促销弹性

### 时间序列ARIMA模型

```
ARIMA(p, d, q):

Δ^d Y_t = Σₚ(φ_i × Δ^d Y_{t-i}) + θ_q × ε_{t-j} + ε_t

其中:
- p: 自回归项数
- d: 差分阶数
- q: 移动平均项数
```

---

## 5. 成本与盈亏分析

### 成本结构

```
Total_Cost = Fixed_Cost + Variable_Cost

Fixed_Cost = Rent + Staff_Salary + Marketing + Depreciation

Variable_Cost = COGS × Sales_Volume
```

### 盈亏平衡点 (Break-Even Point)

```
BEP_Units = Fixed_Cost / (Unit_Price - Unit_Variable_Cost)

BEP_Revenue = BEP_Units × Unit_Price
```

或
```
BEP_Revenue = Fixed_Cost / Contribution_Margin_Ratio

Contribution_Margin_Ratio = (Revenue - Variable_Cost) / Revenue
```

### 投资回收期 (Payback Period)

```
Payback_Period = Initial_Investment / Annual_Net_Cash_Flow
```

### NPV计算

```
NPV = Σₜ [(Revenue_t - Cost_t) / (1 + r)^t] - Initial_Investment

其中:
- r: 折现率
- t: 年份
```

### IRR计算

```
NPV = 0 时对应的 r 即为 IRR

Σₜ [CF_t / (1 + IRR)^t] = Initial_Investment
```

---

## 6. 敏感性分析

###  Tornado图数据

```
Impact_i = NPV_i(high) - NPV_i(low)

标准化影响:
Normalized_Impact_i = Impact_i / Max(Impact) × 100%
```

### 蒙特卡洛模拟

```
NPV_sim = f(X₁, X₂, ..., Xₙ)

其中 Xᵢ ~ Distribution(μᵢ, σᵢ)

结果: P(NPV > 0) = 成功率
```

---

## 7. 综合选址评分

### 加权评分模型

```
Score_j = Σᵢ (w_i × Normalized_Value_ij)

其中:
- Score_j: 候选点j的综合得分
- w_i: 指标i的权重
- Normalized_Value_ij: 指标i在候选点j的标准化值
```

### AHP层次分析法权重确定

```latex
CR = CI / RI < 0.1 时，判断矩阵一致性可接受

CI = (λ_max - n) / (n - 1)

其中:
- λ_max: 最大特征值
- n: 矩阵阶数
- RI: 随机一致性指标
```

---

## 8. 关键假设清单模板

```markdown
| 假设项 | 假设值 | 依据 | 影响程度 | 缓解措施 |
|--------|--------|------|----------|----------|
| 品类渗透率 | 15% | 行业报告 | 中 | 敏感性分析 |
| 转化率 | 5% | 同类门店均值 | 高 | 保守估计 |
| 租金增长率 | 3%/年 | 历史数据 | 低 | 合同条款 |
```

---

*公式版本: 1.0.0 | 更新日期: 2026-04-25*
