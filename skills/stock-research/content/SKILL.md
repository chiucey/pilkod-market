---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: d7487db244500c80b93c88e86c8f5396
    PropagateID: d7487db244500c80b93c88e86c8f5396
    ReservedCode1: 3045022025d74c64cc98ed77fb464100fb5a9848a50a0f628b05f52cd589cef9ea9f3f03022100f56757cb1681c860c35dc421dc59b9dc3c4d28672a5edfa251e67bdde08678c1
    ReservedCode2: 3045022100fb923559a283ca49398ac0147d719db9966b1c801bc7a54939c3b468278ec63d02203cb93f96be8aab7067b5436b8f2fdbc546436ba93beb0d756ed9921bc2aea64f
description: |-
    股票研究与全球事件影响分析 Skill。当用户说"分析股票"、"研究上市公司"、"分析行情"、
    "分析全球事件对市场的影响"、"股票研报"、"XX股票怎么样"、"帮我看一个股票"时激活。
    支持A股（akshare）、港股、美股（yfinance）的数据查询、财报分析、技术面分析、
    宏观事件影响评估，并生成可交互的HTML Dashboard。
name: stock-research
---

# Stock Research Skill

## 数据来源

### A股数据（akshare）
```python
import akshare as ak

# 公司基本信息
stock_info = ak.stock_individual_info_em(symbol="600519")

# 实时行情
stock_zh_a_spot_em()  # 全市场实时行情

# 财务报表
balance = ak.stock_balance_sheet_by_report_em(symbol="600519")  # 资产负债表
income = ak.stock_profit_sheet_by_report_em(symbol="600519")   # 利润表
cashflow = ak.stock_cash_flow_sheet_by_report_em(symbol="600519") # 现金流量表

# 财务指标
fin_indicator = ak.stock_financial_analysis_indicator(symbol="600519")

# 基金持仓（机构持股）
fund_holding = ak.stock_report_fund_hold(symbol="600519")

# 个股历史行情
stock_zh_a_hist(symbol="600519", period="daily", adjust="qfq")

# 龙虎榜（资金动向）
stock_lhb_detail_em(symbol="600519")
```

### 港股数据
```python
hk_hist = ak.stock_hk_hist(symbol="00700", period="daily", adjust="qfq")
hk_info = ak.stock_hk_spot_em()  # 港股实时行情
```

### 美股数据（yfinance）
```python
import yfinance as yf

stock = yf.Ticker("AAPL")
info = stock.info  # 基本信息
financials = stock.financials       # 利润表
balance_sheet = stock.balance_sheet  # 资产负债表
cashflow = stock.cashflow           # 现金流量表
history = stock.history(period="1y")  # 历史行情
```

## 研究工作流程

### Step 1: 收集基本信息
- 判断市场（A/港/美）→ 调用对应数据接口
- 获取公司简称、主营业务、最新股价、总市值
- 搜索最新新闻和公告

### Step 2: 多维度并行分析
并行启动分析师：
- **基本面**：营收、净利润、毛利率、ROE、EPS、估值指标
- **技术面**：均线、成交量、MACD、布林带、支撑压力位
- **新闻面**：最近3个月重大新闻、政策影响、管理层动态
- **机构观点**：券商评级、目标价、盈利预测

### Step 3: 事件影响评估
- 搜索相关新闻（地缘政治、央行政策、行业政策）
- 分析事件对公司的正面/负面影响
- 评估市场整体情绪

### Step 4: 生成研究报告
输出标准格式Markdown，包含：财务摘要、估值分析、技术面判断、机构观点、风险评估

### Step 5: 生成 Dashboard
将分析结果打包为可交互HTML Dashboard，部署并提供链接：
- 黑色/白色极简风格
- 财务数据卡片
- 估值指标仪表盘
- 技术K线图（Chart.js）
- 风险雷达图
- 投资评级展示

## Dashboard 模板结构

```
/workspace/stock-dashboard/
├── index.html          # 主页面（分析结果嵌入）
├── chart.js            # Chart.js（CDN引入）
└── style.css           # 极简样式
```

## A股常用指标计算

```python
# 估值指标
PE = 市值 / 净利润  # 市盈率
PB = 市值 / 净资产  # 市净率
PS = 市值 / 营收    # 市销率

# 盈利能力
ROE = 净利润 / 净资产 * 100  # 净资产收益率
毛利率 = (营收 - 成本) / 营收 * 100
净利率 = 净利润 / 营收 * 100

# 成长性
营收增速 = (本期营收 - 上期营收) / 上期营收 * 100
净利润增速 = (本期净利润 - 上期净利润) / 上期净利润 * 100
```

## 新闻分析 Prompt 模板

"请分析以下新闻对[公司名/行业]的影响：
- 正面因素：
- 负面因素：
- 短期影响：
- 长期影响：
- 风险提示："

## 风险评估维度

1. **经营风险**：行业竞争、管理层变动、主营业务衰退
2. **财务风险**：负债率、现金流、应收账款
3. **市场风险**：估值过高、市场情绪、技术破位
4. **政策风险**：行业监管、宏观经济政策
5. **流动性风险**：成交量过低、股东减持

## 输出规范

每次研究必须包含：
- 📊 财务摘要表格
- 💰 估值分析（PE/PB/PS + 历史分位）
- 📈 技术面判断
- 🏢 核心竞争力
- ⚠️ 风险因素
- 🤖 综合评级（高/中/低）

⚠️ 免责声明必须包含："本报告由AI生成，仅供研究参考，不构成投资建议"
