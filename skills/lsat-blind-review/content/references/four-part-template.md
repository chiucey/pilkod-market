---
name: four-part-template
description: Canonical layout and section-by-section spec for the LSAT LR Blind Review four-part Chinese Word workbook (Part I cards · Part II speed table + 8-section analysis · Part III weakness report · source citations). Read before writing or modifying any build_*.py that emits the DOCX.
license: MIT
allowed-tools:
  - Read
metadata:
  derived_from: /Users/log/.cache/lsat_workbook/build_v3.py (the corrected Day 2+Day 3 build that the user accepted as v3)
  evidence_examples:
    - /Users/log/LSAT_LR_Day1_Blind_Review_解析_v1.docx
    - /Users/log/LSAT_LR_Day2_Day3_Blind_Review_解析_v3.docx
    - /Users/log/LSAT_LR_PT107_Section1_Section3_Blind_Review_解析_v1.docx
    - /Users/log/LSAT_LR_PT109_Section1_Blind_Review_解析_v1.docx
---

# Four-part workbook template

> **2026-09-19 status: SUPERSEDED for typography / colors.** The canonical
> output format is now `references/output-format.md`, reverse-engineered
> from the user-edited `LSAT_LR_Flaw_Q201-240_Blind_Review_解析_v1.docx`
> (127,536 bytes). This file remains as historical reference and a structural
> overview (the four-part layout, the forbidden-tokens list, the verification
> harness layout). For all font / size / spacing / table-style decisions,
> build scripts MUST consult `references/output-format.md` instead.
>
> **2026-09-23 update**: Part I 由"单栏 12pt / 1.15 倍"切到"两栏 9.5pt / 1.2 倍 / 显式 column break"。本文件保留 2026-09-19 之前"单栏 12pt / Card header 13pt blue / Day grouping"等旧板式，仅作历史参考；2026-09-23 起的 workbook 全部走 `references/output-format.md`。
>
> Key changes introduced by `output-format.md`:
>
> - 字体：英文正文 **Times New Roman**；英文标题 **Arial**；CJK 宋体 / 仿宋 / 楷体
> - 字号：标题 16pt（Arial bold）；Part heading 16pt；Card header 12pt；stimulus 12pt；分析 prose 10.5pt
> - 表格：白底黑色细线，**无底色**；正确项仅加粗区分
> - 不再有 cover 封面、无 Part 概览、无来源说明单独成页（来源嵌入每题 ⑤ 段后）
> - Card header 格式：`<Category> · Q{n} · {type}`（Category = 题目分类，不是 scope 名）

This document is the canonical layout spec for any `LSAT_LR_*_Blind_Review_解析_v{n}.docx` deliverable produced by this skill. Every build script under `/Users/log/.cache/lsat_workbook/build_*.py` must conform to it. The structural pattern is the corrected Day 2+Day 3 v3 workbook — every later build is a variation of that file.

## Document-level settings (for typography / colors see `output-format.md` §1)

These apply to the whole DOCX and must be set by the build script, not by a user hand-edit:

| Setting | Value | Why |
|---|---|---|
| Page size | A4 (210 × 297 mm) | Day 2+Day 3 v3 was A4; the 9 already-delivered files all use A4. |
| Margins | top/bottom 2.5 cm; left/right 2.5 cm | Matches v3. Tight enough to fit stimulus + stem + A–E on one card without overflow; loose enough not to clip Latin glyphs. |
| Default style font | **See `references/output-format.md` §2** for the canonical font table. | The table below is the **pre-2026-09-19 default** kept for historical reference. **Do NOT use these values in new builds** — instead read `output-format.md`. |
| English-only runs (stimulus, options, speed-table body) | Times New Roman 12pt (per `output-format.md`) | Was 11pt in the pre-2026-09 default. |
| English title runs (Part headings, card headers, section headings) | Arial 12-16pt (per `output-format.md`) | Was Arial 11pt+ in pre-2026-09 default. |
| CJK-only runs (Chinese analysis, body, 引文) | 仿宋 12pt body / 宋体 14pt bold headings / 楷体 11pt 引文 (per `AGENTS.md`) | Unchanged. |
| Header | None (clean — no running header band) | v3 has no running header; keeps Part I cards visually quiet. |
| Footer | `Page <PAGE> of <NUMPAGES>` (centered, Arial 9pt black) | Required for the `PAGE`/`NUMPAGES` field-code check in the harness. The pre-2026-09 default had a `<scope tagline>` appended — the user's 2026-09-19 v1 dropped this and uses just `Page N / M`. |
| Page break between Parts | Yes — hard page break before Part I, Part II, Part III, and 来源说明 | Without this, the four sections render as one continuous stream and confuse readers (logged in Common Mistakes). |
| Page break between cards | No | Cards flow; the v3 cards take a full page each but no explicit `pageBreakBefore` is set on the card header. A blank spacer paragraph is enough. |

