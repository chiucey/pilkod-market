---
name: football-match-preview
description: Comprehensive football match analysis and prediction skill. Use when users ask to analyze football matches, predict match outcomes, generate match previews, evaluate team/player performance, assess betting odds, or request tactical analysis for European leagues, Asian football, or international competitions. Triggers include: 足球分析, 比赛预测, 赛前分析, 足球预测, match analysis, match preview, 球队分析, 球员评分, 战术分析, 赔率分析.
---

# Football Match Preview & Analysis Skill

Professional football match analysis system with comprehensive prediction models, player evaluation, tactical assessment, and betting analysis.

## Core Workflow

### Step 1: Input Collection

When user provides a match request, collect:
- Two team names (Home team + Away team)
- Competition/League name
- Match date and stage (League/Group stage or Knockout/Final)

If any information is missing, ask the user to provide it before proceeding.

### Step 2: Match Type Determination

Based on user input or match context:

**League/Group Stage Mode** (Can have draw):
- Regular league rounds, group stage matches
- Prediction output: Home Win / Draw / Away Win

**Knockout/Final Mode** (Must produce winner):
- Round of 16, quarterfinals, semifinals, finals, playoffs
- Prediction output: Home team advances OR Away team advances

### Step 3: Comprehensive Analysis

Conduct analysis following the 10-part structure:

#### Part 1: Prediction Model Overview

- **Comprehensive Prediction Model Architecture** (6-factor weighting):
  - Player ability analysis: 35%
  - Recent form: 20%
  - Formation matchup: 15%
  - Home/away factors: 10%
  - Injury assessment: 10%
  - Head-to-head history: 10%

- **Bookmaker Model Comparison**:
  - European models vs Asian models
  - Key bookmakers: Bet365, William Hill, Pinnacle

#### Part 2: Match Prediction Overview

**For League/Group Stage**:
| Result | Probability | Confidence | Odds |
|--------|-------------|------------|------|
| Home Win | XX% | High/Medium/Low | X.XX |
| Draw | XX% | High/Medium/Low | X.XX |
| Away Win | XX% | High/Medium/Low | X.XX |

**For Knockout/Final Stage**:
- **Stage A**: 90-minute normal time - Home/Draw/Away probability
- **Stage B**: 120-minute extra time - Home/Still Draw/Away probability
- **Stage C**: Final advancement prediction (Home advances OR Away advances)
- **Stage D**: Penalty shootout data (historical record, penalty taker ability, goalkeeper save ability)

**Advancement Formula**:
```
Home Advancement = Normal Win + Draw × (Extra Win + Extra Draw × Penalty Win)
```

#### Part 3: Player Comprehensive Analysis (Weight: 35%)

**Multi-source Rating Integration**:
- WhoScored: 25%
- SofaScore: 20%
- FotMob: 15%
- FIFA/FM: 25%
- Transfermarkt: 15%

**Position-specific Data**:

| Position | Key Metrics |
|----------|-------------|
| Forward | Goals, Shots, Dribbling, Rating median, Season trends |
| Midfielder | Passes, Assists, Key passes, Rating median, Season trends |
| Defender | Clearances, Interceptions, Defensive actions, Rating median, Season trends |
| Goalkeeper | Saves, Claiming, Clean sheets, Rating median, Season trends |

**Common Analysis Items**:
- Last 10 matches detailed stats
- Career median + Current season median + Each season breakdown
- Rating median trend line chart (season-by-season)
- Last 10 matches rating trend line chart
- Expert commentator evaluations (sorted by views/shares/likes)

#### Part 4: Formation Matchup Analysis (Weight: 15%)

- Formation capability scores for both teams:
  - Offensive power
  - Control ability
  - Defensive strength
  - Flexibility
- Formation counter matrix
- Expert tactical evaluations

#### Part 5: Recent Form Analysis (Weight: 20%)

- Team's last 10 matches record
- Team rating median (historical + current season + season trends)
- Team rating median trend line chart
- Last 10 matches points/goals scored/goals conceded trend chart
- Form evaluation from commentators

#### Part 6: Home/Away Factors (Weight: 10%)

- Home data: Win rate, Goals scored, Goals conceded, Unbeaten rate
- Away data
- Home/Away coefficient calculation

#### Part 7: Injury & Absence Analysis (Weight: 10%)

- Injury/Suspension list
- Key player absence impact assessment
- Injury impact evaluation from commentators

#### Part 8: Head-to-Head Analysis (Weight: 10%)

- Last 10 encounters record
- Historical encounter statistics
- Head-to-head trend line chart
- Encounters evaluation from commentators

#### Part 9: Betting & Commentary Summary

**For League/Group Stage**:
| Bookmaker | Home Win | Draw | Away Win | Payout |
|-----------|----------|------|----------|--------|
| Bet365 | X.XX | X.XX | X.XX | XX% |
| William Hill | X.XX | X.XX | X.XX | XX% |

**For Knockout/Final Stage**:
- Advancement odds
- 90-minute win/draw/lose odds
- Special odds (Extra time / Penalty shootout)

#### Part 10: Viewing Guide & Key Factors

**For League/Group Stage**:
| Result | Probability | Confidence |
|--------|-------------|------------|
| Home Win | XX% | High/Medium/Low |
| Draw | XX% | High/Medium/Low |
| Away Win | XX% | High/Medium/Low |

**For Knockout/Final Stage**:
| Advancing Team | Probability | Confidence |
|----------------|-------------|------------|
| Home Team | XX% | High/Medium/Low |
| Away Team | XX% | High/Medium/Low |

**Key Match Moments**:
- Midfield control
- Forward chance conversion
- Wide area attacks
- Set pieces
- Substitution timing

**Key Players to Watch**: List key players for each position with reasons

**Time Period Alerts**:
- 0-15 min: Opening phase
- 30-45 min: High-scoring period
- 60-75 min: Substitution window
- 75-90 min: Late drama potential

**Knockout-exclusive Factors**:
- Extra time: Fitness reserves, substitution quotas, mental strength, recent extra time performance
- Penalty shootout: Penalty order, goalkeeper choice, pressure players, field factors
- Special risks: Extra time fatigue, penalty pressure, red/yellow cards, injuries, home pressure

## Data Sources

| Data Type | Primary Source | Quality Indicator |
|-----------|----------------|-------------------|
| Player Ratings | WhoScored | High |
| Player Market Value | Transfermarkt | High |
| Betting Odds | Bet365/William Hill/Pinnacle | High |
| Commentary | Twitter/Weibo/YouTube | Medium |

## Expert Commentators

**Global Top 20**: Gary Lineker, Fabrizio Romano, Rio Ferdinand, Gary Neville, Thierry Henry, etc.

**Asian Top 10**: Keisuke Honda, Zhan Jun, Park Ji-sung, Hidetoshi Nakata, Fan Zhiyi, etc.

**Chinese Top 10**: Zhan Jun, Huang Jianxiang, Dong Lu, Fan Zhiyi, Liu Jianhong, Zhang Lu, Su Dong, He Wei, Xu Yang, Li Xin

## Output Format

Generate a comprehensive match preview report with all 10 parts. Use markdown tables, charts (ASCII or SVG), and structured sections for clarity.

Include probability percentages, confidence levels, and betting odds where applicable. Present both analytical findings and prediction outcomes clearly.

## Quality Requirements

1. All data should be sourced from official/reputable channels
2. Use quality indicators to mark data reliability
3. Provide clear confidence levels for predictions
4. Include multiple perspectives (analytical + betting + expert opinion)
5. Format output for readability and quick scanning
