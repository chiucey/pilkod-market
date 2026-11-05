---
name: Daily Investment
description: 通过AKShare结构化数据+搜索实时内容，多源聚合券商研报，生成每日投研报告

---


# 投资日报聚合技能 (Daily Investment Reporter Skill)

## 概述

一个全面的投资研报聚合技能，可从多个数据源收集并整合券商研报、个股新闻和公司公告，生成结构化的市场简报。专为需要及时、可操作情报的投资者和研究分析师设计，支持短线交易或长期资产配置决策。

## 能力

本技能提供以下核心能力：

1. **多源数据聚合**：使用 AKShare 和网络搜索从券商研报、个股新闻和公司公告中收集数据
2. **去重与冲突解决**：智能合并重复内容并解决不同数据源之间的冲突信息
3. **结构化简报生成**：针对三个关键交易时段生成市场简报：
   - **早报**（盘前）：盘前市场概览和今日重点关注
   - **午报**（盘中）：盘中市场脉动和实时动态
   - **晚报**（盘后）：盘后总结和次日展望
4. **情绪分析**：将市场动向信息分类为利好和利空因素
5. **Markdown 报告输出**：生成简洁、易读的报告，便于快速浏览

## 使用方法

### 基本用法

```python
from daily_investment_reporter import generate_briefing

# 生成早报
report = generate_briefing(
    briefing_type="morning",
    stock_codes=["000001", "600519"],
    include_broker_reports=True,
    include_news=True,
    include_announcements=True
)
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `briefing_type` | string | 是 | - | 简报类型：`morning`（早报）、`afternoon`（午报）或 `evening`（晚报） |
| `stock_codes` | array | 否 | `[]` | 关注的股票代码列表，例如 `["000001", "600519"]` |
| `include_broker_reports` | boolean | 否 | `true` | 是否包含券商研报 |
| `include_news` | boolean | 否 | `true` | 是否包含个股新闻 |
| `include_announcements` | boolean | 否 | `true` | 是否包含公司公告 |
| `output_format` | string | 否 | `"markdown"` | 输出格式：`markdown` 或 `json` |

### 使用场景示例

#### 场景 1：完整早报
```python
report = generate_briefing(
    briefing_type="morning",
    include_broker_reports=True,
    include_news=True,
    include_announcements=True
)
```

#### 场景 2：聚焦个股分析
```python
report = generate_briefing(
    briefing_type="afternoon",
    stock_codes=["600519", "000858", "002415"],
    include_broker_reports=True,
    include_news=True
)
```

#### 场景 3：晚报（JSON 输出）
```python
report = generate_briefing(
    briefing_type="evening",
    output_format="json"
)
```

## 输出格式

### Markdown 结构示例

```markdown
# 📊 投资简报 - [早报/午报/晚报]
**生成时间**: YYYY-MM-DD HH:MM:SS

## 📈 市场概况
[市场概况摘要]

## 🔥 今日要闻
### ✅ 利好因素
- [利好因素 1]
- [利好因素 2]

### ⚠️ 利空因素
- [利空因素 1]
- [利空因素 2]

## 📑 券商研报精选
### [股票代码] - [股票名称]
- **机构**: [券商名称]
- **评级**: [评级]
- **核心观点**: [核心见解]
- **目标价**: [目标价格]

## 📰 个股新闻
### [股票代码] - [股票名称]
- **时间**: HH:MM
- **标题**: [新闻标题]
- **来源**: [来源]
- **摘要**: [简要摘要]

## 📢 公司公告
### [股票代码] - [股票名称]
- **公告类型**: [公告类型]
- **发布时间**: YYYY-MM-DD
- **关键信息**: [关键要点]

## 💡 投资建议
[基于聚合数据的策略建议]

---
*数据来源: AKShare + 多源网络聚合 | 免责声明: 本报告仅供参考，不构成投资建议*
```

## 数据来源

### AKShare API
- `stock_news_em()` - 东方财富个股新闻
- `stock_notice_report()` - 公司公告
- `stock_research_report_em()` - 券商研报
- `stock_zh_a_spot_em()` - A股实时数据

### 网络搜索集成
- 实时新闻聚合
- 研报数据交叉验证
- 补充市场情报

## 核心特性

### 去重算法
- 基于内容哈希的重复检测
- 标题相似度匹配（>85% 阈值）
- 时间戳感知优先级（优先最新内容）

### 冲突解决机制
- 来源可信度排序（券商研报 > 官方公告 > 新闻）
- 交叉引用验证
- 矛盾信息的置信度评分

### 智能分类
- 基于 NLP 的情绪分析
- 利好/利空因素关键词提取
- 行业板块分类

## 技术要求

### 依赖项
```
akshare>=1.12.0
requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0
jieba>=0.42.1
```

### 运行环境
- Python 3.8+
- 需要互联网连接以获取数据
- 推荐：2GB+ 内存用于处理大型数据集

## 错误处理

本技能实现了健壮的错误处理机制：
- **网络故障**：指数退避重试机制
- **数据质量问题**：对输入数据进行验证和清理
- **API 速率限制**：智能节流和缓存
- **数据缺失**：优雅降级，生成部分报告

## 性能考量

- **缓存时长**：实时数据 5 分钟，历史研报 1 小时
- **典型生成时间**：完整简报 10-30 秒
- **速率限制**：每个数据源每分钟最多 60 次 API 调用
- **并发请求**：最多 5 个并行数据获取

## 限制

1. 数据可用性取决于外部 API 正常运行
2. 非交易时段可能实时更新有限
3. 券商研报访问可能因订阅级别而异
4. 历史数据回溯限制为 30 天

## 合规与免责声明

⚠️ **重要提示**：
- 本工具仅供信息参考
- 不构成金融投资建议
- 用户应进行独立研究
- 过往表现不代表未来结果
- 请遵守当地证券法规