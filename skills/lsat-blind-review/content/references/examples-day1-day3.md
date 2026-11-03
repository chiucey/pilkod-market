---
name: examples-day1-day3
description: |
  Worked examples for the two flagship deliverables built with this skill —
  the Day 1 workbook (10 wrong questions, PT109 Section 1) and the Day 2+3
  workbook (34 wrong questions across Cambridge LR Vol.1 Day 2 and Day 3).
  Use this file as the structural template and verification reference whenever
  a new Blind Review build needs concrete shapes for: the wrong-question
  intake row, the anchor-keyword sampling list, the Part I card layout, the
  eight-section Part II analysis, the Part III weakness report, and the
  pre-delivery verification harness output.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
metadata:
  trigger: 用户要求复刻 Day 1 / Day 2+3 工作簿结构或新建 BR 时调用
  source: 基于 /Users/log/.cache/lsat_workbook/ 中真实 build_v3.py / extract_all_workbooks.py 的输出
---

# Day 1 and Day 2+3 — Worked Examples

This file shows exactly what the skill produced the last two times it ran end-to-end. It is the structural template for any new BR build.

The two reference deliverables are:

| Deliverable | Path | Wrong Qs | Builder script (read-only, in `/Users/log/.cache/lsat_workbook/`) |
|---|---|---|---|
| Day 1 v1 | `/Users/log/LSAT_LR_Day1_Blind_Review_解析_v1.docx` | 10 | `extract_pt109.py`, `build_docx.py` (legacy pipeline) |
| Day 2+3 v3 | `/Users/log/LSAT_LR_Day2_Day3_Blind_Review_解析_v3.docx` | 34 | `build_v3.py` (current pipeline) |

The Day 2+3 v2 file (`..._v2.docx`) is the mis-mapped deliverable — keep it as a `.bak2` example of what *not* to ship, and never rebuild it.

## 1. Wrong-question intake (the source-of-truth row)

Both workbooks started from the same schema. Every row is what the user told us they got wrong; the `correct` column is filled in by the build after web verification, and is **never** inferred from the user's pick.

### 1.1 Day 1 (PT109 Section 1, 10 wrong Qs)

| Day | Q | Type | Correct | Your pick | Bucket |
|---|---|---|---|---|---|
| PT109 S1 | 4 | Weaken | D | C | 方法识别 |
| PT109 S1 | 11 | MBT | E | D | 范围控制 |
| PT109 S1 | 12 | Flaw | B | C | 条件逻辑 |
| PT109 S1 | 13 | Assumption / SA | B | A | 条件逻辑 |
| PT109 S1 | 15 | Method (Parallel Flaw) | C | A | 条件逻辑 |
| PT109 S1 | 17 | Weaken Evidence | B | D | 方法识别 |
| PT109 S1 | 18 | Principle Match | A | D | 原则匹配 |
| PT109 S1 | 20 | Weaken EXCEPT | D | A | 方法识别 |
| PT109 S1 | 21 | Principle Justify | C | D | 原则匹配 |
| (other rows in PT109 S1 were answered correctly; not listed) | | | | | |

This list lives in `/Users/log/.cache/lsat_workbook/all_workbooks_wrong_qs.json` under the `"PT109_S1"` source key; the per-Q analyses live in `pt109_section1_chunks.json`. The build script reads these, joins with the verified answer key, and writes Part I / II / III.

### 1.2 Day 2+3 (Cambridge LR Vol.1, 34 wrong Qs)

