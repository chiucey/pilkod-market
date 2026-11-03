---
name: proactive-four-tier-memory
description: 主动式四层认知记忆系统。当用户要求"记住这个流程"、"你还记得上次怎么做吗"、"保持上下文一致性"、长期任务、多轮对话需要记忆积累、或需要从历史经验中学习时触发。核心创新：程序性记忆（会做）独立于语义记忆（知道）、一致性校验作为系统心脏、主动召回优先于被动检索。
license: MIT
version: 1.0.0
---

# Proactive Four-Tier Cognitive Memory System

> 不同于传统记忆系统的三大核心创新：
> 1. **程序性记忆核心化** — "会做什么"单独沉淀，比事实记忆更像人类习得
> 2. **一致性校验系统化** — 每次操作前必检，防止记忆越积越错
> 3. **主动召回默认化** — 每轮对话前主动关联，而非等用户问到

## 架构概览

```
┌────────────────────────────────────────────────────────────────────┐
│                     PROACTIVE MEMORY ENGINE                         │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │              [心脏] CONSISTENCY CHECK ENGINE                  │ │
│  │  • 每次记忆操作前必执行一致性校验                              │ │
│  │  • 检测 Semantic 内矛盾、Episodic-Semantic 冲突               │ │
│  │  • Procedural 有效性验证、情感基线漂移检测                     │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │  WORKING   │→ │  EPISODIC  │→ │  SEMANTIC  │→ │ PROCEDURAL │  │
│  │  MEMORY    │  │  MEMORY    │  │  MEMORY    │  │  MEMORY    │  │
│  │            │  │            │  │            │  │            │  │
│  │ 当前上下文  │  │ 历史事件   │  │ 知识沉淀   │  │ 能力沉淀   │  │
│  │ (会话级)   │  │ (90天)     │  │ (永久)     │  │ (永久)     │  │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘  │
│        ↓               ↓               ↓               ↓         │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │              [默认] PROACTIVE RECALL                          │ │
│  │  • 对话前主动扫描，而非被动等待检索                            │ │
│  │  • 关联历史经验、预警重复错误、提醒待办                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

---

## 核心创新详解

### 创新1: 程序性记忆 — "会做什么"独立于"知道什么"

**与现有记忆系统的本质区别**：

| 记忆类型 | 传统设计 | 本技能设计 |
|---------|---------|-----------|
| 语义记忆 | 存储"是什么"（事实） | 存储"是什么"（事实） |
| 程序性记忆 | 附属功能或缺失 | **独立核心层，存储"会做什么"** |

**程序性记忆的价值**：
```
用户行为 = 知道(语义) + 会做(程序)

传统记忆系统：
  - 记住了"ESLint配置方法"(语义) → 每次都要重新组合
  - 没有"会做什么"的沉淀

本技能设计：
  - 记住了"ESLint配置"(语义)
  - 沉淀了"前端项目初始化"(程序) → 直接调用流程模板
  - 更像人类：通过练习学会技能，而非记住所有步骤
```

**程序性记忆数据结构**：
```yaml
procedural_memories:
  - id: "proc_001"
    type: "workflow"  # workflow | error_fix | shortcut | code_pattern
    name: "前端React项目初始化"
    triggers: ["新项目", "初始化", "React", "前端"]
    steps:
      - "npm create vite@latest . -- --template react-ts"
      - "npm install"
      - "配置 ESLint + Prettier"
    success_rate: 1.0
    usage_count: 5
    last_used: "2026-03-25"
    derived_from: ["ep_20260320_001", "ep_20260322_003"]
```

---

### 创新2: 一致性校验 — 系统心脏，而非附属功能

**传统设计的缺陷**：
```
记忆系统运行 → 记忆越来越多 → 矛盾累积 → 记忆失效
                    ↑
              缺少一致性校验
```

**本技能设计**：
```
每次记忆操作
    ↓
┌─────────────────┐
│  CONSISTENCY    │ ← 系统心脏，每次必检
│  CHECK ENGINE   │
└────────┬────────┘
         ↓
    ┌────┴────┐
    │ 通过?   │
    └────┬────┘
    是→  写入记忆 → 继续
    否→  冲突处理 → 用户确认或自动消解
