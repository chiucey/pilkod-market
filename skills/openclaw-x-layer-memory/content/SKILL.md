---
name: openclaw-x-layer-memory
description: OpenClaw X-Layer记忆系统完整方案。当用户要求创建/诊断/升级OpenClaw多层记忆、3/4/5层记忆工作流、MEMORY.md过载修复、日记层补全、bank/实体层构建、检索增强配置，或需要理解Retain/Recall/Reflect闭环机制时使用。
---

# OpenClaw X-Layer Memory System

把 OpenClaw 的默认两层记忆升级成可解释、可检索、可反思的多层记忆系统。

## 系统概览

### 五层记忆架构

| 层级 | 名称 | 文件位置 | 核心职责 |
|------|------|----------|----------|
| **L1** | Core Memory | `MEMORY.md` | 用户偏好、长期规则、稳定事实 |
| **L2** | Episodic Memory | `memory/YYYY-MM-DD.md` | 当日事件、决策、待办 |
| **L3** | Semantic/Entity Memory | `bank/world.md`, `bank/experience.md`, `bank/opinions.md`, `bank/entities/*.md` | 语义块重组、实体对象化 |
| **L4** | Reflection Memory | `bank/reflections.md` | Consolidation、冲突检测、模式抽取 |
| **L5** | Retrieval/Index Memory | `.memory/index.sqlite` | 高召回检索、hybrid search、temporal decay |

### 三条操作轴

1. **表征轴**：记忆存在哪里（Working → Episodic → Semantic → Procedural → Retrieval）
2. **加工轴**：记忆怎么变化（Capture → Retain → Recall → Reflect → Reconsolidate → Forget）
3. **价值轴**：记忆为什么值得存在（goal impact, behavior change, reuse frequency, confidence）

## 推荐配置

| 场景 | 推荐层数 | 说明 |
|------|----------|------|
| 轻量个人助手 | 3层 | L1 + L2 + L3，先跑通基础流程 |
| 稳定生产环境 | 4层 | + L4，支持偏好演化和冲突修正 |
| 复杂工作区 | 5层 | + L5，高召回和语义检索 |

## 工作流命令

### 审计工作区

```bash
node scripts/audit_openclaw_memory.js --workspace <path> [--json]
```

检查项目：
- MEMORY.md 是否过载（>3000 tokens）
- 日记层是否完整
- `bank/` 是否存在及完整度
- 实体页覆盖率
- 检索增强配置（hybrid/MMR/temporal decay）

### 初始化多层结构

```bash
node scripts/init_x_layer_memory.js --workspace <path> --layers <3|4|5> [--force]
```

安全特性：
- 默认不覆盖已有文件
- 仅创建缺失层
- `--force` 标志可强制覆盖

### 输出 JSON 供其他流程消费

```bash
node scripts/audit_openclaw_memory.js --workspace <path> --json
```

## 关键设计原则

1. **Markdown 是事实源**：索引可重建，源文件不可替代
2. **先写入协议，后检索协议**：解决"写什么"再解决"怎么搜"
3. **先核心压缩，后 ANN**：先处理 MEMORY.md 过载，再上重型检索
4. **分层晋升规则**：
   - L2 → L1：长期有效、跨会话复用、影响行为风格
   - L2 → L3：实体被多次提及、日志无法表达关系
   - L3 → L1：被反复验证、冲突解决、必须每次可见

## 晋升标记语法

在日记层使用标记促进自动晋升：

```
## Retain
- W @entity: durable world fact（世界事实）
- B @project: agent or project experience（项目经验）
- O(c=0.80) @user: preference with confidence（带置信度的偏好）
```

## 检索增强优先级

| 优先级 | 功能 | 适用时机 |
|--------|------|----------|
| P0 | Hybrid Search (BM25 + vector) | 混合精确匹配和语义召回 |
| P1 | MMR Diversity Reranking | 返回结果重复度高 |
| P2 | Temporal Decay | 时间敏感任务 |
| P3 | QMD Backend | 超大规模向量库 |

## Guardrails

- 不要把聊天流水、整份文档、大段代码塞进 `MEMORY.md`
- 不要把检索层当事实源
- 不要在无证据时把推断写成事实
- 不要默认启用最重的向量/ANN 方案
- 不要覆盖用户已有的高质量长期记忆

## 参考文档

需要时阅读以下参考文件：

- `references/openclaw-memory-state.md` - OpenClaw 官方能力与演进方向
- `references/x-layer-design-playbook.md` - 各层详细职责与晋升规则
- `references/human-like-memory-optimization.md` - 仿人类记忆优化策略
- `references/research-map.md` - Hindsight/Mem0/SuCo 等论文要点
- `references/troubleshooting-playbook.md` - 常见症状与修复方案

## 退出条件

工作区应具备：
- 清晰的层次边界
- 可落盘的写入协议
- 可解释的检索路径
- 具体的修复/升级方案

如执行初始化，生成的文件结构应可直接使用。
