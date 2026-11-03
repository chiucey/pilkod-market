---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 94aaf4f75c5456c9ecc6078c8072b030
    PropagateID: 94aaf4f75c5456c9ecc6078c8072b030
    ReservedCode1: 30450220011c75613b1a42a0f83e12ba0d2cb861152c047ef54ce98a9f04d4a7316d64d302210080e2ffe574adbd677822a072945ad75b38fb4219a9bff423c467cacf14039806
    ReservedCode2: 3045022100a267c2a0a422c972ddab7ca6878b7636f2dbe13992e90a6bd0b34a91d23ac23c02206061b6fa9d934f800d5a46c86a011066760e67a8253080ad8b6c6657ea070778
description: 足彩十四场全自动分析体系，覆盖27类赛事及差异化赛程研判优先级策略，支持初盘与临盘侧重机构自动匹配及赔率敏感度对比，进球数区间偏差四维背离验证及子母项压力校验。分析体系基于五层决策框架（战意/实力/资本/关系/环境），融合xG/xGA、Elo、H2H、伤停等数据，引入KS检验、加权模型、凯利指数及泊松分布，实现全量数据自动采集和量化推演。系统自动生成结构化分析报告，包含单场详解与整体汇总，并输出风险标记与选场建议。当用户要求分析足球比赛、预测比分、计算赔率偏差、制定投注策略、进行赛事量化分析、或要求分析十四场/任九/九场时使用。
name: football-claude
---

# Football Claude

## 核心能力

### 五层决策框架
1. **战意层** - 联赛/杯赛/友谊赛熵级别评估，保级/争冠/轮换战意量化
2. **实力层** - Dixon-Coles 泊松模型，Elo 锚定评分，xG/xGA 交叉验证
3. **资本层** - 市场赔率共识，Vig 加权，庄家 Tier 分级（Tier-S/A/B/C）
4. **关系层** - H2H 历史对战，裁判执法风格，主场/客场连胜回归
5. **环境层** - 天气/场地/赛程密度/伤病停赛情报

### 数据融合层级

| Level | 来源 | M_data | 说明 |
|-------|------|--------|------|
| L0 | XLSX + FBref xG + CSV | 0.85 | 三源齐全，最高置信度 |
| L1 | CSV 赔率 + 逐场比分 | 1.0 | 标准模式 |
| L1-B | XLSX 逐场比分 + 内嵌赔率 | 1.0 | XLSX 自足模式 |
| L2 | web_search 赛季汇总 | 1.2 | 无逐场数据 |
| L3 | 仅近 5-10 场比分 | 1.5 | 窄窗口，方差×1.5 |

## 分析流程

### Step 0 - 时区与赛事确认
```
完成时区换算 + 赛事确认
赛事不存在 = 硬性拦截 → 输出候选赛事清单
```

### Step 0.5 - 数据摄入层（三路并行）

#### 0.5-A · CSV 赔率表导入
- **触发**: 用户上传 CSV 赔率表
- **结构**: Bookmaker / Start-Last 配对 / 1X2 / Handicap / O/U
- **清洗规则**:
  - 全行 "-" → 剔除
  - 欧赔 1.01~30.00 → 直接用
  - 美式(±或>100) → 转欧赔
  - 概率 0.01~0.99 → Web3（不参与共识线，权重 0.05）

#### 庄家 Tier 分类
| Tier | 代表庄家 | 说明 |
|------|---------|------|
| Tier-S | PinnacleSports, SBOBET | Vig⁻¹ 加权基准线 |
| Tier-A | Bet365, WilliamHill, Ladbrokes, UniBet, BWin, BetFair, Coral, DraftKings, 888Sport | 标准分析 |
| Tier-B | YSB88, DafaBet, 1XBet, MELbet, Marathonbet, FonBet, Mansion, CloudBet, HKJC | 参考级 |
| Tier-C | Polymarket, Kalshi | 不参与共识线 |

#### 0.5-B · 历史数据库摄入（football-data.co.uk XLSX）
- **触发**: 项目中存在 `all-euro-data-2025-2026.xlsx`
- **规模**: 22 个联赛 sheet，共 6487 场比赛

**联赛参数表（含校准参数）:**

