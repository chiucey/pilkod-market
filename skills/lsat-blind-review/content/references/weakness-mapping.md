# Weakness mapping — Part III 错因标签与底层能力桶

This reference is the single source of truth for the **错因标签** column in
Part II 答案速览表 and the **底层能力** row of Part III. It is also the schema
that `build_cross_workbook_report_v1.py` (read-only reference script under
`/Users/log/.cache/lsat_workbook/`) consumes when aggregating across workbooks.

Read this before writing any Part III prose. The mapping has to be
**structural**, not surface-level — tagging a question by which letter the user
chose, or by the first keyword that pops out of the stimulus, is the most
common reason the 7-day training plan turns out to be useless.

## 1. The four 底层能力 buckets

Every wrong question is tagged with exactly one of these four buckets. The
buckets are **capability deficits**, not question types — a single 题型 can
fall under any of them depending on which step of the reasoning chain broke.

| Bucket | English gloss | What breaks in the BR pipeline |
|---|---|---|
| **条件逻辑** | Conditional logic / bridge integrity | NA↔SA 方向说反；contrapositive 不熟练；隐含桥接被反向误读；跨物种/跨领域外推；「原因桥接」与「必要性桥接」混用 |
| **范围控制** | Scope / quantifier handling | `virtually / almost / typically / as many … as any one` 被升级成 `all / every`；选项范围比 stimulus 范围更窄或更宽；`some + all` 最小范围组合错读 |
| **方法识别** | Method / argument-form recognition | 没有正向归纳 argument 的 inferential move；`dismiss` vs `discredit` / `prove` vs `demonstrate` / `ignore` vs `fail to foresee` 混淆；Parallel 题 form 分类错；EXCEPT 题 4-选-3 归类错 |
| **原则匹配** | Principle / property matching | Principle (Justify) 只匹配了双分支中的 1 支；Principle (Apply) 只在意图维度匹配、忽略实际/可预见伤害维度；Principle Match 把「话题相关的同义改写」误当原则 |

These four names are **canonical**. Do not invent synonyms (`逻辑缺陷`,
`语义精度`, `形式识别`) in the workbook — downstream cross-workbook scripts
key off the exact strings.

## 2. The 错因标签 vocabulary (for Part II 答案速览表)

The 错因标签 column in the speed-table is the same string as the bucket name
**most of the time**, but there are cases where a finer-grained label is
useful. Use the table below; do not invent extra labels.

| 错因标签 | When to use | Maps to bucket |
|---|---|---|
| **条件逻辑** | NA/SA/MSS 的桥接方向说反；contrapositive 错；两变量定义只给一个变量 | 条件逻辑 |
| **范围控制** | 量词被升级（some→all, virtually→every）；选项范围比 stimulus 大/小 | 范围控制 |
| **方法识别** | 没有先列 argument 实际做的 inferential move 就直接匹配；Parallel form 错；EXCEPT 4-选-3 错 | 方法识别 |
| **原则匹配** | Principle 只匹配了双分支的一支；Principle Apply 在错误 property 维度匹配 | 原则匹配 |
| **题型误判** | (rare, escape hatch) — user clearly did not recognize the 题型 and the question-type error cascades into a tag the bucket can't fix | — |

Use **题型误判** only as an escape hatch when none of the four buckets fits.
Never use it as a default for "I can't tell" — if you genuinely can't tell,
re-do the BR before tagging.

The Day-2+3 v3 workbook used `条件逻辑 / 范围控制 / 方法识别 / 原则匹配`
exclusively (34 wrong questions, 0 escape hatches) and that is the bar.

## 3. Tagging rules — how to choose among overlapping candidates

Most wrong questions look like they fit more than one bucket at first glance.
Use this decision order:

1. **Was the user able to identify the 题型 correctly?** If no, that is a
   separate defect that does not fit any bucket — use `题型误判` and stop.
   Do not double-tag.
2. **Did the user identify the 题型 correctly but apply the wrong form?**
   That is **方法识别**. Example: a Parallel (Flawed) question where the
   user found two similar premises but missed that the conclusion's flaw
   is a quantifier shift, not an equivocation.
3. **Did the user identify the form correctly but misread a quantifier /
   scope word in the stimulus or in an option?** That is **范围控制**.
4. **Did the user read the scope correctly but reverse the direction of
   the implicit bridge (NA↔SA, conditional, two-variable definition)?**
   That is **条件逻辑**.
5. **Did the user do everything else correctly but matched on the wrong
   property / dimension in a Principle question?** That is **原则匹配**.

If the user's own per-question 8-section analysis identifies **more than one**
of these layers breaking, pick the **upstream** layer (the one that, if fixed,
would have prevented the downstream layer from ever running). Do not
double-tag.

## 4. Concrete example mapping (Day-2+3 v3)

These 11 representative questions from the v3 workbook (`✓verified` tag
included where applicable) illustrate how the rules above pick one bucket
even when several would seem to fit.

