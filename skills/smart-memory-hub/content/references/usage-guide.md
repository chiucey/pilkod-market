# Smart Memory Hub - 智能记忆管家参考文档

## 概述

Smart Memory Hub 是一款专为解决 AI 记忆问题而设计的技能。与传统记忆系统不同，它同时满足两个核心需求：
1. **可靠的长期记忆能力**
2. **严格的防膨胀机制**

## 核心架构

### 防膨胀约束

| 参数 | 值 | 说明 |
|------|-----|------|
| `MAX_ENTRIES` | 200 | 记忆库最大条目数 |
| `MAX_CHARS_PER_ENTRY` | 200 | 单条记忆最大字符数 |
| `INJECT_LIMIT` | 5 | 每次注入 prompt 的最大条数 |
| `CLEANUP_THRESHOLD` | 180 | 自动清理阈值 |
| `TIMEOUT_MS` | 1000 | 检索超时阈值（毫秒） |
| `CLEANUP_INTERVAL` | 10 | 自动清理检查间隔（轮次） |

### 存储结构

```json
{
  "max_entries": 200,
  "version": "1.0.0",
  "last_cleanup": "2025-01-01T00:00:00Z",
  "degraded_mode": false,
  "entries": [...],
  "compressed_cache": "..."
}
```

### 重要性评分

系统根据以下规则自动计算重要性分数（0-100）：

| 规则 | 加分 |
|------|------|
| 用户明确说"记住" | +30 |
| 信息重复出现 | +10/次 |
| 包含姓名信息 | +25 |
| 包含项目/代号 | +20 |
| 包含待办事项 | +20 |
| 包含联系方式 | +15 |
| 包含偏好设置 | +15 |

## 执行流程

### 启动流程

```
1. 读取 memory.json
2. 加载记忆索引（轻量，不全量加载到上下文）
3. 检查 degraded_mode 状态
4. 清理过期记忆
```

### 用户输入处理

```
1. 检查管理命令 (/remember, /recall 等)
2. 增加对话轮次计数
3. 自动捕获新信息
4. 检索相关记忆（最多 5 条）
5. 验证检索时间 < 1s
6. 格式化为 [记忆] 内容 注入上下文
7. 更新 last_used 时间戳
```

### 自动维护

每 10 轮对话后执行：
1. 检查条目数 ≥ 180？
2. 若是，删除 last_used 最早的 20 条（importance > 90 除外）
3. 若条目数 = 200，强制合并最旧 10 条

## 管理命令详解

### /remember <内容>

**功能**：强制保存一条记忆

**示例**：
```
/remember 用户叫张三，喜欢简洁的回答
/remember 我的项目代号是"天鹰"
```

**行为**：
- 自动计算重要性（基础 50 + 明确记住 +30）
- 检查存储是否已满
- 若已满，触发压缩后再保存

---

### /recall <关键词>

**功能**：检索匹配的记忆列表

**示例**：
```
/recall 项目名称
/recall 偏好
```

**行为**：
- 关键词匹配 + 内容匹配
- 返回最多 10 条
- 不修改上下文，不更新 last_used

---

### /memory_stats

**功能**：显示当前统计信息

**输出示例**：
```
📊 记忆统计：

• 当前条目: 45 / 200
• 总字符数: 3240
• 平均每条: 72 字符

重要性分布：
  - 高 (>70): 15
  - 中 (40-70): 25
  - 低 (<40): 5

• 降级模式: 否 ✅
• 最后清理: 2025-01-01

高频关键词：
  - 项目: 8次
  - 姓名: 5次
```

---

### /clear_memory

**功能**：清空所有记忆

**行为**：
- 首次调用：提示二次确认
- 二次确认 (`/clear_memory confirm`)：真正清空
- 保留 degraded_mode 和 last_cleanup 状态

---

### /compact_memory

**功能**：手动触发压缩合并

**行为**：
- 将最旧的 10 条合并为 1 条压缩摘要
- 创建备份文件
- 更新 compressed_cache

## 降级机制

### 触发条件

1. **I/O 错误**：文件读取/写入失败
2. **检索超时**：> 1000ms
3. **文件过大**：> 5MB

### 降级行为

```
1. 设置 degraded_mode = true
2. 本次会话不再读写记忆
3. 返回提示："[记忆系统暂不可用]"
```

### 恢复

- 用户手动调用 `/clear_memory confirm` 后自动恢复
- 或等待下次会话重新初始化

## 数据存储

**目录**：`~/.openclaw/smart_memory/`

**文件**：
- `memory.json` - 主存储
- `memory_backup.json` - 压缩前备份
- `memory.log` - 操作日志

## 与 OpenClaw 集成

### 插件加载

```python
from memory_engine import SmartMemoryHubPlugin

# 初始化
memory_plugin = SmartMemoryHubPlugin()

# 注册钩子
on_user_message = memory_plugin.on_user_message
```

### 钩子接口

| 钩子 | 时机 | 返回值 |
|------|------|--------|
| `on_user_message` | 用户消息到达 | 记忆注入文本 或 空字符串 |

### 完整集成示例

```python
class MyOpenClawPlugin:
    def __init__(self):
        self.memory = SmartMemoryHubPlugin()

    def on_message(self, user_input: str) -> str:
        # 1. 获取记忆注入
        memory_context = self.memory.on_user_message(user_input)

        # 2. 构建完整 prompt
        full_prompt = f"{memory_context}\n\n用户: {user_input}"

        # 3. 调用 LLM
        response = llm.generate(full_prompt)

        # 4. 可选：从回复中捕获新记忆
        # self.memory.on_bot_reply(response)

        return response
```

## 测试用例

### 记忆保持测试

1. 会话 A：用户说"我叫李四"
2. 重启 OpenClaw
3. 会话 B：用户问"我叫什么？" → 应回答"李四"

### 防堵塞测试

1. 快速写入 210 条模拟记忆
2. 观察自动合并/淘汰
3. 会话不应中断

### 降级测试

1. 手动修改 `memory.json` 为超大文件
2. 触发检索
3. 应出现降级提示

## 版本历史

- **1.0.0** (2025-04-28): 初始版本
  - 支持可靠的长期记忆
  - 实现严格的防膨胀约束
  - 包含完整的降级机制
