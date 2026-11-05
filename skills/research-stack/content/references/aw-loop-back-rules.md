## Loop-Back Decision Rules（什么时候该 loop back，什么时候按假设写）

**核心原则：AW 不创造信息，但也不应该因为信息不确定就停笔。**

---

### 📚 权威依据说明

> ⚠️ 以下 Loop-Back 规则参照了多个权威学术写作规范。AW 在应用这些规则时，**以领域内的具体期刊要求为准**，规范文本仅供参考。
>
> 本节引用的权威来源并非穷举，AW 在执行中以最新版本为准。

#### 主要参考来源

| 来源 | 适用内容 | 引用要点 |
|------|---------|---------|
| **ICMJE** (International Committee of Medical Journal Editors), *Recommendations*, 2025 | 全文本 | 作者责任、COI披露、数据共享声明、统计报告 |
| **EQUATOR Network / CONSORT** (Consolidated Standards of Reporting Trials) | RCT | 方法部分必须包含：样本量计算、随机化方法、盲法 |
| **EQUATOR Network / STROBE** (Strengthening the Reporting of Observational Studies) | 观察性研究 | 方法部分必须包含：分组定义、混杂因素控制、随访 |
| **EQUATOR Network / PRISMA** (Preferred Reporting Items for Systematic Reviews) | 系统评价/Meta分析 | 方法部分必须包含：检索策略、纳入排除标准、偏倚评估 |
| **Lang TA, Secic M.** *How to Report Statistics in Medicine*, 2nd ed. ACP; 2006. | 统计报告 | 效应量必须与CI同时报告；p值不能替代效应量；精确p值 |
| **American Psychological Association.** *Publication Manual of the APA*, 7th ed. APA; 2020. | 心理学/社会科学 | 效应量标注(d/r/η²)；效应量基准；G*Power |
| **Gopen JA, Swan JA.** "The Science of Scientific Writing." *American Scientist*. 1990;78:550-558. | 写作逻辑 | 主题句前置；读者期待引导；逻辑流畅性 |
| **Council of Science Editors / CSE.** *Scientific Style and Format*, 8th ed. SAGE; 2014. | 通用科学写作 | 缩写首次定义；单位格式； reagent ID |
| **Nature** Author Guidelines (nature.com/authors) | Nature 系列期刊 | 方法透明；数据可用性声明；预注册要求 |
| **American Scientist** Statistics Guide (补充规范) | Nature 系列/通用统计 | 效应量+CI 为主，p值作补充；精确 p值；标准化效应量符号 |

---

### 一、决策流程图（核心框架）

```
AW 在写作过程中遇到信息缺口：
         ↓
【问自己一个问题】
"我有足够的信息写出一个诚实、可读的段落吗？"
         ↓
    ┌─ 是，但不确定最佳表达方式 ─┐
    │                               │
    ↓                               ↓
【按合理假设写】              【有明显信息缺口】
 AW 使用标准表述               ① 影响科学准确性？
 标注"[待确认]"               ② 影响叙事连贯性？
 继续推进                      ③ 用户 无法补充？
    │                           │
    │                    任一 YES → 必须 Loop Back
    │                    全部 NO  → 按假设继续写
    ↓
【写完后通知 用户】
 "以下部分我按领域惯例处理，建议补充：[具体]"
```

---

### 二、必须立即 Loop Back（绝对不能假设）

以下情况 AW **无条件 loop back**，不可以用假设绕过：

#### 2.1 数据分析结果（→  loop to DA）

```
引用依据：
  • Lang & Secic (2006): "Effect sizes must always be presented with a
    confidence interval; p-values alone are insufficient."
  • ICMJE (2025): "Authors must report the effect size, precision
    (95% CI), and exact p-value for the primary outcome."

触发条件：
  □ DA 只说"有显著差异"，没有效应量
  □ DA 只说"无显著差异"，没有效应量 CI
  □ 分析方法名称存在但步骤不明确（"我们做了PCA" → 哪种？多少次？）
  □ 样本量 N 不明确
  □ 数据是否预处理（标准化/归一化）未说明

AW → DA 模板：
  "我需要写入 Results 的统计结果：
   1. 具体效应量数值 + 单位（例如：OR=2.3，95%CI: 1.4-3.8）
   2. 精确 p 值（不是 p<0.05）
   3. 分析方法全称 + 关键参数
   4. 样本量 N（每组）"
```

