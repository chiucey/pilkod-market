---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 6aad565fec57e1d6c0e9ea6bb8a8e238
    PropagateID: 6aad565fec57e1d6c0e9ea6bb8a8e238
    ReservedCode1: 3046022100c72785a144e6219766100203010a6ab5bd806a8e7bfb200aacc2d6b44ece9447022100e3776633c3c9320e38cee861011c9b43efa627d65e7d2237075160080bc162e5
    ReservedCode2: 3045022100a0dbb98634635a9c6550c1beba13d05a477ba650f48443c0a04244c7494e8f9902202687a8ab0be0c6c60dd300a74f63cdbee1702d44ea95a353a16a23409d47d02e
description: 特朗普行为模拟预测器。当用户需要预测特朗普（Donald Trump）接下来可能发表的言论、采取的行动、或政策方向时激活。适用场景包括：(1) 追踪特朗普最新动态并做出预测；(2) 分析特朗普对特定事件的可能反应；(3) 模拟特朗普在特定情境下的谈判策略；(4) 预测美国大选相关动向。技能依赖特朗普心理行为画像（references/trump-profile.md）和预测框架（references/prediction-framework.md）作为核心知识库。
name: trump-simulator
---

# Trump Simulator

基于行为心理学、历史行为记录、结构化预测框架，模拟特朗普在给定情境下最可能发表的言论或采取的行动。

---

## 工作流程

### Step 1：获取最新动态（必须）

**主动搜索最近 48 小时内的关键动态**，使用 `batch_web_search` 并行查询：

```
trump latest news today
trump statement today
trump social media truth social recent
trump white house action today
```

获取足够上下文后，再进行预测。

---

### Step 2：情境分析

结合搜索到的最新动态，与以下文件进行模式匹配：
- `references/trump-profile.md` — 查找当前情境触发了哪条行为规律
- `references/prediction-framework.md` — 使用"预测三步法"结构化分析

---

### Step 3：生成结构化预测

使用预测框架的标准化输出格式（见下方），**每次生成 3-5 个预测**，覆盖：

1. **声明型预测**：他可能说什么（主题、基调、用词）
2. **行动型预测**：他可能做什么（政策行动、人事动作）
3. **关系型预测**：他对某特定对象的立场变化

---

### Step 4：输出格式规范

```
## 📊 特朗普行为模拟报告
**模拟时刻**：[当前日期时间]  
**近期背景**：[1-2 句话总结最近关键动态]

---

### 🔮 预测 1：[标题]
- **类型**：声明型 / 行动型 / 关系型
- **置信度**：★★★ / ★★☆ / ★☆☆
- **触发背景**：[当前情境]
- **预测内容**：[具体预测]
- **行为逻辑**：[引用 profile 中的具体模式]
- **时间窗口**：24小时内 / 3天内 / 1周内
- **反向风险**：[预测可能偏差的原因]

---

### 🔮 预测 2：[标题]
[同上结构]

---

## 📋 驱动因素摘要

[基于本次分析，列出影响预测的最关键 3 个变量]
```

---

## ⚠️ 模拟边界说明

- 本技能基于**公开行为记录**进行模式模拟，不代表内幕信息
- 预测具有概率性，高置信不等于必然发生
- 仅供分析研究用途
- 关键决策请结合多方信息源判断
