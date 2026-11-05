# SOP V2: HPV Literature Tagging Workflow

Use this SOP after reading `taxonomy-v2.md`.

## 1. Read and extract the PDF

Extract the title, abstract, methods, results, tables, figures, and conclusions. For scanned or low-quality PDFs, visually inspect relevant pages. Avoid OCR unless no usable text exists.

## 2. Determine type first

Identify `type` before other labels because it affects setting, center type, sample size, and time interpretation.

Evidence hierarchy:

1. Article title and subtitle
2. Abstract design words
3. Methods study design
4. Data source and enrollment method
5. Journal article type or section type

`type` must not be `na`. If unclear, infer from design:

- Surveys -> `cross`
- Follow-up or longitudinal observational analysis -> `cho`, add `prospective` if explicitly prospective
- Retrospective chart/database review -> `resp`; add `cho` if cohort-like
- Systematic review with meta-analysis -> `meta`
- Review without meta-analysis -> `rev`
- Cost-effectiveness or transmission model -> `model`
- Guideline or expert consensus -> `guide` or `consensus`
- Case report or case series -> `caser`
- Randomized trial -> `rct`; nonrandomized clinical trial -> `nrct`

## 3. Fill `type/exposure`

Format: `type[,type...],number8`.

Exposure must be a number `1`-`7`:

- `1` g4
- `2` g9
- `3` g4 & g9
- `4` other & g4
- `5` other & g9
- `6` not distinguished / all vaccine types / vaccine data not separable
- `7` no vaccine exposure or not applicable

Never put `na`, `HIV`, `g4`, or `g9` directly in the exposure part.

## 4. Fill `age`

Use exact enrollment ages, not outcome age bands unless those define the sample.

- `>=18` -> `18,`
- `<=12` -> `,12`
- `18-25` -> `18,25`
- median age only -> single number, such as `18`
- months -> years, such as `6 months` -> `0.5`
- no clear age -> `na,na`

Do not add an unreported minimum age. `12 years and younger` is `,12`, not `0,12`.

## 5. Fill `population`

Format: `population tags,setting`.

Rules:

- Mixed male/female original studies: include `g,female`.
- Ordinary male population: `g`.
- MSM: `msm`.
- Do not use `msw` for generic mixed-sex studies; use only for men who have sex with women or heterosexual male sexual-behavior populations.
- Health examination/screening/community survey: `co`.
- Hospital/clinic/clinical cohort: `cl`.
- Meta/review/model: setting usually `na`.
- Do not repeat specific condition diseases in population. If condition is penile cancer (`4`), population is usually `g,na`, not `g,Malignancy,na`.

## 6. Fill `ethnicity/region`

Format: `region,center`.

- Region: `c`, `y`, `n`, or `na`.
- Center: `m`, `s`, or `na`.

Rules:

- Original single-center study -> `s`.
- Original multicenter or surveillance with multiple sites -> `m`.
- Meta/review/model -> center usually `na`.
- Review/model with substantial China domestic data may be `c,na`.

## 7. Fill `condition/relate disease`

Use core study object and key results, not background-only disease mentions.

Rules:

- Add `3` for HPV infection, HPV genotyping, or HPV-caused disease when central.
- If tagging a subtype, include parent: `2,2.5`; `5,5.1`.
- Vaccination or vaccination intention -> `8`.
- Strategy, implementation, modeling of vaccination/screening strategies -> `8.1`.

## 8. Fill `outcome`

Do not under-tag outcomes. Include all central outcomes from abstract/results/tables.

Common mappings:

- prevalence/proportion -> `pre`
- incidence/cumulative incidence -> `in`
- OR -> `or`
- risk ratio/rate ratio/relative risk -> `rr`
- HPV genotype distribution -> `gen`
- recurrence -> `rein`
- clearance -> `clear`
- immune response, immunotherapy, immune microenvironment -> `imm`
- RCT clinical efficacy -> `efficacy`
- real-world effectiveness -> `effectiveness`
- uptake/coverage/vaccination rate -> `vcr`
- knowledge/attitude/practice/willingness/acceptability -> `kap`
- concern/hesitancy/barrier -> `concern`
- cost/economic burden/cost-effectiveness -> `cost`

Only tag outcomes that are central to the study, not background.

## 9. Fill `sample'size`

Fill only male count.

Priority:

1. Direct male count.
2. Total count minus female count.
3. Total count if all subjects are male.
4. `na` if male count cannot be separated.
5. Meta/review/model -> `na` unless explicit male count is reported.

## 10. Fill `time`

Format: `start year,period`.

- No time -> `na,na`.
- Single-year cross-sectional data -> `YYYY,0`.
- Same-year date ranges -> months/days.
- Cross-year ranges -> year subtraction.
- Multiple periods -> earliest start year and summed period.

## 11. Write Evidence

Evidence must be one complete sentence, not fragments.

Template:

`一项[研究类型]，纳入[研究对象/样本量/地区/时间]，通过分析[数据来源/检测方法/模型/问卷/结局指标]，旨在[研究目的]。`

Example:

`一项横断面研究，纳入2012—2013年西班牙Valencia地区18–25岁大学生543名，通过分析口腔样本HPV检测结果及6个月随访数据，旨在评估大学生口腔HPV感染患病率、持续感染、清除率及基因型分布。`

## 12. Mark Need review

Use `Yes` when any field is inferred, text extraction is incomplete, male sample size requires table verification, region/center type is ambiguous, or review/meta/model has uncertain exposure or population interpretation.

Use `No` only when all 8 fields are well supported by the PDF.