| Q | 题型 | 正确答案 | 你的答案 | 错因标签 | Why this bucket, not that one |
|---|---|---|---|---|---|
| 3 | Weaken | A | E | **条件逻辑** | "ban 不影响 informed citizens" actually *strengthens* the minimally-impairs premise — user inverted the bridge between premise and conclusion |
| 10 | Flaw | B | D | **方法识别** | user named "no relevant evidence" without first listing that the argument's inferential move is a counter-example to a universal claim |
| 11 | MBT | E | D | **范围控制** | "as many … as any one" is per-item `≥`, not aggregate `>`; user upgraded the quantifier |
| 12 | Flaw | B | C | **条件逻辑** | user mis-stated the bridge as "all S → all P" when the stimulus uses "some S → all P" |
| 13 | Assumption | B | A | **条件逻辑** | NA↔SA direction reversed; the negation that would break the argument was hidden in the option's quantifier |
| 14 | Resolve Discrepancy | (correct) | — | — | — (not a wrong question) |
| 15 | Parallel Flaw | C | A | **条件逻辑** | Parallel form matches at premise level but the contrapositive direction is wrong |
| 17 | Weaken Evidence | B | D | **方法识别** | user did not first identify that the argument's structure is "evidence → inference" and conflated weaken-the-inference with weaken-the-evidence |
| 18 | Principle Match | A | D | **原则匹配** | user matched on intent only; option D talks about an outcome-dimension the principle does not address |
| 20 | Weaken EXCEPT | D | A | **方法识别** | user treated EXCEPT as "weaken" and missed the 4-选-3归类 step |
| 21 | Principle Justify | C | D | **原则匹配** | user matched one branch of a two-branch principle |

Note: Q3 in this mapping is the Cambridge Q3 from Day-2+3 v3, **not** the
"airlines / How do the airlines expect to prevent" Q3 from the Day-2 set
referenced in SKILL.md's `Verification` section. The two share a number but
are different questions from different PDFs. The numbers in the speed-table
are the user's Q-numbers (Hard Rule #9), so they must match the user's input
verbatim.

## 5. Worked example — mapping a 6-question Day-1 sample

Input from user (Day 1, six wrong questions):

```
Day 1 Q10 (Assumption)  correct A, chose C
Day 1 Q32 (Method)      correct D, chose B
Day 1 Q40 (Parallel)    correct E, chose A
Day 1 Q14 (Weaken)      correct A, chose D
Day 1 Q21 (Principle)   correct C, chose B
Day 1 Q26 (Flaw)        correct B, chose E
```

Decision walk-through using §3:

- Q10 — user identified 题型 as Assumption but read the bridge direction
  backwards → **条件逻辑**
- Q32 — user identified Method but conflated `dismiss` with `discredit`
  → **方法识别**
- Q40 — user identified Parallel but classified the form wrong (treated
  it as equivocation when it was quantifier-shift) → **方法识别**
- Q14 — user identified Weaken but the failure was upgrading "typically"
  to "always" in the option scan → **范围控制**
- Q21 — user matched on intent only, missing the outcome dimension
  → **原则匹配**
- Q26 — user read the scope correctly but reversed the conditional
  → **条件逻辑**

Distribution: 条件逻辑 × 2, 范围控制 × 1, 方法识别 × 2, 原则匹配 × 1.
The 7-day plan therefore prioritizes (1) NA↔SA + conditional drills,
(2) Method-of-argument + Parallel form drills, (3) MBT/Weaken quantifier
drills, (4) Principle Apply dimension drills.

## 6. Anti-patterns (do NOT do these)

- **Tagging by user's wrong letter.** "User chose D, therefore 范围控制"
  is meaningless — D is a position, not a defect.
- **Tagging by surface keyword.** "Stimulus contains `all`, therefore 范围
  控制" misses every case where the user read `all` correctly but broke on
  a different layer.
- **Double-tagging.** Pick the upstream bucket (§3 step 5). Double tags
  inflate counts and dilute the 7-day plan.
- **Inventing new bucket names.** Downstream scripts key off the canonical
  four. If the analysis genuinely doesn't fit, use `题型误判` (escape
  hatch), not a new label.
- **Tagging before re-doing the BR.** If the user's own per-question
  8-section analysis cannot explain why their choice was wrong, the
  bucket assignment will be a guess. Re-do the BR first.
- **Bucketing by section.** "All PT109-S4 questions are 方法识别" is a
  pattern, not a tag. Tags are per-question.

## 7. How Part III uses the tag distribution

Part III's report aggregates per-bucket counts across the user's wrong
questions for this workbook and produces:

1. **错因标签频次表** — counts per bucket (the four rows above).
2. **错选字母分布表** — independent of buckets; user letter choices
   `A/B/C/D/E` × frequency. This is *not* the same data and must not be
   merged into the bucket table.
3. **4–6 条具体劣势** — each 劣势 is one bucket × the symptom × the
   specific question evidence × the training action. Format:
   `劣势 N · {bucket 内的具体表征}：{evidence from a specific wrong Q}。
   训练动作：{concrete drill}.`
4. **7 日优先级训练清单** — Y 灯 / 黄 / 绿 ranking by bucket frequency
   (highest-count bucket → Y 灯) and by question-type sub-cluster within
   the bucket.

