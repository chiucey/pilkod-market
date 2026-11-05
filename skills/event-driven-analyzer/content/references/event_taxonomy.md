# Event Taxonomy and Classification

Use this reference when the event type is ambiguous, or when one setup carries several overlapping catalysts.

## How to classify

Classify by the investment path, not by the headline. Multiple labels are normal. A cash merger can simultaneously be an antitrust event, a litigation event, a financing event, and a shareholder-vote event — all four labels may matter.

**Ownership boundary.** This skill applies when the central work is the dated event path, probability, timing, payoff, expected return, and monitoring math. Hand off to 独立信用分析流程 when the central work is capital structure, covenant / document review, liquidity, maturity wall, priority, fulcrum-security analysis, or recovery-waterfall analysis.

---

## Primary event types

The list below is grouped roughly by deal mechanics. Each entry states the underwriting question and the analytic outputs the classification implies.

### Cash merger arbitrage
- Question: will the deal close, when, and what is the break price?
- Outputs: spread, annualized spread, implied close probability, break downside, close/delay/break/recut scenarios.

### Stock-for-stock merger arbitrage
- Question: is the spread attractive after exchange ratio, acquirer hedge, collar, dividends, borrow, and acquirer drift risk?
- Outputs: deal value, hedge ratio, spread, collar sensitivity, acquirer risk, vote risk.

### Tender offer
- Question: will tender conditions be satisfied, and what happens if the minimum or a regulatory condition fails?
- Outputs: tender deadline, proration, minimum condition, withdrawal rights, extension path.

### CVR / contingent consideration
- Question: what is the probability-weighted value of the future milestones, and are incentives aligned?
- Outputs: milestone tree, discounting, control-party incentive analysis, liquidity discount.

### Spin-off / split-off
- Question: what are SpinCo and RemainCo worth separately, and what technical flows create opportunity?
- Outputs: SOTP, distribution mechanics, forced-selling analysis, index eligibility, capital structure, management incentives.

### Activism
- Question: can the activist force value creation or governance change, and what outcome is priced in?
- Outputs: campaign demands, vote math, board vulnerability, settlement probability, annual-meeting timeline, value plan.

### Restructuring / distressed event
- Question: which dated restructuring, exchange, court, maturity, or liability-management catalyst changes value, when, and with what payoff?
- Outputs: event path, process timeline, probability tree, sourced recovery / payoff assumptions, scenario EV, monitoring thresholds. Capital structure, covenants, liquidity, maturity wall, priority, fulcrum security, and recovery waterfall are handed to 独立信用分析流程.

### Litigation
- Question: what is the probability-weighted investment impact of trial, ruling, settlement, appeal, injunction, or damages?
- Outputs: merits matrix, damages / remedy range, procedural timeline, settlement incentives, security impact.

### Regulatory event
- Question: which regulator controls the path, what process applies, and what remedies or delays are likely?
- Outputs: agency map, review stage, statutory timeline, theory of harm, remedy feasibility, interaction with outside date.

### Index / technical event
- Question: what flow is expected, who must buy or sell, and how much is already priced?
- Outputs: inclusion / deletion logic, rebalance date, expected flow, liquidity, crowding, unwind plan.

### De-SPAC / SPAC event
- Question: what is the post-close equity really worth after redemption, PIPE, sponsor promote, warrant dilution, and lockups?
- Outputs: trust value, redemption, PIPE, minimum cash, sponsor economics, float, lockups, dilution, projection skepticism.

### Capital return / Dutch tender / exchange offer
- Question: what is the economic effect after proration, tax, participation, leverage, and signaling?
- Outputs: tender range, proration scenarios, accretion / dilution, balance-sheet impact, shareholder behavior.

---

## Intake questions, by context

Only ask for what is necessary and unavailable. If the user has already given enough to start, proceed with best-effort and label assumptions.

**Minimal intake**
- Company / ticker and security.
- Event type, if known.
- The user's position or intended trade, if relevant.
- Output mode — only if the user wants something other than the default full memo (explicit quick read, model / math, red team, monitoring update).
- Allowed sources, and whether to use callable connected routes, user-provided exports, or public web.

**Event-specific missing facts**
- Merger: deal price, current price, expected close, outside date, break price, approvals.
- Stock deal: exchange ratio, acquirer price, collar, dividends, borrow.
- Spin: distribution ratio, SpinCo / RemainCo financials, dates, debt allocation.
- Activism: activist, ownership, demands, annual meeting date, nomination deadline.
- Litigation: venue, claim, procedural posture, next hearing / trial date, damages theory.
- Regulatory: agency, filing status, review stage, outside date, remedy path.
- Restructuring / distressed: dated catalyst, court / RSA / exchange / maturity status, next process date, security expression, and any recovery / payoff assumptions already available. Debt stack, liquidity, maturities, prices, covenant status, and recovery waterfall go to 独立信用分析流程 when central.

---

## Multi-label examples

- `Cash merger + antitrust + financing` — sponsor take-private at high leverage with overlapping assets.
- `Spin-off + index technical + balance-sheet event` — parent distributes a small levered SpinCo that index funds cannot hold.
- `Activism + sale process + governance` — activist demanding board seats while pushing strategic alternatives.
- `Litigation + regulatory + merger arb` — regulator suing to block, with trial schedule driving deal timing.
- `Distressed exchange + litigation + equity stub` — LME under way as creditor group challenges the transaction.

---

## What the classification implies for output

The label set determines what analysis must appear:

- Merger arb: spread / probability / break-price math.
- Spin: SOTP and forced-selling analysis.
- Activism: vote math and campaign path.
- Litigation: merits / timing / damages / settlement.
- Regulatory: agency process and remedy.
- Restructuring (this skill): dated process path, probability / payoff tree, monitoring plan. Capital structure, covenant, and recovery waterfall work belongs to 独立信用分析流程.
- Technical events: flow / liquidity / crowding.
