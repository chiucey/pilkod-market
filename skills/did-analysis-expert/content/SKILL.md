---
name: did-analysis-expert
description: "Difference-in-Differences (DID) analysis expert. Provides parallel trend testing, treatment effect estimation, robustness checks, and heterogeneity analysis. For policy evaluation, causal inference, and quasi-experimental design studies."
license: MIT
compatibility: "Python 3.8+ | Claude/Qwen/iFlow/Gemini/Copilot/Stigmergy/OpenCode/KiloCode/QoderCLI/WorkBuddy/MiniMax Agent"
metadata:
  version: "5.0.0"
  agentskills-io: "true"
  cross-platform: "true"
---

> ## 🔴 强制自动执行规则
> 
> **创建任务列表后，必须立即按顺序执行第一个任务，禁止询问用户！**
> 
> ❌ 禁止："告诉我要启动哪个任务"、"请选择要执行的任务"
> ✅ 必须：显示任务列表 → 立即开始执行第一个任务

# SKILL.md - did-analysis-expert

---
metadata:
  version: "5.1.0-cli-native+agent"
  methodology: "Difference-in-Differences (Angrist & Pischke 2009)"
  absolute-prohibitions: true
  task-decomposition-rules: true
  ai-cli-native: true
  task-queue-support: true
  agentskills-io: true
  cross-platform: true
  state-persistence: true
  academic-alignment: true
  subagent-support: true
  graceful-fallback: true
  created: "2026-03-05"
  updated: "2026-03-14"
  author: "SocienceAI Methodology Expert"
  license: "MIT"

  execution_modes:
    cli_queue: "CLI任务队列（基础）"
    subagent_parallel: "子Agent并行（增强）"

  performance:
    sequential: "20-40分钟/单案例"
    parallel: "30分钟/3案例并行（3x加速）"
---

## 在 AI CLI 中使用

### 方式 1: 在对话中直接使用（推荐）

```
你：使用DID分析技能分析这个政策干预的效果

AI: 好的，我将使用DID分析技能进行分析。
    正在创建任务队列...

    任务清单：
    1. 数据结构验证 (5 分钟)
    2. 平行趋势检验 (15 分钟)
    3. 处理效应计算 (10 分钟)
    4. 稳健性检验 (15 分钟)
    5. 异质性分析 (10 分钟)
    6. DID分析报告 (10 分钟)

    共 6 个任务，预计 65 分钟。开始执行...
```

### 方式 2: 使用 Python 工具

```bash
# 1. 数据验证
python tools/data_validator.py -i data/did_data.csv -o results/validation.json

# 2. 平行趋势检验
python tools/parallel_trends_checker.py -i data/pre_treatment.csv -o results/parallel_trends.json

# 3. 处理效应计算
python tools/treatment_effect_calculator.py -i data/analysis_data.csv -o results/treatment_effect.json

# 4. 稳健性检验
python tools/robustness_tester.py -i results/treatment_effect.json -o results/robustness.json

# 5. 异质性分析
python tools/heterogeneity_analyzer.py -i data/subgroups.csv -o results/heterogeneity.json

# 6. 安慰剂检验
python tools/placebo_test.py -i data/pre_treatment.json --treatment treated --control control --outcome outcome -o results/placebo.json
```

## 基本信息

**名称**: did-analysis-expert (Difference-in-Differences Analysis Expert)
**版本**: 5.0.0-cli-native+agent
**作者**: SocienceAI Methodology Expert
**许可证**: MIT

## 描述


## 🖥️ 项目初始化（跨平台Python脚本）

### 使用Python创建项目目录

```python
import os

# 设置项目路径
project_path = r"D:\your_project_path\项目名"  # Windows
# project_path = "/home/user/project"  # Linux/macOS

# 创建标准目录结构（跨平台兼容）
for subdir in ['.tasks', 'data', 'results', 'visualizations', 'logs']:
    os.makedirs(os.path.join(project_path, subdir), exist_ok=True)

print(f"项目目录创建完成: {project_path}")
```

### 目录结构

```
项目目录/
├── .tasks/           # 任务状态和进度
├── data/             # 原始数据
├── results/          # 分析结果
├── visualizations/   # 可视化
└── logs/             # 日志
```

