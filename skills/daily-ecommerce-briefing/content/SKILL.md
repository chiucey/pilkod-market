---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 041170946c6f1ac178c12b034c50d559
    PropagateID: 041170946c6f1ac178c12b034c50d559
    ReservedCode1: 30440220176131e4b4de2683c0e6591e1473fa082c64ab454d59e3c1202e593a38ebff5e022005d88b89267999d67863728efe0fede9bc3a8aa8305d071f3fb73edc12857c14
    ReservedCode2: 3044022001b8167006970c86fb2eb09a78775ced4e6724c9f55948a9f5c8b2d5eecd29eb0220780f9f38ef092ed2a5c7181fd550f7027099e9a1542c2f7b8ea0c359a80cdf0b
description: 每日电商新闻简报自动化生成技能。当用户要求生成电商行业每日简报、获取电商新闻摘要、创建日报或周报、执行自动化新闻采集任务时使用。Use when users ask to generate daily e-commerce news briefings, extract news summaries, create daily/weekly reports, or execute automated news collection tasks.
name: daily-ecommerce-briefing
---

# 每日电商新闻简报生成器

## 1. 核心目标

每天上午8:40准时提供国内电商行业最重要的新闻简报，帮助用户高效掌握近两天新闻动态。核心价值在于节省信息筛选时间，提供精简高效的每日行业洞察。

## 2. 产出结构

### 四部分新闻内容

| 部分 | 名称 | 目标数量 | 说明 |
|------|------|----------|------|
| Part 1 | 流量争夺新闻 | ≥10条 | 头部互联网公司流量争夺相关新闻 |
| Part 2 | 最重要新闻 | =5条 | 精华筛选的四级标准新闻 |
| Part 3 | 重要新闻 | ≥10条 | 头部电商公司重要新闻 |
| Part 4 | 宽泛新闻 | ≥10条 | 更宽泛的头部电商行业新闻 |

### 每条新闻结构化字段

```markdown
### 新闻标题

- **信息提报时间**：YYYY-MM-DD
- **涉及业务类别**：流量/媒介/费用/内容/频道/广告/其他
- **涉及竞对**：竞争公司名称（无则填"无"）
- **资讯链接**：原始新闻URL
- **信息分类**：销售政策/运营活动/产品功能/案例分享/其他
- **分析师总结和评论**：50-100字的分析与点评
```

### 总结评论三模块结构

1. **核心趋势观察**（3-4个核心趋势及具体表现）
2. **关键数据洞察**（重要数据指标变化及行业意义）
3. **下周关注方向**（潜在热点预测和重点跟踪领域）

## 3. 信源配置与质量标准

### 信源分类体系

| 类别 | 目标占比 | 信源示例 |
|------|----------|----------|
| 扩展高质量信源 | 30-40% | 晚点、西西弗评论、未来消费、疯投圈、互联网怪盗团、见实、运营研究社、增长黑盒、乱翻书、左林右狸、极客公园、Founder Park、魔镜洞察、电商派pro、艾瑞咨询、萝卜投研、易观分析、阿里研究院等 |
| 头条系信源 | <50% | 抖音、头条等字节系平台内容 |
| 社交媒体 | ≤3% | 微博、微信等社交平台 |
| 标准信源 | 60-70% | 36氪、虎嗅、亿邦动力、证券时报、主流财经媒体等 |

### 内容质量过滤

**必须排除**：
- 口语化内容：互助、提现、赚钱、领钱、帮帮我、求求你、好爽了、拿下、活动爽、冲单奖
- 娱乐内容：演唱会、综艺、歌曲、广告推广
- 无关域名：douyin相关链接
- 非电商关键词：无电商、零售、财报、用户增长、流量、战略等关键词

**必须包含**：
- 至少一个电商行业关键词
- 近期日期（近3-4天为佳）

### Part 2 四级筛选标准

