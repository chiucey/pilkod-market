---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 504dbe4e629ebb087b2f63dd5278aabf
    PropagateID: 504dbe4e629ebb087b2f63dd5278aabf
    ReservedCode1: 3045022100f1c9b00a0c10ac3971d683caa1391ebd8cb8317754ac71daad791483f0b884c2022037be92dbb3c85ff754d1e162ab701c3403ce5f16f223031ea1b0ef9ea4277cf4
    ReservedCode2: 3045022100ffd0c3dd8a31d2d5d4905a2b23188073d476daf670416702e5abfb26d94fdbaa022007d5b4e814f02fbab94224c29530a4ad58d033fe4c1a83d4b3847cbef76fd7b3
---

# AI信号追踪器 - 详细参考指南

## Signal类型详解

### 模型层（Model Signals）

#### 追踪什么
- 新模型发布 / 版本更新
- API能力变化（function calling, memory, planning, video I/O）
- 成本变化、latency变化
- 什么能力开始可产品化

#### 信息源优先级

**P0 - 官方源（必须）**
```
海外:
- OpenAI Blog: https://openai.com/blog
- Anthropic News: https://www.anthropic.com/news
- Google AI Blog: https://blog.google/technology/ai/

国内:
- DeepSeek: https://www.deepseek.com
- Qwen: https://qwenlm.github.io
- MiniMax: https://www.minimaxi.com
- Kling: https://kling.kuaishou.com
```

**P1 - 模型社区**
```
- HuggingFace Trending: https://huggingface.co/models?sort=trending
- LMSYS Arena: https://chat.lmsys.org/?leaderboard
- Github Trending (agent/multimodal/video标签)
```

#### 关注指标
- context长度变化
- multimodal能力（图像、视频理解）
- realtime能力
- tool use进化
- video generation

---

### 产品层（Product Signals）

#### 追踪什么
- workflow变化
- Agent能力提升
- UI范式变化
- AI开始替代创作链路中的哪一步

#### 核心观察点

**1. 用户链路变化（最高优先级）**
```
输入方式变化: 文字 → 图片 → 语音 → 视频片段
输出方式变化: 单图 → 多图 → 视频 → 动态内容
是否减少人工步骤
是否改变创作顺序
```

**2. Agent能力变化**
```
planning（任务规划）
auto-editing（自动剪辑）
multi-step execution（多步执行）
autonomous generation（自主生成）
```

**3. UI范式变化**
```
Chat（对话式）
Timeline（时间线）
Canvas（画布）
Workspace（工作空间）
Autonomous flow（自主流程）
```

#### 信息源

**P0 - Twitter/X（最高价值）**
```
重点关注:
- 创始人账号（Sam Altman, Dario Amodei等）
- PM账号（产品经理分享）
- AI power users（深度用户workflow分享）
- workflow分享帖

搜索标签:
#AItool #workflow #ChatGPT #Claude #AIproduct
```

**P0 - Reddit**
```
推荐:
- r/ChatGPT
- r/LocalLLaMA
- r/ArtificialIntelligence
- r/singularity

重点看:
- 用户真实反馈
- workflow变化
- 吐槽与留存问题
```

**P1 - YouTube**
```
- 产品试玩视频
- workflow demo
- 长视频实测（真实使用场景）
```

**P1 - 国内平台**
```
- B站（AI工具测评、创作教程）
- 小红书（AI产品分享、prompt技巧）
```

---

### 用户层（Behavior Signals）

#### 最重要但最容易缺失的一层

#### 追踪什么

**1. 新workflow出现**
```
AI自动切shorts
AI生成B-roll
AI辅助脚本写作
AI配音/翻译
AI内容总结
```

**2. 用户开始稳定复用**
```
不是尝鲜，而是真正纳入生产流程
标志：
- 开始付费
- 推荐给他人
- 主动搜索教程
```

**3. 创作者控制权变化**
```
阶段1: 人类主导（AI只是辅助工具）
阶段2: AI辅助（AI帮助完成部分工作）
阶段3: AI协同（人机协作创作）
阶段4: AI自动执行（人类只需审核）
```

#### 信息源

**P0 - 真实创作者分享**
```
重点看:
- "我是怎么做的"
- "我现在不用XXX了"（替代信号）
- 前后对比分享
- 效率提升数据

搜索:
- "我用AI做了XXX"
- "AI帮我省了X小时"
- "workflow分享"
```

**P0 - workflow教程**
```
为什么重要:
教程代表"稳定需求"
只有真正被使用的功能才会有教程

关注:
- 教程数量增长
- 新教程类型出现
- 教程深度变化（从入门到高级）
```

---

### 市场层（Narrative Signals）

#### 追踪什么
行业开始形成什么共识

#### 核心观察点

**1. 社区认知变化**
```
判断标志:
- "AI视频已经能商用"（vs 一年前的"还是玩具"）
- "AI剪辑已经够用了"（vs "质量不行"）
- "AI是必需品"（vs "AI只是噱头"）

关注平台:
- Product Hunt评论
- Reddit讨论帖
- Twitter投票
- 新闻评论
```

**2. 平台方向**
```
观察:
- 大厂开放什么能力（API、工具）
- 平台扶持什么内容（流量、奖金）
- 平台推出什么AI功能

重要信号:
- YouTube推出AI剪辑工具
- Adobe集成AI功能
- TikTok推出AI特效
```

**3. 资本下注方向**
```
重点不是金额，而是：
- 投资集中在哪类能力
- 什么类型的公司被收购
- 什么方向开始出现独角兽

信息源:
- Crunchbase
- TechCrunch
- 36kr
```

---

