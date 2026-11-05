---
name: hpv-literature-tagger
description: Standardized tagging of HPV-related literature PDFs and batches using an eight-subdirectory label system. Use when the user asks to label, pre-label, validate, correct, or batch process HPV or male HPV-related PDF literature, compare machine labels against corrected labels, produce Excel tagging output, or enforce the project-specific V2 SOP, taxonomy, and QA correction checklist.
---

# HPV Literature Tagger

Use this skill to tag HPV-related literature PDFs into the user's fixed 8-subdirectory label system, produce reviewable Excel outputs, and validate labels against the V2 taxonomy and correction checklist.

## Required references

Before tagging or validating, consult these files:

- `references/taxonomy-v2.md` — complete allowed tags, field formats, and missing-value rules.
- `references/sop-v2.md` — step-by-step tagging workflow and evidence-writing requirements.
- `references/qa-checklist-v2.md` — mandatory post-tagging correction checklist.
- `references/output-schema.md` — required Excel columns and output conventions.

For batch outputs or label validation, run `scripts/validate_labels.py` on the generated `.xlsx` file whenever feasible.

## Core rules

1. Output all 8 fields for every PDF: `age`, `population`, `ethnicity/region`, `type/exposure`, `condition/relate disease`, `outcome`, `sample'size`, `time`.
2. Use only the tags in `taxonomy-v2.md`; do not invent or approximate labels.
3. Use English commas for multi-select values.
4. `type` must never be `na`; infer the study type from title, abstract, methods, and article format.
5. `type/exposure` must end with exposure number `1`-`7`, not text such as `na`, `HIV`, `g4`, or `g9`.
6. Use `na,na` for missing `age` and missing `time`.
7. For `sample'size`, write only male sample size; calculate male count if total and female count are given.
8. Apply the QA checklist before finalizing. Flag uncertain fields for review rather than forcing unsupported specificity.

## PDF tagging workflow

1. Extract PDF text and, where needed, visually inspect tables/pages. Do not use OCR unless no other option exists.
2. Identify the article type first; this sets `type` and affects downstream rules for population scene, region center type, sample size, and time.
3. Fill `age`, `population`, and `ethnicity/region` using participants rules.
4. Fill `type/exposure`, then `condition/relate disease`, then `outcome`.
5. Fill `sample'size` and `time`.
6. Write `Evidence` as one complete sentence: `一项[研究类型]，纳入[研究对象/样本量/地区/时间]，通过分析[数据来源/检测方法/模型/问卷/结局指标]，旨在[研究目的]。`
7. Add `Need review` for low-confidence or ambiguous fields.
8. Run the label validator if an Excel output is created.

## Excel output requirements

Create an `.xlsx` file with at least:

- `标签结果`: one row per PDF or article.
- `说明与复核`: notes on rules, known uncertainties, and review priorities.
- `8子目录规则简表`: compact tag dictionary for reviewers.

Preferred columns are defined in `references/output-schema.md`. Freeze the header row, enable filters/tables, wrap text, and keep evidence/review columns readable.

## Validation

When an `.xlsx` file is available, run:

```bash
python scripts/validate_labels.py <input.xlsx> --sheet 标签结果 --out validation_report.txt
```

Review the report and fix any critical errors before sharing the output. Critical errors include missing 8 fields, `type` as `na`, `type/exposure` ending with a non-1-7 exposure value, missing `age` or `time` written as `na` instead of `na,na`, or labels outside the fixed taxonomy.
