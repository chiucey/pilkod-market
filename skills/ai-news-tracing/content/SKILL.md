---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: cef6e5fdf623b151fd862921658b6f96
    PropagateID: cef6e5fdf623b151fd862921658b6f96
    ReservedCode1: 3045022100ad37effbe8641bc0ef9e7030d86e650fad05edfdbf7a63a7bc2beaac1e7debff0220500f178440e6edbc0c1310ed275982b8d875dc0701b2f3fa5865af96c1deb527
    ReservedCode2: 30460221009c788ef5a09bd98df0a6dce07203c8daf3c06f5b3bc227b9e5ca211935ec540b022100f3693e0b31da765406ab1939e978d0d6b79f3e82f2ca15084c43c5c0a043857c
description: Track and analyze the latest AI news from various sources. Use when users ask about AI news, latest AI developments, AI model releases, AI research papers, AI company updates, or want to stay updated on artificial intelligence trends.
name: ai-news-tracing
---

# AI News Tracing Skill

## 1. 技能概述

这是一个 AI 新闻追踪技能，能够从多个权威来源获取、整理和展示最新的人工智能新闻。支持按类别、来源和时间范围进行筛选，并提供 Markdown 和 JSON 两种输出格式。

## 2. 触发条件

**使用此技能当用户：**
- 请求获取 AI 新闻或最新动态
- 询问特定 AI 模型（如 GPT、Claude、Gemini 等）的最新消息
- 需要追踪 AI 领域的学术研究或论文
- 想要了解 AI 公司的最新动态（融资、合作、产品发布等）
- 要求生成 AI 行业报告或新闻摘要
- 指定了特定的时间范围或新闻来源

**不使用此技能当：**
- 用户请求与 AI 完全无关的话题
- 用户需要代码编写、文档处理等其他帮助
- 用户询问的是一般性技术问题而非新闻

## 3. 核心原则

1. **时效性优先**：优先展示最新新闻
2. **信息来源可靠**：使用官方博客、科技媒体、学术平台
3. **分类清晰**：按模型、研究、产品、公司四大类别组织
4. **多格式支持**：支持 Markdown 和 JSON 输出
5. **上下文提供**：必要时添加背景说明和分析

## 4. 工作流程

### 4.1 接收用户请求

解析用户需求，确定：
- 时间范围：今日、最近 N 天、指定日期
- 新闻类别：模型、研究、产品、公司、全部
- 信息来源：TechCrunch、The Verge、arXiv 等
- 输出格式：Markdown（默认）或 JSON

### 4.2 获取新闻

使用网络搜索工具从以下来源获取信息：

| 来源 | 类型 | URL | 优先级 |
|------|------|-----|--------|
| TechCrunch | 科技新闻 | https://techcrunch.com/category/artificial-intelligence/ | 高 |
| The Verge | 技术报道 | https://www.theverge.com/ai | 高 |
| arXiv | 学术论文 | https://arxiv.org/list/cs.AI/recent | 高 |
| VentureBeat | 行业新闻 | https://venturebeat.com/category/artificial-intelligence/ | 中 |
| Hugging Face | 社区动态 | https://huggingface.co/news | 中 |
| MIT Tech Review | 深度分析 | https://www.technologyreview.com/topic/artificial-intelligence/ | 中 |

### 4.3 筛选和整理

1. **去重处理**：移除重复的新闻条目
2. **时间过滤**：按用户指定的时间范围筛选
3. **类别分类**：将新闻分配到对应类别
4. **相关性排序**：按重要性和相关性排序

### 4.4 生成报告

按标准格式输出新闻报告，包含：
- 新闻标题和来源
- 发布时间
- 内容摘要
- 相关链接
- 统计数据

## 5. 新闻分类

### 5.1 AI 模型 (Models)

- 新模型发布和版本更新
- 模型基准测试结果
- 开源模型发布
- API 更新和功能增强

### 5.2 AI 研究 (Research)

- 学术论文和研究成果
- 算法创新和方法论
- 研究趋势分析
- 预印本平台动态（arXiv）

### 5.3 AI 产品 (Products)

- AI 驱动的新产品发布
- 平台和工具更新
- 企业 AI 解决方案
- 消费者 AI 应用

### 5.4 AI 公司 (Companies)

- 公司融资和并购
- 战略合作和伙伴关系
- 高管动态和组织变化
- 财报和业绩报告

## 6. 命令参数

### 时间参数

| 参数 | 说明 | 示例 |
|------|------|------|
| --today | 只获取今日新闻 | `/ai-news --today` |
| --days N | 获取最近 N 天新闻 | `/ai-news --days 7` |
| --date YYYY-MM-DD | 获取指定日期新闻 | `/ai-news --date 2026-04-10` |

### 类别参数

| 参数 | 说明 | 示例 |
|------|------|------|
| --category models | AI 模型新闻 | `/ai-news --category models` |
| --category research | AI 研究新闻 | `/ai-news --category research` |
| --category products | AI 产品新闻 | `/ai-news --category products` |
| --category companies | AI 公司新闻 | `/ai-news --category companies` |
| --category all | 所有类别（默认） | `/ai-news --category all` |

### 来源参数

| 参数 | 说明 | 示例 |
|------|------|------|
| --source techcrunch | TechCrunch | `/ai-news --source techcrunch` |
| --source arxiv | arXiv | `/ai-news --source arxiv` |
| --source 多个来源 | 逗号分隔 | `/ai-news --source techcrunch,verge` |

### 输出参数

