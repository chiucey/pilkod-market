---
title: PDF Q-number extraction & mapping protocol
applies_to: lsat-blind-review skill (all 4-part workbook builds)
priority: mandatory, runs before any code is written or any subagent is dispatched
related_skills_placeholder: ## Related Skills

- **→ `lsat-pdf-to-section-docx`** — Route here when the source material is an image-only Cambridge LSAT category PDF (cover labeled "Cambridge LSAT / <Category> / N Questions"). This skill transcribes to a Weaken-template `.docx` (two questions per page + answer-key tail), then `lsat-blind-review` or `lsat-prep-tutor` can take over.
- **→ `lsat-prep-tutor`** — Route here for in-session single-question 7Sage-style讲解 (modes A/B/C/D in that skill). Use when the user has a question in hand and wants the analysis now, not a workbook.
- **↔ `lsat-blind-review`** — Default entry point for multi-question BR workbooks. Produces `.docx` (Part I 题目卡 + Part II 八段式 + Part III 劣势报告 + 来源说明).
- **← from `lsat-prep-tutor`** — When the user wants a 7Sage-style analysis baked into a permanent workbook (vs. in-session markdown), route from `lsat-prep-tutor` here.
- **← from `lsat-pdf-to-section-docx`** — When the user finishes a 2-up transcription and then asks for错题分析 or Blind Review on the questions in it, route from `lsat-pdf-to-section-docx` here.
---

# Pre-flight: PDF / DOCX Q-number extraction & mapping protocol

This is the **single highest-leverage safety step** in the whole `lsat-blind-review`
skill. Skipping it (or "inferring" a mapping from page-1 snippets) is the failure
mode that produced the **Day 2 + Day 3 v2 workbook**, which was entirely mis-mapped
and rejected by the user on opening the first three cards. This file is the
canonical, prescriptive version of the four bullets in `SKILL.md § Mandatory
Pre-Flight`. Read it before writing any extractor, builder, or analysis script.

## 1. Why this step exists

The user gives a list of wrong question numbers (e.g. `Q3, Q10, Q17, Q26`) and
expects those numbers to be **the same numbers** that appear in the source PDF
or DOCX. That assumption is correct only if every number in the user's list is
present in the source. The v2 failure happened because the coder agent assumed
"Q17 must be the question about Danaxil" without first enumerating every
`Q{n}.` (or `Question {n}`) label in the source. It then mapped Q17 to a
different stimulus that happened to contain the word "Danaxil" later in the PDF.
Every other question drifted the same way.

The rules below are the only way to prevent that drift. **Do not improvise.**

## 2. The five-step protocol

Run these steps **in order** before any code that consumes question bodies is
written.

### Step 1 — Dump full source text

```python
from pypdf import PdfReader      # or pdfplumber.open(path) for DOCX-styled PDFs
full = "\n".join((page.extract_text() or "") for page in PdfReader(path).pages)
```

For DOCX sources, walk `doc.paragraphs` (and any answer-key `doc.tables`) and
join with `\n`:

```python
from docx import Document
full = "\n".join(p.text for p in Document(path).paragraphs)
```

Save `full` to a scratch file so subsequent steps can be re-run without
re-reading the source. The script that runs this dump is conventionally
named `extract_<scope>_v1.py` and lives in `/Users/log/.cache/lsat_workbook/`.

**Do not** stop after `extract_text()[:120]` of page 1. That snippet cannot
distinguish a Q1-only-odd-numbered book from a Q1..Q40 sequentially numbered
book. Page 1 is the wrong place to make a mapping decision.

### Step 2 — Enumerate every Q label in the source

Use the regex that matches the actual source's labelling scheme. The two
schemes observed in this skill's history:

| Source style                              | Regex (Python raw)                          | Example match |
|-------------------------------------------|---------------------------------------------|---------------|
| Cambridge LR Vol.1 (Day 2 / Day 3 source) | `r"Q(\d+)\.\s*\["`                          | `Q17. [Must Be True Cambridge LR Vol.1 Ch10 Q.31]` |
| LSAT-released PrepTest DOCX / PDF         | `r"^\s*Question\s+(\d+)\s*$"` (multiline)   | `Question 17` on its own line |

