---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 47881ad62e5a5f1948c596c04bd4180a
    PropagateID: 47881ad62e5a5f1948c596c04bd4180a
    ReservedCode1: 3046022100d56faabe5e58527a3d9c1eee13e6d8ce29385535e9f9e7908dc5c9d59108d263022100dea566c0d64985ba4f6a043f5a148eb1cffb2d3be1fad2b24420214390f85416
    ReservedCode2: 304402205a79e7f6b0b5eadc9d641840220d93269a59712518412a91df1ba8b733f9abb702202bfef75ac4ae8412449a826b317857e7d221c48a4eb628025c775d5d6f6d9b53
---

# Investment Evaluation SOP Skill

## Overview

This skill provides a complete workflow for building an investment evaluation decision system—a web application that systematically assesses investment opportunities using four evaluation dimensions and AI-powered scoring. The system implements a structured SOP for investment analysis with automatic scoring based on user-provided data, AI-generated business briefs, and professional PDF export capabilities.

## When to Use This Skill

Use this skill when you need to:

- Build a web application for systematic investment evaluation
- Implement AI-powered scoring based on user-provided analysis
- Create quota management systems (free tier with limited uses, premium tier with monthly allowance)
- Generate professional business analysis reports with AI assistance
- Export evaluation reports as PDF or Markdown documents

## Evaluation Framework

The system assesses investments across four dimensions:

### 1. KANO Model Assessment (40% weight)

Evaluate product/service differentiation and market demand:
- **Differentiation Quality**: Unique features vs. competitors
- **Demand Authenticity**: Real user need vs. artificial demand
- **User Retention**: Frequency of use and long-term engagement

### 2. Industry & Competition Analysis (20% weight)

Analyze market structure and competitive positioning:
- **Market Concentration (CRn)**: Calculate market share of top competitors
- **Barrier to Entry**: Difficulty for new competitors to enter market
- **Incremental vs. Stock**: Growing market vs. market share competition
- **Leader Weaknesses**: Vulnerabilities of market leaders
- **Entry Barriers Assessment**: Regulatory, capital, technology barriers

### 3. Product Lifecycle Evaluation (10% weight)

Determine market stage and growth potential:
- **Market Stage**: Introduction → Growth → Maturity → Decline
- **Growth Drivers**: Key factors accelerating market expansion
- **Scale Effects**: Unit economics and network effects

### 4. Financial Analysis (30% weight)

Calculate key financial metrics:
- **PE Ratio**: Price-to-Earnings valuation
- **Growth Rate (SG)**: Year-over-year revenue/profit growth
- **PEG Ratio**: PE ÷ Growth Rate (valuation relative to growth)

### Scoring & Recommendation

**Overall Score** = (KANO × 0.40) + (Industry × 0.20) + (Lifecycle × 0.10) + (Financial × 0.30)

**Decision Logic**:
- **Score < 3.5**: "Do Not Invest" (red badge)
- **3.5 ≤ Score < 4.5**: "Conditional Investment" (yellow badge)
- **Score ≥ 4.5**: "Strong Investment" (green badge)

## Architecture Overview

### Database Schema

Core tables required:

- **users**: User authentication, roles (admin/user)
- **evaluations**: Investment records with composite scores, business briefs
- **kano_assessments**: KANO model scores (3 dimensions)
- **industry_assessments**: Industry analysis scores (5 dimensions)
- **lifecycle_assessments**: Lifecycle scores (3 dimensions)
- **financial_assessments**: Financial metrics (PE, growth rate, PEG)
- **memberships**: User subscription status (free/premium)
- **usage_logs**: API usage tracking for quota management

### Tech Stack

- **Frontend**: React 19 + Tailwind CSS 4 + shadcn/ui components
- **Backend**: Express 4 + tRPC 11 + Drizzle ORM
- **Database**: MySQL/TiDB
- **AI Integration**: LLM for auto-scoring and business brief generation
- **PDF Export**: Puppeteer for HTML-to-PDF rendering

## Implementation Workflow

### Phase 1: Database Setup

1. Create schema with all evaluation tables (see `references/schema.sql`)
2. Run migrations to initialize database
3. Set up user and membership management tables

### Phase 2: Backend API Development

Implement tRPC procedures for:

1. **Evaluation Management**
   - Create/update/delete evaluations
   - Retrieve evaluation list and details

2. **Auto-Scoring with LLM**
   - Analyze user-provided text to generate 1-5 scores
   - Implement for KANO, Industry, and Lifecycle dimensions
   - Financial dimension uses formula-based calculation (PE × Growth)

3. **Composite Scoring**
   - Calculate weighted overall score (40%, 20%, 10%, 30%)
   - Generate decision recommendation based on thresholds

