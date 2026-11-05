# 地动仪模型核心理论参考
## Core Theory Reference for Dizhendongyi-Climate Skill

---

## 目录

§1 米兰科维奇三要素与耦合机制
§2 经典EBM及其局限
§3 分数阶微积分基础
§4 FEBE方程完整推导
§5 多圈层耦合方程组
§6 四大正反馈机制
§7 关键参数说明
§8 适用范围与边界

---

## §1 米兰科维奇三要素与耦合机制

### 1.1 三要素定义

| 要素 | 符号 | 周期 | 物理效应 |
|------|------|------|---------|
| 岁差 | $\psi$ | ~21,700年（主）+~19,000年（次） | 近日点对应季节变化 → 改变季节辐射分配 |
| 倾角 | $\varepsilon$ | ~41,000年 | 地轴倾斜度变化 → 调制高纬辐射量 |
| 偏心率 | $e$ | ~100,000年+~400,000年 | 轨道椭圆程度 → 调制岁差效应强度 |

### 1.2 三要素耦合强迫

**错误（线性叠加）：**
$$F_{\text{orb}}^{\text{错误}} = F_\psi + F_\varepsilon + F_\delta \quad \text{（忽视物理关联）}$$

**正确（乘积耦合）：**
$$F_{\text{orb}}(t) = \underbrace{F_\varepsilon(t)}_{\text{倾角基线}} + \underbrace{e(t)\cdot F_{\text{seas}}(t)}_{\text{核心：偏心率×岁差}} + \underbrace{F_\delta(t)}_{\text{偏心率净效应}} \tag{5}$$

**各分量具体形式：**

$$F_\varepsilon(t) = -\frac{S}{4}\sin\varepsilon(t)\cos\varepsilon(t)\,\Delta\phi \quad \text{（W·m}^{-2}\text{）} \tag{6}$$

$$F_\psi(t) = \frac{S}{4}\,e(t)\,\sin 2\omega(t) \quad \text{（W·m}^{-2}\text{）} \tag{7}$$

$$F_\delta(t) = \frac{S}{4}\,\delta e(t) \quad \text{（约}<0.2\text{ W·m}^{-2}\text{）} \tag{8}$$

### 1.3 对"10万年难题"的解释

**难题**：偏心率对全球年均辐射的直接贡献不足0.2 W·m⁻²，却主导10万年冰期旋回（幅度4–8°C）。

**本模型的解释**：冰期旋回的10万年周期并非来自偏心率的直接驱动，而是来自偏心率对岁差效应的**非线性调制**：

$$F_{\psi\delta}(t) \propto e(t)\cdot\sin 2\omega(t)$$

当 $e\to0$（近圆轨道），$\sin2\omega$ 的效应自动消失；当 $e\approx0.05$（大偏心率），岁差季节辐射差异被放大7%。2.17万年的岁差周期被偏心率"包络调制"，在频谱上呈现准10万年包络——这在数学上对应**次谐波锁频**（subharmonic locking）现象。

### 1.4 周期谱与地质记录对应

| 周期 | 天文来源 | 主导区域 | 典型地质记录 |
|------|---------|---------|------------|
| ~100,000年 | 偏心率（主周期） | 全球（高纬为主） | 深海δ¹⁸O、极地冰芯 |
| ~400,000年 | 偏心率（长周期） | 全球 | 深海碳循环 |
| ~41,000年 | 倾角 | 高纬 | 冰盖体积、北纬65°N夏季辐射 |
| ~23,000年 | 岁差（主谐波） | 低纬 | 东亚季风降水、ITCZ位移 |
| ~19,000年 | 岁差（次谐波） | 低纬-中纬 | 热带沉积物 |

---

## §2 经典EBM及其局限

### 2.1 行星能量平衡方程

$$\frac{dT}{dt} = \frac{1}{C}\left[\frac{S}{4}(1-\alpha) - \sigma\varepsilon T^4\right] \tag{1}$$

