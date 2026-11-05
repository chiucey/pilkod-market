---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 11eadc87e7218f8d29af7bf55c7ed30e
    PropagateID: 11eadc87e7218f8d29af7bf55c7ed30e
    ReservedCode1: 3045022100b95e4fa4ee3d015b311261efe0ab5a317f03762263d2c1999df80a65988876ad022074220d0e46cf35ed960cce0c6ea37a383b48e91d44d24b59e16ffeb15caa4ff7
    ReservedCode2: 3046022100cb4a69ec5ced4d3bda80668be2a1c69468701516f91c11ba37539de991e96083022100ddbd15f1d2f130ad72983b13c3a05e6ef83ff058293353cba8ff1451e988c1ad
description: 管理每日任务的家务、采购、健身和个人事务。当用户要求创建每日任务清单、管理任务优先级、查看任务进度、继承前一天未完成任务、进行任务统计复盘时使用。
name: daily-task-manager
---

# DailyTaskManager - 每日任务管理器

## 核心能力

1. **任务输入** - 接收文字或语音输入的今日任务，自动识别优先级
2. **智能分类** - 将任务分为 A/B/C/D 四个优先级
3. **任务继承** - 自动继承前一天未完成的任务
4. **清单生成** - 输出可交互的网页任务清单
5. **状态追踪** - 记录完成情况，支持统计分析
6. **软硬时间** - 支持固定时间（硬）和灵活安排（软）的任务

## 优先级定义

| 优先级 | 标签 | 颜色 | 说明 |
|--------|------|------|------|
| A级 | 必须完成 | 红色 | 今天必须完成的核心任务 |
| B级 | 最好完成 | 蓝色 | 今天最好完成的重要任务 |
| C级 | 可延迟 | 灰色 | 可延迟1-3天的任务 |
| D级 | 未来优化 | 浅灰 | 非必要任务，未来优化时再做 |

## 工作流程

### 1. 每日首次启动

```
当用户开始新的一天时：
1. 查询 Supabase 获取昨天未完成的任务
2. 询问用户是否继承这些任务
3. 如果用户没有指定新优先级，保持原优先级
4. 如果用户指定更改，按新优先级分类
```

### 2. 任务输入处理

```
当用户输入新任务时：
1. 解析任务内容
2. 如果用户明确指定优先级，使用指定优先级
3. 如果用户未指定，根据关键词推断优先级：
   - 强烈词语（必须、紧急、重要）→ A级
   - 中度词语（应该、最好、建议）→ B级
   - 弱化词语（可以、有空、之后）→ C级
   - 可选词语（优化、改进、考虑）→ D级
4. 标记软/硬时间（固定时间=硬，灵活=软）
5. 保存到 Supabase
```

### 3. 任务继承逻辑

```
继承规则：
- 前一天的 A级 → 默认保留为 A级
- 前一天的 B级 → 默认保留为 B级
- 前一天的 C级 → 默认升级为 B级（已延迟一天）
- 前一天的 D级 → 保持 D级
- 用户可以随时说"更改优先级"来调整
```

### 4. 生成每日清单

```
生成清单时：
1. 按优先级分组（A→B→C→D）
2. 同优先级内按软/硬时间排序
3. 硬时间任务排在软时间任务之前
4. 生成可交互的网页格式
```

## 输出格式

### 网页清单格式

```html
<div class="daily-task-list" data-date="2024-01-15">
  <div class="priority-section priority-a">
    <h3>🔴 A级任务 - 必须完成</h3>
    <ul class="task-list">
      <li class="task-item" data-task-id="xxx">
        <input type="checkbox" id="task-xxx">
        <label for="task-xxx">
          <span class="task-content">任务描述</span>
          <span class="task-time">09:00</span>
        </label>
      </li>
    </ul>
  </div>
  <!-- 类似结构用于 B/C/D 级 -->
</div>
```

### 数据存储结构 (Supabase)

```sql
-- 任务表
CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  content TEXT NOT NULL,
  priority TEXT CHECK (priority IN ('A', 'B', 'C', 'D')),
  is_hard_time BOOLEAN DEFAULT false,
  scheduled_time TIME,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'cancelled')),
  created_date DATE NOT NULL,
  completed_date DATE,
  source_date DATE,  -- 任务来源日期（用于继承追溯）
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- 每日统计表
CREATE TABLE daily_stats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  date DATE NOT NULL,
  total_tasks INTEGER DEFAULT 0,
  completed_tasks INTEGER DEFAULT 0,
  a_tasks INTEGER DEFAULT 0,
  b_tasks INTEGER DEFAULT 0,
  c_tasks INTEGER DEFAULT 0,
  d_tasks INTEGER DEFAULT 0,
  completion_rate DECIMAL(5,2) DEFAULT 0,
  created_at TIMESTAMP DEFAULT now()
);
```

## 交互命令

| 命令 | 功能 |
|------|------|
| "今天任务：..." | 添加新任务 |
| "优先级A/B/C/D：..." | 指定优先级添加任务 |
| "下午3点做..." | 添加硬时间任务 |
| "有空再做..." | 添加软时间任务 |
| "继承昨天的任务" | 获取并继承未完成任务 |
| "完成任务X" | 标记任务完成 |
| "调整优先级X为A/B/C/D" | 更改任务优先级 |
| "查看本周统计" | 生成统计报告 |
| "生成清单" | 输出网页清单 |

## 示例对话

### 示例1：首次添加任务
```
用户：今天要买牛奶、洗衣服、开会
助手：已添加今日任务：
  🔴 A级：开会（硬时间：待定）
  🔵 B级：买牛奶、洗衣服
是否需要指定具体时间？
```

### 示例2：继承任务
```
助手：您有3个昨天未完成的任务：
  1. 买牛奶 - B级
  2. 准备报告 - A级
  3. 健身 - B级
是否全部继承到今天？

用户：买牛奶改成C级吧
助手：已调整，今天任务更新为：
  🔴 A级：准备报告
  🔵 B级：健身
  ⚪ C级：买牛奶（降级）
```

### 示例3：查看统计
```
用户：查看这周的统计
助手：本周任务统计（1/8-1/14）：
  - 总任务数：42
  - 完成数：35
  - 完成率：83.3%
  - A级完成率：100%
  - B级完成率：85%
  - C级完成率：75%
  - 未完成任务：7
```

## Supabase 连接

```javascript
// Supabase 客户端初始化
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// 核心查询
// 1. 获取今日任务
supabase.from('tasks')
  .select('*')
  .eq('user_id', userId)
  .eq('created_date', today);

// 2. 获取昨日未完成任务
supabase.from('tasks')
  .select('*')
  .eq('user_id', userId)
  .eq('created_date', yesterday)
  .neq('status', 'completed');

// 3. 更新任务状态
supabase.from('tasks')
  .update({ status: 'completed', completed_date: today })
  .eq('id', taskId);
```

## 输出选项

1. **网页清单** - 生成可交互的 HTML，支持勾选和调整
2. **纯文本列表** - 简单的文字清单
3. **统计报告** - 完成率、趋势分析
4. **导出数据** - JSON/CSV 格式

## 限制与边界

- 单日任务上限：50个
- 优先级继承时间：1天（超过1天的C/D级任务需要用户确认）
- 硬时间任务冲突时提示用户
- 跨设备同步延迟：<5秒

## 参考文档

详细实现细节请参见 `references/` 目录：
- `references/database-schema.md` - 数据库表结构详解
- `references/task-classification.md` - 任务分类算法
- `references/statistics-analysis.md` - 统计分析方法
- `references/ui-templates.md` - 网页清单模板
