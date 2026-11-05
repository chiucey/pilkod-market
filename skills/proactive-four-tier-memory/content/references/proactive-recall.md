# Proactive Recall Strategy（主动召回策略）

## 核心定位

主动召回是**默认行为**，而非被动等待用户触发。每轮对话前自动执行，像人类的联想式记忆。

## 被动检索 vs 主动召回

| 模式 | 触发方式 | 行为 |
|------|---------|------|
| 被动检索 | 用户问后触发 | 等待→检索→返回 |
| 主动召回 | 对话前默认执行 | 扫描→注入→主动提示 |

## 主动召回流程

```
对话前（默认执行，无需用户触发）
    ↓
┌─────────────────────────────────────────────────────────────┐
│  1. 实体扫描 → 用户输入中提到什么？                          │
│  2. 待办关联 → 有哪些待跟进事项与此相关？                    │
│  3. 错误预警 → 是否在重复历史上的错误？                     │
│  4. 经验关联 → 上次处理类似问题是怎么做的？                 │
│  5. 情感适配 → 用户当前情绪状态如何？                       │
└─────────────────────────────────────────────────────────────┘
    ↓
主动注入到当前上下文（不等待用户问）
```

## 实现算法

```python
def proactive_recall(user_input, all_memories):
    """主动记忆召回 — 默认行为"""
    results = []

    # 1. 实体提取
    entities = extract_entities(user_input)

    # 2. 待跟进事项检查
    for item in search_pending(all_memories):
        if item.related_to(entities):
            results.append(("followup", item, priority=0.9))

    # 3. 错误模式预警
    for pattern in search_error_patterns(user_input):
        results.append(("error_warning", pattern, priority=0.85))

    # 4. 经验关联
    for exp in search_experience(entities):
        results.append(("experience", exp, priority=0.7))

    # 5. 注入到上下文
    inject_to_context(results)

    return results
```

## 情感感知重排序

```python
def emotion_aware_rerank(results, current_emotion):
    """情感感知重排序"""

    for memory, score in results:
        if current_emotion in ["negative", "frustrated"]:
            # 负面情绪时：
            # - 提升正面记忆权重（提供安慰）
            # - 提升解决方案类记忆权重
            if memory.emotion == "positive":
                score *= 1.2
            elif memory.type == "solution":
                score *= 1.3
        elif current_emotion == "positive":
            # 正面情绪时：
            # - 可以展示更多背景信息
            if memory.type == "learning":
                score *= 1.1

    return sorted(results, key=lambda x: x[1], reverse=True)
```

## 主动召回示例

| 场景 | 被动检索（传统） | 主动召回（本技能） |
|------|-----------------|------------------|
| 用户说"部署项目" | 用户问后才知道上次部署流程 | 自动提示"检测到重复操作，是否使用之前的部署流程？" |
| 用户遇到"engine incompatible"错误 | 检索历史解决方案 | 自动预警"这个错误之前遇到过，修复方案是nvm切换版本" |
| 用户提到项目名 | 手动关联相关上下文 | 自动加载该项目所有相关记忆，包括之前遇到的问题 |
| 用户情绪低落 | 无感知 | 自动提升正面记忆权重，调整响应风格 |

## 触发时机

- **每轮对话前**：自动执行主动召回
- **新任务开始**：加载相关程序性记忆
- **检测到错误**：立即关联错误修复记忆
- **时间节点到达**：提醒待跟进事项

## 隐私保护

```python
def privacy_filter(results, context_type="general"):
    """根据隐私级别过滤主动召回结果"""

    allowed_levels = {
        "general": ["public", "internal"],
        "highly_relevant": ["public", "internal", "sensitive"],
        "explicit_request": ["public", "internal", "sensitive", "confidential"]
    }

    return [m for m in results if m.privacy_level in allowed_levels[context_type]]
```
