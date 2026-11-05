---
name: lsat-blind-review
description: |
  Use when the user provides an LSAT Logical Reasoning practice PDF (Cambridge
  LR Vol.1 or similar) together with a list of question numbers and their
  original wrong answers, and asks for a Blind Review workbook, 7Sage-style
  per-question analysis, or a strength/weakness report. Produces a single
  Chinese Word deliverable `<scope>_Blind_Review_解析_v<n>.docx` in
  `/Users/log/` with Part I question cards (no answers, no hints), Part II
  answer speed-table plus 8-section per-question analysis (web-verified
  correct answers), Part III weakness report, and a 来源说明 section. Default
  Part I cards do NOT include a BR 自答表 / 我的答案 / 信心 / BR self table —
  opt in with `BR_SELF_ANSWER_TABLE=1`. Already-delivered docx files in
  `/Users/log/LSAT_LR_*_Blind_Review_解析_v*.docx` are NOT rebuilt or
  modified; use `scripts/strip_self_answer_table.py` to retroactively strip
  the table from an existing file. Trigger phrases: "Blind Review",
  "错题解析", "7Sage 风格", "错题盲测", "劣势报告", "错因地图".
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
  - AgentSwarm
metadata:
  trigger: 盲测 PDF + 错题列表 → 生成 4 部分中文 docx 盲测工作簿
  source: 基于 wdkimi 会话对 Day1 / Day2+3 / PT107-PT109 共 9 份已交付工作簿的实证工作流
  default-part-i-self-answer-table: false
  opt-in-env-var: BR_SELF_ANSWER_TABLE=1
---

# LSAT LR Blind Review Workbook

This skill produces a single Chinese Word workbook from one or more LSAT
Logical Reasoning practice PDFs plus the user's list of wrong questions with
the letters they originally chose. It was hardened on 9 already-delivered
workbooks (Day 1, Day 2+3, Principle Identify, PT107/PT108/PT109 sections).
Every shipped file passes the pre-flight Q-number protocol, the per-question
web verification, the structural harness, the verbatim stimulus sample, and
the independent visual spot-check.

## What this skill produces

For each invocation:

