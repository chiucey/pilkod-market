---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100fbe0e392fb176d678ef9264302e479582949eee907d274bccb2eae210b61f1a202201897c9bf27dd6f42b7cde98bdf5d448d80a37aa5d5dc1640cb8fcfcfee143958
    ReservedCode2: 3044022057550921b009654cabaa087866f86d7bdf3e84748f4209250e0901451806dc4002205ef4ded5763f3548eb52b85f2d0454aeb49235502a1e27db030ec66899bb6c21
compatibility: 需要 Python 3.8+，依赖 akshare（A股/港股数据）、yfinance（美股数据）、pandas、matplotlib
description: 上市公司金融分析技能。对A股、港股、美股等上市公司进行全面深度分析，涵盖基本面（财务报表、估值指标）、技术面（价格走势、技术指标）、消息面（新闻动态、政策影响），结合宏观政策给出投资建议，输出目标价位、上升空间、风险点，并生成专业HTML格式的研究报告。当用户要求分析股票、研究上市公司、评估投资价值、生成股票报告、查询财务数据时使用此技能。
license: MIT
metadata:
    author: MiniMax
    tags:
        - financial-analysis
        - stock-research
        - investment-analysis
        - report-generation
    version: "1.0"
name: financial-report
---

# 上市公司金融分析报告技能

## 何时使用此技能

当用户提出以下需求时，应激活此技能：

- "分析 [股票代码/公司名称]"
- "生成 [股票] 的研究报告"
- "评估 [股票] 的投资价值"
- "查询 [公司] 的财务数据"
- "帮我研究这只股票"
- "这只股票怎么样"
- "给出 [股票] 的投资建议"
- 任何涉及股票分析、财务评估、投资研究的请求

## 分析框架

本技能采用多维度分析框架，从四个层面全面评估上市公司：

### 1. 基本面分析 (Fundamental Analysis)

**数据收集：**
- 使用 `stocks_financial_data` 工具获取财务报表
- 使用 `stocks_info` 工具获取公司基本信息
- 使用 `stocks_statistics` 工具获取估值指标

**分析维度：**

| 维度 | 指标 | 说明 |
|------|------|------|
| 盈利能力 | 营收、净利润、毛利率、净利率、ROE | 评估公司赚钱能力 |
| 成长性 | 营收增速、净利润增速 | 评估公司成长潜力 |
| 财务健康 | 资产负债率、流动比率、现金流 | 评估财务风险 |
| 估值水平 | PE、PB、PS、PEG | 评估当前估值高低 |
| 股息率 | 分红率、股息率 | 评估股东回报 |

**输出格式：**
```
基本面评分：X/10
核心指标：
- 营业收入：[X]亿，同比增长[X%]
- 净利润：[X]亿，同比增长[X%]
- 毛利率：[X]%
- ROE：[X]%
- PE：[X]倍（历史[X]%分位）
- PB：[X]倍（历史[X]%分位）
```

### 2. 技术面分析 (Technical Analysis)

**数据收集：**
- 使用 `stocks_price` 工具获取历史价格数据
- 至少获取 1 年的日线数据

**分析指标：**

| 指标 | 说明 | 交易信号 |
|------|------|----------|
| 均线系统 | MA5、MA10、MA20、MA60、MA120、MA250 | 金叉/死叉 |
| MACD | DIF、DEA、MACD柱 | 顶背离/底背离 |
| RSI | 6日、12日、24日RSI | 超买/超卖 |
| KDJ | K、D、J值 | 超买/超卖 |
| 布林带 | 上轨、中轨、下轨 | 突破/回踩 |
| 成交量 | 量能变化、量比 | 放量/缩量 |

**技术面评分逻辑：**
- 上升趋势（均线多头排列）：+3分
- MACD 金叉：+2分
- RSI 处于合理区间（40-70）：+2分
- 成交量配合：+2分
- 布林带中轨上方：+1分

### 3. 消息面分析 (News & Sentiment Analysis)

**数据收集：**
- 使用 `stocks_news` 工具获取最新新闻
- 使用 `batch_web_search` 搜索行业动态、政策变化

**分析维度：**

| 维度 | 内容 | 影响 |
|------|------|------|
| 公司新闻 | 业绩公告、重大合同、管理层变动 | 直接影响 |
| 行业动态 | 行业政策、竞争格局变化 | 行业影响 |
| 宏观政策 | 货币政策、财政政策、行业监管 | 系统性影响 |
| 机构观点 | 券商研报、评级变化、目标价 | 机构情绪 |

### 4. 宏观政策分析 (Macro & Policy Analysis)

**分析要点：**
- 宏观经济周期（复苏/繁荣/衰退/萧条）
- 货币政策取向（宽松/紧缩）
- 财政政策导向（刺激/收敛）
- 行业监管政策（支持/限制）
- 国际环境变化（汇率、贸易摩擦等）

## 分析工作流程

### 步骤 1：信息收集（并行执行）

```
并行启动以下数据收集任务：
├── 启动 fundamentals_analyst → 财务报表深度分析
├── 启动 technical_analyst → 技术面分析
├── 启动 news_analyst → 公司动态追踪
└── 启动 sentiment_analyst → 市场情绪分析
```

### 步骤 2：观点碰撞

```
基于分析师报告：
├── 启动 bullish_researcher → 构建正面投资逻辑
└── 启动 bearish_researcher → 识别风险与隐忧
```

### 步骤 3：风险评估

```
启动 risk_manager → 综合风险评估
```

