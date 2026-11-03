---
name: lsat-blind-review-mistakes-history
description: Concrete failure modes from previous Blind-Review workbook builds (Day 2+3 v2 mis-mapping, v3 verified-vs-mirror ratio, layout / verification gaps, recovery actions). Read this before dispatching any new workbook so the same errors do not repeat.
---

# Mistakes history — LSAT LR Blind Review workbooks

This file is the post-mortem log for every known failure of `lsat-blind-review` /
its predecessors. Each entry follows the same shape:

- **What happened** — observable fact, with the deliverable path.
- **Why it happened** — root cause, not surface symptom.
- **What now prevents it** — the rule, code, or check that closes the gap.

Future builds should treat the "what now prevents it" column as a hard
prerequisite, not advice.

---

## 1. Day 2+3 v2 — entire workbook mis-mapped by content keyword

**Deliverable:** `/Users/log/LSAT_LR_Day2_Day3_Blind_Review_解析_v2.docx`
(backed up as `…_v2.bak2`).

**What happened.** A codegen sub-agent was given the user's 34 wrong Q-numbers
plus their chosen letters. Instead of treating the user's Q-numbers as the PDF
Q-numbers, the agent cross-matched by content keywords: it saw "Danaxil" /
"privatization" / "Golden Lake" elsewhere in the source set and assigned those
stimuli to the user's Q17 / Q10 / Q7. The user opened the first 3 cards and
reported "none of these are my wrong questions". The whole document was
wrong; only Part II's answer-letter table happened to be honest.

**Why it happened.** Three reinforcing gaps:

1. The prompt to the generator agent said "fill in the stimulus for each
   user's Q-number" without explicitly forbidding content matching.
2. The agent fell back to its default behavior — when a Q-number is missing
   from the snippet it can see, it matches by content keywords. This is the
   exact failure mode the PDF Q-Number Extraction Protocol exists to prevent.
3. No structural harness in v2 sampled stimulus text. The audit only checked
   paragraph counts and answer-letter counts — both of which were clean.

**What now prevents it.**

- The **PDF Q-Number Extraction Protocol** in SKILL.md § "Mandatory Pre-Flight":
  enumerate every `Q(\d+)\. \[` label in the full text first, diff against the
  user's wrong-question list, STOP on any miss.
- Hard rule #10 in SKILL.md: every prompt to a coder / generator sub-agent
  must start with "Strictly use the user's Q-numbers as the PDF Q-numbers.
  Each Q-body (stimulus + stem + A–E) must be read verbatim from the
  pre-extracted JSON. Do NOT cross-match by content keywords."
- Verification check #8 (stimulus verbatim sampling): the harness picks 3–5
  anchor keywords (e.g. "Danaxil" for Q17, "privatization" for Q10,
  "Golden Lake Development" for Q7 on Day 3) and asserts each appears in
  Part I at the right Q.
- Verification check #9 (independent spot-check): after the harness passes,
  manually read 2–3 question cards from Part I and confirm the stimulus is
  the question the user actually meant. Do not trust the harness alone.

**Lesson.** A clean structural audit is necessary but not sufficient. Any
build where the user's "what Q did I get wrong" data flows through an
LLM-mediated mapping step needs a content-sampling check before the user
opens the file.

---

## 2. Day 2+3 v3 — verified vs mirror label drift

**Deliverable:** `/Users/log/LSAT_LR_Day2_Day3_Blind_Review_解析_v3.docx`
(the correct, currently-shipped version).

**What happened.** Of 34 wrong questions, the v3 build labelled every single
one as `✓verified`. In reality only 13 of 34 had a public prep page
(7Sage / LSAT Lab / LSAT Hacks / PowerScore Forum) confirming the answer
against the **correct** stimulus. The other 21 were best-guess mirrors of
structurally identical Cambridge LR items.

**Why it happened.** The "verified" label was being applied on the basis of
"WebSearch returned any matching answer key" — without checking that the
search hit was actually about the same stimulus. Web search is good enough
to find a likely correct letter, but not good enough to claim verification
unless the prep page quotes or paraphrases the stimulus.

