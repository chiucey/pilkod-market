---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: bbadebe2704d7df94f7f02135eaf7e97
    PropagateID: bbadebe2704d7df94f7f02135eaf7e97
    ReservedCode1: 3046022100f02c05f940368ebaf2f22e88bfa2711bcfd41f600f9cee1e4fe6b210c8dfa1ff022100861bd7f3b5c9c9901ddd50809d8a70c5c345b703a58c2e5bde0c295c826377c8
    ReservedCode2: 304602210088e4904a98d653425db4231eb481ca4c4f081a7602f179ff14ce88565310904302210096ff8005182b3d071c3d921a4c55c401ca6bc7f6ddfe7c48969877a74b927cca
description: AI行业信号追踪器。当用户需要追踪AI行业变化、监控模型/产品/用户行为/市场趋势、建立被动信息输入系统时使用。触发词：AI行业跟踪、被动订阅、行业信号、AI趋势、信号追踪、模型变化、产品变化、用户行为、市场认知。
name: ai-signal-tracker
---

# AI行业信号追踪器

「低成本、持续、抗遗漏」的AI行业信息输入系统。

核心不是看更多信息，而是**更早发现变化、更稳定追踪趋势、更少陷入信息噪音**。

## Signal类型 vs 平台分类

按Signal类型组织信息源，而非按平台分类：

| Signal类型 | 核心问题 | 优先级 |
|-----------|---------|--------|
| 模型层 | AI突然能做什么 | P1 |
| 产品层 | 产品如何改变创作 | P0 |
| 用户层 | 用户开始怎么使用AI | P0 |
| 市场层 | 行业开始相信什么 | P1 |

**原则**：产品变化 > 用户行为变化 > 模型变化 > 营销传播

---

## 信息收集节奏

### 每日（20-30分钟）

收集新Signal：
1. Twitter/X 产品分享
2. Reddit 用户反馈
3. 官方Blog更新

### 每周（核心）

统一整理四层变化：
- 模型变化
- 产品变化
- workflow变化
- 用户行为变化

### 每月（复盘）

判断长期趋势：
- 哪些Signal重复出现
- 哪些变化开始形成共识

---

## 层级追踪指南

### 模型层（Model Signals）

**重点**：什么能力开始可产品化

关注维度：
- context长度、multimodal能力
- function calling、memory、planning
- video能力、realtime能力

**P0信息源**：
- OpenAI Blog、Anthropic News、Google AI Blog
- DeepSeek、Qwen、MiniMax、Kling

**P1信息源**：
- HuggingFace Trending、LMSYS Arena
- Github Trending（agent、multimodal、video标签）

### 产品层（Product Signals）

**核心问题**：AI开始替代创作链路中的哪一步？

关注维度：
- 输入/输出方式变化
- 是否减少人工步骤
- 是否改变创作顺序

**P0信息源**：
- Twitter/X（创始人、PM、AI power users的workflow分享）
- Reddit（r/ChatGPT、r/LocalLLaMA、r/ArtificialIntelligence）

**P1信息源**：
- YouTube（产品试玩、workflow demo）
- B站/小红书（国内AI创作产品）

### 用户层（Behavior Signals）

**最重要但最容易缺失的一层**

关注维度：
- 新workflow出现（AI自动切shorts、AI生成B-roll、AI辅助脚本）
- 用户开始稳定复用（纳入生产流程）
- 创作者控制权变化（人类主导→AI辅助→AI协同→AI自动执行）

**P0信息源**：
- 真实创作者分享（"我是怎么做的"、"我现在不用XXX了"）
- workflow教程（代表稳定需求）

### 市场层（Narrative Signals）

**关注**：行业开始形成什么共识

关注维度：
- 社区认知变化（如"AI视频已经能商用"）
- 平台方向（大厂开放什么能力、平台扶持什么内容）
- 资本下注方向（投资集中在哪类能力）

---

## 被动订阅原则

1. **收集Signal而非新闻**：不是谁发了公告，而是行业正在发生什么变化
2. **按Signal类型组织**：不同平台承担不同Signal职责
3. **关注用户行为**：用户行为变化才是真正被验证的趋势

---

## 关键原则

真正重要的趋势，从来不是某一天爆发的，而是**同一种变化开始在不同地方反复出现**。

收集目标：不是"知道发生了什么"，而是**长期观察少量关键Signal的持续变化**。

---

## 输出格式

执行信息收集后，按以下格式输出：

```
## AI信号追踪报告 [日期]

### 模型层变化
- [Signal 1]
- [Signal 2]

### 产品层变化
- [Signal 1]
- [Signal 2]

### 用户层变化
- [Signal 1]
- [Signal 2]

### 市场层变化
- [Signal 1]
- [Signal 2]

### 本周关键发现
- [核心变化点]

### 趋势判断
- [正在形成共识的变化]
```

---

## 使用建议

| 场景 | 使用方式 |
|-----|---------|
| 每日信息收集 | 运行此技能，按四层结构快速梳理 |
| 周度趋势整理 | 结合本周所有daily记录，整理趋势 |
| 月度复盘 | 分析Signal重复频率，判断长期趋势 |