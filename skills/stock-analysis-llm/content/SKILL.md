---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 97171ad581efc7b76b8ecb9d76fcf727
    PropagateID: 97171ad581efc7b76b8ecb9d76fcf727
    ReservedCode1: 30440220772f67832969f8ff180a3aa5961984959ff28458647c038e9438503b4dd413c402207214306c9ee154965c017ead00dee78acb9e8915d066d7ef683a4c2c2370ec79
    ReservedCode2: 3046022100a553e8c40252e8603b2bd2bdf901622074ef1d55b6b0af67734285bdb90e076c022100b4ffd116ea75549ecf2a45bfcbef182859dc87167e0a594fdbad9f22b143ead7
description: A股智能股票分析Skill（V2+V3合并版）。支持两种模式：(1)快速分析：直接运行脚本，输出完整四大分析师报告；(2)深度LLM辩论：运行脚本获取结构化数据后，由AI进行多轮辩论生成投研结论。当用户要求分析股票、查询持仓状况、进行技术/基本面/情绪研究时触发。使用腾讯财经+东方财富免费API，无需Token。
name: stock-analysis-llm
---

# Stock Analysis LLM Skill（V2+V3合并版）

## 两种使用模式

### 模式一：快速分析（V2原生报告）
```bash
python3 /workspace/skills/stock-analysis-llm/scripts/stock_analysis_v2.py <代码> [名称]
```
脚本直接输出完整分析报告，包含四大分析师 + 辩论机制 + 三方风控，**无需AI介入**。

### 模式二：深度LLM辩论（V3数据结构）
```bash
python3 /workspace/skills/stock-analysis-llm/scripts/stock_analysis_v2.py <代码> --llm
```
输出JSON结构化数据，由无渊读取后执行LLM辩论框架生成深度研判。

---

## 脚本内置分析师（V2原生）

| 函数 | 分析维度 |
|------|---------|
| `market_analyst()` | MA5/10/20均线、压力位、支撑位、20日涨跌 |
| `sentiment_analyst()` | 量比、量价关系、情绪判断 |
| `news_analyst()` | 52周价位、东方财富快讯 |
| `fundamentals_analyst()` | PE、ROE、PB |
| `bull_researcher()` | 看多研究员 |
| `bear_researcher()` | 看空研究员 |
| `research_manager()` | 研究经理裁决 |
| `risk_manager()` | 三方风控投票决策 |

---

## LLM辩论框架（模式二使用）

当使用 `--llm` 参数或用户要求"深度分析"时，运行脚本后读取JSON数据，按以下框架进行分析：

### 1. 市场分析师
- 均线多头/空头/震荡判断
- 压力位与支撑位
- 趋势方向

### 2. 情绪分析师
- 量比分析（放量/缩量是否配合方向）
- 量价配合判断

### 3. 基本面分析师
- PE所处行业水位（亏损/偏低/适中/偏高）
- ROE质量（<5%较低/5-15%一般/>15%优秀）
- PB辅助验证

### 4. 新闻分析师
- 财经快讯标题关键词（AI/半导体/新能源等）
- 判断板块联动影响

### 5. 多空辩论（LLM主导）
整理看多理由 vs 看空理由，给出裁决：
- **偏多**：MA多头排列 + 情绪乐观 + 基本面优秀，缺一可接受
- **偏空**：MA空头排列 + 20日跌幅超10% + 基本面差
- **中性**：信号矛盾或不明朗

### 6. 风控建议
- 激进/保守/中性三方建议
- 止损位参考（支撑位下方5-8%）
- 仓位建议

---

## 数据来源

- **实时行情**：腾讯财经 `qt.gtimg.cn`（免费，无需Token）
- **K线历史**：腾讯财经 `ifzq.gtimg.cn`（60日日线，前复权）
- **财经快讯**：东方财富 `newsapi.eastmoney.com`
- **编码**：腾讯GBK → UTF-8转换

---

## 持仓代码参考

**A股**：510500、588080、600410、600497、601618、601788、603501、000538、002230、002950、300172
**港股**：09988（阿里巴巴）、02015（理想汽车）

## 注意事项

- 港股前缀：6/9开头 → sh，其余 → sz
- 网络超时：10-15秒，失败返回error字段
- 建议优先使用模式一（V2直接报告），模式二用于需要AI深度研判时
