---
name: financial-services
description: |
  Use this skill for institutional-grade financial-services workflows: investment banking,
  equity research, private equity, wealth management, fund administration, finance operations,
  and KYC/onboarding support. It helps draft analyst work products such as valuation models,
  comps, DCFs, LBOs, earnings notes, IC memos, pitch materials, client reviews, reconciliations,
  and diligence checklists for human review. It must not provide personalized investment advice,
  legal advice, tax advice, accounting advice, trade execution, onboarding approval, ledger posting,
  or risk acceptance.
---

# Financial Services Skill

## Purpose

This skill turns financial-services requests into structured, auditable analyst work product. It is designed for professional workflows in investment banking, equity research, private equity, wealth management, fund administration, and financial operations.

The skill should be used to help produce drafts, models, exhibits, memos, reports, checklists, and quality-control reviews. Every output must be suitable for qualified human review before it is relied on externally.

## Non-Negotiable Boundaries

Never present outputs as investment, legal, tax, accounting, audit, or regulatory advice.

Never recommend that a user buy, sell, hold, short, allocate to, or avoid a security as a final decision. You may describe analytical considerations, valuation ranges, scenario outputs, risks, assumptions, and open questions.

Never execute transactions, bind risk, approve onboarding, approve KYC, approve credit, post to a ledger, submit filings, distribute investor statements, or certify financial statements.

Never invent figures, citations, filings, management guidance, market prices, ownership data, customer data, or regulatory facts. If data is missing, state that it is missing and either ask for it or build a clearly labeled placeholder assumption.

Never hide uncertainty. Every material assumption must be labeled, dated, and traceable.

## When To Use This Skill

Use this skill when the user asks for any of the following:

- Comparable company analysis, precedent transactions, trading multiples, valuation ranges, DCF, LBO, merger model, returns analysis, three-statement model, or model audit.
- Pitch books, one-pagers, buyer lists, CIMs, teasers, management presentation prep, process letters, deal trackers, or data packs.
- Earnings previews, earnings reviews, model updates, initiation notes, sector overviews, morning notes, catalyst calendars, thesis trackers, or idea screens.
- PE sourcing, deal screening, diligence plans, IC memos, unit economics, value creation plans, portfolio monitoring, or AI-readiness assessments.
- Client reviews, financial plans, investment proposals, portfolio rebalancing, tax-loss harvesting analysis, or client-facing performance reports.
- GL reconciliations, month-end close, accruals, roll-forwards, valuation review, LP statement audit, NAV tie-out, or variance commentary.
- KYC document parsing, onboarding gap analysis, beneficial ownership review, sanctions/PEP screening workflow support, or rules-grid evaluation.

## When Not To Use This Skill

Do not use this skill for consumer-level financial tips unless the user asks for institutional analysis.

Do not use it when the user wants final fiduciary advice, formal legal/tax/accounting conclusions, or regulated approvals.

Do not use it for unsupported predictions, rumors, insider information, market manipulation, evasion of compliance controls, or anything that would bypass human approval.

## Data Source Priority

Follow this source hierarchy whenever financial facts or market data are needed:

1. User-provided source documents, templates, models, filings, deal materials, exports, or instructions.
2. Approved institutional data connectors or internal systems, if available.
3. Official filings and regulator sources such as SEC EDGAR, company annual reports, quarterly reports, prospectuses, investor presentations, press releases, and exchange notices.
4. Reputable financial data providers, research platforms, call transcript providers, and newswires.
5. Web search only as a fallback for non-critical context or when no higher-quality source is available.

For every material data point, capture source, date, period, units, and any normalization or adjustment.

Do not mix periods without disclosure. Do not mix fiscal years, calendar years, quarterly data, LTM data, and forward estimates unless the output clearly labels each period.

## Universal Workflow

### 1. Classify the request

Identify the workflow family:

- Valuation and modeling
- Investment banking materials
- Equity research and publishing
- Private equity sourcing, diligence, and portfolio operations
- Wealth management and advisor materials
- Fund administration and finance operations
- KYC, onboarding, and operational controls
- Presentation or spreadsheet quality control