**What now prevents it.**

- Hard rule #3 in SKILL.md: tag `✓verified` only when ≥ 1 independent prep
  page confirms the answer against the **correct stimulus** (the same
  Q-number the user listed). Otherwise use `~` for mirror / `?` for
  unconfirmed.
- Common-mistakes entry in SKILL.md: "Marking every question as `✓verified`
  when only 13 of 34 actually had public prep confirmation → dishonest
  labeling. Use `~` for mirrors and `?` for unconfirmed."
- The Day 2+3 v3 workbook now correctly shows `✓verified` on 13 and `~` on
  21. Do **not** inflate this ratio when describing the file to the user.

**Lesson.** A label that means "I checked" must mean something specific. If
the criterion is loose, the label will be applied liberally and lose its
signal value.

---

## 3. v1 (Day 1) — BR self-answer table was added by default

**Deliverable:** `/Users/log/LSAT_LR_Day1_Blind_Review_解析_v1.docx`.

**What happened.** The v1 build included a "BR 自答表 / 我的答案 / 信心"
table on every Part I card, because the build script inherited that table
from an earlier draft. The user later clarified that the default should be
**no** self-answer table — they want a clean Blind Review (read stimulus,
decide, then turn the page). The table is opt-in only.

**What now prevents it.**

- Hard user preference #1: default Part I question cards do **not** include a
  BR self-answer table. If a build script wants to add one it must be
  opt-in via the environment variable `BR_SELF_ANSWER_TABLE=1`.
- The cleanup script `scripts/strip_self_answer_table.py` (see companion
  reference) lets users remove the table from already-shipped docx files
  later, without rebuilding.
- Already-delivered docx files are **not** rebuilt. The v1 Day 1 file keeps
  its self-answer table because the user did not request removal on that
  file; we add the table-strip script as a future-facing convenience, not
  a retroactive edit.

**Lesson.** "Defaults drift toward what the first build happened to do."
Any opinionated default must be made explicit at the skill level, with an
env-var opt-out, before the first run ships.

---

## 4. Layout / verification gaps seen across builds

These are smaller mistakes that did not produce a "wrong workbook" but did
produce a "right workbook with a wrinkle." Each one is now closed.

