# QA Checklist V2

Run this checklist after every tagging pass.

## Critical field checks

1. All 8 required fields are present.
2. `type/exposure` has at least one valid `type` and ends with a number `1`-`7`.
3. `type` is not `na`.
4. `age` missing values are written as `na,na`, not `na`.
5. `time` missing values are written as `na,na`, not `na`.
6. `population` follows `abbr1[,abbr1...],abbr2` and setting is `cl`, `co`, or `na`.
7. `ethnicity/region` follows `abbr3,abbr4` where region is `c/y/n/na` and center is `m/s/na`.
8. `sample'size` is male count only or `na`.

## Correction checks from the calibrated labels

1. Do not convert `<=12 years` into `0,12`; use `,12`.
2. For mixed male/female studies, include `g,female`.
3. Do not use `msw` for generic male/female mixed studies.
4. Meta/review/model population setting is usually `na`.
5. Meta/review/model region center type is usually `na`.
6. Exposure is numeric only; do not write `na`, `HIV`, `g4`, or `g9` in exposure.
7. HIV belongs to population, not exposure.
8. Add `3` to condition when HPV infection/genotype/HPV-caused disease is central.
9. Add parent disease when a child disease code is used: `2,2.5`, `5,5.1`.
10. Do not tag condition diseases that appear only in background.
11. Do not miss `pre` or `in` when prevalence/incidence is central.
12. Map risk ratio, rate ratio, and relative risk to `rr`.
13. Use `efficacy` for clinical trial efficacy and `effectiveness` for real-world effectiveness.
14. If total and female count are available, calculate male count.
15. Missing time is `na,na`; cross-year ranges use year subtraction.

## Review flag guidance

Set `Need review = Yes` when:

- Any PDF is scanned or text extraction is incomplete.
- Age only appears in tables and is uncertain.
- Male sample size requires table-level verification.
- The article is meta/review/model and exposure/condition/outcome mapping is broad.
- Region or center type is inferred rather than explicit.
- Multiple possible study types apply and one is chosen by inference.

Set `Need review = No` only when all labels are directly supported.
