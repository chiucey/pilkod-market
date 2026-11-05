---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: a53e3963c70ea4045b508f6d746c6c62
    PropagateID: a53e3963c70ea4045b508f6d746c6c62
    ReservedCode1: 3046022100d34522348df83d396bacf63eeca4b26b005c8ef62c3c8512d17559fd6e77bc16022100c6d4a185e86eff9ec160ba7f68802e57d1fc59c011d57eaa8a481498ed7da6bb
    ReservedCode2: 3045022100962be6b3d97f76b98b66cadbb870377834d8701934debbaed214c38812243bf202207aa26b1cdf52a0ac5c815c67587d2051a7ae8926b6430491c9638764bd92ae0e
description: 定时监控指定期刊的最新论文，每天上午9:00自动抓取并推送1篇论文的精简解读至指定飞书群，支持手动触发。触发词：「推送今天的文献」「查看最新论文」「文献推送」「最新论文」「帮我找篇论文」。不干预用户已设置的cron定时任务。
name: literature-alert
---

# Literature Push - 文献定时推送技能

## 功能概述

- **自动触发**：每天上午 9:00（北京时间）通过 cron 定时任务执行
- **手动触发**：用户说"推送今天的文献"、"查看最新论文"、"文献推送"、"最新论文"、"帮我找篇论文"时执行
- **推送内容**：从19个指定期刊中每天抓取1篇最新论文，进行深度解读
- **文档归属**：所有生成的解读云文档，必须在发送推送前将 owner 转移给用户（ou_3ece79b23506d5cb111ae94ccccb3556）

## 推送目标

- **群聊** → 飞书群 `小红文献分享`（chat_id: oc_68320b61253685413edcc7ee6ec11bae）
- **私聊** → 用户个人 `叶 Zhengpei`（ou_3ece79b23506d5cb111ae94ccccb3556）

## 科研方向优先级（筛选论文时参考）

**🔥 Tier 1（核心主攻）**
- 橡胶叶螨 / 捕食螨 系统（eDNA 叶片洗涤监测、林下间作、食物网稳定性）
- 入侵粉蚧（木瓜秀粉蚧）+ 孟氏隐唇瓢虫（上行效应、氮/水胁迫对天敌功能的影响）
- eDNA 监测、Metabarcoding、食物网分子溯源、入侵害虫生物防治

**⚡ Tier 2（应用支撑）**
- 豇豆/芒果蓟马系统（迁入规律溯源、肠道植物 DNA）、商品化天敌效果评估

**🗑️ Tier 3（暂缓）**
- 小花蝽规模化养殖、纯描述性调查

## 监控期刊列表（18本）

1. Annual Review of Entomology | 2. Journal of Pest Science | 3. Pest Management Science
4. Biological Control | 5. Experimental and Applied Acarology
6. Ecology Letters | 7. Agriculture, Ecosystems and Environment
8. Journal of Agricultural and Food Chemistry | 9. Insect Science
10. Insect Biochemistry and Molecular Biology | 11. Molecular Ecology Resources
12. eLife | 13. Entomologia Generalis | 14. BMC Biology
15. Journal of Economic Entomology | 16. Ecology and Evolution
17. Current Biology | 18. PNAS | 19. Molecular Ecology

## 执行流程

> ⚠️ **owner 转移规则（自动触发和手动触发均适用）**：
> 所有通过 feishu_doc（action=create）创建的云文档，均须在发送推送前完成 owner 转移。
> 转移目标：ou_3ece79b23506d5cb111ae94ccccb3556
> 文档创建者（Bot）必须有文档的管理权限才能完成转移。
> 若转移失败，继续推送，但在推送正文中注明"文档暂时无法转移所有权，请手动移入文献解读文件夹"。

### Step 0: 检查推送记录

读取 `push_log.json`，获取已推送论文的 DOI 列表，避免重复推送。

### Step 1: 抓取最新论文

