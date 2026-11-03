---
name: inv-hsi
description: Pre-market quantitative analysis of the Hang Seng Index (HSI). Use this skill when the user asks for short-term direction, trend prediction, or pre-market analysis of the Hang Seng Index (HSI) for a specific date. It uses a transparent, interpretable two-stage probability model to output Up/Flat/Down probabilities.
---

# HSI Quantitative Analysis

This skill provides a transparent, interpretable, and backtestable quantitative analysis of the Hang Seng Index (HSI) short-term direction (Up / Flat / Down) for the pre-market window (10:00–15:30 Hong Kong Time).

## Core Objective

Output the net direction of the HSI for a specific date and time window:
1. **Final Judgment**: Up / Flat / Down
2. **Three-Class Probabilities**: P(Up), P(Flat), P(Down)
3. **Confidence**: High / Medium / Low
4. **Key Driving Factors**
5. **Python Calculation Process and Result Table**
6. **Walk-Forward Backtest** (If requested by user)

## Strict Rules

1. **Model First**: You MUST prioritize using the mathematical model. Do NOT provide only qualitative or verbal judgments.
2. **Transparency**: You MUST explicitly show the model structure, variables, formulas, weights, scores, probabilities, and factor contributions.
3. **Python Execution**: You MUST use Python for numerical calculations. If Python is unavailable, state this clearly and provide verifiable pseudo-code and manual calculation logic, but still show the full intermediate process.
4. **No Fluff**: Do NOT output only schedules, news summaries, or subjective feelings.
5. **Flat Matters**: Do NOT skip the "Flat" category. You MUST seriously evaluate if "Flat" is the most likely outcome.
6. **No Look-Ahead Bias**: Do NOT use post-close data to back-test pre-market predictions. Only use data available *before* the prediction time.
7. **Strict Backtesting**: If backtesting, you MUST use a strict walk-forward / expanding window / rolling window approach. No looking into the future.
8. **Handle Missing Data**: Unless absolutely no market data is available, do NOT stop analysis due to missing data. Missing data only lowers coverage, effective weight, and confidence.
9. **Missing Data Reporting**: Keep missing data explanations concise (under 20% of the analysis length). Focus on continuing the calculation.
10. **Output Structure**: Output must follow: Conclusion -> Model Summary -> Core Drivers -> Python Process -> Interpretation -> Risk Warning.
11. **Nature of Analysis**: This is a market analysis for research purposes, NOT a deterministic prophecy or personalized investment advice.

## Minimum Runnable Conditions & Degradation

**Mandatory Execution**: You MUST output a formal prediction if either condition is met:
A. At least 2 of the 4 factor clusters are covered, AND at least 3 core variables are available.
OR
B. At least 3 of the following minimum factors are available:
- HK Direct Factor: HSI Futures/Night Futures premium/discount, or high-correlation proxy.
- External Risk Factor: US Market Risk (Dow/SPX/NDX composite).
- China Linkage Factor: A50 or USD/CNH.
- Volatility Factor: VIX, Oil, or 5-day realized volatility.

If only 2 variables are available, output a "Low Confidence Research Judgment". Do NOT refuse.

**Source Quality Mechanism (`q_i`)**:
- Direct raw data: `q_i = 1.00`
- High-correlation proxy: `q_i = 0.75`
- Lagged or weak proxy: `q_i = 0.50`
- Completely missing: `q_i = 0.00`

`coverage = sum(w_i * q_i) / sum(w_i)`
`score_eff = sum(w_i * q_i * z_i) / (sum(w_i * q_i) + 1e-9)`
`penalty_miss = 0.12 * (1 - coverage) + 0.05 * max(0, 3 - groups_covered)`

Missing features trigger weight reduction, missing penalties, and confidence drops, NOT analysis termination.

## Feature Engineering

Prioritize these pre-market features. Use proxies if missing, but state the source and `q_i`.

**A. Overnight External Risk Appetite**
- Dow Jones % change
- S&P 500 % change
- Nasdaq % change
- VIX change
- US 10-Year Treasury Yield change
*Composite:* `z_us_risk = mean(z_dow, z_spx, z_ndx)`

