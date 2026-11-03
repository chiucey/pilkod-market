---
name: earn-money
description: >
  跨市场多因子共振交易分析体系，覆盖A股/港股/美股超短线扫描、中长线波段、全市场指数风控、行业景气评级。
  触发词：扫描今日短线机会、指数风控扫描、综合分析报告、查看XXX板块、分析XXX股票、
  短线扫描、指数风控、各大指数、全市场扫描、跨市场分析、筹码分析、板块分析、股票分析、选股、买卖建议、仓位管理、止盈止损、
  盈亏比测算、技术指标共振、均线系统、MACD、RSI、SKDJ、涨停分析、跌停分析、
  涨停原因、跌停原因、涨停板块、连板梯队、龙头股、炸板分析、赚钱效应、
  北向资金、南向资金、主力资金、市场情绪、行业景气度、量化风控、交易纪律、恒生指数、恒生科技、纳斯达克
---

# 为赚钱 — 跨市场多因子共振交易分析体系

## 核心原则

1. 拆分超短线交易体系与中长线波段体系，解决短中指标错配、信号滞后问题
2. 筹码仅作辅助验证，不作为唯一决策依据；筹码数据若不可获取则跳过该维度，不编造
3. 所有交易信号执行多因子共振判定，杜绝单一指标决策
4. 均线系统双轨制：超短线以60分钟5MA/10MA/20MA为第一判定，中长线以日线5/10/20/60为参考；60日均线降级为辅助参考
5. 所有交易场景强制输出潜在盈亏比×胜率估算=期望值，量化交易性价比
6. 全局最高优先级：交叉自验求实 — 所有结论必须依托真实可查数据，无法交叉验证的信号直接作废
7. 流动性是一切交易的前提 — 日均成交额不足的标的直接淘汰
8. 所有交易分析必须前置「四维全景环境评估」（政策/行业/资金/情绪四维），详见 [environment-assessment.md](references/environment-assessment.md)
9. 大盘综合分析必须执行「涨跌停复盘」——逐行业归因涨停催化因子、逐一分析跌停原因，详见 [limit-analysis.md](references/limit-analysis.md)
10. **个股/板块分析必须前置「护城河深度分析」**——5维度壁垒评估+竞争对手硬核对比+三档分级结论，详见 [moat.md](references/moat.md)
11. **个股/板块分析必须包含「参与者博弈全景」**——8类参与者立场/逻辑/隐忧/博弈推演+多空力量对比+博弈核心结论，详见 [game-theory.md](references/game-theory.md)
12. **所有分析报告必须以「大师点评」收尾**——4-6位虚拟大师从实战视角校准AI结论，严防AI幻觉，用芒格10大思维模型检查盲区，详见 [master-review.md](references/master-review.md)

## 触发指令与对应流程

| 指令 | 执行内容 | 详细规则 |
|------|---------|---------|
| `扫描今日短线机会` | 市场情绪+主线板块+连板梯队+异动个股 | 见 [shortline.md](references/shortline.md) |
| `指数风控扫描` | 全市场指数技术诊断+资金面+跨市场联动+仓位风控建议 | 见 [index-scan.md](references/index-scan.md) |
| `综合分析报告` | 四维全景评估+涨跌停复盘+短线情绪扫描+大盘风控+景气校验+技术诊断+均线双轨+盈亏比完整方案 | 见 [comprehensive.md](references/comprehensive.md) |
| `查看XXX板块` | 四维全景评估+板块生命周期+题材等级+资金+景气+技术+均线双轨+盈亏比 | 见 [sector.md](references/sector.md) |
| `分析XXX股票` | 四维全景评估+区分短长线，量价+资金+筹码+基本面+同业对标+公告+景气+技术+均线双轨+研报+盈亏比 | 见 [stock.md](references/stock.md) |

## 综合分析总流程（通用框架）

