---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 00bf097696cc408e2d748b672facb342
    PropagateID: 00bf097696cc408e2d748b672facb342
    ReservedCode1: 304502203a8a8e623d82ddce7e2ccfeafd463823f86dbe9ab5ec3e1bddc002e55fbbf291022100c9266d9e57392ceef8165e5ab5d48f6ab08a3212f5bbb26335927a11ef43d771
    ReservedCode2: 304502210094626e81a0e841385bcefaeae462cdcd16bb2dac9fa277961be5378c14ac3722022008dc17a06dcfced770ac98be45cc9cc9c09e0cd08fb48b69548f0152fd4d0397
---

# Supabase 数据库设置指南 / Database Setup Guide

## 更新表结构 / Updated Table Schema

### 1. bottles 表（漂流瓶主表）/ Bottles Table

```sql
CREATE TABLE bottles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content TEXT NOT NULL CHECK (char_length(content) >= 1 AND char_length(content) <= 500),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days'),
  parent_id UUID REFERENCES bottles(id) ON DELETE CASCADE,
  is_reply BOOLEAN DEFAULT FALSE,
  reply_count INTEGER DEFAULT 0,
  sender_device_id VARCHAR(255),  -- 发送者设备ID，用于追踪
  has_new_replies BOOLEAN DEFAULT FALSE,  -- 是否有未读回复
  last_reply_at TIMESTAMP WITH TIME ZONE  -- 最后回复时间
);

-- 创建索引优化随机查询
CREATE INDEX idx_bottles_created_at ON bottles(created_at DESC);
CREATE INDEX idx_bottles_expires_at ON bottles(expires_at);
CREATE INDEX idx_bottles_parent_id ON bottles(parent_id);
CREATE INDEX idx_bottles_sender ON bottles(sender_device_id);  -- 用于查询用户发送的瓶子
CREATE INDEX idx_bottles_has_new_replies ON bottles(has_new_replies) WHERE has_new_replies = TRUE;

-- RLS 策略（允许匿名访问）
ALTER TABLE bottles ENABLE ROW LEVEL SECURITY;

-- 允许任何人插入
CREATE POLICY "Anyone can insert bottles" ON bottles
  FOR INSERT TO anon
  WITH CHECK (true);

-- 允许任何人读取
CREATE POLICY "Anyone can read bottles" ON bottles
  FOR SELECT TO anon
  USING (expires_at > NOW() OR expires_at IS NULL);

-- 允许更新回复数
CREATE POLICY "Anyone can update bottles" ON bottles
  FOR UPDATE TO anon
  USING (true);
```

### 2. bottle_recipients 表（领取记录）/ Recipients Table

```sql
CREATE TABLE bottle_recipients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bottle_id UUID NOT NULL REFERENCES bottles(id) ON DELETE CASCADE,
  recipient_identifier VARCHAR(255) NOT NULL,
  claimed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  is_reply_conversation BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_recipients_bottle_id ON bottle_recipients(bottle_id);
CREATE INDEX idx_recipients_recipient ON bottle_recipients(recipient_identifier);

-- RLS 策略
ALTER TABLE bottle_recipients ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can insert recipients" ON bottle_recipients
  FOR INSERT TO anon
  WITH CHECK (true);

CREATE POLICY "Anyone can read recipients" ON bottle_recipients
  FOR SELECT TO anon
  USING (true);
```

### 3. reply_conversations 表（回复对话）/ Reply Conversations Table

```sql
CREATE TABLE reply_conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  original_bottle_id UUID NOT NULL REFERENCES bottles(id) ON DELETE CASCADE,
  reply_bottle_id UUID NOT NULL REFERENCES bottles(id) ON DELETE CASCADE,
  sender_device_id VARCHAR(255) NOT NULL,  -- 回复发送者设备ID
  recipient_device_id VARCHAR(255) NOT NULL,  -- 原瓶子发送者设备ID
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  is_read BOOLEAN DEFAULT FALSE  -- 是否已读
);

CREATE INDEX idx_conversations_original ON reply_conversations(original_bottle_id);
CREATE INDEX idx_conversations_sender ON reply_conversations(sender_device_id);
CREATE INDEX idx_conversations_recipient ON reply_conversations(recipient_device_id);
CREATE INDEX idx_conversations_unread ON reply_conversations(is_read) WHERE is_read = FALSE;

-- RLS 策略
ALTER TABLE reply_conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can insert conversations" ON reply_conversations
  FOR INSERT TO anon
  WITH CHECK (true);

CREATE POLICY "Anyone can read conversations" ON reply_conversations
  FOR SELECT TO anon
  USING (true);

CREATE POLICY "Anyone can update conversations" ON reply_conversations
  FOR UPDATE TO anon
  USING (true);
```

