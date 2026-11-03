---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: e09b996584546c4bdb87c3d9d10100f2
    PropagateID: e09b996584546c4bdb87c3d9d10100f2
    ReservedCode1: 3045022100cc20a9f26edbc980a1bb6da8056540ba20c8659640e06f202564c1336d596a6b02205ddd231fcdb23d7e3782330919a7f3dde6a2f29c296e57faf1dcbfa1c00b9031
    ReservedCode2: 304402207783ed42a08d66daa9350ee710a124597b7043ecbc2cfe714560e6cc13a204e702200b064dbd93c66dd0a77c7236423e642000121d4645a239024007f89ca03b30dd
description: 自定义行业新闻追踪技能。支持用户配置任意行业的关键词、RSS源、行业媒体和微信公众号，自动生成每日/每周资讯报告并推送至飞书群。触发词：创建新闻追踪任务、配置新闻关键词、添加新闻来源、监控XX行业新闻、设置每日新闻推送、自定义行业资讯。
name: news-monitor
---

# News Monitor（自定义行业新闻追踪）

## 功能概述

自动化追踪任意行业的每日/每周资讯。支持自定义关键词、RSS 源、行业媒体、微信公众号等多信源聚合，自动去重、生成报告并推送至飞书群。

## 触发词

- "创建新闻追踪任务"
- "配置新闻关键词"
- "添加新闻来源"
- "帮我监控XX行业的新闻"
- "设置每日新闻推送"
- "自定义行业资讯"

## 配置文件结构

所有可配置项集中在 `references/config.md`，包含三大模块：

- **关键词列表**（必填）：追踪的核心词 + 行业变体词
- **RSS 源列表**（可选）：行业博客/新闻网站 RSS 地址
- **行业媒体列表**（可选）：site:xxx.com 定向搜索域名列表

## 输出规范

所有推送使用 Markdown 格式，链接统一用 `<URL>` 包裹：

```
📡 行业资讯日报
📅 YYYYMMDD
共收录 X 条

---
标题
🗓 日期 | 来源
<链接>
📝 摘要
```

## 使用流程

### 首次配置

用户说"创建新闻追踪任务"：

**第一步**：确认追踪行业和核心关键词
**第二步**：写入 `references/config.md`
**第三步**：创建日报 + 周报 Cron 任务（参考 prompt 模板）

### 修改配置

读取 `references/config.md`，修改对应字段即可。

### 手动触发

直接运行对应 Cron 任务，或说"立即推送今天的新闻"。

---

> 技能文件结构：
> - `references/config.md` — 用户可自定义的配置文件
> - `references/prompt-template-daily.md` — 日报 Prompt 模板
> - `references/prompt-template-weekly.md` — 周报 Prompt 模板
