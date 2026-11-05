---
name: equity-research
description: >-
  Research stocks, companies, markets, filings, earnings, valuation, corporate actions, and financial claims
  with dated and normalized data. Use when investigating a ticker, company financials, market context, why a
  price moved, or a financial rumor. Normalize and quality-check data before modeling or reporting.
  Research only; do not place orders or give personalized trading instructions.
---

# Equity Research

A portable, research-only skill for investigating equities, companies, markets, filings, earnings, valuation,
corporate actions, catalysts, risks, and financial claims.

## Core workflow

Always follow:

`identify -> normalize -> quality-check -> model -> report`

Use two conceptual layers:

1. **Data layer** — produce traceable, normalized inputs.
2. **Report layer** — explain fundamentals, valuation, catalysts, risks, scenarios, and unresolved issues.

Do not bypass data-quality checks before modeling or reporting.

---

## 1. Identify the instrument and observation point

Before combining data, identify and record:

- market/exchange;
- ticker;
- legal entity;
- share class;
- currency;
- market timezone;
- trading session;
- observation timestamp;
- whether each value is real-time, delayed, or historical.

Resolve ticker changes, mergers, aliases, spin-offs, suspensions, delistings, and cross-listed shares before
combining datasets.

Never call a timestamp-free web quote "real-time".

---

## 2. Normalize raw data

Prefer, in roughly this order:

1. exchange notices and official market data;
2. regulator filings and disclosure systems;
3. SEC/EDGAR or local equivalents;
4. company investor-relations pages and audited reports;
5. central banks/statistical agencies for macro context;
6. licensed or documented market-data services;
7. reputable financial media for context/cross-checking;
8. community discussion and search snippets only as leads/sentiment.

For every raw item, preserve:

```yaml
instrument: "ticker/entity/share class"
market: "market"
currency: "ISO-4217 or unknown"
unit: "unit scale or unknown"
value: "raw value"
period: "fiscal period or date range"
publication_date: "date or unknown"
captured_at: "ISO-8601"
adjustment_status: raw | split_adjusted | dividend_adjusted | total_return | unknown
source_url: "https://..."
transformation: "none or explicit formula/rate/date"
```

Also record, when applicable:

- statement/line-item definition;
- consolidated vs segment vs continuing-operation scope;
- accounting standard (GAAP, IFRS, local standard, or other);
- reported vs adjusted/non-GAAP status;
- exchange-rate date when currency conversion is performed;
- restatement/reclassification status;
- source page/table or equivalent evidence location.

### Normalization rules

Do not combine unlike:

- fiscal periods;
- reporting scopes;
- currencies;
- unit scales;
- accounting definitions;
- share classes;
- adjustment states;

unless the transformation is explicit and traceable.

Keep raw inputs and derived values conceptually separate.

Do not compare quarterly, annual, and TTM figures without labeling the periods.

Do not call management-defined adjusted earnings GAAP/IFRS.

Preserve restatements and reclassifications instead of silently overwriting history.

---

## 3. Corporate actions and price-series normalization

Track, when relevant:

- announcement date/time;
- record date;
- ex-date;
- effective date;
- ratio or cash amount;
- source.

Include:

- splits and reverse splits;
- dividends;
- rights issues;
- buybacks;
- tender offers;
- ticker/name changes;
- trading suspensions;
- delistings.

Label price series explicitly as:

- raw close;
- split-adjusted;
- dividend-adjusted;
- total-return;
- unknown adjustment status.

Check whether the source has already adjusted a series. Never double-adjust prices.

Use:

- announcement time for event-study timing;
- ex-date for price-impact analysis.

---

## 4. Data-quality checks

Before valuation, scenario analysis, or a strong conclusion, check for:

- source/period mismatch;
- unit errors;
- currency errors;
- sign errors;
- decimal-place errors;
- restatements;
- missing periods;
- price discontinuities around corporate actions;
- earnings growth without corresponding cash-flow support;
- receivables materially ahead of revenue;
- inventory materially ahead of revenue;
- unusual related-party transactions;
- one-off gains;
- aggressive capitalization;
- unusual non-GAAP adjustments;
- conflicting prices;
- conflicting filings;
- conflicting dates;
- conflicting share counts;
- inaccessible evidence;
- snippet-only evidence.

These are **review signals, not proof of fraud or manipulation**.

When a red flag appears, state what evidence would resolve it, such as:

- a filing;
- a footnote;
- an accounting policy;
- an audit disclosure;
- an independent market-data source;
- an exchange/regulator notice.

Do not turn an anomaly into an accusation without supporting evidence.

---

## 5. Define indicators before comparing them

Every metric must have a clear definition.

### Revenue and growth

Specify:

- period;
- currency;
- reported vs constant-currency basis.

### Gross, operating, and net margin

Specify:

- numerator;
- denominator;
- scope.

### ROE / ROIC

Specify:

- equity/capital definition;
- average-balance vs ending-balance methodology.

### Leverage

Specify treatment of:

- debt;
- cash;
- leases;
- other debt-like obligations;
- net debt.

### Cash flow

Separate:

- operating cash flow;
- investing cash flow;
- financing cash flow;
- free cash flow, with an explicit definition.

### Valuation multiples

For PE / PB / PS / EV-EBITDA, specify:

- price/enterprise-value date;
- earnings/revenue/book-value period;
- share count;
- diluted vs basic shares;
- net debt treatment;
- currency;
- accounting basis;
- peer set.

Historical and peer comparisons must disclose differences in:

- period;
- currency;
- accounting standard;
- adjustment methodology;
- capital structure where relevant.

---

## 6. Valuation and scenarios

### Multiples

For each multiple, show:

