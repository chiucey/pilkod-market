# 领域特化适配指南

本文档为 Comprehensive Data Analyst 提供各实证科学领域的具体适配内容。

---

## 通用适配规则

当研究者提供领域上下文时，DA 自动进行以下适配：

1. **示例和术语**：使用领域特定的示例
2. **统计默认值**：使用领域公认的方法
3. **报告标准**：遵循领域特定的报告规范
4. **基准和效应量**：使用领域已知的参考值

---

## 1. 生物学 / 生物化学

### 典型数据特征
- 高维度数据（基因组、转录组、蛋白组、代谢组）
- 技术性变异（批次效应）
- 多重检验问题

### 统计方法适配

| 分析目标 | 推荐方法 | 特殊考虑 |
|---------|---------|---------|
| 差异表达 | Limma-voom / DESeq2 | 需 FDR 校正 |
| 通路富集 | GSEA / Fisher 精确检验 | 多重检验校正 |
| 批量校正 | ComBat / limma removeBatchEffect | 记录校正方法 |
| 可视化 | Volcano plot / Heatmap / QQ-plot | 展示校正后 P 值 |

### 效应量指标
- **Fold Change (FC)**: 基因表达变化的倍数
  - 通常使用 |log₂FC| > 1（约 2 倍变化）作为阈值
- **Q-value**: FDR 校正后的 P 值

### 报告标准
- **MIAME** (Minimum Information About a Microarray Experiment)
- 可视化需包含 QQ-plot 评估整体分布

### 参考文献
- Ritchie ME et al. (2015). *Nucleic Acids Research* 43:e47.
- Love MI et al. (2014). *Genome Biology* 15:550.
- Brazma A et al. (2001). *Nature Genetics* 29:365-371.

---

## 2. 医学 / 临床试验

### 典型数据特征
- 随机对照试验（RCT）或观察性研究
- 二分类或生存结局
- 需考虑意向治疗分析

### 统计方法适配

| 分析目标 | 推荐方法 | 特殊考虑 |
|---------|---------|---------|
| 二分类结局 | Chi-square / Fisher / Logistic 回归 | OR/RR + NNT |
| 生存分析 | Kaplan-Meier / Log-rank / Cox 回归 | HR + 95% CI |
| 非劣效性 | 非劣效性检验 | 预设边界 |
| 协变量校正 | 多因素回归 | 记录所有变量 |

### 效应量指标
- **Odds Ratio (OR)**: 优势比
- **Relative Risk (RR)**: 相对危险度
- **Absolute Risk Reduction (ARR)**: 绝对风险降低
- **Number Needed to Treat (NNT)**: 需治疗人数 = 1/ARR

### 报告标准
- **CONSORT** (Consolidated Standards of Reporting Trials)
- **STROBE** (观察性研究)

### 解读指南
```
OR = 2.0 的解读：
"处理组的优势是对照组的 2 倍"
（即事件发生的几率是 2 倍）

⚠️ OR ≠ RR（当结局不罕见时，OR 会高估 RR）
```

### 参考文献
- Schulz KF et al. (2010). *BMJ* 340:c332.
- Vandenbroucke JP et al. (2007). *PLoS Med* 4:e297.
- Cox DR (1972). *J Royal Stat Soc B* 34:187-220.

---

## 3. 化学 / 分析化学

### 典型数据特征
- 测量值（浓度、纯度）
- 需报告测量不确定度
- 仪器精度和重复性

### 统计方法适配

| 分析目标 | 推荐方法 | 特殊考虑 |
|---------|---------|---------|
| 测量不确定度 | GUM 方法 | 传播不确定度 |
| 检测限/定量限 | LOD/LOQ | IUPAC 定义 |
| 方法验证 | 重复性/再现性 | Horwitz 函数 |
| 批次间变异 | ANOVA | 分层设计 |

### 关键概念

**测量不确定度 (GUM)：**
$$u_c(y) = \sqrt{\sum_{i=1}^{N} c_i^2 u(x_i)^2}$$

其中 cᵢ 为灵敏系数，u(xᵢ) 为输入量的标准不确定度。

**检测限 (LOD)：**
$$LOD = \frac{3.3 \sigma}{S}$$

其中 σ 为空白标准差，S 为标准曲线斜率。

**定量限 (LOQ)：**
$$LOQ = \frac{10 \sigma}{S}$$

### 报告标准
- **IUPAC** 指南
- 结果报告格式：[值 ± 扩展不确定度] 单位

### 参考文献
- JCGM 100:2008. *Evaluation of measurement data — Guide to the expression of uncertainty in measurement*.
- Horwitz W (1982). *Analytical Chemistry* 54:67A-76A.

---

## 4. 物理学 / 工程学

### 典型数据特征
- 精确测量
- 误差传播
- 仪器校准

### 统计方法适配

| 分析目标 | 推荐方法 | 特殊考虑 |
|---------|---------|---------|
| 误差传播 | 蒙特卡洛模拟 | 非线性传播 |
| 最小二乘拟合 | χ² 最小化 | 权重回归 |
| 仪器校准 | 标准曲线 | 报告不确定度 |
| 重复性/再现性 | Gage R&R | 分量分解 |

### 关键公式

**线性误差传播：**
$$u_c(y) = \sqrt{\left(\frac{\partial f}{\partial x_1} u(x_1)\right)^2 + ...}$$

