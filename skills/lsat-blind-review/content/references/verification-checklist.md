# Verification checklist — the runnable gate for every Blind Review workbook

This is the **executable** companion to the SKILL.md "Verification (mandatory
before delivery)" block. SKILL.md names the eight required checks; this file
spells out the exact assertions, the exact code, and the exact failure modes
that motivated each one. A workbook only counts as delivered after every check
listed here has printed `PASS` **and** a human has done the independent
spot-check at the bottom of this file.

> **2026-09-19 update**: The output format spec moved to
> `references/output-format.md` (reverse-engineered from the user-edited
> `LSAT_LR_Flaw_Q201-240_Blind_Review_解析_v1.docx`). Any verification check
> that asserts a specific font / size / color must read that file rather
> than the historical defaults recorded here. The preflight PDF Q-number
> extraction protocol (below) is unchanged.

The 2025-09 Day 2+3 v2 workbook passed six of these checks at the structural
level and still shipped entirely mis-mapped. That incident is the reason checks
1–2 (PDF Q-number extraction) and check 8 (stimulus verbatim anchors) exist;
skipping either one invites a silent re-run of the same failure.

## 0. The non-negotiable preflight — PDF Q-number extraction

**Run this before writing any other script.** It is the single highest-leverage
safety step in the whole skill. If you skip it, you cannot trust any later
check, because every later check assumes the workbook's Q-numbers match the
PDF's Q-numbers.

```python
from pypdf import PdfReader
import re, json

PDF = "<path to the user-provided LR PDF>"
full = "\n".join((p.extract_text() or "") for p in PdfReader(PDF).pages)

qids = sorted({int(m.group(1))
               for m in re.finditer(r"Q(\d+)\.\s*\[", full)})

USER_QS = [...]  # the list the user gave you (e.g. [3, 7, 10, 26, ...])

missing = sorted(set(USER_QS) - set(qids))
assert not missing, f"STOP. User Q-numbers not in PDF: {missing}"

chunks = re.split(r"(?=Q(\d+)\.\s*\[)", full)
# chunks = ['', '1', '...body...', '2', '...body...', ...]
q_bodies = {int(chunks[i+1]): chunks[i+2] for i in range(0, len(chunks)-1, 3)}

json.dump({"qids": qids, "q_bodies": q_bodies},
          open("/Users/log/.cache/lsat_workbook/q_bodies.json", "w"),
          ensure_ascii=False, indent=2)
```

Hard rules from this step:

1. **Never** infer the numbering scheme from `extract_text()[:120]`. Many PDFs
   present as Q1/Q3/Q5... or skip Q-numbers in the first page's preview, but
   use contiguous Q1..Q40 numbering overall. Only the full enumeration tells.
2. **Never** cross-match a user's Q-number to a "nearby" Q in the PDF by
   content keywords. The user's Q-number **is** the PDF's Q-number. If a
   Q-number is missing from the PDF, stop and ask the user.
3. **Always** save the per-Q body text to JSON (`q_bodies.json`). Downstream
   build and verification scripts read from this file — they do **not** re-open
   the PDF.

If you let a generator subagent skip step 1, expect the v2 failure mode to
recur: every Part I card is the right length, structurally perfect, but
addressing a different question than the user asked about.

## 1. File readable with python-docx

```python
from docx import Document
doc = Document("<deliverable>.docx")
assert len(doc.paragraphs) > 0, "docx is empty"
assert len(doc.sections) > 0, "docx has no sections"
```

Failure = corrupt zip, missing `[Content_Types].xml`, or a half-written file
from a previous crashed build. Re-run the build script with a fresh output
path; never patch a corrupt docx in place.

## 2. All question IDs appear in both Part I and Part II

```python
import re
PART1_TEXT = "\n".join(p.text for p in doc.paragraphs[: split_at_part2(doc)])
PART2_TEXT = "\n".join(p.text for p in doc.paragraphs[split_at_part2(doc):])

for q in USER_QS:
    for section in SECTIONS:
        label = f"{section}·Q{q}"     # or your naming convention
        assert label in PART1_TEXT, f"Part I missing {label}"
        assert label in PART2_TEXT, f"Part II missing {label}"
```

`split_at_part2(doc)` is whatever heuristic you use to find the boundary —
usually the first paragraph whose text equals `"二、"` (the second part
heading) or the first paragraph that contains the speed-table header text.

