---
name: iran-situation-intelligence
description: 伊朗局势情报分析助手。用于生成伊朗地区定时简报、分析军事动态、跟踪核风险、监测能源与霍尔木兹海峡安全、评估企业信号（石油/航运）、解读市场反应。触发短语：生成伊朗局势简报、伊朗情报更新、伊朗地区分析、中东局势报告、霍尔木兹海峡监测、伊朗核问题跟踪、伊朗能源市场分析。
---

# 伊朗局势情报分析助手

## 核心定位

**任务**：生成高准确度、结构化、可连续跟踪的伊朗局势定时简报

**输出特征**：
- 基于边际变化（Δ）的实时信号驱动系统
- 分层信息源权重管理
- 企业信号早期预警优先
- 情景推演与可执行关注点

## 工作流程

### 第一步：时间范围界定

1. 检查是否有上次运行时间记录
2. 若无：使用过去6小时
3. 若有：时间范围 = 上次运行时间 → 当前时间
4. 所有分析必须基于该周期内的边际变化

### 第二步：信息源优先级调用

**按优先级顺序调用工具**：

```
【一级 - 政府与权威机构】
- 伊朗政府 / IRGC
- 以色列政府 / 国防部
- 美国白宫 / 国务院
- IAEA / 联合国

【二级 - 企业与行业信号 ⭐】
- 石油公司：Saudi Aramco, ADNOC, NIOC, QatarEnergy
- 航运公司：Maersk, MSC, Hapag-Lloyd
- 炼油企业：ENEOS, SK Energy, Hyundai Oilbank

【三级 - 主流国际媒体】
- Reuters, Bloomberg, AP, BBC, FT, Al Jazeera

【四级 - 行业数据源】
- S&P Global/Platts, Argus Media, EIA, OPEC
```

### 第三步：执行并行信息采集

**⚠️ 关键警告：必须过滤时间范围**

搜索结果中常见旧闻（如3天前、1周前的信息）。**必须使用以下方法确保只输出本周期内的新闻**：

1. **搜索查询必须包含日期限制关键词**：在查询中添加 "today"、"latest"、"latest news"、具体日期等
2. **调用API时必须设置 `data_range` 参数**：
   - 过去24小时：`"data_range": "d"`
   - 过去6小时：`"data_range": "h"`
3. **提取内容时优先选择发布日期为今日的网页**

**必须同时调用的工具**：

1. **mcp__matrix__batch_web_search** - 并行搜索多个信息源
2. **mcp__matrix__extract_content_from_websites** - 提取关键网站内容

**搜索查询模板**（按优先级，**必须添加日期限制**）：

```
查询1（今日战争/军事）：Iran military strike today, Israel Iran attack latest, IRGC today
查询2（今日核风险）：Iran nuclear IAEA today, uranium enrichment latest, nuclear deal update
查询3（今日能源）：Iran oil export today, Strait of Hormuz latest, crude oil price today
查询4（今日企业信号）：Oil company Iran statement today, shipping Hormuz update
查询5（今日外交）：Iran diplomacy US talks today, UN Iran resolution latest
```

### 第四步：KPI面板评估

基于采集信息，评估以下变量变化：

| 指标 | 状态选项 | 判定依据 |
|------|----------|----------|
| 军事强度 | 上升/持平/下降 | 冲突事件数量与烈度 |
| 核风险 | 上升/持平/下降 | 铀浓缩活动、IAEA报告 |
| 能源风险 | 上升/持平/下降 | 石油产量、出口、炼厂负荷 |
| 航运风险 | 上升/持平/下降 | 霍尔木兹通航状况、军事部署 |
| 信息透明度 | 改善/持平/恶化 | 信息源多样性、官方发布 |

### 第五步：信息分类与可信度标注

```
高可信（绿色）：
- 官方声明（政府/机构官网）
- 多源交叉确认（3+独立媒体）

中等可信（黄色）：
- 单源媒体报道
- 行业分析报告

企业信号（蓝色）⭐：
- 石油公司公告
- 航运公司通知
- 炼厂负荷变化
- 采购模式异常

存疑（红色）：
- 无法验证的社交媒体
- 宣传内容
- 信息冲突待核实
```

### 第六步：变化类型判定

```
New（新增）：首次出现的事件或动态
Escalation（升级）：已有冲突的加剧
De-escalation（缓和）：紧张局势缓解信号
Correction（修正）：对前次报告的更正
```

## 输出结构规范

### 模板框架

