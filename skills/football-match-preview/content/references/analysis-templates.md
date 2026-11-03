# Football Match Analysis Reference Guide

## Match Type Determination Guide

### League/Group Stage Characteristics
- Regular season matches
- Group stage in tournaments (World Cup, Euro Cup, Champions League, etc.)
- Matches where a draw result is acceptable
- Points are awarded (3 for win, 1 for draw, 0 for loss)

### Knockout/Final Stage Characteristics
- Round of 16, Quarterfinals, Semifinals, Finals
- Playoff matches
- No draw allowed - must determine a winner
- May involve extra time (90+30 minutes) and penalty shootout

## 6-Factor Weighting System

| Factor | Weight | Description |
|--------|--------|-------------|
| Player Ability | 35% | Comprehensive player ratings from multiple sources |
| Recent Form | 20% | Team performance in last 10 matches |
| Formation Matchup | 15% | Tactical compatibility and counters |
| Home/Away | 10% | Venue-based performance differentials |
| Injuries | 10% | Key player availability impact |
| Head-to-Head | 10% | Historical encounter analysis |

## Probability Calculation Formulas

### League/Group Stage
```
Final Probability = (Player×0.35) + (Form×0.20) + (Formation×0.15) + (Home×0.10) + (Injury×0.10) + (H2H×0.10)
```

### Knockout Stage Advancement
```
Home Advancement = Normal Win + (Draw × Extra Win) + (Draw × Extra Draw × Penalty Win)
```

### Confidence Level Thresholds
- **High Confidence**: Probability >= 70%
- **Medium Confidence**: Probability 50-69%
- **Low Confidence**: Probability < 50%

## Multi-Source Rating Integration

### Player Rating Sources
| Source | Weight | Data Quality | Update Frequency |
|--------|--------|--------------|-----------------|
| WhoScored | 25% | High | Per match |
| SofaScore | 20% | High | Per match |
| FIFA/FM | 25% | Medium-High | Periodic |
| FotMob | 15% | Medium | Daily |
| Transfermarkt | 15% | High | Periodic |

### Combined Rating Formula
```
Final Rating = (WhoScored×0.25) + (SofaScore×0.20) + (FIFA×0.25) + (FotMob×0.15) + (Transfermarkt×0.15)
```

## Position-Specific Metrics

### Forward Analysis
- Goals scored
- Shots per game
- Shot accuracy
- Dribbling success rate
- Key passes
- Rating median trend

### Midfielder Analysis
- Pass completion %
- Assists
- Key passes
- Through balls
- Interceptions (defensive mids)
- Rating median trend

### Defender Analysis
- Clearances
- Interceptions
- Tackles
- Blocked shots
- Aerial duels
- Rating median trend

### Goalkeeper Analysis
- Saves
- Save percentage
- Clean sheets
- Punches/Claims
- Distribution accuracy
- Rating median trend

## Formation Analysis Matrix

### Common Formations
| Formation | Offensive | Control | Defensive | Flexibility |
|-----------|-----------|---------|-----------|-------------|
| 4-3-3 | High | Medium | Medium | Medium |
| 4-4-2 | Medium | High | High | Low |
| 3-5-2 | Medium | High | Medium | High |
| 4-2-3-1 | High | High | Medium | Medium |
| 5-3-2 | Low | Medium | High | Low |

### Formation Counters
| Against | Weak Against | Strong Against |
|---------|--------------|----------------|
| 4-3-3 | 5-3-2 | 4-4-2 |
| 4-4-2 | 4-2-3-1 | 3-5-2 |
| 3-5-2 | 4-4-2 | 4-3-3 |
| 5-3-2 | 4-3-3 | 4-2-3-1 |

## Home/Away Coefficient Calculation

### Home Advantage Factors
```
Home Coefficient = Base (1.0) + Travel Fatigue Factor + Familiarity Factor + Crowd Factor
```

### Typical Home Advantages
- Win rate increase: 10-15%
- Goals scored increase: 15-20%
- Goals conceded decrease: 10-15%

## Bookmaker Odds Analysis

### European Odds (Decimal)
| Result | Odds | Implied Probability |
|--------|------|---------------------|
| Home Win | 2.00 | 50% |
| Draw | 3.40 | 29.4% |
| Away Win | 4.00 | 25% |

### Asian Handicap Examples
| Handicap | Home | Away | Interpretation |
|----------|------|------|----------------|
| 0 | 1.90 | 1.95 | Equal match |
| -0.5 | 2.00 | 1.85 | Home must win |
| +0.5 | 1.85 | 2.00 | Away +0.5 |
| -1 | 2.10 | 1.75 | Home must win by 2+ |

### Payout Calculation
```
Payout = Odds × Stake × Implied Probability Factor
```

## Extra Time & Penalty Analysis

### Extra Time Factors
- Fitness level after 90 minutes
- Substitution quota utilization
- Mental state after close 90 minutes
- Experience in extra time situations

### Penalty Shootout Factors
- Historical penalty success rate
- Pressure player identification
- Goalkeeper penalty save record
- Order of penalty takers
- Field conditions

## Trend Chart Data Format

### Season Rating Trend
```
Season | Rating Median
2020-21 | 7.2
2021-22 | 7.4
2022-23 | 7.1
2023-24 | 7.5
2024-25 | 7.6
```

### Form Trend (Last 10 Matches)
```
Match | Date | Opponent | Score | Rating
1 | Date | Team A | 2-1 | 7.5
2 | Date | Team B | 1-1 | 6.8
...
```

## Expert Commentator Sourcing

### Global Commentators (by influence)
1. Gary Lineker (BBC/ESPN)
2. Fabrizio Romano (Transfer news)
3. Rio Ferdinand (Analysis)
4. Gary Neville (Tactical)
5. Thierry Henry (Analysis)

### Asian Commentators
1. Keisuke Honda (Japan)
2. Zhan Jun (China)
3. Park Ji-sung (Korea)
4. Hidetoshi Nakata (Japan)
5. Fan Zhiyi (China)

### Evaluation Metrics
- Twitter engagement (likes, retweets, replies)
- YouTube views and comments
- Weibo reposts and likes
- Professional credibility

## Output Template Structure

```
# Match Preview Report

## Match Information
- Teams: [Home] vs [Away]
- Competition: [League/Tournament]
- Date: [Date]
- Stage: [League/Knockout]

## Part 1: Prediction Model Overview
[Model architecture and weights]

## Part 2: Match Prediction
[Probability table based on match type]

## Part 3: Player Analysis
[Position-by-position ratings and trends]

## Part 4: Formation Analysis
[Tactical matchup analysis]

## Part 5: Recent Form
[Team performance trends]

## Part 6: Home/Away Factors
[venue-based analysis]

## Part 7: Injury Analysis
[Availability and impact]

## Part 8: Head-to-Head
[Historical encounters]

## Part 9: Betting Summary
[Odds comparison]

## Part 10: Viewing Guide
[Key factors and predictions]
```
