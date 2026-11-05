# Investment Evaluation System - API Endpoints

Complete tRPC API specification for the investment evaluation system.

## Authentication & Context

All endpoints require user authentication via Manus OAuth. The `ctx.user` object contains:

```typescript
{
  id: number;
  openId: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  createdAt: Date;
  updatedAt: Date;
  lastSignedIn: Date;
}
```

## Evaluation Management

### evaluations.create

Create a new investment evaluation.

**Input:**
```typescript
{
  projectName: string;        // Project/company name
  description?: string;       // Optional description
}
```

**Output:**
```typescript
{
  id: number;
  projectName: string;
  description?: string;
  compositeScore: number | null;
  recommendation: string | null;
  createdAt: Date;
}
```

**Behavior:**
- Checks user quota before creation
- Returns error if quota exhausted
- Logs usage in `usage_logs` table
- Returns 201 Created on success

**Errors:**
- `QUOTA_EXCEEDED`: User has reached monthly quota
- `FORBIDDEN`: User role insufficient
- `BAD_REQUEST`: Missing required fields

### evaluations.list

Retrieve all evaluations for the current user.

**Input:**
```typescript
{
  skip?: number;              // Pagination offset (default: 0)
  take?: number;              // Pagination limit (default: 10)
  sortBy?: 'createdAt' | 'compositeScore';  // Sort field
  sortOrder?: 'asc' | 'desc'; // Sort order (default: desc)
}
```

**Output:**
```typescript
{
  evaluations: Array<{
    id: number;
    projectName: string;
    description?: string;
    compositeScore: number | null;
    recommendation: string | null;
    createdAt: Date;
    updatedAt: Date;
  }>;
  total: number;              // Total count
}
```

### evaluations.get

Retrieve a single evaluation with all assessment data.

**Input:**
```typescript
{
  id: number;                 // Evaluation ID
}
```

**Output:**
```typescript
{
  id: number;
  projectName: string;
  description?: string;
  compositeScore: number | null;
  recommendation: string | null;
  businessBrief?: string;
  createdAt: Date;
  updatedAt: Date;
  
  // Nested assessment data
  kano?: {
    differentiationScore: number;
    demandScore: number;
    retentionScore: number;
  };
  industry?: {
    concentrationScore: number;
    barrierScore: number;
    incrementalScore: number;
    leaderScore: number;
    entryScore: number;
  };
  lifecycle?: {
    stageScore: number;
    driversScore: number;
    scaleScore: number;
  };
  financial?: {
    peRatio: number;
    growthRate: number;
    pegRatio: number;
    financialScore: number;
  };
}
```

**Errors:**
- `NOT_FOUND`: Evaluation does not exist
- `FORBIDDEN`: User does not own this evaluation

### evaluations.update

Update an evaluation.

**Input:**
```typescript
{
  id: number;
  projectName?: string;
  description?: string;
}
```

**Output:**
```typescript
{
  id: number;
  projectName: string;
  description?: string;
  updatedAt: Date;
}
```

### evaluations.delete

Delete an evaluation.

**Input:**
```typescript
{
  id: number;
}
```

**Output:**
```typescript
{
  success: boolean;
}
```

## KANO Assessment

### evaluations.updateKano

Update KANO model assessment and trigger AI scoring.

**Input:**
```typescript
{
  evaluationId: number;
  differentiationAnalysis: string;  // User analysis text
  demandAnalysis: string;
  retentionAnalysis: string;
}
```

**Output:**
```typescript
{
  kanoScore: number;
  scores: {
    differentiation: number;
    demand: number;
    retention: number;
  };
  reasoning: {
    differentiation: string;
    demand: string;
    retention: string;
  };
}
```

**Process:**
1. Call LLM for each dimension with scoring prompts
2. Store scores in `kano_assessments` table
3. Recalculate composite score
4. Return individual scores and reasoning

## Industry Assessment

### evaluations.updateIndustry

Update industry & competition analysis and trigger AI scoring.

**Input:**
```typescript
{
  evaluationId: number;
  concentrationAnalysis: string;
  barrierAnalysis: string;
  incrementalAnalysis: string;
  leaderAnalysis: string;
  entryAnalysis: string;
}
```

**Output:**
```typescript
{
  industryScore: number;
  scores: {
    concentration: number;
    barrier: number;
    incremental: number;
    leader: number;
    entry: number;
  };
  reasoning: {
    concentration: string;
    barrier: string;
    incremental: string;
    leader: string;
    entry: string;
  };
}
```

## Lifecycle Assessment

### evaluations.updateLifecycle

Update lifecycle evaluation and trigger AI scoring.

**Input:**
```typescript
{
  evaluationId: number;
  stageAnalysis: string;
  driversAnalysis: string;
  scaleAnalysis: string;
}
```