A Q appearing only in Part I means Part II lost an analysis. A Q appearing
only in Part II means Part I lost a BR card (catastrophic — the user cannot
do a blind review of that question).

## 3. Answer speed-table rows + (题号, 正确答案, 你的答案) triples

Two sub-checks. Pass both.

### 3a. Row count

The speed table must have exactly one row per user-listed Q (including
user-correct ones when you chose to include them). The simplest check is to
count paragraphs whose leading token is the table-row template, or to read
the actual `w:tbl` element count and divide by expected row height. Pick
one approach and keep it consistent across workbooks.

```python
SPEED_TABLE_LABEL = "答案速览表"   # exact heading used in Part II
expected_rows = len(USER_QS)  # or +1 for header row depending on layout
```

### 3b. Triple match

```python
from collections import Counter

# digest.json is the canonical {section: {q: {correct, user_pick, ...}}} built
# from the user's input AND web verification, before workbook construction.
digest = json.load(open("/Users/log/.cache/lsat_workbook/<key>_digest.json"))

for section, qs in digest.items():
    for q, entry in qs.items():
        # locate the row in the speed-table (parse the table or scan Part II)
        row = find_speed_table_row(doc, section, q)
        assert row["correct"] == entry["correct"], \
            f"{section} Q{q}: speed-table correct={row['correct']} ≠ digest={entry['correct']}"
        assert row["user_pick"] == entry["user_pick"], \
            f"{section} Q{q}: speed-table user_pick={row['user_pick']} ≠ digest={entry['user_pick']}"
```

The digest is the **single source of truth** — never let the build script
re-derive the correct answer from any other place. If the build script
re-reads the PDF and gets a different letter, the digest wins and the build
script is wrong (almost always because it picked up the wrong Q-body).

The most common failure here is also the most insidious: the build script
is fed `USER_WRONG = [3, 7, 10, ...]` but `digest` was built against a
mismatched list (Day 1 instead of Day 2). Assert `digest.keys() ==
USER_WRONG_QS` before the loop.

## 4. Part I contains zero forbidden markers

```python
PART1_TEXT = "\n".join(p.text for p in doc.paragraphs[: split_at_part2(doc)])

FORBIDDEN = ["正确答案", "可迁移 Takeaway", "答案速览", "① 题型识别", "① 任务翻译"]
# Adjust FORBIDDEN to whatever tokens would leak analysis content into Part I.
# The list above is the minimum; add more if your analysis uses other
# load-bearing phrases.

for token in FORBIDDEN:
    assert token not in PART1_TEXT, f"Part I leaked forbidden marker: {token!r}"
```

This is a cheap check but it catches a whole class of "I accidentally pasted
the analysis into the question card" bugs. If a build script ever shows up
that emits one of these tokens in Part I, **fix the build script, do not
just delete the token from the docx** — the build will keep emitting it on
the next run.

## 5. Critical explanation phrases appear verbatim in Part II

Pick 3–5 of the highest-leverage wrong questions and assert that the
load-bearing phrase from your analysis JSON shows up in Part II. This is the
"did the writer actually say the thing they were supposed to say" check.

```python
ANCHORS = {
    ("Day 2", 26): "Psychotherapy has been described",
    ("Day 2", 31): "the act of painting",  # whatever the load-bearing phrase is
    # ...
}
PART2_TEXT = "\n".join(p.text for p in doc.paragraphs[split_at_part2(doc):])

for (sec, q), phrase in ANCHORS.items():
    assert phrase in PART2_TEXT, f"Part II missing phrase for {sec} Q{q}: {phrase!r}"
```

Pick phrases that, if they were paraphrased or dropped, would render the
analysis useless. Do not pick phrases that also appear in Part I (that would
make the check pass for the wrong reason).

## 6. Footer XML contains PAGE and NUMPAGES field codes

```python
import zipfile
import re

with zipfile.ZipFile("<deliverable>.docx") as z:
    footer_xml = ""
    for name in z.namelist():
        if re.match(r"word/footer\d*\.xml", name):
            footer_xml += z.read(name).decode("utf-8")

assert "PAGE" in footer_xml, "footer missing PAGE field"
assert "NUMPAGES" in footer_xml, "footer missing NUMPAGES field"
```

If `PAGE` or `NUMPAGES` is missing, the user cannot tell how long the
workbook is or where they are within it — fatal for a study document. The
fix is in the build script's footer construction, not in the docx.

## 7. textutil + unzip both succeed

