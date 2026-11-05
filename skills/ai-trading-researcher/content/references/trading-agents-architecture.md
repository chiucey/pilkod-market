# TradingAgents 框架架构参考

## 项目信息

- **GitHub**: https://github.com/TauricResearch/TradingAgents
- **Stars**: 44.1k
- **License**: Apache-2.0
- **语言**: Python 100%

## 框架架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    TradingAgents Framework                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │   Analyst   │    │  Researcher │    │    Trader    │   │
│  │    Team     │───▶│    Team      │───▶│    Agent     │   │
│  └─────────────┘    └─────────────┘    └─────────────┘   │
│         │                  │                  │             │
│  ┌──────┴──────┐    ┌──────┴──────┐    ┌──────┴──────┐    │
│  │ Fundamentals│    │   Bullish   │    │  Risk Mgmt  │    │
│  │  Analyst     │    │  Researcher  │    │    Team     │    │
│  ├──────────────┤    ├──────────────┤    ├──────────────┤    │
│  │  Sentiment   │    │   Bearish    │    │  Portfolio   │    │
│  │  Analyst     │    │  Researcher  │    │   Manager    │    │
│  ├──────────────┤    └──────────────┘    └──────────────┘    │
│  │    News      │                                            │
│  │  Analyst     │                                            │
│  ├──────────────┤                                            │
│  │  Technical   │                                            │
│  │  Analyst     │                                            │
│  └──────────────┘                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 代理详细说明

### 1. 分析师团队 (Analyst Team)

#### 基本面分析师 (Fundamentals Analyst)
- **职能**: 评估公司财务报表和业绩指标
- **分析内容**:
  - 营收和利润趋势
  - 利润率分析
  - 资产负债表健康度
  - 估值比率（P/E, P/B, P/S 等）
  - 现金流分析
- **输出**: 公司内在价值评估、潜在红旗信号

#### 情绪分析师 (Sentiment Analyst)
- **职能**: 分析市场情绪和投资者心理
- **分析内容**:
  - 社交媒体情绪趋势
  - 新闻情绪评分
  - 分析师评级共识
  - 期权市场情绪指标
- **输出**: 短期市场情绪报告、情绪转折点预警

#### 新闻分析师 (News Analyst)
- **职能**: 监控和解读影响市场的事件
- **分析内容**:
  - 重大新闻事件
  - 宏观经济指标
  - 行业动态
  - 政策变化影响
- **输出**: 新闻影响评估、事件驱动分析

#### 技术分析师 (Technical Analyst)
- **职能**: 识别价格模式和交易信号
- **分析工具**:
  - MACD (Moving Average Convergence Divergence)
  - RSI (Relative Strength Index)
  - 移动平均线 (MA)
  - 布林带 (Bollinger Bands)
  - 成交量分析
- **输出**: 技术信号报告、支撑阻力位、价格预测

### 2. 研究员团队 (Researcher Team)

#### 多头研究员 (Bullish Researcher)
- **职能**: 评估投资的正面论据
- **分析重点**:
  - 增长潜力
  - 竞争优势
  - 积极催化剂
  - 估值修复空间

#### 空头研究员 (Bearish Researcher)
- **职能**: 识别投资风险和负面因素
- **分析重点**:
  - 下行风险
  - 竞争威胁
  - 估值过高风险
  - 潜在负面事件

### 3. 交易代理 (Trader Agent)

- **职能**: 综合所有分析形成交易决策
- **决策因素**:
  - 分析师共识
  - 多空辩论结果
  - 风险收益比
  - 时机选择
- **输出**: 交易信号、持仓建议、目标价格

### 4. 风险管理团队 (Risk Management Team)

- **职能**: 评估和控制交易风险
- **风险因素**:
  - 市场波动性
  - 流动性风险
  - 集中度风险
  - 杠杆风险
- **输出**: 风险评估报告、仓位限制建议

### 5. 投资组合经理 (Portfolio Manager)

- **职能**: 最终交易决策
- **职责**:
  - 审核交易提案
  - 批准/否决交易
  - 分配资金
  - 监控投资组合表现

## 工作流程

```
用户输入股票代码
       │
       ▼
┌─────────────────┐
│  TradingAgents  │
│     Graph       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Analyst Team   │
│ (4个分析师并行) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Researcher     │
│  Team           │
│ (多空辩论)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Trader        │
│   Agent         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Risk Management │
│     Team        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Portfolio     │
│   Manager       │
└────────┬────────┘
         │
         ▼
   交易决策输出
```

## 支持的 LLM 提供商

| 提供商 | 模型示例 | 配置参数 |
|--------|----------|----------|
| OpenAI | GPT-4o, GPT-4o-mini, GPT-5.x | `llm_provider: "openai"` |
| Google | Gemini 1.5, Gemini 2.0 | `llm_provider: "google"` |
| Anthropic | Claude 3.5, Claude 4.x | `llm_provider: "anthropic"` |
| xAI | Grok 2, Grok 3 | `llm_provider: "xai"` |
| OpenRouter | 多模型聚合 | `llm_provider: "openrouter"` |
| Ollama | 本地模型 | `llm_provider: "ollama"` |

## 数据源

| 数据类型 | 默认数据源 | 备选方案 |
|----------|------------|----------|
| 股票价格 | yfinance | Alpha Vantage |
| 技术指标 | yfinance | 自定义计算 |
| 基本面数据 | Alpha Vantage | OpenAI/Google API |
| 新闻数据 | Alpha Vantage | 聚合新闻源 |
| 情绪数据 | 内置算法 | 第三方情绪 API |

## API 密钥配置

```bash
# 必需
export OPENAI_API_KEY=...       # OpenAI (GPT)
export ALPHA_VANTAGE_API_KEY=... # Alpha Vantage

# 可选
export GOOGLE_API_KEY=...       # Google (Gemini)
export ANTHROPIC_API_KEY=...    # Anthropic (Claude)
export XAI_API_KEY=...          # xAI (Grok)
export OPENROUTER_API_KEY=...   # OpenRouter
```

## 版本历史

- **v0.2.3** (2026-03): 多语言支持、GPT-5.4 系列模型
- **v0.2.2** (2026-03): 五级评分系统、OpenAI Responses API
- **v0.2.0** (2026-02): 多提供商 LLM 支持
