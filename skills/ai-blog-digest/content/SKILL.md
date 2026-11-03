---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 43f8d5d8ec26c635a0b13aee10c1bdde
    PropagateID: 43f8d5d8ec26c635a0b13aee10c1bdde
    ReservedCode1: 3045022100d3cc4199ec9790475161f929dbf80f7b5ea55a90fba9a32be13a0687d9e95a290220094918885f613033a80650832e0d74b07727d3eeb75e0e467bc8930cd8747271
    ReservedCode2: 304502205aa2c06a6d54a1f66a3ab63dfbe8bd0141787c83b2c2cd7e0178aac3d980980702210098607c72eb57d28564a1a7f17f39ab520e2cd9cf37ddb8c84acc99a3abc4a14b
description: 监控AI前沿公司博客并生成内容摘要。当用户要求生成AI资讯日报/周报、获取AI行业动态、整理AI博客更新、订阅AI资讯、查看AI领域最新进展、整理OpenAI/Anthropic/Google/DeepMind/Meta/NVIDIA博客更新时使用。
name: ai-blog-digest
---

# AI 前沿公司博客内容摘要

## 工作流程

### 1. 确定时间范围
- **日报**: 过去24小时内更新
- **周报**: 过去7天内更新（默认）
- **自定义**: 根据用户指定日期范围

### 2. 抓取博客列表

使用 `extract_content_from_websites` 工具并行抓取以下博客列表页：

| 公司 | 博客 URL | 列表页选择策略 |
|------|----------|----------------|
| OpenAI | https://openai.com/blog | 首页最新文章列表 |
| Anthropic | https://www.anthropic.com/news | 消息/新闻列表页 |
| Google AI | https://blog.google/technology/ai/ | AI专栏 |
| DeepMind | https://deepmind.google/discover/blog/ | 博客列表页 |
| Meta Engineering | https://engineering.fb.com | 工程博客 |
| NVIDIA | https://blogs.nvidia.com | 官方博客 |

### 3. 提取文章信息

对于每个博客，提取以下信息：
- **标题** (Title)
- **发布日期** (Date)
- **链接** (URL)
- **摘要/预览** (Summary/Excerpt)
- **分类标签** (Category Tags)

### 4. 过滤与排序

- 按发布日期降序排列（最新在前）
- 过滤掉非文章内容（导航、公告等）
- 按公司分类整理

### 5. 生成摘要报告

输出格式：

```
# AI 前沿公司博客更新摘要

**时间范围**: [日期范围]
**生成时间**: [时间戳]

## 📊 统计概览
- 总文章数: X 篇
- 涉及公司: X 家

## 📝 按公司分类

### OpenAI (X 篇)
| 标题 | 日期 | 摘要 |
|------|------|------|
| [文章1] | [日期] | [摘要] |
| ... | ... | ... |

### Anthropic (X 篇)
...

### Google AI (X 篇)
...

### DeepMind (X 篇)
...

### Meta Engineering (X 篇)
...

### NVIDIA (X 篇)
...

---
来源: 各公司官方博客 | 生成时间: [时间]
```

## 输出选项

- **Markdown格式**: 直接在对话中显示（默认）
- **文件保存**: 保存到 `extract/ai-blog-digest-YYYY-MM-DD.md`
- **定时任务**: 配置 cron job 定期生成并推送

## 触发短语

- "生成AI博客日报"
- "生成AI博客周报"
- "查看AI公司最新博客"
- "AI资讯周报"
- "整理AI博客更新"
- "订阅AI博客"
- "获取OpenAI/Anthropic/Google/DeepMind/Meta/NVIDIA最新文章"

## 注意事项

1. **并行抓取**: 使用批量工具同时抓取多个博客，提高效率
2. **内容清洗**: 使用 `smart-web-fetch` 技能优化HTML转Markdown
3. **错误处理**: 单个博客失败不影响其他博客的抓取
4. **去重**: 同一文章在不同来源出现时合并展示
