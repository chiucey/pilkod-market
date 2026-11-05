# 统计方法参考文献

本文档提供 SKILL.md 中引用的统计方法的详细说明和文献来源。

---

## 1. 假设检验基础

### 1.1 P值的正确解读

**正确解读（GraphPad Prism 标准）：**
> P = probability of observing a difference as large as observed, **if the null hypothesis is true**.

**公式表达：**
$$P = P(observed\ data\ |\ H_0\ is\ true)$$

**常见误解（⚠️ 禁止使用）：**
- ❌ "P = 3% 概率认为差异是真实的" —— 这是逆向条件错误
- ❌ "P = 差异是假阳性的概率" —— 混淆了条件概率

**参考文献：**
- GraphPad Prism 11, *The most common misinterpretation of a P value*, www.graphpad.com/guides/prism/latest/statistics

### 1.2 置信区间的正确解读

95% 置信区间的含义：
> 如果从同一总体中重复抽样无数次，95% 的置信区间将包含真实的总体参数。

⚠️ **常见误解：** 这不是说"真实值有 95% 的概率落在区间内"。

**参考文献：**
- GraphPad Prism 11, *Advantages of reporting confidence intervals*, www.graphpad.com/guides/prism/latest/statistics

---

## 2. 效应量

### 2.1 Cohen's d

$$d = \frac{\bar{X}_1 - \bar{X}_2}{SD_{pooled}}$$

其中：
$$SD_{pooled} = \sqrt{\frac{(n_1-1)SD_1^2 + (n_2-1)SD_2^2}{n_1+n_2-2}}$$

**解读阈值（Cohen 1988）：**
| |d| 范围 | 解读 |
|---|------|------|
| 微小效应 | < 0.2 | 可能无实际意义 |
| 小效应 | ≈ 0.2 | 需要大样本才能检测 |
| 中等效应 | ≈ 0.5 | 实际意义中等 |
| 大效应 | ≈ 0.8 | 通常有实际意义 |
| 很大效应 | ≈ 1.2 | 实际意义显著 |

**参考文献：**
- Cohen J (1988). *Statistical Power Analysis for the Behavioral Sciences*. 2nd ed. Erlbaum.

### 2.2 其他效应量指标

| 类型 | 适用场景 | 公式/说明 |
|------|---------|----------|
| Glass's Δ | 两组，方差不等 | Δ = (X̄₁ - X̄₂) / SD₂ |
| Hedges' g | 小样本校正 | g = d × (1 - 3/(4df-1)) |
| Pearson r | 相关性 | r = √(t²/(t²+df)) |
| Odds Ratio (OR) | 分类结局 | OR = (a/c)/(b/d) |
| Relative Risk (RR) | 队列研究 | RR = (a/(a+b))/(c/(c+d)) |

---

## 3. 参数检验

### 3.1 Welch's t-test

**为何使用 Welch's t-test 而非 Student's t-test：**

当两组方差不等时（σ₁² ≠ σ₂²），Student's t-test 的第一类错误率会膨胀。

Welch's t-test 公式：
$$t = \frac{\bar{X}_1 - \bar{X}_2}{\sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}}}$$

自由度（Welch-Satterthwaite 近似）：
$$df = \frac{\left(\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}\right)^2}{\frac{s_1^4}{n_1^2(n_1-1)} + \frac{s_2^4}{n_2^2(n_2-1)}}$$

**参考文献：**
- Welch BL (1947). *Biometrika* 34:28-35.
- GraphPad Prism 11, *The unpaired t test — Choosing between the two versions*

### 3.2 单因素 ANOVA

**假设：**
1. 独立性
2. 正态性（组内，N≥15 时稳健）
3. 方差齐性

**参考文献：**
- Fisher RA (1925). *Statistical Methods for Research Workers*.
- GraphPad Prism 11, *One-way ANOVA*

### 3.3 事后比较（Post-hoc）

| 方法 | 控制 | 适用场景 |
|------|------|---------|
| Tukey HSD | 族错误率 (FWER) | 组数 ≤ 5 |
| Bonferroni | FWER | 保守 |
| Dunnett | 与对照组的比较 | 有对照组时 |
| Benjamini-Hochberg | FDR | 探索性研究 |

**参考文献：**
- Tukey JW (1949). *Biometrics* 5:99-114.
- Benjamini Y, Hochberg Y (1995). *J Royal Stat Soc B* 57:289-300.

---

## 4. 非参数检验

### 4.1 Mann-Whitney U 检验

**适用：** 两组独立样本的序数或连续数据，不满足正态假设

**原理：** 比较两组秩和

**假设：**
1. 两组分布形状相同（仅位置参数可能不同）
2. 独立性

⚠️ **注意事项：**
- Lognormal 数据（正偏态）：报告 median + IQR 而非 mean + SD
- 不要用 Grubbs 检验 outlier——高值可能是真实的自然变异

**参考文献：**
- Mann HB, Whitney DR (1947). *Annals of Math Stat* 18:50-60.
- GraphPad Prism 11, *The Mann-Whitney test*

### 4.2 Wilcoxon 符号秩检验

**适用：** 配对样本

**参考文献：**
- Wilcoxon F (1945). *Biometrics Bulletin* 1:80-83.

### 4.3 Kruskal-Wallis 检验

**适用：** 三组及以上独立样本

**参考文献：**
- Kruskal WH, Wallis WA (1952). *J American Stat Assoc* 47:583-621.

