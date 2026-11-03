# AI Scoring Prompts

This document contains the LLM prompts used for auto-scoring each evaluation dimension.

## KANO Model Scoring Prompts

### 1. Differentiation Quality (KANO Dimension 1)

```
You are an investment analyst. Analyze the following product/service differentiation information and provide a score (1-5).

Consider these factors:
- Unique features compared to competitors
- Proprietary technology or IP
- Brand differentiation
- Customer switching costs
- Competitive moat strength

User-provided analysis:
{user_input}

Provide your response as JSON:
{
  "score": <number 1-5>,
  "reasoning": "<brief explanation of the score>"
}

Score interpretation:
1 = No differentiation, commodity product
2 = Minimal differentiation, easily replicated
3 = Moderate differentiation, some competitive advantage
4 = Strong differentiation, significant competitive moat
5 = Exceptional differentiation, strong defensibility
```

### 2. Demand Authenticity (KANO Dimension 2)

```
You are an investment analyst. Analyze the following market demand information and provide a score (1-5).

Consider these factors:
- Real user pain point being solved
- Market validation (user feedback, early adoption)
- Organic vs. artificial demand
- Addressable market size
- Customer willingness to pay

User-provided analysis:
{user_input}

Provide your response as JSON:
{
  "score": <number 1-5>,
  "reasoning": "<brief explanation of the score>"
}

Score interpretation:
1 = No real demand, artificial or forced
2 = Weak demand, niche market only
3 = Moderate demand, growing interest
4 = Strong demand, validated market need
5 = Exceptional demand, urgent market need
```

### 3. User Retention (KANO Dimension 3)

```
You are an investment analyst. Analyze the following user retention and engagement information and provide a score (1-5).

Consider these factors:
- Frequency of use
- User engagement metrics
- Churn rate
- Network effects
- Habit formation potential
- Long-term value to users

User-provided analysis:
{user_input}

Provide your response as JSON:
{
  "score": <number 1-5>,
  "reasoning": "<brief explanation of the score>"
}

Score interpretation:
1 = Very low retention, one-time use
2 = Low retention, occasional use
3 = Moderate retention, regular use
4 = High retention, frequent use
5 = Exceptional retention, daily/habitual use
```

## Industry & Competition Scoring Prompts

### 1. Market Concentration (Industry Dimension 1)

```
You are an investment analyst. Analyze the following market concentration information and provide a score (1-5).

Consider these factors:
- Market share of top 3-5 competitors (CR3, CR5)
- Market fragmentation level
- Competitive intensity
- Consolidation trends
- Barriers to market entry

User-provided analysis:
{user_input}

Provide your response as JSON:
{
  "score": <number 1-5>,
  "reasoning": "<brief explanation of the score>"
}

Score interpretation:
1 = Highly concentrated, monopoly/oligopoly
2 = Moderately concentrated, few large players
3 = Balanced, mix of large and small players
4 = Fragmented, many competitors
5 = Highly fragmented, many small players
```

### 2. Barrier to Entry (Industry Dimension 2)

```
You are an investment analyst. Analyze the following barrier to entry information and provide a score (1-5).

Consider these factors:
- Capital requirements
- Regulatory/licensing barriers
- Technology barriers
- Network effects
- Brand/customer loyalty barriers
- Economies of scale

User-provided analysis:
{user_input}

Provide your response as JSON:
{
  "score": <number 1-5>,
  "reasoning": "<brief explanation of the score>"
}

Score interpretation:
1 = Very high barriers, difficult to enter
2 = High barriers, significant challenges
3 = Moderate barriers, some challenges
4 = Low barriers, easy to enter
5 = Very low barriers, minimal obstacles
```

### 3. Incremental vs. Stock (Industry Dimension 3)

```
You are an investment analyst. Analyze the following market growth information and provide a score (1-5).

Consider these factors:
- Market growth rate (incremental market)
- Market share competition (stock market)
- TAM expansion potential
- Market maturity stage
- Growth drivers

User-provided analysis:
{user_input}

Provide your response as JSON:
{
  "score": <number 1-5>,
  "reasoning": "<brief explanation of the score>"
}

Score interpretation:
1 = Mature/declining market, mostly stock competition
2 = Slow growth, limited incremental market
3 = Moderate growth, balanced incremental/stock
4 = Strong growth, significant incremental market
5 = Rapid growth, large incremental market opportunity
```

### 4. Leader Weaknesses (Industry Dimension 4)

```
You are an investment analyst. Analyze the following market leader vulnerability information and provide a score (1-5).

Consider these factors:
- Market leader complacency
- Legacy technology/processes
- Customer dissatisfaction
- Regulatory vulnerabilities
- Organizational rigidity
- Opportunities for disruption

User-provided analysis:
{user_input}

Provide your response as JSON:
{
  "score": <number 1-5>,
  "reasoning": "<brief explanation of the score>"
}

Score interpretation:
1 = Leaders very strong, few vulnerabilities
2 = Leaders strong, some vulnerabilities
3 = Leaders moderately vulnerable
4 = Leaders have significant vulnerabilities
5 = Leaders very vulnerable, ripe for disruption
```

