---
name: math-solver
description: >
  专业数学解题技能。当用户提出以下类型的问题时自动触发：
  【微积分/分析】解方程、极限、导数、微分、积分（定积分/不定积分/反常积分/含参积分）、
  泰勒展开、级数（收敛性/求和）、多元函数（偏导/全微分/重积分/曲线曲面积分）、
  $\varepsilon$-$\delta$ 证明、Fourier/Laplace 变换；
  【线性代数】矩阵运算（乘法/逆/转置）、行列式、特征值/特征向量、
  Jordan 标准形、SVD 分解、Gram-Schmidt 正交化、线性方程组、二次型、
  向量空间与子空间、秩-零化度定理；
  【概率统计】概率分布（PDF/CDF/期望/方差）、条件概率/贝叶斯、
  联合分布/边缘分布、大数定律/中心极限定理、假设检验（t/F/卡方/Z检验）、
  置信区间、最大似然估计、回归分析、方差分析（ANOVA）；
  【微分方程】ODE（可分离/线性/Bernoulli/全微分/高阶常系数）、
  Laplace 变换解初值问题、数值解（RK4）、方向场可视化；
  【数值分析】插值（Lagrange/Newton/样条）、数值积分（梯形/Simpson/Gauss/Romberg）、
  方程求根（Newton/二分/弦截）、数值线性代数（LU/Cholesky/迭代法）、误差分析；
  【优化】无约束/有约束优化、Lagrange 乘数法、KKT 条件、线性规划、整数规划、变分法；
  【其他高级专题】复变函数、留数定理、抽象代数、组合数学、图论、竞赛数学、数学证明；
  关键词触发：「怎么求」「帮我算」「帮我证明」「这道题怎么做」「解方程」「求积分」
  「求导」「特征值」「概率」「统计检验」「微分方程」「数学问题」
  "solve", "integrate", "differentiate", "eigenvalue", "probability", "prove",
  "linear algebra", "differential equation", "optimization", "statistics"
agent_created: true
version: "3.0"
---

# Math Solver — 专业数学解题助手

## 概述

本技能提供**专业级数学解题能力**，覆盖高中至研究生数学全部核心科目。与普通对话相比，本技能的核心优势在于：

| 能力维度 | 普通对话 | 本技能 |
|---------|---------|--------|
| 多步骤推导 | 容易丢中间项 | 完整 LaTeX 逐步推导，关键步骤加注释 |
| 数值验证 | 无验证环节 | 每题都有 SymPy 反代 / 数值回验 |
| 复杂计算 | 手算越界即出错 | 调用 Python 计算引擎（SymPy/NumPy/SciPy）|
| 可视化 | 只描述，不画图 | 生成函数图、分布图、3D曲面、方向场 |
| 证明题 | 结构松散 | 严格形式化证明框架 |
| 误差/收敛分析 | 定性描述 | 精确误差阶、条件数、收敛速度 |

---

## 核心工作流程

```
用户提交数学问题
        │
        ▼
[Step 1] 题型识别与难度分级
  ├── 基础题（高中/大一/概念题）
  ├── 中级题（大学核心课程标准题）
  └── 高级题（综合/证明/数值/优化）
        │
        ▼
[Step 2] 资源与路径决策
  ┌─────────────────────────────────────────────────────┐
  │ A. 纯符号计算    → SymPy 辅助 + 手工推导            │
  │ B. 需数值验证    → scripts/math_helper.py 回验       │
  │ C. 需可视化      → math_helper.py 绘图函数           │
  │ D. 需查公式/定理 → 加载 references/math_formulas.md  │
  │ E. 证明题        → 启用形式化证明模板                │
  │ F. 含参/含积分号 → Leibniz 换序合法性验证 + SymPy    │
  └─────────────────────────────────────────────────────┘
        │
        ▼
[Step 3] 分步解答（详见「解题规范」节）
  - 每步标注使用的定理/方法
  - LaTeX 排版，关键步骤加注释
  - 最终答案用 $$\boxed{...}$$ 框出
        │
        ▼
[Step 4] 验证 & 延伸
  - 数值反代验证（符号结果）
  - 几何/物理直觉说明（若适用）
  - 常见陷阱提示
  - 相关知识点延伸（按需）
```

---

## 解题规范

