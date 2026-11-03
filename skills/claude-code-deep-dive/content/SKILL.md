---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: a339ff5d142e5afbeab1d17bc38463c2
    PropagateID: a339ff5d142e5afbeab1d17bc38463c2
    ReservedCode1: 304502205655ec78f2f1c9e1f4e52dcc13da2268f66df08c7d1eeaa2cd4a8d52ecec38d4022100dd38020b2150f783f4a937c7f7de992eed6c3dfa656cd260b75e28493c7aada3
    ReservedCode2: 3046022100d16b878a96fd56e4a9047ed34671f09fdbabb380e6979ae0efe7b53d4b783205022100e8cfcb826bfae7d5b7597205de324d3b16e7f9742ba2d57583906c635922425f
description: Claude Code源码深度研究。query.ts流式架构/Capybara v8数据/遥测双管道/KAIROS天牛Tick。
name: claude-code-deep-dive
platforms:
    - OpenClaw
tags:
    - Claude-Code
    - deep-dive
    - architecture
    - telemetry
    - feature-flags
    - KAIROS
version: 1.0.0
---

# Claude Code深度研究补充篇 · MiMoClaw新发现
> 版本：v1.0.0
> 来源：MiMoClaw Claude Code学习成果 × 源码级分析
> 定位：对Claude_Code源码架构研究.md的补充深化

---

## 一、query.ts 源码级架构（785KB的真相）

> 来源：DEEP_DIVE_MODULES.md

### 1.1 核心循环的本质

```
不是状态机，是while-true循环 + AsyncGenerator流式
```

```typescript
// 伪代码表示
async function* query() {
  while (true) {
    const normalized = normalizeMessagesForAPI(messages)
    const response = await claude.complete(normalized)
    
    if (response.stop_reason === 'tool_use') {
      // 工具调用：执行 → 追加结果 → 继续循环
      const result = await executeTool(response.tool)
      messages.push({ role: 'user', content: result })
      // 注意：不return，继续循环
    } else {
      // 文本返回：结束
      yield response
      break
    }
  }
}
```

### 1.2 recordTranscript() 崩溃恢复机制

```
每个user/assistant消息都写入JSONL文件
· user消息：阻塞写入（崩溃不丢失）
· assistant消息：fire-and-forget（异步）
→ 位置：~/.claude/telemetry/ 或项目目录
→ 格式：JSONL（每行一个事件）
→ 用途：崩溃后恢复session状态
```

### 1.3 autoCompact() 触发时机

```
触发条件：token窗口使用率 ≥ 85%
触发位置：while-true循环内部（每次API返回后检查）
压缩对象：
  · AI思考过程（可丢弃）
  · 连续对话（合并压缩）
  · 工具调用的中间结果（保留关键输出）
保留内容：
  · 系统提示词（不变）
  · 最终决策点（标记保留）
  · 文件读取结果（重要，保留）
```

---

## 二、工具系统深度解析

### 2.1 buildTool() 工厂架构

```
buildTool<Input, Output, Progress>(definition)
  ↓
返回标准Tool接口
  ↓
每个工具有7个方法：
```

| 方法 | 作用 | 调用时机 |
|------|------|---------|
| `validateInput()` | 尽早拒绝无效参数 | 权限检查之前 |
| `checkPermissions()` | 工具特定授权逻辑 | 执行之前 |
| `isEnabled()` | 功能开关 | 工具调用前检查 |
| `isConcurrencySafe()` | 可否并行执行 | 并发控制 |
| `isReadOnly()` | 是否只读（无副作用） | 执行前判断 |
| `isDestructive()` | 是否不可逆操作 | 危险操作警告 |
| `renderXxx()` | React/Ink终端渲染 | 输出展示 |

### 2.2 工具分类清单

```
文件类：FileRead, FileEdit, FileWrite, NotebookEdit
搜索类：GlobTool (文件名匹配), GrepTool (内容搜索，基于ripgrep)
执行类：BashTool, PowerShellTool
网络类：WebFetch, WebSearch, MCPTool (可扩展)
代理类：AgentTool (派生子代理), SendMessageTool
任务类：TaskCreate, TaskUpdate, TaskList
交互类：AskUserQuestionTool (向用户提问)
特殊类：EnterPlanModeTool, TodoWriteTool
```

---

## 三、s01-s12完整架构层级

> 来源：CLAUDE_CODE_DISTILLED.md

| 层 | 名称 | 核心机制 | OpenClaw对应 |
|---|------|---------|------------|
| s01 | 核心循环 | while-true + API调用 + 工具执行 | sessions_spawn |
| s02 | 工具调度 | buildTool()工厂，注册制 | Skill注册表 |
| s03 | 计划模式 | 先列步骤再执行，完成率翻倍 | 计划模式skill |
| s04 | 子Agent | 独立messages[]，隔离不污染 | sessions_spawn isolated |
| s05 | 按需知识 | SkillTool延迟加载，98%节省 | 路由表+描述精简 |
| s06 | 上下文压缩 | autoCompact()三层策略 | session-compactor |
| s07 | 任务持久化 | 基于文件的任务图，状态跟踪 | MEMORY.md |
| s08 | 后台任务 | 守护线程跑慢操作，完成注入通知 | cron任务 |
| s09 | Agent团队 | 持久队友 + 异步邮箱 | 协调主Agent |
| s10 | 团队协商 | Request-Response驱动协商 | 协作协议 |
| s11 | 自主Agent | 空闲循环自动认领任务 | cron+heartbeat |
| s12 | 工作树隔离 | 每个代理独立目录 | subagent目录隔离 |

---

