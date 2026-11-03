---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: aba7bc4f87c650103133f25070378a51
    PropagateID: aba7bc4f87c650103133f25070378a51
    ReservedCode1: 3044022002be20c159f07414418988cf90bd8d09747d40a3d44906510fd9927316a5459b02204ea00a9ef4b4e7590c3746780b6528a6f3837806fce80def9d47cde0257f7926
    ReservedCode2: 3046022100da651b3f86cf61156adaa998dee7f77a3a9359fa5e4e4891f116232f2bda760a022100b6a68af73a62f961dbdaec151780b414bed898f7653249e880c74ee003b2dfc1
description: 漂流瓶技能 - 匿名发送和获取随机句子。当用户想要发送一句话到漂流瓶池、随机获取一个漂流瓶、或者回复一个漂流瓶时使用。 / Drifting Bottle Skill - Anonymously send and receive random messages. Use when users want to throw a message into the bottle pool, pick up a random bottle, or reply to a bottle.
name: drifting-bottle
---

# 漂流瓶 / Drifting Bottle

一个匿名漂流瓶应用，让用户可以发送、获取和回复随机句子。每个瓶子都有唯一ID，方便管理和追踪。

An anonymous drifting bottle app that allows users to send, receive, and reply to random messages. Each bottle has a unique ID for easy management and tracking.

## 发送对象规则 / Message Target Rules

**重要 / Important**: 消息只能发送给以下两种对象 / Messages can only be sent to the following two targets:

| 发送目标 / Target | 说明 / Description |
|------------------|-------------------|
| **消息池 / Pool** | 发到公开的瓶子池，随机被别人获取 / Send to public pool, randomly picked up by others |
| **来信者 / Original Sender** | 回复瓶子时，自动发给原瓶子发送者 / When replying, automatically send to original bottle sender |

**禁止 / Forbidden**: 不能指定发送给其他特定用户 / Cannot send to other specific users

## 核心功能 / Core Features

### 1. 发送漂流瓶 / Send a Bottle

**触发 / Trigger**: 用户想要"发送"、"扔出"、"投递"一句话到消息池 / User wants to "send", "throw", or "post" a message to the pool

**发送目标 / Target**: 消息池（公开池）

**流程 / Flow**:
1. 接收用户提交的句子（1-500字符）/ Receive user's message (1-500 characters)
2. 生成唯一的消息ID（UUID格式）/ Generate unique message ID (UUID format)
3. 插入到消息池数据库 / Insert into pool database
4. 检查用户之前发送的瓶子是否有新回复 / Check if user's previous bottles have new replies
5. 返回发送成功确认 + 回复通知（如有）/ Return success confirmation + reply notification (if any)

**输入参数 / Input Parameters**:
- `action`: "send"
- `message`: 要发送的句子 / Message to send

**返回示例 / Return Example**:
```
漂流瓶已投入大海 🌊
瓶子ID: abc123-xxx-xxx
━━━━━━━━━━━━━━━━━━━
📬 新消息提醒：你有 2 条新回复！
瓶子ID: xyz789-aaa-bbb
输入"查看回复"查看内容
```

### 2. 获取漂流瓶 / Get a Bottle

**触发 / Trigger**: 用户想要"获取"、"捡起"、"打开"漂流瓶 / User wants to "get", "pick up", or "open" a bottle

**流程 / Flow**:
1. 从消息池中随机选择一条未过期的瓶子 / Randomly select an unexpired bottle from pool
2. 标记该瓶子已被获取（支持一瓶多发）/ Mark bottle as claimed (supports multiple recipients)
3. 返回瓶子内容和瓶子ID / Return bottle content and bottle_id
4. 检查用户之前发送的瓶子是否有新回复 / Check if user's previous bottles have new replies
5. 提醒用户记录瓶子ID以便后续回复 / Remind user to save bottle_id for future replies

**输入参数 / Input Parameters**:
- `action`: "get"

**返回示例 / Return Example**:
```
🎉 捡到一个漂流瓶！
瓶子ID: def456-yyy-yyy
━━━━━━━━━━━━━━━━━━━
"愿你被世界温柔以待"
━━━━━━━━━━━━━━━━━━━
💡 提示：回复请使用 "回复 def456-yyy-yyy：内容"
（回复会直接发给这个瓶子的发送者）
━━━━━━━━━━━━━━━━━━━
📬 新消息提醒：你之前发送的瓶子有 1 条新回复！
```

### 3. 回复漂流瓶 / Reply to a Bottle

**触发 / Trigger**: 用户想要"回复"一个漂流瓶 / User wants to "reply" to a bottle

**发送目标 / Target**: 来信者（原瓶子发送者）