按以下顺序尝试数据源，找到未推送的新论文即停止：

#### 数据源 1️⃣：PubMed API（推荐）

```bash
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=JournalName[Journal]+AND+2026/04/01[PDAT]:2026/05/09[PDAT]&sort=pubdate&retmax=10&retmode=json"
```

期刊查询词对照：

| 期刊 | PubMed 查询词 |
|------|--------------|
| Annual Review of Entomology | "Annual Review of Entomology"[Journal] |
| Journal of Pest Science | "Journal of Pest Science"[Journal] |
| Pest Management Science | "Pest Management Science"[Journal] |
| Biological Control | "Biological Control"[Journal] |
| Experimental and Applied Acarology | "Experimental and Applied Acarology"[Journal] |
| Ecology Letters | "Ecology Letters"[Journal] |
| Agriculture, Ecosystems and Environment | Agriculture AND Ecosystems AND Environment |
| Journal of Agricultural and Food Chemistry | "Journal of Agricultural and Food Chemistry"[Journal] |
| Insect Science | "Insect Science"[Journal] |
| Insect Biochemistry and Molecular Biology | "Insect Biochemistry and Molecular Biology"[Journal] |
| eLife | "eLife"[Journal] |
| Entomologia Generalis | "Entomologia Generalis"[Journal] |
| BMC Biology | "BMC Biology"[Journal] |
| Journal of Economic Entomology | "Journal of Economic Entomology"[Journal] |
| Ecology and Evolution | "Ecology and Evolution"[Journal] |
| Current Biology | "Current Biology"[Journal] |
| PNAS | "Proceedings of the National Academy of Sciences"[Journal] |
| Molecular Ecology | "Molecular Ecology"[Journal] |

#### 数据源 2️⃣：CrossRef API

```bash
curl "https://api.crossref.org/works?filter=from-pub-date:2026-04-01,until-pub-date:2026/05/09,journal-title:JournalName&rows=10&sort=published&order=desc" -H "Accept: application/json"
```

#### 数据源 3️⃣：期刊官网 RSS（仅用于 Nature/Science/Cell 等顶刊备选）

| 期刊 | RSS 地址 |
|------|---------|
| Nature | https://www.nature.com/nature.rss |
| Science | https://www.science.org/rss/current.xml |
| Cell | https://www.cell.com/cms/feed |

#### 数据源 4️⃣：Google Scholar（最后备选）

### Step 2: 去重过滤

对比搜索结果与 `push_log.json` 中的 DOI，跳过已推送论文。

### Step 3: 筛选论文

**✅ 入选标准：**
1. 相关性：橡胶叶螨/捕食螨、入侵粉蚧/孟氏隐唇瓢虫、eDNA监测、Metabarcoding、食物网溯源、入侵害虫生物防治、上行效应
2. 创新性：含"novel"、"mechanism"、"genomic"、"eDNA"、"metagenomics"、"predatory mite"、"biological control"等关键词
3. 时间优先：最新发表优先

**❌ 排除标准：**
社论、勘误、Letter、News、纯方法学无创新、综述（除非与 Tier 1 高度相关）、会议摘要

### Step 4: 获取论文详情

获取优先级：① OA 期刊官网 → ② bioRxiv/arXiv → ③ PubMed 摘要 → ④ CrossRef 元数据

### Step 5: 创建飞书云文档（Bot 是 owner）

使用 `feishu_doc`（action=create）创建空白文档（不带 folder_token）。

文档标题格式：`[论文英文标题简写]-解读报告`（不超过80字符）

记录返回的 `document_id`（即 doc_token）。

### Step 6: 写入文档内容

使用 `feishu_doc`（action=write）将10部分深度解读内容填入文档。

### Step 7: 等待 3 秒后转移 owner（必须执行）

> 这是统一规范——自动触发和手动触发均须执行。

