---
name: lhmxstock
description: Multi-agent LLM stock trading and analysis framework. Use when users ask for stock analysis, trading decisions, market research, investment recommendations, portfolio management, or quantitative trading strategies. A professional multi-agent framework that simulates institutional research team collaboration.
---

# LHMXstock: Multi-Agent Stock Trading Analysis Framework

## Framework Overview

LHMXstock is a multi-agent collaborative stock trading analysis framework that simulates the operations of professional investment research institutions. By deploying specialized LLM-powered agents—including fundamental analysts, sentiment experts, technical analysts, traders, and risk management teams—they collaboratively evaluate market conditions and provide trading decision recommendations. These agents develop optimal strategies through dynamic discussions.

> **Disclaimer**: LHMXstock framework is designed for research purposes only. Trading performance may vary based on many factors including underlying language models, model temperature, trading periods, data quality, and other non-deterministic factors. This framework does not constitute financial, investment, or trading advice.

---

## Agent Architecture

### 1. Analyst Team

#### Fundamentals Analyst
- **Responsibilities**: Evaluate company financial health and performance metrics
- **Capabilities**:
  - Analyze core financial data including revenue, profit, and cash flow
  - Identify intrinsic value and potential risk signals
  - Compare with industry competitors
  - Assess valuation levels (PE, PB, PS ratios, etc.)

#### Sentiment Analyst
- **Responsibilities**: Analyze social media and public sentiment
- **Capabilities**:
  - Monitor social platform discussions and trends
  - Quantify market sentiment using sentiment scoring algorithms
  - Track investor attention and market hotspots
  - Identify sentiment reversal signals

#### News Analyst
- **Responsibilities**: Monitor global news and macroeconomic indicators
- **Capabilities**:
  - Track major financial news events
  - Analyze macroeconomic event impacts on markets
  - Monitor policy changes and regulatory developments
  - Evaluate event-driven trading opportunities

#### Technical Analyst
- **Responsibilities**: Analyze price trends using technical indicators
- **Capabilities**:
  - MACD, RSI, Bollinger Bands and other indicator analysis
  - Trend line, support/resistance level identification
  - Volume-price relationship analysis
  - Price pattern recognition and prediction

### 2. Research Team

#### Bullish Researcher
- **Responsibilities**: Evaluate investment opportunities from a positive perspective
- **Capabilities**:
  - Identify company growth potential
  - Recognize positive catalysts
  - Build bull case arguments
  - Assess upside potential

#### Bearish Researcher
- **Responsibilities**: Evaluate investment risks from a risk perspective
- **Capabilities**:
  - Identify potential risk factors
  - Build bear case arguments
  - Assess downside risk
  - Provide risk warnings

### 3. Trader Agent

- **Responsibilities**: Synthesize analysis reports and make trading decisions
- **Capabilities**:
  - Aggregate analyst and researcher viewpoints
  - Weigh bull and bear arguments
  - Determine entry timing and position sizing
  - Define stop-loss and take-profit strategies

### 4. Risk Management Team

- **Responsibilities**: Continuously evaluate portfolio risk
- **Capabilities**:
  - Assess market volatility risk
  - Monitor liquidity risk
  - Evaluate position concentration risk
  - Provide risk-adjusted recommendations

### 5. Portfolio Manager

- **Responsibilities**: Final trading decision approval
- **Capabilities**:
  - Review trading proposals
  - Assess risk-reward ratios
  - Decide execution or rejection
  - Monitor overall portfolio performance

---

## Technical Architecture

### Core Framework
- **LangGraph**: For building flexible and scalable agent workflows
- **Modular Design**: Each agent operates independently and is configurable
- **Extensible Architecture**: Supports adding custom agents and data sources

### Language Model Support
| Type | Recommended Models | Description |
|------|-------------------|-------------|
| Deep Thinking Models | o1-preview, o4-mini, gpt-4.1 | Used for complex analysis and reasoning |
| Quick Thinking Models | gpt-4o, gpt-4.1-mini | Used for simple queries and summarization |

### Data Source Configuration
| Data Type | Default Option | Alternatives |
|-----------|----------------|--------------|
| Stock Data | yfinance | alpha_vantage, akshare |
| Technical Indicators | yfinance | custom calculation |
| Fundamental Data | alpha_vantage | openai, local data |
| News Data | alpha_vantage | Sina Finance, East Money |

---

## Usage Methods

### Basic Usage

```python
from lhmxstock.graph.trading_graph import LHMXStockGraph
from lhmxstock.default_config import DEFAULT_CONFIG

# Initialize trading graph
graph = LHMXStockGraph(debug=True, config=DEFAULT_CONFIG.copy())

# Execute analysis
_, decision = graph.propagate("AAPL", "2024-05-10")
print(decision)
```

### Custom Configuration

```python
from lhmxstock.graph.trading_graph import LHMXStockGraph
from lhmxstock.default_config import DEFAULT_CONFIG

# Create custom configuration
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4.1-nano"
config["quick_think_llm"] = "gpt-4.1-nano"
config["max_debate_rounds"] = 2
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "alpha_vantage",
    "news_data": "akshare",
}

graph = LHMXStockGraph(debug=True, config=config)
_, decision = graph.propagate("TSLA", "2024-06-15")
print(decision)
```