## Cover page — REMOVED in 2026-09-19 v1

The pre-2026-09-19 workbooks (Day1, Day2_Day3 v3, Principle_Identify, PT107/PT108/PT109, 跨Workbook_报告) all used a multi-line cover page (Title / Subtitle / Version / Meta / Part 概览 / 使用说明). The user-edited 2026-09-19 v1 explicitly **dropped the cover page** and replaced it with a single title line at paragraph 0:

```
LSAT LR · <Scope> · Blind Review Workbook v{n}
```

Format: Arial 16pt bold black, left-aligned, no centering, no subtitle, no version line, no Part 概览, no 使用说明. Build scripts MUST follow this format. See `references/output-format.md` §3.1.

The cover-page content below is preserved for historical reference and for understanding the pre-2026-09-19 workbooks; **do NOT emit a cover page in new builds.**
6. **使用说明** (14pt bold heading in `0x1F4E79`, then 5 numbered lines 11pt): how to use the workbook in the intended order.

End the cover with a hard page break before Part I.

## Part I — 盲测卡片 (question cards)

The whole point of Part I is to be answer-free so the user can do a real Blind Review. The forbidden-tokens list for Part I is enforced by the verification harness and by the build script's `build_part_i()` helper:

- `正确答案`, `答案速览`, `可迁移 Takeaway`, `错因`, `7Sage`, `验证` — none of these tokens may appear in Part I content. Treat them as a denylist when scanning the assembled DOCX.

### Per-card layout

For each question the user listed as wrong, in ascending Q-number order within each Day, render this exact sequence:

```
<card-header>  Day {day} · Q{n} · {TypeLabel}              # 13pt bold, color 0x1F4E79
                space_before 10pt, space_after 4pt

<stimulus>      For each paragraph in the source stimulus:
                  one paragraph; 11pt; left_indent 0.3cm; space_after 2pt
                verbatim — no paraphrase, no summary

<stem>          One paragraph; 11pt bold; left_indent 0.3cm
                space_before 4pt, space_after 4pt
                verbatim — do not strip question mark, do not split "?" from rest

<options A-E>   For each of A B C D E in order:
                  one paragraph "{letter}. {option_body}"
                  {letter}. in 11pt bold; option body in 11pt regular
                  left_indent 0.6cm; space_after 2pt
                verbatim — preserve curly quotes, em-dashes, italics on proper nouns
                if an option is missing in the source, emit a one-line "—" placeholder
                  and flag in build log; do NOT silently invent option text

<spacer>        One empty paragraph; space_after 8pt
```

The `TypeLabel` comes from the `TYPE_TAG_MAP` in `build_v3.py` (Assumption / MBT / Flaw / Method / Principle). If the PDF's bracket label is something else (e.g. `Strengthen`, `Resolve`, `Parallel`), pass it through verbatim.

### BR self-answer table — opt-in only

**Default: NO BR self-answer table in Part I.** The user explicitly does not want a `我的答案`/`信心` table in the question cards by default — see the AGENTS.md file naming preference and the 2025-09 history where the Day 2+Day 3 workbook shipped without one and that was the right call.

If a build script wants to include one, it MUST be gated on the environment variable `BR_SELF_ANSWER_TABLE=1`. Treat this as a hard contract:

| `BR_SELF_ANSWER_TABLE` | Behavior |
|---|---|
| unset / `0` / `false` / empty | No self-answer table. The card ends with the spacer paragraph only. |
| `1` / `true` / `yes` | Append a 2-row × 5-col table at the end of each card, before the spacer. Header row bold; body row blank cells for the user to fill in. Columns: `我的答案` · `信心(1-5)` · `BR预判方向` · `用时(秒)` · `备注`. |

Scripts that emit the table must read the env var at the top of the build, e.g.:

```python
import os
EMIT_SELF_ANSWER_TABLE = os.environ.get("BR_SELF_ANSWER_TABLE", "").lower() in ("1", "true", "yes")
```

