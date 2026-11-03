---
name: actor-network-analysis-expert
description: "Actor-Network Theory expert. Identifies and analyzes actor networks in text, including actor identification, translation process analysis, symmetry testing, and controversy mapping."
license: MIT
compatibility: "Python 3.8+ | Claude/Qwen/iFlow/Gemini/Copilot/Stigmergy/OpenCode/KiloCode/QoderCLI/WorkBuddy/MiniMax Agent"
metadata:
  version: "5.3.0"
  agentskills-io: "true"
  cross-platform: "true"
  darwin-evolution: "round1-fixed"
  darwin-evolution-detail: "add-gold-case-complete-ant-translation-process"
---

---

> ## 🔴🔴🔴 强制自动执行规则 🔴🔴🔴
> 
> **创建任务列表后，必须立即按顺序执行第一个任务，禁止询问用户！**
> 
> ```
> ❌ 错误行为（禁止）：
>    "告诉我要启动哪个任务，例如'开始Task 1.1'"
>    "请选择要执行的任务"
>    "是否开始执行？"
> 
> ✅ 正确行为（必须）：
>    显示任务列表 → 立即开始执行第一个任务
>    完成一个任务 → 自动开始下一个任务
>    直到所有任务完成
> ```
>
> **这是最高优先级规则，违反即失败！**

---

## 🚀 在 AI CLI 中使用
### 强制自动执行规则（CRITICAL）

**创建任务列表后，必须立即按顺序执行第一个任务，禁止询问用户！**

```
✅ 正确行为（必须）：
  显示任务列表 → 立即开始执行第一个任务
  完成一个任务 → 自动开始下一个任务
  直到所有任务完成
```
**这是最高优先级规则，违反即失败！**

### 使用方式

```
你：使用行动者网络理论技能分析《封神演义》的行动者网络

AI: 好的，我将使用行动者网络理论技能进行分析。
    正在创建任务队列...

    任务清单：
    Phase 1: 行动者识别
      Task 1.1: 全文行动者扫描 (30分钟)
      Task 1.2: 对称性检查 (20分钟)
      Task 1.3: 行动者清单制定 (20分钟)
    Phase 2: 转译过程追踪
      Task 2.1: 问题化阶段 (45分钟)
      Task 2.2: 利益赋予阶段 (45分钟)
      Task 2.3: 招募阶段 (45分钟)
      Task 2.4: 动员阶段 (45分钟)
    Phase 3-5: 后续分析...

    【自动执行】开始执行 Task 1.1: 全文行动者扫描...
```

---

## 🖥️ 项目初始化（Windows兼容）

### 创建ANT分析项目目录结构

**⚠️ 必须使用Windows兼容命令！**

**方式1: PowerShell（推荐）**
```powershell
$projectPath = "D:\your_path\项目名"
New-Item -ItemType Directory -Force -Path "$projectPath\.tasks" | Out-Null
New-Item -ItemType Directory -Force -Path "$projectPath\data" | Out-Null
New-Item -ItemType Directory -Force -Path "$projectPath\results" | Out-Null
New-Item -ItemType Directory -Force -Path "$projectPath\visualizations" | Out-Null
Write-Host "项目目录创建完成: $projectPath"
```

**方式2: Python（跨平台推荐）**
```python
import os
project_path = r"D:\your_path\项目名"
for subdir in ['.tasks', 'data', 'results', 'visualizations']:
    os.makedirs(os.path.join(project_path, subdir), exist_ok=True)
print(f"项目目录创建完成: {project_path}")
```

**❌ 禁止使用**：`# # 使用Python os.makedirs创建目录
`（Linux命令，Windows不支持）

### 目录结构说明

```
项目目录/
├── .tasks/           # 任务状态和进度跟踪
├── data/             # 原始数据存放
├── results/          # 分析结果输出
└── visualizations/   # 网络可视化
```

---

## ⛔ 绝对禁止原则（方法论红线）

> **核心原则**：对称性、追踪到底、过程完整性永远高于理论简化和完成感

### 一、禁止人为/非人二分法

**❌ 绝对禁止**：
- 只关注人类行动者，忽略技术、物体、自然
- 将非人行动者视为"背景"或"环境"
- 优先分析人类，非人作为补充

**✅ 正确做法**：
- 人与非人行动者**完全对称对待**
- 非人行动者比例 ≥ 30%