| Day | Q | Type | Correct | Your pick | Bucket |
|---|---|---|---|---|---|
| 2 | 3 | Acceptance / SA | D | C | 条件逻辑 |
| 2 | 8 | Acceptance / SA | E | D | 范围控制 |
| 2 | 10 | Acceptance / SA | D | B | 条件逻辑 |
| 2 | 13 | MBT | E | B | 范围控制 |
| 2 | 14 | MBT | D | C | 范围控制 |
| 2 | 17 | MBT | C | B | 范围控制 |
| 2 | 23 | Flaw | C | B | 方法识别 |
| 2 | 26 | Flaw | C | A | 方法识别 |
| 2 | 27 | Flaw | A | E | 方法识别 |
| 2 | 29 | Flaw | C | E | 方法识别 |
| 2 | 31 | Method | B | C | 方法识别 |
| 2 | 34 | Method | B | D | 方法识别 |
| 2 | 36 | Principle | D | B | 原则匹配 |
| 2 | 37 | Principle | D | C | 条件逻辑 |
| 2 | 38 | Principle | C | A | 方法识别 |
| 3 | 7 | Flaw | B | E | 条件逻辑 |
| 3 | 9 | Acceptance / SA | A | D | 原则匹配 |
| 3 | 10 | Acceptance / SA | A | C | 条件逻辑 |
| 3 | 12 | MBT | D | C | 范围控制 |
| 3 | 16 | MBT | B | E | 范围控制 |
| 3 | 22 | Flaw | B | A | 方法识别 |
| 3 | 23 | Flaw | B | A | 方法识别 |
| 3 | 24 | Flaw | C | E | 方法识别 |
| 3 | 25 | Flaw | B | C | 方法识别 |
| 3 | 27 | Flaw | D | E | 范围控制 |
| 3 | 28 | Flaw | D | E | 范围控制 |
| 3 | 29 | Flaw | E | B | 方法识别 |
| 3 | 30 | Flaw | D | D | 方法识别 |
| 3 | 32 | Method | E | B | 方法识别 |
| 3 | 33 | Method | C | B | 方法识别 |
| 3 | 34 | Method | C | E | 条件逻辑 |
| 3 | 35 | Principle | E | A | 方法识别 |
| 3 | 38 | Principle | C | B | 原则匹配 |
| 3 | 39 | Principle | C | D | 原则匹配 |

34 rows total: 15 from Day 2 (Q3, Q8, Q10, Q13, Q14, Q17, Q23, Q26, Q27, Q29, Q31, Q34, Q36, Q37, Q38) and 19 from Day 3 (Q7, Q9, Q10, Q12, Q16, Q22, Q23, Q24, Q25, Q27, Q28, Q29, Q30, Q32, Q33, Q34, Q35, Q38, Q39). Q30 (Day 3) is the row where the user picked D and the correct answer is also D — it appears in the workbook because the user flagged it as "I almost chose E, decided D, want to confirm my read." Do not silently drop "correct = your pick" rows; include them with a `verified_self` tag in Part II.

## 2. Anchor keywords for stimulus verbatim sampling

The mandatory verification harness needs 3–5 distinct anchor keywords per workbook, chosen so each one uniquely identifies a *different* wrong-Q card. These are pulled from the actual stimulus text in the source PDF. The build script reads them from a config block; the harness then asserts each anchor appears in Part I of the rendered DOCX.

### 2.1 Day 1 anchor list (sample)

```python
DAY1_ANCHORS = [
    ("Q4",  "handedness",                        "PT109 S1 Q4 (marmosets, imitation)"),
    ("Q11", "advertisements that contain",       "PT109 S1 Q11 (TV ad, percent)"),
    ("Q12", "win each of the past six games",     "PT109 S1 Q12 (coaching flaw)"),
    ("Q13", "trading in company stock",          "PT109 S1 Q13 (CEO assumption)"),
    ("Q15", "similar argument pattern",          "PT109 S1 Q15 (parallel flaw)"),
]
```

If any of these strings fails to appear in the rendered Day 1 DOCX's Part I, the build halts. The same gate caught the Day 2+3 v2 disaster — when Q3's stimulus was missing "How do the airlines expect to prevent", the harness flagged it on the first build attempt.

### 2.2 Day 2+3 anchor list (the canonical example)

These six anchors are referenced verbatim in SKILL.md §"Verification" and were used to retroactively catch the v2 mis-mapping:

```python
DAY23_ANCHORS = [
    ("Q3",   "How do the airlines expect to prevent",          "Day 2 Q3 (airline / biz-traveler SA)"),
    ("Q10",  "privatization",                                  "Day 2 Q10 (state-owned utility)"),
    ("Q17",  "Danaxil",                                        "Day 2 Q17 (MBT / superlative)"),
    ("Q26",  "Psychotherapy has been described",               "Day 2 Q26 (Flaw / target vs practice)"),
    ("Q7",   "Golden Lake Development",                        "Day 3 Q7 (Flaw / NA strength)"),
    ("Q33",  "modern centuries",                               "Day 3 Q33 (Method / same-direction)"),
]
```

When authoring anchor keywords for a new workbook:

1. Open the source PDF, run the Q-number extraction protocol (SKILL.md §"Mandatory Pre-Flight").
2. For each wrong Q, find a 3–6 word phrase that is **unmistakably** from that question's stimulus — proper nouns ("Danaxil", "Golden Lake Development"), distinctive lead clauses ("How do the airlines expect to prevent"), or rare vocabulary not used in any other question.
3. Reject anchors that could plausibly appear in the wrong Q (e.g. don't use "therefore" — every argument ends with that).
4. Keep 3–5 anchors per workbook; a workbook with N < 10 wrong Qs can use 3 anchors; N ≥ 30 should use 5–6.

## 3. Part I card — exact layout

Each wrong-Q card is a single page (or page-spanning if the stimulus is long). The layout below is what the builder emits. **No answers, no hints, no explanation** — only stimulus + stem + A–E.

```
┌──────────────────────────────────────────────────────────────┐
│ Day 2 · Q23 · Flaw                                          │
│                                                              │
│ 【stimulus — verbatim English, 1+ paragraph】               │
│ Economists have traditionally argued that the value of a    │
│ good is determined solely by the cost of producing it.      │
│ However, some recent studies have shown that consumers     │
│ are often willing to pay substantially more for a good     │
│ whose price they associate with higher quality, even when  │
│ the production cost is identical to a cheaper alternative. │
│ Therefore, the traditional economic view fails to account  │
│ for all the factors that determine a good's value.          │
│                                                              │
│ 【stem】                                                     │
│ Which one of the following most accurately describes the    │
│ flaw in the economists' argument?                            │
│                                                              │
│ 【options】                                                  │
│ A. It relies on evidence that is irrelevant to its claim.   │
│ B. It draws a conclusion from a sample that is biased.     │
│ C. It fails to consider an alternative explanation that    │
│    accounts for the very evidence it cites.                │
│ D. It confuses a necessary condition for a sufficient one.  │
│ E. It bases a generalization on a single case study.        │
│                                                              │
│ [page break]                                                 │
└──────────────────────────────────────────────────────────────┘
```

Notes:

- Heading is `Day <n> · Q{nn} · {题型}` — 宋体四号 (14pt) bold black, per AGENTS.md.
- Stimulus / stem / options: 仿宋小四 (12pt) regular black.
- Latin words are typeset in **Times New Roman** (English prose) and **Arial** (English titles); CJK in 宋体 / 仿宋 / 楷体 per `AGENTS.md` (2026-09 override of the prior Latin Aptos + CJK Microsoft YaHei default).
- No `BR self-answer table` unless `BR_SELF_ANSWER_TABLE=1` is exported before the build (see SKILL.md Hard Rule #1).
- No bold, shading, or colour on any option letter.

## 4. Part II — eight-section analysis template

Per the SKILL.md, every wrong question gets an analysis with eight numbered sections. Below is the canonical Day 2 Q23 example, abbreviated; the full version is ~400–600 字 of Chinese.

```
Day 2 · Q23 · Flaw                                                       ✓verified
─────────────────────────────────────────────────────────────────────────────
正确答案：C   你的答案：B   错因标签：替代解释遗漏（方法识别）

① 题型识别
Flaw。识别 argument 缺陷类型；选项是 abstract 视角的 flaw 名。

② 任务翻译
「指出 argument 的逻辑错误是什么」。

③ stimulus 拆解 / 条件关系
P1 传统观点：价值 = 生产成本。
P2 反例：消费者愿付高价 → 高质量感知 ⇒ 高价，即便成本相同。
C 传统观点 fail to account for all factors。

隐含桥接：消费者愿付高价 ⇒ 因为「高质量感知」驱动（C 的解释）。
论证假设：高价仅由「高质量感知」驱动，无其他竞争性解释。

④ BR 预判
看到 C：「fail to consider an alternative explanation that accounts for
the very evidence it cites」。这恰好命名了 stimulus 的结构 —— stimulus
自己给出反例，并隐含「高质量感知」这个替代解释，但 economists 没有
考虑它。

⑤ 正确答案为何对
C 精准命中：stimulus 反例可由「高质量感知」解释，economists 未考虑
此替代解释，因此他们的「价值 = 成本」模型 fail。BR 时应识别为
"alternative explanation overlooked"。

⑥ 你实际所选为何有吸引力又为何不对
B「draws a conclusion from a sample that is biased」—— 看起来抓住
「some recent studies」字样。但 stimulus 没有采样偏差，只有一类反例；
且 B 没有触及 economists 未考虑替代解释这一核心缺陷。

⑦ 其余选项排除
A「irrelevant evidence」 — 错；evidence 高度相关。
D「necessary ↔ sufficient」 — 错；未发生该混淆。
E「generalization from single case」 — 部分对（确实 single counter-
example），但 C 比 E 更精确：根本不是「过快地一般化」，而是「忽视了
替代解释」。

⑧ 可迁移 Takeaway + 原题选项速览
Takeaway：Flaw 题出现反例 + 结论抱怨模型不完整 → 先查「alternative
explanation overlooked」(C 类)，其次才是 sampling / hasty generalization。
原题选项速览（只列字母，不展开）：
A — irrelevant evidence
B — biased sample        ← 你的错选
C — alt explanation overlooked  ← 正确答案
D — necessary ↔ sufficient
E — single-case generalization
```

Per Hard Rule #1 of the skill, **none** of the literal strings `正确答案`, `可迁移 Takeaway`, or `答案速览` may appear in Part I of the rendered DOCX; they only appear in Part II.

## 5. Part III — weakness report (excerpt)

The Day 2+3 v3 report has four sections. Below is an excerpt of the Day 2 report's first weakness entry (the rest is in the actual DOCX):

```
③ 错因标签频次表（Day 2+3 全部 34 题）

| 错因标签 | 题数 | 涉及题号 |
|---|---|---|
| 替代解释遗漏 (Flaw) | 2 | Day2 Q23、Day3 Q22 |
| fatal leap 误识为循环 | 1 | Day3 Q29 |
| 鸽笼原理 MBT | 1 | Day3 Q12 |
| 方法角色 EXCEPT 误判 | 4 | Day2 Q31/Q34、Day3 Q32/Q33 |
| 原则强度过强 | 3 | Day2 Q37、Day3 Q38/Q39 |
| … | … | … |

⑥ 7 日优先级训练清单（Day 2+3 节选）

| 日期 | 状态 | 训练内容 |
|---|---|---|
| Day 1 | 黄灯 | Method/EXCEPT 角色识别 — Day 2 Q31/Q34 + Day 3 Q32/Q33/Q34/Q35 共 6 题 |
| Day 2 | 黄灯 | Acceptance NA 桥接 — Day 2 Q3/Q8/Q10 + Day 3 Q7/Q9/Q10 共 6 题 |
| Day 3 | 红灯 | MBT 数字与精度 — Day 2 Q13/Q14/Q17 + Day 3 Q12/Q16 共 5 题 |
| Day 4 | 黄灯 | Principle Apply/Identify 三要素 — Day 2 Q36/Q37/Q38 + Day 3 Q38/Q39 共 5 题 |
| Day 5 | 红灯 | Flaw 替代解释 / fatal leap / false negative — Day 2 Q23/Q26/Q29 + Day 3 Q23/Q28/Q29/Q30 共 7 题 |
| Day 6 | 绿灯 | 综合套题 30 题，重点记 BR 预判 vs 正确的一致率 |
| Day 7 | 绿灯 | 重做本套 34 道（限时 1 分 30 秒/题），目标 ≥ 28/34 一致 |
```

The Day 1 report follows the same four-section shape but with the 10-row anchor list and the four-bucket weakness decomposition (条件逻辑 / 范围控制 / 方法识别 / 原则匹配).

## 6. Verification harness — what `ALL PASS` actually looks like

The harness is a one-shot Python script (e.g. `verify_lsat_v3.py` in `/Users/log/.cache/`). Below is the Day 2+3 v3 harness output that gates delivery:

```
$ python3 /Users/log/.cache/verify_lsat_v3.py
[1/8] python-docx import           PASS
[2/8] Q-IDs in Part I and Part II   PASS (34 cards, 34 analyses)
[3/8] 答案速览表 row count          PASS (34 rows)
[3/8]   (题号, 正确答案, 你的答案) triples verified
                                        PASS (13 ✓verified, 21 ~ mirror)
[4/8] Part I contains 正确答案/可迁移 Takeaway/答案速览   PASS (0 hits)
[5/8] Critical phrases in Part II  PASS
       Day1 Q10/Q32/Q40 (n/a)       PASS
       Day2 Q26/Q31/Q38             PASS (C / B / C)
       Day3 Q29/Q33                 PASS (E / C)
[6/8] Footer PAGE / NUMPAGES field codes   PASS
[7/8] textutil convert txt         PASS
[7/8] unzip -t                     PASS
[8/8] Stimulus verbatim sampling   PASS
       Day2 Q3   anchor "How do the airlines expect to prevent"  found
       Day2 Q10  anchor "privatization"                          found
       Day2 Q17  anchor "Danaxil"                                 found
       Day2 Q26  anchor "Psychotherapy has been described"      found
       Day3 Q7   anchor "Golden Lake Development"               found
       Day3 Q33  anchor "modern centuries"                      found
ALL PASS — 34/34
```

Two non-obvious rules to keep in mind:

1. The "13 ✓verified, 21 ~" line in step [3/8] is *expected*. Only 13 of the 34 answers had public prep-page confirmation (7Sage / LSAT Lab / LSAT Hacks / PowerScore Forum); the other 21 are structurally identical to confirmed Cambridge LR items, so we tag them `~` (best-guess mirror). **Never** mark all 34 as `✓verified` — that is dishonest labeling (see Hard Rule #3 and the "Common Mistakes" section of SKILL.md).
2. If step [8/8] fails on Day 2 Q3 with `anchor "How do the airlines expect to prevent" NOT found`, that is the v2-style mis-mapping signature: the build script cross-matched Q3's content to a different Q-number's stimulus. Re-run the PDF Q-Number Extraction Protocol and re-extract the Q-body JSON; do not patch the harness.

## 7. Hard-rule quick reference (from the actual builds)

These are the rules both reference builds enforced; new workbooks must enforce them too.

| # | Rule | Enforced by | Reference build evidence |
|---|---|---|---|
| 1 | Part I never contains 正确答案 / 可迁移 Takeaway / 答案速览 | `build_v3.py` Part I builder | Day 2+3 v3 harness step [4/8] PASS |
| 2 | Every "correct" answer web-verified or tagged `~` | `verify_lsat_v3.py` step [3/8] | 13 ✓verified + 21 ~ |
| 3 | Stimulus verbatim against pre-extracted JSON | step [8/8] anchor sampling | Day 2+3 v3 6/6 anchors found |
| 4 | No build scripts left in `/Users/log/` | builder path is `/Users/log/.cache/lsat_workbook/` | `build_v3.py` lives only there |
| 5 | Filename uses `vx` suffix | builder filename emitter | `LSAT_LR_Day2_Day3_Blind_Review_解析_v3.docx` |
| 6 | Footer has PAGE / NUMPAGES field codes | builder `add_footer()` | Day 2+3 v3 harness step [6/8] PASS |
| 7 | Q-numbers = PDF Q-numbers (no content cross-match) | pre-flight extraction + JSON join | Day 2+3 v2 failed this; v3 fixed it |
| 8 | Back up before rebuilding a known-bad version | manual `cp ... .bakN` step before `build_v3.py` | Day 2+3 v2 is now `.bak2` |

## 8. How to use this file for a new workbook build

1. Run SKILL.md §"Mandatory Pre-Flight" on the new PDF; extract Q-IDs and per-Q bodies to JSON.
2. Take the user's wrong-Q list, drop it into the schema in §1 above (rows = user-pick rows).
3. Pick anchor keywords (§2) — at least 3, ideally 5–6 for N ≥ 30.
4. Build Part I cards per the layout in §3 (no answers, no `BR self` table unless `BR_SELF_ANSWER_TABLE=1`).
5. Build Part II analyses per the template in §4 (eight sections; `✓verified` only after web search).
6. Build Part III per the structure in §5 (分布表 + 4–6 劣势 + 7 日清单 + 来源说明).
7. Run the harness; expect the shape of the output in §6. If any step fails, do not deliver — fix and re-run.

The verification-before-completion rule is non-negotiable: do not claim the workbook is done until the harness prints `ALL PASS` and a human has spot-checked 2–3 cards in the rendered DOCX against the source PDF (SKILL.md §"Independent spot-check before declaring done").

## Related Skills

- **→ `lsat-pdf-to-section-docx`** — Route here when the source material is an image-only Cambridge LSAT category PDF (cover labeled "Cambridge LSAT / <Category> / N Questions"). This skill transcribes to a Weaken-template `.docx` (two questions per page + answer-key tail), then `lsat-blind-review` or `lsat-prep-tutor` can take over.
- **→ `lsat-prep-tutor`** — Route here for in-session single-question 7Sage-style讲解 (modes A/B/C/D in that skill). Use when the user has a question in hand and wants the analysis now, not a workbook.
- **↔ `lsat-blind-review`** — Default entry point for multi-question BR workbooks. Produces `.docx` (Part I 题目卡 + Part II 八段式 + Part III 劣势报告 + 来源说明).
- **← from `lsat-prep-tutor`** — When the user wants a 7Sage-style analysis baked into a permanent workbook (vs. in-session markdown), route from `lsat-prep-tutor` here.
- **← from `lsat-pdf-to-section-docx`** — When the user finishes a 2-up transcription and then asks for错题分析 or Blind Review on the questions in it, route from `lsat-pdf-to-section-docx` here.