1. **数据采集**：使用 `finance-data-retrieval` / `neodata-financial-search` 获取行情、资金、技术指标数据；搭配 akshare 程序化取数。**所有采集数据必须标注采集时间戳与数据截止日期**
2. **四维全景环境评估**：政策/行业/资金/情绪四维；见 [environment-assessment.md](references/environment-assessment.md)
3. **短线情绪扫描+涨跌停复盘**：见 [limit-analysis.md](references/limit-analysis.md)
4. **大盘+板块双重风控**：筹码辅助验证（若数据可获取）+ 均线系统双轨判定（超短线60分钟MA + 中长线日线MA）
5. **护城河深度分析**（个股/板块必做）：见 [moat.md](references/moat.md)
6. **参与者博弈全景**（个股/板块必做）：见 [game-theory.md](references/game-theory.md)
7. **多因子共振校验**：资金、情绪、量价、题材、筹码、技术指标（均线/MACD/RSI/SKDJ），中长线叠加行业景气判定；详见 [technical.md](references/technical.md)
8. **盈亏比×胜率测算**：计算标准化潜在盈亏比、估算胜率区间、输出期望值
9. **仓位匹配**：根据期望值和风控规则匹配仓位，设定止盈止损；详见 [risk-control.md](references/risk-control.md)
10. **输出方案**：操作策略 + 风险等级 + 参与者状态 + 产业提示 + 交易期望值评级
11. **大师点评（胜率校准）**：见 [master-review.md](references/master-review.md)
12. **渲染交付**：将完整分析报告渲染为HTML文档交付给用户，见 [html-spec.md](references/html-spec.md)

## 数据获取规范

- 优先级：`neodata-financial-search`（第一）> `finance-data-retrieval`（第二）> WebSearch（第三）
- **数据可信度分级**：交易所原始数据（Tier 1）> Wind/Choice（Tier 2）> akshare/NEODATA（Tier 3）> WebSearch（Tier 4）
- 常规采集：筹码峰周期、成本区间、资金流向、量价数据、全维度技术指标（日线均线5/10/20/60、60分钟均线5/10/20及状态）
- 中长线补充：行业产能周期、景气增速、机构一致预期、长期政策规划数据
- 新闻仅采信3日内权威来源（交易所官网、证券时报、上海证券报、东方财富、同花顺），过期资讯标注禁止用于实盘
- 技术指标参数为默认值（日线均线5/10/20/60、60分钟均线5/10/20、MACD 12,26,9、RSI 14、SKDJ 9,3,3），**禁止AI自行更改参数**
- ⚠️ **回测声明**：本体系盈亏比区间为理论推演值，未经历史数据回测验证

## 盈亏比计算公式

```
潜在盈亏比 = 预期盈利空间 / 最大亏损空间
  预期盈利空间 = 目标价（止盈位）- 买入价
  最大亏损空间 = 买入价 - 止损位（关键支撑位下方2%-3%）

交易期望值 = 盈亏比 × 预估胜率

胜率估算维度：
  - 技术共振因子数量：≥4因子同向 → 胜率55%-65%；3因子 → 45%-55%；<3因子 → <45%
  - 市场情绪状态：平稳 → +5%；亢奋/弱势 → -10%
  - 板块景气等级：S/A级 → +5%；B级 → 不调整；C/D级 → -15%
  - 资金面配合：主力持续流入 → +5%

动态调整触发：
  - 市场突发重大利空 → 全局盈亏比×0.7
  - 板块内出现龙头跌停 → 板块盈亏比×0.8
  - 北向资金单日净流出>100亿 → 大盘盈亏比×0.8
  - 四维全景评估🔴高风险 → 盈亏比×0.7；🟡中风险 → ×0.9；🟠警示 → ×0.85
```

## 详细规则参考

| 规则 | 文件 |
|------|------|
| 超短线扫描 | [shortline.md](references/shortline.md) |
| 全市场指数风控 | [index-scan.md](references/index-scan.md) |
| 综合分析报告 | [comprehensive.md](references/comprehensive.md) |
| 板块分析 | [sector.md](references/sector.md) |
| 个股分析 | [stock.md](references/stock.md) |
| 技术指标共振 | [technical.md](references/technical.md) |
| 四维全景环境评估 | [environment-assessment.md](references/environment-assessment.md) |
| 涨跌停复盘 | [limit-analysis.md](references/limit-analysis.md) |
| 研报结论分析 | [research-report.md](references/research-report.md) |
| 信号共振与风控 | [risk-control.md](references/risk-control.md) |
| 筹码分析 | [chip.md](references/chip.md) |
| 护城河深度分析 | [moat.md](references/moat.md) |
| 参与者博弈分析 | [game-theory.md](references/game-theory.md) |
| 大师点评 | [master-review.md](references/master-review.md) |
| 交易铁律与复盘 | [trading-rules.md](references/trading-rules.md) |
| 置信度与回测验证 | [backtest.md](references/backtest.md) |
| HTML报告输出规范 | [html-spec.md](references/html-spec.md) |

## 风险声明

股市存在政策波动、流动性变化、行业周期与结构性回调风险。本体系仅为交易逻辑参考，不构成投资建议。

**当前体系处于🔬理论值阶段**，所有盈亏比、胜率、期望值为理论推演值，未经历史数据回测验证。详见 [backtest.md](references/backtest.md)。
