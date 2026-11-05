---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: b364999d408c8dcb25921164041fc2a1
    PropagateID: b364999d408c8dcb25921164041fc2a1
    ReservedCode1: 304402206a35111f62c4285c4b04c46c7816861e89720acf60c633c5bf62349fca14d7b202204c70c4b0fcc3263497869460095b33f69d73a664e747bf76286e314730e00e3e
    ReservedCode2: 3045022100c67f3a7c77fc9ed66bf883b7008f91544c54183fe296ab157800e79e553a36f3022012a75d9db7eb712670f5fd0022f9ae3971c0226adde5df29b3e672796debcbfc
description: Daily news morning post skill with trending hot searches, weather info, and AI news. Use when users ask for morning news, daily briefing, today's hot topics, tech news, "/morning", "/早报", or request generating daily news summary. Supports automatic weather info based on user IP location.
name: daily-morning-post
---

# Daily Morning Post

每日新闻早报生成技能，自动获取当日热搜新闻、科技动态、AI资讯、GitHub热门，并为用户提供基于IP定位的当地天气信息。

## 执行流程

### Step 1 - 获取日期和用户位置

1. 获取当前日期，格式化为 `YYYY-MM-DD`
2. 获取当前时间（包含星期信息）
3. 获取用户位置信息（通过IP定位获取城市，用于天气查询）

### Step 2 - 获取当地天气

使用 `mcp__matrix__batch_web_search` 查询用户IP定位城市的天气：

- 搜索查询：`今日天气 {城市名}` 或 `weather {城市名} today`

从搜索结果中提取：
- 当前温度
- 天气状况（晴/雨/多云等）
- 空气质量
- 穿衣建议（可选）

### Step 3 - 并行搜索新闻

使用 `mcp__matrix__batch_web_search` 并行发起以下6个维度的搜索：

1. **热搜新闻**: `微博热搜 今日` / `知乎热榜 今天` / `抖音热搜 今日`
2. **科技/编程**: `tech news today 2026` / `科技新闻 今天`
3. **AI/大模型**: `AI LLM news today 2026` / `人工智能 大模型 最新动态`
4. **GitHub Trending**: `GitHub trending today`
5. **国内外时事**: `world news today` / `国内外重要新闻 今天`
6. **财经/商业**: `business finance news today` / `财经新闻 今天`

### Step 4 - 汇总输出

按以下模板格式化为中文早报：

## 输出模板

```markdown
# 🌅 每日早报 | {日期} {星期}

{问候语}！现在是 {时间}，{城市名}今日天气 {温度} {天气状况}，来看看今日资讯~

---

## 🌤️ 今日天气 ({城市名})

- **温度**: {温度}
- **天气**: {天气状况}
- **建议**: {出行/穿衣建议}

---

## 🔥 热搜速览

1. **标题** - 热度指数 / 平台来源
2. **标题** - 热度指数 / 平台来源
3. **标题** - 热度指数 / 平台来源
4. **标题** - 热度指数 / 平台来源
5. **标题** - 热度指数 / 平台来源

---

## 🚀 科技前沿

1. **标题** - 一句话摘要
2. **标题** - 一句话摘要
3. **标题** - 一句话摘要

---

## 🤖 AI & 大模型

1. **标题** - 一句话摘要
2. **标题** - 一句话摘要
3. **标题** - 一句话摘要

---

## 💻 GitHub 热门

1. **仓库名** - 简介 + star趋势
2. **仓库名** - 简介 + star趋势
3. **仓库名** - 简介 + star趋势

---

## 📰 时事要闻

1. **标题** - 一句话摘要
2. **标题** - 一句话摘要
3. **标题** - 一句话摘要

---

## 💹 财经速递

1. **标题** - 一句话摘要
2. **标题** - 一句话摘要
3. **标题** - 一句话摘要

---

## ✨ 每日一言

> 每日一言/名言

*来源: 各新闻平台 | 天气数据来自网络*
```

## 热搜来源优先级

| 优先级 | 平台 | 说明 |
|--------|------|------|
| 1 | 微博热搜 | 国内最具影响力的社交媒体热搜榜 |
| 2 | 知乎热榜 | 深度讨论和知识类热点 |
| 3 | 抖音/快手热搜 | 短视频平台热点 |
| 4 | 百度/搜狗热搜 | 搜索引擎热点趋势 |
| 5 | 头条/腾讯热搜 | 资讯平台热点 |

## 关键设计决策

| 决策 | 说明 |
|------|------|
| **天气优先** | 早报开头展示用户所在城市天气，增强实用性 |
| **并行搜索** | 单次响应中并行发起多个WebSearch调用，提升响应速度 |
| **中文输出** | 所有内容翻译/组织为中文，符合用户习惯 |
| **简洁控制** | 每个板块控制在3-5条，保持信息密度适中 |
| **热搜优先** | 热搜板块放在最前面，满足用户即时热点需求 |

## 触发示例

- "帮我看看今天的新闻"
- "早报"
- "/morning"
- "生成今日资讯"
- "最新科技动态"
- "热搜新闻"
- "今天有什么热点"
- "今天天气怎么样"
- "生成早报"
