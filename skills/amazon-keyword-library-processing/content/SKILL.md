---
name: amazon-keyword-library-processing
description: Amazon keyword library SOP for converting keyword research spreadsheets into listing optimization and advertising execution decisions. Use when Codex needs to process an Amazon keyword library, extract level-1 English keyword roots, classify intent/attribute/brand risk, score keyword opportunities from Sif metrics, assign priority, split terms into main push words, test words, negative keywords, and backend Search Terms, or design SEO and SP/SB/SBV ad actions from keyword research data.
---

# Amazon Keyword Library Processing

## Overview

Use this workflow to turn an Amazon keyword library into execution-ready decisions for listing copy and ads. The required final outputs are:

- Main push keywords: terms suitable for title, bullets, Search Terms, SP exact, and possibly brand ads.
- Test keywords: relevant expansion terms for SP phrase/broad testing and long-tail discovery.
- Negative keywords: irrelevant, mismatched, brand-risk, or intent-drift terms to block early.
- Backend terms: relevant terms that are unsuitable for front-end copy or main ad targeting but useful for Search Terms indexing.

When working from a spreadsheet, prioritize the sheet containing high/medium/low relevance terms. Ignore unrelated-term sheets unless the user explicitly asks to mine them.

## Required Inputs

Gather these before scoring:

- Product title and key selling points/bullets. Use these as the evidence source for product type, material, size/specs, pack count, compatibility, use case, target buyer, and any attributes that must match.
- Keyword table columns: keyword, relevance score, weekly search volume, ABA rank, conversion rate, suggested bid low/mid/high, Top3 click share, Top3 conversion share, and placement/share metrics if available.
- Operational goal: precision conversion, traffic expansion, new-product launch, SEO optimization, ad testing, or mature-product defense.

If the user has not provided a product title and selling points/bullets, ask for them before final attribute matching. Do not treat missing product evidence as final `unclear`; mark it as `needs product evidence` only in a temporary draft.

## Workflow

1. Preserve the raw keyword table.
   - Work on a copy or add analysis columns to the existing high/medium/low relevance sheet.
   - Keep original metrics unchanged for auditability.

2. Add decision columns.
   - Required columns: level-1 English root, product intent, attribute match, brand risk, opportunity score, priority, risk note, final action, and placement/ad suggestion.
   - Add helper score columns when a spreadsheet formula workflow is useful.

3. Extract the level-1 English root.
   - Output a concrete English root token or phrase from the keyword itself, not a translated demand category.
   - Good examples: `pop up canopy`, `popup canopy`, `canopy tent`, `10x10 canopy`, `waterproof`, `heavy duty`, `coleman`, `eurmax`, `canopy weights`, `outdoor canopy`.
   - Bad examples: `core keyword`, `adjacent term`, `brand/product-line`, `main demand`, `accessory category`.
   - Prefer the most decision-relevant root in this order: explicit brand/product line, hard attribute such as size/material, exact product form, adjacent product form, broad scenario.
   - Use this column to group terms for review, but do not let it replace product intent or brand-risk judgment.

4. Classify product intent.
   - Use exactly these labels unless the user provides a different taxonomy: `precise`, `near-precise`, `testable`, `off-intent`.
   - Ask: if a buyer searched this term and clicked the product, would they feel they found the right product?
   - Treat product-form mismatch as more important than surface relevance.

5. Classify attribute match.
   - Compare keyword attributes against the product title and selling points/bullets.
   - Use `match`, `no keyword attribute`, `needs product evidence`, or `mismatch`.
   - Mark size, material, quantity, model, compatibility, and usage constraints that conflict with the provided title/selling points as mismatch.
   - Use `no keyword attribute` when the keyword does not specify a comparable attribute.
   - Use `needs product evidence` only when the keyword contains an attribute but the title/selling points do not provide enough evidence to compare it; ask the user for missing specs before finalizing.
   - A relevant keyword with a hard attribute mismatch must not become a main push keyword.

6. Mark brand risk.
   - Use `yes` when the keyword contains a competitor brand, branded product line, or proprietary term.
   - Brand terms can be tested later, but do not recommend them as new-product launch main push terms.

7. Score opportunity and assign priority.
   - Use the scoring model in [scoring-and-actions.md](references/scoring-and-actions.md).
   - Make clear which original metric column each helper score uses: relevance score, weekly search volume, attributed conversion rate, suggested mid bid, and Top3 click/conversion concentration.
   - Calibrate thresholds by category before relying on numeric outputs; search volume, conversion, CPC, and concentration ranges vary by market.

8. Assign final action.
   - Apply hard exclusion rules before numeric priority:
     - brand risk = yes
     - attribute match = mismatch
     - attribute match = needs product evidence
     - product intent = off-intent
   - Then split the remaining words into main push, test, backend, or negative.
   - When in doubt, prefer `test` or `backend` over `main push`.

9. Produce execution outputs.
   - Listing plan: title terms, bullet terms, backend Search Terms, and terms to avoid in front-end copy.
   - Advertising plan: SP exact main terms, SP phrase/broad test terms, negatives, and any SB/SBV candidates.
   - Risk log: brand-risk, attribute-mismatch, off-intent, and high-concentration terms with reasons.

## Decision Rules

Use hard rules to protect execution quality:

- Never let high search volume override off-intent, brand risk, or attribute mismatch.
- Main push terms must have precise or near-precise intent and no hard mismatch.
- Test terms can include broader scenario terms, but they need controlled budgets and clear negatives.
- Backend terms should be relevant and indexable, but not awkward or misleading in front-end copy.
- Negative terms should include hard mismatches, clear off-intent terms, competitor brand terms during launch, and terms likely to waste ad spend.

## Output Format

For spreadsheet work, return or create a workbook with:

- Processed keyword sheet with all original columns plus decision columns.
- Summary sheet with counts by final action, priority, intent, level-1 English root, brand risk, and attribute match.
- Listing optimization sheet with title/bullets/Search Terms recommendations.
- Advertising sheet with SP exact, SP phrase/broad, negatives, and optional SB/SBV candidates.

For text-only work, present:

1. Executive summary: what the keyword pool says about the product opportunity.
2. Four keyword pools: main push, test, negative, backend.
3. Listing plan: where each main keyword should go.
4. Ad plan: match type, budget posture, and negative list.
5. Risk notes: why high-volume terms were excluded.

## References

- Read [scoring-and-actions.md](references/scoring-and-actions.md) when formulas, thresholds, or action mapping are needed.