```

**一致性校验维度**：

| 校验类型 | 检查内容 | 处理策略 |
|---------|---------|---------|
| Semantic内部 | 同一偏好有两个矛盾值 | 自动采用最新的，标记旧值为superseded |
| Episodic-Semantic | 事件与长期知识矛盾 | 检测趋势，≥3次冲突才触发更新 |
| Procedural有效性 | 流程成功率<50%且使用≥3次 | 标记deprecated或更新 |
| 情感基线 | 用户情绪分布漂移>30% | 监控，7天后确认才更新 |

**一致性检查流程（每次操作前必执行）**：
```python
def consistency_check():
    """记忆一致性校验 — 系统心脏"""
    issues = []

    # 1. Semantic 内部一致性
    for pair in find_contradictions(semantic_memories):
        issues.append(f"语义矛盾: {pair[0].key} vs {pair[1].key}")

    # 2. Episodic-Semantic 一致性
    for event in recent_episodic:
        if event contradicts(semantic):
            issues.append(f"事件与知识矛盾: {event.id}")

    # 3. Procedural 有效性
    for proc in procedural_memories:
        if proc.success_rate < 0.5 and proc.usage_count > 3:
            issues.append(f"低效流程: {proc.name}")

    # 4. 情感基线漂移
    if emotion_drift_detected():
        issues.append("情感基线漂移")

    return issues  # 有issues则阻塞写入，等待消解
```

---

### 创新3: 主动召回 — 默认行为，而非被动检索

**传统检索模式（被动）**：
```
用户提问 → 记忆检索 → 返回结果
    ↑
 等待触发
```

**本技能设计（主动）**：
```
┌─────────────────────────────────────────────────────────────┐
│                  PROACTIVE RECALL ENGINE                    │
│                                                              │
│  对话前自动执行（默认行为，无需用户触发）:                     │
│                                                              │
│  1. 实体扫描 → 用户输入中提到什么？                          │
│  2. 待办关联 → 有哪些待跟进事项与此相关？                    │
│  3. 错误预警 → 是否在重复历史上的错误？                     │
│  4. 经验关联 → 上次处理类似问题是怎么做的？                 │
│  5. 情感适配 → 用户当前情绪状态如何？                       │
│                                                              │
│  主动注入到当前上下文，而非等待检索                           │
└─────────────────────────────────────────────────────────────┘
```

**主动召回示例**：

| 场景 | 被动检索（传统） | 主动召回（本技能） |
|------|-----------------|------------------|
| 用户说"部署项目" | 用户问后才知道上次部署流程 | 自动提示"检测到重复操作，是否使用之前的部署流程？" |
| 用户遇到错误 | 检索历史解决方案 | 自动预警"这个错误之前遇到过，修复方案是..." |
| 用户提到项目名 | 手动关联相关上下文 | 自动加载该项目所有相关记忆 |

**主动召回触发算法**：
```python
def proactive_recall(user_input, all_memories):
    """主动记忆召回 — 默认行为"""
    results = []

    # 1. 实体提取
    entities = extract_entities(user_input)

    # 2. 待跟进事项检查
    for item in search_pending(all_memories):
        if item.related_to(entities):
            results.append(("followup", item, priority=0.9))

    # 3. 错误模式预警
    for pattern in search_error_patterns(user_input):
        results.append(("error_warning", pattern, priority=0.85))

    # 4. 经验关联
    for exp in search_experience(entities):
        results.append(("experience", exp, priority=0.7))

    # 5. 注入到上下文（不等待用户问）
    inject_to_context(results)

    return results
```

---

## 记忆类型详解

### 1. Working Memory（工作记忆）

**定义**：当前会话的临时上下文

**特点**：
- 容量有限（最近N轮对话）
- 会话结束自动清空
- 不需要持久化

**包含**：
- 当前对话完整上下文
- 正在执行的任务状态
- 临时变量
- 当前情感状态快照

### 2. Episodic Memory（情景记忆）

**定义**：按时间顺序的事件记录

**数据结构**：
```yaml
episodic_memories:
  - id: "ep_20260326_001"
    date: "2026-03-26"
    type: "task_completion|decision|milestone|error|learning"
    summary: "一句话摘要"
    details: "详细描述"
    tags: ["前端", "React"]
    emotion: "positive|neutral|negative"
    importance: 0.7  # 0.0-1.0
    linked_semantic: ["sem_pref_002"]
    linked_procedural: ["proc_001"]  # 新增：关联程序性记忆
    source: "user_input"  # user_input | system_detect | explicit_request
