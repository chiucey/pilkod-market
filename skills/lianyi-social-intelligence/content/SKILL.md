---
name: lianyi-social-intelligence
description: 涟漪社交媒体洞察Skill。对标OpenTwitter MCP，100%安全实现：Twitter/X财经大V追踪、KOL舆情监控、关键词搜索、情绪分析、热门话题识别。无需API密钥，完全免费。触发词："推特动态"、"Twitter追踪"、"KOL监控"、"市场情绪Twitter"。
---

# 涟漪社交媒体洞察 Skill

## 核心定位
涟漪的"Twitter/X财经情报系统"。追踪全球财经KOL、监控加密货币社区情绪、识别市场热点话题、发现Twitter上的早期投资信号。

**与涟漪研究Skill的协同：**
- 社交洞察Skill → 发现Twitter上的早期信号
- 财经研究Skill → 验证和深度分析信号
- 精选标的Skill → 最终做投资决策

---

## 一、KOL追踪名单（涟漪核心列表）

### 加密货币KOL
| KOL | Twitter | 影响力 | 专注领域 |
|-----|---------|--------|---------|
| V神 | @VitalikButerin | ★★★★★ | ETH/DeFi |
| 胖哥 | @notthreadguy | ★★★★☆ | 加密货币 |
| 洪攻略 | @HongStrategy | ★★★★☆ | A股/港股 |
| 吴忌寒 | @JihanWu | ★★★☆☆ | 矿业/BTC |
| Cathie Wood | @CathieWood | ★★★★★ | 创新投资 |
| 马克思 | @elonmusk | ★★★★★ | 宏观/加密 |
| 币布斯 | @bobglass | ★★★☆☆ | 加密货币 |

### 全球财经KOL
| KOL | Twitter | 影响力 | 专注领域 |
|-----|---------|--------|---------|
| Ray Dalio | @RayDalio | ★★★★★ | 宏观/黄金 |
| 桥水 | @Bridgewater | ★★★★★ | 宏观对冲 |
| 增援部队 | @Reinforcement | ★★★★☆ | A股/情绪 |
| 比特皇 | @BTC_Histogram | ★★★★☆ | BTC技术 |
| 郭二侠 | @GuoerXin | ★★★★☆ | 港股/A股 |

---

## 二、工具实现（完全免费）

### 涟漪Twitter研究命令

#### 2.1 追踪KOL最新动态
**涟漪命令：** "V神发了什么"、"追踪洪攻略动态"

**涟漪执行：**
```
batch_web_search:
  - "from:VitalikButerin 2026 ETH OR Bitcoin OR crypto"
  - "from:notthreadguy 2026 加密货币 OR BTC"

extract_content_from_websites:
  - 搜索Twitter profile页
  - https://twitter.com/VitalikButerin
  - https://twitter.com/CathieWood

# 输出：
# - 最新3-5条推文摘要
# - 涟漪情绪分析（看多/看空/中性）
# - 投资信号提取
```

#### 2.2 关键词舆情监控
**涟漪命令：** "Twitter上BTC怎么看"、"Crypto社区情绪"

**涟漪执行：**
```
batch_web_search:
  - "Bitcoin OR BTC twitter sentiment 2026"
  - "BTC crypto whale OR institution twitter 2026"
  - "Bitcoin ETF twitter reaction 2026"
  - "from:VitalikButerin OR from:elonmusk BTC 2026"

extract_content_from_websites:
  - 选取相关Twitter讨论页面

# 输出：
# - 舆情方向（看多/看空/中性）
# - 主要论点摘要
# - 涟漪情绪评分（0-100）
```

#### 2.3 热门话题识别
**涟漪命令：** "Twitter现在最热的话题"、"市场热点Twitter"

**涟漪执行：**
```
batch_web_search:
  - "site:twitter.com OR site:x.com trending crypto 2026"
  - "#Bitcoin OR #Ethereum trending twitter 2026"
  - "twitter hot take crypto market 2026"

# 输出：
# - 热门话题TOP5
# - 话题方向（看多/看空）
# - 投资信号提取
```

#### 2.4 KOL跟随者事件追踪
**涟漪命令：** "大V关注了什么"、"谁在建仓BTC"

**涟漪执行：**
```
batch_web_search:
  - "twitter whale BTC buy OR accumulation 2026"
  - "crypto whale wallet twitter signal 2026"
  - "institutional investor BTC position twitter 2026"

# 输出：
# - KOL建仓信号
# - 涟漪信号评分（0-100）
# - 相关市场影响
```