### ⚠️ 禁止使用
- ❌ `# # 使用Python os.makedirs创建目录
`（Linux命令，Windows不支持）
- ✅ 使用Python的`os.makedirs(path, exist_ok=True)`（跨平台兼容）


**双重差分分析专家** - 支持**复杂任务分解**和**长时任务执行**的因果推断分析技能。

DID (Difference-in-Differences) 通过比较处理组和对照组在政策实施前后的变化差异，识别和估计政策的因果效应。

### 核心能力

1. **数据结构验证**
   - 面板数据完整性检验
   - 处理组/对照组识别
   - 政策前后期数验证

2. **平行趋势检验**
   - 事件研究法
   - 趋势图绘制
   - 统计显著性检验

3. **处理效应计算**
   - 双向固定效应模型
   - 聚类标准误
   - 置信区间估计

4. **稳健性检验**
   - 安慰剂检验
   - 敏感性分析
   - 子群体分析

### 适用场景

- 政策评估研究
- 准实验设计分析
- 面板数据因果推断
- 自然实验分析
- 干预效果评估

## 方法论基础

### DID核心公式

```
DID效应 = (Y_处理组,后 - Y_处理组,前) - (Y_对照组,后 - Y_对照组,前)
```

### 标准回归方程

```
Y_it = α + β(Treated_i × Post_t) + γX_it + μ_i + λ_t + ε_it
```

### 核心假设

1. **平行趋势假设**：处理组和对照组在无干预时有相同趋势
2. **外生性假设**：处理分配与潜在结果无关
3. **SUTVA**：无溢出效应

## 六大绝对禁止原则

### 1. 禁止未检验平行趋势就报告效应

**错误做法**:
```yaml
直接估计DID效应:
  - 忽视平行趋势假设
  - 直接报告因果效应
```

**正确做法**:
```yaml
平行趋势检验优先:
  步骤1: 绘制事前趋势图
  步骤2: 事件研究法检验
  步骤3: 统计检验通过
  步骤4: 才能报告效应
```

### 2. 禁止忽视聚类标准误

**错误做法**:
```yaml
使用普通标准误:
  - 忽视面板数据相关性
  - 导致假阳性结果
```

**正确做法**:
```yaml
聚类稳健标准误:
  - 在单位层面聚类
  - 解决序列相关问题
```

### 3. 禁止忽视溢出效应

**错误做法**:
```yaml
假设无溢出:
  - 不讨论处理组对对照组的影响
  - 忽视SUTVA违反
```

**正确做法**:
```yaml
讨论溢出效应:
  - 评估处理组影响范围
  - 讨论潜在偏误方向
```

### 4. 禁止选择性报告

**错误做法**:
```yaml
选择性报告:
  - 只报告显著结果
  - 隐藏不稳健发现
```

**正确做法**:
```yaml
透明报告:
  - 报告所有预定义分析
  - 包括不显著结果
```

### 5. 禁止过度外推

**错误做法**:
```yaml
过度外推:
  - 将局部因果效应推广到全局
  - 忽视研究情境限制
```

**正确做法**:
```yaml
有限外推:
  - 明确因果效应的适用范围
  - 讨论外部效度限制
```

### 6. 禁止忽视假设限制

**错误做法**:
```yaml
忽视假设:
  - 不讨论识别假设
  - 不报告潜在违反
```

**正确做法**:
```yaml
假设讨论:
  - 逐一讨论核心假设
  - 诚实报告潜在违反
```

## 工具链

| # | 工具名称 | 功能描述 |
|---|----------|----------|
| 1 | analyze.py | 主分析入口，调度各工具 |
| 2 | data_validator.py | 验证 DID 数据结构 |
| 3 | parallel_trends_checker.py | 检验平行趋势假设 |
| 4 | treatment_effect_calculator.py | 计算处理效应 |
| 5 | robustness_tester.py | 鲁棒性检验 |
| 6 | heterogeneity_analyzer.py | 异质性分析 |
| 7 | placebo_test.py | 安慰剂检验 |
| 8 | planning-integration.py | 任务规划集成 |

## 质量保证机制

1. **阶段检查点**：每阶段结束进行质量检查
2. **平行趋势门槛**：未通过平行趋势检验不得报告因果效应
3. **稳健性覆盖**：必须至少执行2种稳健性检验
4. **标准误规范**：必须使用聚类稳健标准误
5. **假设讨论**：必须讨论识别假设的潜在违反