| Sheet | 联赛 | 场次 | Ḡ_league | ξ(衰减) | 半衰期 | γ(主场) | PS基准Vig |
|-------|------|------|----------|---------|--------|---------|----------|
| E0 | 英超 Premier League | 309 | 1.365 | 0.0019 | ~365天 | 1.22 | 3.54% |
| E1 | 英冠 Championship | 489 | 1.290 | 0.0019 | ~365天 | 1.21 | 4.86% |
| D1 | 德甲 Bundesliga | 252 | 1.605 | 0.0019 | ~365天 | 1.24 | 3.52% |
| SP1 | 西甲 La Liga | 300 | 1.345 | 0.0019 | ~365天 | 1.32 | 3.53% |
| I1 | 意甲 Serie A | 310 | 1.220 | 0.0019 | ~365天 | 1.12 | 3.51% |
| F1 | 法甲 Ligue 1 | 251 | 1.390 | 0.0019 | ~365天 | 1.28 | 3.53% |
| SC0 | 苏超 Premiership | 192 | 1.345 | 0.0022 | ~315天 | 1.27 | 5.31% |
| N1 | 荷甲 Eredivisie | 261 | 1.595 | 0.0022 | ~315天 | 1.27 | 5.28% |
| P1 | 葡超 Primeira Liga | 250 | 1.365 | 0.0022 | ~315天 | 1.18 | 5.15% |

> 注：Ḡ_league = 联赛场均进球÷2（单侧）；γ 从该赛季 HomeWin%/AwayWin% 校准

#### 0.5-C · FBref xG/PPDA 数据交叉引用
- **触发**: 存在 `team_metrics_template_compact_3_3.csv`
- **用途**:
  - 校验 Dixon-Coles λ/μ 与 FBref xG 偏差 > 20% 触发审查
  - PPDA 数据用于风格冲突检测（高压 vs 低压）
  - NPxGD 验证 ClubElo 排名一致性

#### 队名标准化映射
| football-data | FBref | 常见中文 |
|---------------|-------|---------|
| Man United | Manchester United | 曼联 |
| Man City | Manchester City | 曼城 |
| Nott'm Forest | Nottingham Forest | 诺丁汉森林 |
| Wolves | Wolverhampton Wanderers | 狼队 |
| Spurs | Tottenham | 热刺 |
| Ein Frankfurt | Eintracht Frankfurt | 法兰克福 |
| RB Leipzig | RasenBallsport Leipzig | 莱比锡 |
| Ath Madrid | Atletico Madrid | 马竞 |

### Step 1 - 提出阶段（Proposer Agent）

**1-A 基线实力:**
$$\Delta Elo = Elo_{Home} - Elo_{Away} + HCA$$
（主场联赛 +60~80 / 中立 0）

**1-B 赛制与战意:**

| 赛制 | 熵基础 |
|------|--------|
| 联赛 | 低熵 |
| 杯赛单回合 | 高熵 |
| 杯赛两回合 | 高熵 |
| 友谊赛 | 中熵 |

**1-C 熵级别:**
- **低熵**: 阵容稳定 + 双方有积分需求
- **中熵**: 友谊赛有内驱力 / 杯赛轮换有限
- **高熵**: 战意不明 / 大幅轮换 / 核心未确认

> ⚠️ 高熵触发强制降仓

### Step 2 - 反馈阶段（Feedback Agent）

**2-A 混沌因子（≥3项）:**
- 裁判尺度（该裁判历史执法黄牌/红牌/犯规均值）
- 中轴线轮换预警（GK/CB/CDM 换人触发断崖预警）
- 伤停核心
- 战意不对称
- 场地气候

**2-B 轮换风险:**
| 风险 | 条件 |
|------|------|
| 低 | ≤2人变动 |
| 中 | 3-5人含中轴 |
| 高 | ≥6人或 GK/CDM 替换 |

**2-C PPDA 风格冲突检测:**
当双方 PPDA 差值 > 4.0 时，标注「⚠️ 高压 vs 低压风格冲突 — 比赛节奏可能极端化」

### Step 3 - 分析阶段（Analyst Agent - Dixon-Coles 引擎）

#### 3-A Dixon-Coles 时间衰减引擎
$$P(X=x,Y=y) = \tau_{\lambda,\mu}(x,y) \cdot \frac{e^{-\lambda}\lambda^x}{x!} \cdot \frac{e^{-\mu}\mu^y}{y!}$$

$$\lambda = \alpha_{home} \cdot \beta_{away} \cdot \bar{G}_{league} \cdot \gamma, \quad \mu = \alpha_{away} \cdot \beta_{home} \cdot \bar{G}_{league}$$

**时间衰减:**
$$w_j = e^{-\xi(t_{now}-t_j)}$$