- one DOCX file `/Users/log/LSAT_LR_<scope>_Blind_Review_解析_v{n}.docx`
  (`v{n}` follows the project's `vx` / `vx.x` convention from `AGENTS.md`),
- 4 parts in fixed order: Part I question cards → Part II answer speed-table
  + 8-section per-question analysis → Part III weakness report → 来源说明,
- English stimulus / stem / A–E wording kept verbatim from the user's PDF,
- Chinese analysis prose in the user-preferred fonts (CJK 宋体 / 仿宋 /
  楷体 per `AGENTS.md`), English prose **Times New Roman**, English titles
  **Arial** (2026-09 user override of the prior Latin Aptos default —
  applies to every new workbook, not retroactively to the 9 frozen
  deliverables),
- correct-answer letters in Part II rendered in **bold black, NO shading**
  (per `AGENTS.md` 红线；supersedes the prior `#DCE6F1` light-blue default),
- page footer carries `PAGE` / `NUMPAGES` field codes,
- **canonical output format**: see `references/output-format.md` (2026-09-19
  reverse-engineered from the user-edited
  `LSAT_LR_Flaw_Q201-240_Blind_Review_解析_v1.docx`). Every build script
  must consume `references/output-format.md` as the single source of truth
  for fonts, sizes, page setup, table styling, and structural layout.
  Older typography notes in `references/four-part-template.md` are kept
  for historical reference but are superseded by `output-format.md`.
- **顶部时间戳**：第 1 段右对齐一行 `Finished Time: {时间戳}`（Arial 9pt
  regular 黑色），位置在标题行正下方。格式 `H:MMa.m./p.m. Mon Dth (Wkd), YYYY`，
  例 `Finished Time: 12:27p.m. Sep 19th (Sat), 2026`。详见
  `references/output-format.md` §3.1。
- **封面 PNG（默认行为，2026-09-28 起所有新 workbook 必做）**：
  每个 workbook 必须同时交付一张 A4 cover PNG
  (`/Users/log/LSAT_LR_<scope>_cover.png`)，用 `scripts/render_cover.py`
  生成，并**嵌入 docx 第 1 页**（在原标题 + 时间戳之前，用 `scripts/insert_cover.py`）。
  遵循 `references/cover-template.md` 设计规范（简洁风格，LSAT 大标题 +
  副标题 + Blind Review，不含版本号 v1）。**不**重写既有正文板式；
  详见 `references/cover-template.md`。

- **封底 PNG（仅奇数页数 workbook 适用，2026-09-28 起所有新 workbook 必做）**：
  若 workbook 最终页数为**奇数**（即 `cover + content` 总页数 mod 2 == 1），则自动生成
  A4 back cover PNG (`/Users/log/LSAT_LR_<scope>_back_cover.png`) 并**嵌入 docx
  作为最后一页**（用 `scripts/insert_back_cover.py`）。Back cover 内容为
  详细英文 workbook 介绍（4 段：ABOUT / METHODOLOGY / HOW TO USE / CAVEAT）+
  版权信息。**所有文字 ≤9pt**（标题 Arial Bold 9pt、正文 Arial Regular 9pt），
  介绍部分总字数 ≤350 词。偶数页 workbook 不插入封底。详见
  `references/back-cover-template.md`。

## What this skill will NOT do

- It will not invent, paraphrase, or drop English question text. Every Q-body
  is read verbatim from the user's PDF.
- It will not put any answer / hint / Takeaway text in Part I. The forbidden
  tokens when scanning Part I content are `正确答案`, `可迁移 Takeaway`,
  `答案速览`, `题型识别`, `BR 预判`.
- It will not include the BR self-answer table (`自答表` / `我的答案` /
  `信心` / `BR self`) in Part I unless `BR_SELF_ANSWER_TABLE=1` is set in
  the build environment. This default matches the user's standing preference.
- It will not rebuild or modify any already-delivered DOCX in
  `/Users/log/LSAT_LR_*_Blind_Review_解析_v*.docx`. The 9 known deliverables
  are frozen. Use `scripts/strip_self_answer_table.py` to retroactively
  clean them up if the user later changes their mind about the table.
- It will not trust page-1 snippets to determine the PDF's Q-numbering
  scheme — only a full enumeration of every Q label in the document tells
  the builder which numbering the PDF actually uses.

## Bundle contents

| Path | What it is |
|---|---|
| `SKILL.md` | This file. |
| `references/output-format.md` | **Canonical output format** (fonts, sizes, page setup, table styling, structural layout). Single source of truth; reverse-engineered from the user-edited 2026-09-19 v1 Flaw workbook. Every build script must read this. |
| `references/cover-template.md` | **封面模板规范**（2026-09-28 起所有新 workbook 适用）：A4 PNG 封面设计 + 参数 + 调用示例 + 红线。 |
| `references/back-cover-template.md` | **封底模板规范**（2026-09-28 起所有奇数页数 workbook 适用）：A4 PNG 封底设计 + ≤9pt 字体规则 + 4 段英文模板 + 红线。 |
| `references/preflight-protocol.md` | The "PDF Q-Number Extraction Protocol" step-by-step, with the exact `pdfplumber` / regex snippets, and the failure mode that caused Day 2+3 v2. |
| `references/verification-checklist.md` | The full mandatory verification harness (Part I/II structural, stimulus verbatim sample, footer XML, `textutil` / `unzip` smoke). |
| `references/mistakes-history.md` | Real-world failure cases from the 9 shipped workbooks (Day 2+3 v2 mis-map, the `✓verified` overclaim on v3, etc.) and the lessons learned. |
| `scripts/render_cover.py` | **封面渲染脚本**（2026-09-28 起所有新 workbook 适用）：CLI `python render_cover.py "<subtitle>" <out.png> [year]`；library `render_cover(subtitle, output_path, year=None)`。 |
| `scripts/insert_back_cover.py` | **封底插入脚本**（2026-09-28 起所有奇数页数 workbook 适用）：检测 workbook 页数 → 奇数时插入 PNG 作为最后一页；偶数时跳过。CLI `python insert_back_cover.py <docx> <png> [--force]`。 |
| `references/weakness-mapping.md` | The four底层能力 buckets (条件逻辑 / 范围控制 / 方法识别 / 原则匹配) and the per-bucket remediation actions used in Part III. |
| `references/four-part-template.md` | Older 4-part typography reference. **Superseded by `output-format.md` for fonts/colors**; kept for historical reference only. |
| `scripts/strip_self_answer_table.py` | Retroactively removes the BR self-answer table from an already-delivered DOCX. Read-only by default; writes a `<name>.nostable.docx` next to the source. Required tool for the "do not rebuild" rule. |
| `scripts/build_*.py` (live in `/Users/log/.cache/lsat_workbook/`) | The actual codegen builders (Day1, Day2+3 v3, PT107/PT108/PT109, cross-workbook report). Read-only reference; the skill cites them but never edits. |
| `scripts/verify_*.py` (live in `/Users/log/.cache/lsat_workbook/`) | The verification harnesses each workbook ships with. Read-only reference. |

## When to use

Use this skill whenever:

- The user attaches an LSAT Logical Reasoning practice PDF and gives a list
  of wrong question numbers with the letters they originally chose.
- The user asks for Blind Review pages, 7Sage-style explanations, a
  "劣势报告 / 错因地图", or any combination of those.
- Multiple Days / sections can be combined into one document (default
  behavior; see the `<scope>` naming rules below).

When **not** to use:

- Pure practice / drill without a workbook deliverable.
- Reading-comprehension or logic-games sections (different schema; not in
  scope — refer the user to a different workflow).
- The user explicitly asks only for a plain answer key without analysis.
- The user only wants to retroactively remove a self-answer table from an
  already-delivered DOCX — just run
  `scripts/strip_self_answer_table.py` directly; do not invoke this skill.

## Mandatory Pre-Flight: PDF Q-Number Extraction Protocol

**Run this BEFORE writing any code or trusting any LLM/agent that the user's
question numbers map to the PDF's question numbers.** This is the single
highest-leverage safety step — skipping it caused the Day 2+3 v2 workbook to
be entirely mis-mapped (Q-numbers were cross-matched by content keywords,
the user opened the first 3 cards and none were their real wrong questions;
the broken file is kept as `LSAT_LR_Day2_Day3_Blind_Review_解析_v2.docx.bak2`
and the correct version is `..._v3.docx`).

1. Extract full text from every page:
   `full = "\n".join((page.extract_text() or "") for page in PdfReader(path).pages)`.
2. Enumerate every Q label in the PDF:
   `qids = sorted({int(m.group(1)) for m in re.finditer(r"Q(\d+)\.\s*\[", full)})`.
3. Compare `qids` to the user's wrong-question list. If any user Q is
   missing, STOP and ask the user — do **not** cross-match by content
   keywords. The user's Q-number **is** the PDF's Q-number.
4. Save `qids` and the chunked per-Q body text (use
   `re.split(r"(?=Q(\d+)\.\s*\[)", full)` to split on Q-label boundaries) to
   a JSON file for downstream scripts.

Full snippet and rationale: `references/preflight-protocol.md`.

## Core Pattern (4-Part Workbook)

The canonical layout is documented in `references/output-format.md`. This
section gives the high-level shape; the formatting reference is the source of
truth for every visual detail.

> **Last updated 2026-09-23** — Part I (Question cards) 调整为两栏 + 9.5pt + 行前后 3pt / 行间距 1.2 倍 + 每 2 题 column break（过长题单列）。Part II / III 沿用原板式。9 份已冻结 docx 不重建。

1. **Part I — Question cards**: ONLY the user's **wrong questions** (the ones
   the user got wrong on the practice set). **All other attempted-but-correct
   questions are NOT included in Part I.** This is the 2026-09-19 user
   preference update — previously Part I contained all attempted questions
   (Day 1 / PT109 style), but the user has decided that Blind Review cards
   are most useful when focused exclusively on questions that need re-doing.
   - **2026-09-23 板式更新**：Part I 整段改用 **两栏布局**，BR 题目全文（含选项）统一 **9.5pt**，行前后各 **3pt**，行间距 **1.2 倍**；每题之后空两行；每 2 题后显式 `<w:br w:type="column"/>`，过长题可独占一列。具体实现细节以 `references/output-format.md` §1 / §2 / §3.2 / §5 为准；Part II / III 不受影响。
   - Per-card layout（**全部 9.5pt / space_before 3pt / space_after 3pt / line_spacing 1.2 倍**）：
     - Card header: `<Category> · Q{n} · {type}` — Arial **9.5pt** bold (Category is the 题目 classification like `Flaw` / `Method`, NOT the docx scope name).
     - stimulus block (verbatim, Times New Roman **9.5pt**),
     - `Question {n}` line (Times New Roman **9.5pt** bold),
     - stem (Times New Roman **9.5pt** bold),
     - options A–E (Arial **9.5pt** bold for letter, Times New Roman **9.5pt** regular for body).
   - **Section 0 = 两栏** (`<w:cols w:num="2" w:space="720" w:equalWidth="1"/>`)；Part II / III 恢复单栏。
   - **题末留白 + 列断**：每张卡片写完后追加 2 个空段（`<w:p>` 内容空字符串，继承 9.5pt / 1.2 / 3pt）；每 2 题后在第 2 个空段里嵌入 `<w:br w:type="column"/>`，下一题进入新列。
   - **过长单题**：若单题渲染后估计超过单列容量（建议阈值 > 50 行 或 > 1500 字符，可在 builder 实测后微调），该题单独占一列，写完后追加 2 个空段 + column break，下一题进入新列，不凑满 2 题再换栏。
   - **No answers, no hints, no BR 自答表 by default.** The speed-table in
     Part II serves as the answer key for these cards.
   - **opt-in** BR 自答表 with three rows (我的答案 / 信心 / BR self) — only
     emitted when the build environment has `BR_SELF_ANSWER_TABLE=1`.
     When the env var is unset or `0`, the table is skipped entirely so the
     user can do a clean Blind Review pass without seeing their previous
     answer scaffolding.