| Symptom | Where seen | Prevention |
|---|---|---|
| Forgot page break between Parts → reader sees one continuous stream. | early v1 drafts | Build script inserts `<w:br w:type="page"/>` before Part II and Part III headings; verify checks Part I / II / III each contain their respective speed-table marker. |
| Answer speed-table missing the user's chosen-letter column. | some early per-PT drafts | Hard rule #3 in SKILL.md + verification check #3: every (题号, 正确答案, 你的答案) triple must be present. |
| Helper script `build_*.py` left in project root. | Day 2+3 v2 era | Hard rule #1: scripts live under `/Users/log/.cache/lsat_workbook/` or `/Users/log/.cache/lsat_review/`. |
| Footer missing `PAGE` / `NUMPAGES` field codes. | some PT109 drafts | Hard rule #8 + verification check #6: footer XML must contain both field codes. |
| Highlight color for correct answers not applied. | some PT107 drafts | Hard rule #8: bold + light-blue (`DCE6F1`) shading for correct answers in Part II. |
| CJK fallback to SimSun / Latin fallback to Times. | first 4 builds | Hard rule #8: CJK 宋体 / 仿宋 / 楷体 per `AGENTS.md`; English Times New Roman for prose, Arial for titles. (2026-09 override of the prior YaHei + Aptos default.) |
| **2026-09-19 output format reset** — first build after user's font / color override still used Aptos + YaHei + #DCE6F1 shading. | `LSAT_LR_Flaw_Q201-240_v1.docx` first build (2026-09-19) | User-edited v1 (127 KB) is now the canonical reference; `references/output-format.md` is the single source of truth for fonts / colors / sizes / spacing. Build scripts MUST read `output-format.md` before generating any new workbook. |
| Cover page (Title / Subtitle / Version / Meta / Part 概览 / 使用说明) emitted in 2026-09-19 first build. | `LSAT_LR_Flaw_Q201-240_v1.docx` first build | User dropped the entire cover page; new title line is `LSAT LR · <Scope> · Blind Review Workbook v{n}` as paragraph 0. See `output-format.md` §3.1. |
| Standalone 来源说明 final page emitted in 2026-09-19 first build. | `LSAT_LR_Flaw_Q201-240_v1.docx` first build | User embedded sources inline at the end of each question's ⑤ section as `来源：lsatlab + 7sage ...` lines; no standalone 来源说明 page. See `output-format.md` §3.5. |
| **2026-09-19 Part I scope change**: all 40 attempted Qs in Part I (legacy "Day 1 / PT109" pattern). | `LSAT_LR_Flaw_Q201-240_v1.docx` first build | User preference update: Part I now contains ONLY the user's wrong questions. Part II's speed-table + 8-section analysis also scope-narrows to the same wrong Qs. Correct-but-attempted Qs are dropped entirely. See `output-format.md` §3.2. |
| **2026-09-19 missing timestamp row**: top of docx had only the title, no `Finished Time:` line. | `LSAT_LR_Flaw_Q201-240_v2.docx` (first build with only-wrong-Qs Part I) | User-requested addition: every workbook must include a right-aligned `Finished Time: {H:MMa.m./p.m. Mon Dth (Wkd), YYYY}` row immediately below the title. Apply retroactively to v2 by saving as v3. See `output-format.md` §3.1. |
| Wrong file delivered when rebuilding over a known-bad version. | Day 2+3 v2 → v3 transition | Always copy the old file to `<name>.bakN` before re-emitting. v3 of Day 2+3 sits next to v2.bak2; the user can diff if needed. |
| Web-search confirmation against the wrong stimulus (paired with v2 mapping). | Day 2+3 v2 | Verification check #9 + hard rule #3 chain — verify Q-mapping first, then verify answers. |
| Generator agent improvising on ambiguous prompts. | Day 2+3 v2 | Hard rule #10: every generator prompt starts with the "no content matching" rule. |

---

## 5. Build-script archaeology — what lives where

The build scripts that produced each deliverable are kept under
`/Users/log/.cache/lsat_workbook/` (read-only convention — do not modify,
do reference). When the orchestrator needs to retrace a build:

| Deliverable | Build script | Verify script | Pre-extract JSON |
|---|---|---|---|
| `LSAT_LR_Day1_Blind_Review_解析_v1.docx` | (early `build_docx.py` draft) | `verify_pt109.py` lineage | `q_bodies.json` |
| `LSAT_LR_Day2_Day3_Blind_Review_解析_v2.docx` | `build_v3.py` (mis-mapped) | — | (v2 used a content-keyword match path) |
| `LSAT_LR_Day2_Day3_Blind_Review_解析_v3.docx` | `build_v3.py` (re-run with strict mapping) | `verify_cross_workbook_report_v1.py` lineage | `q_bodies.json` + per-Q clean JSON |
| `LSAT_LR_Principle_Identify_Section3_Blind_Review_解析_v1.docx` | `build_pi_s3_v1.py` | `verify_pi_s3_v1.py` | `pi_s3_clean.json` |
| `LSAT_LR_PT107_Section1_Section3_Blind_Review_解析_v1.docx` | `build_pt107_s1s3_v1.py` | `verify_pt107_s1s3_v1.py` | `pt107_s1_clean.json`, `pt107_s3_clean.json` |
| `LSAT_LR_PT108_Section2_Blind_Review_解析_v1.docx` | `build_pt108_s2_v1.py` | `verify_pt108_s2_v1.py` | `pt108_s2_clean.json` |
| `LSAT_LR_PT109_Section1_Blind_Review_解析_v1.docx` | `build_pt109_s1` lineage (via `build_docx.py`) | `verify_pt109.py` | `pt109_section1_clean.json` |
| `LSAT_LR_PT109_Section3_Blind_Review_解析_v1.docx` | `build_pt109_s3_v1.py` | `verify_pt109_s3_v1.py` | `pt109_s3_clean.json` |
| `LSAT_LR_PT109_Section4_Blind_Review_解析_v1.docx` | `build_pt109_s4_v1.py` | `verify_pt109_s4_v1.py` | `pt109_s4_clean.json` |
| `LSAT_LR_跨Workbook_错题优劣势分析报告_v1.docx` | `build_cross_workbook_report_v1.py` | `verify_cross_workbook_report_v1.py` | `all_workbooks_wrong_qs.json`, `all_workbooks_local_weaknesses.json` |

