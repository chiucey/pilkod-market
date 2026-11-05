# Extraction and QA Rules

## Knowledge Card Definition

A knowledge card is a reusable medical content asset. It must be concise, source-traceable, and limited to one core conclusion.

Good card:
- “IL-23/Th17 axis activation is associated with psoriatic inflammation in lesional skin samples.”

Bad card:
- “This review introduces psoriasis, mechanisms, treatments, and future trends.”

## Split Rules

Split into separate cards when a paragraph contains multiple independent facts, such as:

- disease burden and treatment gap.
- efficacy and safety.
- adult population and pediatric population.
- mechanism and clinical outcome.
- product A and product B.
- guideline recommendation and reimbursement policy.

## Article-Type Specific Rules

### Basic Research

Extract mechanism cards around:
- immune cell type.
- cytokine/pathway/target.
- model system.
- experimental manipulation.
- directional result.
- interpretation boundary.

Never imply human efficacy from preclinical findings.

### Clinical Research

Extract cards around:
- PICO.
- endpoint result.
- effect size and CI/P value.
- safety result.
- subgroup finding.
- clinical interpretation.

Never imply superiority unless the study was designed and statistically powered for comparison.

### Meta-analysis/Systematic Review

Extract cards around:
- included study design and sample size.
- pooled effect size.
- heterogeneity.
- bias/quality assessment.
- evidence grade.

If primary study details are required for a reusable claim, flag `Needs_Source_Tracing = Yes`.

### Review

Extract framework cards and cite the review location. If the card includes clinical data, product comparison, key efficacy/safety data, or immunology mechanism data, flag source tracing unless the primary source is available.

### Guideline/Policy

Extract cards around recommendation, applicable population, evidence grade, clinical pathway, policy change, or use-management requirement.

### Product/Competitor Content

Any product or competitor content must be neutral, evidence-based, and compliance flagged. Avoid promotional tone in `Source_Fact_CN`. Put possible messaging ideas only in `Interpretation_CN` or `Suggested_Output_Form`, and mark as requiring review.

## Review Flag Logic

- Needs_Source_Tracing = Yes: review-derived data, unclear source, secondary citation, missing page/figure, or any card likely to be externally reused.
- Needs_Medical_Review = Yes: any medical claim, treatment implication, mechanism interpretation, or clinical conclusion.
- Needs_Compliance_Review = Yes: product, competitor, promotional strategy, comparative claim, patient management, prescribing habit, market need, or policy-sensitive content.
- Needs_Patient_Rewrite = Yes: patient education use or technical language intended for patients.

## Suggested Output Forms

Allowed values:
- 机制图
- 临床解读
- PICO表
- 证据链表
- 森林图解读
- 指南更新卡
- 患者教育卡
- 医生PPT要点
- 医学DA话术素材
- 竞品对比表
- 法规政策摘要
- 内部培训材料