**ρ（低比分修正）联赛校准值:**

| 联赛 | ρ | 依据 |
|------|---|------|
| E0, D1, SP1, I1, F1 | -0.07 | 五大联赛标准值 |
| E1, E2, D2, SP2, I2, F2 | -0.07 | 二级联赛同框架 |
| E3, EC, SC0-SC3 | -0.05 | 低级别联赛进球分布更离散 |
| B1, N1, P1, T1, G1 | -0.06 | 中等联赛 |

**τ 低比分修正:**
$$\tau = \begin{cases} 1-\lambda\mu\rho & (0,0) \\ 1+\lambda\rho & (0,1) \\ 1+\mu\rho & (1,0) \\ 1-\rho & (1,1) \\ 1 & \text{其余} \end{cases}$$

#### 3-B 情境修正层

| 因子 | 对象 | 系数 | 触发条件 |
|------|------|------|----------|
| 保级战意溢价 | λ/μ | ×1.15~1.25 | ±1位±3分≤4轮 |
| 客场连胜≥7均值回归 | μ | ×0.90~0.95 | 客场连胜≥7 |
| H2H连续零封≥4 | λ/μ | ×0.85 | H2H单方≥4场零封 |
| 核心缺席 | λ/μ | ×0.80~0.92 | 进攻核心/中轴停赛伤缺 |
| 新教练首秀 | μ(客) | ×0.80~0.85 | 上任≤7天 |
| 停赛射手王(≥30%队内球) | λ/μ | ×0.80~0.85 | 停赛 |
| 零客场胜≥4场 | μ | ×0.85 | 客场≥4场零胜 |
| 上场净胜≥3球信心溢出 | λ/μ | ×1.10~1.15 | 上轮净胜≥3 |
| 赛制修正(友谊赛) | λ | ×0.90~0.95 | 友谊赛 |

> 安全阈值: $0.65 \leq \prod c_k \leq 1.40$

#### 3-C Gamma-Poisson 后验

先验: $\lambda \sim \text{Gamma}(\alpha_0, \beta_0)$，$\alpha_0 = \bar{G}_{league} \times 5$，$\beta_0 = 5$

后验:
$$\lambda|\text{data} \sim \text{Gamma}(\alpha_0+S_w, \; \beta_0+N_w)$$

$$\hat{\lambda} = \frac{\alpha_0+S_w}{\beta_0+N_w}, \quad \sigma_\lambda = \sqrt{\frac{\alpha_0+S_w}{(\beta_0+N_w)^2}}, \quad CV_\lambda = \sigma_\lambda / \hat{\lambda}$$

**CV_total → φ（仓位系数）:**

| CV_total | φ |
|----------|---|
| <0.10 | 1.00 |
| 0.10~0.18 | 0.80 |
| 0.18~0.25 | 0.60 |
| ≥0.25 | 0.40 |

#### 3-D SOT Ratio Gate (Rule Patch #10)

**触发条件:**
- 某队近 5 场射正率 (HST/HS 或 AST/AS) < 25% 或 > 55%（极端偏差）
- 且 Dixon-Coles λ/μ 与实际场均进球偏差 > 30%

**效果:**
- 射正率 < 25%（低效）: λ/μ ×0.90~0.95
- 射正率 > 55%（超高效）: λ/μ ×1.05~1.10

### Step 4 - 验证阶段（Verifier Agent）

#### 4-A 赔率采集（优先级）

**未来比赛:**
1. ✅ CSV 上传（实时赔率）
2. 🔄 web_search 兜底

**复盘分析:**
- ✅ XLSX 收盘赔率（`*C*` 列）

#### 4-B Vig 计算与加权共识线

$$Vig_i = \left(\frac{1}{d_1}+\frac{1}{d_X}+\frac{1}{d_2}-1\right)\times100\%$$

去 Vig 公正概率:
$$P_{fair,k,i} = \frac{1/d_{k,i}}{\sum_k 1/d_{k,i}}$$

Vig⁻¹ 加权共识线:
$$\bar{P}_k = \frac{\sum w_i P_{fair,k,i}}{\sum w_i}, \quad w_i = 1/Vig_i$$

| Vig | 信号 |
|-----|------|
| <3.5% | ✅ 透明 |
| 3.5~5.5% | ✅ 正常 |
| 5.5~7% | ⚠️ 轻度避险 |
| >7% | 🚨 强制降仓/No Bet |
| >10% | ⛔ 强制 No Bet |