```python
python3 -c "
import urllib.request, json, time
time.sleep(3)
with open('/root/.openclaw/openclaw.json') as f:
    cfg = json.load(f)
app_secret = cfg['channels']['feishu']['accounts']['main']['appSecret']
app_id = 'cli_a97d2d8990389bd9'
auth_url = 'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal'
payload = json.dumps({'app_id': app_id, 'app_secret': app_secret}).encode()
req = urllib.request.Request(auth_url, data=payload, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as r:
    app_token = json.loads(r.read()).get('app_access_token', '')
doc_token = 'DOC_TOKEN'  # 替换为 Step 5 返回的实际 doc_token
transfer_url = f'https://open.feishu.cn/open-apis/drive/v1/permissions/{doc_token}/members/transfer_owner?type=docx'
payload2 = json.dumps({'member_type':'openid','member_id':'ou_3ece79b23506d5cb111ae94ccccb3556','need_notification':False}).encode()
req2 = urllib.request.Request(transfer_url, data=payload2, headers={'Authorization':f'Bearer {app_token}','Content-Type':'application/json'})
with urllib.request.urlopen(req2, timeout=10) as r2:
    result = json.loads(r2.read())
    print('owner转移:', result.get('msg'), result.get('code'))
"
```

- 若返回 `code: 0` 且 `msg: "Success"` → 转移成功，继续 Step 8
- 若返回 `403` 或其他错误 → 跳过转移，在推送正文中注明「文档暂时无法转移所有权，请手动移入文献解读文件夹」

### Step 8: 发送飞书群推送

使用 `message` 工具发送到 `oc_68320b61253685413edcc7ee6ec11bae`：

```
📖 今日文献推送 | [日期]

【论文标题】
[标题]

【中文译名】
[中文翻译]

【期刊】
[期刊名称] | [发表时间]

【作者】
[作者列表]

【核心发现】
[3-5句话概括研究关键发现]

【推荐理由】
[为什么这篇值得读：创新点/方法/应用价值，以及和用户研究方向的关联]

【原文链接】
[DOI或URL]

---
🔗 详细深度解读报告：[飞书云文档链接]
📁 文档已归属您，请手动移入「文献解读」文件夹
```

### Step 9: 更新推送记录

追加到 `push_log.json`，保留最近30条。

### Step 10: 错误处理

| 问题 | 解决方案 |
|------|---------|
| API 请求失败 | 降级到备用数据源，记录到 `error_log.json` |
| 无法获取全文 | 标注"⚠️ 仅基于摘要解读"继续推送 |
| 飞书推送失败 | 降级私聊用户 ou_3ece79b23506d5cb111ae94ccccb3556 |
| 无新论文 | 扩大时间范围到14天，仍无则跳过当天推送 |
| owner 转移失败 | 跳过转移，推送正文注明提示，继续发送 |

错误日志路径：`/workspace/skills/literature-alert/error_log.json`

格式：
```json
{"date": "2026-05-09", "error": "错误描述", "step": "Step X"}
```

---

## 推送目标判断逻辑

| 内容类型 | 推送去向 |
|----------|----------|
| 系统日志/错误记录 | 用户私聊（ou_3ece79b23506d5cb111ae94ccccb3556） |
| 正式论文解读 | 飞书群（oc_68320b61253685413edcc7ee6ec11bae） |

---

## 输出模板

### 群推送消息模板（见 Step 8）

---

## 触发规则

**执行推送**：推送今天的文献 / 查看最新论文 / 文献推送 / 最新论文 / 帮我找篇论文

**不触发**：仅有链接无说明 / 系统通知

---

## 常见错误

| 错误 | 正确做法 |
|------|----------|
| 推送付费墙论文 PDF | 仅提供摘要解读 + 合法访问链接 |
| 重复推送同一论文 | 检查 push_log.json 中的 DOI |
| 忘记转移 owner | Step 7 必须在发送推送前完成 |
| 推送前未检查已推送记录 | Step 0 必做 |
| 发现错误不记录 | 所有错误写入 error_log.json |