## 四、遥测系统完整分析

> 来源：01-遥测与隐私分析.md

### 4.1 双管道架构

```
第一方日志管道：
  端点：api.anthropic.com/api/event_logging/batch
  协议：OpenTelemetry + Protocol Buffers
  批量：最多200事件/批，每10秒刷新
  重试：二次方退避，最多8次
  失败处理：持久化到磁盘，积极重试
  ⚠️ 无法关闭（直接API用户）

第三方日志管道：
  端点：http-intake.logs.us5.datadoghq.com/api/v2/logs
  范围：仅64种预批准事件类型
  Token：pubbbf48e6d78dae54bceaa4acf463299bf
  可关闭：✅ 可以（设置禁用）
```

### 4.2 环境指纹清单（每个事件都带）

```
platform, platformRaw, arch, nodeVersion
终端类型
已安装的包管理器和运行时
CI/CD检测
GitHub Actions元数据
WSL版本、内核版本
版本控制系统类型
Claude Code版本和构建时间
部署环境
```

### 4.3 Capybara v8实测问题

```
虚假声明率：v8为29-30%，v4为16.7%
停止序列误触发：约10%概率（prompt尾出现<functions>时）
空tool_result：导致零输出，需要注入marker workaround
过度写注释：需要专门的反注释prompt补丁
验证不足：需要thoroughness counterweight补丁
```

---

## 五、Feature Flag命名体系

### 5.1 命名规则

```
所有feature flag使用 tengu_ 前缀 + 随机鸟名对
例：tengu_onyx_plover, tengu_coral_fern
目的：掩盖真实用途，防止泄露
```

### 5.2 已识别Flag对照表

| Flag | 用途 | Kill Switch? |
|------|------|-------------|
| tengu_onyx_plover | Auto Dream（后台记忆整理） | — |
| tengu_coral_fern | memdir功能 | — |
| tengu_herring_clock | 团队内存 | — |
| tengu_frond_boric | 分析kill switch | ✅ |
| tengu_amber_quartz_disabled | 语音模式kill switch | ✅ |
| tengu_amber_flint | 代理团队 | — |

---

## 六、模型代号体系与保护机制

### 6.1 代号全谱

| 代号 | 角色 | 证据 |
|------|------|------|
| **Tengu（天狗）** | 产品/遥测前缀 | 所有250+事件和flag用`tengu_*` |
| **Capybara（水豚）** | Sonnet v8系列 | `capybara-v2-fast[1m]`，有行为问题 |
| **Fennec（耳廓狐）** | Opus 4.6前代 | `fennec-latest`→`opus`迁移 |
| **Numbat（袋食蚁兽）** | 下一代模型 | 注释`launch numbat`标记 |

### 6.2 代号保护机制

```
Undercover模式保护规则：
· 禁止出现在commit message或PR描述
· 禁止出现在构建产物中
· 冲突代号用String.fromCharCode()动态构造

特别注意：capybara是唯一冲突代号
  → 既是宠物物种名称（Buddy系统）
  → 又是模型代号
  → 用编码方式避免触发检查
```

---

## 七、KAIROS深度解析

### 7.1 天牛Tick心跳机制（推测）

```
架构推测逻辑：
  <tick> 信号 → 保持代理活跃
  每tick → 检查是否有待处理任务
  无任务 → 代理进入休眠/空闲循环
  有任务 → 代理自动认领并执行

关联机制：
  · MCP Channel Notifications（社交软件消息触发）
  · KAIROS_GITHUB_WEBHOOKS（GitHub信号订阅）
  · scheduled check-in skills（定时触发）
  · remote control（远程控制）
```

### 7.2 KAIROS与OpenClaw功能对照

| KAIROS能力 | OpenClaw现状 | 差距 |
|-----------|------------|------|
| 自主认领任务 | cron定时任务可近似 | 部分差距 |
| 事件驱动触发 | MCP channel | 基本一致 |
| GitHub Webhook订阅 | 无内置 | 需开发 |
| 远程控制 | 无内置 | 需开发 |
| brief视图（极简） | 无 | 需开发 |
| 工具主动推消息 | 无（轮询） | 重大差距 |

---

## 八、实施建议（基于源码）

### 8.1 OpenClaw当前成熟度

```
L4（多Agent + 有压缩）：
  ✅ s01: sessions_spawn
  ✅ s04: 隔离subagent
  ✅ s06: session-compactor
  ✅ s10: expert-collaboration-protocol

L3（有工具注册）：
  ✅ s02: Skill路由表

L5-L7待实现：
  🔜 s07: 任务图状态（MEMORY.md）
  🔜 s03: 计划模式
  🔜 s05: Skill描述精简
  🔜 s08: 后台任务通知
  🔜 s12: subagent目录隔离
```

### 8.2 最高ROI的3个改进

```
① Skill描述精简（s05）
   → 减少每次调用60% token消耗
   → 工作量：每skill改1行description
   → 收益：所有创作任务token-60%

② MEMORY.md任务图格式（s07）
   → 防止长篇创作写到一半忘了进度
   → 工作量：写一个模板到MEMORY.md
   → 收益：每个长篇项目少浪费30分钟重读历史

③ subagent目录隔离规范（s12）
   → 防止subagent误操作其他项目文件
   → 工作量：在subagent指令里加一行cd
   → 收益：避免一次文件误删事故
```

---

*版本：v1.0.0 | 2026-04-02*
*来源：MiMoClaw DEEP_DIVE_MODULES × CLAUDE_CODE_DISTILLED × 01-05分析系列 × agent-engineering-guide*
*补充自：Claude_Code源码架构研究.md（主文件）*