2. **Part II — Answer speed-table + per-question analysis**:
   - 答案速览表 with columns 题号 / Day (=Category) / 题型 / 正确答案 / 你的答案
     / 错因标签 / 核查状态 (13 行 × 7 列).
   - For each wrong question, eight-section analysis: ① 题型识别 → ② 任务翻译
     → ③ stimulus 拆解 / 条件关系 → ④ BR 预判 → ⑤ 正确答案为何对 →
     `核查：✓verified` + `来源：...` 行 → ⑥ 你实际所选为何有吸引力又为何不对
     → ⑦ 其余选项排除 → ⑧ 可迁移 Takeaway.
   - Tag `✓verified` (web-confirmed via lsatlab / 7Sage / LSAT Hacks /
     PowerScore Forum / Apollo / TestMaxPrep against the correct stimulus) or
     `~` (best-guess mirror of a structurally identical Cambridge LR item) or
     `?` (unconfirmed).

3. **Part III — Strength/weakness report**:
   - 题型分布表 (4×2) + 错选字母分布表 (6×2) + 错因标签频次表 (5×2).
   - 4–6 条具体劣势（表征 → 涉及错题 → 训练动作）.
   - 7 日优先级训练清单 (7×1 表). Uses `[Y 灯]` / `[黄]` / `[绿]` TEXT prefix —
     **no colored text** per `AGENTS.md` 红线.
   - See `references/weakness-mapping.md` for the four底层能力 buckets.

