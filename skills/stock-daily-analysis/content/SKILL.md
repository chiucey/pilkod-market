---
name: stock-daily-analysis
description: LLM-powered daily stock analysis system. Supports A-share/HK/US stock analysis with technical indicators (MA5/10/20, MACD, RSI, BIAS), trend analysis, and buy signal scoring. Triggers: stock analysis, analyze stocks, daily analysis, technical analysis, stock diagnosis, stock screening.
---

# Stock Daily Analysis Skill

LLM-powered daily stock analysis system providing A-share/HK/US stock technical analysis and AI decision recommendations for OpenClaw.

## Core Functions

1. **Multi-Market Support** - A-share, HK, US stock data
2. **Technical Analysis** - MA5/10/20, MACD, RSI, BIAS indicators
3. **Trend Trading** - Trend alignment detection, buy signal scoring
4. **AI Decision** - DeepSeek/Gemini deep analysis

## Usage

### Basic Analysis

```python
from scripts import analyze_stock, analyze_stocks

# Single stock analysis
result = analyze_stock('600519')
print(result['ai_analysis']['operation_advice'])

# Batch analysis
results = analyze_stocks(['600362', '601318', '159892'])
```

### Direct Function Calls

```python
from scripts.data_fetcher import get_daily_data, get_realtime_quote
from scripts.trend_analyzer import StockTrendAnalyzer

# Get data
df = get_daily_data('600519', days=60)
quote = get_realtime_quote('600519')

# Technical analysis
analyzer = StockTrendAnalyzer()
result = analyzer.analyze(df, '600519')
print(f"Trend: {result.trend_status.value}")
print(f"Signal: {result.buy_signal.value} (Score: {result.signal_score})")
```

## Configuration

Copy `config.example.json` to `config.json` and configure:

```json
{
  "ai": {
    "provider": "openai",
    "api_key": "sk-your-deepseek-key",
    "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-chat"
  }
}
```

## Return Data Format

```python
{
    'code': '600519',
    'name': 'Kweichow Moutai',
    'technical_indicators': {
        'trend_status': 'Strong Bull',
        'ma5': 1500.0,
        'bias_ma5': 2.5,
        'macd_status': 'Golden Cross',
        'rsi_status': 'Strong Buy',
        'buy_signal': 'Buy',
        'signal_score': 75
    },
    'ai_analysis': {
        'sentiment_score': 75,
        'operation_advice': 'Buy',
        'confidence_level': 'High',
        'target_price': '1550',
        'stop_loss': '1420'
    }
}
```

## Disclaimer

This project is for educational and research purposes only. Stock markets involve risks, invest with caution.
