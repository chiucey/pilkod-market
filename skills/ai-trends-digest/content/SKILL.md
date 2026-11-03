---
name: ai-trends-digest
description: Collect and organize trending AI knowledge. Use when users ask to gather trending AI terms, summarize weekly AI trends, compile usage examples and community reviews, or need high-quality credible AI knowledge summaries.
---

# AI热门知识摘要

收集过去7天内AI领域的热门术语、新概念、技术趋势及其高质量来源、使用示例和社区评论。

## 工作流程

### 1. 热门趋势识别

使用 `batch_web_search` 搜索过去7天的AI热门话题：

```
搜索策略：
- "AI [日期]" 或 "artificial intelligence [日期]"
- "LLM trends [月份]"
- "AI news this week"
- "machine learning breakthrough [近期]"
- "AI research viral [周/月]"
```

### 2. 核心信息收集

对每个识别的热门term，使用 `extract_content_from_websites` 深入提取：

**必收集信息**：
- 术语/概念的精确定义
- 官方文档或权威来源
- 实际使用代码/示例
- 社区反馈和评价

### 3. 信誉度评估标准

按以下标准筛选内容（可信度分级）：

| 等级 | 来源类型 | 权重 |
|------|----------|------|
| A+ | 官方文档/论文/顶级会议 | 1.0 |
| A  | 技术博客/知名开发者/主流媒体 | 0.8 |
| B  | 社区讨论/产品发布/创业公司 | 0.6 |
| C  | 社交媒体/论坛/未验证消息 | 0.3 |

**质量门槛**：仅收录B级以上内容，重点推荐A级以上。

### 4. 结构化输出

每个热门term按以下格式整理：

```markdown
## [术语名称]

**定义**：简洁的术语解释

**来源**：权威链接 + 信誉等级

**使用示例**：
```[语言]
// 示例代码或使用场景
```

**社区评论摘要**：
- 正面评价：...
- 质疑/批评：...
- 实际应用场景：...

**可信度评级**：A+ / A / B
```

## 输出质量标准

1. **时效性**：所有内容来自过去7天内
2. **可信度**：每个term必须有可信来源支撑
3. **实用性**：包含可直接使用的示例
4. **平衡性**：包含正面和负面评价
5. **可验证性**：提供原始链接供核实

## 快速执行提示

收集AI热门知识时：
1. 先用通用搜索定位热门话题
2. 锁定3-5个核心term深入研究
3. 对每个term验证来源可信度
4. 提取实际使用示例而非泛泛描述
5. 整理社区真实评价而非单一来源
