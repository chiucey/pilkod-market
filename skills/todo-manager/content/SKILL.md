---
name: todo-manager
description: 个人待办事项管理技能。当用户提到待办、提醒、任务清单、待办事项、提醒我、设置提醒、每天提醒我、或发送类似"帮我记一下xxx"的话语时触发此技能。支持：(1) 添加待办 (2) 列出待办 (3) 标记完成 (4) 删除待办 (5) 设置定时提醒 (6) 每天早晨自动提醒所有待办。
---

# Todo Manager — 个人待办管理

## 核心文件

- **待办数据**: `~/.openclaw/todo_manager/todos.json`
- **脚本**: `/workspace/skills/todo-manager/scripts/todo.py`
- **每日提醒**: `/workspace/skills/todo-manager/scripts/daily_reminder.py`

## 指令速查

### 添加待办
```
todo.py add "<内容>" [YYYY-MM-DD HH:MM]
```
示例：
- `todo.py add "审阅供应商资质文件"`（无截止时间）
- `todo.py add "提交QVL申请" "2026-03-28 14:00"`（指定时间提醒）

### 列出全部
```
todo.py list
```

### 标记完成
```
todo.py done <id>
```

### 删除待办
```
todo.py rm <id>
```

### 查看详情
```
todo.py info <id>
```

## 工作流程

### 1. 接收用户指令

用户可能这样说：
- "帮我记一下这个月要审QVL"
- "提醒我明天上午10点检查仓库"
- "我有哪些待办"
- "待办全部列出来"
- "把第3条标记完成"

**提取要素：**
- 待办内容（必填）
- 提醒时间（用户说"明天10点"、"下午3点"等 → 换算为 `YYYY-MM-DD HH:MM`）
- ID（用于完成/删除）

### 2. 执行命令

用 `exec` 工具运行脚本，例如添加：
```bash
python3 /workspace/skills/todo-manager/scripts/todo.py add "审阅供应商资质文件" "2026-04-15 10:00"
```

### 3. 设置 Cron 定时提醒

**规则：**
- 用户指定了具体时间 → 创建一次性 Cron 任务，到时推送微信
- 用户说"每天早上提醒" → 创建每日 Cron 任务（默认 08:00）

**Cron 创建方式：**
- 使用 `cron-mastery` skill
- 提醒内容调用 `daily_reminder.py`，将输出作为消息发送
- 投递目标：当前用户微信 (`channel: "openclaw-weixin"`, `to: "o9cq80zSDSyCIjzRjqI84x1PT-os@im.wechat"`)

**示例（每天早上8点提醒）：**
```
每天 08:00 → 运行 /workspace/skills/todo-manager/scripts/daily_reminder.py
              → 将输出通过微信发给 o9cq80zSDSyCIjzRjqI84x1PT-os@im.wechat
```

**示例（一次性定时提醒）：**
```
2026-03-28 10:00 → 运行 python3 /workspace/skills/todo-manager/scripts/todo.py list
                 → 将输出通过微信发给 o9cq80zSDSyCIjzRjqI84x1PT-os@im.wechat
```

### 4. 用户确认与回复

执行完成后，用自然语言告知用户：
- 已添加的内容
- 提醒时间（如有）
- 当前待办数量

## 注意事项

- **微信投递**：所有提醒必须通过 `message` 工具发送至 `channel: "openclaw-weixin"`, `to: "o9cq80zSDSyCIjzRjqI84x1PT-os@im.wechat"`
- **时间解析**：用户说"明天下午3点" → 换算为明天15:00；"本周五" → 推算具体日期
- **过期检测**：`daily_reminder.py` 自动将过期的待办标记为🔴
- **仅文字**：Cron 投递内容为纯文本，微信可直接显示