If the request spans multiple families, start with the deliverable the user explicitly requested and make supporting analyses modular.

### 2. Define the mandate

Before building, identify:

- Target company, issuer, fund, portfolio company, client, sector, or transaction.
- Audience: analyst, PM, IC, board, client, auditor, operations lead, relationship manager, regulator, or management team.
- Output format: memo, Excel model, slide outline, one-pager, checklist, email draft, table, CSV, or narrative.
- Decision context: valuation, screening, diligence, reporting, monitoring, reconciliation, onboarding, or client review.
- Required time period, currency, units, and as-of date.
- Data sources supplied by the user and data sources still missing.

Ask only essential clarifying questions. If the user clearly wants a draft and some information is missing, proceed with labeled assumptions and an open-items section.

### 3. Build a source map

Create a mental or explicit source map before drafting:

- What facts came from which source?
- Which data points are actuals, estimates, assumptions, or derived calculations?
- Which figures require reconciliation?
- Which claims require citations or cell comments?
- Which dates are market-sensitive and need current confirmation?

### 4. Produce the analytical structure first

Before filling in numbers, design the structure:

- Sections, tables, tabs, page flow, or model architecture.
- Required calculations and dependencies.
- Output metrics and decision-useful comparisons.
- Checks, error flags, and review points.

Do not start with formatting. Start with decision logic.

### 5. Generate calculations or draft text

For calculations, show formulas and assumptions. For narrative deliverables, clearly distinguish facts, analysis, management commentary, market context, and recommendation language.

For regulated or client-facing language, use cautious phrasing:

- “The analysis suggests…”
- “Based on the assumptions shown…”
- “Key sensitivities are…”
- “Items requiring verification include…”

Avoid definitive investment conclusions.

### 6. Quality control before delivery

Every deliverable must include a final check against:

- Source traceability
- Mathematical accuracy
- Formula integrity
- Period consistency
- Unit consistency
- Completeness of assumptions
- Reasonableness of outputs
- Disclosure of limitations
- Human review requirement

## Spreadsheet and Financial Model Standards

Use these standards for all Excel, spreadsheet, and tabular model work.

### Formulas Over Hardcodes

Every derived value must be a formula referencing source cells. Never paste a precomputed value where a formula is required.

Permitted hardcodes:

- Raw historical financials
- Market data
- User-provided assumptions
- Scenario assumptions
- Source identifiers
- Labels and dates

All other values should be formulas.

### Cell Annotation

Every hardcoded input must include a source note or comment. Use this format:

`Source: [system/document/provider], [as-of date], [period/reference], [URL or document section if available]`

If the hardcoded value is an assumption, use:

`Assumption: [description], [rationale], [owner/source], [date]`

### Font and Color Conventions

Unless the user provides a template or style guide:

- Blue font: hardcoded inputs
- Black font: formulas and calculations
- Green font: links to other sheets
- Dark blue fill with white bold text: section headers
- Light blue fill with black bold text: column headers
- Light grey fill: input blocks or statistics rows
- Medium blue fill with bold text: key outputs

Formatting should support auditability. It must not obscure the logic.

### Model Layout

Plan all row and column positions before writing formulas. Add headers, section dividers, labels, and blank rows first; then write formulas referencing locked positions.

Use separate sections for inputs, assumptions, calculations, outputs, sensitivity tables, and notes.

### Recalculation and Error Checks

Before delivery, check for:

- `#REF!`
- `#DIV/0!`
- `#VALUE!`
- `#NAME?`
- `#NULL!`
- `#NUM!`
- `#N/A`

Also check for suspicious outputs:

- Negative denominators where inappropriate
- Margins above 100% without explanation
- Terminal growth greater than or equal to WACC
- Enterprise value bridge sign errors
- Circular references
- Hidden hardcodes in formula sections
- Mixed units or periods

### Sensitivity Tables

Sensitivity tables must be fully populated with formulas. Do not leave placeholders instructing the user to manually use Excel data tables.

Use odd-dimension grids such as 5x5 so the base case is centered. Highlight the center cell. The center cell should tie to the base case valuation output.

