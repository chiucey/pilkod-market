---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 804b783be0ba9f3c50d7105fdbda267a
    PropagateID: 804b783be0ba9f3c50d7105fdbda267a
    ReservedCode1: 304502202068027867e585227276c9e51a31730f201720b0f1063c4cd162508abb0cdd09022100dd81d5e4df2ba596e9df6496f5a49c9702eb2fe0e0b6fe347ca60336f909ab05
    ReservedCode2: 30460221009c1137c9ab878be3f20f5e208515da2d9da77ba39910d6ff1da352c018fc2df3022100acf817ff0ed43b81a87a1f75e3bbb5799916155679e4d7ddb8bd4de727f39b79
description: Claude Code 12层Harness工程学指南。s01-s12逐层详解+5个设计模式+OpenClaw成熟度模型。
name: agent-engineering-guide
platforms:
    - OpenClaw
tags:
    - agent-engineering
    - 12-layer-harness
    - Claude-Code
    - architecture
    - multi-agent
version: 1.0.0
---

# Agent工程学指南 · 12层Harness实践
> 版本：v1.0.0
> 来源：MiMoClaw Claude Code研究 × opensource-comparison × implementation-guide
> 定位：用Claude Code工程化思想提升OpenClaw的多Agent协作能力

---

## 一、s01-s12 逐层详解（Claude Code工程架构）

> 对应Claude Code源码的12层渐进式"安全带"机制

### s01 · 核心代理循环

**目标：** 用最简循环处理所有逻辑

```
OpenClaw实现：
while (true) {
  input = getUserInput()
  response = await callAPI(input)
  if (response.toolCalls) {
    result = await executeTools(response.toolCalls)
    context.push(result)  // 追加结果，进入下一轮
  } else {
    return response  // 结束
  }
}
```

**Claude Code的改进：**
- `AsyncGenerator` 流式输出，不阻塞消费者
- 每次 `tool_result` 追加到 messages[]，循环继续
- 消息通过 `recordTranscript()` 写入 JSONL，支持崩溃恢复

**OpenClaw实践：**
```
✅ sessions_spawn 运行subagent = 独立循环实例
✅ 主session收集subagent结果 = 循环追加机制
✅ sessions_history 持久化 = 崩溃恢复
```

---

### s02 · 工具注册制（核心设计）

**原则：新增工具不修改核心循环**

Claude Code用 `buildTool()` 工厂，所有工具注册到表：
```typescript
const tools = {
  'Bash': bashTool,
  'Read': readTool,
  'Edit': editTool,
  // 新增工具只需注册，不修改while-true循环
}
```

**OpenClaw对应实现：**
```
✅ 每个skill导出标准tools:字段（name/description/input/risk_level）
✅ 主Agent通过路由表发现工具，不硬编码
✅ 新增skill不需要修改核心架构
```

---

### s03 · 计划模式（Plan Mode）

**设计：** 先列步骤再执行，完成率提升显著

```
用户请求 → Agent先输出执行步骤（Plan）
         → 用户确认/修改
         → 按步骤执行
         → 完成
```

**OpenClaw应用场景：**
```
写作任务：先输出大纲 → 用户确认 → 逐章创作
长篇创作：先输出细纲 → 用户确认 → 填充正文
多Agent任务：先输出分工表 → 各Agent按表执行
```

**触发条件：**
```
· 用户说"先规划"/"先列大纲"
· 任务包含"帮我写"/"写一个"
· subagent任务分解前
```

---

### s04 · 子Agent隔离（Session隔离）

**设计：** 每个子任务有独立messages[]，不污染主对话

```
主Agent ←→ 主Session Context
  ├── Subagent A ←→ A的独立Session（隔离）
  ├── Subagent B ←→ B的独立Session（隔离）
  └── Subagent C ←→ C的独立Session（隔离）
```

**OpenClaw实现（sessions_spawn）：**
```
sessions_spawn(
  task="写第3章",
  mode="isolated",  // 隔离模式，不污染主session
  cleanup="delete"  // 完成后清理
)
```

**关键约束（源码级硬性规则）：**
```
Subagents cannot spawn other subagents.
（子代理不能派生子代理，防止循环嵌套）
OpenClaw对应：主Agent → subagent → 禁止再派subsubagent
```

---

### s05 · 按需知识（Skill延迟加载）

**设计：** Skill/CLAUDE.md 不在系统提示词里，按需读取

```
Claude Code：Skill内容仅在相关任务时自动检索调用
实际效果：98%的对话不触发任何Skill加载

OpenClaw改进方案：
Layer 1（始终）：Skill name + 1行功能描述（< 50字）
Layer 2（按需）：完整SKILL.md内容（仅相关Expert被调用时）
```