## 信息收集节奏详解

### 每日（20-30分钟）

**时间分配建议**
```
Twitter/X浏览: 10分钟
- 关注列表最新动态
- 搜索关键词：#AI #ChatGPT #Claude

Reddit浏览: 10分钟
- 热门帖子快速浏览
- 重点：r/ChatGPT, r/ArtificialIntelligence

官方Blog检查: 5-10分钟
- OpenAI/Anthropic/Google更新
- 国内：DeepSeek/Qwen/MiniMax

快速记录:
发现Signal时，用一句话记录
格式：[层级] [Signal描述] [来源]
```

### 每周（核心）

**周末整理（1-2小时）**
```
1. 收集本周所有daily记录
2. 按四层分类整理
3. 找出重复出现的Signal
4. 判断趋势方向
5. 更新追踪列表
```

**输出格式**
```
## 周报 [周数]

### 本周新增Signal

模型层:
- [Signal]
- [Signal]

产品层:
- [Signal]
- [Signal]

...

### 趋势判断
- 正在加速的变化
- 出现拐点的信号
- 需要持续观察的方向

### 下周重点
- 关注什么
- 需要深入研究的主题
```

### 每月（复盘）

**复盘维度**
```
1. Signal频率统计
   - 哪些Signal出现次数最多
   - 哪些方向开始密集

2. 趋势验证
   - 月初判断的趋势是否确认
   - 有没有反向信号

3. 信息源效果评估
   - 哪些信息源最有价值
   - 哪些需要调整

4. 框架迭代
   - Signal类型是否需要调整
   - 优先级是否需要更新
```

---

## Signal判断标准

### 什么值得记录

**强Signal（立即记录）**
```
1. 能力跃迁
   - 某模型突然可以做到之前做不到的事
   - benchmark出现明显变化

2. 产品形态变化
   - 新的产品类型出现
   - 主流产品重大更新

3. 用户行为质变
   - 某AI工具开始被主流用户采用
   - 出现新的使用场景

4. 市场认知转变
   - 社区共识发生改变
   - 大厂做出战略调整
```

**弱Signal（持续观察）**
```
1. 单点案例
   - 某个用户分享的workflow
   - 某篇评测文章

2. 模糊趋势
   - "似乎更多人开始用"
   - "感觉某类产品在增加"

3. 营销噪音
   - 新产品发布宣传
   - 公司PR稿
```

### Signal验证方法

**三重复制原则**
```
一个Signal如果只在一个地方出现：
→ 可能是噪音，需要继续观察

一个Signal如果在2-3个不同地方出现：
→ 可能是趋势，需要深入关注

一个Signal如果在多个平台、多个时间段反复出现：
→ 确认是重要趋势，值得重点追踪
```

---

## 工具与效率

### 信息收集工具建议

**RSS聚合器**
```
- Inoreader（支持过滤关键词）
- Feedly（简洁）
- Netvibes（自定义仪表盘）
```

**浏览器插件**
```
- Save to Pocket（稍后读）
- Email to Notion（直接入库）
```

**笔记系统**
```
推荐:
- Notion（结构化管理）
- Obsidian（网络化笔记）
- Logseq（概念图谱）

至少需要:
- 每日快速记录区
- Signal归档区
- 趋势分析区
```

### 信息归档结构示例

```
AI Signal Tracker/
├── 📅 Daily/
│   ├── 2024-01-15.md
│   ├── 2024-01-16.md
│   └── ...
├── 📊 Weekly/
│   ├── W01-2024.md
│   ├── W02-2024.md
│   └── ...
├── 📈 Monthly/
│   ├── 2024-01.md
│   └── 2024-02.md
├── 🔍 Signals/
│   ├── Model/
│   │   ├── new-models.md
│   │   └── api-changes.md
│   ├── Product/
│   │   ├── workflow-changes.md
│   │   └── ui-patterns.md
│   ├── Behavior/
│   │   ├── new-use-cases.md
│   │   └── workflow-evolution.md
│   └── Market/
│       ├── narrative-shifts.md
│       └── investment-trends.md
└── 🎯 Trend-Analysis/
    ├── active-trends.md
    └── watch-list.md
```

---

## 常见问题

### Q: 每天信息太多怎么办？

**A: 聚焦核心Signal**
```
1. 只看P0信息源
2. 用关键词过滤（agent、multimodal、video）
3. 设定时间限制（25分钟番茄钟）
4. 只记录一句话，不追求完整
```

### Q: 如何判断是趋势还是噪音？

**A: 时间验证法**
```
第一天出现 → 记录，继续观察
第二周又出现 → 关注
一个月内出现3次以上 → 重要趋势
```

### Q: 信息源太多顾不过来？

**A: 优先级排序**
```
第一梯队（必看）:
- OpenAI Blog
- Anthropic News
- Twitter: Sam Altman

第二梯队（每天看）:
- Twitter: AI PMs
- r/ChatGPT热门帖
- 产品发布公告

第三梯队（每周看）:
- HuggingFace Trending
- GitHub Trending
- YouTube新视频

第四梯队（按需看）:
- 新闻报道
- 分析文章
- 播客访谈
```

### Q: 记录了一大堆但不知道怎么用？

**A: 定期提炼**
```
每周:
- 提炼3个最重要的Signal
- 判断趋势方向

每月:
- 提炼1-2个核心变化
- 更新认知框架
```

---

## 核心原则提醒

> 真正重要的趋势，从来不是某一天爆发的。
> 而是同一种变化，开始在不同地方反复出现。

**最终目标**
```
不是：
"知道发生了什么"

而是：
"长期观察少量关键Signal的持续变化"
```