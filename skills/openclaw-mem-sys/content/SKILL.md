---
name: openclaw-mem-sys
description: "OpenClaw 持久化记忆压缩系统。当用户询问「之前的对话做了什么」「mem-search 搜索」「会话历史」「项目上下文」「之前修复了什么 bug」「如何实现 xxx」「记得上次」「跨会话记忆」「自动保存上下文」「查看内存」「查询观察记录」时使用。也适用于：恢复项目进度、搜索历史决策、追踪功能开发历史、查找之前的技术方案。"
---

# OpenClaw Memory System (OpenClaw-Mem-Sys)

为 OpenClaw 构建的持久化内存压缩系统，通过自动捕获工具使用观察、生成语义摘要并使其可用于未来会话，无缝保留跨会话的上下文。

---

## 触发场景

当用户出现以下需求时，应触发此技能：

| 场景 | 触发短语示例 |
|------|------------|
| 询问历史工作 | "上个会话做了什么？"、"之前修复了什么 bug？" |
| 搜索项目历史 | "mem-search 搜索认证相关"、"查找之前的实现" |
| 恢复项目进度 | "继续上次的工作"、"恢复项目上下文" |
| 查询技术决策 | "我们之前为什么选择这个方案？"、"之前的讨论结论" |
| 追踪功能开发 | "这个功能是怎么实现的？"、"添加了哪些改动？" |

---

## 快速开始

### 安装依赖

```bash
cd /workspace/openclaw-mem-sys
npm install better-sqlite3 chromadb

# 初始化数据库
node scripts/init-db.js

# 启动 Worker 服务
node scripts/worker.js &

# 访问 Web 查看器
# http://localhost:37778
```

### 首次使用流程

1. 系统在 `~/.openclaw-mem/` 创建配置和数据库
2. 自动注册 5 个生命周期钩子
3. 启动后台 Worker 服务
4. 生成 mem-search 技能供搜索使用

---

## 核心功能

| 功能 | 描述 |
|------|------|
| 持久化内存 | 上下文跨会话自动保留 |
| 渐进式披露 | 分层记忆检索，显示令牌成本 |
| 语义搜索 | 使用 mem-search 技能自然语言查询 |
| Web 查看器 | http://localhost:37778 实时查看内存流 |
| 隐私控制 | 使用 `<no-store>` 标签排除敏感内容 |
| 自动操作 | 无需手动干预，后台运行 |

---

## mem-search 技能使用

### 触发方式

用户可以直接使用以下方式触发 mem-search：

```
"mem-search: 上个会话做了什么"
"搜索: 认证相关的观察"
"查询: worker-service.ts 的修改"
"查看最近的会话摘要"
"记得上次我们讨论的内容"
```

### 10 种搜索操作

| 操作 | 触发示例 | 说明 |
|------|----------|------|
| 搜索观察 | "mem-search 搜索数据库相关" | 全文搜索观察记录 |
| 搜索会话 | "mem-search 上周的会话摘要" | 跨会话摘要搜索 |
| 搜索提示 | "mem-search API 相关的请求" | 搜索原始用户请求 |
| 按概念搜索 | "mem-search 发现、问题 - 解决方案" | 按概念标签查找 |
| 按文件搜索 | "mem-search worker-service.ts" | 查找文件相关记录 |
| 按类型搜索 | "mem-search 决策、bug 修复" | 按类型筛选 |
| 最近上下文 | "mem-search 最近 3 次会话" | 获取最近会话 |
| 时间线 | "mem-search 昨天下午的工作" | 获取时间点上下文 |
| 时间线+搜索 | "mem-search 认证功能时间线" | 组合搜索 |
| API 帮助 | "mem-search 使用说明" | 获取使用文档 |

### 自然语言查询示例

**会话历史查询**:
```
"上个会话我们修复了哪些 bug？"
"上周我做了哪些工作？"
"这次会话我们讨论了什么决策？"
```

**功能实现追踪**:
```
"认证功能是怎么实现的？"
"添加查看器 UI 时发生了什么？"
"我们是如何决定使用 SQLite 的？"
```

