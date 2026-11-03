# Human-Like Memory Optimization
更新时间：2026-03-26

## 1. 先区分三件事

很多 Agent 方案把这三件事混在一起：

- 存在哪里
- 怎么理解
- 为什么触发行为

如果不拆开，就会出现"写了很多记忆，但还是像没记住"。

## 2. 更适合 OpenClaw 的三条轴

### A. 表征轴：记忆存在哪里

这是存储结构，不是价值本身。

- Working
- Episodic
- Semantic
- Procedural
- Retrieval / Index

这条轴回答：
- 信息被放在哪一层
- 每层生命周期是什么
- 哪层是 canonical source

### B. 加工轴：记忆怎么变化

这是更接近人类记忆的部分。

- Capture
- Retain
- Recall
- Reflect
- Reconsolidate
- Forget

这条轴回答：
- 哪些事件会被记住
- 哪些会被抽象成模式
- 旧记忆如何被新证据改写
- 什么应该被遗忘

### C. 价值轴：记忆为什么值得存在

这是"记忆有没有用"的判断层。

- goal impact
- behavior change
- reuse frequency
- emotional salience
- confidence
- reversibility risk

这条轴回答：
- 记住它以后，系统行为会不会更好
- 如果删掉它，性能会不会下降
- 它只是历史，还是会改变后续决策

## 3. 准确的理解

更准确的说法是：
- 数据 / 事件是原材料
- 语义 / 模式是压缩后的长期知识
- 价值 / 行动是决定它是否该被保留和调用的控制逻辑

## 4. 对 OpenClaw 最有价值的优化

### 优化 1：把"事件"与"模式"分仓

不要让 `MEMORY.md` 同时装事件和模式。

推荐：
- 事件进 `memory/YYYY-MM-DD.md`
- 模式进 `bank/world.md`、`bank/opinions.md`、`bank/entities/*.md`
- 会做法的经验进 `bank/procedures.md`

### 优化 2：加入"行为增益"评估

对每条长期记忆记录：
- 它影响了什么行为
- 最近几次是否被调用
- 调用后是否提升了成功率

没有行为增益的长期记忆，不要无限留在核心层。

### 优化 3：把"反思"从可选变成固定环节

在 OpenClaw 里，至少要有定期 reflection：
- 冲突检测
- 趋势检测
- 模式抽取
- 过期淘汰
- 晋升到 `MEMORY.md` 的候选生成

### 优化 4：把 Procedural Memory 单独成层

因为很多 Agent 失败，不是"不知道事实"，而是"不会复用做法"。

对编程和工作流场景尤其重要：
- 常用命令序列
- 错误-修复对
- 初始化模板
- 排障路径

### 优化 5：用"一致性引擎"控制记忆腐烂

至少要检查：
- Semantic 内部矛盾
- Episodic 与 Semantic 是否出现趋势性冲突
- Procedural 是否过时
- 高置信偏好是否被新证据推翻

## 5. 对"仿人类"的进一步增强建议

### 1. Surprise / prediction error

人类更容易记住"违反预期"的事。

还要看：
- surprise
- expectation violation

### 2. Self-model / identity

建议增加：
- current goals
- role constraints
- stable identity commitments

### 3. State-dependent recall

工程上可以近似为：
- 相似任务状态
- 相似错误状态
- 相似情绪状态
- 相似项目阶段

### 4. Observation / inference split

建议每条高价值记忆拆成：
- observation
- inference
- confidence
- evidence

## 6. 最推荐的落地结构

对 OpenClaw，推荐最终用"5 层 + 3 条轴"的看法：

- Layer 1: Core Memory
- Layer 2: Episodic Memory
- Layer 3: Semantic / Entity Memory
- Layer 4: Procedural / Reflection Memory
- Layer 5: Retrieval / Index Memory

再用三条轴约束它：
- 表征轴：放哪
- 加工轴：怎么变
- 价值轴：为什么值得保留

这样既保留工程可实现性，也比"单纯三层存储"更接近人类记忆。