---

## 5. 相关性分析

### 5.1 Pearson 相关系数

**适用：** 两变量均为连续型，关系线性，数据近似双变量正态

**公式：**
$$r = \frac{\sum(X_i - \bar{X})(Y_i - \bar{Y})}{\sqrt{\sum(X_i - \bar{X})^2 \sum(Y_i - \bar{Y})^2}}$$

**解读：**
- |r| < 0.3：弱相关
- 0.3 ≤ |r| < 0.5：中等相关
- |r| ≥ 0.5：强相关

**参考文献：**
- Pearson K (1896). *Proc R Soc* 60:489-498.

### 5.2 Spearman 秩相关系数

**适用：** 序数数据、非线性但单调关系、非正态数据

**原理：** 对数据进行秩转换后计算 Pearson 相关系数

**参考文献：**
- Spearman C (1904). *Amer J Psych* 15:72-101.

---

## 6. 分类数据分析

### 6.1 卡方检验

**适用：** 分类变量的独立性检验

**要求：** 每个单元格的期望频数 ≥ 5

**参考文献：**
- Pearson K (1900). *Phil Mag* 50:157-175.

### 6.2 Fisher 精确检验

**适用：** 2×2 表，样本量小（期望频数 < 5）

**优点：** 无需近似，精确计算 P 值

**参考文献：**
- Fisher RA (1935). *J Royal Stat Soc* 98:39-54.

---

## 7. 多重比较校正

### 7.1 Bonferroni 校正

$$\alpha_{adjusted} = \frac{\alpha}{m}$$

其中 m 为检验次数。

**优点：** 简单保守
**缺点：** 过于保守，功效损失大

### 7.2 Benjamini-Hochberg (BH) FDR 校正

**原理：** 控制假发现率（False Discovery Rate）

**步骤：**
1. 对所有 p 值排序：p₁ ≤ p₂ ≤ ... ≤ pₘ
2. 找到最大 k 使得 pₖ ≤ k/m × α
3. 拒绝所有 pᵢ (i ≤ k) 的假设

**参考文献：**
- Benjamini Y, Hochberg Y (1995). *J Royal Stat Soc B* 57:289-300.

---

## 8. 功效分析

### 8.1 G*Power

G*Power 是免费的功效分析软件，支持：
- t 检验（单样本、两独立、配对）
- ANOVA（单因素、多因素）
- 相关性
- 回归
- 卡方检验

**下载：** https://www.gpower.hhu.de/

### 8.2 效应量估算

**基于预研究/文献估算：**
- 使用前人研究的效应量作为预期效应
- 考虑样本异质性，适当保守估计

**基于经验法则：**
- Cohen (1988) 的标准：d = 0.5（中等效应）

---

## 9. 重采样方法

### 9.1 Bootstrap

**原理：** 从样本中重复抽样（带放回），构建效应量的经验分布

**用途：**
- 估计置信区间
- 不依赖分布假设

**参考文献：**
- Efron B, Tibshirani RJ (1993). *An Introduction to the Bootstrap*. Chapman & Hall.

### 9.2 置换检验

**原理：** 在零假设下，所有分组都是等价的，因此可以随机置换分组标签

**要求：** 样本量足够大（通常 n ≥ 1000）

**参考文献：**
- Fisher RA (1935). *The Design of Experiments*.
- Edgington ES (1995). *Randomization Tests*. 3rd ed. Dekker.

---

## 10. 回归分析

### 10.1 线性回归

**基本假设：**
1. 线性关系
2. 独立性
3. 同方差性
4. 正态性（残差）

### 10.2 稳健标准误 (Huber-White)

当存在异方差时，使用稳健标准误：
$$\hat{SE}_{robust} = \sqrt{\hat{J} \hat{V} \hat{J}}$$

**参考文献：**
- White H (1980). *Econometrica* 48:817-838.

---

## 11. 特殊领域方法

### 11.1 生物信息学

| 方法 | 用途 | 参考文献 |
|------|------|---------|
| Limma | 微阵列差异表达 | Ritchie ME et al. (2015) *Nucleic Acids Res* |
| DESeq2 | RNA-seq 差异表达 | Love MI et al. (2014) *Genome Biol* |
| GSEA | 基因集富集分析 | Subramanian A et al. (2005) *PNAS* |

### 11.2 临床试验

| 方法 | 用途 | 参考文献 |
|------|------|---------|
| CONSORT | 报告标准 | Schulz KF et al. (2010) *BMJ* |
| Kaplan-Meier | 生存分析 | Kaplan EL, Meier P (1958) *J American Stat Assoc* |
| Cox 回归 | 生存分析 | Cox DR (1972) *J Royal Stat Soc B* |

### 11.3 测量不确定度

| 方法 | 用途 | 参考文献 |
|------|------|---------|
| GUM | 测量不确定度 | JCGM 100:2008 |
| Monte Carlo | 不确定度传播 | JCGM 101:2008 |

---

## 12. 发表偏倚

**问题：** 已发表文献中的效应量存在系统性高估

**参考文献：**
- Turner EH et al. (2008). *NEJM* 358:252-260.
  - 74 个 FDA 审查的临床试验中：所有 36 个阳性结果均发表；36 个阴性结果中只有 3 个明确发表。

**解决方案：**
- 预注册（Pre-registration）
- 阴性结果发表倡议
- 效应量的置信区间
