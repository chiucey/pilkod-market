---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 4eb96cd9c14e10ccb6e72586690875db
    PropagateID: 4eb96cd9c14e10ccb6e72586690875db
    ReservedCode1: 304402202bc0cfa3854f954b469080f83b8a48b5df4406ca107b6add3d22740fd6064e1302204019c70fea22f118deba57a3cf9541738ceef80594281c08d295cb235c8c8f04
    ReservedCode2: 3046022100b2598ffbfb4f554761ce54c47ac012d727391c9a4eef5f4d52fd871a98aa02fc022100935d253ee83d870fb8f9651db3fb9001289ce8b21b9818b4a6660e106042e3bd
description: Fudan Management School DSBA (Data Science and Business Analytics) exam preparation guide. Use when users need to prepare for DSBA admission exams, practice interview questions, or understand exam topics. Covers mathematical analysis, linear algebra, probability, Python programming, machine learning, and quantitative finance.
name: dsba-exam-prep
---

# DSBA保研备考助手

## 一、项目概览

DSBA（数据科学与商业分析）是复旦管理学院专硕项目，招生约50人，重点考察：
- 数学统计基础（数学分析、高等代数、概率论与数理统计）
- Python编程能力（2024年起新增笔试）
- 机器学习与量化金融知识

**近年趋势**：
- 2022年前：数学分析+高等代数+概率论（均为证明题，难度大）
- 2023年：难度下降，概率统计占比更大
- **2024年起**：新增Python编程笔试（计入总分）

---

## 二、笔试部分

### 题目1：数学分析 - 一致连续性证明

**题目**：设函数 $f(x) = \ln(1+x^2)$，证明 $f(x)$ 在 $\mathbb{R}$ 上一致连续。

**解答**：

对于 $f(x) = \ln(1+x^2)$，任取 $x_1, x_2 \in \mathbb{R}$：

$$|f(x_1) - f(x_2)| = |\ln(1+x_1^2) - \ln(1+x_2^2)| = \left|\ln\frac{1+x_1^2}{1+x_2^2}\right|$$

由拉格朗日中值定理，存在 $\xi$ 介于 $x_1$ 与 $x_2$ 之间，使得：

$$|f(x_1) - f(x_2)| = |f'(\xi)| \cdot |x_1 - x_2| = \frac{2|\xi|}{1+\xi^2} \cdot |x_1 - x_2|$$

由于 $\frac{2|\xi|}{1+\xi^2} \leq 1$ 对所有 $\xi \in \mathbb{R}$ 成立，故：

$$|f(x_1) - f(x_2)| \leq |x_1 - x_2|$$

对任意 $\varepsilon > 0$，取 $\delta = \varepsilon$，当 $|x_1 - x_2| < \delta$ 时：

$$|f(x_1) - f(x_2)| \leq |x_1 - x_2| < \varepsilon$$

故 $f(x)$ 在 $\mathbb{R}$ 上一致连续。$\square$

---

### 题目2：高等代数 - 特征值与特征向量

**题目**：设矩阵 $A = \begin{pmatrix} 2 & 1 \\ 1 & 2 \end{pmatrix}$

(1) 求 $A$ 的所有特征值和特征向量
(2) 判断 $A$ 是否正定
(3) 求 $A^{100}$

**解答**：

**(1) 求特征值**

特征方程：$|\lambda E - A| = 0$

$$\begin{vmatrix} \lambda-2 & -1 \\ -1 & \lambda-2 \end{vmatrix} = (\lambda-2)^2 - 1 = \lambda^2 - 4\lambda + 3 = 0$$

解得：$\lambda_1 = 1, \lambda_2 = 3$

- 当 $\lambda_1 = 1$ 时，特征向量：$\xi_1 = k(1, -1)^T, k \neq 0$
- 当 $\lambda_2 = 3$ 时，特征向量：$\xi_2 = k(1, 1)^T, k \neq 0$

**(2) 判断正定性**

$A$ 的主子式：$\Delta_1 = 2 > 0, \Delta_2 = \begin{vmatrix} 2 & 1 \\ 1 & 2 \end{vmatrix} = 3 > 0$，故 $A$ 正定。

**(3) 求 $A^{100}$**

$$A^{100} = P \begin{pmatrix} 1^{100} & 0 \\ 0 & 3^{100} \end{pmatrix} P^{-1} = \frac{1}{2} \begin{pmatrix} 1+3^{100} & 3^{100}-1 \\ 3^{100}-1 & 1+3^{100} \end{pmatrix}$$

---

### 题目3：概率论与数理统计 - 重期望公式

