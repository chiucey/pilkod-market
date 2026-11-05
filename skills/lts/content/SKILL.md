---
name: lts
description: LTS-长线问题解决（LTS — Long Term Solver）。长线问题解决与追踪。当用户提出复杂、跨多步骤、需要持续跟进的问题时触发。适用场景：（1）新长期目标或难题；（2）把大问题拆解成可执行步骤；（3）定期回顾进展；（4）检查某个任务的状态；（5）遇到可拆解提升效率的任务时主动优化。触发词：「先记下来」「需要长期追踪」「长线问题」「定期回顾」「拆解这个问题」「进展如何」「LTS」「LTS-长线问题解决」「帮我建立这个问题」「遇到可以拆解提升效率的任务」。
---

# 长线问题解决 Skill

## 核心原则（必读）

三大原则来自用户制定，详见 `references/workflow-principles.md`：

1. **Plan 模式** — 先列计划 → 拆模块 → 定文件路径 → 验证步骤，再动手
2. **最小闭环** — 每轮只做一个完整闭环，能跑再扩功能
3. **问题排查** — 现象 → 日志 → 定位 → 修复 → 验证，不靠猜测

## Plan 模式（前置，适用于所有任务）

每次开始任何工作前（包括 skill 自我分析），先口述或写出：

```
Plan：
1. 我要做什么
2. 分哪几步
3. 如何验证

→ 不跳步，不脑补，先把计划写清楚再动手
```

---

## 交互流程

触发后按以下顺序处理：

### 第一步：理解问题
不立即创建文件，先向用户确认。

首次触发时，使用 `references/first-use-guide.md` 的三问模板引导用户回答，根据答案生成个性化问题文件。

- **核心目标是什么？** 用一句话复述给用户确认
- **为什么重要？** 理解背景，帮助判断优先级和拆解方向
- **有没有时间/资源限制？** 避免拆解出无法执行的行动

### 第二步：判断是否适用
参见 `references/applicable-scope.md` 判断是否适合用此 skill 追踪。

### 第三步：创建记录
用户确认后，在 `/workspace/memory/problems/` 下创建文件（模板：`references/problem-template.md`）。

### 第四步：Plan 模式拆解
创建文件后，用 Plan 模式给出：
- 计划步骤
- 模块拆解
- 文件路径
- 验证步骤

### 第五步：定时回顾（可选）
如果问题预计跨多周，询问是否需要 cron 定时回顾。详见 `references/cron-review.md`。

## 快速开始

1. 确认问题 → 2. 判断适用性 → 3. 创建记录 → 4. Plan 拆解 → 5. 定时回顾（可选）

## 参考文件

| 文件 | 用途 |
|------|------|
| `references/workflow-principles.md` | 三大原则原文 |
| `references/decomposition-guide.md` | 拆解方法与行动项标准 |
| `references/review-checklist.md` | 回顾三步与状态标签 |
| `references/problem-template.md` | 问题文件 Markdown 模板 |
| `references/applicable-scope.md` | 适用边界与触发条件判断 |
| `references/first-use-guide.md` | 首次使用引导问答模板 |
| `references/cron-review.md` | 定时回顾频率与 cron 配置 |
