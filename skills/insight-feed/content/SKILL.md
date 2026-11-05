---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: d0ae35dcf0741b53e34715ba1cfd2437
    PropagateID: d0ae35dcf0741b53e34715ba1cfd2437
    ReservedCode1: 304502207df93505cd197e12c6a98f50a65a7b2638ea07a6d5f4f88fe0c1bb38be93e17b022100fe5951f23136d4e90f9b7e0b29cc6520518088fc8d1c9a48938ccb8261e26e2e
    ReservedCode2: 30460221009db877190684cf487d5c9bcbc1059f1772f64bac7dc45af23be34dc8a9b44cd2022100adf9340c2a7978891fc0461e77cf560a91927dbf06456099de17765e7e424aed
description: 通用资讯聚合与定时推送技能。根据用户配置的关键词和信源，自动搜集、筛选、汇总并推送到飞书群。支持每日/每周定时运行、关键词自定义、信源自定义（RSS/网页搜索/公众号）。触发场景：(1) 用户想搭建某个主题的自动化资讯追踪；(2) 用户要创建一个每日/每周新闻推送到飞书群；(3) 用户想追踪特定关键词（竞品、行业动态、公司动态等）并定时推送；(4) 用户要新增/修改/查看已配置的资讯追踪任务。
name: insight-feed
---

# insight-feed · 资讯聚合推送

配置一次，自动追踪，持续推送。

## 核心概念

| 概念 | 说明 |
|------|------|
| **话题（Topic）** | 一个追踪主题，如「eSIM行业」「新能源汽车」「竞品动态」 |
| **关键词** | 追踪的关键词列表，支持 AND/OR 组合 |
| **信源** | RSS订阅源 + 网页搜索关键词 + 公众号搜索 |
| **推送目标** | 飞书群 ID |
| **调度周期** | `daily`（每天）或 `weekly`（每周一） |

---

## 文件结构

```
insight-feed/
├── SKILL.md                          ← 本文件
├── references/
│   └── config-schema.json            ← 配置格式说明
└── scripts/
    └── parse_keywords.js             ← 关键词文件解析脚本
```

**配置文件位置：** `/workspace/insight-feed/config.json`

---

## 第一步：创建配置文件

用户首次使用或要新增话题时，执行此步骤。

### 快速配置模板

将以下内容写入 `/workspace/insight-feed/config.json`：

```json
{
  "topics": [
    {
      "id": "topic-1",
      "name": "eSIM行业动态",
      "keywords": ["eSIM", "eUICC", "物联网SIM"],
      "searchTemplates": [
        "site:gsma.com {keyword} 2026",
        "site:c114.com.cn {keyword}",
        "site:ithome.com {keyword} 2026",
        "site:caict.ac.cn {keyword}"
      ],
      "wechatAccounts": ["联通eSIM", "物联网智库", "广和通FIBOCOM"],
      "rssSources": [
        "https://www.c114.net.cn/rss/",
        "https://trustedconnectivityalliance.org/feed/"
      ],
      "feishuChatId": "oc_3586059a0a77037c5dfc1be0154456bd",
      "schedule": "daily",
      "enabled": true
    }
  ]
}
```

### 配置字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `topics[].id` | ✅ | 唯一标识，英文+数字 |
| `topics[].name` | ✅ | 话题名称，用户可见 |
| `topics[].keywords` | ✅ | 核心关键词数组，至少1个 |
| `topics[].searchTemplates` | ❌ | 网页搜索模板，`{keyword}` 占位 |
| `topics[].wechatAccounts` | ❌ | 微信公众号名称列表 |
| `topics[].rssSources` | ❌ | RSS 订阅源 URL 列表 |
| `topics[].feishuChatId` | ✅ | 推送目标飞书群 ID |
| `topics[].schedule` | ✅ | `daily` 或 `weekly` |
| `topics[].enabled` | ✅ | `true` / `false` |

**默认搜索模板**（未指定时使用）：
```
site:gsma.com {keyword} 2026
site:c114.com.cn {keyword}
site:ithome.com {keyword} 2026
site:36kr.com {keyword}
"{keyword}" 2026
```

---

## 第二步：初始化 Cron 任务

配置完成后，调用 `cron` 工具为每个 `enabled: true` 的话题创建定时任务。