**题目**：设随机变量 $X \sim \text{Exp}(1)$，$Y|X=x \sim \text{Poisson}(x)$。求 $E(Y)$ 和 $\text{Var}(Y)$。

**解答**：

**(1) 求 $E(Y)$**

由全期望公式：$E(Y) = E[E(Y|X)] = E(X) = 1$

**(2) 求 $\text{Var}(Y)$**

$$\text{Var}(Y) = E[\text{Var}(Y|X)] + \text{Var}[E(Y|X)] = E(X) + \text{Var}(X) = 1 + 1 = 2$$

---

### 题目4：Python编程 - 列表推导式

**题目**：某电商平台有1000个商品的销售数据，存储在列表 `sales` 中，每个元素是一个包含 `(商品ID, 销量, 单价)` 的元组。请用Python完成：

(1) 计算总销售额
(2) 筛选出销量大于500的商品
(3) 用字典推导式统计各价位区间商品数量

**解答**：

```python
import random

sales = [(f"prod_{i}", random.randint(10, 1000), round(random.uniform(5, 500), 2)) for i in range(1000)]

# (1) 计算总销售额
total_revenue = sum(quantity * price for _, quantity, price in sales)
print(f"总销售额: {total_revenue:.2f} 元")

# (2) 筛选高销量商品
high_volume_products = [(pid, qty, price) for pid, qty, price in sales if qty > 500]
print(f"高销量商品数量: {len(high_volume_products)}")

# (3) 统计价位分布
price_categories = {
    '低价(<100)': len([p for _, _, price in sales if price < 100]),
    '中价(100-300)': len([p for _, _, price in sales if 100 <= price <= 300]),
    '高价(>300)': len([p for _, _, price in sales if price > 300])
}
print(f"价位分布: {price_categories}")
```

---

### 题目5：蒙特卡洛模拟 - 投资组合VaR计算

**题目**：用蒙特卡洛模拟方法计算投资组合在95%置信水平下的VaR。已知：
- 股票A：收益率0.1，波动率0.2
- 股票B：收益率0.15，波动率0.25
- 相关系数0.3，权重各50%

**解答**：

```python
import numpy as np

np.random.seed(42)
n_simulations = 10000
initial_investment = 1000000
mu_a, sigma_a = 0.1, 0.2
mu_b, sigma_b = 0.15, 0.25
rho = 0.3

# Cholesky分解生成相关随机数
cov_matrix = np.array([[sigma_a**2, rho*sigma_a*sigma_b],
                        [rho*sigma_a*sigma_b, sigma_b**2]])
chol = np.linalg.cholesky(cov_matrix)
z = np.random.standard_normal((n_simulations, 2))
z_correlated = z @ chol.T

# 计算组合收益率
returns_a = mu_a + z_correlated[:, 0]
returns_b = mu_b + z_correlated[:, 1]
portfolio_returns = 0.5 * returns_a + 0.5 * returns_b

# 计算VaR
portfolio_values = initial_investment * (1 + portfolio_returns)
var_95 = initial_investment - np.percentile(portfolio_values, 5)
print(f"95% VaR: {var_95:.2f} 元")
```

---

### 题目6：回归分析 - ANOVA组间组内平方和

**题目**：三种设计方案A、B、C的用户停留时间数据如下，计算SSB和SSW：

```python
design_a_times = [5, 6, 4, 2, 5, 8, 7, 9]
design_b_times = [6, 4, 8, 5, 5, 9, 6, 10]
design_c_times = [5, 6, 4, 5, 6, 7, 8, 6]
```

**解答**：

```python
def calculate_mean(times):
    return sum(times) / len(times)

def calculate_overall_mean(*args):
    total_sum = sum(sum(times) for times in args)
    total_length = sum(len(times) for times in args)
    return total_sum / total_length

def calculate_ssb(*args):
    """组间平方和 SSB = Σ n_i * (x̄_i - x̄)²"""
    overall_mean = calculate_overall_mean(*args)
    return sum(len(group) * (calculate_mean(group) - overall_mean)**2 for group in args)

def calculate_ssw(*args):
    """组内平方和 SSW = Σ Σ (x_ij - x̄_i)²"""
    ssw = 0
    for group in args:
        group_mean = calculate_mean(group)
        ssw += sum((x - group_mean)**2 for x in group)
    return ssw

ssb = calculate_ssb(design_a_times, design_b_times, design_c_times)
ssw = calculate_ssw(design_a_times, design_b_times, design_c_times)
print(f"SSB: {ssb:.2f}, SSW: {ssw:.2f}")
```

---