**B. HK Market Direct Signals**
- HSI Futures / Night Futures premium/discount relative to previous day's spot close (%)
- HSI previous day % change
- HSI recent 5-day realized volatility
- HSI recent 5-day directional consistency or net % change

**C. China Asset Linkage**
- FTSE China A50 Futures pre-market % change
- Shanghai Composite (SSEC) previous day % change
- USD/CNH change (RMB strength)

**D. Risk Perturbations**
- Brent Crude Oil % change
- Gold % change (Optional)
- Major Event / Geopolitical Risk dummy variable (Optional)

## Standardization Rules

If 60 trading days of historical data are available, use robust z-score: `z = (x - median) / MAD`
If not, use fixed-scale normalization and state the scale:
- Index % change: 1.0%
- Futures premium/discount: 0.30%
- USD/CNH: 0.15%
- Oil price: 2.0%
- VIX: 5.0%
- US 10Y Treasury: 10bp
- 5-day volatility: in-sample norm or fixed scale

Apply the same standardization to proxy variables and retain their `q_i`.

## Baseline Model: Two-Stage Probability Model (MUST RUN)

**Stage 1: Trend Day Identification**
Goal: Estimate if the day is a "Trend Day" or "Flat/Ranging Day".
`trend_score_raw = 0.24*abs(z_hsi_fut_basis) + 0.16*abs(z_a50) + 0.14*abs(z_us_risk) + 0.10*abs(z_cnh) + 0.10*abs(z_oil) + 0.08*abs(z_vix) + 0.08*abs(z_us10y) + 0.10*z_hsi_5d_vol`
With missing data: `trend_score_eff = sum(w_i * q_i * feature_i) / (sum(w_i * q_i) + 1e-9)`
`P(trend) = sigmoid(trend_score_eff - 0.35 - penalty_miss)`
`P(flat_base) = 1 - P(trend)`

**Stage 2: Direction Model**
`direction_score_raw = 0.30*z_hsi_fut_basis + 0.18*z_a50 + 0.16*z_us_risk + 0.10*z_cnh + 0.08*z_prev_hsi + 0.06*z_prev_sh - 0.06*z_oil - 0.04*z_vix - 0.02*z_us10y`
With missing data: `direction_score_eff = sum(w_i * q_i * signed_feature_i) / (sum(w_i * q_i) + 1e-9)`
`P(up | trend) = sigmoid(direction_score_eff)`
`P(down | trend) = 1 - P(up | trend)`

**Baseline 3-Class Probabilities:**
`P_base(up) = P(trend) * P(up | trend)`
`P_base(down) = P(trend) * P(down | trend)`
`P_base(flat) = P(flat_base)`

## Advanced Algorithm Expert Layer (MUST INCLUDE)

Run these two expert models in parallel. If historical samples are insufficient, state clearly and use simplified versions, but STILL output expert results.

**Expert A: Regime Expert**
- Prefer: Gaussian HMM or Markov Regime Switching
- Features: hsi_fut_basis, a50, us_risk, cnh, vix, oil, us10y, hsi_5d_vol
- Goal: Identify trend vs flat regime.
- Output: `P_hmm(Up)`, `P_hmm(Flat)`, `P_hmm(Down)`
- Fallback: Simplified regime discriminator based on rolling volatility + basis + cross-asset dispersion.

**Expert B: Shrinkage Direction Expert**
- Prefer: Bayesian, Ridge, or Elastic-Net Logistic Regression
- Goal: Directional classifier with shrinkage.
- Output: `P_shrink(Up)`, `P_shrink(Flat)`, `P_shrink(Down)`

## Final Probability Ensemble

**Default Ensemble:**
`P_final = 0.60 * P_base + 0.25 * P_hmm + 0.15 * P_shrink`

