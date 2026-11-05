---
name: agent-memory
description: 为 AI agents 提供结构化长期记忆，实现跨对话的上下文理解和实体追踪。
---

# AgentMemory 技能 🧠

为 AI agents 提供结构化长期记忆系统，跨会话记住事实、从经验中学习并追踪实体。

## 安装

```bash
clawdhub install agent-memory
```

## 核心功能

### 1. 记住事实
```python
from src.memory import AgentMemory

mem = AgentMemory()

# 记住重要信息
mem.remember("用户偏好中文回复", tags=["user_preference"])

# 按标签搜索记忆
results = mem.search("用户偏好")
```

### 2. 跨会话记忆
```python
# 查询历史记忆
mem.recall("用户持仓", session_id="session_123")

# 记忆实体
mem.remember_entity("沃格光电", properties={
    "code": "603773",
    "industry": "玻璃基/MiniLED",
    "last_known_price": 34.07
})
```

### 3. 经验积累
```python
# 从错误中学习
mem.learn_from_error(
    error="Tushare API 超限",
    solution="使用batch_web_search作为备用数据源",
    context="获取A股数据时"
)
```

## 何时使用

- 记住用户的个人信息、偏好、习惯
- 跨会话追踪重要实体（如持仓股票、项目状态）
- 将经验教训积累为可复用知识
- 需要在长对话中保持上下文连续性

## 数据存储

记忆数据存储在 workspace 的 `memory/` 目录：
- `memory/entities/` — 实体信息
- `memory/conversations/` — 对话记忆
- `memory/patterns/` — 模式经验

## 与 MEMORY.md 的关系

- **MEMORY.md** — 精选长期记忆，由 AI 主动管理
- **AgentMemory** — 更广泛的结构化记忆系统，支持搜索和实体追踪
- 两者配合使用效果最佳