### Daily 任务（每天 8:56 北京时间）

```json
{
  "name": "【资讯追踪】话题名称",
  "schedule": { "kind": "cron", "expr": "56 8 * * 1-5", "tz": "Asia/Shanghai" },
  "payload": {
    "kind": "agentTurn",
    "message": "【自动任务】执行资讯追踪，推送今日要闻。\n\n读取配置文件：/workspace/insight-feed/config.json\n\n步骤：\n1. 读取配置，找到 enabled=true 且 schedule=daily 的话题\n2. 对每个话题执行搜索（batch_web_search，data_range: d）\n3. 筛选、去重、生成报告\n4. 发送到配置中指定的 feishuChatId\n5. 所有链接用尖括号 <URL> 包裹\n\n【重要】链接必须用尖括号包裹，防止飞书渲染异常。",
    "timeoutSeconds": 480
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "delivery": { "mode": "none" }
}
```

### Weekly 任务（每周一 8:35 北京时间）

```json
{
  "name": "【资讯周报】话题名称",
  "schedule": { "kind": "cron", "expr": "35 8 * * 1", "tz": "Asia/Shanghai" },
  "payload": {
    "kind": "agentTurn",
    "message": "【自动任务】执行资讯周报推送，搜集过去7天动态。\n\n今天是{{TODAY}}。搜集范围：今天往前推7天。\n\n读取配置文件：/workspace/insight-feed/config.json\n\n步骤：\n1. 读取配置，找到 enabled=true 且 schedule=weekly 的话题\n2. 对每个话题执行搜索（batch_web_search，data_range: d，每项10条）\n3. 筛选发布时间在过去7天内的条目\n4. 去除重复链接，生成周报\n5. 发送到配置中指定的 feishuChatId\n6. 报告开头格式：📡 资讯周报 · 话题名称 | 过去7天（YYYY年MM月DD-DD日）\n\n【重要】链接必须用尖括号包裹。",
    "timeoutSeconds": 600
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "delivery": { "mode": "none" }
}
```

---

## 第三步：运行时行为

每次定时任务触发时，执行以下流程：

```
1. 读取 /workspace/insight-feed/config.json
2. 根据话题 schedule 筛选对应任务
3. 构建搜索查询列表
4. 并行执行 batch_web_search（data_range: d，每天推送则限当天；每周推送限过去7天）
5. RSS 源调用 python3 /workspace/skills/rss-reader/scripts/rss.js check --since 168h
6. 微信文章：搜索 {keyword} site:mp.weixin.qq.com，找转载页面读取
7. 合并去重，按时间倒序
8. 生成 Markdown 报告
9. 用 message 工具发送到对应飞书群（channel: feishu，target: chat:群ID）
10. 链接全部用 <URL> 格式
```

---

## 常用操作

### 新增话题
在 `config.json` 的 `topics` 数组中添加新对象，然后调用 `cron` 工具创建对应任务。

### 修改关键词
直接编辑 `/workspace/insight-feed/config.json`，下次定时任务自动生效。

### 查看已创建的任务
调用 `cron list` 查看所有定时任务。

### 删除话题
将 `config.json` 中对应话题的 `enabled` 改为 `false`，然后调用 `cron remove` 删除该任务。

---

## 输出报告格式模板

```
📡 资讯追踪 · {话题名称}
📅 {日期}
共收录 X 条资讯（网页搜索 + RSS + 公众号）

---

**{序号}. {标题}**
📅 {发布时间} | 📰 {来源}
{一句话摘要（50字以内）}

---
⚠️ 由 AI 自动搜集，数据源涵盖 {信源列表}。如链接失效请告知。
```

---

## 微信文章处理策略

1. 搜索 `site:mp.weixin.qq.com {关键词}` 找文章
2. 如微信文章被拦截，用文章标题在百度/谷歌搜索第三方转载
3. 找到转载后用 `extract_content_from_websites` 抓取
4. 实在找不到转载，保留标题作为参考

## 注意事项

- 每条消息最多推送 **20 条** 资讯，超出截断并注明「其余 N 条略过」
- 链接统一用尖括号 `<URL>` 包裹，飞书不会渲染异常
- 定时任务如失败，查看 `cron runs {任务ID}` 排查原因
- 配置文件修改后无需重启，下次定时任务自动读取新配置