```

**生命周期**：90天，可压缩归档

### 3. Semantic Memory（语义记忆）

**定义**：从具体经历中提取的抽象知识

**与程序性记忆的区别**：
```
语义记忆 = 知道什么（事实、概念、偏好）
程序性记忆 = 会做什么（流程、技能、能力）
```

**数据结构**：
```yaml
semantic_memories:
  - id: "sem_user_001"
    type: "user_preference|project_knowledge|fact|concept|principle"
    key: "communication_style"
    value: "直接、高效、不喜欢废话"
    confidence: 0.95
    privacy_level: "public|internal|sensitive|confidential"
    version: 3
    prev_values: ["随意", "简洁"]  # 版本历史
    linked_procedural: []  # 关联的程序性记忆
```

### 4. Procedural Memory（程序性记忆）[核心创新]

**定义**：Agent通过重复实践学会的"会做什么"

**提取触发条件**：
| 触发信号 | 阈值 | 说明 |
|---------|------|------|
| 相同操作重复 | ≥3次 | 用户多次执行相同或高度相似的操作序列 |
| 相同错误重复 | ≥2次 | 同一个错误出现多次，需要记住修复方案 |
| 成功模式 | ≥3次 | 某种方法连续成功，值得沉淀为标准流程 |
| 用户显式要求 | 1次 | "记住这个流程"、"以后都这样做" |

**程序性记忆类型**：

| 类型 | 说明 | 示例 |
|------|------|------|
| workflow | 工作流程模板 | 前端项目初始化、部署流程 |
| error_fix | 错误-修复对 | Node版本不匹配→nvm切换 |
| shortcut | 快捷命令 | `npm run test && npm run build` |
| code_pattern | 代码片段 | 常用React组件模板 |

---

## 记忆操作流程

### 1. 会话初始化（Proactive Recall 默认执行）

```
会话开始
    ↓
[心脏] consistency_check() ← 必检
    ↓
load_semantic() → 加载用户画像和知识
load_today_episodic() → 加载今日事件
    ↓
[默认] proactive_recall() ← 不等待用户问
    ├→ 扫描待跟进事项
    ├→ 预警重复错误
    ├→ 关联历史经验
    └→ 注入到当前上下文
    ↓
开始对话
```

### 2. 记忆写入（一致性校验阻塞）

```
新信息进入
    ↓
[心脏] consistency_check() ← 阻塞直到通过
    ↓
┌─────────────────────┐
│     通过？           │
└─────────┬───────────┘
  是→    │    否→
  写入   │  冲突消解
         │    ├→ 自动修复（置信度差异>0.3）
         │    └→ 用户确认（置信度差异≤0.3）
```

### 3. 记忆检索（主动+被动双模式）

```
用户输入
    ↓
[默认] proactive_recall() ← 主动注入相关记忆
    ↓
被动检索（按需）
    ├→ 语义检索（回答问题）
    ├→ 模式检索（执行任务）
    └→ 时序检索（复盘历史）
    ↓
情感感知重排序
    ↓
返回结果
```

### 4. 定期演化（每周/每月）

```
触发演化
    ↓
[心脏] consistency_check() ← 全面扫描
    ↓
提取新程序性记忆 ← 检测重复模式
更新语义记忆 ← 从事件中提炼
压缩旧情景记忆 ← 归档超过90天的事件
更新情感基线 ← 趋势确认后
    ↓
生成演化报告
```

---

## 与其他技能协作

| 协作技能 | 协作方式 |
|---------|---------|
| self-improvement | 错误和修正自动流入程序性记忆 |
| agent-browser | 浏览器操作记录到情景记忆，检测可复用流程 |
| using-universal-workflow | intake阶段加载相关程序性记忆 |
| capturing-reusable-knowledge | 捕获的知识存入语义记忆 |
| reviewing-work | 复盘时触发记忆演化+一致性校验 |

---

## 触发短语

Use when the user says or means:

- "记住这个流程" / "remember this process"
- "你还记得上次怎么做吗" / "do you remember how we did it last time"
- "保持上下文" / "maintain context"
- "从之前学到的" / "learned from before"
- "这个错误之前遇到过" / "I've seen this error before"
- 长期任务、多轮对话需要记忆积累
- 需要主动关联历史经验而非被动检索

---

## 参考文档

- [procedural-extraction.md](references/procedural-extraction.md) — 程序性记忆提取详解
- [consistency-engine.md](references/consistency-engine.md) — 一致性校验引擎详解
- [retrieval-strategy.md](references/retrieval-strategy.md) — 主动召回策略详解
