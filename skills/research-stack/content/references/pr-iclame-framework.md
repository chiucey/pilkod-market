## Review Framework (ICLAME)

```
I — Importance: Is the question significant?
C — Clarity: Can you understand exactly what was done?
L — Logic: Does the design actually answer the question?
A — Analysis: Are the stats appropriate?
M — Methods: Are methods sound and reproducible?
E — Evidence: Do the data support the conclusions?
```

---

## Three-Stage Independent Review Process
### （适用于研究论文与基金申请书评审）

> ⚠️ **Foundational Rule: PR must complete Stage 1 before receiving any context from 用户, PM, or AW.**
> This applies to all research papers and grant applications. See Task Input Spec for the enforcement mechanism.

---

### Stage 1 — 独立审读与推理（PR 自主完成）

**PR 在不获取任何背景信息的情况下，独立完成审读与推理。**

```
输入：
  · AW 产出的研究论文或基金申请书（完整文本）
  · PR 自身的领域知识（领域内公认的背景知识，独立于 LR 的文献调研）

工作内容：
  1. 理解研究问题：根据论文内容，判断该研究问题的重要性
  2. 评估方法设计：根据论文描述，评估研究设计的合理性
  3. 逻辑推演结论：从已知前提（领域共识 + 论文数据），严密推导应得结论
  4. 形成独立判断：研究结论是否成立？成立的理由是什么？

输出（Stage 1 Report）：
  · 我（PR）认为该研究的核心结论是什么？（独立得出）
  · 该结论成立的理由（按逻辑链条列出）
  · 该结论不成立的理由（如果我判断不成立）
  · 方法学上最大的潜在问题（独立判断）
  · 结论是否存在过度外推？（独立判断）
```

**PR 在 Stage 1 完成之前，不得读取任何来自 用户、PM、AW 的信息。**

---

### Stage 2 — 背景信息整合（Stage 1 完成后接收）

**PR 在形成独立判断后，接收项目背景信息。**

```
接收来自以下来源的信息：
  · 用户：核心发现描述、项目目标、研究意图
  · PM：项目特化信息（领域、数据类型、研究类型）
  · AW：叙事重点说明、写作意图

工作内容：
  整合背景信息，与 Stage 1 的独立判断进行对照：
  · 我的独立结论与 用户/PM/AW 的描述是否一致？
  · 如果不一致，具体差异在哪里？

输出（Stage 2 Memo）：
  · Stage 1 独立结论（摘要）
  · Stage 2 背景信息整合结果
  · Stage 1 与 Stage 2 的对比分析表
```

---

### Stage 3 — 对比分析与迭代核实

**Stage 3 的核心工作是比较 Stage 1 独立结论与 Stage 2 背景信息，识别差异，并推动解决。**

#### Step 3a：一致性判断

```
IF Stage 1 结论 = Stage 2 背景信息：
  → 判断：研究论文或基金申请书科学严谨、逻辑严密
  → 无需进入 Step 3b，直接输出最终 Review Report

IF Stage 1 结论 ≠ Stage 2 背景信息：
  → 进入 Step 3b：差异分析
```

#### Step 3b：差异分析

```
PR 识别具体差异：

差异类型 A：结论层面
  · PR 独立判断认为结论不成立，但论文声称结论成立
  → 列出支撑"结论不成立"的具体理由

差异类型 B：证据层面
  · 论文数据不足以支撑其声称的结论
  → 指出：数据实际说明了什么，与声称结论的差距在哪里

差异类型 C：逻辑层面
  · 从已知前提无法推导出论文声称的结论
  → 指出：正确的逻辑推导应该是什么

差异类型 D：方法学层面
  · PR 发现的方法学问题，在 Stage 2 背景信息中未被提及
  → 指出该问题及其潜在影响
```

#### Step 3c：驱动核实流程

```
差异确认后，PR → PM：
"Stage 3 发现以下差异：[描述]
需要向相关角色核实：
□ 是否 AW 在写作过程中错误表达了研究发现？
□ 是否 DA 在数据分析中出现了偏差或错误？
□ 是否 ED 在实验设计上存在未披露的缺陷？
□ 是否 LR 在文献调研中存在系统性偏差或遗漏？"

PM 协调核实：
  1. PM → AW："[具体差异]，请核实是否写作过程中存在错误表达？"
  2. PM → DA："[具体差异]，请核实数据分析过程是否存在问题？"
  3. PM → ED："[具体差异]，请核实实验设计是否完整合理？"
  4. PM → LR："[具体差异]，请核实文献综述是否准确覆盖了该方向？"

各角色回复 → PM → PR：
  · 如果问题出在 AW → AW 修正，重新提交 PR 审核
  · 如果问题出在 DA → DA 重新分析，AW 修正文本，PR 重新审核
  · 如果问题出在 ED → ED 补充说明，PR 评估影响
  · 如果问题出在 LR → LR 补充调研，结果交 PR 重新判断
```

#### Step 3d：迭代与关闭

```
核实循环（Step 3c）持续进行，直到：
  ① PR 的所有质疑都得到实质性回应
  ② PR 与 用户/PM 共同确认：剩余分歧为学术判断差异，不可进一步消解

用户 和 PM 总结反馈结果，与 PR 讨论：
  · 最终结论是什么？（经过验证的结论）
  · 该结论与原始研究意图的关系
  · 是否需要修改论文或申请书的核心内容

PR 给出最终立场：
  · 我（PR）接受该结论 / 不接受
  · 理由：……
```

---

### PM 在三阶段中的角色

```
PM 协调 Step 3c 的整个核实流程：
  → 发起各角色核实请求
  → 收集各角色回复
  → 向 PR 汇总反馈
  → 记录每次差异与核实结果

在项目结束或里程碑达成时，PM 总结：
  · PR 共提出 N 个质疑
  · 其中 N 个已解决，问题出在 [角色]
  · [角色] 的 [具体问题] 已修正
  · 剩余 [N] 个学术判断差异，已与 用户 确认

基于以上，PM 驱动 Research Stack Self-Improvement：
  → 如果问题集中在某一角色，PM 提出该角色需要完善的方面
  → 记录至 /workspace/self-improving/domains/research-stack.md
```

---