## SQL 函数 / SQL Functions

### 0. 自动更新回复数函数（Trigger用）/ Auto Update Reply Count (for Trigger)

```sql
-- 创建自动更新回复数的函数
CREATE OR REPLACE FUNCTION update_parent_reply_count()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.parent_id IS NOT NULL THEN
    UPDATE bottles
    SET reply_count = (
      SELECT COUNT(*) FROM bottles WHERE parent_id = NEW.parent_id
    ),
    has_new_replies = TRUE,
    last_reply_at = NOW()
    WHERE id = NEW.parent_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
DROP TRIGGER IF EXISTS trigger_update_reply_count ON bottles;
CREATE TRIGGER trigger_update_reply_count
AFTER INSERT ON bottles
FOR EACH ROW
EXECUTE FUNCTION update_parent_reply_count();
```

### 1. 随机获取漂流瓶 / Get Random Bottle

```sql
CREATE OR REPLACE FUNCTION get_random_bottle()
RETURNS bottles AS $$
DECLARE
  selected_bottle bottles;
BEGIN
  SELECT * INTO selected_bottle
  FROM bottles
  WHERE (expires_at > NOW() OR expires_at IS NULL)
    AND is_reply = FALSE
  ORDER BY RANDOM()
  LIMIT 1;

  RETURN selected_bottle;
END;
$$ LANGUAGE plpgsql;
```

### 2. 发送漂流瓶（包含追踪）/ Send Bottle with Tracking

```sql
CREATE OR REPLACE FUNCTION send_bottle(
  p_content TEXT,
  p_sender_device_id VARCHAR
)
RETURNS bottles AS $$
DECLARE
  new_bottle bottles;
BEGIN
  INSERT INTO bottles (content, sender_device_id, is_reply)
  VALUES (p_content, p_sender_device_id, FALSE)
  RETURNING * INTO new_bottle;

  RETURN new_bottle;
END;
$$ LANGUAGE plpgsql;
```

### 3. 回复漂流瓶（包含通知更新）/ Reply Bottle with Notification

```sql
CREATE OR REPLACE FUNCTION reply_bottle(
  p_original_bottle_id UUID,
  p_content TEXT,
  p_sender_device_id VARCHAR,
  p_sender_ip VARCHAR  -- 用于匿名追踪
)
RETURNS bottles AS $$
DECLARE
  original_bottle bottles;
  reply_bottle bottles;
BEGIN
  -- 获取原瓶子
  SELECT * INTO original_bottle
  FROM bottles
  WHERE id = p_original_bottle_id;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'Bottle not found';
  END IF;

  -- 创建回复瓶子
  INSERT INTO bottles (content, sender_device_id, parent_id, is_reply)
  VALUES (p_content, p_sender_device_id, p_original_bottle_id, TRUE)
  RETURNING * INTO reply_bottle;

  -- 更新原瓶子的回复数和最后回复时间
  UPDATE bottles
  SET reply_count = reply_count + 1,
      last_reply_at = NOW(),
      has_new_replies = TRUE
  WHERE id = p_original_bottle_id;

  -- 创建对话记录
  INSERT INTO reply_conversations (original_bottle_id, reply_bottle_id, sender_device_id, recipient_device_id)
  VALUES (p_original_bottle_id, reply_bottle.id, p_sender_device_id, original_bottle.sender_device_id);

  RETURN reply_bottle;
END;
$$ LANGUAGE plpgsql;
```

### 4. 检查用户的新回复 / Check User's New Replies