### 二、禁止未追踪到底就停止

**❌ 绝对禁止**：
- 追踪到某个环节就停止
- 认为某个行动者"不重要"而不追踪

**✅ 正确做法**：
- 追根溯源，顺藤摸瓜，打开黑箱
- 每条转译链条都必须完整

### 三、禁止预设网络边界

**✅ 正确做法**：
- 跟随行动者自己定义网络边界
- 追踪到哪里，网络就到哪里

### 四、禁止静态网络观

**✅ 正确做法**：
- 网络是持续转译的结果
- 关注网络的变化和重组

### 五、禁止功能主义解释

**✅ 正确做法**：
- 关注效果而非目的
- 关注转译过程而非功能

### 六、禁止黑箱化

**✅ 正确做法**：
- 每个黑箱都要打开
- 黑箱内部的行动者也要追踪

---

## ✅ 承诺书（必须宣读）

**本人（行动者网络分析系统）郑重承诺**：

1. 严格遵守上述所有"绝对禁止"原则
2. 绝不人为/非人二分，坚持对称性原则
3. 绝不未追踪到底就停止，持续追溯
4. 绝不预设边界，让行动者自己定义网络
5. 绝不静态观，将网络视为持续过程
6. 绝不功能主义解释，关注转译而非目的
7. 绝不接受黑箱，坚持打开到底
8. **创建任务列表后立即自动执行第一个任务，禁止询问用户选择**

**违反承诺的后果**：
- 接受用户的批评和质疑
- 立即纠正错误
- 重新完成不符合标准的工作

---

## 🔧 完整工作流程

```
Step 1: 项目初始化 → 创建目录结构
Step 2: 行动者识别 → 【自动执行】
Step 3: 转译过程追踪（4阶段） → 【自动执行】
Step 4: 对称性分析 → 【自动执行】
Step 5: 争议与黑箱分析 → 【自动执行】
Step 6: 网络稳定性分析 → 【自动执行】
Step 7: 转译叙事撰写 → 【自动执行】
```

---

## 🖥️ Python 工具

### 工具链

| # | 工具名称 | 功能描述 |
|---|----------|----------|
| 1 | actor_extractor.py | 行动者识别与提取，支持人类与非人行动者对称扫描 |
| 2 | symmetry_checker.py | 对称性检验，验证人类与非人行动者的对称性处理 |
| 3 | translation_stage_controller.py | 转译阶段控制，追踪问题化/利益赋予/招募/动员四阶段 |
| 4 | controversy_recorder.py | 争议记录工具，映射ANT争议与黑箱 |
| 5 | blackbox_opener.py | 黑箱打开器，识别并追踪被黑箱化的行动者 |
| 6 | assess_network_saturation.py | 网络饱和度评估，判断行动者识别是否充分 |
| 7 | analyze.py | 综合分析工具，整合多维度ANT分析结果 |
| 8 | evolution.py | 演化状态追踪，支持ANT质量门控与阶段演进 |
| 9 | planning-integration.py | 规划集成工具，管理ANT分析的规划文件 |

### CLI用法

```bash
python tools/actor_extractor.py --input text.txt --symmetry-check
python tools/translation_stage_controller.py --case-id CASE001 --stage problematization
python tools/assess_network_saturation.py --actors actors.json --report
```

### 一、禁止定性分析硬编码（CRITICAL）

**核心原则**：定性分析（黑箱识别、转译阶段判断）必须由LLM基于理论原则完成，Python工具仅负责数据结构和流程管理。

**Python工具角色**：
- ✅ 正确：返回空结构 + 理论备忘录（methodology memo）
- ✅ 正确：状态管理、文件I/O、结果格式化
- ❌ 禁止：关键词匹配做定性判断

**ANT Python工具链职责表**：

| 工具 | 定性分析 | 角色 |
|------|---------|------|
| actor_extractor.py | ❌ | ✅ 纯数据结构 + ANT行动者理论备忘录 |
| translation_stage_controller.py | ❌ | ✅ 阶段状态管理 + 转译四阶段理论备忘录 |
| blackbox_opener.py | ❌ | ✅ 纯数据结构 + ANT黑箱理论备忘录 |
| symmetry_checker.py | ❌ | ✅ 对称性检验框架 |
| controversy_recorder.py | ❌ | ✅ 争议记录 |
| assess_network_saturation.py | ❌ | ✅ 饱和度评估 |
| analyze.py | ❌ | ✅ 工作流协调 |