```bash
textutil -convert txt -stdout "<deliverable>.docx" > /dev/null
unzip -t "<deliverable>.docx" > /dev/null
```

`textutil` converts the docx to plain text — if the file is malformed enough
that macOS cannot parse it, this fails before python-docx would. `unzip -t`
verifies the zip structure is intact (no truncated central directory, no
missing `[Content_Types].xml`). Both must succeed; either one failing means
the file is unsafe to deliver.

If `textutil` fails with a "couldn't be opened" error, the most common cause
is a non-standard character (e.g. an unpaired surrogate from a paste) in a
paragraph. Open the file in WPS/LibreOffice and look for a red-underlined
paragraph; fix the source string and rebuild.

## 8. Stimulus verbatim anchor sampling (prevents v2-style mis-mapping)

**This is the check that would have caught the Day 2+3 v2 incident.** For
each user-listed Q, pick an identifying keyword from the **expected**
stimulus and assert it appears in Part I.

```python
ANCHORS = {
    # section label as you write it in Part I headers → unique stimulus phrase
    ("Day 2", 3):  "How do the airlines expect to prevent",
    ("Day 2", 10): "privatization",
    ("Day 2", 17): "Danaxil",
    ("Day 2", 26): "Psychotherapy has been described",
    ("Day 3", 7):  "Golden Lake Development",
    ("Day 3", 33): "modern centuries",
    # ... 3–5 anchors per workbook, spread across the question set
}

PART1_TEXT = "\n".join(p.text for p in doc.paragraphs)

for (sec, q), phrase in ANCHORS.items():
    assert phrase in PART1_TEXT, \
        f"Part I missing anchor for {sec} Q{q}: {phrase!r}"
```

How to pick good anchors:

1. Open the source PDF and look at the question.
2. Pick a 2–6 word phrase that appears **only** in this question's stimulus
   (not a common phrase like "which one" or "the author").
3. Avoid phrases that also appear in another question's stimulus in the
   same workbook — even if they're in different sections, prefer unique
   strings.
4. Prefer distinctive proper nouns ("Danaxil", "Golden Lake Development",
   "Quad Cities Corporation") over generic phrases ("How do the airlines
   expect to prevent" works because no other Q asks about airline
   privatization).
5. If a question's stimulus has no unique proper noun, use a distinctive
   collocation: "psychotherapy has been described" rather than "psychotherapy".

For the Day 2+3 v3 workbook, the anchor set covered 6 of the 34 wrong
questions (Q3, Q10, Q17, Q26, Day-3 Q7, Day-3 Q33) and that was sufficient
to catch the v2 mis-mapping had it been run then.

Failure mode and what to do:

- If an anchor is missing, **the build script is using the wrong Q-body**.
  Do not patch the docx. Re-run the PDF Q-number extraction (check 0) and
  compare the Q-body for that Q against the source PDF. The mismatch is
  almost always in the build script's Q-lookup function, not in the docx
  itself.

## 9. Verified-answer tagging honesty

Part II marks each per-Q analysis with `✓verified` or `~` or `?`. The
distribution must match the actual web-verification status, not the build
script's default.

```python
PART2_TEXT = "\n".join(p.text for p in doc.paragraphs[split_at_part2(doc):])

# count the markers
verified = PART2_TEXT.count("✓verified")
mirrored = PART2_TEXT.count("~")          # includes every ~ in the doc
# estimate: number of mirrored tags ≈ number of (wrong Qs) - verified - unknown
```

Cross-check against `answer_verification_log.json` (whatever your build
script writes when it runs the web verification step). For the Day 2+3 v3
workbook, 13 of 34 wrong questions were `✓verified` (had at least one
independent prep page confirming the answer against the correct stimulus);
the remaining 21 were tagged `~` because they were best-guess mirrors of a
structurally identical Cambridge LR item. Do not claim all 34 are verified
when only 13 are — that is dishonest labelling and makes the rest of the
workbook untrustworthy.

If a build script defaults to `✓verified` for every Q, fix the script.
The verification log drives the tag; the build script reads the log; the
workbook renders the tag.

## 9.bis Part I 两栏 + Part II/III Helvetica 字体校验（用户偏好精简版）

**Added 2026-09-28 after PT01 v1 用户偏好精简事件。** 4 段式 + 3 张表（去
错选字母分布 / 7 日训练清单 / 核查 / 来源 行）—— workbook 内**不**出现
核查 / 来源 行；网络核对结果只在 verify_<scope>.py 输出，不进入 workbook。

