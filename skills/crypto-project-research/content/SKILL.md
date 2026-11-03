---
name: crypto-project-research
description: Research and evaluate the long-term investment value of cryptocurrency projects. Use when users ask to analyze a specific crypto project, evaluate blockchain project fundamentals, assess DeFi/NFT/Web3 investments, or generate comprehensive crypto due diligence reports.
---

# Crypto Project Long-Term Value Research Agent

## Core Capability

This skill researches and evaluates the long-term investment value of cryptocurrency and blockchain projects through a comprehensive multi-dimensional analysis framework.

## Research Dimensions

### 1. Project Fundamentals
- **Whitepaper Analysis**: Technology innovation, use case validity, problem-solution fit
- **Tokenomics**: Supply mechanics, inflation schedule, token utility, distribution model
- **Technical Architecture**: Consensus mechanism, scalability solutions, security audits
- **Competitive Positioning**: Market landscape, differentiation, moat sustainability

### 2. Team & Governance
- **Core Team**: Background verification, past achievements, team size and structure
- **Governance Model**: Decentralization level, decision-making processes, treasury management
- **Investor Backers**: Quality of VC/angels, reputational assessment

### 3. Community & Ecosystem
- **Community Health**: Active users, developer activity, social sentiment
- **Ecosystem Growth**: dApp ecosystem, partnerships, integrations
- **Token Holder Distribution**: Concentration analysis, vesting schedules

### 4. Market & Financial Metrics
- **Market Performance**: Price history, liquidity, market cap rankings
- **On-chain Metrics**: Transaction volume, active addresses, network activity
- **Financial Transparency**: Revenue models, burn mechanisms, treasury reports

### 5. Risk Assessment
- **Regulatory Risk**: Jurisdictional concerns, compliance status
- **Technical Risk**: Code vulnerabilities, centralization points
- **Competitive Risk**: Threat from alternatives, technology obsolescence
- **Team Risk**: Key person dependency, incentive alignment

## Execution Workflow

### Step 1: Project Identification
```
User Input: [Project Name/Symbol/Contract Address]
↓
Validate project identity and gather basic metadata
↓
Create research framework tailored to project type (L1, DeFi, NFT, etc.)
```

### Step 2: Multi-Source Data Collection
- **Web Search**: Official documentation, news, announcements
- **On-chain Data**: Token distribution, transaction history, smart contract analysis
- **Social Data**: Community sentiment, developer discussions, sentiment trends
- **Market Data**: Price, volume, market metrics

### Step 3: Structured Analysis
Apply the 5-dimension framework:
1. Score each dimension (1-10 scale)
2. Weight dimensions based on project type
3. Identify key strengths and red flags
4. Compare against competitors

### Step 4: Risk-Adjusted Valuation
```
Long-term Value Score = Σ(Dimension_Score × Weight) × Risk_Adjustment_Factor

Risk Factors:
- High concentration: 0.7-0.9 multiplier
- Regulatory uncertainty: 0.6-0.8 multiplier
- Team risks: 0.7-0.9 multiplier
```

### Step 5: Research Report Generation
Output comprehensive report with:
- Executive Summary (1-2 paragraphs)
- Project Overview
- Dimension-by-dimension analysis
- Risk assessment
- Investment thesis (bull/bear case)
- Comparative analysis (vs. top 3 competitors)
- Final recommendation

## Output Format

### Structured Report
```markdown
# [Project Name] Long-Term Value Research

## Executive Summary
[2-3 sentence overview with key verdict]

## 1. Project Fundamentals
### Score: X/10
- Whitepaper & Vision: [Analysis]
- Tokenomics: [Analysis]
- Technical Architecture: [Analysis]
- Competitive Position: [Analysis]

## 2. Team & Governance
### Score: X/10
[Detailed analysis...]

## 3. Community & Ecosystem
### Score: X/10
[Detailed analysis...]

## 4. Market & Financials
### Score: X/10
[Detailed analysis...]

## 5. Risk Assessment
### Overall Risk Level: [Low/Medium/High]
- Regulatory Risk: [Level]
- Technical Risk: [Level]
- Competitive Risk: [Level]
- Team Risk: [Level]

## Comparative Analysis
| Metric | Project | Competitor A | Competitor B |
|--------|---------|--------------|--------------|
| Market Cap | $X | $X | $X |
| TVL/Users | X | X | X |
| Tokenomics | X/10 | X/10 | X/10 |
...

## Investment Thesis
### Bull Case
[Key catalysts for value appreciation...]

### Bear Case
[Key risks and concerns...]

## Final Assessment
**Long-Term Value Score: X/10**
**Recommendation: [Buy/Hold/Neutral/Sell]**

---
Research Date: [Date]
Analyst: Crypto Research Agent
```

## Quality Standards

### Research Rigor
- Cite all data sources with timestamps
- Distinguish between verifiable facts and analyst opinions
- Flag uncertainties and data limitations
- Update analysis for major events

### Objectivity
- Present both bull and bear cases fairly
- Avoid pump/dump speculation
- Focus on fundamental value drivers
- Consider multiple time horizons

### Completeness
- Cover all 5 dimensions
- Include comparative analysis
- Provide actionable insights
- Flag critical red flags

## Tool Integration

Use available tools for comprehensive research:
- `mcp__matrix__batch_web_search`: Multi-source information gathering
- `mcp__matrix__extract_content_from_websites`: Deep dive into documentation
- `mcp__matrix__stocks_info`: For projects with stock exposure
- `mcp__matrix__bash`: For running analysis scripts
- Direct web research for latest news and updates

## Trigger Examples

**Use this skill when user says:**
- "Analyze [project name] long-term potential"
- "Research [token symbol] investment value"
- "Due diligence on [DeFi protocol]"
- "Evaluate [NFT/Gaming/DAO] project"
- "Is [project] a good investment?"
- "Compare [project A] vs [project B]"
- "Deep dive into [project] fundamentals"

**Do NOT use for:**
- Real-time trading signals
- Price predictions
- Short-term market analysis
- Non-cryptocurrency investments

## Version

1.0.0
