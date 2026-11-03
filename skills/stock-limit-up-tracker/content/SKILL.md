---
name: stock-limit-up-tracker
description: Stock limit-up analysis skill. Used when users ask about limit-up boards, strong stocks, trading strategies, limit-up reviews, consecutive limit-up analysis, Dragon Tiger List data, limit-up reason analysis, seal rate calculation, etc. Provides professional features including A-share market limit-up stock identification, consecutive board tracking, timing analysis, and market sentiment judgment.
---

# Stock Limit-Up Tracker Skill

## Core Capabilities

This skill focuses on A-share market limit-up board (Limit-Up Board) analysis and trading strategy support.

### 1. Limit-Up Stock Identification & Analysis
- Real-time tracking of limit-up stocks
- Analyze seal time, seal strength, and order volume changes
- Identify first-time limit-up stocks (N consecutive boards)
- Calculate seal rate (ratio of stocks maintaining limit-up)

### 2. Trading Timing Analysis
- Sector linkage effect analysis
- Leader stock identification vs. follower distinction
- Limit-up quality assessment (hard seal vs. loose seal)
- Break-seal risk warning

### 3. Consecutive Board Tracking
- Statistics on consecutive boards (3-board, 5-board streaks)
- Analyze characteristics and drivers of consecutive board stocks
- Track demon stocks and leader stock trends
- Consecutive board review and next-day expectations

### 4. Limit-Up Reason Analysis
- Announcement-driven (earnings, M&A, restructuring)
- Policy benefits
- Sector rotation
- Capital promotion
- Technical patterns

### 5. Market Sentiment Judgment
- Limit-up count statistics
- Limit-down count comparison
- Yesterday's limit-up today's performance
- Yesterday's consecutive boards today's performance
- Break-seal rate monitoring

## Usage

### Query Limit-Up Information
Users can ask:
- "What are today's limit-up stocks"
- "Find stocks with recent 3 consecutive boards"
- "Analyze the limit-up reason for XX stock"
- "How is the current trading sentiment"

### Trading Strategy Analysis
- Hard seal vs. loose seal identification
- Queue trading tips
- Position management strategies
- Stop-loss/take-profit levels

## Data Sources

Uses stock data APIs to obtain:
- Real-time market data
- Limit-up board data
- Dragon Tiger List data
- Historical K-line data

## Output Format

Analysis results include:
- **Stock Code & Name**
- **Limit-Up Time** (first seal time)
- **Seal Status** (sealed, repeatedly opened, broken)
- **Seal Order Volume** (current sealed amount)
- **Floating Market Cap**
- **Limit-Up Reason** (inferred from data analysis)
- **Consecutive Board Status**
- **Trading Suggestions** (for reference only)

## Risk Warning

> Warning
> - This skill only provides information analysis, not investment advice
> - Stock markets involve risks, invest with caution
> - Limit-up trading is a high-risk strategy that may face huge losses
> - Please make decisions based on your own risk tolerance

## Technical Limitations

1. Data Delay: Real-time data may have 1-5 seconds delay
2. Incomplete Information: Unable to obtain non-public insider information
3. Prediction Inaccuracy: Market trends cannot be accurately predicted
4. API Limitations: Data acquisition is limited by external API services

## References

For detailed trading strategies and case studies, refer to the references/ directory.