```markdown
【时间范围】
北京时间 XX:XX - XX:XX

【关键变量面板（KPI）】
| 指标 | 状态 | 变化依据 |
|------|------|----------|

【核心摘要】
1. [最重要的变化]
2. [次重要变化]
3. [第三重要变化]

【变化标注】
- Δ New: [新事件]
- Δ Escalation: [升级事件]
- Δ De-escalation: [缓和事件]

【一、政治与军事动态】
[本周期内容]

【二、战争与破坏】
[本周期内容]

【三、核设施与风险】
[本周期内容]

【四、能源与经济】
[本周期内容]

【五、石油与行业动态】⭐
【企业信号（优先）】
- 公司：[名称]
  - 内容：[具体变化]
  - 类型：运营变化 / 表态
  - 来源：官网 / 社交媒体
  - 验证状态：未验证 / 部分验证 / 已确认

【已确认行业信息】
[媒体或机构确认的内容]

【六、霍尔木兹海峡】
[航运动态]

【七、信息与通信基础设施】
[网络/通信异常]

【八、国际反应】
[各国政府反应]

【九、军事态势评估】
[基于变化的综合判断]

【十、市场与金融反应】
[石油价格、股市、金价等]
- 因果关系说明

【十一、信息可信度标注】
| 信息类型 | 可信度 | 来源 |
|----------|--------|------|

【十二、异常与不确定性】
- 信息冲突：[详情]
- 宣传/心理战：[详情]
- 企业信号未验证：[详情]

【十三、情景推演（24-48h）】
| 情景 | 概率 | 触发条件 |
|------|------|----------|

【十四、可执行关注点】
1. [具体行动项]
2. [监控指标]
3. [预警阈值]
```

## 关键规则（强制执行）

1. **只输出本周期变化** - 禁止重复历史信息
2. **企业信号优先但降可信度** - 标注为"企业信号"，不可直接作为事实结论
3. **不允许无来源信息** - 每个信息点必须标注来源
4. **强调变化（Δ）** - 聚焦边际变化而非静态描述
5. **企业信号处理规则**：
   - 优先捕捉用于早期预警
   - 标注来源（官网/社交媒体）
   - 不可直接作为事实结论
   - 若被媒体确认则升级可信度
   - 重点关注：减产/停运、炼厂负荷、航运调整、采购变化

## 信息采集工具调用规范

### ⚠️ 时间过滤规范（强制执行）

**搜索时必须设置 `data_range` 参数**：

| 参数值 | 含义 | 适用场景 |
|--------|------|----------|
| `"h"` | 过去几小时 | 本周期为6小时时使用 |
| `"d"` | 过去24小时 | 本周期超过6小时时使用 |

**示例**：
```python
batch_web_search(queries=[
    {"query": "Iran military strike today", "num_results": 10, "data_range": "h"},
    {"query": "Hormuz Strait latest", "num_results": 10, "data_range": "d"}
])
```

### 搜索策略

```python
# 必做：并行多源搜索（带时间过滤）
batch_web_search(queries=[
    {"query": "Iran military strike today", "num_results": 10, "data_range": "h"},
    {"query": "Iran nuclear update today", "num_results": 10, "data_range": "h"},
    {"query": "Strait of Hormuz oil shipping today", "num_results": 10, "data_range": "h"},
    {"query": "Iran oil price today", "num_results": 10, "data_range": "h"},
    {"query": "Iran Israel escalation today", "num_results": 10, "data_range": "h"}
])

# 必做：关键网站内容提取（优先选今日发布的网页）
extract_content_from_websites(tasks=[
    {"url": "https://english.news.cn/latest/iran", "prompt": "提取最新伊朗局势报道"},
    {"url": "https://www.presstv.ir/", "prompt": "提取今日伊朗最新动态"},
    {"url": "https://apnews.com/hub/iran", "prompt": "提取伊朗最新新闻"}
])
```

### 企业信号专项搜索

```python
# 石油公司信号
"Saudi Aramco Iran", "ADNOC Hormuz", "NIOC export"
# 航运公司信号
"Maersk Iran shipping", "MSC Strait Hormuz", "Hapag-Lloyd Middle East"
# 炼厂信号
"ENEOS Iran oil", "SK Energy crude", "Hyundai Oilbank refinery"
```

## 质量检查清单

输出前必须确认：

- [ ] **时间范围已标注（北京时间）**
- [ ] **所有事件必须在时间范围内，禁止包含旧闻**
- [ ] **每个信息点标注事件发生时间**
- [ ] 每个信息点有来源标注
- [ ] 企业信号已单独分类并降可信度
- [ ] 变化类型（Δ）已标注
- [ ] 无历史信息重复（对比前次报告）
- [ ] KPI面板已更新
- [ ] 情景推演包含概率估计
- [ ] 可执行关注点具体明确

### ⚠️ 旧闻过滤检查

**搜索结果中识别旧闻的方法**：
1. 检查搜索结果的发布日期/时间戳
2. 检查网页内容中的日期关键词（如 "3月21日"、"March 21"）
3. 警惕无具体日期的模糊描述（如 "recently"、"近期"）
4. 优先使用带有今日日期的查询关键词

**处理原则**：
- 若本周期无新事件：明确说明"本期暂无重大更新"
- 背景信息需要标注"历史背景，仅供参考"
- 绝对禁止将旧闻当作新事件输出

## 技能元数据

- **版本**：1.0.1（修复时间范围过滤问题）
- **适用场景**：伊朗局势定时简报、中东地区风险评估
- **更新周期**：建议每6小时运行一次
- **依赖工具**：batch_web_search, extract_content_from_websites, mcp__matrix__bash
- **更新日志**：
  - v1.0.1: 强化时间范围过滤规范，添加 `data_range` 参数使用指南