4. **来源说明**: NOT a separate page. Source URLs are embedded inline at the
   end of each question's ⑤ section as `来源：lsatlab PT... + 7sage ...`. The
   user-modified 2026-09-19 v1 explicitly dropped the standalone 来源说明 page;
   `references/output-format.md` codifies this.

## Hard Rules

1. **Never** leave helper / build scripts in the project root. Put them
   under `/Users/log/.cache/lsat_workbook/` or `/Users/log/.cache/lsat_review/`.
2. **Never** put correct answers, hints, or analysis prose in Part I. Treat
   `正确答案`, `可迁移 Takeaway`, `答案速览`, `题型识别`, `BR 预判` as
   forbidden tokens when scanning Part I content.
3. **Never** include the BR self-answer table (`我的答案` / `信心` / `BR self`)
   in Part I unless the build environment exports `BR_SELF_ANSWER_TABLE=1`.
   Default is "off" — the table is only added when the user explicitly opts
   in for that build. Day 1 v1 kept the table because the user did not
   request removal on that file; every workbook shipped after the 2025-09
   preference update defaults to "no table".
4. **Never** rebuild, rename, or modify any already-delivered DOCX in
   `/Users/log/LSAT_LR_*_Blind_Review_解析_v*.docx`. The 9 known files are
   frozen deliverables. If the user wants the BR self-answer table removed
   from one of them, run `scripts/strip_self_answer_table.py <path>` to
   produce `<path>.nostable.docx`; do not overwrite the original. The
   builder must refuse to emit a path that collides with a known deliverable.