**流程 / Flow**:
1. 接收回复内容和原瓶子ID / Receive reply content and original bottle ID
2. 验证瓶子ID是否存在 / Validate bottle ID exists
3. 创建回复记录，系统自动关联原发送者 / Create reply record, system auto-links original sender
4. **回复直接发送给原瓶子发送者** / **Reply directly sent to original bottle sender**
5. 原发送者下次查询时会收到回复通知 / Original sender will receive reply notification on next query
6. 返回回复成功确认 / Return success confirmation

**输入参数 / Input Parameters**:
- `action`: "reply"
- `bottle_id`: 原瓶子ID / Original bottle ID
- `message`: 回复内容 / Reply content

**返回示例 / Return Example**:
```
💌 回复已发送！
━━━━━━━━━━━━━━━━━━━
原瓶子: def456-yyy-yyy
你的回复: "谢谢你，也愿你被温柔以待"
━━━━━━━━━━━━━━━━━━━
📨 回复将直接发送给这个瓶子的发送者
```

### 4. 查看我的瓶子 / Check My Bottles

**触发 / Trigger**: 用户想要"查看"、"管理"自己发送的瓶子 / User wants to "check" or "manage" their sent bottles

**流程 / Flow**:
1. 获取用户所有发送过的瓶子列表 / Get all bottles sent by user
2. 检查每个瓶子的回复数量 / Check reply count for each bottle
3. 标记有新回复的瓶子 / Mark bottles with new replies
4. 返回瓶子列表及状态 / Return bottle list with status

**输入参数 / Input Parameters**:
- `action`: "check_my_bottles"

**返回示例 / Return Example**:
```
📦 我的漂流瓶
━━━━━━━━━━━━━━━━━━━
瓶子ID: abc123-xxx    📝 2 条回复 🆕
瓶子ID: ghi789-zzz    📝 0 条回复
瓶子ID: jkl012-aaa    📝 1 条回复 🆕
━━━━━━━━━━━━━━━━━━━
🆕 = 有新回复
查看回复请输入：查看回复 <瓶子ID>
```

### 5. 查看回复 / View Replies

**触发 / Trigger**: 用户想要"查看回复" / User wants to "view replies"

**发送目标 / Target**: 来信者（这些是别人发给用户的回复）/ Original sender (these are replies sent to the user)

**流程 / Flow**:
1. 根据瓶子ID获取所有回复 / Get all replies for the bottle ID
2. 标记回复为已读 / Mark replies as read
3. 返回回复内容列表 / Return reply content list

**输入参数 / Input Parameters**:
- `action`: "view_replies"
- `bottle_id`: 瓶子ID / Bottle ID

**返回示例 / Return Example**:
```
💌 abc123-xxx 的回复（来自来信者）
━━━━━━━━━━━━━━━━━━━
1. "谢谢你的祝福！"
   收到时间：2024-03-22 10:30
2. "很高兴遇见你"
   收到时间：2024-03-22 14:15
━━━━━━━━━━━━━━━━━━━
回复这条瓶子：回复 abc123-xxx：内容
```

## Supabase 数据模型 / Data Model

### 表 / Table: bottles
| 字段 / Field | 类型 / Type | 说明 / Description |
|------|------|------|
| id | UUID | 主键，瓶子唯一标识（用于回复）/ Primary key, unique bottle identifier (for replies) |
| content | TEXT | 句子内容 / Message content |
| created_at | TIMESTAMP | 创建时间 / Creation time |
| expires_at | TIMESTAMP | 过期时间（可选）/ Expiration time (optional) |
| parent_id | UUID | 父瓶子ID（回复时关联来信者）/ Parent bottle ID (links to original sender) |
| sender_device_id | VARCHAR | 发送者设备ID（用于追踪来信）/ Sender device ID (for tracking) |
| reply_count | INTEGER | 回复数量 / Reply count |
| has_new_replies | BOOLEAN | 是否有新回复（未读）/ Has new replies (unread) |
| last_reply_at | TIMESTAMP | 最后回复时间 / Last reply time |

### 表 / Table: reply_conversations
| 字段 / Field | 类型 / Type | 说明 / Description |
|------|------|------|
| id | UUID | 主键 / Primary key |
| original_bottle_id | UUID | 原瓶子ID / Original bottle ID |
| reply_bottle_id | UUID | 回复瓶子ID / Reply bottle ID |
| sender_device_id | VARCHAR | 回复发送者设备ID / Reply sender device ID |
| recipient_device_id | VARCHAR | 原瓶子发送者设备ID（来信者）/ Original sender device ID (incoming) |
| created_at | TIMESTAMP | 创建时间 / Creation time |
| is_read | BOOLEAN | 是否已读 / Is read |