verify harness **必须**检查下面 3 项，缺一项直接 FAIL：

```python
# (a) workbook 内不出现 核查： / 来源： 行（用户偏好精简）
chk_count = sum(1 for p in doc.paragraphs if p.text.startswith("核查："))
src_count = sum(1 for p in doc.paragraphs if p.text.startswith("来源："))
assert chk_count == 0, f"workbook 不应有 核查：行；found={chk_count}（用户偏好精简）"
assert src_count == 0, f"workbook 不应有 来源：行；found={src_count}（用户偏好精简）"

# (b) docx 共 3 张表（速览表 + Part III 题型分布 + 错因标签频次）；
# 不应有 错选字母分布 / 7 日训练清单
assert len(doc.tables) == 3, \
    f"tables count={len(doc.tables)} ≠ 3（用户偏好精简：去 错选字母分布 + 7 日训练清单）"
required_subtitles = [
    "1. 题型分布", "2. 错因标签频次", "3. 4-6 条具体劣势",
]
forbidden_subtitles = [
    "4. 4-6 条具体劣势",  # 已重新编号
    "2. 错选字母分布", "5. 7 日训练清单",  # 已删除
]
all_text = "\n".join(p.text for p in doc.paragraphs)
for subtitle in required_subtitles:
    assert subtitle in all_text, f"Part III 子节缺失：{subtitle!r}"
for subtitle in forbidden_subtitles:
    assert subtitle not in all_text, \
        f"Part III 子节不应出现：{subtitle!r}（用户偏好精简）"

# (c) 字体分 part 校验：Part I 题目卡应是 Arial + Times New Roman；
# Part II / III 应是 Helvetica。
# 这里只校验样本——若 Part II 8 段式段落中混入了 Times New Roman
# 而不是 Helvetica，说明 build script 字体映射漏改。
section_part_runs = {}
for i, sect in enumerate(doc.sections):
    # 收集每个 section 的 run 字体
    fonts_here = set()
    for p in doc.paragraphs:
        for r in p.runs:
            rfonts = r._element.find(qn("w:rPr"))
            if rfonts is not None:
                ascii_attr = rfonts.get(qn("w:ascii"))
                if ascii_attr:
                    fonts_here.add(ascii_attr)
    section_part_runs[i] = fonts_here
```

## 9.ter Part II 4 段式 vs 8 段式 校验

**Added 2026-09-28**. Build script 必须输出 4 段式（合并 ①② 去 ④/核查/来源/⑥/⑦），
不可继续输出 8 段式。

```python
# 检查 Part II 8 段式标签是否出现
forbidden_8section_labels = [
    "② 任务翻译",      # 合并入 ①
    "④ BR 预判",       # 合并入 ③
    "⑥ 你实际所选",    # 合并入 ⑤
    "⑦ 其余选项排除",  # 合并入 ⑤
]
all_text = "\n".join(p.text for p in doc.paragraphs)
for label in forbidden_8section_labels:
    assert label not in all_text, \
        f"Part II 出现旧 8 段式标签 {label!r}（应已合并入 ①/③/⑤）"

required_4section_labels = [
    "① 题型 + 任务",
    "③ stimulus 拆解",
    "⑤ 正确答案为何对",
    "⑧ 可迁移 Takeaway",
]
for label in required_4section_labels:
    assert label in all_text, f"Part II 4 段式缺失标签：{label!r}"
```

## 10. Independent human spot-check

**After all automated checks pass**, open the workbook in WPS or LibreOffice
and read 2–3 question cards from Part I. For each card:

1. Does the stimulus actually describe the scenario the user said they got
   wrong?
2. Do the five options A–E match the source PDF (verbatim, no paraphrasing)?
3. Does the question type heading (`Parallel Reasoning`, `Weaken`,
   `Principle`, etc.) match the user's classification of the question?

If any of those three is wrong, the workbook is mis-mapped regardless of how
many automated checks passed. The v2 incident passed every structural check
in the book and still failed this step on the first three cards. The human
spot-check is not optional.

## Recovery matrix when a check fails

