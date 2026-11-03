---
description: Sample inputs and expected outputs for the three lsat-blind-review scripts (verify_workbook.py, grade_verification.py, strip_self_answer_table.py).
---

# Examples

These files show the shape of each script's input/output so future agents and
the user can run them without reading the source.

| File | What it is | Used by |
|---|---|---|
| `meta.json` | Sample workbook-specific data passed to `verify_workbook.py --meta` | `scripts/verify_workbook.py` |
| `truth.json` | Sample authoritative ground truth passed to `grade_verification.py --truth` | `scripts/grade_verification.py` |
| `verify_output.txt` | Expected PASS output for `verify_workbook.py` on a clean workbook | reference only |
| `strip_output.txt` | Expected output for `strip_self_answer_table.py` on the PI S3 v1 workbook | reference only |

## meta.json shape

Minimum required fields: `wrong_qs` (list of Q-numbers as ints). All other
fields are optional but enable stronger checks:

- `user_answers` / `answer_key` — enable speed-table triple matching.
- `anchors` — enable stimulus verbatim anchor sampling (mandatory under
  the skill's "stimulus verbatim sampling" rule).
- `critical_phrases` — high-leverage phrases that MUST appear in the document.
- `forbidden_part1` — tokens that must NOT appear in Part I (default:
  正确答案 / 可迁移 Takeaway / 答案速览).
- `header_pattern` — python format string for per-card headings; default is
  `Q{n}` as substring.
- `speed_table_header` — column names expected in row 0 of the speed-table;
  default is `["题号", "题型", "正确答案", "你的答案"]`.

## truth.json shape

Same fields as meta.json, plus per-question fields under `questions`:

- `answer` — correct letter (web-verified).
- `user_pick` — the user's chosen letter.
- `type` — question type label (Method/EXCEPT, Weaken, …).
- `anchor` — short identifying keyword from the stimulus.
- `critical_phrases` — list of high-leverage phrases for this Q.

`grade_verification.py` produces a 0–100 score across 8 sections
(see `--help` for weights) and exits non-zero if the score is below
`--threshold` (default 90).

## strip_output.txt

Demonstrates the cleanup path for an already-delivered BR workbook. The
script removes every BR self-answer table (header row containing `我的答案`
and `信心`) and the immediately-preceding `【BR 自答】` heading paragraph.
The PI S3 v1 workbook had 17 such tables; stripping them saves ~1.5 KB
while leaving stimulus, analysis, weakness report, and footer untouched.

## Related Skills

- **→ `lsat-pdf-to-section-docx`** — Route here when the source material is an image-only Cambridge LSAT category PDF (cover labeled "Cambridge LSAT / <Category> / N Questions"). This skill transcribes to a Weaken-template `.docx` (two questions per page + answer-key tail), then `lsat-blind-review` or `lsat-prep-tutor` can take over.
- **→ `lsat-prep-tutor`** — Route here for in-session single-question 7Sage-style讲解 (modes A/B/C/D in that skill). Use when the user has a question in hand and wants the analysis now, not a workbook.
- **↔ `lsat-blind-review`** — Default entry point for multi-question BR workbooks. Produces `.docx` (Part I 题目卡 + Part II 八段式 + Part III 劣势报告 + 来源说明).
- **← from `lsat-prep-tutor`** — When the user wants a 7Sage-style analysis baked into a permanent workbook (vs. in-session markdown), route from `lsat-prep-tutor` here.
- **← from `lsat-pdf-to-section-docx`** — When the user finishes a 2-up transcription and then asks for错题分析 or Blind Review on the questions in it, route from `lsat-pdf-to-section-docx` here.