#### 2.2 实验方法描述（→ loop to ED）

```
引用依据：
  • ICMJE (2025): "Methods must contain sufficient detail to allow
    others to reproduce the experiments."
  • CONSORT (2024): 方法部分必须包含随机化、盲法、样本量计算依据
  • STROBE (2007): 观察性研究必须描述分组定义、混杂因素、样本量

触发条件：
  □ 变量没有操作定义（"我们测量了代谢物" → 哪些？用什么平台？）
  □ 关键试剂/设备没有来源（抗体货号、仪器型号）
  □ 实验步骤缺少关键参数（时间/温度/浓度）
  □ 对照组设置描述不完整

AW → ED 模板：
  "Methods 部分需要以下信息才能写完整：
   1. [变量名] 的操作定义：如何测量/获取？
   2. 实验设计的完整描述：包括对照设置
   3. 关键技术参数：[时间/温度/浓度/批次]"
```

#### 2.3 文献支撑（→ loop to LR）

```
触发条件：
  □ 引用某结论但没有文献来源
  □ 引用"已有研究"但未指明是哪个研究
  □ 引用数据（例如"该代谢物在血液中浓度为X"）无文献
  □ "据我们所知，这是首次报告" — 需要 LR 确认

AW → LR 模板：
  "Introduction/Discussion 中引用了以下内容，需要文献支撑：
   [列出具体引用句]
   请提供：作者/年份/期刊，或说明该说法是否可核实"
```

#### 2.4 结论外推（需要与 PR/用户 确认）

```
引用依据：
  • ICMJE (2025): "Authors must distinguish between statistical
    association and causal inference; observational data cannot
    support causal claims without explicit caveats."
  • Gopen & Swan (1990): Scientific writing must guide reader
    expectations; overclaiming violates the writer's contract with the reader.

触发条件：
  □ 从动物结果外推到人类（无明确说明）
  □ 从细胞实验外推到机制（无直接证据）
  □ 统计相关 → 声称因果（无因果设计）
  □ 样本研究 → 声称普适性（无泛化证据）

AW 处理方式（按优先级）：
  1. AW → PR："该结论是否有过度外推？"
  2. PR 确认 → AW 调整表述
  3. PR 无法确认 → AW 通知 用户，用户 拍板

用户 拍板前，AW 的默认处理：
  → 将外推性结论改为保守表述
  → "suggest" 而非 "demonstrate"
  → 明确注明"需要在[具体条件]中进一步验证"
```

---

### 三、按合理假设继续写（无需等待）

以下情况 AW **按领域标准假设继续写**，不需要 loop back：

#### 3.1 变量定义在领域内有共识

```
引用依据：
  • CSE (2014), Scientific Style and Format, 8th ed.: "Standardized
    terminology in a field is preferred; if the author uses a nonstandard
    term, it must be defined at first use."
  • ICMJE (2025): "All abbreviations must be defined at first use in the
    abstract and again at first use in the text."

示例：
  "空腹血糖" → AW 按标准定义写，不标注
  "CRP" → AW 写"C-reactive protein (CRP)"，不标注
  "HPLC" → AW 写"high-performance liquid chromatography (HPLC)"，不标注

操作：
  → 使用标准术语，用户 提供具体细节后替换
  → 如果 用户 提供了具体变量 → 按 用户的写
  → 如果 用户 未提供 → AW 按领域共识写，标注"[变量定义已按领域惯例处理]"
```

#### 3.2 统计格式有惯用惯例

```
引用依据：
  • APA (2020), Publication Manual of the APA, 7th ed.: 效应量必须
    与置信区间同时报告；标准效应量符号（d, r, η², OR, RR）须一致使用
  • Lang & Secic (2006): 精确 p 值而非阈值形式（p=0.034 而非 p<0.05）；
    效应量 + CI + p值三者并列是标准报告格式
  • Nature Author Guidelines: Nature 系列接受效应量+CI 为主要统计量，
    p值作为补充；Nature Communications 使用 American Scientist 统计报告规范

示例：
  效应量格式 → AW 使用领域惯例格式（OR/RR/d/η² 等）
  CI 格式 → AW 使用"(95%CI: X to Y)"格式
  p 值 → AW 报告精确 p 值而非阈值

操作：
  → 按目标期刊的惯常格式写
  → 用户 提供格式要求后调整
  → 目标期刊不明 → 使用 Nature Communications 通用格式
```

#### 3.3 引言逻辑结构

