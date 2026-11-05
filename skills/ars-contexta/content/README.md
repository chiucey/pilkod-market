# Ars-Contexta — 知识图谱管理系统

> 版本：1.0.0
> 基于 Arscontexta 理念，为 MiniMax Agent 打造的知识管理系统

---

## 核心功能

Ars-Contexta 是一个结构化的知识管理系统，采用 Zettelkasten 方法论：

- **原子化笔记**: 一条笔记 = 一个核心观点
- **Wiki 链接**: 用 [[链接]] 连接知识，形成网络
- **渐进披露**: 精准 description 引导探索
- **三空间架构**: 自我空间 / 知识空间 / 操作空间

## 快速开始

```
/init     — 初始化知识系统（首次使用）
/capture  — 快速捕获想法到 inbox
/reduce   — 处理 inbox，生成原子笔记
/graph    — 查看图谱概览
/review   — 维护图谱健康度
/remember — 持久化学会话洞见
```

## 目录结构

```
ars-contexta/
├── SKILL.md                    # 主技能文件
├── skills/
│   └── method/
│       ├── init.md             # 初始化模块
│       ├── capture.md          # 捕获模块
│       ├── reduce.md            # 提取模块
│       ├── graph.md             # 图谱模块
│       └── review.md            # 回顾模块
└── vault/
    ├── self/                   # 自我空间（慢变）
    │   ├── identity.md         # 身份定义
    │   ├── goals.md            # 长期目标
    │   └── methodology.md      # 操作方法论
    ├── notes/                  # 知识空间（稳定增长）
    │   ├── inbox/              # 原始材料
    │   ├── atomic/             # 原子笔记
    │   ├── domains/            # 领域笔记
    │   ├── mocs/               # 笔记导览
    │   └── archive/            # 归档
    └── ops/                    # 操作空间（波动）
        └── queue.md            # 任务队列
```

## 工作流程

```
/capture → inbox/
   ↓
/reduce → vault/notes/atomic/
   ↓
/graph → 建立 wiki 链接
   ↓
/review → 更新 MOC、发现孤立节点
   ↓
健康图谱
```

## 笔记 Schema

```yaml
---
title: "笔记标题"
created: "YYYY-MM-DD"
tags: [标签1, 标签2]
status: draft  # draft | review | evergreen | needs-review
description: "一句话精准描述核心观点（必填）"
---

# 标题

正文内容...

## 相关笔记
- [[关联笔记]] — 关联原因
```

## 健康评分

| 评分 | 状态 | 说明 |
|------|------|------|
| 9-10 | 🟢 优秀 | 结构健康，持续增长 |
| 7-8 | 🟡 良好 | 有改进空间 |
| 5-6 | 🟠 一般 | 需要维护 |
| <5 | 🔴 需修复 | 风险较高 |

## 命令参考

| 命令 | 功能 | 使用频率 |
|------|------|----------|
| /init | 初始化引导 | 一次 |
| /capture | 快速捕获 | 随时 |
| /reduce | 洞见提取 | inbox 有内容时 |
| /graph | 图谱概览 | 按需 |
| /review | 知识回顾 | 每周 |
| /remember | 会话持久化 | 按需 |

---

*Ars-Contexta — 让知识自己说话*