5. **Always** verify every "correct answer" letter via `WebSearch` before
   delivery. Tag `✓verified` only when ≥ 1 independent prep page confirms
   the answer against the **correct stimulus** (the same Q-number the user
   listed); otherwise `~` (structural mirror) or `?` (unconfirmed). Do not
   overclaim: on Day 2+3 v3 only 13 of 34 wrong questions had public prep
   confirmation — the remaining 21 were `~`, not `✓verified`.
6. **Always** keep the original English stimulus, stem, and option wording
   verbatim. Do not paraphrase the English.
7. **Always** file-name the deliverable with the user-preferred version
   suffix: `LSAT_LR_<scope>_Blind_Review_解析_v{n}.docx` in the project root
   (`/Users/log/`). `<scope>` examples: `Day1`, `Day2_Day3`,
   `Principle_Identify_Section3`, `PT107_Section1_Section3`,
   `PT108_Section2`, `PT109_Section1`, `PT109_Section3`, `PT109_Section4`,
   `跨Workbook_错题优劣势分析报告`.
8. **Always** include a verification harness (`verify_<scope>.py`) and run
   it; print the pass output before claiming the work is done.
9. **Always** place this hard rule at the top of any prompt to a coder /
   generator subagent: "Strictly use the user's Q-numbers as the PDF
   Q-numbers. Each Q-body (stimulus + stem + A–E) must be read verbatim
   from the pre-extracted JSON. Do NOT cross-match by content keywords."
10. Page footer must carry `PAGE` / `NUMPAGES` field codes; correct answers
    in Part II rendered in **bold black with NO shading** (per `AGENTS.md`
    红线 — user `AGENTS.md` forbids table cell shading; this overrides the
    prior `#DCE6F1` default); CJK in 宋体 / 仿宋 / 楷体 per `AGENTS.md`
    (English prose **Times New Roman**, English titles **Arial** — 2026-09
    user override of the prior Latin Aptos + CJK YaHei default).
    **See `references/output-format.md` for the canonical font / size /
    spacing / table-style spec.**
11. **Never** map a user's wrong-question number to a different Q-number by
    content-keyword matching. If a Q-number is missing from the PDF, STOP
    and ask the user before proceeding. This is the Day 2+3 v2 failure mode.

## Verification (mandatory before delivery)

Run the per-scope harness and assert all of:

1. File readable with `python-docx`.
2. All question IDs appear in both Part I and Part II.
3. Answer speed-table has the expected number of rows; every
   (题号, 正确答案, 你的答案) triple matches the user's input AND the
   verified-correct answer from web search.
4. Part I contains zero `正确答案` / `可迁移 Takeaway` / `答案速览` /
   `题型识别` / `BR 预判` markers.
5. Critical explanation phrases for the highest-leverage questions appear
   verbatim in Part II (e.g. Day 1 Q10 / Q32 / Q40, Day 2 Q26 / Q31 / Q38).
6. Footer XML contains `PAGE` and `NUMPAGES` field codes.
7. `textutil -convert txt -stdout <file>` succeeds; `unzip -t <file>`
   reports no errors.
8. **Stimulus verbatim sampling** (prevents the Day 2+3 v2 content mismatch
   from passing structural checks): for each user-listed Q, assert that an
   identifying keyword from the expected stimulus is present in Part I.
   Pick 3–5 distinct anchor keywords spread across the question set.
   Examples for Day 2+3: Q3 must contain "How do the airlines expect to
   prevent", Q10 must contain "privatization", Q17 must contain "Danaxil",
   Q26 must contain "Psychotherapy has been described", Q7 (Day 3) must
   contain "Golden Lake Development", Q33 (Day 3) must contain "modern
   centuries". For each new workbook, pick anchor keywords that uniquely
   identify the **intended** question.
9. **BR self-answer table opt-in check** (NEW): if the environment did not
   export `BR_SELF_ANSWER_TABLE=1`, assert no `<w:tbl>` in Part I contains
   the strings `我的答案` / `信心` / `BR self`. If the env var was set,
   assert exactly one such table per question card.

