---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: b5f4de2b1f123607319ea7b7ee88d566
    PropagateID: b5f4de2b1f123607319ea7b7ee88d566
    ReservedCode1: 3045022031488a3b05b2cf7ed3ef8e66e0bab643aeb9ea0e8b78b654cfee7b9dc1eaee8e0221008af7649eb22143df76c683725ba508efb3897f5ea55b0ec03c8a24bedd58f850
    ReservedCode2: 3045022078c39aaa80caf749790a6f9b3a16a049ab8ca7babedd719e13be0fb67913f933022100ccae55993fca21ff1a071b1e2ea6cca3254921daca2072ca7eaea15a8e9af725
description: 智能体跨平台迁移分析器。帮助用户在不同平台间丝滑迁移智能体。当用户要求将 AI Agent 从 A 平台迁移到 B 平台时触发，例如"帮我迁移智能体"、"从 OpenClaw 迁移到 Dify"、"迁移到 Coze"、"如何把机器人迁移到新服务器"。自动检测源平台配置、子代理、MCP Server 和外挂数据库，生成完整迁移方案和分步实施指南。
name: agent-migrator
---

# Agent Migrator V2

智能体跨平台迁移分析器。**先问方向，再动手** — 不知道目的地，就无法判断哪些资产能用、哪些要重来。

---

## 工作流程

### Step 0: 询问目标平台（强制第一步）

**询问用户:** "请问你想把当前的智能体迁移到哪个平台？"

支持的平台：
- OpenClaw、CherryBot、Dify、Coze、AnythingLLM、AutoGen
- 云服务器（自部署）、自定义平台

**未指定目标平台时，不继续扫描。**

---

### Step 1: 扫描源平台

运行扫描脚本：

```bash
python3 /workspace/skills/agent-migrator/scripts/scanner.py \
  --source <平台名> --target <目标平台> [--path /扫描路径]
```

**自动检测:**
- 配置文件（openclaw.json、.env、channels.yaml）
- 技能目录（skills/）
- 记忆文件（memory/）
- 身份配置（SOUL.md、USER.md、IDENTITY.md）

---

### Step 2: 平台差异分析

对比源平台与目标平台的架构差异：

| 差异维度 | 分析内容 |
|---------|---------|
| 配置格式 | 能否直接导入？需格式转换？ |
| 渠道接入 | 飞书/Telegram/Discord 等是否支持 |
| 技能系统 | skills/ 目录能否复用？ |
| 记忆机制 | memory/ 对话历史是否兼容 |
| 子代理 | runtime 是否兼容 |
| MCP Server | 需重新注册 |
| 外挂数据库 | 需重新配置连接 |

---

### Step 3: 扩展组件检测

自动检测三类组件：

**🤖 子代理配置**
- 检测来源: `openclaw.json > agents[]/sessions[]`、`skills/*/agent.json`
- 输出: 名称、运行时类型、模型、Prompt 描述

**🔗 MCP Server 连接**
- 检测来源: `openclaw.json > mcpServers[]`、`.env > MCP_*`、`mcp.json`
- 输出: Server 名称、连接地址、认证方式
- **强制规则**: 禁止直接传输，必须在目标平台重新注册

**🗄️ 外挂数据库**
- 检测来源: `openclaw.json > databases[]`、`.env > SUPABASE_*/POSTGRES_*`
- 支持: Supabase、PostgreSQL、MySQL、MongoDB、Redis、SQLite
- **强制规则**: 禁止明文传输凭证，必须重新配置

---

### Step 4: 生成文件迁移清单

输出四分类清单：

```
📋 文件迁移清单
├── ✅ 可迁移文件（直接复制可用）
│   ├── MEMORY.md、memory/*.md
│   └── SOUL.md、USER.md、IDENTITY.md
│
├── 🔁 需转换文件（格式/语法需调整）
│   ├── openclaw.json（转换为目标平台格式）
│   └── skills/*.md（部分技能需重构）
│
├── 🔧 需重建文件（无法迁移）
│   ├── credentials/、.env
│   ├── MCP Server 连接
│   └── 数据库连接
│
└── ⏭️ 可跳过文件（平台特定缓存/临时文件）
```

---

### Step 5: 生成迁移文档

自动生成 `migration-plan-<时间戳>.md`，包含：

1. **执行摘要** — 迁移概述、各组件计数、风险等级
2. **平台差异报告** — 源 vs 目标 逐维度对比
3. **扩展组件检测报告** — 子代理 / MCP Server / 数据库清单
4. **文件清单表** — 路径、类型、迁移方式、注意事项
5. **分步指南** — 可直接复制执行的命令
6. **校验清单** — 迁移后逐一确认

---

## 风险评估

| 风险等级 | 条件 |
|---------|------|
| 🟢 低 | 无需重建文件，无扩展组件 |
| 🟡 中 | 存在需重建文件或少量扩展组件 |
| 🔴 高 | 存在多个数据库连接或复杂 MCP 配置 |

---

## 重要规则

### 子代理迁移
- 不同平台 runtime 不兼容（OpenClaw subagent vs Coze Bot 等）
- **处理**: 在目标平台重新创建子代理定义，参考原配置中的 model 和 prompt

### MCP Server（强制）
- 地址和 Token **禁止直接传输**
- 必须在目标平台重新注册所有 MCP Server
- 如部署在内网，确认目标服务器网络可达

### 外挂数据库（强制）
- Host/Port/Token/密钥 **禁止明文传输**
- Supabase: 重新创建项目，导出/导入数据后更新 .env
- PostgreSQL/MySQL: 确认网络可达后更新连接字符串

---

## 输出位置

- 迁移文档: `/workspace/migration-plan-<时间戳>.md`
- 摘要 JSON: `/workspace/migration-plan-<时间戳>-summary.json`
