---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 28257353983c26e8ff6e7865418cc1e4
    PropagateID: 28257353983c26e8ff6e7865418cc1e4
    ReservedCode1: 304502203ceb6a69d599588d1d698219ac0a4fa58950177a67d2b07533ac76089520b1ba022100a3ef1a046ff8e0237cbc80185b7d001b2a10271883f9211b4060f0dc6929b387
    ReservedCode2: 3046022100f2fd362574e57eeff9520df4481e0d8eeafe9edc449f98c9ed995dc04eb0753e0221009991d9c84ac30c3714237f829a514e26bb4254851069c7ef58f6d1b118ceefdf
description: 生成长春天气+V2EX热帖每日简报。当用户说"今日简报"、"生成简报"、"每天早上8点简报"、或需要定时生成日报/早报时使用。提供详细天气预报、V2EX热门帖子、科技要闻深度分析。
name: daily-briefing
---

# 每日简报生成器

自动生成长春天气与V2EX热帖的每日简报，包含详细天气预报和科技新闻分析。

## 工作流程

### 1. 数据采集

**天气数据获取：**
- 使用 `batch_web_search` 搜索"长春天气预报 今天 明天 一周"
- 使用 `extract_content_from_websites` 获取中国天气网长春预报

**V2EX热帖获取：**
- 使用 `extract_content_from_websites` 提取：
  - https://www.v2ex.com/?tab=hot (今日热帖)
  - https://www.v2ex.com/ (最新帖子)

**科技要闻采集：**
- 使用 `batch_web_search` 搜索当日重要科技新闻

### 2. 内容整合

**天气预报部分需包含：**
- 今日详细天气（温度、天气状况、风向风力）
- 未来7天天气预报
- 重要天气提醒（降水、降温预警）

**V2EX热帖部分需包含：**
- 今日热门帖子TOP10
- 帖子标题、链接和回复数

**科技要闻部分需包含：**
- 2-5条当日重要科技/互联网新闻
- 每条新闻包含标题和简要分析

### 3. 简报展示

**部署网页展示：**
- 使用现代深色主题UI设计
- 包含天气卡片、V2EX帖子列表、科技要闻板块
- 部署到线上供用户访问

**定时任务设置：**
- 使用 `create_cron_job` 设置每天早上8点自动执行
- Cron表达式：`0 8 * * *`

### 4. 文件更新（定时任务执行时）

1. 读取现有模板 `/workspace/temp-skills/daily-briefing/dist/index.html`
2. 更新 `weatherData`、`v2exPosts`、`techNews` 对象
3. 重新写入HTML文件
4. 使用 `deploy` 重新部署

## 输出产物

- **简报网页**：部署后的可访问URL
- **定时任务**：每日8点自动更新

## 快速执行命令

当用户触发简报生成时，按顺序执行：
1. 数据采集（天气 + V2EX）
2. 内容整合
3. 网页更新
4. 部署发布