**Skill描述精简标准：**
```
✅ 好描述（< 100字）：
  "番茄短篇创作专家。千字万金套路、钩子公式、3章完结节奏。"

❌ 差描述（> 200字）：
  "本技能用于帮助用户进行小说创作，涵盖从灵感捕捉到
   完稿发布的全链路指导，整合多个Expert协同工作……"
```

---

### s06 · 上下文压缩（Compaction）

**设计：** token超阈值时自动压缩历史消息

```
触发时机（Claude Code实测）：
  窗口使用率 ≥ 85% 时自动触发

压缩算法（3步）：
  Step 1: 识别重要消息（工具结果/关键决策）
  Step 2: LLM生成摘要
  Step 3: 替换历史，继续循环
```

**OpenClaw等效实现（session-compactor skill）：**
```
✅ session_status 监控用量
✅ 接近100k tokens时触发警告
✅ 手动压缩：生成进度快照 → 写入MEMORY.md
✅ 新session从快照恢复，不从头读历史
```

---

### s07 · 任务持久化（Task Graph）

**设计：** 基于文件的任务图，状态跟踪，崩溃可恢复

```
Claude Code:
  ~/.claude/tasks/{taskId}.json
    {
      "id": "abc123",
      "status": "in_progress",
      "steps": ["分析大纲", "✓写第1章", "进行中写第2章"],
      "checkpoint": "写第3章中"
    }
```

**OpenClaw改进方案：**
```
在MEMORY.md里维护任务状态：
  ## 当前任务：穿越异界·神王投影 卷一
  - [✓] 第1章：完成
  - [✓] 第2章：完成
  - [→] 第3章：进行中（写到一半）
  - [ ] 第4章：待写
  - 进度快照时间：2026-04-02 03:00
```

---

### s08 · 后台任务（Daemon Thread）

**设计：** 慢操作在后台跑，完成后注入通知

```
Claude Code:
  后台守护线程 → 慢操作（git clone/大型重构）
  → 完成时 → 注入 <notify> 消息到主循环
  → 用户收到通知，不阻塞主对话
```

**OpenClaw对应实现：**
```
✅ cron任务（定时写入，到期自动触发）
✅ subagent运行在后台（sessions_spawn）
✅ 主session定期检查subagent状态（sessions_list）
✅ 完成后主session自动汇总结果
```

---

### s09 · Agent团队（Persistent Teammates）

**设计：** 持久队友 + 异步邮箱，共享目标

```
Claude Code架构：
  Agent A ↔ 异步邮箱 ↔ Agent B
       ↔ 共享任务图 ↔
       ↔ 主用户 ↔

持久队友 = 长时间运行的Agent，有记忆和上下文
异步邮箱 = 消息队列，Agent不在线也能接收消息
```

**OpenClaw对应方案：**
```
主Agent = 我（长时间运行，有MEMORY.md持久化）
协作者Agent = subagent（按需启动，独立session）
消息传递 = subagent完成后 → 结果写入工作文件
         主Agent读取工作文件 → 继续协调
```

---

### s10 · 团队协商协议（Request-Response）

**设计：** Agent之间用"请求-响应"模式协商

```
Claude Code:
  Agent A ──请求: "请完成模块X"──→ Agent B
  Agent A ←─响应: "完成，结果是Y"─── Agent B

Agent可以：
  · 接受请求 → 执行 → 响应结果
  · 拒绝请求 → 说明理由 → 等待下一个请求
  · 转交请求 → 转发给其他Agent
```

**OpenClaw主Agent协调模板：**
```
协调主Agent（我）：
  → 分派任务给各subagent
  → 等待subagent响应
  → 汇总结果或处理拒绝
  → 必要时重新分配或自行完成

Subagent响应规范：
  输出格式：{"status": "done"/"failed"/"refused", "result": "...", "reason": "..."}
```

---

### s11 · 自主Agent（Idle Mode）

**设计：** 空闲循环时自动认领任务，不需要用户每次确认

```
Claude Code KAIROS模式推测逻辑：
  if (没有用户输入 && 有待处理任务) {
    agent.自动认领并执行();
  }
  if (完成任务) {
    agent.通知用户();
  }
  if (无事可做) {
    agent.进入休眠();
  }
```

**OpenClaw中的近似实现：**
```
✅ cron任务 = 定时自动执行（类似KAIROS的scheduled check-in）
✅ heartbeat检查 = 定期巡查（如HEARTBEAT.md的定期检查）
⚠️ 完全自主认领任务 = 需要KAIROS模式（平台级功能）
```

---

### s12 · 工作树隔离（Work Tree Isolation）

**设计：** 每个代理在独立目录工作，不会互相污染