- numerator;
- denominator;
- period;
- share count;
- net debt;
- currency;
- peer set;
- accounting definition.

Do not compare multiples that are built from materially different definitions without explaining the difference.

### DCF

Expose, at minimum:

- forecast horizon;
- revenue assumptions;
- operating-margin assumptions where used;
- free-cash-flow assumptions;
- discount rate;
- terminal growth rate or exit multiple;
- net debt;
- diluted shares;
- valuation currency;
- sensitivity ranges.

### Scenarios

When scenarios are requested, use:

- bear;
- base;
- bull.

Clearly distinguish:

- observed facts;
- management claims;
- analyst interpretation;
- model assumptions;
- model outputs.

Every estimate and model result must be labeled as such.

A target price is a model output, not a verified fact and not a personalized recommendation.

A valuation is not a promise.

---

## 7. News, catalysts, and rumor verification

For catalysts, record:

- claim;
- event date/time;
- publication date;
- source;
- source type;
- what is confirmed;
- what is unconfirmed;
- market reaction, if relevant.

Prefer official company, exchange, and regulator evidence for material claims.

If the question is whether a financial rumor is true:

1. treat the rumor as an unverified claim;
2. search current official company, exchange, and regulator records;
3. cross-check reputable financial media;
4. separate confirmation from inference;
5. report unresolved portions explicitly.

Do not treat an unverified rumor as a fact or as a catalyst.

Community discussion may help identify a lead or sentiment but is not primary evidence for material factual claims.

---

## 8. Report structure

Use this structure unless the user asks for a materially different format:

```markdown
# Equity research: <ticker> <name>

## Market snapshot (as of <date/time/timezone>)

## Fundamentals and normalized financials

## Valuation (history/peers and assumptions)

## Catalysts and event timeline

## Technical observations (optional, dated)

## Bull case

## Bear case

## Key risks and unresolved data

## Sources, periods, units, delays, and transformations
```

### Report rules

Include:

- dated market snapshot;
- normalized financial fundamentals;
- valuation vs history and peers;
- news catalysts and event timeline;
- optional descriptive technical analysis;
- bull case;
- bear case;
- key risks;
- macro and industry context where relevant;
- data sources and dates;
- periods and units;
- transformations;
- adjustment status;
- delay/freshness information;
- conflicts and unresolved fields.

Place a data-quality note before a confident conclusion.

Do not hide missing or delayed data.

---

## 9. Evidence and source ledger

For important claims, maintain a simple evidence ledger with fields such as:

```yaml
claim: "statement being supported"
source: "source name"
source_type: "exchange | regulator | filing | IR | audited_report | data_service | media | community"
publication_date: "date or unknown"
captured_at: "ISO-8601"
url: "https://..."
evidence_location: "page/table/section or equivalent"
relation: "supports | contradicts | contextualizes"
access_limit: "none | delayed | paywalled | partial | inaccessible"
adjustment_policy: "description or unknown"
status: "confirmed | disputed | unresolved"
```

Record source relation, publication date, capture time, access limits, update policy, and adjustment policy when
these materially affect interpretation.

---

## 10. Platform adapters and capability mapping

The host platform may implement these capabilities in different ways:

| Capability | Minimum output | Possible implementation |
|---|---|---|
| `quote_source` | quote, timestamp, delay, currency, adjustment status | exchange or market-data service |
| `filing_source` | filing/IR document, period, page/table, date | regulator or company repository |
| `financial_parser` | line items with units, periods, scope, accounting basis | PDF/XBRL/table parser |
| `accounting_normalizer` | raw-to-normalized values and transformations | host data layer |
| `corporate_action_adjuster` | action dates, ratios, adjusted series | market-data/corporate-action source |
| `valuation_model` | assumptions, scenarios, sensitivity, derived values | spreadsheet or model runtime |
| `quality_checker` | flags with evidence and unresolved state | host analysis tools |
| `news_catalyst_search` | dated claims and source records | web/news search |
| `evidence_ledger` | claim/source records | host schema |
| `xlsx_export` | table file and validation status | spreadsheet adapter |
| `structured_output` | Markdown plus JSON/YAML | host renderer |

When using an adapter, record as relevant:

- authentication requirements;
- quota/rate limits;
- regional limitations;
- freshness;
- adjustment policy;
- output format;
- privacy constraints;
- failure states.

If a capability is unavailable:

1. narrow the scope;
2. do not invent the missing data;
3. mark affected fields unresolved;
4. explain what evidence/capability is missing.

Spreadsheet export is optional. It is an artifact/output capability, not part of the financial definitions.

---

## 11. Research boundaries

This skill is for research and scenario analysis only.

Do not:

- place orders;
- manage an account;
- execute trades;
- present personalized buy/sell instructions;
- imply certainty about future prices;
- present model outputs as facts.

Always label:

- delayed data;
- incomplete data;
- modeled data;
- management claims;
- estimates;
- unresolved conflicts.

---

## 12. Completion checklist

Before finalizing an equity-research answer, verify that the following are visible or explicitly marked unresolved:

- instrument;
- legal entity;
- share class;
- market;
- currency;
- observation date/time/timezone;
- trading session where relevant;
- delay/freshness;
- adjustment status;
- raw inputs;
- normalized inputs;
- transformations;
- corporate actions;
- accounting basis;
- periods;
- units;
- valuation assumptions;
- scenario assumptions;
- source dates;
- evidence locations where material;
- source conflicts;
- unresolved fields;
- data-quality concerns.

Every derived number should be traceable back to preserved inputs and stated transformations.

The final report must not contain a personalized trading instruction.

---

## Minimal operating rule

When in doubt, prefer:

**traceability over speed, primary evidence over snippets, explicit normalization over silent assumptions, and
qualified conclusions over false certainty.**