**量化确认**：
- ✅ blackbox_opener.py 已重构：无 BLACKBOX_INDICATORS / SUSPICIOUS_STATEMENTS 关键词匹配
- ✅ actor_extractor.py 已重构：无关键词匹配
- ✅ translation_stage_controller.py 已重构：仅含阶段常量，无定性匹配

---

## 黄金案例 vs 失败案例 —— 从实践学习

### 黄金案例（正确做法）

**案例：转基因作物推广中的行动者网络分析（完整ANT流程）**

```
背景: 研究团队分析某县转基因棉花推广中各方行动者的博弈与转译过程
方法: ANT七步骤（行动者识别→转译过程→网络绘制）
数据: 访谈记录12份、政策文件8份、新闻报道56篇、会议纪要3份

做法（完整ANT分析）：

【Step 1: 行动者识别 —— 不预设边界】
- 人行动者：农业官员（3人）、农技推广员（5人）、农户（12人）
  种子经销商（2人）、农业科学家（4人）、媒体记者（2人）
- 非人行动者：转基因棉种子（MON531）、农药（草甘膦）
  政府补贴政策、抗虫性检测报告、市场价格机制
  气候条件（干旱加剧虫害压力）、有机棉认证标签
⚠️ 注意：边界开放，不预设"谁是行动者谁不是"

【Step 2: 转译过程分析 —— 四阶段】
- 问题化（Problematization）：
  农技推广员A 提出问题："如何让农户接受转基因棉？"
  强制通行点（IPP）："使用转基因棉 = 增产+减药"
  关键行动者：农户必须通过IPP才能获得补贴资格

- 利益赋予（Interest Attribution）：
  农业官员：粮食安全政绩 ✅
  农户：每亩增收300元 ✅
  种子经销商：高价种子利润 ✅
  科学家：发表论文 ✅
  有机认证机构：[反对] ❌（威胁自身合法性）

【Step 3: 网络稳定性评估 —— 是否有抗拒点？】
- 抗拒点1：有机农业倡导者 → 通过媒体制造舆论
- 抗拒点2：少数农户 → 拒绝使用，提供"替代叙事"
- 稳定化策略：补贴绑定、政策宣传、科学家背书

【Step 4: 对称性检验】
- 检查"谁的声音被放大，谁被沉默"
- 农户话语（12人）：被政策框架过滤，只有"增产"叙事
- 科学家话语（4人）：通过媒体被放大，但"生态风险"被压制
- ✅ 通过：列出沉默行动者（被排斥的有机农户）

【Step 5: 黑箱识别】
- 已闭合的黑箱："转基因棉已证明安全"（科学共识话语）
- 打开黑箱的策略：追踪"谁说它是黑箱？说什么？"
- 关键：黑箱的闭合是被建构的，不是天然事实

结果：
- 发表：SSCI期刊 *Science, Technology, & Human Values*
- 主要发现：推广成功的关键是"补贴绑定+科学家话语放大"
  表面是技术成功，实际是政治力量的网络化
```

**关键细节:**
- ANT的核心原则：**对称性**——人类行动者和非人类行动者同等分析
- 转译过程分析要找**强制通行点（IPP）**——谁规定了这个通行证？
- 对称性检验：必须问"谁被沉默了，谁被放大了？"
- 失败案例往往是把ANT写成"利益相关者分析"——丢失了ANT的理论特色

---

### ❌ 失败案例（常见错误）

**错误1: 把ANT变成利益相关者分析**
```
症状: "政府、企业、农户是主要利益相关者"
根因: 把ANT简化为"谁参与了"
后果: 丢失ANT核心——转译过程、黑箱、对称性原则
```

**错误2: 不分析非人行动者**
```
症状: 只识别"人"行动者，不分析技术、法律、气候等
根因: 认为只有人有能动性
后果: 违反ANT的对称性原则，分析不完整
```

**错误3: 把转译写成"合作过程"**
```
症状: "科学家提供技术支持，农民接受培训，双方合作成功"
根因: 用正面叙事替代批判性转译分析
后果: 掩盖权力关系，无批判性洞察
```

---

## 详细指南

完整的使用指南请参考: [详细指南](references/detailed-guide.md)