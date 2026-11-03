---
name: claude-mem
description: 给Claude Code/Cursor等工具装"长期记忆"的Skill。自动记录每次对话的关键信息，新会话开始时自动注入相关上下文，解决每次开新会话AI就失忆的问题。GitHub: https://github.com/thedotmack/claude-mem
---

# Claude-mem Skill

## 是什么

给Claude Code/Cursor等工具装"长期记忆"的Skill，解决每次开新会话AI就失忆的问题。

自动记录每次对话的关键信息，压缩存储。新会话开始时自动注入相关上下文。

## 核心能力

- **自动记录**：每次对话的关键信息自动压缩存下来
- **三层检索机制**：索引→时间线上下文→完整细节，省token
- **本地Web界面**：跑在 localhost:37777，可视化查看记忆内容
- **隐私控制**：`<private>内容</private>` 自动跳过不记录

## 使用场景

- 长期项目，多会话协同
- 需要记住之前讨论过的决策和背景
- 不想每次重复解释项目上下文

## 来源

https://github.com/thedotmack/claude-mem