**Independent spot-check before declaring done**: after the harness passes,
manually read 2–3 question cards from Part I and confirm the stimulus is the
question the user actually meant. Do not rely solely on the harness — the
Day 2+3 v2 file passed every structural check while being entirely
mis-mapped.

Full harness layout and per-workbook overrides:
`references/verification-checklist.md`.

## Weakness Mapping (Part III)

Tag every wrong question with one of four 底层能力 buckets and surface them
in the report:

| Bucket | Common symptoms | Example Day-2+3 questions |
|---|---|---|
| 条件逻辑 (Assumption / SA bridge) | NA↔SA 方向说反；跨物种 / 跨领域外推 | Q3、Q10、Q12、Q16 |
| 范围控制 (MBT quantifier handling) | virtually / almost / "no … more quickly" 被升级 | Q14、Q17 |
| 方法识别 (Method / EXCEPT) | 不正向归纳；dismiss vs discredit 混淆；挑战方式类型误判 | Q13、Q32、Q33、Q34、Q36、Q37 |
| 原则匹配 (Principle Apply / Identify) | 双分支只匹配一支；只在意图忽略实际 / 可预见伤害 | Q35、Q38、Q39 |

Also report the user's wrong-letter distribution (most-mistaken letter =
highest remediation priority). Full bucket catalog and remediation actions:
`references/weakness-mapping.md`.

## Recovery matrix when state goes missing

| Lost | Still have | Action |
|---|---|---|
| `/Users/log/.cache/lsat_workbook/build_<scope>.py` | nothing | Read `references/bundle-scripts.md` to reconstruct from the spec, OR escalate — the cache scripts are the canonical builders. |
| The source PDF | `/Users/log/LSAT_LR_<scope>_Blind_Review_解析_v<n>.docx` | **STOP — do not rebuild.** The deliverable is the deliverable. The script-side deletion of `<w:tbl>` elements that contain `我的答案` is acceptable and reversible only by re-running the build script. Use `scripts/strip_self_answer_table.py` instead. |
| Both builder and PDF | the already-delivered DOCX | Same as above — the deliverable is the source of truth. Do not regenerate Part I unless the user explicitly asks. |
| The user's wrong-question list | the DOCX | Read the 答案速览表 from Part II to recover (题号, 你的答案) pairs; cross-check with the verified-correct column to confirm what the user originally got wrong. |

## Real-World Impact

The 9 already-delivered DOCX files (all frozen — do not rebuild):

- `/Users/log/LSAT_LR_Day1_Blind_Review_解析_v1.docx` — 10 wrong questions,
  built and verified, kept the BR self-answer table because the preference
  predated the 2025-09 opt-in default change. To remove the table now, run
  `scripts/strip_self_answer_table.py` on this file.
- `/Users/log/LSAT_LR_Day2_Day3_Blind_Review_解析_v2.docx` —
  **mis-mapped, kept as a cautionary example.** Coder agent cross-matched
  Q-numbers by content keywords; user opened the first 3 cards and reported
  none were their real wrong questions. Backed up as `.bak2`. The `.docx`
  in `/Users/log/` is the broken one — `textutil` and the harness both
  passed but the content is wrong.
- `/Users/log/LSAT_LR_Day2_Day3_Blind_Review_解析_v3.docx` —
  **current correct version.** Strict PDF Q-number mapping, every Q-body
  verbatim from pre-extracted JSON, 13/34 answers `✓verified`, 21/34 tagged
  `~` (no public prep confirmation — do not promote them to `✓verified`).
  Harness includes stimulus verbatim sampling plus independent spot-check.
- `/Users/log/LSAT_LR_Principle_Identify_Section3_Blind_Review_解析_v1.docx`
- `/Users/log/LSAT_LR_PT107_Section1_Section3_Blind_Review_解析_v1.docx`
- `/Users/log/LSAT_LR_PT108_Section2_Blind_Review_解析_v1.docx`
- `/Users/log/LSAT_LR_PT109_Section1_Blind_Review_解析_v1.docx`
- `/Users/log/LSAT_LR_PT109_Section3_Blind_Review_解析_v1.docx`
- `/Users/log/LSAT_LR_PT109_Section4_Blind_Review_解析_v1.docx`
- `/Users/log/LSAT_LR_跨Workbook_错题优劣势分析报告_v1.docx`