**加权回归：**
$$\chi^2 = \sum \frac{(y_i - f(x_i))^2}{\sigma_i^2}$$

### 参考文献
- Taylor JR (1997). *An Introduction to Error Analysis*. 2nd ed. University Science Books.
- Bevington PR, Robinson DK (2003). *Data Reduction and Error Analysis*. 3rd ed. McGraw-Hill.

---

## 5. 心理学 / 社会科学

### 典型数据特征
- 问卷/量表数据
- 潜在变量
- 多层次嵌套结构

### 统计方法适配

| 分析目标 | 推荐方法 | 特殊考虑 |
|---------|---------|---------|
| 量表信度 | Cronbach's α | α ≥ 0.7 |
| 效度检验 | 验证性因子分析 (CFA) | 拟合指数 |
| 重复测量 | 多层线性模型 (HLM) | 随机效应 |
| 效应量基准 | 领域特定 Cohen's d | 社会心理学 d=0.4 典型 |

### 领域特定的效应量基准

| 子领域 | 小效应 | 中效应 | 大效应 |
|--------|--------|--------|--------|
| 社会心理学 | d ≈ 0.3 | d ≈ 0.5 | d ≈ 0.8 |
| 认知心理学 | d ≈ 0.2 | d ≈ 0.4 | d ≈ 0.6 |
| 临床心理学 | d ≈ 0.3 | d ≈ 0.6 | d ≈ 1.0 |

### 功效分析
- 使用 **G*Power** 进行先验功效分析
- 典型 α = 0.05，功效 = 0.80

### 报告标准
- **APA** 第七版格式
- 效应量 + 置信区间 + P 值三者必须同时报告

### 参考文献
- Cohen J (1988). *Statistical Power Analysis for the Behavioral Sciences*. 2nd ed. Erlbaum.
- Faul F et al. (2009). *Behavioral Research Methods* 41:1149-1160. (G*Power)
- Cronbach LJ (1951). *Psychometrika* 16:297-334.

---

## 6. 经济学 / 计量经济学

### 典型数据特征
- 时间序列或面板数据
- 内生性问题
- 异方差普遍

### 统计方法适配

| 分析目标 | 推荐方法 | 特殊考虑 |
|---------|---------|---------|
| 异方差稳健推断 | Huber-White 稳健 SE | Newey-West |
| 内生性 | 工具变量 (IV) | 2SLS |
| 因果推断 | 倍分法 (DID) | 平行趋势检验 |
| 时间序列 | ARIMA / VAR | 单位根检验 |

### 关键概念

**倍分法 (Difference-in-Differences):**
$$Y_{it} = \alpha + \beta_1 Post_t + \beta_2 Treatment_i + \beta_3 (Post_t \times Treatment_i) + \epsilon_{it}$$

β₃ 为双重差分估计量。

**工具变量法 (2SLS):**
- 第一阶段：Z → X
- 第二阶段：X̂ → Y

### 参考文献
- Wooldridge JM (2010). *Econometric Analysis of Cross Section and Panel Data*. 2nd ed. MIT Press.
- Angrist JD, Pischke JS (2009). *Mostly Harmless Econometrics*. Princeton University Press.
- Cameron AC, Trivedi PK (2005). *Microeconometrics*. Cambridge University Press.

---

## 7. 生态学 / 环境科学

### 典型数据特征
- 空间自相关
- 生态学设计
- 过度离散

### 统计方法适配

| 分析目标 | 推荐方法 | 特殊考虑 |
|---------|---------|---------|
| 计数数据 | 泊松/负二项回归 | 考虑过度离散 |
| 空间相关 | 空间自回归模型 | Moran's I |
| 多样性分析 | 广义线性混合模型 | 随机效应 |
| 物种分布 | MaxEnt / GAM | 模型验证 |

### 参考文献
- Zuur AF et al. (2009). *Mixed Effects Models and Extensions in Ecology with R*. Springer.
- Legendre P, Legendre L (2012). *Numerical Ecology*. 3rd ed. Elsevier.

---

## 8. 机器学习与数据科学

### 典型数据特征
- 大样本
- 高维度
- 预测为主

### 统计方法适配

| 分析目标 | 推荐方法 | 特殊考虑 |
|---------|---------|---------|
| 模型评估 | 交叉验证 | 留出法/LOOCV |
| 性能度量 | AUC-ROC / F1 | 类别不平衡 |
| 特征选择 | LASSO / Elastic Net | 正则化 |
| 不确定性量化 | 贝叶斯方法 | 后验分布 |

### 模型验证
- **训练/验证/测试集划分**
- **K 折交叉验证**
- **留一法 (LOOCV)** 适用于小样本

### 参考文献
- Hastie T et al. (2009). *The Elements of Statistical Learning*. 2nd ed. Springer.
- James G et al. (2013). *An Introduction to Statistical Learning*. Springer.

---

## 适配触发机制

当研究者描述研究领域时，DA 应：

1. **识别领域关键词**：生物学、医学、化学、物理、心理、经济等
2. **激活对应模块**：根据上表加载领域特定内容
3. **调整示例和术语**：使用领域内常用的表达方式
4. **提供领域特定基准**：使用领域公认的标准进行比较

**示例触发：**
- "我在做 RNA-seq 分析" → 激活生物学模块
- "这是一个随机对照试验" → 激活医学/临床模块
- "我想检验干预效果" → 检查是否需要 CONSORT 标准
