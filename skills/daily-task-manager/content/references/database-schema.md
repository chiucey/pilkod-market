# 数据库表结构详解

## 概述

DailyTaskManager 使用 Supabase（PostgreSQL）作为后端数据库，支持实时订阅和跨设备同步。

## 表结构

### 1. tasks - 任务表

```sql
CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  content TEXT NOT NULL,
  priority TEXT CHECK (priority IN ('A', 'B', 'C', 'D')) NOT NULL,
  is_hard_time BOOLEAN DEFAULT false,
  scheduled_time TIME,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'cancelled')),
  created_date DATE NOT NULL,
  completed_date DATE,
  source_date DATE,
  notes TEXT,
  order_index INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 索引优化
CREATE INDEX idx_tasks_user_date ON tasks(user_id, created_date);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
```

### 2. daily_stats - 每日统计表

```sql
CREATE TABLE daily_stats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  date DATE NOT NULL UNIQUE,
  total_tasks INTEGER DEFAULT 0,
  completed_tasks INTEGER DEFAULT 0,
  a_tasks INTEGER DEFAULT 0,
  b_tasks INTEGER DEFAULT 0,
  c_tasks INTEGER DEFAULT 0,
  d_tasks INTEGER DEFAULT 0,
  a_completed INTEGER DEFAULT 0,
  b_completed INTEGER DEFAULT 0,
  c_completed INTEGER DEFAULT 0,
  d_completed INTEGER DEFAULT 0,
  completion_rate DECIMAL(5,2) DEFAULT 0,
  avg_completion_time INTERVAL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX idx_daily_stats_user ON daily_stats(user_id);
CREATE INDEX idx_daily_stats_date ON daily_stats(date);
```

### 3. user_preferences - 用户偏好表

```sql
CREATE TABLE user_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT UNIQUE NOT NULL,
  default_priority TEXT DEFAULT 'B',
  working_hours_start TIME DEFAULT '09:00',
  working_hours_end TIME DEFAULT '18:00',
  theme TEXT DEFAULT 'light',
  notification_enabled BOOLEAN DEFAULT true,
  auto_inherit BOOLEAN DEFAULT true,
  auto_inherit_priorities TEXT[] DEFAULT ARRAY['A', 'B'],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

## 行级安全策略 (RLS)

```sql
-- 启用 RLS
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_stats ENABLE ROW LEVEL SECURITY;

-- 任务表策略
CREATE POLICY tasks_user_policy ON tasks
  FOR ALL
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- 统计表策略
CREATE POLICY stats_user_policy ON daily_stats
  FOR ALL
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());
```

## 常用查询

### 获取今日任务（含排序）
```sql
SELECT * FROM tasks
WHERE user_id = $1
  AND created_date = CURRENT_DATE
  AND status != 'cancelled'
ORDER BY
  CASE priority
    WHEN 'A' THEN 1
    WHEN 'B' THEN 2
    WHEN 'C' THEN 3
    WHEN 'D' THEN 4
  END,
  is_hard_time DESC,
  scheduled_time ASC NULLS LAST,
  order_index ASC;
```

### 获取昨日未完成任务
```sql
SELECT * FROM tasks
WHERE user_id = $1
  AND created_date = CURRENT_DATE - INTERVAL '1 day'
  AND status = 'pending'
ORDER BY priority ASC;
```

### 更新任务状态
```sql
UPDATE tasks
SET
  status = $2,
  completed_date = CASE WHEN $2 = 'completed' THEN CURRENT_DATE ELSE NULL END,
  updated_at = now()
WHERE id = $1;
```

### 生成每日统计
```sql
INSERT INTO daily_stats (user_id, date, total_tasks, completed_tasks, ...)
SELECT
  $1,
  CURRENT_DATE,
  COUNT(*) as total_tasks,
  COUNT(*) FILTER (WHERE status = 'completed') as completed_tasks,
  COUNT(*) FILTER (WHERE priority = 'A') as a_tasks,
  ...
FROM tasks
WHERE created_date = CURRENT_DATE;
```

## 实时订阅

```javascript
// 订阅今日任务变化
supabase
  .channel('tasks-today')
  .on('postgres_changes', {
    event: '*',
    schema: 'public',
    table: 'tasks',
    filter: `user_id=eq.${userId}&created_date=eq.${today}`
  }, handleTaskChange)
  .subscribe();
```
