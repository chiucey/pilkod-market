---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: fa047c31a5d4e90af8a812fe35b797fa
    PropagateID: fa047c31a5d4e90af8a812fe35b797fa
    ReservedCode1: 3046022100f731435dc55a5d96318a9b34f81f09f1cf7311a79f17fe388929f216fc07fa34022100efdd36c4f5b85d862750ca5ec7eec65b1f8f4b28d5fd951ba9155a44b923990f
    ReservedCode2: 3046022100d9983dff622fd703f97fb4b7510f27dbba1450664eee3ad73515772b4d55c3f00221009b7027e7434bc1bfafe465850de0430ffaffc6bbe012103bc77d1ff852d3f8d1
---

# Open Memory System

三层记忆框架 — 适用于 AI Agent 的持久化记忆系统。

## 功能特性

- **Working Memory** — 会话级临时记忆
- **Short-Term Memory** — 跨会话短期记忆
- **Long-Term Memory** — 持久化记忆（偏好/实体/事件）
- **自动过期清理** — 避免记忆无限膨胀
- **Hook 自动触发** — 自动捕捉用户偏好和重要事件
- **Cron 定期整理** — 保持记忆系统健康

## 安装

```bash
# 1. 解压到 skills 目录
cd ~/.openclaw/workspace/skills
unzip open-memory-system.zip -d open-memory-system

# 2. 部署 Hook
cp -r open-memory-system/scripts/auto-* ~/.openclaw/workspace/.hooks/

# 3. 初始化记忆目录
mkdir -p ~/.openclaw/workspace/memory/{user/{preferences,entities,events},agent/{persona,episodic},short-term}

# 4. 创建 Cron（参考 crons/memory-crons.txt）
```

## 使用示例

```bash
# 记录用户偏好
python3 scripts/memory.py pref "沟通方式" "直接高效" "用户明确表示"

# 记录重要事件
python3 scripts/memory.py event "项目启动" "Miloya 开发公司正式成立" "成功"

# 记录经验教训
python3 scripts/memory.py episode "第一次部署失败" "negative" "需要检查依赖版本"

# 读取核心记忆
python3 scripts/memory.py read

# 每日统计
python3 scripts/memory.py summary
```

## 项目结构

```
open-memory-system/
├── SKILL.md              # Skill 说明文档
├── README.md             # 本文件
├── scripts/
│   ├── memory.py         # 核心记忆 CLI
│   ├── distill_l2.py     # L2 自动提炼
│   ├── auto-load-memory/ # Hook: session start → 加载记忆
│   └── auto-save-memory/ # Hook: session end → 保存 learnings
└── crons/
    └── memory-crons.txt  # Cron 配置指南
```

## 设计说明

- `auto-save-memory` 将在 `.learnings/` 目录中新增的 md 文件保存到 `memory/user/events/`
- `distill_l2.py` 在每日 20:00 从 `short-term/` 提炼有价值内容到 `user/events/`
- 如需精细控制，可在 `.learnings/` 文件中标记 `[L2]` 或 `[重要]` 来区分优先级

## License

MIT
