---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 32af36c7f570f69acf50016572a6a28e
    PropagateID: 32af36c7f570f69acf50016572a6a28e
    ReservedCode1: 3044022033d21d7ea83789a51135f907868256ec4f9a30fc2c1458bd93d38f77834a209502201189c40639d9f2991f979dd4484dbf08b8612d2ca7fd8bd3b4fd6ca3d8666b85
    ReservedCode2: 3045022100af0061d3ab66be91c1f8712ca1bfc8bd8dde7e2ee4344c0141d5b04bdb01bd7602206ae2e13bfbcc7ea025d922256e766e120d4ea9be5cbbb80c3fed27ab8b59e75b
description: Crude oil daily news push. Used when users request comprehensive crude oil market reports, WTI/Brent crude analysis, technical indicator interpretation (RSI/CCI/Options IV), trading recommendations, or daily crude oil newsletter subscription.
name: crude-oil-daily-news
---

# Crude Oil Daily News Skill

Act as a senior crude oil analyst and trader to write comprehensive crude oil market reports covering the past 24 hours (WTI crude, Brent crude).

## Execution Protocol

### Phase 1: Data Preparation (Parallel Execution)

1. Parallel price data search (WTI crude, Brent crude, US Dollar Index DXY, 10-Year US Treasury Yield)
2. Parallel technical indicators search (RSI(14), CCI(20), WTI Options IV/OVX Index)
3. Parallel news events search (priority: geopolitics > OPEC+/inventories > central bank policy > macro data > weather)

### Phase 2: Data Integration & Quality Check

1. Verify all data timeliness (within 48 hours)
2. Verify at least 1 authoritative source (Reuters/Bloomberg/WSJ/CNBC)
3. Data quality rating (High/Medium/Low)
4. Mark missing data as "Data Unavailable"

### Phase 3: Content Writing

Write report following this structure:
1. **Key Indicators Overview** - Summary table
2. **Market Summary** - 24-hour overall sentiment
3. **WTI Crude** - Price performance → drivers → technical analysis
4. **Brent Crude** - Price performance → drivers → technical analysis
5. **Spread & Term Structure** - WTI-Brent spread, Contango/Backwardation
6. **Risk Management Matrix** - Risk types and responses
7. **Scenario Analysis** - Key scenario projections
8. **RSI/CCI/Options IV Comprehensive Analysis** - Three-indicator matrix
9. **Trading Recommendations** - Conditional framework (short-term/mid-term)
10. **Key Watch Points** - Three bullet points

### Phase 4: Final Review

1. Verify all required steps completed
2. Verify iron rules compliance
3. Check for common mistakes

## Core Constraints (Iron Rules)

- **Time Rule**: Use relative time expressions (today/yesterday/last 24 hours), no hardcoded dates
- **Trading Advice**: Must use "if...then..." conditional sentences, no absolute price predictions
- **Stop Loss**: Every condition must include stop loss/invalidation price
- **Emotional Control**: No emotional vocabulary (surge/crash/bottom/top/etc.)
- **Data Sources**: Core facts must cite authoritative sources

## Technical Indicators Analysis

See references/technical-indicators.md

## News Priority Rules

See references/news-priority.md

## Trading Recommendations Template

See references/trading-framework.md

## Risk Quantification Standards

- Single trade max loss: 2% of account
- Single day max loss: 3% of account
- Weekly max loss: 5% of account
- OVX percentile >80%: Reduce position by half
- OVX percentile >95%: Reduce position to 1/3

## Prohibitions

- No absolute price predictions
- No personal subjective opinions
- No motivational fluff
- No specific position size recommendations
- No emotional vocabulary
- No unverified social media sources
- No hiding limitations of technical indicators

---

*For detailed indicator analysis, news priority, and trading framework, see the references/ directory*