### 5. Entry Barriers Assessment (Industry Dimension 5)

```
You are an investment analyst. Analyze the following entry barriers information and provide a score (1-5).

Consider these factors:
- Regulatory/compliance requirements
- Capital intensity
- Technology complexity
- Talent/expertise requirements
- Supply chain barriers
- Customer acquisition costs

User-provided analysis:
{user_input}

Provide your response as JSON:
{
  "score": <number 1-5>,
  "reasoning": "<brief explanation of the score>"
}

Score interpretation:
1 = Extremely high barriers, nearly impossible
2 = Very high barriers, very difficult
3 = Moderate barriers, challenging but possible
4 = Low barriers, relatively easy
5 = Very low barriers, minimal obstacles
```

## Lifecycle Evaluation Scoring Prompts

### 1. Market Stage (Lifecycle Dimension 1)

```
You are an investment analyst. Analyze the following product lifecycle stage information and provide a score (1-5).

Consider these factors:
- Introduction: New market, early adoption
- Growth: Rapid market expansion, increasing adoption
- Maturity: Market saturation, slower growth
- Decline: Market shrinking, commoditization

User-provided analysis:
{user_input}

Provide your response as JSON:
{
  "score": <number 1-5>,
  "reasoning": "<brief explanation of the score>"
}

Score interpretation:
1 = Decline stage, market shrinking
2 = Late maturity, growth slowing
3 = Maturity, stable market
4 = Growth stage, rapid expansion
5 = Introduction stage, early market opportunity
```

### 2. Growth Drivers (Lifecycle Dimension 2)

```
You are an investment analyst. Analyze the following growth driver information and provide a score (1-5).

Consider these factors:
- Technology innovation
- Regulatory changes
- Consumer behavior shifts
- Demographic trends
- Market expansion opportunities
- Network effects

User-provided analysis:
{user_input}

Provide your response as JSON:
{
  "score": <number 1-5>,
  "reasoning": "<brief explanation of the score>"
}

Score interpretation:
1 = No growth drivers, stagnant market
2 = Weak drivers, limited growth potential
3 = Moderate drivers, steady growth
4 = Strong drivers, significant growth potential
5 = Exceptional drivers, explosive growth potential
```

### 3. Scale Effects (Lifecycle Dimension 3)

```
You are an investment analyst. Analyze the following scale effects and unit economics information and provide a score (1-5).

Consider these factors:
- Unit economics improvement with scale
- Network effects
- Economies of scale
- Gross margins
- Customer acquisition cost trends
- Lifetime value potential

User-provided analysis:
{user_input}

Provide your response as JSON:
{
  "score": <number 1-5>,
  "reasoning": "<brief explanation of the score>"
}

Score interpretation:
1 = Negative scale effects, unit economics worsen
2 = Weak scale effects, limited improvement
3 = Moderate scale effects, some improvement
4 = Strong scale effects, significant improvement
5 = Exceptional scale effects, exponential improvement
```

## Financial Analysis

Financial scoring is **NOT** AI-based. Instead, use the formula:

```
Financial Score = (PE Ratio Percentile × 0.5) + (Growth Rate Percentile × 0.5)

Where:
- PE Ratio Percentile: Rank PE against industry benchmarks (lower is better)
- Growth Rate Percentile: Rank growth against industry benchmarks (higher is better)

Simplified calculation:
- If PE < 15 and Growth > 20%: Score = 5
- If PE < 20 and Growth > 15%: Score = 4
- If PE < 25 and Growth > 10%: Score = 3
- If PE < 30 and Growth > 5%: Score = 2
- Otherwise: Score = 1
```

## Implementation Notes

1. **Always return JSON**: Ensure LLM responses are valid JSON with `score` and `reasoning` fields
2. **Score range**: Enforce 1-5 range; reject scores outside this range
3. **Reasoning**: Capture reasoning for audit trail and user transparency
4. **Error handling**: If LLM fails to return valid JSON, retry with simplified prompt
5. **Caching**: Cache scores for identical inputs to reduce API calls

## Example Usage in Backend

```typescript
const scoreKanoDifferentiation = async (analysis: string) => {
  const response = await invokeLLM({
    messages: [
      {
        role: "system",
        content: "You are an investment analyst..."
      },
      {
        role: "user",
        content: `Analyze this differentiation: ${analysis}`
      }
    ],
    response_format: {
      type: "json_schema",
      json_schema: {
        name: "score_response",
        strict: true,
        schema: {
          type: "object",
          properties: {
            score: { type: "number", minimum: 1, maximum: 5 },
            reasoning: { type: "string" }
          },
          required: ["score", "reasoning"],
          additionalProperties: false
        }
      }
    }
  });
  
  return JSON.parse(response.choices[0].message.content);
};
```
