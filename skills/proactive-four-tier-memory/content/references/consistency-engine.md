# Consistency Engine（一致性校验引擎）

## 核心定位

一致性校验是记忆系统的**心脏**，而非附属功能。每次记忆操作前必检，防止记忆越积越错。

## 为什么必须是心脏

```
传统设计：
记忆系统 → 记忆越来越多 → 矛盾累积 → 记忆失效
              ↑
        缺少一致性校验

本技能设计：
每次操作 → 一致性校验 → 通过才写入 → 记忆持续有效
                ↑
          系统心脏
```

## 校验维度

| 校验类型 | 检查内容 | 处理策略 |
|---------|---------|---------|
| Semantic内部 | 同一偏好有两个矛盾值 | 自动采用最新的，标记旧值为superseded |
| Episodic-Semantic | 事件与长期知识矛盾 | 检测趋势，≥3次冲突才触发更新 |
| Procedural有效性 | 流程成功率<50%且使用≥3次 | 标记deprecated或更新 |
| 情感基线 | 用户情绪分布漂移>30% | 监控，7天后确认才更新 |

## 校验流程

```python
def consistency_check():
    """记忆一致性校验 — 系统心脏"""
    issues = []

    # 1. Semantic 内部一致性
    for pair in find_contradictions(semantic_memories):
        issues.append(f"语义矛盾: {pair[0].key} vs {pair[1].key}")

    # 2. Episodic-Semantic 一致性
    for event in recent_episodic:
        if event.contradicts(semantic):
            issues.append(f"事件与知识矛盾: {event.id}")

    # 3. Procedural 有效性
    for proc in procedural_memories:
        if proc.success_rate < 0.5 and proc.usage_count > 3:
            issues.append(f"低效流程: {proc.name}")

    # 4. 情感基线漂移
    if emotion_drift_detected():
        issues.append("情感基线漂移")

    return issues  # 有issues则阻塞写入
```

## 矛盾处理协议

| 优先级 | 矛盾类型 | 处理方式 | 时效 |
|-------|---------|---------|------|
| P0 | 安全相关矛盾 | 立即修复 | 即时 |
| P1 | 用户偏好矛盾 | 下次会话确认 | 24h内 |
| P2 | 事实知识矛盾 | 自动采用最新的 | 即时 |
| P3 | 情感基线漂移 | 累积确认后更新 | 7天 |
| P4 | Procedural过时 | 标记归档 | 下次使用时 |

## 确认Prompt

```
检测到记忆矛盾，需要确认：

关于「{key}」：
- 之前记录：{old_value}（来源：{source}，时间：{date}）
- 新的信息：{new_value}（来源：{source}，时间：{date}）

请确认哪个是正确的，或者两者都是（我会合并记录）。
```

## 一致性报告格式

```json
{
  "check_time": "2026-03-26T23:59:59+08:00",
  "overall_score": 0.97,
  "checks": {
    "semantic_internal": {"score": 1.0, "issues": []},
    "episodic_semantic": {"score": 0.95, "issues": [...]},
    "procedural_validity": {"score": 1.0, "issues": []},
    "emotion_baseline": {"score": 0.93, "issues": [...]}
  },
  "pending_confirmations": [],
  "auto_resolved": [...]
}
```
