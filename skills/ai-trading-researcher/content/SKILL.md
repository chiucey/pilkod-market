---
name: ai-trading-researcher
description: An AI-driven multi-agent stock trading research skill. Use when users ask to analyze stocks, research investment opportunities, trading decision analysis, market insights, fundamental analysis, technical analysis, sentiment analysis, or multi-agent debate-style investment research.
---

# AI Trading Researcher

基于 [TradingAgents](https://github.com/TauricResearch/TradingAgents) 框架的多代理 AI 股票交易研究技能。

## 核心功能

### 多代理分析师团队

| 代理 | 职责 |
|------|------|
| **基本面分析师** | 评估公司财务和业绩指标，识别内在价值和潜在风险 |
| **情绪分析师** | 分析社交媒体和公众情绪，使用情绪评分算法判断短期市场情绪 |
| **新闻分析师** | 监控全球新闻和宏观经济指标，解读事件对市场的影响 |
| **技术分析师** | 运用技术指标（MACD、RSI 等）检测交易模式，预测价格走势 |

### 研究辩论机制

- **多头研究员** 和 **空头研究员** 对分析师的观点进行批判性评估
- 通过结构化辩论平衡潜在收益与固有风险

### 交易决策

- 交易员代理整合分析师和研究员的报告
- 风险管理和投资组合经理评估风险并做出最终决策

## 使用方式

### 触发场景

用户可以使用以下方式触发此技能：

- "分析一下 [股票代码] 的投资价值"
- "帮我研究 [公司名] 的基本面"
- "我想了解 [股票] 的技术面情况"
- "进行多代理股票研究 [股票代码]"
- "帮我做投资决策分析 [股票代码]"
- "获取 [股票] 的市场情绪报告"
- "对比分析 [股票A] 和 [股票B]"

### 输出内容

技能将提供：

1. **综合分析报告**
   - 基本面分析（财务指标、估值、增长潜力）
   - 技术分析（趋势、支撑阻力、技术信号）
   - 情绪分析（市场情绪、社交媒体趋势）
   - 新闻影响评估（重大事件、宏观经济因素）

2. **多空辩论摘要**
   - 多头观点和论据
   - 空头观点和风险
   - 最终综合判断

3. **交易建议**
   - 明确的买入/卖出/持有建议
   - 目标价格区间
   - 风险等级评估
   - 持仓建议（仓位大小）

## 技术实现

- 基于 LangGraph 构建的 Multi-Agent 架构
- 支持多种 LLM 提供商：OpenAI GPT、Google Gemini、Anthropic Claude 等
- 整合多种数据源：yfinance、Alpha Vantage 等

## 注意事项

- 本技能仅供研究参考，不构成投资建议
- 实际交易前请自行评估风险
- 市场有风险，投资需谨慎

## 相关资源

- 原始项目：[TradingAgents GitHub](https://github.com/TauricResearch/TradingAgents)
- 研究论文：[arXiv:2412.20138](https://arxiv.org/abs/2412.20138)