| 级别 | 标准 | 说明 |
|------|------|------|
| 一级 | 必须入选 | 巨头战略调整、重大监管政策、行业里程碑事件 |
| 二级 | 优先入选 | 头部电商平台核心业务动态、重大投资并购 |
| 三级 | 选择性入选 | 重要数据发布、行业趋势分析 |
| 四级 | 补充入选 | 其他重要新闻 |

## 4. 去重机制

### 四层去重检查

1. **URL去重**：基于文章URL主键去重
2. **标题相似性**：归一化标题相似度阈值90%
3. **跨天去重**：与数据库中近7天记录比对
4. **同一公司同一主题去重**：相似主题只保留最具深度的1条

### 状态库表结构

```sql
CREATE TABLE IF NOT EXISTS articles (
  url TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  normalized_title TEXT NOT NULL,
  source_domain TEXT NOT NULL,
  published_date TEXT NOT NULL,
  processed_date TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS execution_log (
  date TEXT PRIMARY KEY,
  high_quality_count INTEGER,
  standard_count INTEGER,
  final_count INTEGER,
  generated_at TEXT
);
```

## 5. 文件目录规则

```
/workspace/
├── outputs/电商简报/
│   ├── YYYY-MM-DD.md          # 每日简报文件
│   └── 电商简报数据库.xlsx      # 累积数据库
├── temp/                      # 临时文件
│   ├── high_quality_articles.json
│   ├── standard_articles.json
│   ├── deduped_articles.json
│   └── classified_articles.json
├── data/shared_state/
│   └── state.db               # SQLite去重数据库
└── src/                       # 脚本文件
    ├── 01_search_high_quality.py
    ├── 02_search_standard.py
    ├── 03_deduplicate.py
    ├── 04_classify.py
    ├── 05_generate_briefing.py
    └── 06_update_database.py
```

## 6. 执行流程

### 日常运行流程

1. **08:00-08:10**：执行高质量信源搜索（深度分析公众号优先）
2. **08:10-08:20**：补充标准信源搜索
3. **08:20-08:30**：执行四层去重检查
4. **08:30-08:35**：四部分分类
5. **08:35-08:40**：生成最终简报
6. **08:40前**：交付并更新数据库

### 质量验收标准

| 指标 | 目标 | 优先级 |
|------|------|--------|
| 扩展高质量信源占比 | ≥30% | 核心 |
| 头条系占比 | <50% | 核心 |
| 社交媒体占比 | ≤3% | 核心 |
| 近两天文章占比 | ≥30% | 次优 |
| 各部分数量达标 | Part1≥8, Part2=5, Part3≥8, Part4≥8 | 灵活 |
| 框架一致性 | 完整结构化字段+三模块总结 | 必须 |
| 总字数 | ≥2,000字 | 参考 |

## 7. 技术执行要点

### 搜索关键词策略

**Part 1（流量争夺）**：
- 用户增长策略、渠道拓展、内容生态建设、社交裂变、流量变现、跨界竞争
- 结合平台名称：阿里巴巴、腾讯、字节跳动、百度、美团、京东、拼多多

**Part 2-4（电商新闻）**：
- 电商平台动态、零售战略、财报分析、投资并购、行业趋势
- 结合公众号名称搜索

### 上下文管理策略

- 采用独立Python脚本处理全流程，避免对话上下文超限
- 链式执行模式，单一脚本<15,000字符
- 实时清理temp/中间文件
- 定期清理state.db超过30天的记录

### 数据库维护

```sql
-- 清理30天前记录
DELETE FROM articles WHERE date(published_date) < date('now', '-30 days');

-- 幂等写入
INSERT OR IGNORE INTO articles (url, title, normalized_title, source_domain, published_date)
VALUES (?, ?, ?, ?, ?);
```

## 8. 注意事项

1. **时效性与质量平衡**：深度分析公众号内容非每日产出，接受10-50%的高质量信源每日波动
2. **数量灵活调整**：当高质量内容不足时，适当降低数量目标但保持内容质量
3. **内容相关性第一**：必须包含电商行业关键词，排除娱乐、文化等无关内容
4. **框架一致性**：严格使用Part1/Part2/Part3/Part4标题格式，每条新闻包含完整结构化字段
