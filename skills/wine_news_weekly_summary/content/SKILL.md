---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 702e8e2159d42d4173db26c74ab1e3e7
    PropagateID: 702e8e2159d42d4173db26c74ab1e3e7
    ReservedCode1: 3045022001eaaf8747458d057d65c231e66d003efa0bfe9afc1a0d5f55b8b96b114701b50221009e5b8787f8c8e6fdbe20043269bbad0a89da4918b219876bad30c0facfb19ea3
    ReservedCode2: 3046022100df3f47f64d35b057dd56f205b13328d05633c78ac68f01e9ec0bab43956a2971022100a0e3f87e594e2d143b33861f4c4c680c74cd04c87c1bc870e62fe547cc0ddb74
author: MiniMax Agent
description: 酒类新闻每周汇总技能 - 联网搜索多个专业酒类新闻来源，汇总上周期间的酒类新闻简讯，支持市场动态、进出口贸易、趋势报告、拍卖信息、新旧世界动态等内容，自动整理为330-350字的规范中文简讯并以Markdown格式输出。
name: wine_news_weekly_summary
tags:
    - 新闻收集
    - 酒类行业
    - 市场监测
    - 每周汇总
    - 数据整理
version: 1.0.0
---

# 酒类新闻每周汇总技能

## 技能描述

这是一个专门用于收集和整理酒类行业每周新闻的自动化技能。通过联网搜索多个专业酒类新闻来源，汇总上周期间的酒类新闻简讯，并以规范的 Markdown 格式输出。

## 技能元数据

- **技能名称**: 酒类新闻每周汇总
- **技能版本**: v1.0
- **适用场景**: 酒类行业新闻监测、市场情报收集
- **目标用户**: 酒类行业从业者、市场分析师、媒体编辑

## 时间范围

汇总上一周期间的酒类新闻简讯，确保所有新闻内容在规定时间范围内。

## 新闻来源

以下是本次任务指定的新闻来源，请优先从这些网站获取信息：

| 序号 | 来源网站 | URL |
|------|----------|-----|
| 1 | Meininger's International | https://www.meiningers-international.com/news |
| 2 | Robb Report Food & Drink | https://robbreport.com/food-drink/page/2/ |
| 3 | Vinography | https://www.vinography.com/category/wine-news |
| 4 | Wine News | https://winenews.it/en/post/news/ |
| 5 | Harper's Wine & Spirit | https://harpers.co.uk/news/categoryfront.php/id/11/News.html |
| 6 | Wine Business | https://www.winebusiness.com/news/region/global/9 |
| 7 | The Spirits Business | https://www.thespiritsbusiness.com/category/news/ |
| 8 | Vinetur | https://www.vinetur.com/en/latest/ |
| 9 | The Drinks Business (Wine) | https://www.thedrinksbusiness.com/tag/wine/ |
| 10 | Just-Drinks | https://www.just-drinks.com/news/ |

## 内容聚焦领域

本技能聚焦以下酒类新闻主题：

- **市场动态**: 酒类市场走势、销售数据分析
- **进出口贸易**: 全球酒类进出口政策、海关数据、贸易动态
- **趋势报告**: 行业研究报告、消费趋势分析
- **拍卖信息**: 名酒拍卖记录、拍卖市场行情
- **新旧世界**: 旧世界（法国、意大利、西班牙等）与新世界（美国、澳大利亚、智利等）葡萄酒产区的新闻动态
- **企业新闻**: 知名酒企的重大公告、并购、合作等

## 输出格式规范

### Markdown 格式要求

每条新闻简讯必须严格遵循以下格式：

```markdown
### [标题文字（中文翻译）]
- 简讯: [简讯内容，约330-350字，使用中文书写]
- 来源: [原新闻地址链接]
```

### 内容规范

1. **标题要求**:
   - 必须为中文翻译标题
   - 简洁明了，体现新闻核心内容
   - 避免过长的标题

2. **简讯内容要求**:
   - 字数控制在330-350字左右
   - 使用中文撰写
   - 专有名词或品牌名称可使用英文原文
   - 修正其他语言文字字符，确保中文显示正常
   - 内容需提炼原新闻的核心信息

3. **来源标注**:
   - 必须附上原始新闻链接
   - 链接需确保可访问

## 输出数量要求

本次任务需输出 **30-40条** 新闻简讯。

## 质量检查要求

### 内容真实性检查

1. **严格时间约束**: 确保所有新闻都在上一周的时间范围内
2. **真实来源验证**: 仅使用上述指定新闻来源的内容
3. **杜绝虚假内容**: 不得虚构或捏造任何新闻事实
4. **去重检查**: 确保输出新闻与历史输出不重复

### 语言文字检查

1. **中文规范**: 简讯正文使用规范中文
2. **字符修正**: 修正其他语言文字字符，确保中文显示正常
3. **专有名词处理**: 品牌名、人名、产区名等专有名词可保留英文

### 字数统计检查

1. 每条简讯字数严格控制在330-350字
2. 需进行字数统计验证
3. 超出或不足字数的简讯需调整

## 执行流程

### 第一步：来源搜索

使用 batch_web_detail_search 工具对上述指定新闻来源进行并行搜索，搜索词可包括：

- "wine market news"
- "spirits industry"
- "wine import export"
- "wine auction"
- "alcohol trade"
- "new world wine news"
- "old world wine"
- "wine trend report"

### 第二步：内容提取

从搜索结果中提取符合条件的新闻内容，注意：

- 筛选上周时间范围内的新闻
- 优先选择聚焦领域内的新闻
- 记录原始来源链接

### 第三步：内容整理

将英文新闻内容翻译整理为中文简讯：

- 保持原意准确传达
- 控制字数在330-350字
- 修正可能存在的字符显示问题
- 创建规范的 Markdown 格式

### 第四步：质量审核

完成初稿后进行自检：

- [ ] 检查时间范围是否正确
- [ ] 验证新闻真实性
- [ ] 统计每条简讯字数
- [ ] 检查是否有重复内容
- [ ] 确认格式规范

### 第五步：输出交付

按格式要求输出最终结果，确保：

- 新闻数量在30-40条之间
- 每条新闻格式规范
- 所有链接可访问
- 内容无重复

## 注意事项

1. **网络环境**: 本技能在大陆网络环境运行，部分国外网站可能无法直接访问，请优先选择可访问的来源
2. **时区处理**: 注意日期计算，确保覆盖完整的上一周
3. **内容平衡**: 尽量涵盖不同来源和不同主题类型
4. **时效性**: 确保新闻为真实最新的报道，而非旧闻重复

## 技能使用示例

用户输入：
> 请帮我汇总上周的酒类新闻

技能执行：
1. 联网搜索指定新闻来源
2. 筛选上周期间的酒类新闻
3. 整理翻译为330-350字的中文简讯
4. 以 Markdown 格式输出30-40条新闻汇总

预期输出：
```markdown
### 法国葡萄酒出口额创历史新高
- 简讯: [约340字的中文简讯内容]...
- 来源: [原始链接]

### 纳帕谷遭遇极端天气影响葡萄产量
- 简讯: [约340字的中文简讯内容]...
- 来源: [原始链接]

... (共30-40条)
```