### 1. LaTeX 输出标准

- **行内公式**：`$...$`
- **独立推导块**：`$$...$$`
- **多步对齐推导**：`\begin{align}...\end{align}`
- **最终答案**：`$$\boxed{...}$$`

示例：
```latex
\begin{align}
  \int_0^1 x^2\,dx &= \left[\frac{x^3}{3}\right]_0^1 \\
                    &= \frac{1}{3} - 0 \\
                    &= \frac{1}{3}
\end{align}
```

### 2. 计算题标准格式

```
**[题型识别]** 这是一道 ___ 类型题，使用 ___ 方法。

**[关键定理/方法]**
- 定理名称：简要表述

**[解题过程]**
Step 1: ...（说明操作目的）
Step 2: ...
...（中间步骤用 LaTeX 展开，不跳步）

**[最终结果]**
$$\boxed{...}$$

**[验证]** 数值代入 / 几何意义 / 特殊值检验...
**[注意事项]** 常见错误 / 条件限制 / 特殊情况...
```

### 3. 证明题标准格式

```
**定理（Theorem）**：[精确数学陈述]

**证明策略**：[直接证明 / 数学归纳 / 反证法 / 构造法 / 夹逼]

**证明（Proof）**：
  (1) [定义与假设建立]
  (2) [核心论证步骤，每步有充分理由]
  ...
  (n) [由 (n-1) 推得结论]
  ∴ [最终结论成立]。$\square$

**注**：[证明思路来源 / 类似命题 / 推广方向（选填）]
```

### 4. 数值分析题标准格式

```
**[算法选择]** 使用 ___ 算法，理由：___

**[误差分析]**
- 截断误差阶：$O(h^k)$
- 条件数：___（若适用）

**[迭代过程]** 表格形式展示前 n 步

**[收敛性]** 理论收敛速度 vs 实测结果对比
```

---

## 科目覆盖与专项能力

### 高等数学（微积分）

**本技能擅长但普通对话容易出错的场景**：

| 题型 | 普通对话局限 | 本技能处理方式 |
|------|------------|--------------|
| 含参积分 $\int_0^1 x^\alpha \ln x\,dx$ | 易漏换序合法性验证 | SymPy 精确计算 + 控制收敛定理验证 |
| $\varepsilon$-$\delta$ 语言证明 | 无法严格量化 $\delta$ | 构造显式 $\delta$ 表达式，逐步验证 |
| 级数一致收敛 | 判别条件混淆 | 逐一适用 M-test / Dini / Abel 定理 |
| 反常积分敛散性 | 比较函数选取不当 | 系统选取，精确量级比较 |
| 含绝对值/分段函数积分 | 分段处理易遗漏奇点 | 精确分析奇点，分段积分求和 |
| 多元极值（带约束） | Lagrange 乘数法计算繁 | 符号解析 + 数值优化双重验证 |
| Wallis 公式推导 | 容易丢系数/递推错 | 归纳法完整证明 + 数值验证 |

### 线性代数

**专项能力**：
- 矩阵完整分析：行列式、秩、逆矩阵、特征值/向量、正定性、条件数、矩阵范数
- SVD 分解及低秩近似（含奇异值物理意义解释）
- Gram-Schmidt 正交化（逐步展示，数值稳定版本）
- 齐次/非齐次线性方程组解空间结构（基础解系完整构造）
- 二次型化标准形（正交变换法 + 配方法 + 合同变换对比）
- Jordan 标准形（含广义特征向量链完整构造，不可对角化情形）
- 矩阵指数 $e^{At}$（Jordan 形法 / Cayley-Hamilton 法）

**调用 `scripts/math_helper.py`**：
```bash
# 矩阵全面分析（特征值/行列式/秩/逆/正定性/条件数）
python scripts/math_helper.py matrix --json '{"matrix_data": [[4,1],[2,3]]}'

# 线性方程组求解（自动判断唯一解/无穷多解/无解）
python scripts/math_helper.py linear_sys --json '{"A_data": [[1,2,3],[4,5,6],[7,8,9]], "b_data": [1,2,3]}'

# Gram-Schmidt 正交化
python scripts/math_helper.py gram_schmidt --json '{"vectors": [[1,1,0],[1,0,1],[0,1,1]]}'
```

