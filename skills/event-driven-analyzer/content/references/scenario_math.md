# Scenario Math and Calculation Frameworks

Reference for dated-event spread, annualized return, market-implied probability, stock-deal hedge ratio, scenario EV, CVR pricing, spin SOTP, and payoff math. Capital structure, covenants, priority, fulcrum security, and recovery waterfall are out of scope — those belong to 独立信用分析流程, and this skill consumes the outputs as terminal-value assumptions.

## Return primitives

### Gross return

`gross_return = terminal_value / current_price - 1`

### Annualized return

`annualized_return = (1 + gross_return) ** (365 / days_to_resolution) - 1`

Use simple annualization only when the user expects it:

`simple_annualized_return = gross_return * 365 / days_to_resolution`

Caveat: annualized return is misleading for binary trades. Always pair annualized spread with downside and expected value.

---

## Cash merger arbitrage

Inputs:
- Current target price.
- Cash deal price.
- Estimated close date or days to close.
- Break price / downside.
- Dividends, financing cost, borrow where relevant.

Outputs:
- Gross spread.
- Annualized spread.
- Market-implied close probability.
- Probability-weighted expected return.

Implied-probability formula:

`market_implied_probability = (current_price - break_price) / (deal_price - break_price)`

Interpretation:
- If implied probability sits below the analyst's probability and downside is defensible, the spread may be attractive.
- If implied probability is low because downside is understated, the spread may be a value trap.

Common adjustments:
- Add expected dividends if the holder receives them.
- Subtract financing / carry cost.
- Adjust terminal values for recut or remedy scenarios.
- Add explicit delay scenarios when timing is uncertain.

---

## Stock-for-stock merger arbitrage

Inputs:
- Target price.
- Acquirer price.
- Exchange ratio.
- Collar terms, if any.
- Expected dividends.
- Borrow cost and hedge availability.
- Days to close.

Formulas:
- `deal_value = acquirer_price * exchange_ratio`
- `gross_spread = deal_value / target_price - 1`
- `hedge_shares = target_shares * exchange_ratio`

Adjustments:
- Fixed vs. floating exchange ratio.
- Collars and walk-away thresholds.
- Proration and election mechanics.
- Dividend mismatch between target and acquirer.
- Borrow cost on the short-acquirer leg.
- Acquirer vote risk and acquirer fundamental risk.
- Residual exposure when the hedge ratio is partial or collar-dependent.

---

## CVR valuation

Inputs per milestone:
- Payment amount.
- Probability of achievement.
- Expected payment date.
- Discount rate.
- Transferability / liquidity discount.
- Enforcement or sponsor incentive risk.

Formula:

`cvr_value = sum(payment_i * probability_i / (1 + discount_rate) ** years_i) - liquidity_discount`

Senior checks:
- Are milestones independent or conditional?
- Does management / the control party have incentive to maximize or minimize payout?
- Is there reporting transparency?
- Is the CVR tradeable?
- Are there comparable outcomes?

---

## Scenario tree EV

Each scenario must carry:
- Scenario name.
- Probability.
- Timing in days or months.
- Terminal value.
- Rationale.
- Signposts.

公式参考:
- `expected_terminal_value = Σ probability_i × terminal_value_i`
- `expected_return = expected_terminal_value / current_price − 1`
- `expected_annualized_return`:按时间加权或按情景加权两种口径任选其一,需注明。

概率纪律(很重要,容易踩雷):

- 概率必须加总到 100%。
- 概率和不等于 1 时,先修正情景权重,再计算任何概率加权数值;不要在未归一化的输入上得出加权结论。
- 仅在显式标注"未归一化、仅供诊断"的内部草稿里允许出现概率不为 1 的中间表。
- 在情景树尚未对齐或未明确标注"未归一化"的情况下,**禁止**把概率加权结论写进面向读者的产物。

---

## Downside / break price methods

For high-stakes trades, use at least two methods:

1. Unaffected price.
2. Peer-adjusted unaffected price.
3. Market-adjusted unaffected price.
4. Fundamental standalone value.
5. Historical trading range.
6. Bear-case valuation.
7. Debt recovery or liquidation value supplied by 独立信用分析流程 when capital structure, covenants, priority, or recovery waterfalls drive the terminal case.
8. Litigation-loss or damages-adjusted value.

Preferred merger break-price formula:

`peer_adjusted_break = unaffected_price * (1 + peer_return_since_unaffected_date) + idiosyncratic_adjustment`

Do not accept the unaffected price blindly when there has been deal leakage, sector movement, earnings, guidance, macro shock, or unrelated company-specific news.

---

## Spin-off SOTP

Inputs:
- SpinCo revenue, EBITDA, EBIT, FCF, net debt.
- RemainCo revenue, EBITDA, EBIT, FCF, net debt.
- Peer multiples.
- Dis-synergies, stranded costs, separation costs.
- Tax leakage, pension, litigation, environmental liabilities.
- Share count and distribution ratio.

Formulas:

`enterprise_value = metric * selected_multiple`

`equity_value = enterprise_value - net_debt - other_claims`

`per_share_value = equity_value / pro_forma_share_count`

Senior checks:
- Which shareholder base will own SpinCo after distribution?
- Is forced selling likely?
- Is the best entry pre-spin, when-issued, or post-distribution?
- Is the balance sheet fair, or value-shifting?

---

## Distressed event bridge

When a dated distressed catalyst depends on capital structure or recovery, do not build the credit stack here. Hand off to or rely on 独立信用分析流程 for:
- Enterprise value range, cash, debt, secured / unsecured status, guarantees, collateral, DIP / new-money claims, rights offering economics, covenants, maturity wall, priority, recovery waterfall.
- Fulcrum security, value-break location, priming risk, structural subordination, intercreditor terms, class-vote dynamics, court / process recovery risks.

This skill then owns the event bridge:
1. Identify the dated catalyst or process step.
2. Translate sourced credit / recovery outputs into terminal payoffs.
3. Assign scenario probabilities and timing.
4. Compute expected return, annualized return where useful, and monitoring thresholds.

---

## Position sizing bridge

A short event-driven sizing conversation should cover:
- Expected return.
- Downside gap.
- Adverse-scenario probability.
- Liquidity and exit capacity.
- Correlation to the existing book.
- Mark-to-market path volatility.
- Catalyst date certainty.
- Borrow / financing constraints.

Sample phrasing:
"The expected value is attractive, but the break downside and regulatory path argue for a starter position until the next gating item clears."

---

## Flow event math

For technical / passive-flow events, add `flow_event` fields: estimated shares to buy / sell, ADV, days-to-trade, flow-vs-ADV, impact bands, assumed participation rate, borrow / financing cost, expected reversal, liquidity exit plan. 算术口径仅供参考 — PM probability and market-impact judgment remain manual.