### 2.2 线性化（零维EBM）

令 $T=T_0+\Delta T$，$\Delta T\ll T_0$，对 $\sigma\varepsilon T^4$ 做一阶泰勒展开：

$$\frac{d(\Delta T)}{dt} = -\frac{1}{\tau}\,\Delta T + \frac{F_{\text{orb}}(t)}{C},\qquad \tau = \frac{C}{4\sigma\varepsilon T_0^3} \tag{2}$$

**解析解（初条件 $\Delta T(0)=0$）：**

$$\Delta T(t) = \int_0^t \frac{F_{\text{orb}}(t')}{C}\,e^{-(t-t')/\tau}\,dt' \tag{3}$$

→ **单一特征时间 $\tau$，指数衰减**。

### 2.3 经典EBM的根本局限

| 观测 | EBM预测 | 实际记录 |
|------|--------|---------|
| 冰期旋回衰减 | 指数，~10,000年归零 | 幂律，信号持续>100,000年 |
| DO旋回 | 不出现 | 千年尺度反复出现 |
| 深海温度响应 | 单一τ | 多尺度τ叠加 |

→ 真实气候系统存在**宽分布特征时间谱**，须引入分数阶微分方程。

---

## §3 分数阶微积分基础

### 3.1 Caputo分数阶导数（最适合物理初值问题）

