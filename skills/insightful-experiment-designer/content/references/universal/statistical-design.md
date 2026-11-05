# 统计实验设计

> 适用于所有需要统计推断的研究领域

---

## 核心概念

### 统计实验 vs 确定实验
```
统计实验：关注推断，有随机变异
  → 关注：效应大小、置信区间、统计显著性

确定实验：无随机变异（如工程模拟）
  → 关注：点估计、误差传播、灵敏度分析
```

---

## 样本量计算原理

### 核心公式（两样本比较）
```
n = 2 × (Z_α + Z_β)² × σ² / δ²

其中：
- Z_α = 1.96 (α = 0.05, 双侧检验)
- Z_β = 0.84 (检验力 = 0.80)
- σ = 标准差（估计值）
- δ = 最小可检测效应

简化版（已知变异系数时）：
n ≈ 8 × CV² / (效应量)²
```

### 效应量的度量

| 领域 | 常用度量 | 解释 |
|------|---------|------|
| 连续变量 | Cohen's d | 标准化均值差异 |
| 比例/率 | Cohen's h | 比例差异 |
| 相关性 | r | 相关系数 |
| 方差分析 | f | 效应量 f |
| 机器学习 | AUC, F1 | 分类性能 |

### Cohen's d 参考标准
```
小效应：d = 0.2
中等效应：d = 0.5
大效应：d = 0.8

注：具体领域的"可接受效应"可能不同
```

---

## 多领域功效分析

### 生物医学
```r
# 两组比较
library(pwr)
pwr.t.test(d = 0.5, sig.level = 0.05, power = 0.80)
# 每组需要 n = 64

# 多组 ANOVA
pwr.anova.test(k = 4, f = 0.25, sig.level = 0.05, power = 0.80)
```

### 工程/制造业
```r
# 等价性检验
# 效应量用过程标准差的倍数表示
delta_acceptable <- 0.1 * sigma  # 可接受差异为 10% sigma

# 估计所需重复数
n <- (2 * sigma^2) / (delta_acceptable^2) * (Z_alpha + Z_beta)^2
```

### 软件/A/B 测试
```python
# Python 示例
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

power_analysis = NormalIndPower()
effect_size = proportion_effectsize(0.10, 0.12)  # 10% vs 12% 转化率
n = power_analysis.solve_power(effect_size, power=0.80, alpha=0.05)
```

### 机器学习
```python
# 超参数调优的样本量
# 经验法则：每个超参数组合至少 30 次重复
# 或基于方差估计

import numpy as np
variance_estimate = 0.01  # 从预实验估计
desired_ci_width = 0.05
n = 4 * variance_estimate / (desired_ci_width / 1.96)^2
```

---

## 多元设计

### 因子设计
```
全因子设计：2^k 或 3^k
  - 优点：可估计交互作用
  - 缺点：样本量指数增长

部分因子设计：2^(k-p)
  - 优点：减少实验次数
  - 缺点：部分效应混杂

筛选设计：Plackett-Burman
  - 优点：高效筛选大量因子
  - 缺点：仅估计主效应
```

### 响应面设计
```
Central Composite Design (CCD)
  - 适合：优化连续参数
  - 可拟合二次模型

Box-Behnken Design
  - 优点：无极端组合
  - 适合：安全性约束场景
```

---

## 序贯设计与适应性试验

### 序贯分析
```
优势：
- 可提前停止（效应明显时）
- 可增加样本（效应不确定时）

方法：
- 成组序贯设计（group sequential）
- 自适应随机化
- 贝叶斯序贯设计
```

### 样本量再估计
```
期中分析时允许调整：
□ 非盲态再估计（基于累积数据）
□ 盲态再估计（基于总方差）
□ 禁止：基于已观测效应值调整
```

---

## 多重比较控制

### 问题
```
m 个比较时：
- 若每个用 α = 0.05
- 家族误差率 FWER = 1 - (1-0.05)^m
- m = 10 时，FWER ≈ 40%
```

### 控制方法
| 方法 | 控制 | 适用场景 |
|------|------|---------|
| Bonferroni | FWER | 保守，简单 |
| Holm | FWER | 比 Bonferroni 功效更高 |
| Benjamini-Hochberg | FDR | 探索性，发现导向 |
| Tukey HSD | 配对比较 | 两两比较 |

### FDR vs FWER 选择
```
FWER 控制：结论必须可靠，避免假阳性
  → 临床试验，法规要求场景

FDR 控制：容许一定假阳性，最大化发现
  → 探索性组学筛选，机器学习特征选择
```

---

## 实际计算工具

### R 包
```r
library(pwr)      # 基础功效分析
library(powerAnalysis)  # 直观界面
library(POWERr)   # 贝叶斯功效分析
library(lmPerm)    # 置换检验
```

### Python 库
```python
from statsmodels.stats.power import TTestIndPower, FTestAnovaPower
from scipy.stats import norm
# 或使用 pingouin 库
import pingouin as pg
```

### 在线工具
- G*Power (免费桌面软件)
- Russ Lenth's Power Calculator
- ClinCalc Sample Size Calculator

---

## 常见错误

### 样本量估计错误
```
□ 使用期望效应而非最小可检测效应
□ 忽略多重比较的 alpha 校正
□ 使用单尾检验但实际需要双尾
□ 未考虑多重检验的样本量膨胀
□ 混淆技术重复和生物重复
```

### 功效不足的后果
```
□ 假阴性率升高
□ 浪费资源（收集了无统计意义的数据）
□ 伦理问题（受试者暴露于无效研究中）
□ 发表偏倚（阴性结果难以发表）
```