## 使用示例 / Usage Examples

### 发送漂流瓶 / Send to Pool
```
用户 / User: 我想发送一句话："愿你被世界温柔以待"
技能 / Skill: 漂流瓶已投入大海 🌊
            瓶子ID: abc123-xxx
            → 发往消息池，公开给所有人
            （如有回复则提示）
```

### 获取漂流瓶 / Get from Pool
```
用户 / User: 给我一个漂流瓶
技能 / Skill: 🎉 捡到一个漂流瓶！
            瓶子ID: def456-yyy
            "愿你被世界温柔以待"
            💡 提示：回复请使用"回复 def456-yyy：内容"
            → 回复会直接发给这个瓶子的发送者
```

### 回复漂流瓶 / Reply to Sender
```
用户 / User: 回复 def456-yyy："谢谢你，也愿你被温柔以待"
技能 / Skill: 💌 回复已发送！
            → 直接发送给 def456-yyy 的发送者
```

### 查看我的瓶子 / Check My Bottles
```
用户 / User: 查看我的瓶子
技能 / Skill: 📦 我的漂流瓶
            abc123-xxx  📝 2条回复 🆕
            ghi789-zzz  📝 0条回复
```

### 查看来信 / View Incoming Replies
```
用户 / User: 查看回复 abc123-xxx
技能 / Skill: 💌 abc123-xxx 的来信
            1. "谢谢你的祝福！"
            2. "很高兴遇见你"
```

## 新消息通知机制 / New Message Notification

### 触发时机 / When to Notify

| 场景 / Scenario | 通知内容 / Notification |
|----------------|------------------------|
| 发送瓶子后 / After sending | 检查并提示该瓶子是否有新回复（来自来信者）/ Check and notify if bottle has new replies (from senders) |
| 获取瓶子后 / After getting | 提示用户所有发送过的瓶子中是否有新回复 / Notify if any sent bottles have new replies |
| 每次交互 / Every interaction | 主动查询并显示所有未读回复数 / Actively query and show all unread reply count |

### 通知格式 / Notification Format
```
📬 新消息提醒
━━━━━━━━━━━━━━━━━━━
你有 X 条新回复！
瓶子ID: xxx-yyy
输入"查看回复 xxx-yyy"查看内容
━━━━━━━━━━━━━━━━━━━
```

## 错误处理 / Error Handling

| 场景 / Scenario | 返回 / Response |
|------|------|
| 数据库连接失败 / Database connection failed | "暂时无法连接到漂流瓶服务器，请稍后再试" / "Cannot connect to bottle server, please try again later" |
| 瓶子池为空 / Bottle pool is empty | "海面上没有漂流瓶了，成为第一个投瓶的人吧" / "No bottles on the sea, be the first to throw one!" |
| 内容超长 / Content too long | "这句话太长了，请控制在500字以内" / "Message too long, please keep it under 500 characters" |
| 无效的瓶子ID / Invalid bottle ID | "这个瓶子不存在或已消失" / "This bottle doesn't exist or has disappeared" |
| 找不到瓶子记录 / Bottle not found | "未找到对应的瓶子记录" / "Cannot find bottle record" |

## 技术实现 / Technical Implementation

- **后端 / Backend**: Supabase (PostgreSQL)
- **认证 / Auth**: 匿名用户，无需登录 / Anonymous users, no login required
- **追踪方式 / Tracking**: 使用设备ID追踪用户发送的瓶子 / Use device ID to track user's sent bottles
- **消息路由 / Message Routing**: 只能路由到消息池或来信者 / Can only route to pool or original sender
- **通知机制 / Notification**: 每次操作时检查 has_new_replies 字段 / Check has_new_replies field on every interaction
- **随机获取 / Random Selection**: 使用 ORDER BY RANDOM() 实现 / Implemented with ORDER BY RANDOM()

## 注意事项 / Notes

1. **发送对象限制 / Message Target Restriction**: 只能发送到消息池或来信者，不能指定其他用户 / Can only send to pool or original sender, cannot specify other users
2. 所有用户交互完全匿名 / All user interactions are completely anonymous
3. 支持一瓶多发：同一瓶子可以被多人获取 / Supports multiple recipients: same bottle can be claimed by multiple people
4. 回复时系统自动追踪原发送者（来信者）/ System automatically tracks original sender when replying
5. 建议设置瓶子过期时间（如30天）以保持数据新鲜 / Recommended to set expiration time (e.g., 30 days) to keep data fresh
6. **瓶子ID是用户管理瓶子的唯一凭证，请提醒用户记录 / Bottle ID is the only credential for managing bottles, remind users to save it**
7. **每次交互时主动检查并提醒新回复 / Actively check and remind about new replies on every interaction**