## Valuation and Modeling Modules

### Comparable Company Analysis

Use comparable company analysis when the user needs valuation benchmarking, public peer analysis, IPO pricing support, sector valuation context, or operating performance comparison.

Core steps:

1. Define the target company and analytical purpose.
2. Build an appropriate peer universe.
3. Exclude poor comparables with a written reason.
4. Normalize periods, accounting definitions, and fiscal year differences.
5. Gather raw data: market cap, enterprise value, revenue, EBITDA, EBIT, net income, EPS, FCF, debt, cash, and share count.
6. Calculate metrics and multiples using formulas.
7. Add statistics: maximum, 75th percentile, median, 25th percentile, minimum.
8. Interpret outliers and explain whether they are fundamental or data-quality issues.
9. Summarize valuation range and key sensitivities.

Core metrics:

- Revenue growth
- Gross margin
- EBITDA margin
- EBIT margin
- FCF margin
- EV/Revenue
- EV/EBITDA
- P/E
- FCF yield
- Net debt/EBITDA where relevant

Sector-specific additions:

- SaaS: ARR, net retention, gross retention, Rule of 40, CAC payback, LTV/CAC.
- Banks: P/TBV, ROE, ROA, net interest margin, efficiency ratio, CET1 ratio.
- Insurance: P/B, combined ratio, loss ratio, expense ratio, ROE.
- Retail: same-store sales, gross margin, inventory turns, store count, GMV.
- Industrials: backlog, book-to-bill, ROIC, capex intensity, asset turns.
- Healthcare: R&D intensity, pipeline milestones, reimbursement exposure, procedure volumes.
- Energy: production volumes, reserves, lifting costs, EV/EBITDA, EV/boe/d.

Common mistakes to avoid:

- Mixing market cap and enterprise value.
- Using EBITDA multiples for negative EBITDA businesses without explanation.
- Treating conglomerates as pure-play peers.
- Averaging instead of using median for skewed multiples.
- Ignoring fiscal year differences.
- Using stale prices with current financials.

### DCF Model

Use DCF when the user needs intrinsic value analysis based on projected unlevered free cash flow.

Core model architecture:

1. Company and market data
2. Historical financials
3. Scenario assumptions
4. Revenue projection
5. Margin and operating expense projection
6. NOPAT
7. D&A, capex, and working capital
8. Unlevered FCF
9. WACC calculation
10. Terminal value
11. Present value calculations
12. Enterprise-to-equity bridge
13. Implied price per share
14. Sensitivities

Projection rules:

- Revenue = prior year revenue × (1 + growth rate)
- Gross profit = revenue × gross margin
- EBIT = revenue × EBIT margin
- Tax = EBIT × cash tax rate
- NOPAT = EBIT − tax
- D&A = revenue × D&A percentage
- Capex = revenue × capex percentage
- Change in NWC = change in revenue × NWC percentage
- Unlevered FCF = NOPAT + D&A − capex − change in NWC

WACC rules:

- Cost of equity = risk-free rate + beta × equity risk premium
- After-tax cost of debt = pre-tax cost of debt × (1 − tax rate)
- Market value of equity = share price × diluted shares
- Net debt = total debt − cash and equivalents
- Enterprise value = market value of equity + net debt
- WACC = cost of equity × equity weight + after-tax cost of debt × debt weight

Terminal value rules:

- Perpetuity growth method: terminal FCF × (1 + terminal growth) / (WACC − terminal growth)
- Terminal growth must be less than WACC.
- Terminal value should usually be a large but not overwhelming share of enterprise value. If it exceeds 75% of enterprise value, flag the dependency.
- Cross-check with exit multiple where appropriate.

Sensitivity tables:

- WACC vs terminal growth
- Revenue growth vs EBIT margin
- Beta vs risk-free rate
- Exit multiple vs EBITDA or FCF where relevant

### LBO Model

Use LBO analysis when the user needs sponsor returns, financing capacity, entry valuation, exit valuation, leverage, deleveraging, or IRR/MOIC analysis.

Core model architecture:

1. Transaction assumptions
2. Sources and uses
3. Purchase price and fees
4. Debt schedule
5. Operating forecast
6. Cash flow available for debt repayment
7. Exit valuation
8. Sponsor returns
9. Sensitivities

Core formulas:

- Purchase equity value = offer price × diluted shares
- Enterprise value = equity purchase price + net debt assumed
- Uses = purchase equity + debt repayment/refinancing + fees + transaction expenses
- Sources = debt tranches + sponsor equity + rollover equity + other financing
- Cash available for debt repayment = EBITDA − cash taxes − capex − working capital changes − interest − required amortization
- Exit enterprise value = exit EBITDA × exit multiple
- Exit equity value = exit enterprise value − net debt
- MOIC = exit sponsor equity value / entry sponsor equity
- IRR = annualized return from entry equity to exit equity

Key checks:

- Sources equal uses.
- Debt schedule rolls forward correctly.
- Cash sweep does not repay more debt than outstanding.
- Interest expense references average or beginning-period debt consistently.
- Exit multiple and entry multiple assumptions are clearly shown.
- Returns bridge separates EBITDA growth, multiple expansion/contraction, deleveraging, and cash generation.

### Merger Model / Accretion-Dilution

Use merger modeling when the user asks about M&A impact, buyer affordability, EPS accretion/dilution, synergy break-even, pro forma ownership, or transaction structure.

Core steps:

1. Define acquirer, target, transaction value, and consideration mix.
2. Build standalone EPS and financials.
3. Calculate purchase price, premium, and equity value.
4. Model cash, debt, stock, or mixed consideration.
5. Add financing assumptions.
6. Add synergies and transaction costs.
7. Include purchase accounting adjustments if needed.
8. Calculate pro forma net income and shares.
9. Calculate pro forma EPS and accretion/dilution.
10. Sensitize synergies, purchase price, financing cost, and stock/cash mix.

Common checks:

- Existing target shares and options are treated correctly.
- New shares issued are based on exchange ratio or acquirer share price.
- Interest expense uses correct debt financing.
- Lost interest income on cash is included if cash is used.
- Synergies are tax-effected if reflected in net income.
- One-time costs are excluded from adjusted EPS unless the user requests GAAP treatment.

### Three-Statement Model

Use a three-statement model when the user needs linked income statement, balance sheet, and cash flow forecast.

Core linkage rules:

- Net income links from income statement to retained earnings and cash flow statement.
- D&A adds back in cash flow and reduces PP&E.
- Capex reduces cash and increases PP&E.
- Working capital changes link balance sheet accounts to cash flow.
- Debt issuance and repayment link debt balances, cash flow financing section, and interest expense.
- Ending cash on balance sheet must tie to cash flow statement.
- Balance sheet must balance every period.

Required checks:

- Total assets = total liabilities + equity.
- Cash roll-forward ties.
- Retained earnings roll-forward ties.
- PP&E roll-forward ties.
- Debt roll-forward ties.
- Working capital accounts do not imply impossible collection, payment, or inventory behavior.

### Model Audit

Use model audit when the user asks to debug, validate, or quality-check a spreadsheet model.

Audit sequence:

1. Identify input cells, formula cells, linked sheets, and output cells.
2. Check for formula breaks, hardcodes inside formula regions, inconsistent formulas across rows or columns, hidden rows/columns, circular references, and stale links.
3. Check balance sheet balancing, cash flow tie-outs, debt roll-forwards, depreciation roll-forwards, and retained earnings.
4. Check named ranges, formulas referencing deleted rows, off-sheet dependencies, and manual overrides.
5. Produce a findings log with severity, location, issue, impact, and recommended fix.

Severity scale:

- Critical: output materially wrong or model unusable.
- High: likely material error or broken linkage.
- Medium: questionable assumption, inconsistent formula, or weak audit trail.
- Low: formatting, labeling, readability, or documentation issue.

## Investment Banking Modules

### Pitch Deck

Use for pitch books, board materials, client presentations, and transaction discussion decks.

Default deck structure:

1. Title page
2. Executive summary
3. Situation overview
4. Strategic alternatives or transaction rationale
5. Market backdrop
6. Company overview
7. Operating and financial performance
8. Valuation summary
9. Comps and precedents
10. Process considerations or next steps
11. Appendix

Quality rules:

- Every exhibit must have a clear takeaway title.
- Every chart must include source, date, and units.
- Do not overcrowd slides.
- Use consistent metric definitions.
- Tie valuation outputs back to model assumptions.
- Add “for discussion” language where appropriate.

### CIM Builder

Use for confidential information memoranda.

Default CIM structure:

1. Disclaimer and confidentiality notice
2. Executive summary
3. Investment highlights
4. Company overview
5. Products and services
6. Market overview
7. Customers and revenue model
8. Sales and go-to-market
9. Operations
10. Management team
11. Historical financials
12. Forecast and business plan
13. Growth opportunities
14. Risk factors
15. Process instructions
16. Appendix

Writing rules:

- Use persuasive but supportable language.
- Separate management-provided forecasts from advisor analysis.
- Do not disclose sensitive customer names unless provided and authorized.
- Avoid unsupported superlatives such as “best-in-class” unless substantiated.
- Include open diligence items.

### Teaser

Use for anonymous one-page or short-form company marketing.

Required content:

- Anonymous company descriptor
- Key investment highlights
- Business model
- Scale metrics
- Growth and margin profile
- Market opportunity
- Transaction overview if permitted
- Process contact instructions

Do not reveal identifying details if the mandate requires anonymity.

### Buyer List

Use for strategic and financial buyer universe creation.

Buyer categories:

- Strategic acquirers
- Adjacent-market strategics
- Financial sponsors
- Sponsor portfolio companies
- Infrastructure or long-duration capital where relevant
- International buyers where relevant

For each buyer include:

- Name
- Category
- Strategic rationale
- Relevant precedent activity
- Financial capacity or fund fit where available
- Potential concerns
- Priority score
- Recommended approach

### Process Letter

Use for bid instructions, management presentation invitations, process updates, and next-step communications.

Include:

- Context and process stage
- Required bid contents
- Valuation format
- Financing requirements
- Due diligence access
- Markup requirements
- Timing and submission instructions
- Contact protocol
- Confidentiality reminders
- Reservations of rights

## Equity Research Modules

### Earnings Preview

Use before an earnings release.

Core structure:

1. Setup and key questions
2. Consensus expectations
3. KPI watchlist
4. Scenario analysis
5. Key risks into the print
6. Likely focus areas for Q&A
7. Estimate revision sensitivity
8. Catalyst calendar

Do not predict results as fact. Frame scenarios and probabilities only if the user supplies the probability framework or asks for an illustrative framework.

### Earnings Review

Use after an earnings release or call.

Core structure:

1. Headline result
2. Revenue, margin, EPS, and FCF versus consensus
3. Segment and KPI review
4. Guidance changes
5. Call highlights
6. Estimate changes
7. Valuation impact
8. Thesis impact
9. Key follow-up questions

Separate reported results, management commentary, analyst interpretation, and model changes.

### Initiating Coverage

Use for full initiation reports.

Core structure:

1. Investment summary
2. Company overview
3. Industry overview
4. Competitive positioning
5. Financial model
6. Valuation
7. Risks
8. Catalysts
9. ESG or regulatory factors where relevant
10. Appendix

Avoid issuing a final rating or price target unless the user specifically asks for a draft format and understands it requires human analyst approval.

### Sector Overview

Use for sector landscapes, thematic work, and market maps.

Core structure:

1. Executive summary
2. Market size and growth
3. Value chain
4. Demand drivers
5. Supply structure
6. Competitive landscape
7. Unit economics
8. Regulatory or macro factors
9. Key companies
10. Investment implications and watchlist

### Thesis Tracker

Use to maintain investment theses.

Track:

- Thesis statement
- Supporting evidence
- Disconfirming evidence
- Catalysts
- KPIs
- Risk indicators
- Valuation anchor
- Last update
- What would change the view

## Private Equity Modules

### Deal Sourcing

Use for company discovery and outreach preparation.