### 概率论与数理统计

**专项能力**：
- 任意分布的 PDF/CDF/分位数/期望/方差精确计算
- 联合分布 → 边缘分布 → 条件分布完整推导链
- 贝叶斯后验计算（含先验 → 似然 → 后验更新过程）
- 特征函数/矩母函数法推导分布（正态/泊松/二项的 MGF 推导）
- 假设检验全流程（假设建立 → 检验统计量 → p 值 → 结论 → I类II类错误分析）
- 置信区间精确构造（枢轴量法）
- 最大似然估计（含 Fisher 信息矩阵与 Cramér-Rao 下界）
- ANOVA（单因素 / 双因素方差分析）
- 分布拟合检验（KS 检验、卡方拟合优度检验）

**调用示例**：
```bash
# 分布数值计算（CDF/PDF/分位数/期望/方差）
python scripts/math_helper.py dist --json '{"dist_name":"normal","params":[0,1],"queries":[{"type":"cdf","x":1.96},{"type":"pdf","x":0}]}'

# 贝叶斯更新
python scripts/math_helper.py bayes --json '{"prior":{"A":0.3,"B":0.7},"likelihood_table":{"A":0.9,"B":0.2}}'

# 假设检验（单样本 t 检验）
python scripts/math_helper.py hypo_test --json '{"data":[2.1,1.9,2.3,1.8,2.0],"test_type":"t_one_sample","mu0":2.0}'

# 假设检验（双样本 Welch t 检验）
python scripts/math_helper.py hypo_test --json '{"data":[2.1,1.9,2.3,1.8,2.0],"data2":[2.5,2.3,2.6,2.4,2.7],"test_type":"t_two_sample"}'
```

### 微分方程

**专项能力**：
- 一阶 ODE：可分离变量、线性（积分因子）、Bernoulli 方程、全微分方程、Riccati 方程
- 二阶常系数线性 ODE：特征根法、待定系数法、常数变易法
- Euler-Cauchy 方程
- 高阶线性 ODE（特征方程法）
- Laplace 变换法解初值问题（含阶跃函数、冲激函数）
- 方向场可视化（直观展示解曲线族）
- 数值解法（Euler / Heun / RK4 / 自适应步长，含误差对比）

**调用示例**：
```bash
# 绘制 ODE 方向场
python scripts/math_helper.py plot_ode --expr "x - y" --output "ode_field.png"

# Laplace 变换
python scripts/math_helper.py laplace --expr "t**2 * exp(-3*t)"

# Laplace 逆变换
python scripts/math_helper.py inv_laplace --expr "s / (s**2 + 4)"
```

### 数值分析（高专业壁垒）

这是**普通对话最难处理的领域**，本技能提供完整支持：

- **误差分析**：绝对误差、相对误差、有效数字、误差传播公式（含条件数分析）
- **插值**：Lagrange、Newton 差商（逐差表）、三次样条（含边界条件），给出插值误差估计
- **数值积分**：梯形、Simpson、Gauss-Legendre、Romberg，误差阶精确标注
- **方程求根**：Newton-Raphson（含收敛阶分析）、二分法、弦截法、不动点迭代
- **数值线性代数**：LU / Cholesky / QR 分解，Jacobi / Gauss-Seidel 迭代（含收敛判据）
- **ODE 数值解**：Euler / Heun / RK4 / 自适应步长（含局部截断误差阶对比表）

**调用示例**：
```bash
# 高精度数值积分（含误差估计）
python scripts/math_helper.py num_int --expr "sin(x)/x" --var x --lower 0 --upper "pi"

# Newton 迭代法求根（含收敛过程表）
python scripts/math_helper.py newton --expr "x**3 - 2*x - 5" --point 2

# Lagrange 插值（给出插值多项式表达式）
python scripts/math_helper.py lagrange --json '{"points": [[0,1],[1,2],[2,5],[3,10]]}'
```

### 变换理论

- **Laplace 变换**：正/逆变换，解初值问题，含延迟、卷积、周期函数
- **Fourier 级数**：计算系数（实数型/指数型），Parseval 等式验证，Gibbs 现象说明
- **Fourier 变换**：计算变换对，卷积定理，Plancherel 等式
- **Z 变换**（数字信号处理场景）

