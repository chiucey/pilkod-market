# OpenClaw Memory System (openclaw-mem-sys) 🧠

> 为 OpenClaw 构建的持久化内存压缩系统 —— 让 AI 记住跨会话的项目上下文

**[English](#english) | [中文](#中文)**

---

<a name="中文"></a>
## 快速开始

### 3 步安装

```bash
# 1. 安装依赖
cd /workspace/skills/openclaw-mem-sys
npm install

# 2. 初始化数据库
node scripts/init-db.js

# 3. 启动 Worker 服务
node scripts/worker.js &
```

访问 **http://localhost:37778** 查看 Web 界面。

---

### 核心功能

| 功能 | 说明 |
|------|------|
| 🧠 跨会话记忆 | 项目上下文自动保留 |
| 🔍 语义搜索 | 自然语言查询历史 |
| 📊 渐进式披露 | 智能上下文注入 |
| 🔒 隐私控制 | 敏感内容自动过滤 |

---

### 使用示例

**查询历史工作**:
```
"上个会话我们修复了哪些 bug？"
"认证功能是如何实现的？"
"显示 worker-service.ts 的修改历史"
```

**自动记忆**:
- 系统自动捕获工具使用观察
- 会话结束生成摘要
- 下次会话自动加载相关上下文

---

## 系统架构

```
OpenClaw Gateway
    ↓
生命周期钩子 (5 个)
    ↓
Worker 服务 (端口 37778)
    ↓
SQLite + Chroma 向量库
```

---

## 配置

编辑 `~/.openclaw-mem/settings.json`:

```json
{
  "worker": { "port": 37778 },
  "ai": { "model": "qwen3.5-plus" },
  "context": { "maxTokens": 4000 }
}
```

---

## 故障排除

**Worker 未启动**:
```bash
node scripts/worker.js
tail -f ~/.openclaw-mem/worker.log
```

**搜索无结果**:
```bash
node scripts/rebuild-index.js
```

---

**版本**: 1.0.0 | **许可**: MIT
