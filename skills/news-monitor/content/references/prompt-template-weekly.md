# 周报 Prompt 模板

> 每次运行周报 Cron 任务时，复制此模板到 cron payload message 中，替换变量。

---

【自动任务】搜集过去7天的 {{INDUSTRY}} 行业资讯，生成每周汇总报告，发送至飞书群。

今天是 {{TODAY}}。

## ⏰ 时间范围

搜集范围：**今天往前推7天**，即北京时间 {{TODAY}} 减去7天，到 {{TODAY}} 零点。

举例：如果是2026年4月27日（周一），搜集范围 = 2026年4月20日 00:00 ~ 2026年4月27日 00:00

## ⏰ 第二步：RSS 源轮询

运行以下命令获取近 7 天内 RSS 源中的内容：
`python3 /workspace/skills/rss-reader/scripts/rss.js check --since 168h 2>&1`

从返回结果中筛选包含以下关键词的条目：
{{KEYWORDS}}

## ⏰ 第三步：多源并行关键词搜索

【搜索A - 通用全网】（batch_web_search，data_range: d，每项10条）
{{GENERAL_SEARCH_QUERIES}}

【搜索B - 行业媒体定向】（batch_web_search，data_range: d）
{{SITE_SEARCH_QUERIES}}

【搜索C - 微信公众号】（batch_web_search，data_range: d，每项10条）
{{WECHAT_SEARCH_QUERIES}}

## ⏰ 第四步：处理微信公众号链接

对于来自 mp.weixin.qq.com 的链接：
1. 如果微信文章无法直接访问（被拦截），记录文章标题和关键词
2. 用文章标题在第三方平台（百家号、CSDN、简书等）搜索转载
3. 找到转载页面后，用 extract_content_from_websites 抓取完整内容
4. 如果找不到转载，保留标题和关键词作为参考来源

## ⏰ 第五步：综合筛选

1. **发布时间必须在{{TODAY}}往前推7天的范围内，不允许超出**
2. 必须包含关键词之一：{{KEYWORDS}}
3. 去除重复链接，同一事件保留最权威来源
4. 按发布时间倒序

## ⏰ 第六步：整理报告

每条资讯必须包含：
- **标题**
- **发布时间**
- **来源网站**
- **原始链接**（用尖括号包裹，如 `<https://example.com>`）
- **一句话摘要**（50字以内）

报告开头格式：
📡 **{{INDUSTRY}} 行业资讯周报**
📅 过去7天（北京时间YYYY年MM月DD日 - YYYY年MM月DD日）
共收录 X 条资讯（RSS 源 + 全网搜索 + 公众号）

## ⏰ 第七步：判断推送

- 有内容：发送完整报告，按发布时间倒序列出
- 无内容：发送"📡 {{INDUSTRY}} 行业资讯周报 | 过去7天暂无更新，下周再见。"

## ⏰ 第八步：发送至飞书群

使用 message 工具：
- action: send
- channel: feishu
- target: chat:{{CHAT_ID}}
- message: 完整报告（UTF-8，Markdown格式）

【重要】所有链接必须用尖括号 `< >` 包裹，防止飞书将下划线渲染为斜体。

---

## 变量说明

| 变量 | 含义 | 示例 |
|------|------|------|
| `{{INDUSTRY}}` | 追踪的行业名称 | eSIM、物联网、芯片 |
| `{{KEYWORDS}}` | 核心关键词列表（逗号分隔） | eSIM、eUICC、eSIM手机 |
| `{{GENERAL_SEARCH_QUERIES}}` | 通用搜索查询列表 | "eSIM 最新 新闻 2026" 等 |
| `{{SITE_SEARCH_QUERIES}}` | site: 定向搜索列表 | site:caict.ac.cn eSIM 等 |
| `{{WECHAT_SEARCH_QUERIES}}` | 微信公众号搜索列表 | "联通 eSIM" site:mp.weixin.qq.com 等 |
| `{{CHAT_ID}}` | 飞书群 ID | oc_xxx |
| `{{TODAY}}` | 今日日期 | 2026年4月27日 |
