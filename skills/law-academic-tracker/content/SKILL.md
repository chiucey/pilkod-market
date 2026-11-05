---
name: law-academic-tracker
description: |
  追踪中国法学顶刊公众号每日推送，生成学术动态结构化报告。Use when the user asks to
  "追踪法学动态"、"生成学术报告"、"查看法学公众号推送"、"法学热点分析"，or when a cron
  fires at 07:00 for daily law journal digest. Do NOT use for general social media analytics
  (use social-media-insights) or non-law academic topics (use deep-research).
descriptions:
  zh-Hans: "追踪中国法学顶刊公众号每日推送，生成学术动态结构化报告，输出 Markdown + HTML 可视化面板。"
---

# Law Academic Tracker

追踪法学核心期刊公众号每日推送，生成结构化学术动态报告。

目标账号（按优先级）：
1. **法学研究**
2. **中国法学**
3. **清华法学**
4. **中国法律评论**

**重点关注学者**（按用户研究方向加权）：
- 民商法方向：王利明、孙宪忠、程啸、崔建远、高圣平、朱虎、施天涛、赵旭东、蒋大兴
- 其他方向：莫纪宏（宪法）、谢鸿飞（民法教义学）

## 每次运行的判断逻辑

```
读取 /Users/sunhan/.minimax/skills/law-academic-tracker/references/article-queue.json
  → 已有 article_count 篇

若 article_count < 15：
  → 今日新增文章追加到队列
  → 更新 article_count
  → 输出："今日收集 X 篇，当前累计 Y/15，等待下次触发生成报告"

若 article_count >= 15：
  → 进入报告生成流程（见 Procedure）
  → 生成完毕后清空队列，重置 article_count = 0
```

**原因**：15 篇足够做关键词聚类和跨学科分析；30 篇跨度过长（按日均 1-2 篇推送算需要 15-20 天），保持报告时效性。

## Inputs to collect

首次运行时需要用户确认（或 cron 上下文已有则跳过）：
- 四个公众号中哪些要纳入本次追踪（默认全部）
- 报告输出路径（默认 `~/Desktop/法学动态报告/`）

## Procedure

### 阶段一：文章采集（Browser + Web Search）

1. **获取当日文章列表**

   按 `references/data-source-fallbacks.md` 的优先级策略采集：
   - **优先**：用 Bing 站内搜索 `site:mp.weixin.qq.com "公众号名" 今日`
   - **次优**：用 Sogou 微信搜索 `https://weixin.sogou.com/weixin?query=公众号名`
   - **兜底**：直接访问各期刊官网目录（中国法学网 iolaw.cssn.cn / 中国法学会 chinalaw.org.cn / 清华法学 law.tsinghua.edu.cn / 中国法律评论官网）
   - **补充**：对重点学者进行学者名搜索，确保覆盖其最新成果

   **关键约束**：若某公众号当日 0 推送，**不要停留**，转去其他公众号或其他来源补足 15 篇阈值。

   原因：微信反爬严格，单一搜索源经常 0 命中；多源兜底是稳定产出的关键。

2. **提取文章链接和标题**

   从搜索结果中提取每篇文章的标题、链接、发布时间。
   过滤掉：广告、征稿启事、书评类短文（标题含"征稿""目录""书评"字样则排除）。

3. **读取文章内容**

   依次用 Browser 打开每篇文章，读取正文内容（提取标题、摘要、关键词/标签、正文前三段）。

   原因：获取完整正文才能做主题提取和关键词分析；只读标题不够准确。

4. **追加到文章队列**

   将当日采集到的文章写入 `references/article-queue.json`，格式：
   ```json
   {
     "articles": [
       {
         "id": "uuid",
         "account": "法学研究",
         "title": "...",
         "url": "...",
         "published_at": "2026-08-17",
         "summary": "一句话摘要",
         "keywords": ["...", "..."],
         "scholar": "作者名",
         "scholar_weight": 1.0,
         "collected_at": "2026-08-17T07:00:00+08:00"
       }
     ],
     "article_count": N,
     "last_updated": "..."
   }
   ```
   更新 `article_count` 字段。

   **学者权重规则**：
   - 重点关注学者（王利明、孙宪忠、崔建远等）`scholar_weight = 2.0`
   - 一般学者 `scholar_weight = 1.0`
   - `article_count = Σ scholar_weight`，用于阈值判断