**调用示例**：
```bash
# Laplace 变换
python scripts/math_helper.py laplace --expr "t**2 * sin(3*t)"

# Laplace 逆变换（部分分式展开）
python scripts/math_helper.py inv_laplace --expr "s / (s**2 + 4)"
```

### 多元优化（高专业壁垒）

- **无约束优化**：一阶必要条件（KKT简化）、二阶充分条件（Hessian 正定性）、梯度法
- **有约束优化**：Lagrange 乘数法（解析）+ SLSQP / 内点法（数值），KKT 条件验证
- **线性规划**：标准形转化 + 单纯形法（`scipy.optimize.linprog`）
- **凸优化**：凸集/凸函数判断，强/弱对偶性
- **整数规划**（调用 PuLP / CBC 求解器）

**调用示例**：
```bash
# 多元无约束优化（梯度/Hessian + 数值验证）
python scripts/math_helper.py optimize --json '{"expr_str":"(x-2)**2 + (y-3)**2","variables":"x y","x0":[0,0]}'

# 单变量符号极值（含二阶导判断极值类型）
python scripts/math_helper.py sym_opt --expr "x**3 - 3*x + 1" --var x
```

---

## 可视化能力

当用户提到「画图」「看图形」「展示函数」「绘制分布」时自动触发绘图：

```bash
# 单函数 / 多函数对比图
python scripts/math_helper.py plot --expr "sin(x)" --output "plot.png"
python scripts/math_helper.py plot --json '{"expr_list":["sin(x)","cos(x)","sin(x)+cos(x)"],"x_range":[-6.28,6.28],"labels":["sin","cos","sin+cos"],"output":"trig.png"}'

# 概率分布图（PDF + CDF 双图）
python scripts/math_helper.py plot_dist --json '{"dist_name":"normal","params":[0,1],"output":"normal_dist.png"}'

# ODE 方向场（含典型解曲线）
python scripts/math_helper.py plot_ode --json '{"ode_rhs_str":"x - y**2","output":"phase.png"}'

# 3D 曲面图
python scripts/math_helper.py plot_3d --json '{"expr_str":"sin(x)*cos(y)","x_range":[-3.14,3.14],"y_range":[-3.14,3.14],"output":"surface.png"}'
```

---

## 自动资源加载规则

| 触发场景 | 触发条件关键词 | 执行动作 |
|---------|-------------|---------|
| 公式查询 | 「XX公式」「XX定理怎么表述」「什么是XX」 | 加载 `references/math_formulas.md` |
| 数值计算 | 表达式复杂、需验证、用户要绘图 | 运行 `scripts/math_helper.py` |
| 分布计算 | 涉及具体概率分布的数值计算 | `dist` 或 `plot_dist` 命令 |
| 证明题 | 含「证明」「prove」「充分必要」 | 启用形式化证明模板 |
| 误差/精度 | 含「误差」「精度」「收敛阶」「条件数」 | 加载数值分析公式 + `num_int`/`newton` |
| 优化问题 | 含「最优」「极值」「约束」「规划」 | 启用优化解题流程 |
| 微分方程可视化 | 含「方向场」「解曲线」「相图」 | `plot_ode` 命令 |

---

## 高专业壁垒场景示例

以下是本技能专门攻克的**典型高难场景**：

### 场景 1：含参数的定积分（积分号下求导）

**问题**：$\displaystyle\int_0^1 \frac{x^a - x^b}{\ln x}\,dx$

**难点**：需验证积分号下求导的合法性，正确处理 $\ln x$ 在 $x \to 0^+$ 时的奇性。

**本技能处理**：
1. 令 $I(a) = \int_0^1 \frac{x^a}{\ln x}\,dx$，对 $a$ 求导（Leibniz 法则）
2. 验证控制收敛条件（$\left|\frac{x^a}{\ln x}\right| \le x^{c}$ 对充分小的 $c$ 在 $[0,1]$ 可积）
3. $I'(a) = \int_0^1 x^a\,dx = \frac{1}{a+1}$
4. 积分还原：$I(a) = \ln(a+1) + C$，由 $I(0) = 0$ 定 $C = 0$
5. 结论：$\displaystyle\int_0^1\frac{x^a-x^b}{\ln x}\,dx = \ln\frac{b+1}{a+1}$
6. SymPy 数值验证（取 $a=1, b=2$ 对比解析值与数值积分）