### 一、禁止定性分析硬编码（CRITICAL）

**核心原则**: DID中的平行趋势判断、政策效果解释、异质性分析结论必须由LLM基于方法论原则得出，Python工具仅做数值计算。

**Python工具角色**:
- ✅ `parallel_trends_checker.py`: 计算交互项回归，返回p值，智力判断留给LLM
- ✅ `treatment_effect_calculator.py`: 计算处理效应和标准误
- ✅ `robustness_tester.py`: 执行安慰剂检验、置换检验
- ❌ 禁止：用阈值判断"平行趋势是否成立"

---

## 黄金案例 vs 失败案例 —— 从实践学习

### 黄金案例（正确做法）

**案例：某电商平台"限时折扣"DID分析（完整DID流程+平行趋势检验）**

```
背景: 某电商平台测试"限时折扣"对GMV的影响，在20%门店试点
方法: DID（双重差分）+ 平行趋势检验 + 稳健性检验
数据: 100家门店，60天日销数据（试点前30天+试点后30天）

做法（完整DID分析）：

【Step 1: 平行趋势检验 —— DID前提，不跳过】
检验方法: 预处理期（t=0~29天）交互项回归
模型: Y = α + β1·Time + β2·Treatment + β3·(Time×Treatment) + ε
结果: β3=0.02, SE=0.15, p=0.87
结论: 交互项不显著（p>0.1），处理组和对照组在干预前趋势平行 ✓
→ 可以使用DID估计政策效果

【Step 2: DID主估计 —— 交互项回归】
模型: Y_it = α + β1·Post + β2·Treatment + β3·(Post×Treatment) + ε
结果: β3=15.3, SE=3.2, t=4.8, p<0.001
解释: 控制组间差异和时间趋势后，限时折扣使GMV提升15.3万元/天

【Step 3: 异质性分析 —— 政策效果是否因店而异？】
分组依据: 按历史月均GMV分为高/低流量两组
- 高流量组: β3=22.1, SE=4.1, p<0.001
- 低流量组: β3=8.7, SE=2.9, p=0.003
结论: 高流量门店效果更显著，折扣策略应差异化

【Step 4: 稳健性检验 —— 排除偶然性】
1. 更换对照组: 用邻近门店替代，效应一致（β3=14.8, p<0.001）✓
2. 安慰剂检验: 随机分配处理组，无显著效应（p=0.34）✓
3. 不同时间窗口: 45天/60天/90天，效应一致 ✓
结论: 政策效果稳健，不是偶然

结果:
- 发表：管理学期刊
- 主要发现：限时折扣对高流量门店效果显著（22万/天 vs 8.7万/天）
- 管理建议：资源应优先分配给高流量门店，折扣策略差异化
```

**关键细节:**
- DID的核心前提：**平行趋势**——干预前处理组和对照组趋势必须平行
- 平行趋势检验要用**预处理期数据**，不是全部数据
- 稳健性检验必不可少：安慰剂检验+更换对照组+多时间窗口
- 失败案例是不检验平行趋势就直接做DID——结果可能有偏

---

### ❌ 失败案例（常见错误）

**错误1: 不检验平行趋势就直接做DID**
```
症状: "我们用DID发现政策效果显著（p<0.001）"
根因: 跳过平行趋势检验
后果: 政策效果可能是组间差异而非政策本身，结论有偏
```

**错误2: 把相关当因果**
```
症状: "试点门店GMV提升了15万，所以政策有效"
根因: 没有对照组比较，不知道提升是来自政策还是市场整体
后果: 把混杂因素当成政策效果
```

**错误3: 样本量不足仍做DID**
```
症状: "只有3家门店试点，我们做了DID"
根因: 样本量太小，统计功效不足
后果: 无法区分政策效果和随机波动，置信区间宽到无意义
```

**错误4: 聚类标准误缺失**
```
症状: "处理效应15.3万（p<0.001）"但使用简单标准误
根因: 门店间存在组内相关，不聚类标准误会低估标准误
后果: p值被低估，结论过于乐观
```

---

## 详细指南

完整的使用指南请参考: [详细指南](references/detailed-guide.md)

---

**版本**: 5.0.0-cli-native+agent
**更新日期**: 2026-03-14
**方法论严谨性**: 0%妥协