$${ }_0^C D_t^{h} f(t) = \frac{1}{\Gamma(1-h)}\int_0^t \frac{f'(t')}{(t-t')^{h}}\,dt', \qquad 0<h<1 \tag{4}$$

**性质：**
- $h=1$：还原为经典一阶导数 $f'(t)$
- $h\to0^+$：还原为 $f(t)-f(0)$（积分算子）
- 初值 $f(0)$ 具有清晰的物理可测量性（初始温度）

### 3.2 Mittag-Leffler函数（分数阶的本征函数）

$$E_{h,1}(z) = \sum_{k=0}^{\infty}\frac{z^k}{\Gamma(hk+1)} \tag{5}$$

**两个极限（记住这两个）：**

| 极限 | 结论 |
|------|------|
| $E_1(z)$ | $=e^z$ —— 经典指数函数 |
| $E_{h,1}(-t^h)\to 0$ 当 $t\to\infty$ | 以幂律 $t^{-h}$ 衰减（永不完全归零） |

### 3.3 分数阶积分（Riemann-Liouville）

$${ }_0 D_t^{-\alpha} f(t) = \frac{1}{\Gamma(\alpha)}\int_0^t \frac{f(t')}{(t-t')^{1-\alpha}}\,dt', \qquad \alpha>0 \tag{6}$$

→ 物理意义：**历史加权和**，$t'$ 时刻的贡献与 $(t-t')^{\alpha-1}$ 成正比，越远的历史权重越低（幂律衰减）。

---

## §4 FEBE方程完整推导

### 4.1 物理出发点

从能量守恒出发：

$$C\frac{d(\Delta T)}{dt} = F_{\text{in}}(t) - F_{\text{out}}(t) \tag{7}$$

关键假设：热流密度 $q(t)$ 与温度梯度之间存在**非局部（分数阶）本构关系**：

$$q(t) = -\kappa\,{ }_0^C D_t^{1-h}\Delta T(t), \qquad 0<h\leq 1 \tag{8}$$

- $h=1$：恢复经典傅里叶定律（局地梯度-通量关系）→ 指数衰减
- $h<1$：热扩散具有记忆性，存在深层海洋等超慢弛豫路径

### 4.2 FEBE方程（核心方程）

联立能量连续性方程与方程 (8)，取垂直方向一维平均并化简：

$$\boxed{{ }_0^C D_t^{h}\,\Delta T(t) = -\frac{\Delta T(t)}{\tau_0} + \frac{F_{\text{orb}}(t)}{C}},\qquad 0<h\leq 1 \tag{9}$$

### 4.3 解析解

对方程 (9) 作 Laplace 变换：

$$\mathcal{L}\{{ }_0^C D_t^h f(t)\}(s) = s^h F(s) - s^{h-1}f(0) \tag{10}$$

初条件 $\Delta T(0)=0$，整理得：

$$s^h\Delta T(s) = -\frac{1}{\tau_0}\Delta T(s) + \frac{F_{\text{orb}}(s)}{C} \tag{11}$$

$$\Delta T(s) = \frac{s^{h-1}}{s^h+\tau_0^{-1}}\cdot\frac{F_{\text{orb}}}{C} \tag{12}$$

逆变换查表或级数展开：

$$\boxed{\Delta T(t) = \frac{\tau_0^{h}}{C}\left[1 - E_{h,1}\left(-\left(\frac{t}{\tau_0}\right)^{h}\right)\right]\cdot F_{\text{orb}}},\qquad 0<h<1 \tag{13}$$

### 4.4 极限行为（为什么FEBE优于EBM）

**短时间（$t\to0$，幂律启动）：**

$$\Delta T(t) \approx \frac{F_{\text{orb}}}{C\,\Gamma(1+h)}\,t^{h} \quad (t\to 0) \tag{14}$$

→ 初始响应与 $t^h$ 成正比（$h<1$ 时增速慢于线性）。

**长时间（$t\to\infty$，超慢收敛）：**

$$\Delta T(t) \approx \frac{\tau_0^{h}F_{\text{orb}}}{C}\left[1 - \frac{1}{\Gamma(1-h)}\left(\frac{\tau_0}{t}\right)^{h}\right] \quad (t\to\infty) \tag{15}$$

→ 温度以幂律 $t^{-h}$ 缓慢趋近平衡，残余信号**永不归零**——这正是冰期旋回"信号持续"的数学表达。

### 4.5 完整预报方程（代入三要素耦合强迫+CO₂强迫）

$$\boxed{{ }_0^C D_t^{h_i}\Delta T_i(t) = -\frac{\Delta T_i(t)}{\tau_i} + \frac{F_\varepsilon(t)+e(t)F_{\text{seas}}(t)+F_\delta(t)+\Delta Q_{\text{CO}_2}(t)}{C_i}} \tag{16}$$

其中 CO₂ 辐射强迫（IPCC近似）：

$$\Delta Q_{\text{CO}_2}(t) = 5.35\ln\frac{C_{\text{CO}_2}(t)}{C_0}\quad \text{（W·m}^{-2}\text{）} \tag{17}$$

---

## §5 多圈层耦合方程组

### 5.1 方程形式

设系统有 $n$ 个圈层组件（大气、混合层海洋、温跃层、深层海洋、冰盖、植被），向量形式为：

$$\boxed{{ }_0^C\mathbf{D}_t^{\mathbf{h}}\,\boldsymbol{\Delta T}(t) = \mathbf{C}^{-1}\left[\mathbf{F}(t) - \mathbf{L}\,\boldsymbol{\Delta T}(t) + \mathbf{G}(\boldsymbol{\Delta T})\right]} \tag{18}$$

### 5.2 各组件典型参数

| 组件 | 记忆指数 $h_i$ | $\tau_i$ | $C_i$（J·m⁻²·K⁻¹） |
|------|-------------|---------|-------------------|
| 大气+混合层海洋 | 0.30–0.50 | $10^2$–$10^3$ yr | $\sim10^8$ |
| 温跃层 | 0.50–0.70 | $10^3$–$10^4$ yr | $\sim10^8$ |
| 深层海洋 | 0.60–0.80 | $10^4$–$10^5$ yr | $\sim10^9$ |
| 大陆冰盖 | 0.70–0.90 | $\sim10^5$ yr | $10^9$–$10^{10}$ |
| 植被（慢反馈） | 0.50–0.70 | $10^3$–$10^4$ yr | 数据稀疏 |

### 5.3 非线性反馈项

$$G_{\text{ice-albedo}}[\Delta T] = \lambda_{\text{ice}}\cdot\frac{\partial\alpha}{\partial T}\cdot\Delta T\cdot\text{ICE}(t) \tag{19a}$$

$$G_{\text{CO}_2}[\Delta T] = \lambda_{\text{CO}_2}\cdot\ln\frac{\text{CO}_2(t)}{\text{CO}_{2,0}} \tag{19b}$$

$$G_{\text{AMOC}}[\Delta T] = \lambda_{\text{AMOC}}\cdot\bigl[\text{AMOC}(t)-\text{AMOC}_0\bigr] \tag{19c}$$

$$G_{\text{veg}}[\Delta T] = \lambda_{\text{veg}}\cdot f_{\text{veg}}(T,P)\cdot\Delta T \tag{19d}$$

---

## §6 四大正反馈机制

| 反馈 | 放大倍数 | 关键方程 | 典型时间尺度 |
|------|---------|---------|------------|
| 冰-反照率 | 2–4× | Eq.(19a) | 千年–万年 |
| CO₂温室 | 3–5°C等效 | Eq.(19b) | 百–千年 |
| AMOC滞后 | ~2°C（8.2ka事件） | Eq.(19c) | 百–千年 |
| 植被-气候 | 空间异质 | Eq.(19d) | 千–万年 |

**系统综合敏感度（放大后的总效应）：**
$$\lambda_{\text{sys}} \approx \frac{4\text{--}8\ \text{K}}{30\text{--}60\ \text{W·m}^{-2}} \approx 0.07\text{--}0.27\ \text{K/(W·m}^{-2}\text{)}$$

---

## §7 关键参数说明

| 参数 | 取值范围 | 校准来源 |
|------|---------|---------|
| $h$ | 0.4–0.9（分组件） | 冰芯季节层（高频）；深海δ¹⁸O旋回（低频） |
| $\tau_0$ | $10^2$–$10^5$ yr | 与米兰科维奇周期匹配 |
| $C$ | $10^8$–$10^{10}$ J·m⁻²·K⁻¹ | 全球能量收支观测 |
| $\lambda_{\text{ice}}$ | 0.3–0.6 | 冰盖模型敏感性实验 |
| $\lambda_{\text{CO}_2}$ | 1.0–1.5 W·m⁻²/ppm | IPCC AR6 |

---

## §8 适用范围与边界

| 适用 | 不适用 |
|------|--------|
| 轨道尺度（10³–10⁵年）气候演变 | 年代际ENSO/NAM等短周期 |
| 冰期-间冰期旋回 | 年代际ENSO预测 |
| 全新世轨道尺度趋势 | 精确10年分辨率预测 |
| 地质记录的周期分析 | 近期天气事件 |
| 碳汇韧性评估 | 精确年际温度预测 |

**临界条件**（超出时方程结构需调整）：
- 辐射强迫变化幅度 > 10 W·m⁻²（需引入非线性项）
- 系统跨越气候临界点（需引入分岔分析）
- 下垫面（陆海分布）发生重大改变

---

## 快速参考：核心方程体系

```
F_orb(t)   = F_ε(t) + e(t)·F_seas(t) + F_δ(t)              [三要素耦合]
F_ε(t)     = -(S/4)sinε·cosε·Δφ                             [倾角强迫]
F_ψ(t)     = (S/4)·e(t)·sin2ω(t)                            [岁差强迫]
ΔQ_CO2     = 5.35·ln(CO2/CO2_0)                              [温室强迫]
{ }_0^C D_t^h ΔT = -ΔT/τ₀ + F_orb/C                         [FEBE核心]
ΔT(t)      = (τ₀^h/C)·[1-E_{h,1}(-(t/τ₀)^h)]·F_orb         [FEBE解]
```
