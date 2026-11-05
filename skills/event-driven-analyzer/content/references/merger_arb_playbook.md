# Merger Arbitrage Playbook

Reference for cash mergers, fixed-ratio and floating stock-for-stock deals, tender offers, collars, competing bids, recuts, CVR consideration, and deal-break scenarios. The playbook is organized **by lifecycle stage**: setup -> diligence -> pricing -> recommendation -> closeout.

## PM objective

Decide whether the residual spread compensates for the actual residual risk after timing, downside, financing, regulatory path, shareholder vote, acquirer drift, and execution constraints (borrow, liquidity, withdrawal mechanics).

---

## Stage 1 — Setup: required fact pack

Pull the following before any math is published.

**Identifiers and dates**
- Buyer, target, ticker(s), security, listing venue.
- Announcement date and unaffected date.
- Current target price + market-data timestamp.

**Consideration**
- Form: cash, stock, mixed, election, collar, CVR, tender.
- Per-share deal value and aggregate transaction value.
- Current gross spread and annualized spread.

**Process gates**
- Expected close date vs. outside date (these are not the same).
- Required approvals: target vote, acquirer vote (if applicable), antitrust, CFIUS, sector regulator, foreign filings.
- Conditions precedent: financing, no-injunction, MAE, minimum tender, tax opinion, listing approval.

**Economic protections**
- Break fee, reverse termination fee, ticking fee where applicable.
- Financing commitments and their expiration.
- Pending litigation status.

**Execution inputs (only if hedging is on the table)**
- Borrow availability and options-market liquidity.
- Source documents reviewed, and a list of missing documents.

---

## Stage 2 — Diligence by deal archetype

Pick the branch that matches the deal structure. Each branch lists what the output **must** produce, then a list of senior checks.

### Branch A — Cash deal

Must produce:
- Gross spread.
- Annualized spread.
- Market-implied close probability (formula below).
- Analyst probability tree.
- Break price / downside methodology.
- Expected value and expected annualized return.
- Gating item and next catalyst.
- Trade recommendation.

Market-implied probability:

`(current target price - break price) / (cash deal price - break price)`

Senior checks:
- Is the break price leak-adjusted and peer-adjusted, or just the raw unaffected print?
- Did target post weak earnings or guidance after announcement, making downside worse than the unaffected anchor?
- Is the reverse termination fee large enough to signal real buyer commitment?
- Does the buyer have a financing-out or conditional-funding clause?
- Does the outside date leave enough runway for a remedy or litigation path?
- Is the spread wide because of real risk, or because of crowding, illiquidity, small-cap neglect, tax, index deletion, or borrow mechanics?

### Branch B — Fixed/floating stock-for-stock deal

Must produce:
- Exchange ratio and deal value.
- Long-target / short-acquirer hedge ratio.
- Gross spread and annualized spread.
- Collar sensitivity if applicable.
- Dividend and borrow adjustments.
- Acquirer vote risk.
- Acquirer fundamental risk and stock volatility.
- Residual beta and factor exposure on the spread leg.

Senior checks:
- Does the acquirer short raise borrow, dividend, or short-squeeze risk?
- Does the collar reshape the hedge as the acquirer drifts?
- Does the acquirer's shareholder base actually support this transaction?
- Is the acquirer overpaying in a way that creates short-leg risk if the deal breaks?
- Is the target really the cleanest expression, or is the acquirer mispriced and the better trade is on the acquirer side?

### Branch C — Tender offer

Must produce:
- Offer price and expiration.
- Minimum tender condition.
- Proration mechanics.
- Withdrawal rights.
- Extension path.
- Regulatory conditions.
- Back-end merger or squeeze-out process.
- Tax considerations where relevant.

Senior checks:
- Can the tender close without a separate shareholder meeting?
- Is the minimum condition realistically achievable given the holder base?
- Are arbs or insiders blocking participation that would otherwise meet the minimum?
- Does the buyer have the financing capacity and legal headroom to extend if needed?

---

## Stage 3 — Underwrite the regulatory path

Do not write "regulatory risk" as a generic line item. Make the underwriting specific:
- Agency and jurisdiction.
- Review stage.
- Theory of harm.
- Market definition.
- Customer / competitor opposition.
- Remedy feasibility.
- Political sensitivity.
- Litigation probability.
- Interaction with outside date and financing expiration.

Common issue archetypes to consider:
- Horizontal concentration.
- Vertical foreclosure.
- Potential competition.
- Nascent competition.
- Platform / ecosystem entrenchment.
- Labor-market effects.
- Buyer power or monopsony.
- Serial acquisition / roll-up.
- National security / data sensitivity.

---

## Stage 4 — Pull the deal document apart

From the merger agreement or tender documents, extract and label:
- Consideration and adjustment mechanisms.
- Outside date and extension mechanics.
- Regulatory-efforts covenant (reasonable best efforts, hell-or-high-water, divestiture cap).
- No-shop, go-shop, fiduciary out.
- Matching rights.
- Break fee and reverse termination fee.
- Financing cooperation and debt commitment terms.
- MAE definition and carveouts.
- Interim operating covenants.
- Termination rights.
- Specific performance availability.
- Shareholder support agreements.

---

## Stage 5 — Scenario tree template

Most deals warrant scenarios for:
- Close on time.
- Close with delay / remedy.
- Price recut.
- Competing bid / higher bid where plausible.
- Break.

Each scenario carries probability, timing, terminal value, return, rationale, signposts.

---

## Stage 6 — Recommendation phrasing (examples)

Calibrate language to evidence:
- "Attractive, but size as a regulatory trade rather than a clean arb. The spread pays for a second-request path, but not for full litigation."
- "Avoid despite optical annualized spread. Break downside is understated and buyer financing is vulnerable."
- "Prefer options because the event is binary and the timeline is uncertain."
- "Prefer long target / short acquirer at deal ratio; residual acquirer vote risk argues for lower sizing."

---

## Stage 7 — Final checklist

Before sign-off:
- Deal terms verified from primary source, or explicitly marked unverified.
- Current price and spread carry a timestamp.
- Break price is triangulated (not just blindly unaffected).
- Market-implied probability is shown.
- Our analyst probability tree is shown and sums to 100%.
- Gating item is specific to a controller / process step / date.
- Outside date and expected close date are treated as separate fields.
- Trade expression and a sizing / risk note are included.
- Monitoring plan names the next date and the action attached to each signal.