And gate the per-card table emission behind that flag. Do not check the env var inside the loop on every iteration — read once.

### Day grouping in Part I

Group cards by Day (or by section for PT-based scopes). Render a Day heading (`Day N · Blind Review Cards`, 16pt bold, `0x1F4E79`) before each group's first card. Use `space_before 10pt` on the Day heading. Do not add a page break between Days — the cards already take enough vertical space that consecutive cards on different Days flow naturally.

For PT-based scopes (e.g. `PT107 Section 1 + Section 3`), use the section number as the grouping key instead of Day: `Section {N} · Blind Review Cards`.

### What Part I must NOT contain

In addition to the forbidden tokens above, Part I must not contain:

- `BR 预判` direction hints (those belong in Part II §④)
- Anything from `analyses.json` or any analysis prose
- Cross-references to other questions ("see Q17 analysis")
- The Day-wide total of wrong questions, or any heading that says "wrong" or "错"

The harness scans the Part I paragraph stream for these patterns and fails the build if any are found.

## Part II — 答案速览表 + 8节解析

Always starts on a new page (the cover's last action is the Part I page break; Part II begins with its own page break). Order: speed table first, then per-question analyses.

### 2.1 Speed table (答案速览表)

A 6-column × (1 + N) row table, in this exact order:

| Day | Q | 题型 | 正确答案 | 你的答案 | 错因标签 |
|---|---|---|---|---|---|
| (header row, 10pt bold, white text on `0x1F4E79` shading) |

- Day and Q are the integer values from the user's wrong-question list.
- 题型 is the `type` field from `analyses.json` (e.g. `Assumption`).
- 正确答案 is the verified-correct letter; the cell is **bold 10pt on `0xDCE6F1` shading**. This is the only cell that gets shading on the speed table.
- 你的答案 is the letter the user picked.
- 错因标签 is the short tag from `analyses.json["wrong_tag"]` (e.g. `方向反`, `NA 强度过强`).

The rows must be sorted by `(Day, Q)` ascending — Day 1 first within its group, then Day 2, etc. Combined-Day workbooks list Day 2 first, then Day 3 (matches v3).

### 2.2 Per-question analysis (8节解析)

For each wrong question, in the same `(Day, Q)` ascending order as the speed table, render this exact structure:

1. **Heading line** (13pt bold, color `0x1F4E79`):
   `Day {day} · Q{n} · {TypeLabel}    {verification_tag}`

   Where `verification_tag` is one of:
   - `✓verified` — at least one independent public prep page (7Sage / LSAT Lab / LSAT Hacks / PowerScore Forum) confirms the answer against the **correct stimulus** (the same Q-number the user listed).
   - `~` — best-guess mirror of a structurally identical Cambridge LR item, no independent confirmation.
   - `?` — unconfirmed; flagged for the user to verify manually.

   Do not invent `✓verified` tags. Day 2+Day 3 v3 had 13 of 34 with `✓verified` and 21 with `~`. Reporting `✓verified` on a question where no independent source confirms the letter is dishonest labeling.

2. **Info line** (10pt regular): `题型：{type}    你的答案：{user_ans}    正确答案：{correct}    错因标签：{tag}`. The 正确答案 token is 10pt bold in `0xC0392B` (red) so it stands out from the surrounding gray.

3. **Eight sections** (each section one paragraph, 10.5pt regular, left_indent 0.3cm, space_after 3pt):

   | § | Section heading | What goes here |
   |---|---|---|
   | ① | 题型识别 | Identify the question type in 1 sentence; call out the LSAT sub-skill (NA / SA / MBT / Flaw / Method / Principle Identify / etc.). |
   | ② | 任务翻译 | Translate the stem into Chinese; state the actual task (prove / weaken / find flaw / identify principle / etc.). |
   | ③ | stimulus 拆解 / 条件关系 | List the premise(s) and conclusion(s); note any conditional logic, quantifiers, or scope-shifts. |
   | ④ | BR 预判 | The predicted direction of the answer BEFORE looking at the options. What must the correct answer do, in 1–2 sentences? |
   | ⑤ | 正确答案为何对 | Why the verified-correct letter satisfies ④. Reference the stimulus directly. |
   | ⑥ | 你实际所选为何有吸引力又为何不对 | Why the user's pick was seductive (the cognitive trap) AND why it fails the actual task. This is the highest-leverage section for learning. |
   | ⑦ | 其余选项排除 | Quick elimination of A, C, D (or whichever were not the correct answer or the user's pick). One line each. |
   | ⑧ | 可迁移 Takeaway + 原题选项速览 | One transferable lesson (1–2 sentences) + a 5-line speed-read of the options with ✓/✗ markers. |

4. **Options speed-read block** (10.5pt, bold for the mark, left_indent 0.4cm): one line per option, format `  {letter} {mark} — {one-line note}`. `mark` is `✓` for correct (red `0xC0392B`), `你选` for the user's pick (must be a different letter from correct, otherwise the question shouldn't be in the wrong-Q list), `✗` for the rest. The note for `你选` lines is colored `0x804000` (amber) so the eye finds the trap instantly; other notes are `0x333333`.

After the options block, one empty spacer paragraph (space_after 6pt). Then the next question's heading — no page break between questions in Part II.

## Part III — 全卷错题分布与劣势报告

Always starts on a new page. Five sub-sections, in this exact order:

### 3.1 ① 题型分布（按错题数降序）

A 3-column × (1 + |unique_types|) row table:

| 题型 | 错题数 | 占比 |
|---|---|---|
| (header, 10pt bold white on `0x1F4E79`) |

Sort rows by `错题数` descending; ties broken by 题型 alphabetically. `占比` is `{count}/{total_err}*100:.1f}%`.

### 3.2 ② 错选字母分布（你实际所选）

Same 3-column shape, columns `错选字母 · 次数 · 占比`. Always show all 5 letters A–E, even if a letter has 0 occurrences (the user wants to see "A: 0" not "no A row"). Sort by 次数 descending, ties by letter ascending.

This is the table that surfaces "结尾偏好" — the Day 2+Day 3 user had B + D = 9 of 34 picks and the v3 劣势 6 calls this out as a training target.

### 3.3 ③ 错因标签频次表

Same 3-column shape, columns `错因标签 · 次数 · 占比`. Sort by 次数 descending; show all tags that appear in `analyses.json["wrong_tag"]` (don't filter out rare tags).

### 3.4 ④ 4–6 条具体劣势（表征 → 涉及错题 → 训练动作）

This is the prose analysis section. Each 劣势 gets three paragraphs:

1. **Title** (11.5pt bold, red `0xC0392B`): `劣势 {k}：{one-line summary}`. Space_before 6pt.
2. **Evidence** (10.5pt, label "  · 表征与证据：" in bold, then the evidence string): list the specific questions that demonstrate this weakness, with the user's pick → correct pair shown for each. Left_indent 0.4cm.
3. **Action** (10.5pt, label "  · 训练动作：" in bold, then the action string): concrete training steps (what 题库, what to focus on, what time pressure). Left_indent 0.4cm.

The Day 2+Day 3 v3 ships exactly 6 劣势s; that count (4–6) is the project's convention. Do not invent more than 6; do not produce fewer than 4 unless the user has < 4 wrong questions total.

### 3.5 ⑤ 7 日优先级训练清单

A 3-column × 8 row table:

| 日期 | 状态 | 训练内容 |
|---|---|---|
| (header, 10pt bold white on `0x1F4E79`) |
| Day 1 | 黄灯 / 红灯 / 绿灯 | <one-line training task> |
| ... |
| Day 7 | ... | ... |

State color rules (use the same RGB triplets as v3):

- `红灯` → `0xC0392B` (red)
- `黄灯` → `0xC89010` (amber)
- `绿灯` → `0x38761D` (green)

The 7-day plan is a `建议`, not a contract. Each day's 训练内容 must reference at least one specific question from the user's wrong-Q list, plus a 7Sage 题库 count (e.g. "做 7Sage Method 题库 20 题").

## 来源说明

Final section, always starts on a new page. Header `附：来源说明` (14pt bold, `0x1F4E79`). Then 5 numbered lines (10.5pt regular, space_after 3pt):

1. English stimulus / stem / A–E come from the user-provided Cambridge LR Vol.1 (or whatever scope) PDF. No rewrite, no abbreviation.
2. Answers and analysis思路 were cross-verified against the following public prep pages (each wrong Q has at least one independent source):
   - `https://7sage.com/lsat-practice/`
   - `https://lsatlab.com/`
   - `https://lsathacks.com/`
   - `https://forum.powerscore.com/`
   - `https://cracklsat.com/`
3. All 8-section Chinese analysis prose in this workbook is original writing based on the cited public sources and the question's argument structure; no third-party explanation prose was copied verbatim.
4. Verification tally: state the count of `✓verified` vs `~` vs `?` honestly. The Day 2+Day 3 v3 tally was 13 / 21 / 0. Do not round up `~` to `✓verified` even if the answer happens to match a known correct answer key — the verification tag refers to the cross-check process, not the answer's correctness.
5. The 错因标签 taxonomy is this workbook's own training-purpose classification; it is not an official attribution of any question.

## Typography rules summary

These apply across all four parts:

| Element | Latin font | CJK font | Size | Weight | Color |
|---|---|---|---|---|---|
| Cover title | Arial | 宋体 | 26pt | bold | black |
| Cover subtitle | Arial | 宋体 | 18pt | bold | black |
| Version line | Arial | 宋体 | 14pt | bold | `0x1F4E79` |
| Part heading (`Part I/II/III · ...`) | Arial | 宋体 | 20pt | bold | black |
| Section heading (`① 题型分布` etc.) | Arial | 宋体 | 14pt | bold | `0x1F4E79` |
| Day heading (`Day 2 · Blind Review Cards`) | Arial | 宋体 | 16pt | bold | `0x1F4E79` |
| Card header (`Day N · Q{n} · Type`) | Arial | 宋体 | 13pt | bold | `0x1F4E79` |
| Stimulus paragraph | Times New Roman | 仿宋 | 11pt | regular | black |
| Stem | Times New Roman | 宋体 | 11pt | bold | black |
| Option letter (`A. ` etc.) | Times New Roman | 宋体 | 11pt | bold | black |
| Option body | Times New Roman | 仿宋 | 11pt | regular | black |
| Info line (Part II) | Times New Roman | 仿宋 | 10pt | regular | black, with 正确答案 in **bold black** (no shading, no red — `AGENTS.md` 红线) |
| 8-section analysis prose | Times New Roman | 仿宋 | 10.5pt | regular | black |
| Options speed-read `✓` mark | Times New Roman | 宋体 | 10.5pt | bold | black bold ✓ (no red — `AGENTS.md` 红线) |
| Options speed-read 你选 line | Times New Roman | 仿宋 | 10.5pt | regular | black |
| 劣势 title | Arial | 宋体 | 11.5pt | bold | `0xC0392B` (保留用于警示标签 — 可选；如要严格执行 `AGENTS.md` 全部无色，去掉此色) |
| 劣势 evidence / action body | Times New Roman | 仿宋 | 10.5pt | regular | black |
| Footer | Times New Roman | 宋体 | 9pt | regular | black |

Font rationale (2026-09 override): 英文正文 Times New Roman（serif，兼容 LR 印刷风格），英文标题 Arial（sans-serif，对应 Part / Card 标题的层级强调）。CJK 部分按 `AGENTS.md`：宋体标题 / 仿宋正文 / 楷体引文。本表取代了此前「Latin Aptos + CJK YaHei」的默认配置，9 份冻结 docx 不追溯修改，新 workbook 全部按本表执行。

Color rationale: `0x1F4E79`（deep blue）保留为导航色；红色 `0xC0392B` / 琥珀色 `0x804000` / 浅蓝 `0xDCE6F1` 等强调色按 `AGENTS.md` 红线（Word 表格样式偏好）一律**禁用**——正确项仅以加粗区分，无底色。7 日优先级训练清单的 Y 灯 / 黄 / 绿三色亦统一改为纯文字前缀（`[Y 灯]` / `[黄]` / `[绿]`），不引入颜色差异。

## Sample card schematic

```
Day 2 · Q3 · Assumption                                              ← 16pt bold blue Day heading (Arial)
Day 2 · Q3 · Assumption                                              ← 13pt bold blue card header (Arial)

How do the airlines expect to prevent frequent fliers from           ← 11pt stimulus paragraph (Times New Roman)
plagiarizing the discounts that are offered to those who              ← 11pt stimulus paragraph (Times New Roman)
fly frequently? ...                                                   ← (continue verbatim)

Which one of the following is an assumption required by the          ← 11pt bold stem (Times New Roman)
argument above?

A. Frequent fliers value discounts at least as much as ...            ← 11pt A. bold (Arial) + body regular (Times New Roman)
B. The discounts offered to frequent fliers are not ...               ← 11pt B. bold + body regular
C. ...                                                               ← (etc. through E)

                                                                       ← spacer paragraph
```

After the last card in Day 2's group, the next group's Day heading appears (`Day 2 · Blind Review Cards` for Day 2, then `Day 3 · Blind Review Cards`).

## Verification checklist for any new build

A new workbook is not done until all of the following pass. The harness under `/Users/log/.cache/verify_lsat_*.py` enforces most of these; the rest are eyeball checks.

1. File opens with `python-docx`; `Document(path).paragraphs` returns > 0 paragraphs.
2. Every question ID in the user's wrong-Q list appears in BOTH Part I and Part II.
3. Speed table row count = number of wrong questions + 1 header.
4. Every (Q, 正确答案, 你的答案) triple matches the user's input AND the verified-correct answer from web search.
5. Part I scanned for forbidden tokens (`正确答案`, `答案速览`, `可迁移 Takeaway`, `错因`, `7Sage`, `验证`) — zero matches.
6. Critical explanation phrases for the highest-leverage questions (per Part II) appear verbatim.
7. Footer XML contains `PAGE` and `NUMPAGES` field codes.
8. `textutil -convert txt -stdout <file>` succeeds.
9. `unzip -t <file>` reports no errors.
10. **Stimulus verbatim sampling** — for each wrong Q, pick an identifying anchor keyword from the source stimulus and assert it appears in Part I. For example, Day 2+Day 3 v3 sampled: Q3 = "How do the airlines expect", Q10 = "privatization", Q17 = "Danaxil", Q26 = "Psychotherapy has been described", Day 3 Q7 = "Golden Lake Development", Day 3 Q33 = "modern centuries". For any new workbook, pick 3–5 anchors that uniquely identify the intended questions — these are the canaries that catch the v2-style content-keyword mis-mapping.
11. **Independent spot-check** — after the harness passes, manually open the DOCX in Word/WPS/LibreOffice and read 2–3 question cards in Part I. Confirm the stimulus is the question the user actually meant. The harness can pass structurally while the content is entirely wrong.
12. `BR_SELF_ANSWER_TABLE` opt-in contract: confirm whether the env var was set; confirm the table is present iff the var was `1` / `true` / `yes`. If unset, scan Part I for `我的答案` / `BR 预判` table fragments and assert zero matches.

For items 10–11 specifically, do not rely on the harness's "all checks passed" output alone — that is exactly how the v2 workbook passed Phase 1–6 with the wrong questions in every card.

## What this template does NOT prescribe

- The exact 8-section prose content of a per-question analysis — that comes from `analyses.json` or whatever per-question analysis source the build script uses.
- The exact 错因标签 taxonomy — the build script's `analyses.json` defines the tags; this template only says "use them verbatim, count them in Part III §③".
- The exact 4–6 劣势 list — the build script composes these from the analysis data; this template only says "4–6 of them, each with 表征 → 涉及错题 → 训练动作 structure".
- The 7-day plan's specific dates — this template says "Day 1 through Day 7 with traffic-light status" and references one specific wrong-Q per day. The plan's content is the build script's call.
- Page-level layout decisions beyond the part-level page breaks (e.g. whether to start a card on a new page if the previous one nearly fills a page) — these are at the build script's discretion and not enforced here.

For any layout question not covered above, the canonical reference is `/Users/log/.cache/lsat_workbook/build_v3.py` — its output `/Users/log/LSAT_LR_Day2_Day3_Blind_Review_解析_v3.docx` is the project-accepted v3 and the template above was reverse-engineered from it.

## Related Skills

- **→ `lsat-pdf-to-section-docx`** — Route here when the source material is an image-only Cambridge LSAT category PDF (cover labeled "Cambridge LSAT / <Category> / N Questions"). This skill transcribes to a Weaken-template `.docx` (two questions per page + answer-key tail), then `lsat-blind-review` or `lsat-prep-tutor` can take over.
- **→ `lsat-prep-tutor`** — Route here for in-session single-question 7Sage-style讲解 (modes A/B/C/D in that skill). Use when the user has a question in hand and wants the analysis now, not a workbook.
- **↔ `lsat-blind-review`** — Default entry point for multi-question BR workbooks. Produces `.docx` (Part I 题目卡 + Part II 八段式 + Part III 劣势报告 + 来源说明).
- **← from `lsat-prep-tutor`** — When the user wants a 7Sage-style analysis baked into a permanent workbook (vs. in-session markdown), route from `lsat-prep-tutor` here.
- **← from `lsat-pdf-to-section-docx`** — When the user finishes a 2-up transcription and then asks for错题分析 or Blind Review on the questions in it, route from `lsat-pdf-to-section-docx` here.