Compute the sorted integer list:

```python
qids = sorted({int(m.group(1)) for m in re.finditer(LABEL_RE, full)})
print(f"[extract] enumerated Q labels: {qids[0]}..{qids[-1]}  n={len(qids)}")
```

For PrepTest-style sources where the marker can be repeated (e.g. "Question 17"
in the running header AND in the body), prefer first-occurrence index with a
duplicate check, as in `/Users/log/.cache/lsat_workbook/extract_pt107_s1.py`
and `extract_pi_s3_v1.py`:

```python
marker_idx = {}
for i, t in enumerate(paras):
    m = marker_re.match(t)
    if m:
        qn = int(m.group(1))
        if qn in marker_idx:
            raise SystemExit(f"duplicate Question marker for Q{qn} at paragraph {i}")
        marker_idx[qn] = i
qids = sorted(marker_idx)
```

### Step 3 — Compare against the user's wrong-Q list

```python
USER_WRONG = [3, 8, 10, 13, 14, 17, 23, 26, 27, 29, 31, 34, 36, 37, 38]  # from user
missing = [q for q in USER_WRONG if q not in qids]
extra   = [q for q in qids if q not in range(min(qids), max(qids) + 1)]
if missing or extra:
    raise SystemExit(
        f"Q-number mismatch. user-missing-in-source={missing}; "
        f"source-out-of-range={extra}. STOP — ask the user before proceeding."
    )
```

**If `missing` is non-empty, STOP. Do not cross-match by content keywords. Do
not "find the closest question." Do not paraphrase. Tell the user which Q-numbers
they listed are not in the source and ask them to confirm.** This is the v2
failure mode; treating the user's Q-numbers as authoritative is the v3
correction.

### Step 4 — Slice per-Q body verbatim

Split `full` (or `paras`) into a dict keyed by Q-number. Each entry holds the
stimulus, stem, options A–E, and `status` ("complete" or "partial"). Two
layouts observed:

- **Cambridge LR style**: stimulus → stem → `Q{n}. [<header>]` → options.
  Stimulus sits *before* the `Q{n}.` marker; stem + A–E sit *after*. See
  `/Users/log/.cache/lsat_workbook/parse_source.py` for `split_question()`.
- **PrepTest DOCX style**: `Question {n}` is its own paragraph; stimulus sits
  *before* the marker; stem + A–E sit *after*. See
  `/Users/log/.cache/lsat_workbook/pi_s3_extract.py` for `stimulus_block()`.

Whichever layout applies, the rule is the same: **each Q-body (stimulus + stem
+ A–E) must be read verbatim from the source text dump. Do not summarize. Do
not paraphrase the English. Do not "fix" OCR artefacts in place** — flag them
in a notes file and re-read the source image if the answer depends on the
disputed character.

Write the sliced dict to `/Users/log/.cache/lsat_workbook/<scope>_clean.json`
with one top-level key per day/section:

```json
{
  "day2": {"1": {"qnum": 1, "stimulus": "...", "stem": "...", "options": {"A": "...", "B": "...", "C": "...", "D": "...", "E": "..."}}, "2": {...}, ...},
  "day3": {"1": {...}, ...}
}
```

### Step 5 — Hand the clean JSON to downstream scripts

Every later script (builder, harness, weakness extractor) reads from the
`<scope>_clean.json` produced in Step 4. They never re-read the source PDF.
They never re-enumerate Q-numbers. The Q-number mapping is locked at this
step.

## 3. What the verification harness must check (handoff to SKILL.md § Verification)

The mapping produced by this protocol is verified by the harness in
`SKILL.md § Verification` step 8 ("Stimulus verbatim sampling"). For every
user-listed wrong Q, the harness asserts that 3–5 anchor keywords from the
expected stimulus appear in Part I. The anchor-keyword dict is stored alongside
the analysis data (`META["anchors"]` in
`/Users/log/.cache/lsat_workbook/build_pt109_s3_v1.py` and the `_v1.py` peer
scripts). Pick keywords that:

- are unique to that question (e.g. `Danaxil` for Q17 in Day 2, `Golden Lake
  Development` for Day 3 Q7, `How do the airlines expect to prevent` for Day 2 Q3,
  `modern centuries` for Day 3 Q33),
- span more than one line of the stimulus (do not pick all from the first
  sentence),
- are not option text (option text appears in Part I and would false-positive
  any keyword check).

If any anchor check fails, treat it as a Q-mapping failure and re-run Steps
2–4 before delivering. Do **not** patch the anchors to make the check pass.

## 4. Hard rules (do not violate, ever)

1. **The user's Q-number is the PDF/DOCX Q-number.** If the user lists Q17,
   `qids` must contain `17`. Any other interpretation is the v2 failure mode.
2. **Never cross-match by content keywords.** "Find the question about
   Danaxil" is forbidden. "Look up Q17, then read its stimulus" is the only
   allowed sequence.
3. **Never trust `extract_text()[:120]`.** It cannot distinguish a
   sequentially numbered book from a Q1/Q3/Q5-only book.
4. **Never read a Q-body from anywhere other than the `full` text dump from
   Step 1.** No paraphrasing, no LLM-generated "stimulus reconstructions,"
   no copying from a previous workbook.
5. **Always assert `qids == list(range(min, max+1))` when the source uses
   contiguous numbering.** Cambridge LR Vol.1 always does; some PrepTests do
   not. If the source is non-contiguous, ask the user to confirm which
   Q-numbers they meant.
6. **Always back up a wrong deliverable before rebuilding.** When replacing a
   known-bad file (like v2), copy to `<name>.bak2` first. The user may want to
   diff.
7. **Always place the hard rule at the top of any prompt to a coder/generator
   subagent**: "Strictly use the user's Q-numbers as the PDF Q-numbers. Each
   Q-body (stimulus + stem + A–E) must be read verbatim from the pre-extracted
   JSON. Do NOT cross-match by content keywords."
8. **Always run an independent spot-check after the harness passes.** The
   harness can pass structurally while the content is entirely wrong (this
   is exactly what happened with v2). Manually read 2–3 question cards in
   Part I and confirm the stimulus is the question the user meant.

## 5. Reference implementations in `.cache/lsat_workbook/`

These scripts embody the protocol and are the closest thing to a worked example
for each source type:

| Source type                       | Script                                          | Layout |
|-----------------------------------|-------------------------------------------------|--------|
| Cambridge LR Vol.1 (Day 2/3 txt)  | `extract_pdf3.py` (text dump) → `parse_source.py` → `q_bodies.json` | stimulus-then-marker |
| LSAT-released PrepTest PDF        | `extract_pt107_s3.py`                           | marker-then-content (text layer) |
| LSAT-released PrepTest DOCX       | `extract_pt107_s1.py`, `extract_pi_s3_v1.py` / `pi_s3_extract.py` | marker-then-content (paragraph walk) |
| PT109 Section 1 (OCR'd PDF)       | `pt109_section1_chunks.json` → `parse_pt109.py` | heuristic last-option marker |

When writing a new extractor, copy the structure of the closest peer above.
When in doubt, copy `extract_pi_s3_v1.py` — it has the cleanest expression of
the protocol (explicit `marker_idx` dict, explicit `missing` / `extra` check,
explicit `assert qids == expected`).

## 6. Quick preflight checklist (run before Step 1)

```text
[ ] pypdf / pdfplumber installed (for PDF sources)
[ ] python-docx installed (for DOCX sources)
[ ] source PDF/DOCX is openable from its known path
[ ] /Users/log/.cache/lsat_workbook/ exists and is writable
[ ] user's wrong-Q list captured (Day 2 + Day 3, or Section N, etc.)
[ ] intended output filename follows LSAT_LR_<scope>_Blind_Review_解析_v{n}.docx
[ ] v{n} does not collide with an already-shipped deliverable in /Users/log/
```

If any of the above is missing, fix it before running Step 1. The cost of a
five-minute check is small; the cost of a v2-style rewrite is a half-day.