### 题目7：算法复杂度 - 冒泡排序

**题目**：分析以下代码的时间复杂度：

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
```

**解答**：

- 外层循环运行 $n$ 次
- 内层循环平均运行 $n/2$ 次
- **时间复杂度：$O(n^2)$**

---

## 三、面试部分

### 题目8：机器学习 - Lasso回归原理

**面试题目**：请介绍一下Lasso回归的原理，并说明它与Ridge回归的区别。

**参考答案**：

**Lasso回归目标函数**：
$$\min_{\beta} \sum_{i=1}^{n}(y_i - \beta_0 - \sum_{j=1}^{p}\beta_j x_{ij})^2 + \lambda \sum_{j=1}^{p}|\beta_j|$$

**核心特点**：
1. **稀疏性**：L1惩罚导致部分系数变为0，实现特征选择
2. **可解释性**：自动筛选重要特征
3. **适用于高维数据**

| 特性 | Lasso (L1) | Ridge (L2) |
|------|-----------|-----------|
| 惩罚项 | $\lambda\sum|\beta_j|$ | $\lambda\sum\beta_j^2$ |
| 特征选择 | 有 | 无 |
| 适用场景 | 高维稀疏数据 | 多重共线性 |

---

### 题目9：概率论 - 中心极限定理

**面试题目**：请解释中心极限定理，并说明实际应用场景。

**参考答案**：

**定理表述**：设 $X_1, X_2, ..., X_n$ 独立同分布，$E(X_i) = \mu$，$\text{Var}(X_i) = \sigma^2$，则：

$$\frac{\bar{X} - \mu}{\sigma / \sqrt{n}} \xrightarrow{d} N(0, 1)$$

**核心理解**：
- 无论原始分布如何，样本均值趋向正态分布
- 样本量一般 $n \geq 30$

**应用场景**：
1. 民意调查的置信区间计算
2. 质量控制图
3. 金融风险建模
4. 假设检验基础（t检验、ANOVA）

---

### 题目10：金融量化 - CAPM与APT对比

**面试题目**：请比较CAPM和APT模型的异同。

**参考答案**：

| 维度 | CAPM | APT |
|------|------|-----|
| 公式 | $E(R_i) = R_f + \beta_i [E(R_m) - R_f]$ | $E(R_i) = R_f + \sum \beta_{ij} f_j$ |
| 风险因子 | 单一市场因子 | 多因子模型 |
| 假设条件 | 严格（完全市场） | 相对宽松 |
| 特征选择 | 无 | 有（多因子） |

**APT优势**：
- 不需要市场投资组合
- 可纳入size、value、momentum等因子
- Fama-French模型就是APT思想的实证应用

---

### 题目11：统计学 - p值含义

**面试题目**：请解释p值的含义。

**参考答案**：

**定义**：p值是在原假设（$H_0$）成立的条件下，观察到检验统计量比实际观测值更极端的概率。

**决策规则**：
- p < 0.01：强烈拒绝 $H_0$
- 0.01 ≤ p < 0.05：拒绝 $H_0$
- p ≥ 0.10：不拒绝 $H_0$

**重要澄清**：
- ❌ p值不是"$H_0$为真的概率"
- ✅ p值是"在$H_0$为真时，获得这样数据的概率"
- 需要结合效应量一起报告

---

### 题目12：Python手写快速排序

**面试题目**：请手写快速排序算法，并分析其时间复杂度。

**参考答案**：

```python
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
```

**时间复杂度**：
| 情况 | 复杂度 | 原因 |
|------|--------|------|
| 最好 | $O(n\log n)$ | 划分均匀 |
| 最坏 | $O(n^2)$ | 已排序+固定基准 |
| 平均 | $O(n\log n)$ | 随机数据接近最好 |

---

## 四、高频考点总结

| 模块 | 笔试考点 | 面试考点 |
|------|---------|---------|
| 数学分析 | 一致连续、泰勒展开、级数 | 一致收敛、大数定律 |
| 高等代数 | 特征值、正定矩阵 | 正交矩阵、线性空间 |
| 概率统计 | MLE、假设检验、回归 | 中心极限定理、p值 |
| Python | 列表推导式、正则、Pandas | 算法复杂度、手写代码 |
| 机器学习 | - | Lasso、XGBoost、LSTM |
| 金融量化 | - | CAPM、APT、VaR |

---

## 五、推荐复习资料

- **数学分析**：马知恩《工科数学分析》
- **高等代数**：居余马《线性代数》
- **概率统计**：茆诗松《概率论与数理统计》
- **Python**：LeetCode简单题型、牛客网剑指offer