```
Claude Code:
  agent-A/ → /tmp/claude/agent-a/{workspace}/
  agent-B/ → /tmp/claude/agent-b/{workspace}/
  互相隔离，即使删除错误也不影响其他Agent
```

**OpenClaw对应方案：**
```
每个subagent的workspace隔离：
  · subagent1 → /workspace/长篇小说及规划/
  · subagent2 → /workspace/番茄短故事/
  · 互相不进入对方目录

文件隔离原则：
  · 各项目文件独立目录
  · 共享文件放在 /workspace/shared/
  · subagent只在指定目录内操作
```

---

## 二、OpenClaw 12层Harness实施清单

| 层级 | 已实现 | 实施项 | 优先级 |
|------|--------|--------|--------|
| s01 | ✅ | while-true循环 + sessions_spawn | — |
| s02 | ✅ | Skill注册制 + 路由表 | — |
| s03 | 🔜 | 计划模式 → 加到session-compactor | 中 |
| s04 | ✅ | Subagent隔离 + 禁止嵌套 | — |
| s05 | 🔜 | Skill描述精简（≤100字） | 高 |
| s06 | ✅ | session-compactor | — |
| s07 | 🔜 | 任务图状态跟踪 → MEMORY.md格式 | 高 |
| s08 | ✅ | cron任务 + subagent后台 | — |
| s09 | 🔜 | Agent团队协调模板 | 中 |
| s10 | ✅ | expert-collaboration-protocol | — |
| s11 | 🔜 | KAIROS式自主认领（需平台） | 低 |
| s12 | 🔜 | subagent目录隔离规范 | 中 |

---

## 三、Claude Code工程学·设计模式手册

### 模式1：工具注册表（新增工具不改核心）

```typescript
// ❌ 错误：if-else硬编码
if (tool === 'Bash') return execBash()
if (tool === 'Read') return execRead()

// ✅ 正确：注册表
const tools = new Map()
tools.set('Bash', bashTool)
tools.set('Read', readTool)
tools.set('Edit', editTool)
// 新增工具：只需注册，不修改核心循环
```

**OpenClaw对应：** Skill注册到novel-expert-system路由表，主Agent只知道名字不知道实现。

### 模式2：循环不退出，结果追加（不是覆盖）

```typescript
// ❌ 错误：每次覆盖messages
messages = [userInput]  // 第一轮
messages = [userInput, response]  // 第二轮（丢失第一轮）

// ✅ 正确：追加
messages.push(userInput)
messages.push(response)
messages.push(toolResult)  // 追加，不覆盖
// 继续循环
```

**OpenClaw对应：** subagent结果累积到session，不清空历史直到压缩。

### 模式3：权限拒绝 ≠ 任务失败

```typescript
// 权限被拒时，AI不应该放弃，而是：
// 1. 通知用户权限被拒
// 2. 继续尝试其他步骤（如果可能）
// 3. 或者请求更明确的授权

if (permissionDenied) {
  return {
    status: 'BLOCKED',
    reason: '缺少授权',
    suggestion: '是否可以授权？或者我换个方案？'
  }
}
```

**OpenClaw对应：** skill执行被拒时 → 记录到MEMORY.md → 通知用户 → 等授权继续。

### 模式4：超时写入，崩溃可恢复

```typescript
async function runWithCheckpoint(fn, intervalMs = 30000) {
  const checkpoint = setInterval(() => {
    writeStateToFile({
      progress: fn.progress,
      timestamp: Date.now()
    })
  }, intervalMs)
  try {
    return await fn()
  } finally {
    clearInterval(checkpoint)
  }
}
```

**OpenClaw对应：** subagent每5分钟把进度写入MEMORY.md。

### 模式5：分而治之，不要大循环

```
❌ 一个Agent写完整本书
   → 上下文爆炸 → 写到一半OOM

✅ 分工模式：
   主Agent（我）→ 协调 + 大纲 + 质检
   subagent1 → 第1-5章
   subagent2 → 第6-10章
   subagent3 → 第11-15章
   → 各自独立session → 不互相污染
   → 主Agent汇总 → 统一质检
```

---

## 四、OpenClaw Agent系统成熟度模型

| 成熟度 | 特征 | 对应层级 |
|--------|------|---------|
| L1 | 单Agent，串行执行 | s01 |
| L2 | 单Agent + 工具注册 | s01-s02 |
| L3 | 多Agent派发（隔离） | s04 |
| L4 | 有压缩机制（不OOM） | s06 |
| L5 | 计划模式 + 任务持久化 | s03-s07 |
| L6 | 后台任务 + 团队协商 | s08-s10 |
| L7 | 自主运行 + 工作树隔离 | s11-s12 |

---

*版本：v1.0.0 | 2026-04-02*
*来源：MiMoClaw Claude Code研究 × agent-engineering-guide × opensource-comparison*