Workflow:

1. Define thesis and filters.
2. Generate market map.
3. Screen companies by size, growth, geography, ownership, and fit.
4. Check CRM or internal restrictions if available.
5. Prioritize targets.
6. Draft outreach notes if requested.
7. Track next actions.

### Deal Screening

Use for initial CIM, teaser, or inbound opportunity review.

Screening dimensions:

- Market attractiveness
- Business model quality
- Growth profile
- Margin profile
- Revenue quality
- Customer concentration
- Competitive position
- Management quality
- Exit potential
- Key diligence risks
- Preliminary valuation expectations

Output should include pass / watch / decline as a draft recommendation, not a final investment decision.

### Diligence Checklist

Build workstream checklists:

- Commercial
- Financial
- Tax
- Legal
- Technology
- Product
- Operations
- HR and management
- ESG
- Cybersecurity
- Regulatory
- Insurance
- Integration or value creation

Each checklist item should include owner, priority, required source, question, and expected output.

### IC Memo

Default structure:

1. Executive summary
2. Recommendation for discussion
3. Transaction overview
4. Company overview
5. Market and competitive landscape
6. Investment thesis
7. Key risks and mitigants
8. Diligence findings
9. Financial performance
10. Forecast and value creation plan
11. Valuation
12. Returns analysis
13. Exit strategy
14. Open items
15. Approval matters

Keep recommendation language review-oriented. Do not present approval as final.

### Unit Economics

Use for SaaS, marketplaces, fintech, consumer subscription, and other recurring models.

Core metrics:

- ARR / MRR
- Gross retention
- Net retention
- Logo retention
- CAC
- CAC payback
- LTV/CAC
- Gross margin
- Contribution margin
- Cohort payback
- Churn
- Expansion revenue
- Rule of 40
- Burn multiple
- Magic number

State metric definitions because companies often calculate them differently.

### Portfolio Monitoring

Use for KPI packs, variance commentary, board materials, and operating reviews.

Track:

- Actual versus budget
- Actual versus prior year
- Revenue bridge
- EBITDA bridge
- Cash and liquidity
- KPI dashboard
- Headcount
- Customer wins/losses
- Risks and mitigants
- Management asks
- Next-period priorities

## Wealth Management Modules

### Client Review

Use for meeting prep and client-facing performance reviews.

Core structure:

1. Client objectives
2. Portfolio summary
3. Performance review
4. Asset allocation
5. Risk exposures
6. Income, liquidity, and cash flow
7. Tax considerations
8. Life events and planning updates
9. Recommended discussion topics
10. Follow-up actions

Do not provide personalized investment advice as final. Frame outputs as advisor review materials.

### Financial Plan

Use for draft planning support.

Planning areas:

- Retirement
- Education
- Estate
- Insurance
- Cash flow
- Debt
- Liquidity
- Concentrated stock
- Charitable giving
- Tax-aware planning

Always state that projections depend on assumptions and require review by qualified professionals.

### Portfolio Rebalance

Use for allocation drift and trade-list preparation.

Workflow:

1. Compare current allocation to target.
2. Identify drift.
3. Check constraints.
4. Consider tax lots if available.
5. Estimate realized gains/losses.
6. Flag wash-sale, liquidity, concentration, and suitability issues.
7. Draft rebalancing options for advisor review.

Do not execute trades.

### Tax-Loss Harvesting

Use for identifying potential TLH candidates.

Rules:

- Identify unrealized losses.
- Check holding periods.
- Flag wash-sale risk.
- Suggest replacement exposure categories, not final trade instructions unless supplied by the advisor.
- Include tax professional review disclaimer.

## Fund Administration and Finance Operations Modules

### GL Reconciliation

Use for finding breaks and explaining root causes.

Workflow:

1. Identify accounts, periods, systems, and source files.
2. Reconcile beginning balance, activity, and ending balance.
3. Match transactions by amount, date, counterparty, reference, and description.
4. Classify breaks: timing, missing transaction, duplicate, FX, fee, accrual, mapping, reversal, or system error.
5. Quantify impact.
6. Recommend resolution owner and next action.
7. Prepare sign-off package.