The cross-workbook aggregation script
(`/Users/log/.cache/lsat_workbook/build_cross_workbook_report_v1.py`)
joins per-workbook buckets by the canonical four strings, so any deviation
in the per-workbook Part III breaks the cross-workbook comparison.

## 8. Worked end-to-end example — building Part III from a tag distribution

Given a Day-2+3 v3 workbook with the following tag distribution (real
numbers from the v3 build):

```
条件逻辑: 11   (Q3, Q10, Q12, Q13, Q15, Q16, Q22, Q26, Q31, Q35, Q38)
范围控制: 4    (Q14, Q17, Q18, Q30)
方法识别: 9    (Q4, Q13, Q17, Q20, Q32, Q33, Q34, Q36, Q37)
原则匹配: 10   (Q11, Q19, Q21, Q24, Q25, Q27, Q28, Q29, Q35, Q39)
```

Note: Q13 appears under both 条件逻辑 and 方法识别 in different v3
subsections — that is a documented inconsistency. The current canonical
v3 tag for Q13 is **条件逻辑** (per the upstream-layer rule in §3);
the 方法识别 assignment was an early draft and should be re-tagged if
ever re-built. This is exactly the kind of drift the cross-workbook
script will surface.

The Part III 劣势 table for this distribution would look like:

```
劣势 1 · 条件逻辑：隐含桥接方向反转（NA↔SA 说反 / 跨域外推）。
  涉及错题：Q3（bridge 说反）、Q13（NA↔SA）、Q22（跨域外推）。
  训练动作：BR 时先把 argument 的核心桥接单独写出，用 "否定此桥接能否
            瓦解结论" 反向筛选项；每天 3 题 Assumption + MSS 交叉。

劣势 2 · 方法识别：未先列 argument 的 inferential move 就匹配选项。
  涉及错题：Q17（"dismiss vs discredit" 混淆）、Q32（"强化结论" 当
  Weaken）、Q33（未识别 multi-cause 结构）。
  训练动作：BR 时强制先写 "arguer actually did X" 一句话，再扫选项；
            每天 2 题 Method (Describe) + 1 题 Parallel。

劣势 3 · 原则匹配：双分支只匹配 1 支。
  涉及错题：Q18（intent 维匹配，忽略 outcome 维）、Q21（matched
  descriptive branch, missed normative branch）、Q35（matched frequency,
  missed severity）。
  训练动作：Principle (Justify) 题 BR 时先列 principle 的全部
            property 维度，逐项核对选项是否同时覆盖；每天 2 题。

劣势 4 · 范围控制：量词升级 / 选项范围 > stimulus 范围。
  涉及错题：Q14（virtually → every）、Q17（no … more quickly → never）。
  训练动作：BR 时建立 "量词升级自查表"（required / some / virtually
            / typically / as many … as any one）；每天 1 题 MBT + 1 题
            Weaken (范围敏感型)。
```

7-day plan: Y 灯 = 条件逻辑 + 方法识别（合计 20 题），黄 = 原则匹配
（10 题），绿 = 范围控制（4 题）+ 整 Section 计时复测。

## 9. Quick-reference card (for prompt preamble to coder agents)

When dispatching a coder/analyst subagent to write Part III, paste this
card verbatim into the prompt preamble **before** any other instructions:

```
错因标签只能用以下四个之一（外加 escape hatch 「题型误判」）：
  条件逻辑 / 范围控制 / 方法识别 / 原则匹配
禁止同义改写、禁止双标签、禁止按错选字母或表面关键词打标签。
若用户 BR 8 节分析无法定位缺陷层，先补做 BR 再打标签。
跨 workbook 聚合脚本按这四个字符串 join，命名漂移会让对比失败。
```

This card has been retrofitted onto every PT107 / PT108 / PT109 build
script after the v2 failure mode, and is now mandatory.

## 10. Related Skills

## Related Skills

- **→ `lsat-pdf-to-section-docx`** — Route here when the source material is an image-only Cambridge LSAT category PDF (cover labeled "Cambridge LSAT / <Category> / N Questions"). This skill transcribes to a Weaken-template `.docx` (two questions per page + answer-key tail), then `lsat-blind-review` or `lsat-prep-tutor` can take over.
- **→ `lsat-prep-tutor`** — Route here for in-session single-question 7Sage-style讲解 (modes A/B/C/D in that skill). Use when the user has a question in hand and wants the analysis now, not a workbook.
- **↔ `lsat-blind-review`** — Default entry point for multi-question BR workbooks. Produces `.docx` (Part I 题目卡 + Part II 八段式 + Part III 劣势报告 + 来源说明).
- **← from `lsat-prep-tutor`** — When the user wants a 7Sage-style analysis baked into a permanent workbook (vs. in-session markdown), route from `lsat-prep-tutor` here.
- **← from `lsat-pdf-to-section-docx`** — When the user finishes a 2-up transcription and then asks for错题分析 or Blind Review on the questions in it, route from `lsat-pdf-to-section-docx` here.