#### 4-C 泊松-市场偏差

$$\Delta_k = P_{Poisson,k} - \bar{P}_{weighted,k}$$

动态阈值:
$$\theta_k = 3.0\% \times M_{entropy} \times M_{data}$$

| M_entropy | M_data |
|-----------|--------|
| 低熵×1.0 / 中熵×1.5 / 高熵×2.0 | L0×0.85 / L1×1.0 / L1-B×1.0 / L2×1.2 / L3×1.5 |

#### 4-D 漂移矩阵

**4-D.1 单庄变化率:**
$$\Delta_{k,i} = (Odds_{Last} - Odds_{Start})/Odds_{Start} \times 100\%$$

**4-D.2 DCI（庄家共识指数）:**

| DCI | 信号 |
|-----|------|
| >85% | 🔴 强 |
| 70-85% | 🟡 中 |
| 50-70% | ⚪ 弱 |
| <50% | 🔵 分裂 |

**4-D.3 SLD（锐利线变化）:**
$$SLD_k = (\Delta_{Pin} + \Delta_{SBOBET})/2$$

| SLD | 信号 |
|-----|------|
| <1% | ⚪ |
| 1-3% | 🟡 |
| ≥3% | 🔴 |

**4-D.7 SLMO（双锐利庄盘面同步迁移覆盖）:**
触发条件（三项同时）:
- Pinnacle + SBOBET 同一市场盘面变更
- 方向一致
- 与泊松偏差方向矛盾

→ 标注「⛔ SLMO 触发」，受影响盘口降级 Observe Only（≤0.25U）

**4-D.8 RDSD（散户驱动缩短识别）:**
触发:
- 某盘口 DCI 缩短>70%
- SLD<2%（锐利庄不动）
- Tier-B 庄缩短>5%

→ 标注「🏷️ RDSD — 散户驱动」，反向盘口 +1 信号增强点

**4-D.9 RDSD-SSG（散户同向防御）:**
触发:
- 首选方案方向与 DCI 缩短方向一致
- SLD < 2%
- Tier-B 庄在该方向缩短 > 5%

| 条件 | R |
|------|---|
| SLD < 2% 且方向中性 | 0.50 |
| SLD 轻微反向 | 0.35 |

#### 4-E 跨市场一致性校验

1X2↔AH 剪刀差:
$$Scissors = P(1)_{AH} - P(1)_{1X2}$$

| Scissors | 信号 |
|----------|------|
| <2% | 一致 |
| 2-5% | 轻微分歧 |
| ≥5% | 显著分歧 |

### Step 5 - 总结阶段（Summarizer Agent）

#### 【1】赛制战意与高熵预警
赛制+熵级别 / 双方战意（驱动+强度）/ 2-3 个关键混沌因子

#### 【2】偏差信号解读
判断规则:
- 超额>3% + Tier1 → 强价值优先建仓
- 超额>3% + Tier2/3 → 条件价值需交叉验证
- 超额0-3% → 微弱价值仅低熵考虑
- RDSD 增强 → 未过阈但差额<1% → 纳入候选池（0.5U 上限）

#### 【3】W.A.M. 加权评定

| 维度 | 权重 |
|------|------|
| ClubElo-泊松数学概率 | 0.35 |
| 赛事性质与战意 | 0.20 |
| 市场微结构(Vig/共识线) | 0.20 |
| 赔率偏差+漂移信号 | 0.15 |
| 混沌因子 | 0.10 |

#### 【4】数据核验（The Tale of the Tape）
```
📊 数据来源核验：
├─ 逐场比分：✅ XLSX L1-B / ⚠️ web_search L2
├─ FBref xG/PPDA：✅ 模板命中 / ❌ 未覆盖
├─ 赔率来源：✅ CSV L1 / ✅ XLSX 收盘 / ⚠️ web_search L2
├─ 射门统计：✅ XLSX 可用 / ❌ 不可用
├─ 裁判数据：✅ XLSX Referee / ❌ 不可用
└─ 综合数据级别：L0 / L1 / L1-B / L2 / L3
```

#### 【5】冷门暴露评估（Rule Patch #9）

$$P_{upset} = 1 - P_{favorite}$$

| 条件 | U | 附加 |
|------|---|------|
| P(upset) ≤ 35% 且站热门侧 | 1.00 | ✅ 正常执行 |
| P(upset) 36-45% 且站热门侧 | 1.00 | ⚠️ 冷门警示，建议不叠加多盘口 |
| P(upset) > 45% 且站热门侧 | 0.75 | 🔴 开放赛局 |
| 站冷门侧（打冷） | 1.00 | 需超额>5%方可全仓 |