Note: the cache directory is read-only by convention. The skill itself does
not own these scripts; the user's project root does. New scripts for new
workbooks should also be written there.

---

## 6. Already-delivered docx files — do not rebuild

Per user preference #2, the following 9 (plus the cross-workbook report,
10 total) files are **already delivered** and must not be rebuilt or
modified:

1. `/Users/log/LSAT_LR_Day1_Blind_Review_解析_v1.docx`
2. `/Users/log/LSAT_LR_Day2_Day3_Blind_Review_解析_v2.docx` (broken — left in place for diff against `…_v2.bak2` and v3)
3. `/Users/log/LSAT_LR_Day2_Day3_Blind_Review_解析_v3.docx` (current correct)
4. `/Users/log/LSAT_LR_Principle_Identify_Section3_Blind_Review_解析_v1.docx`
5. `/Users/log/LSAT_LR_PT107_Section1_Section3_Blind_Review_解析_v1.docx`
6. `/Users/log/LSAT_LR_PT108_Section2_Blind_Review_解析_v1.docx`
7. `/Users/log/LSAT_LR_PT109_Section1_Blind_Review_解析_v1.docx`
8. `/Users/log/LSAT_LR_PT109_Section3_Blind_Review_解析_v1.docx`
9. `/Users/log/LSAT_LR_PT109_Section4_Blind_Review_解析_v1.docx`
10. `/Users/log/LSAT_LR_跨Workbook_错题优劣势分析报告_v1.docx`

If a user wants the BR self-answer table removed from any of these, point
them at `scripts/strip_self_answer_table.py` (companion reference) — it
edits the docx in place without re-running the original build.

---

## 7. Anti-patterns to refuse at the prompt level

These are patterns the orchestrator should **reject** in any prompt that
reaches a generator sub-agent, even if the user phrased them innocently:

- "Fill in the stimulus that best matches this Q-number" → forbidden; the
  stimulus is read verbatim from the pre-extracted JSON.
- "Find a Cambridge LR question that looks like Q17" → forbidden; use the
  Q-number the user gave, full stop.
- "Mark all answers verified if WebSearch returns the same letter" →
  forbidden; the search hit must reference the same stimulus.
- "Include a self-answer table on every card" → forbidden by default; opt-in
  via `BR_SELF_ANSWER_TABLE=1`.
- "Skip the harness for speed" → forbidden; the harness is the only honest
  proof of completion.
- "Just open the docx in Word / LibreOffice and fix the layout" →
  **forbidden**; see entry §8 below. Build script 直出 final docx，禁止
  GUI round-trip。

When the orchestrator sees a prompt that could lead a sub-agent into any of
these, rewrite the prompt or stop and ask the user.

## 8. PT01 v1 — 用户偏好精简事件（2026-09-28）

**Deliverable**: `/Users/log/LSAT_LR_PT01_Section3_Section4_Blind_Review_解析_v1.docx` (用户附的 116 KB 版本 — 用户的"干净 workbook"目标版)

**What happened.** Build script `build_pt01_s3s4_v1.py` 直出 57 KB 的 fresh docx（含 9 题核查 / 来源 + 5 张表）。用户随后手工编辑或 LibreOffice 改写，得到 116 KB 的版本：