### 阶段二：报告生成（队列累计 ≥ 15 篇时触发）

5. **读取全部文章内容**

   一次性读取 `article-queue.json` 中全部 15+ 篇的 summary 和 keywords 字段。

6. **分析学术动态**

   - **主题聚类**：将 15+ 篇文章按主题分组（如：民法典适用、物权法、合同法、商法、营商环境、数字法学等）
   - **关键词统计**：运行 `scripts/keyword-counter.js` 统计高频词，输出 Top 20
   - **交叉学科识别**：识别文章中涉及法学以外学科的术语（如经济学、社会学、心理学、环境科学、科学技术等）

7. **生成 Markdown 报告**

   输出到 `~/Desktop/法学动态报告/YYYY-MM-DD-学术动态报告-N.md`

   格式：
   ```markdown
   # 法学学术动态报告
   **统计周期**：YYYY-MM-DD ~ YYYY-MM-DD（共 X 篇）
   **数据来源**：法学研究 / 中国法学 / 清华法学 / 中国法律评论

   ## 一、本期文章列表与核心主题

   | # | 来源 | 标题 | 核心主题 | 关键词 |
   |---|------|------|----------|--------|
   | 1 | 法学研究 | ... | 民法典物权编 | 物权变动、不动产登记 |

   ## 二、学术动态分析

   ### 2.1 重点议题

   （按出现频次排列，分析每个议题的核心争论和学者观点）

   ### 2.2 高频关键词

   （Top 20 关键词 + 词云图说明）

   ### 2.3 交叉学科方向

   （识别出的跨学科议题，如法律经济学、法律社会学、数字法学等）

   ## 三、研究建议

   （基于本期动态，给出研究选题建议）

   ---
   *本报告由 Mavis 自动生成*
   ```

8. **生成 HTML 可视化面板**

   强制执行：
   ```
   node /Users/sunhan/.minimax/skills/law-academic-tracker/scripts/generate-dashboard.js \
     <报告数据JSON路径> <输出HTML路径>
   ```
   若报告数据 JSON 尚未生成，需先用队列数据构建（包含 articles、themes、topKeywords、crossDisciplines 四个数组）。

   HTML 面板必须包含：
   - 文章列表（可筛选来源公众号）
   - 关键词词频柱状图
   - 主题聚类饼图
   - 交叉学科方向列表

   原因：可视化面板比纯文本报告更直观，便于快速扫描和分享。

9. **通知用户**

   生成完毕后，向用户发送完成通知，内容：
   - 报告路径
   - 本期关键发现（3 条）
   - 可视化面板路径

10. **清空队列**

    生成报告后，将 `article-queue.json` 的 `articles` 置空，`article_count` 归零，`last_updated` 更新。

## Output contract

必须同时产出两份文件（同一目录下）：

1. **Markdown 报告**：`YYYY-MM-DD-学术动态报告-N.md`
   - 包含全部 3 个章节（文章列表、重点议题、高频关键词、交叉学科）
   - 字数：1500-3000 字

2. **HTML 可视化面板**：`YYYY-MM-DD-学术动态面板-N.html`
   - 自包含（所有 CSS/JS 内联），无需服务器，直接浏览器打开
   - 支持按公众号筛选
   - 包含至少一个图表（词频柱状图 + 主题聚类图）

## Failure handling

- **搜索结果为空**：跳过该公众号，记录 "当日未获取到文章"，继续其他账号
- **Browser 读取文章失败**（如文章被删除/需要登录）：跳过该篇，在队列中标记 `status: "failed"`，不影响计数
- **队列文件损坏**：创建新队列文件，从当天开始重新积累
- **报告生成失败**：保留已积累的文章队列，下次触发时继续使用，不重复采集

## Examples

**Trigger**: cron 每日 07:00 自动触发（第一批文章积累阶段）

Input: 今日从 4 个公众号共采集到 8 篇（含 1 篇王利明论文权重 2.0），队列累计 10/15
Output: "✅ 今日收集 8 篇（含王利明等 2 篇高权重），当前累计 10/15，还需 5 篇触发报告生成。"

**Trigger**: cron 每日 07:00 自动触发（报告生成阶段）

Input: 队列累计已达 16 篇，触发报告生成
Output: 生成 `2026-08-17-学术动态报告-1.md` 和 `2026-08-17-学术动态面板-1.html`
