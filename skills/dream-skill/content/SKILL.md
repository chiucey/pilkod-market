---
name: dream-skill
description: 自动记忆整合 Skill。定时（默认每24小时）分析近期会话与记忆文件，将零散信号合并写入持久化记忆，更新入口索引，使后续会话能快速 orient。触发条件：距上次整合≥minHours 且有新会话≥minSessions。三道门（时间门+会话门+锁门）全过才执行，否则静默跳过。手动触发：「整理记忆」「执行整合」。安装后运行 scripts/dream.py --setup 配置 cron。
---

# Dream Skill

自动后台记忆整合。模拟人类睡眠时的记忆整理过程——近24小时的碎片信号 → 合并写入结构化记忆 → 更新入口索引。

---

## 核心工作流

```
cron job 触发（默认每24小时一次）
  ├─ 检查：时间门（距上次≥minHours？）
  ├─ 检查：会话门（新会话数≥minSessions？）
  ├─ 检查：锁门（无其他实例正在运行？）
  ├─ 三门全过 → 执行四阶段整合
  │     Phase 1: Orient（定向记忆目录）
  │     Phase 2: Gather（收集近期信号）
  │     Phase 3: Consolidate（合并写入记忆）
  │     Phase 4: Prune & Index（修剪入口索引）
  └─ 完成后发送通知到主会话
```

三门任一不过 → **静默退出**（不通知，不浪费资源）

---

## 安装与配置

### 首次安装

```bash
python ~/.qclaw/skills/dream-skill/scripts/dream.py --setup
```

这会创建一个 cron job，触发周期为 `everyMs: 86400000`（24小时）。

### 配置文件

`~/.qclaw/skills/dream-skill/config.json`：

```json
{
  "autoDreamEnabled": true,
  "minHours": 24,
  "minSessions": 5,
  "notificationChannel": "webchat"
}
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `autoDreamEnabled` | `true` | `false` 时 cron 停止触发 |
| `minHours` | `24` | 两次整合的最小时间间隔（小时） |
| `minSessions` | `5` | 触发所需的最小新会话数 |
| `notificationChannel` | `webchat` | 通知发送到的频道 |

### 查看状态

```bash
python ~/.qclaw/skills/dream-skill/scripts/dream.py --status
```

输出示例：
```
上次整合：2026-04-02T22:00:00+08:00
距今：6.2 小时
当前状态：已整合（lock 持有中）
下次触发：约 18 小时后
```

### 手动触发

```bash
python ~/.qclaw/skills/dream-skill/scripts/dream.py --run
```

手动触发不受三门限制，立即执行整合并通知。

### 卸载

```bash
python ~/.qclaw/skills/dream-skill/scripts/dream.py --teardown
```

---

## 触发条件详解

### 时间门

`now - lastConsolidatedAt >= minHours`

- `lastConsolidatedAt` 存储在 `~/.qclaw/skills/dream-skill/state/lock.json` 的 `lastConsolidatedAt` 字段
- 默认 24 小时。设为 0 则绕过此门。

### 会话门

`transcripts with mtime > lastConsolidatedAt >= minSessions`

- 扫描 `~/.qclaw/workspace/transcripts/` 目录下 mtime 在 lastConsolidatedAt 之后的会话文件
- 排除当前活跃会话
- 默认 5 个。设为 0 则绕过此门。

### 锁门

检查 `lock.json` 中 `holderSessionId` + `holderTimestamp`：

- `now - holderTimestamp < STALE_THRESHOLD_MS`（默认 30 分钟）→ 有实例正在运行，退出
- 否则可获取锁，继续执行

---

## 四阶段整合（isolated session 执行内容）

详见 `references/prompt.md`。核心逻辑：

1. **Orient**：`ls` 记忆目录，读入口索引，了解现有结构
2. **Gather**：读每日日志，grep 会话转录（窄词，不读全量），找矛盾点
3. **Consolidate**：合并到已有 topic 文件，相对日期→绝对日期，删除矛盾记忆
4. **Prune & Index**：入口索引 ≤25KB，≤200行，每条≤150字符

工具约束：
- Bash：仅只读命令（`ls` / `grep` / `cat` / `find` / `stat` 等）
- Edit/Write：仅限 `~/.qclaw/workspace/memory/` 目录

---

## 状态文件

| 文件 | 位置 | 用途 |
|------|------|------|
| `lock.json` | skill state dir | lastConsolidatedAt + holderSessionId + holderTimestamp |
| `state.json` | skill state dir | 上次运行状态（sessionsReviewed / filesWritten 等） |

---

## 文件结构

```
dream-skill/
├── SKILL.md              ← 本文件
├── scripts/
│   └── dream.py          ← gate 检查、锁机制、cron 配置脚本
└── references/
    └── prompt.md         ← 四阶段整合 prompt（isolated session 执行内容）
```