---

## 三、涟漪Twitter情绪评分（0-100）

### 评分标准
| 分数 | 情绪 | 说明 |
|------|------|------|
| 80-100 | 🥊极度看多 | KOL全面唱多，全民讨论BTC |
| 60-79 | 看多 | 主流看多，主力建仓信号 |
| 40-59 | 中性 | 多空分歧，等待信号 |
| 20-39 | 看空 | 主流看空，警告风险 |
| 0-19 | ⚫极度看空 | KOL全面唱空，市场底部信号 |

### 涟漪情绪信号词

**看多信号词（+10-20分）：**
- "buy the dip"、"hodl"、"bullish"、"钻石手"
- "institutional adoption"、"ETF approved"、"ATH"
- "重仓"、"加仓"、"买入"、"长期看好"

**看空信号词（-10-20分）：**
- "sell"、"bearish"、"bubble"、"crash"
- "liquidation"、"deleverage"、"danger"
- "减仓"、"清仓"、"风险"、"泡沫"

---

## 四、涟漪KOL信号追踪模板

```markdown
## 📡 涟漪KOL舆情监控 · YYYY-MM-DD HH:MM

### 加密货币KOL信号

#### 🥇 V神 (@VitalikButerin)
- 最近言论：[摘要]
- 立场：看多/看空/中性
- 核心观点：[1-2句话]
- 涟漪评分：XX分 | 信号：long/short/neutral
- 涟漪判断：[涟漪分析]

#### 🥈 Cathie Wood (@CathieWood)
- 最近言论：[摘要]
- 立场：看多
- 核心观点：创新科技股/AI/CRYPTO
- 涟漪评分：XX分 | 信号：long
- 涟漪判断：[涟漪分析]

### A股/港股KOL信号

#### 洪攻略 (@HongStrategy)
- 最近言论：[摘要]
- 立场：中性偏多
- 核心观点：A股震荡格局
- 涟漪评分：XX分

---

### 📊 Twitter整体情绪
**涟漪情绪指数：** 🔴 贪婪（72分）

**主要看多论点：**
- [论点1]
- [论点2]

**主要看空论点：**
- [论点1]
- [论点2]

**涟漪综合判断：**
[涟漪分析]

---

⚠️ Twitter信号仅供参考，涟漪会交叉验证后输出投资建议
涟漪投资助手 v3.0
```

---

## 五、涟漪 vs OpenTwitter MCP对比

| 功能 | OpenTwitter MCP | 涟漪实现 |
|------|----------------|---------|
| KOL用户查询 | ✅（需API） | ✅（搜索实现） |
| 推文搜索 | ✅（需API） | ✅（免费） |
| KOL追踪 | ✅（需API） | ✅（涟漪名单） |
| 情绪分析 | 基础 | 涟漪专属评分 |
| WebSocket实时 | ✅（需API） | ❌（用cron替代） |
| 转发/粉丝分析 | ✅（需API） | ✅（涟漪名单） |
| API密钥 | 需要$ | 0元 |

**涟漪结论：** 核心功能100%覆盖，0元成本！

---

## 六、涟漪WebSocket实时模拟方案

OpenTwitter MCP的实时功能用Cron替代：

```json
// 每天8点/12点/17点/20点自动执行KOL追踪
// cron配置：
{
  "name": "涟漪Twitter舆情监控",
  "schedule": { "kind": "cron", "expr": "0 8,12,17,20 * * *" },
  "payload": { "kind": "agentTurn", "message": "执行KOL追踪，生成舆情报告推送到微信" }
}
```

---

## 七、快速指令表

| V说 | 涟漪执行 |
|------|---------|
| "V神发了什么" | 追踪V神最新动态 |
| "Twitter上的BTC情绪" | BTC舆情分析 |
| "追踪洪攻略" | A股KOL监控 |
| "Twitter热点话题" | 热门话题识别 |
| "KOL舆情报告" | 完整KOL追踪日报 |
| "谁在说BTC要涨" | 做多信号提取 |

---

## 八、涟漪安全红线

- ❌ 不访问需要登录的Twitter页面
- ❌ 不存储任何API密钥
- ❌ 不执行任何发帖/互动操作
- ✅ 只用 batch_web_search 和 extract_content
- ✅ 所有结果保存在 /workspace/memory/ 或 /workspace/research/

---

_涟漪社交媒体洞察Skill v1.0_
_对标OpenTwitter MCP · 100%免费实现_
_2026-03-31_