| 参数 | 说明 | 示例 |
|------|------|------|
| --format markdown | Markdown 格式（默认） | `/ai-news --format markdown` |
| --format json | JSON 格式 | `/ai-news --format json` |
| --save | 保存到文件 | `/ai-news --save` |

## 7. 输出格式

### 7.1 Markdown 格式（默认）

```markdown
# AI 新闻追踪报告 - [日期]

## AI 模型

1. **[新闻标题]**
   - **来源**: [来源名称]
   - **时间**: [发布时间]
   - **摘要**: [新闻摘要]
   - **链接**: [URL]

## AI 研究

[类似结构...]

---
**统计**: 共 N 条新闻 | 来源: [来源列表] | 类别: [类别列表]
```

### 7.2 JSON 格式

```json
{
  "status": "success",
  "timestamp": "2026-04-12T16:00:00Z",
  "total_items": 15,
  "date_range": {
    "start": "2026-04-11",
    "end": "2026-04-12"
  },
  "categories": {
    "models": [
      {
        "title": "新闻标题",
        "source": "来源",
        "time": "2026-04-12T10:00:00Z",
        "summary": "摘要内容",
        "link": "https://..."
      }
    ],
    "research": [],
    "products": [],
    "companies": []
  },
  "sources_used": ["techcrunch", "verge", "arxiv"],
  "trending_topics": ["GPT-5", "Claude-4", "Llama-4"]
}
```

## 8. 使用示例

### 示例 1: 获取今日 AI 新闻

**输入**: "获取今天的 AI 新闻"

**处理**: 使用 `batch_web_search` 搜索今日 AI 新闻，整理后输出

**输出**:
```
# AI 新闻追踪报告 - 2026-04-12

## AI 模型

1. **[新闻标题]** - OpenAI
   - 来源: OpenAI Blog
   - 时间: 2026-04-12 09:30
   - 摘要: [摘要内容]
   - 链接: https://...

## AI 研究

1. **[论文标题]** - arXiv
   - 来源: arXiv.org
   - 时间: 2026-04-12 14:20
   - 摘要: [摘要内容]
   - 链接: https://arxiv.org/abs/...

---
**统计**: 共 8 条新闻
```

### 示例 2: 按类别筛选

**输入**: "查看最近一周的 AI 模型新闻"

**处理**:
1. 搜索 "AI model release news 2026"
2. 搜索 "GPT Claude Gemini latest 2026"
3. 筛选时间范围为最近 7 天
4. 过滤只保留模型相关类别

### 示例 3: 按来源筛选

**输入**: "从 TechCrunch 获取 AI 产品新闻"

**处理**:
1. 访问 TechCrunch AI 分类页面
2. 提取产品相关报道
3. 整理后输出

### 示例 4: 生成 JSON 格式报告

**输入**: "以 JSON 格式给我最近一个月的 AI 研究论文"

**处理**:
1. 搜索 arXiv 最新 AI 论文
2. 筛选研究类别
3. 时间范围设为 30 天
4. 输出 JSON 格式

### 示例 5: 综合搜索

**输入**: "过去 7 天 OpenAI、Anthropic 和 Google 的 AI 新闻"

**处理**:
1. 分别搜索三家公司最新动态
2. 合并并去重
3. 按时间排序
4. 输出综合报告

## 9. 搜索策略

### 9.1 关键词组合

| 类型 | 关键词示例 |
|------|-----------|
| 模型发布 | "GPT-5 release", "Claude 4 announced", "Gemini Ultra" |
| 研究论文 | "AI research paper 2026", "arXiv machine learning" |
| 产品更新 | "ChatGPT update", "AI product launch", "Claude API" |
| 公司新闻 | "OpenAI funding", "Anthropic partnership", "AI startup" |

### 9.2 时间敏感搜索

使用日期参数增强搜索：
- 今日: 添加 "today" 或 "April 12 2026"
- 本周: 添加 "this week" 或日期范围
- 本月: 添加 "April 2026" 或 "recent weeks"

### 9.3 来源指定

在搜索时指定来源：
- "site:techcrunch.com AI news"
- "site:theverge.com artificial intelligence"
- "site:arxiv.org cs.AI"

## 10. 注意事项

### 10.1 网络依赖

- 技能依赖网络搜索获取最新新闻
- 确保网络连接正常
- 部分来源可能需要处理反爬虫机制

### 10.2 信息时效性

- 新闻同步可能存在延迟
- 对于实时性要求高的场景，建议直接访问来源网站
- 历史新闻可能受来源保留策略影响

### 10.3 版权和引用

- 新闻内容仅用于信息分享
- 引用新闻时请标注来源
- 遵守各来源的使用条款

## 11. 故障排除

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 无搜索结果 | 关键词不准确 | 尝试更通用的搜索词 |
| 结果过少 | 时间范围过窄 | 扩大时间范围或来源 |
| 内容重复 | 多源重复报道 | 使用去重功能 |
| 格式异常 | 输出参数错误 | 检查参数格式 |

## 12. 性能优化

1. **日常使用**：使用 `--today` 获取最相关新闻
2. **深度研究**：使用 `--days 30 --category research` 获取更多论文
3. **竞品分析**：组合使用 `--source` 和 `--category companies`
4. **数据存档**：使用 `--format json` 便于程序处理

## 13. 版本历史

**v1.0.0** (2026-04-12)
- 初始版本发布
- 支持 4 个新闻类别
- 整合 6 个新闻来源
- Markdown 和 JSON 输出格式
- 时间、类别、来源三重过滤