- **去掉每题 `核查：` + `来源：` 行**：核查 0/9、来源 2/9（仅 Q23 / Q24 残留）。
- **去掉 Part III 的 `2. 错选字母分布` 表**：用户认为不需要。
- **去掉 Part III 的 `5. 7 日训练清单` 表 + 章节标题**：用户认为不需要。
- **Part III `3. 错因标签频次` 被重新编号为 `2.`**（因前一张表删除）。
- **Part II 8 段式被精简为 4 段式**：合并 ①② 为 ①，去 ④ BR 预判 + ⑥ 你实际所选 + ⑦ 其余选项排除（合并入 ③ / ⑤）。
- **行间距收紧**：Part I 从 1.2× → 1.05×；Part II/III 从 1.15× → 1.00×。
- **Part II/III 字体切换为 Helvetica（sans-serif）**：与 Part I 的 Arial+Times New Roman 形成跨 Part 视觉对比。
- **section 数从 4 增加到 7**（次要影响；LibreOffice 插入 implicit sectPr）。

**Why it happened.** 这些修改是用户**有意**做的清理，不是 GUI round-trip 损坏。用户偏好是：

1. workbook 应**干净**——`核查 / 来源 / 错选字母分布 / 7 日训练清单` 都是 build-time 元数据，不属于 end-user workbook。
2. 行间距太松应调紧。
3. 用不同字体（Helvetica vs Arial/Times New Roman）区分 Part 之间。

**What now prevents it.**

1. **`references/output-format.md` 改写 §3.3 Part II**：从 8 段式精简为 4 段式（合并 ①② 去 ④⑥⑦），删除 `核查 / 来源` 行。
2. **`references/output-format.md` 改写 §3.4 Part III**：从 5 张子表精简为 3 张子表（去 `错选字母分布` + `7 日训练清单`）。
3. **`references/output-format.md` 改写 §2 字体规则 + §5 间距表**：Part II/III 字体 = Helvetica 10.5pt；Part I 行距 1.05×；Part II/III 行距 1.00×。
4. **`references/verification-checklist.md` 新增 §9.bis**：校验 workbook 内**不**出现 核查：/来源：行；tables count == 3；不出现 错选字母分布 / 7 日训练清单 子节。
5. **`references/verification-checklist.md` 新增 §9.ter**：校验 Part II 不出现 ②/④/⑥/⑦ 等 8 段式旧标签。

**Recovery action for the affected PT01 v1 docx**: build_pt01_s3s4_v1.py 已按新偏好重写并重新直出（57 KB 风格但内容更精简）。用户附的 116 KB 版本是用户手工编辑的产物，**不是** verify harness 拒收的对象——它是最终交付目标。

**Lesson**：verify_<scope>.py 必须按用户当前偏好校准（workbook 内**不**有 X，**不**等于**校验 X**）。老的"必须有核查 / 来源"是 build-time metadata，不是 end-user content。

## Related Skills

- **→ `lsat-pdf-to-section-docx`** — Route here when the source material is an image-only Cambridge LSAT category PDF (cover labeled "Cambridge LSAT / <Category> / N Questions"). This skill transcribes to a Weaken-template `.docx` (two questions per page + answer-key tail), then `lsat-blind-review` or `lsat-prep-tutor` can take over.
- **→ `lsat-prep-tutor`** — Route here for in-session single-question 7Sage-style讲解 (modes A/B/C/D in that skill). Use when the user has a question in hand and wants the analysis now, not a workbook.
- **↔ `lsat-blind-review`** — Default entry point for multi-question BR workbooks. Produces `.docx` (Part I 题目卡 + Part II 八段式 + Part III 劣势报告 + 来源说明).
- **← from `lsat-prep-tutor`** — When the user wants a 7Sage-style analysis baked into a permanent workbook (vs. in-session markdown), route from `lsat-prep-tutor` here.
- **← from `lsat-pdf-to-section-docx`** — When the user finishes a 2-up transcription and then asks for错题分析 or Blind Review on the questions in it, route from `lsat-pdf-to-section-docx` here.