```sql
CREATE OR REPLACE FUNCTION check_user_new_replies(p_device_id VARCHAR)
RETURNS TABLE(
  bottle_id UUID,
  bottle_content TEXT,
  reply_count INTEGER,
  has_new_replies BOOLEAN,
  last_reply_at TIMESTAMP
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    b.id,
    b.content,
    b.reply_count,
    b.has_new_replies,
    b.last_reply_at
  FROM bottles b
  WHERE b.sender_device_id = p_device_id
    AND b.is_reply = FALSE
  ORDER BY b.has_new_replies DESC, b.last_reply_at DESC NULLS LAST;
END;
$$ LANGUAGE plpgsql;
```

### 5. 获取瓶子的所有回复 / Get All Replies for a Bottle

```sql
CREATE OR REPLACE FUNCTION get_bottle_replies(p_bottle_id UUID, p_device_id VARCHAR)
RETURNS TABLE(
  reply_id UUID,
  reply_content TEXT,
  reply_created_at TIMESTAMP,
  is_read BOOLEAN
) AS $$
BEGIN
  -- 标记为已读
  UPDATE reply_conversations
  SET is_read = TRUE
  WHERE original_bottle_id = p_bottle_id
    AND recipient_device_id = p_device_id;

  -- 更新瓶子的has_new_replies
  UPDATE bottles
  SET has_new_replies = FALSE
  WHERE id = p_bottle_id
    AND sender_device_id = p_device_id;

  -- 返回回复列表
  RETURN QUERY
  SELECT
    b.id,
    b.content,
    b.created_at,
    CASE WHEN rc.is_read THEN TRUE ELSE FALSE END AS is_read
  FROM reply_conversations rc
  JOIN bottles b ON rc.reply_bottle_id = b.id
  WHERE rc.original_bottle_id = p_bottle_id
  ORDER BY rc.created_at ASC;
END;
$$ LANGUAGE plpgsql;
```

### 6. 获取未读回复总数 / Get Total Unread Count

```sql
CREATE OR REPLACE FUNCTION get_unread_reply_count(p_device_id VARCHAR)
RETURNS INTEGER AS $$
DECLARE
  unread_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO unread_count
  FROM bottles b
  WHERE b.sender_device_id = p_device_id
    AND b.has_new_replies = TRUE;

  RETURN unread_count;
END;
$$ LANGUAGE plpgsql;
```

## Supabase API 端点 / API Endpoints

### 1. 发送漂流瓶 / Send Bottle
```
POST /rest/v1/bottles
Headers:
  apikey: {SUPABASE_ANON_KEY}
  Authorization: Bearer {SUPABASE_ANON_KEY}
  Content-Type: application/json
  Prefer: return=representation

Body:
{
  "content": "你的句子",
  "is_reply": false,
  "sender_device_id": "用户设备ID"
}
```

### 2. 随机获取漂流瓶 / Get Random Bottle
```
POST /rest/v1/rpc/get_random_bottle
Headers:
  apikey: {SUPABASE_ANON_KEY}
  Authorization: Bearer {SUPABASE_ANON_KEY}
```

### 3. 回复漂流瓶 / Reply to Bottle
```
POST /rest/v1/rpc/reply_bottle
Headers:
  apikey: {SUPABASE_ANON_KEY}
  Authorization: Bearer {SUPABASE_ANON_KEY}
  Content-Type: application/json
  Prefer: return=representation

Body:
{
  "p_original_bottle_id": "原瓶子UUID",
  "p_content": "回复内容",
  "p_sender_device_id": "发送者设备ID"
}
```

### 4. 检查新回复 / Check New Replies
```
POST /rest/v1/rpc/check_user_new_replies
Headers:
  apikey: {SUPABASE_ANON_KEY}
  Authorization: Bearer {SUPABASE_ANON_KEY}
  Content-Type: application/json

Body:
{
  "p_device_id": "用户设备ID"
}
```

### 5. 获取瓶子的回复 / Get Bottle Replies
```
POST /rest/v1/rpc/get_bottle_replies
Headers:
  apikey: {SUPABASE_ANON_KEY}
  Authorization: Bearer {SUPABASE_ANON_KEY}
  Content-Type: application/json

Body:
{
  "p_bottle_id": "瓶子UUID",
  "p_device_id": "用户设备ID"
}
```

## 环境变量 / Environment Variables

您的项目凭证已配置：

```
SUPABASE_URL=https://fxkpgryzfzjuglqyceno.supabase.co
SUPABASE_ANON_KEY=sb_publishable_QqNJSauZqCtgJOfFUiBWnw_4Yy6o1c-
```