### 场景 2：Jordan 标准形（不可对角化矩阵）

**问题**：求矩阵 $A$ 的 Jordan 标准形及相似变换矩阵 $P$

**难点**：需计算广义特征向量链，结构复杂，手算极易出错。

**本技能处理**：
- SymPy 符号计算 Jordan 块结构
- 完整展示广义特征子空间的基构造过程：$\ker(A-\lambda I)^k$ 逐层递进
- 验证 $P^{-1}AP = J$（SymPy 数值反验）

### 场景 3：双样本假设检验 + 效应量 + 功效分析

**问题**：给定两组样本，进行 Welch t 检验，计算 Cohen's d 效应量，给出功效曲线

**难点**：需区分等方差/不等方差，正确使用 Welch–Satterthwaite 自由度，功效分析需解非线性方程。

**本技能处理**：`scipy.stats.ttest_ind(equal_var=False)` + Cohen's d 计算 + 功效曲线绘图

### 场景 4：变分法（Euler-Lagrange 方程）

**问题**：用变分法求最速降线（brachistochrone 问题）

**本技能处理**：
- 推导泛函极值条件 $\frac{\partial F}{\partial y} - \frac{d}{dx}\frac{\partial F}{\partial y'} = 0$
- 带入最速降线 Lagrangian $F = \sqrt{\frac{1 + y'^2}{2gy}}$
- 化简为等周积分，求解摆线参数方程 $x = r(\theta - \sin\theta)$，$y = r(1 - \cos\theta)$

### 场景 5：随机变量函数的分布推导

**问题**：$X \sim N(0,1)$，求 $Y = X^2$ 的 PDF

**难点**：Jacobian 变换需正确处理双支（$X > 0$ 与 $X < 0$），漏支导致结果差 2 倍。

**本技能处理**：
- CDF 求导法：$F_Y(y) = P(X^2 \le y) = P(-\sqrt{y} \le X \le \sqrt{y})$
- 微分后得 $f_Y(y) = \frac{1}{\sqrt{2\pi y}} e^{-y/2}$（$y > 0$）
- 识别为 $\chi^2(1)$ 分布（自由度为 1 的卡方分布）
- 数值验证：蒙特卡洛模拟 vs 理论 PDF

---

## 错误处理与边界情况

| 情况 | 处理方式 |
|------|---------|
| 题目条件不足 | 列出所缺条件，给出最一般情形的解并说明参数意义 |
| 问题无解 | 严格证明无解（矛盾方程组/约束不相容/无极小值），说明原因 |
| 数值不稳定 | 报告矩阵条件数，建议预处理（行列变换 / 缩放 / 正则化）或换算法 |
| 超纲问题 | 说明所需前置知识，给出学习路径与推荐教材 |
| 答案有多种等价形式 | 列出所有等价形式，说明各自在不同场景下的优劣 |
| 脚本执行报错 | 解析错误原因，切换为符号推导手算，给出修正后结果 |
| 题目含笔误/不一致 | 指出疑似笔误的位置，给出「题目原样」和「合理修正后」两种解答 |

---

## 资源文件

| 路径 | 内容 | 何时加载 |
|------|------|---------|
| `scripts/math_helper.py` | Python 计算引擎（SymPy / NumPy / SciPy / Matplotlib） | 需数值计算、可视化、大规模矩阵运算时 |
| `references/math_formulas.md` | 全科公式速查（13 个专题，含复变/数值分析/变换理论） | 查公式、验定理、建立解题框架时 |
| `references/example_calculus.md` | 微积分实操案例（含参积分/级数/多元极值） | 参考解题格式，或用户要求看案例时 |
| `references/example_linalg.md` | 线性代数实操案例（Jordan形/SVD/最小二乘） | 参考矩阵类题目解题格式时 |
| `references/example_stats.md` | 概率统计实操案例（假设检验/贝叶斯/分布推导） | 参考统计类题目解题格式时 |

**Python 命令**：系统使用 `python`（Python 3.9），完整调用格式：`python scripts/math_helper.py <command> <args>`

---

*Skill version: 3.0 — 专业数学解题助手，覆盖大学数学全科目及数值分析、变换理论等高阶领域*