### Configuration Options

```python
DEFAULT_CONFIG = {
    # LLM Configuration
    "llm_provider": "openai",  # openai, google, anthropic, xai, ollama
    "deep_think_llm": "gpt-4.1",
    "quick_think_llm": "gpt-4.1-mini",

    # Debate Rounds
    "max_debate_rounds": 2,

    # Data Source Configuration
    "data_vendors": {
        "core_stock_apis": "yfinance",
        "technical_indicators": "yfinance",
        "fundamental_data": "alpha_vantage",
        "news_data": "alpha_vantage",
    },

    # API Keys
    "api_keys": {
        "openai": None,
        "alpha_vantage": None,
    },

    # Debug Mode
    "debug": False,
}
```

---

## Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                      LHMXstock Workflow                          │
└─────────────────────────────────────────────────────────────────┘

1. Input Processing
   ├── Receive stock ticker (e.g.: AAPL, TSLA, 600519.SS)
   ├── Receive analysis date
   └── Load configuration and API keys

2. Data Collection Phase
   ├── Fundamental data collection
   ├── Technical indicator calculation
   ├── News data acquisition
   └── Sentiment data gathering

3. Analysis Phase
   ├── Fundamental analysis
   ├── Technical analysis
   ├── News impact assessment
   └── Sentiment analysis

4. Debate Phase (Multiple Rounds)
   ├── Bullish researcher presents bull case
   ├── Bearish researcher presents bear case
   ├── Inter-agent discussion and rebuttal
   └── Form balanced assessment conclusions

5. Trading Decision
   ├── Trader aggregates all viewpoints
   ├── Develop trading strategy
   └── Submit for risk management review

6. Risk Review
   ├── Risk team assessment
   ├── Portfolio manager approval
   └── Execute or reject trade

7. Output Results
   ├── Comprehensive analysis report
   ├── Trading recommendations
   └── Risk warnings
```

---

## Configuration Requirements

### Environment Variables

```bash
# LLM Provider API Keys
export OPENAI_API_KEY=your_openai_api_key
export GOOGLE_API_KEY=your_google_api_key
export ANTHROPIC_API_KEY=your_anthropic_api_key

# Data Source API Keys
export ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
```

### Dependencies

```
langgraph>=0.0.15
langchain>=0.1.0
yfinance>=0.2.0
pandas>=2.0.0
numpy>=1.24.0
python-dotenv>=1.0.0
```

---

## Output Examples

### Stock Analysis Report

```json
{
  "ticker": "AAPL",
  "analysis_date": "2024-05-10",
  "analyst_reports": {
    "fundamental": {
      "score": 8.5,
      "highlights": ["Revenue up 12%", "Gross margin stable at 38%", "Strong cash flow"],
      "concerns": ["iPhone sales growth slowing", "Greater China revenue decline"]
    },
    "technical": {
      "score": 7.0,
      "signals": ["RSI in neutral zone", "MACD golden cross forming", "Breaking above 50-day MA"],
      "trend": "Consolidating upward"
    },
    "sentiment": {
      "score": 7.5,
      "overall": "Slightly positive",
      "highlights": ["Analyst ratings upgraded", "Social media attention increasing"]
    },
    "news": {
      "score": 8.0,
      "impact": "Positive",
      "key_events": ["Earnings beat expectations", "AI strategy announcement"]
    }
  },
  "debate_summary": {
    "bullish_points": ["Reasonable valuation", "Leading AI positioning", "Services revenue growth"],
    "bearish_points": ["Hardware growth slowing", "Increasing competition", "Regulatory risks"]
  },
  "trading_decision": {
    "action": "BUY",
    "confidence": 0.75,
    "entry_price": "185.50",
    "stop_loss": "175.00",
    "target_price": "200.00",
    "position_size": "10%"
  },
  "risk_assessment": {
    "overall_risk": "Medium",
    "volatility": "Medium",
    "liquidity": "Excellent"
  }
}
```

---

## Use Cases

1. **In-depth Stock Analysis**: Comprehensive analysis of specific stocks
2. **Investment Decision Support**: Trading recommendations and risk assessment
3. **Portfolio Diagnostics**: Evaluate risk-return characteristics of existing positions
4. **Market Research**: Analyze market hotspots and sector rotation
5. **Quantitative Strategy Development**: Research framework for algorithmic trading strategies
6. **Research Report Generation**: Automatically generate structured analysis reports

---

## Limitations

1. **Model Dependency**: Analysis quality depends on the underlying LLM capabilities
2. **Data Latency**: Real-time data may have delays
3. **Historical Backtesting**: Past performance does not indicate future returns
4. **Non-deterministic**: Same inputs may produce different outputs
5. **Risk Management**: Cannot guarantee avoidance of all investment risks

---

*LHMXstock - Intelligent Research, Smarter Decisions*