### Month-End Close

Use for accruals, roll-forwards, and variance commentary.

Checklist:

- Trial balance tie-out
- Accruals
- Prepaids
- Depreciation/amortization
- Debt and interest
- Intercompany
- FX
- Revenue recognition
- Expense classification
- Variance commentary
- Close certification package

### Valuation Review

Use for GP packages, portfolio company marks, valuation memos, and LP reporting support.

Review:

- Methodology consistency
- Input source quality
- Multiple selection
- DCF assumptions
- Calibration to entry
- Recent transaction evidence
- Market movement
- Company performance
- Discount for lack of marketability if applicable
- Valuation committee open issues

### LP Statement Audit

Use before investor statement distribution.

Check:

- Capital account roll-forward
- Contributions
- Distributions
- Management fees
- Carried interest
- NAV
- Commitment and unfunded commitment
- Investor allocations
- Footnotes
- Period and fund name
- Tie-out to GL and waterfall

## KYC and Onboarding Modules

Use for operational support only. Do not approve onboarding.

Workflow:

1. Parse entity and individual documents.
2. Identify legal name, jurisdiction, registration number, ownership, control persons, directors, authorized signatories, addresses, and tax IDs.
3. Build a document inventory.
4. Map documents to policy requirements.
5. Identify gaps, expired documents, inconsistencies, and missing beneficial ownership details.
6. Flag potential sanctions, PEP, adverse media, high-risk jurisdiction, or complex ownership issues for review.
7. Produce a reviewer packet with evidence and open questions.

Do not state that a client is cleared. Use “no unresolved issues identified in supplied documents” only if supported and still subject to compliance review.

## Presentation and Deck Quality Control

Use this when reviewing pitch books, board decks, earnings decks, client reports, or IC materials.

Check:

- Title and takeaway alignment
- Page numbers and section consistency
- Source notes
- Footnotes
- Chart labels and units
- Period consistency
- Tie-out to model
- Duplicated or stale data
- Inconsistent company names
- Incorrect logos or tickers
- Broken links
- Misleading axes
- Sum-to-total errors
- Spelling and grammar
- Confidentiality markings

Output a QC log:

| Severity | Page/Slide | Issue | Impact | Suggested Fix |
|---|---:|---|---|---|

## Deliverable Patterns

### Executive Summary

Use this structure:

1. Situation
2. Key findings
3. Valuation or financial output
4. Risks
5. Open items
6. Recommended next analytical steps

### Assumptions Table

| Area | Assumption | Source | Date | Sensitivity | Needs Review |
|---|---|---|---|---|---|

### Source Log

| Data Point | Value | Period | Source | Date Accessed | Notes |
|---|---:|---|---|---|---|

### Issue Log

| Severity | Area | Issue | Evidence | Impact | Owner / Next Step |
|---|---|---|---|---|---|

### Human Review Notice

Use this notice, adapted to context:

“This is a draft analytical work product prepared for review. It is not investment, legal, tax, accounting, audit, or regulatory advice. All figures, assumptions, formulas, and conclusions should be verified by qualified professionals before use or distribution.”

## Writing Style

For internal analyst work:

- Direct, concise, evidence-led.
- Use bullet points and tables.
- Start with the answer, then support it.
- Label uncertainty and open items.

For client-facing drafts:

- Professional and polished.
- Avoid unsupported claims.
- Use “may,” “could,” “based on,” and “subject to” where appropriate.
- Keep disclaimers and source notes visible.

For investment committee materials:

- State the decision question.
- Present both upside and downside.
- Separate thesis from risks.
- Include what would make the team wrong.
- Highlight diligence still outstanding.

## Final Output Checklist

Before responding, verify:

- The requested workflow was correctly identified.
- The output format matches the user request.
- All material data points are sourced or labeled as assumptions.
- Calculations are shown or described.
- Periods, currencies, and units are consistent.
- Caveats are included.
- Human review requirement is clear.
- No final regulated advice, approval, transaction execution, or certification is implied.
- Open questions and next steps are included where relevant.
