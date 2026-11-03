---
title: "操作方法论"
created: "2026-04-11"
tags: [self, methodology, principles]
status: evergreen
description: "从会话中积累的操作原则，持续演化的行为准则"
---

# 操作方法论

## 知识处理原则

1. **原子性**: 一条笔记只含一个核心观点
2. **链接优先**: 用 [[wiki链接]] 让图谱结构说话
3. **渐进披露**: description 是读者决定是否深入的唯一入口
4. **时效性**: 新知识要反向更新旧笔记
5. **无摩擦捕获**: 想法先进 inbox，不追求完美

## 从会话中学习

<!-- /remember 会将新发现的原则自动追加到此处 -->
<!-- 格式: - YYYY-MM-DD: [原则]（来源: [任务/对话]） -->

## 命令使用规范

| 命令 | 触发条件 | 输出位置 |
|------|----------|----------|
| /capture | 任何想法出现 | inbox/ |
| /reduce | inbox 有内容 | atomic/ |
| /graph | 需要了解状态 | 终端输出 |
| /review | 每周定期 | 终端输出 |
| /remember | 发现新洞见 | methodology.md |

## 质量门禁

### 发布前检查
- [ ] description 精准概括核心观点
- [ ] 至少有 1 条 wiki 链接
- [ ] tags 准确分类
- [ ] status 与内容匹配

### 图谱健康阈值
- 连接率 < 50%: 触发警告
- 孤立节点 > 10%: 需要 review
- inbox > 10 条: 需要 reduce