4. **Business Brief Generation**
   - Synthesize all evaluation data
   - Perform web search for supplementary market data
   - Generate structured brief with Executive Summary, Market Analysis, Competitive Landscape, Financial Projections, Risk Assessment

5. **Report Export**
   - Export as PDF with headers/footers
   - Export as Markdown
   - Support one-click copy to clipboard

6. **Quota Management**
   - Check user quota before evaluation creation
   - Log usage in `usage_logs` table
   - Calculate remaining quota (free: 3/month, premium: 50/month)

### Phase 3: Frontend Development

1. **Evaluation List Page**
   - Display all evaluations with composite scores
   - Show quota status (e.g., "Free | 2/3 remaining")
   - Create new evaluation button
   - Links to AI assistant and Douyin configuration

2. **Evaluation Form**
   - Four tabs: KANO, Industry, Lifecycle, Financial
   - Text input fields for analysis (no manual scoring dropdowns)
   - Auto-scoring with loading states
   - Save/update/delete buttons

3. **Business Brief Tab**
   - Display generated brief with Markdown rendering
   - "Copy Brief" button (copies to clipboard)
   - "Export PDF" button (downloads formatted PDF)
   - Loading state during generation

4. **Membership Page**
   - Display free vs. premium plans
   - "Subscribe" button (9 CNY/month)
   - Show quota limits for each tier

5. **Douyin Bot Configuration Guide**
   - API documentation
   - Configuration steps
   - Quota and pricing explanation

### Phase 4: Integration & Optimization

1. Add quota checking before evaluation creation
2. Implement membership subscription logic
3. Optimize PDF styling (1.5x line spacing, headers/footers with date)
4. Add error handling and user feedback (toasts)
5. Implement AI chat assistant for investment consulting

## AI Integration Details

### Auto-Scoring Prompts

For each dimension, use structured prompts:

```
Analyze the following [DIMENSION] information and provide a score (1-5).
Consider: [specific factors for this dimension]
User data: [user input]
Return JSON: { score: number, reasoning: string }
```

See `references/scoring-prompts.md` for complete prompts for each dimension.

### Business Brief Generation

1. Collect all evaluation data
2. Identify missing information gaps
3. Use web search API to supplement data
4. Generate structured brief with:
   - Executive Summary (2-3 sentences)
   - Market Analysis (market size, growth rate, trends)
   - Competitive Landscape (key competitors, market share)
   - Financial Projections (revenue forecast, profitability)
   - Risk Assessment (key risks and mitigation)
   - Investment Recommendation (aligned with overall score)

## Quota Management

**Free Tier**: 3 evaluations per month
**Premium Tier**: 50 evaluations per month (9 CNY/month)

Implementation:

1. Check user's current month usage before creating evaluation
2. Log each evaluation creation in `usage_logs` table
3. Calculate remaining quota based on membership type
4. Show quota status in UI header
5. Display upgrade prompt when quota exhausted

## Customization Points

**Adjust Scoring Weights**: Modify the weights in the scoring algorithm (currently 40%, 20%, 10%, 30%)

**Change Quota Limits**: Update free tier (default 3) and premium tier (default 50) in quota checking logic

**Customize Evaluation Dimensions**: Add or remove dimensions by extending database schema and updating scoring prompts

**Modify Decision Thresholds**: Adjust the "pass" (3.5) and "excellent" (4.5) thresholds in recommendation logic

**Integrate Payment**: Use `webdev_add_feature` with `feature="stripe"` to enable real payment processing for premium subscriptions

## Bundled Resources

### references/

- **schema.sql**: Complete database schema with all tables and relationships
- **scoring-prompts.md**: LLM prompts for each evaluation dimension with examples
- **api-endpoints.md**: Complete tRPC API specification and request/response formats

## Next Steps

1. Read `references/schema.sql` to understand the complete database structure
2. Review `references/scoring-prompts.md` for LLM integration details
3. Check `references/api-endpoints.md` for backend API specification
4. Customize for your specific branding/requirements

## Common Customizations

**Adjust Scoring Weights**: Modify the weights in the scoring algorithm (currently 40%, 20%, 10%, 30%)

**Change Quota Limits**: Update free tier (default 3) and premium tier (default 50) in the quota checking logic

**Customize Evaluation Dimensions**: Add or remove dimensions by extending the database schema and updating scoring prompts

**Modify Decision Thresholds**: Adjust the "pass" (3.5) and "excellent" (4.5) thresholds in the recommendation logic

**Integrate Payment**: Use `webdev_add_feature` with `feature="stripe"` to enable real payment processing for premium subscriptions