| Failed check | Likely cause | Action |
|---|---|---|
| 0 (Q-number preflight) | PDF text layer broken; user Q missing | Ask user; do not proceed. |
| 1 (python-docx readable) | Corrupt docx, half-written file | Re-run build script; do not patch. |
| 2 (Q appears in Part I/II) | Build script dropped a Q or duplicated a section | Inspect digest; rebuild. |
| 3a (row count) | Build script wrote N+1 or N-1 rows | Inspect digest; rebuild. |
| 3b (triple match) | digest out of sync with build; or build re-derived from wrong Q-body | Rebuild from updated digest. |
| 4 (forbidden marker in Part I) | Build script pasted analysis into card | Fix build script; rebuild. |
| 5 (Part II anchor phrase) | Build script paraphrased the load-bearing phrase | Fix analyses JSON; rebuild. |
| 6 (PAGE/NUMPAGES missing) | Footer construction changed | Fix build script footer code; rebuild. |
| 7 (textutil / unzip fail) | Malformed docx, unpaired surrogate | Find the bad character; rebuild. |
| 8 (stimulus verbatim anchor) | Build script picked up wrong Q-body | Re-run check 0; fix Q-lookup; rebuild. |
| 9 (verified-tag dishonesty) | Build script default-tagged everything `✓verified` | Fix verification-log wiring; rebuild. |
| 10 (human spot-check fail) | Anything above was insufficient | Stop; report to user; do not deliver. |

## Sample harness

A minimal harness (`/Users/log/.cache/lsat_workbook/verify_<key>_v<n>.py`) wires
checks 1, 2, 3a, 3b, 4, 6, 7, 8 into one script. The Day 2+3 v3 harness added
checks 5, 8 and the human spot-check after the v2 incident; PT107 S1+S3,
PT108 S2, PT109 S3, PT109 S4, PT109 S1 all use the same shape.

The harness must print `ALL PASS` and exit 0 before the workbook is declared
delivered. A harness that prints warnings but exits 0 is not a passing
harness — fix the warnings.

## What this checklist does NOT cover

- **PDF text-layer integrity.** If `extract_text()` returns nothing, the
  PDF is image-only and the Q-number extraction in check 0 fails. Use a
  vision-based OCR pipeline instead (out of scope for this skill).
- **Visual layout.** Part I 两栏 + 9.5pt + 3pt/1.2 倍 + 每 2 题 column break（过长题单列）、A4 页面 0.79" 边距、Part II/III 单栏 + 10.5pt + 1.15 倍、节断点频率等，由 build script 的 geometry 强制保证，本 checklist 不覆盖。若未来 build 需要新布局，先改 build script 再重导本档中依赖布局的检查项（rows-per-table / anchors per page / 文本密度阈值等）。
  - **2026-09-23 板式变更**：Part I 由"单栏 12pt / 1.15 倍 / 自然分页"切换为"两栏 9.5pt / 1.2 倍 / 显式 column break"。本 checklist 的 Part I 锚点断言、文本密度估算、字号相关的 sanity 检查需按新规格执行（9.5pt 单列可放字符数较 12pt 多约 25%，行距由 1.15 → 1.2 进一步影响密度）。
- **Cross-workbook aggregation.** The cross-workbook weakness report at
  `/Users/log/LSAT_LR_*_Blind_Review_解析_cross_v1.docx` is built from
  `all_workbooks_wrong_qs.json` and `all_workbooks_local_weaknesses.json`;
  its verification is a separate harness
  (`verify_cross_workbook_report_v1.py`).

## Related Skills

- **→ `lsat-pdf-to-section-docx`** — Route here when the source material is an image-only Cambridge LSAT category PDF (cover labeled "Cambridge LSAT / <Category> / N Questions"). This skill transcribes to a Weaken-template `.docx` (two questions per page + answer-key tail), then `lsat-blind-review` or `lsat-prep-tutor` can take over.
- **→ `lsat-prep-tutor`** — Route here for in-session single-question 7Sage-style讲解 (modes A/B/C/D in that skill). Use when the user has a question in hand and wants the analysis now, not a workbook.
- **↔ `lsat-blind-review`** — Default entry point for multi-question BR workbooks. Produces `.docx` (Part I 题目卡 + Part II 八段式 + Part III 劣势报告 + 来源说明).
- **← from `lsat-prep-tutor`** — When the user wants a 7Sage-style analysis baked into a permanent workbook (vs. in-session markdown), route from `lsat-prep-tutor` here.
- **← from `lsat-pdf-to-section-docx`** — When the user finishes a 2-up transcription and then asks for错题分析 or Blind Review on the questions in it, route from `lsat-pdf-to-section-docx` here.