**文件修改历史**:
```
"worker-service.ts 做了哪些更改？"
"查找对这个文件的所有修改"
"显示 app.js 的修改记录"
```

**上下文恢复**:
```
"继续上次没完成的工作"
"恢复项目状态"
"加载之前的项目上下文"
```

---

## 生命周期钩子

系统自动注册 5 个钩子，无需手动干预：

### 1. SessionStart (会话开始)
- 加载项目上下文
- 注入最近会话摘要
- 准备记忆系统

### 2. UserPromptSubmit (用户请求提交)
- 分析请求是否涉及历史上下文
- 触发 mem-search 检索相关记忆
- 将结果注入当前会话

### 3. PostToolUse (工具使用后)
- 捕获工具执行结果
- 生成观察记录
- 标记重要决策和发现

### 4. Stop (会话暂停)
- 保存当前状态
- 生成临时摘要

### 5. SessionEnd (会话结束)
- 生成完整会话摘要
- 提取关键概念
- 更新向量索引

---

## Web 查看器

访问 **http://localhost:37778** 查看：

- 实时内存流
- 会话历史列表
- 搜索界面
- 设置面板
- 统计信息

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/observations` | GET | 获取观察列表 |
| `/api/sessions` | GET | 获取会话列表 |
| `/api/search` | POST | 全文搜索 |
| `/api/search/semantic` | POST | 语义搜索 |
| `/api/stats` | GET | 统计信息 |
| `/api/health` | GET | 健康检查 |

---

## 隐私控制

### 排除敏感内容

在对话中使用 `<no-store>` 标签：

```
<no-store>
API 密钥: sk-1234567890abcdef
密码: mysecretpassword
</no-store>
```

系统会自动跳过标记内容的存储。

### 配置排除模式

编辑 `~/.openclaw-mem/settings.json`:

```json
{
  "privacy": {
    "excludePatterns": ["password", "secret", "api_key", "token", "credential"]
  }
}
```

---

## 配置

配置文件：`~/.openclaw-mem/settings.json`

```json
{
  "worker": {
    "port": 37778,
    "host": "localhost"
  },
  "database": {
    "sqlite": "~/.openclaw-mem/memory.db",
    "chroma": "~/.openclaw-mem/chroma"
  },
  "ai": {
    "model": "qwen3.5-plus",
    "summaryThreshold": 5,
    "compressionRatio": 0.1
  },
  "context": {
    "maxTokens": 4000,
    "injectionMode": "progressive",
    "includeFiles": true,
    "includeTimestamps": true
  }
}
```

---

## 故障排除

### Worker 服务未启动

```bash
# 检查进程
ps aux | grep worker.js

# 手动启动
node /workspace/openclaw-mem-sys/scripts/worker.js

# 查看日志
tail -f ~/.openclaw-mem/worker.log
```

### 数据库损坏

```bash
# 备份当前数据库
cp ~/.openclaw-mem/memory.db ~/.openclaw-mem/memory.db.bak

# 重新初始化
node /workspace/openclaw-mem-sys/scripts/init-db.js
```

### 搜索无结果

```bash
# 重建索引
node /workspace/openclaw-mem-sys/scripts/rebuild-index.js
```

---

## 目录结构

```
openclaw-mem-sys/
├── SKILL.md              # 本技能文档
├── _meta.json            # 元数据
├── README.md             # 使用说明
├── package.json          # 依赖配置
├── scripts/
│   ├── init-db.js        # 数据库初始化
│   ├── worker.js         # Worker 服务
│   ├── mem-search.js     # 搜索技能
│   ├── rebuild-index.js  # 重建索引
│   └── hooks/
│       ├── session-start.js
│       ├── user-prompt.js
│       ├── post-tool.js
│       ├── stop.js
│       └── session-end.js
├── web/
│   ├── index.html        # Web 查看器
│   ├── app.js
│   └── styles.css
└── references/
    └── api-docs.md       # API 文档
```

---

## 系统要求

| 组件 | 要求 |
|------|------|
| Node.js | 18.0.0+ |
| Python 3 | 用于向量嵌入 |
| OpenClaw | 支持插件的最新版本 |
| SQLite 3 | 已内置 |