#### 【6】交易计划

**仓位公式:**
$$Position_k = Unit_{cap} \times TierMult_k \times \phi \times D \times \min(R, D_{existing}) \times U$$

| 组件 | 来源 |
|------|------|
| Unit_cap | 低熵 2.0 / 中熵 1.0 / 高熵 0.5 / 高熵+Vig>7% = NoBet |
| TierMult | T1×1.0 / T2×0.75 / T3×0.50 |
| φ | CV<0.10→1.0 / 0.10-0.18→0.8 / 0.18-0.25→0.6 / ≥0.25→0.4 |
| D | 泊松与漂移同向→1.0 / 矛盾→0.5 |
| R | RDSD-SSG 触发→0.50/0.35 |
| U | 冷门门控系数 |

**输出格式:**
```
冷门暴露: P(upset) = XX.X% | 首选方向: [热门侧/冷门侧] | 门控系数 U = X.XX
[若 RDSD-SSG 触发] RDSD-SSG: 散户同向检测 | R = X.XX

首选方案：[盘口] @ [赔率]（建议仓位：X Unit）
  逻辑锚点：[战意+偏差超额+Vig+Tier+漂移验证]
  参数置信度：CV=X.XX → φ=X.XX | λ* 95%CI [X.XX, X.XX] | μ* 95%CI [X.XX, X.XX]
  仓位推导：Unit_cap(X) × TierMult(X) × φ(X) × D(X) × R(X) × U(X) = X.XX Unit

次选方案（如有）：同上格式

避险警示（Avoid）：
  → [盘口]：[负偏差数据+陷阱理由]

观察区（SLMO 覆盖触发时）：
  → [盘口]：泊松 Δ+X.X%，但双锐利庄盘面迁移矛盾，降级观察。如执行上限 0.25U。
```

## 全局强制规则

1. **LaTeX 公式强制**: 所有概率/Vig/偏差计算须 LaTeX 展示推导
2. **严禁捏造**: xG/PPDA 禁止凭空估算，诚实标注数据级别
3. **时区先行**: Step 0 完成时区换算+赛事确认后方可启动
4. **赛事不存在=硬性拦截**: 输出候选赛事清单
5. **赔率来源透明**: 标注层级与时效
6. **三不明→No Bet**: 战意不明+伤停不明+阵容未公布 → No Bet
7. **专业简洁量化**: 结论须有数据锚点
8. **偏差表无解读**: 信号判断统一在 Step 5【2】
9. **CSV = Level 1**: M_data=1.0
10. **Dixon-Coles 参数显式展示**: α,β,γ,ρ 推导不得省略
11. **修正不重复**: 历史比分→Dixon-Coles 已吸收；赛前新闻→手动修正
12. **φ 不可覆盖**: 方差降仓不可手动覆盖
13. **R 与 D 取严格者**: RDSD-SSG 与漂移矛盾系数不叠加
14. **U 与 Unit_cap 叠加**: 冷门门控与熵级别仓位叠加
15. **交易计划以冷门暴露开头**: Step 5【6】强制格式
16. **XLSX 优先级**: 当数据库可用且包含目标联赛时，Step 3 必须从 XLSX 提取
17. **收盘 vs 当前区分**: `*C*` 列为收盘赔率用于复盘；未来比赛用 CSV 或 web_search
18. **联赛参数不可手动覆盖**: Ḡ_league / ξ / γ 从参数表读取
19. **队名归一化在 Step 0.5 完成**: 进入 Step 1 前必须已匹配
20. **SOT Ratio Gate 独立**: Patch #10 是后置校验，不修改 Dixon-Coles 核心参数

## 使用示例

### 基础分析
```
用户: 分析 曼城 vs 曼联
助手: [执行 Step 0-5 完整流程]
```

### 带 CSV 赔率
```
用户: 分析 巴萨 vs 皇马，附上赔率.csv
助手: [CSV 导入 → L1 模式 → 完整分析]
```

### 复盘模式
```
用户: 复盘 切尔西 vs 阿森纳 (2024-12-15)
助手: [XLSX 收盘赔率 → L1-B 复盘模式]
```

### 批量十四场
```
用户: 分析第XX期十四场
助手: [批量分析 → 汇总报告 → 选场建议]
```