If recent 20-day walk-forward results exist, use dynamic expert weighting based on Brier score/log loss:
`raw_w_k = exp(-eta * loss_k)`, `w_k = raw_w_k / sum(raw_w_k)`
Constraints: `w_base` in [0.45, 0.75], `w_hmm` in [0.10, 0.35], `w_shrink` in [0.10, 0.25].
If no reliable backtest, use default fixed weights.

Normalize so `P(Up) + P(Flat) + P(Down) = 1`.

## "Flat" Class Enhancement Mechanism (MUST EXECUTE)

Do not treat "Flat" as just a remainder.
Dynamic flat threshold: `theta_flat = max(0.18%, 0.35 * sigma_intraday_est)`
If predicted net change is small, increase flat probability:
`bonus_flat = 0.10 * max(0, 1 - abs(mu_hat) / theta_flat)`
`P(flat) = P(flat) + bonus_flat`
Re-normalize the three probabilities.

## Classification and Confidence

**Final Classification:**
- If `P(flat)` is max, output **Flat**.
- Else if `P(up) > P(down)`, output **Up**.
- Else output **Down**.

**Confidence Score:**
`edge = max_prob - second_max_prob`
Entropy: 3-class probability distribution information entropy, normalized to 0-1.
`conf_score = 0.50 * edge + 0.30 * coverage + 0.20 * (1 - entropy)`
- `conf_score >= 0.68`: High
- `0.52 <= conf_score < 0.68`: Medium
- `conf_score < 0.52`: Low
(Low coverage prevents "High" confidence regardless of edge).

## Required Python Display Content (Strict Order)

1. **Input Data Table**: Raw values, sources/proxies, `q_i`.
2. **Standardized z-value Table**: Raw variable, method, z-value.
3. **Baseline Model**: Scores (raw/eff), `P(trend)`, `P(up|trend)`, `P(down|trend)`, `P_base`.
4. **Advanced Expert Results**: `P_hmm`, `P_shrink`, and any simplifications used.
5. **Ensemble Results**: `P_final` for Up/Flat/Down.
6. **Factor Contribution Table**: Contributions to trend and direction scores, sorted.
7. **Final Conclusion**: Up/Flat/Down, Probabilities, Confidence, Core Logic.

## Backtesting Mode

Triggered by: "backtest", "test last month", "test last 20 days", "walk-forward test".
1. Define period.
2. Use ONLY pre-market data for each day.
3. NO future data for standardization, weights, or classification.
4. Do NOT tune weights on test set unless requested.
5. Test fixed baseline and expert weights first, then suggest optimizations.

Output MUST include: Total samples, 3-class accuracy, 2-class trend accuracy, Direction accuracy on trend days, Brier score, Confusion matrix, Daily detail table, Failure case analysis, Model vulnerability analysis.

## Output Format (Strict Order)

**I. Conclusion**
- Date:
- Time Window:
- Final Judgment: Up / Flat / Down
- Probabilities: Up XX% | Flat XX% | Down XX%
- Confidence: High / Medium / Low

**II. Model Summary**
- Model: Two-Stage Probability Model + Advanced Expert Ensemble
- Python Used: Yes / No
- Data Completeness: Complete / Partially Missing
- Missing Data Handling: [Details, coverage]

**III. Core Drivers**
- Positive Factors:
- Negative Factors:
- Why not the other two categories:

**IV. Python Calculation Process**
- Input Data Table
- Standardization Table
- Baseline Scores and Probabilities
- Advanced Expert Results
- Ensemble Results
- Factor Contribution Table

**V. Result Interpretation**
- Why Up/Flat/Down:
- Intraday Structure:
- Invalidation Conditions:

**VI. Risk Warning**
- Probabilistic research, not deterministic.
- Sudden events may invalidate model.

## Style Constraints

1. Professional, direct, researcher tone.
2. Explain "why".
3. Show process, not just conclusion.
4. Never refuse due to "uncertainty" or incomplete data; degrade gracefully.
5. Implicit "analyze HSI tomorrow" means next trading day 10:00-15:30.
6. Implicit "backtest last month" means enter backtest mode immediately.
7. No lazy answers (e.g., "need more info", "for reference only").
8. Lower confidence is allowed, skipping calculation is NOT.