Lesson learned (full case study in `references/mistakes-history.md`):
every future workbook task must run the "PDF Q-Number Extraction Protocol"
before any code is written, must mark `✓verified` only when ≥ 1 public
prep page confirms the answer against the correct stimulus, and must
default the BR self-answer table to OFF unless `BR_SELF_ANSWER_TABLE=1`
is set.

## Common Mistakes

- Leaving `build_*.py` in the project root → pollutes `/Users/log/`
  workspace. Move to `.cache/lsat_workbook/`.
- Putting the answer speed-table or any analysis text in Part I → user can
  no longer do a clean BR.
- Including the BR self-answer table by default → violates the
  `BR_SELF_ANSWER_TABLE=1` opt-in preference. Gate it on the env var; never
  on a code-level constant that defaults to True.
- Overwriting an already-delivered DOCX with a rebuild → violates the
  "frozen deliverables" rule. Use `scripts/strip_self_answer_table.py` to
  produce `<name>.nostable.docx` next to the original instead.
- Marking every question as `✓verified` when only 13 of 34 actually had
  public prep confirmation → dishonest labeling. Use `~` for mirrors and
  `?` for unconfirmed.
- Skipping the verification harness output → cannot truthfully claim
  completion.
- Forgetting to add a page break between Parts → layout looks like one
  continuous stream and confuses readers.
- Treating the user's "错选" letters as ground truth without also listing
  them in Part II — both columns must appear so the user can compare their
  choice vs the correct answer.
- **Cross-matching Q-numbers by content keywords when the user's Q-number
  can't be found in the PDF** (v2 failure mode): the PDF almost certainly
  uses Q-numbers sequentially Q1–Q40 even if page-1 preview only shows one
  Q. Always run the full `re.findall(r"Q(\d+)\.", text)` enumeration first.
- **Trusting "all checks passed" without independent spot-check**
  (v2 failure mode): the harness can pass structurally while the content
  is entirely wrong. After the harness passes, manually read 2–3 question
  cards in Part I and confirm the stimulus matches the user's intended
  question.
- **Marking answers as "已联网核对" without confirming the核对对象 is the
  correct stimulus** (v2 failure mode): if the Q-number mapping is wrong,
  every "verified" label is misleading. Verify Q-mapping first, then
  verify answers.
- **Letting the coder agent improvise when uncertain** (v2 failure mode):
  if any prompt to a generator agent is ambiguous about Q-mapping, the
  agent will fill the gap by content-matching. State the hard rule
  explicitly: "Use PDF Q-numbers as Q-numbers. Do not cross-match by
  content."
- **Failing to back up a wrong deliverable before rebuilding** (data-loss
  risk): when replacing a known-bad version, copy the old file to
  `<name>.bak2` (or `.bakN`) first so the user can diff if needed.
- **Defaulting the BR self-answer table to True in a generator prompt**
  (post-2025-09 regression risk): if a downstream coder agent is told to
  "keep the table from Day 1 v1" without also being told about the opt-in
  env var, it will silently re-introduce the table on every new workbook.
  Always include both the preference statement and the env var name.

## Related Skills

- **→ `lsat-pdf-to-section-docx`** — Route here when the source material is an image-only Cambridge LSAT category PDF (cover labeled "Cambridge LSAT / <Category> / N Questions"). This skill transcribes to a Weaken-template `.docx` (two questions per page + answer-key tail), then `lsat-blind-review` or `lsat-prep-tutor` can take over.
- **→ `lsat-prep-tutor`** — Route here for in-session single-question 7Sage-style讲解 (modes A/B/C/D in that skill). Use when the user has a question in hand and wants the analysis now, not a workbook.
- **↔ `lsat-blind-review`** — Default entry point for multi-question BR workbooks. Produces `.docx` (Part I 题目卡 + Part II 八段式 + Part III 劣势报告 + 来源说明).
- **← from `lsat-prep-tutor`** — When the user wants a 7Sage-style analysis baked into a permanent workbook (vs. in-session markdown), route from `lsat-prep-tutor` here.
- **← from `lsat-pdf-to-section-docx`** — When the user finishes a 2-up transcription and then asks for错题分析 or Blind Review on the questions in it, route from `lsat-pdf-to-section-docx` here.