**Output:**
```typescript
{
  lifecycleScore: number;
  scores: {
    stage: number;
    drivers: number;
    scale: number;
  };
  reasoning: {
    stage: string;
    drivers: string;
    scale: string;
  };
}
```

## Financial Assessment

### evaluations.updateFinancial

Update financial metrics (no AI scoring, formula-based).

**Input:**
```typescript
{
  evaluationId: number;
  peRatio: number;            // Price-to-Earnings
  growthRate: number;         // Year-over-year growth %
  analysis?: string;          // Optional analysis notes
}
```

**Output:**
```typescript
{
  financialScore: number;
  pegRatio: number;           // Calculated: PE / Growth
  metrics: {
    pe: number;
    growth: number;
    peg: number;
  };
}
```

**Calculation:**
```
PEG = PE / Growth Rate
Financial Score = (1 - (PE - 15) / 30) * 2.5 + (Growth / 40) * 2.5
  (Simplified: score based on PE and growth percentiles)
```

## Business Brief Generation

### evaluations.generateBrief

Generate AI-powered business analysis brief.

**Input:**
```typescript
{
  evaluationId: number;
}
```

**Output:**
```typescript
{
  brief: string;              // Markdown formatted
  sections: {
    executiveSummary: string;
    marketAnalysis: string;
    competitiveLandscape: string;
    financialProjections: string;
    riskAssessment: string;
    recommendation: string;
  };
}
```

**Process:**
1. Collect all evaluation data (KANO, Industry, Lifecycle, Financial)
2. Identify missing information gaps
3. Use web search to supplement data
4. Generate structured brief using LLM
5. Store in `evaluations.businessBrief` field
6. Return formatted brief

## Report Export

### evaluations.exportBriefPDF

Export business brief as PDF.

**Input:**
```typescript
{
  evaluationId: number;
}
```

**Output:**
```typescript
{
  success: boolean;
  pdf: string;                // Base64 encoded PDF
  filename: string;           // e.g., "ProjectName-Brief-2026-01-21.pdf"
}
```

**Features:**
- A4 format with 1.5x line spacing
- Header with project name and "Business Analysis Brief"
- Footer with page numbers and generation date
- Markdown formatting preserved
- Chinese font support

## Quota Management

### quota.check

Check user's remaining quota.

**Input:**
```typescript
{
  // No input required
}
```

**Output:**
```typescript
{
  membershipType: 'free' | 'premium';
  monthlyQuota: number;       // Total quota for month
  usedQuota: number;          // Already used this month
  remainingQuota: number;     // Available for use
  resetDate: Date;            // When quota resets
}
```

### quota.deduct

Deduct from user's quota (called internally by evaluations.create).

**Input:**
```typescript
{
  count: number;              // Amount to deduct (default: 1)
}
```

**Output:**
```typescript
{
  success: boolean;
  remainingQuota: number;
}
```

**Errors:**
- `QUOTA_EXCEEDED`: Insufficient quota

## Membership Management

### membership.subscribe

Subscribe to premium membership.

**Input:**
```typescript
{
  // No input required
}
```

**Output:**
```typescript
{
  success: boolean;
  membershipType: 'premium';
  subscriptionStartDate: Date;
  subscriptionEndDate: Date;
  monthlyQuota: number;       // 50 for premium
}
```

**Process:**
1. Create/update membership record
2. Set subscription dates (1 month from now)
3. Update quota to 50
4. Return confirmation

### membership.cancel

Cancel premium membership.

**Input:**
```typescript
{
  // No input required
}
```

**Output:**
```typescript
{
  success: boolean;
  membershipType: 'free';
  monthlyQuota: number;       // 3 for free
}
```

## AI Assistant

### ai.chat

Chat with AI investment consultant.

**Input:**
```typescript
{
  message: string;            // User message
  evaluationId?: number;      // Optional context
  conversationHistory?: Array<{
    role: 'user' | 'assistant';
    content: string;
  }>;
}
```

**Output:**
```typescript
{
  response: string;           // AI response
  suggestions?: string[];     // Optional follow-up suggestions
}
```

**Capabilities:**
- Answer questions about evaluations
- Provide investment analysis insights
- Suggest data sources for research
- Explain scoring logic
- Generate investment recommendations

## Error Handling

All errors follow this format:

```typescript
{
  code: string;               // Error code (e.g., 'QUOTA_EXCEEDED')
  message: string;            // Human-readable message
  details?: object;           // Additional context
}
```

**Common Error Codes:**
- `UNAUTHORIZED`: User not authenticated
- `FORBIDDEN`: User lacks permission
- `NOT_FOUND`: Resource does not exist
- `BAD_REQUEST`: Invalid input
- `QUOTA_EXCEEDED`: Monthly quota exhausted
- `INTERNAL_ERROR`: Server error

## Rate Limiting

- Free tier: 3 evaluations/month
- Premium tier: 50 evaluations/month
- AI chat: 100 messages/day per user
- PDF export: 10 exports/day per user