### 步骤 4：事实核查

```
启动 fact_checker → 对关键数据和事实进行二次核查验证
```

### 步骤 5：生成报告

根据 `assets/report_template.html` 模板生成专业 HTML 报告。

## 输出格式

### 研究报告核心内容

```markdown
## 📊 公司研究报告：[公司名称]（[股票代码]）

### 研究摘要
[公司核心业务、行业地位、当前估值水平的概述]

### 财务分析
| 指标 | 最新值 | 同比变化 | 行业对比 |
|------|--------|----------|----------|
| 营业收入 | [X]亿 | [+/-X%] | [优/中/弱] |
| 净利润 | [X]亿 | [+/-X%] | [优/中/弱] |
| 毛利率 | [X]% | [+/-Xpp] | [优/中/弱] |
| ROE | [X]% | [+/-Xpp] | [优/中/弱] |

### 估值分析
| 估值指标 | 当前值 | 历史分位 | 行业均值 |
|----------|--------|----------|----------|
| 市盈率(PE) | [X] | [X]% | [X] |
| 市净率(PB) | [X] | [X]% | [X] |
| 市销率(PS) | [X] | [X]% | [X] |

### 技术分析
| 指标 | 当前值 | 信号 |
|------|--------|------|
| MA均线 | 多头/空头/缠绕 | 看涨/看跌/中性 |
| MACD | [X] | 金叉/死叉 |
| RSI | [X] | 超买/超卖/合理 |
| 布林带 | [X] | 突破/回踩 |

### 机构观点
- 券商评级：[买入/增持/中性/减持] [X]家
- 目标价区间：[X] - [X] 元
- 一致预期：[简述]

### 核心竞争力
- [竞争优势1]
- [竞争优势2]

### 风险因素
- [风险1]
- [风险2]

### 投资建议
**目标价**：[X] 元
**上升空间**：[X]%
**止损价**：[X] 元
**核心逻辑**：[一段话总结]

### 综合评估
**投资价值**：🟢 高 / 🟡 中等 / 🔴 低
**风险等级**：⚠️ 高 / 中 / 低

### ⚠️ 免责声明
- 本报告由AI生成，仅供研究参考
- 不构成投资建议，请独立判断
```

## 数据来源

### A股/港股数据

```python
import akshare as ak

# 公司基本信息
stock_info = ak.stock_individual_info_em(symbol="600519")

# 财务报表
balance_sheet = ak.stock_balance_sheet_by_report_em(symbol="600519")
income = ak.stock_profit_sheet_by_report_em(symbol="600519")
cash_flow = ak.stock_cash_flow_sheet_by_report_em(symbol="600519")

# 财务指标
fin_indicator = ak.stock_financial_analysis_indicator(symbol="600519")

# 港股数据
hk_hist = ak.stock_hk_hist(symbol="00700", period="daily", adjust="qfq")
```

### 美股数据

```python
import yfinance as yf

stock = yf.Ticker("AAPL")
info = stock.info
financials = stock.financials
balance_sheet = stock.balance_sheet
cash_flow = stock.cashflow
```

## 辅助工具

### 股价查询
使用 `stocks_price` 工具批量获取股票价格数据：
```
queries: [{"symbol": "600519.SS", "start_date": "2023-01-01", "end_date": "2024-04-15"}]
```

### 新闻查询
使用 `stocks_news` 工具获取公司最新新闻：
```
queries: [{"symbol": "AAPL", "snippet_count": 10}]
```

### 网络搜索
使用 `batch_web_search` 获取：
- 最新券商研报和目标价
- 行业政策变化
- 公司重大事项

## 报告生成

### HTML 报告模板

使用 `assets/report_template.html` 模板生成报告。模板特性：

- **视觉风格**：黑色背景 (#0a0a0a)，专业交易员风格
- **配色方案**：绿色系（上涨）、红色系（下跌）、灰色系（中性）
- **图表展示**：使用 Chart.js 绑定价格走势图、财务指标柱状图
- **响应式设计**：支持桌面端和移动端

### 报告部署

生成 HTML 报告后：

1. 使用 `Write` 工具保存报告文件
2. 使用 `deploy` 工具部署到线上
3. 提供可访问的 URL 给用户

## 常见问题处理

### Q1：股票代码格式
- A股：600519.SS（上交所）、000001.SZ（深交所）
- 港股：00700.HK、09988.HK
- 美股：直接使用代码，如 AAPL、TSLA

### Q2：数据缺失处理
- 若某个财务指标无法获取，标注为"暂不可用"
- 若历史数据不足1年，技术分析可靠性降低，需特别说明

### Q3：多股票对比
- 支持同时分析多只股票
- 生成对比分析报告
- 使用表格展示关键指标对比

### Q4：报告语言
- 用户使用中文时，报告使用中文
- 用户使用英文时，报告使用英文
- 保持术语一致性

## 相关文件

- `scripts/fetch_data.py` - 数据获取脚本
- `scripts/analysis.py` - 分析计算脚本
- `scripts/generate_report.py` - 报告生成脚本
- `references/ANALYSIS_GUIDE.md` - 分析方法论详解
- `references/INDICATORS.md` - 财务指标参考
- `references/MARKETS.md` - 市场规则说明
- `assets/report_template.html` - HTML 报告模板
- `assets/styles.css` - 报告样式表

## 更新日志

- v1.0 (2024-04-15): 初始版本，包含完整的四维度分析框架和报告生成功能