```
AW 已知标准框架：
  大背景 → 已知研究 → 研究空白 → 本研究
  ↓
  按此框架写，用户 提供具体文献后替换
  重要文献缺失 → 标注"[建议补充：关于X的研究]"
```

#### 3.4 用户 未回应的可选信息

```
用户 没有回答 Task Input Spec 中的可选问题：
  → AW 按最优默认处理
  → 在稿件中标注"[建议补充：具体内容]"
  → 不影响主叙事线时，不等待 用户
```

---

### 四、按章节细分的 Loop-Back 边界

#### 4.1 Introduction

```
可按假设写：
  ✓ 领域大背景描述
  ✓ 引言逻辑结构（Gap → 本研究）
  ✓ 用户 提供的文献优先使用

必须 Loop Back：
  ✗ "这是首次报告"（未核实）→ LR 确认
  ✗ 引用具体数字（"X代谢物浓度为Y"）无文献 → LR 核实
  ✗ 用户 未提供核心发现 → 不能写 Introduction！
```

#### 4.2 Methods

```
可按假设写：
  ✓ 通用实验步骤格式
  ✓ 统计方法的惯常描述
  ✓ 领域标准缩写

必须 Loop Back：
  ✗ N（样本量）不明确
  ✗ 关键试剂/设备无来源
  ✗ 分析方法步骤不完整
  ✗ 数据预处理未说明
```

#### 4.3 Results

```
可按假设写：
  ✓ 描述性统计格式（Mean±SD / Median[IQR]）
  ✓ 表格和图的惯常结构

必须 Loop Back：
  ✗ "显著/无显著"但无具体统计量
  ✗ 主要结果效应量为零但无解释
  ✗ 用户 未提供核心发现数据 → 不能写 Results！
```

#### 4.4 Discussion

```
可按假设写：
  ✓ 与已有文献的对比逻辑
  ✓ 机制解释（按 用户 提供的假设）
  ✓ 局限性声明（通用格式）

必须 Loop Back：
  ✗ 机制解释与 DA 提供的数据不符 → AW 不能自行修正差异
  ✗ 用户的叙事重点与结果矛盾 → 必须告知 用户
  ✗ PR 指出的问题在 Discussion 未解决 → 必须处理
```

---

### 五、边界情况判断标准

**以下两种情况的判断方法：**

#### 边界情况 A："我不确定是否需要 loop back"

```
判断标准 — 问自己：
  1. 如果我用假设绕过这个问题，审稿人会发现吗？
     → 会 → 必须 Loop Back
     → 不会 → 进入 2

  2. 这个缺口会影响读者理解全文吗？
     → 会 → 必须 Loop Back
     → 不会 → 进入 3

  3. 用户 可以用一句话回答吗？
     → 可以 → 问 用户，不调用角色
     → 不可以 → Loop Back 到对应角色
```

#### 边界情况 B："DA/ED/LR 给出了部分信息，但不完整"

```
判断标准：
  1. 部分信息能否支撑一个诚实、可读的句子？
     → 能 → 用现有信息写，标注"[具体缺失部分，建议补充]"
     → 不能 → AW → 角色："你提供的[部分]我已使用，以下[缺失部分]仍需补充"
```

---

### 六、Loop-Back 频率管理

```
□ 同一问题 loop back > 2次：
  → PM → 用户："[角色] 对同一问题的回答仍不完整，是否需要你直接提供？"

□ AW 向 3+ 个不同角色同时发起 loop back：
  → PM → 用户："目前写作需要 [N] 个角色的补充信息，是否暂停写作等你提供？"

□ 用户 在 loop back 过程中直接给出答案：
  → AW 直接使用，不再调用相关角色
  → 告知 PM："用户 直接提供答案，已使用，跳过对 [角色] 的调用"

□ 用户 确认某类问题他可以直接回答，不需要走 loop back：
  → AW 记入 用户的直接偏好（下次直接问 用户）
  → 标注来源："用户 直接提供"
```

---

### 七、Loop-Back 通知 PM 的标准格式

```
AW loop back 发生时，同时通知 PM：

通知内容：
  1. [角色] 被调用的原因（1句话）
  2. 具体问题（1-2句话）
  3. 是否影响写作主线：
     - 是（阻塞）：暂停该部分写作
     - 否（非阻塞）：继续，标注"[待补充]"

PM 记录至项目状态：【跨角色调用】表
```

---
