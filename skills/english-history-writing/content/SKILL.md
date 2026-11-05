---
name: english-history-writing
description: >
  English academic history writing skill with two core functions: (1) **Topic Generation** — produce
  exam-style history writing prompts across four types: term explanation (名词解释), source analysis
  (材料分析), event commentary (事件评述), and person evaluation (人物评价), delivered as a Word document;
  (2) **Writing Correction** — grade and annotate submitted English history essays at native-speaker
  academic standard (100-point rubric), producing a Word document with the original text, inline-
  annotated version, numeric score, and a 200–300 word Chinese commentary. Trigger immediately when
  the user asks to: generate history writing questions / 出题 / 生成题目 / 写作题目 / academic writing
  prompt, OR submit an essay for correction / 批改 / 帮我改 / 批改这篇 / 评分 / 帮我打分, even if
  they only say "出题" or "批改". Always produce a deliverable file — never just answer in plain text.
---

# English History Academic Writing Skill

You support two distinct workflows. Identify which one the user needs, then follow the corresponding pipeline below.

---

## Workflow A — Topic Generation (出题)

**Trigger**: User asks for history writing questions / prompts / 出题 / 生成题目.

### Step 1 — Determine parameters

Ask (or infer from context) two things:
1. **Question type** — one or more of:
   - **Term Explanation** (名词解释): define and contextualise a historical term/concept
   - **Source Analysis** (材料分析): analyse a provided primary or secondary source excerpt
   - **Event Commentary** (事件评述): evaluate the causes, process, and significance of a historical event
   - **Person Evaluation** (人物评价): assess a historical figure's role, impact, and legacy
2. **Number of questions** — default is **1** per type selected.

If the user hasn't specified, generate **one question of each type** (4 questions total).

### Step 2 — Select questions from the reference bank

Read `references/sample_questions.md` (bundled with this skill). Choose questions that best fit the user's request. Randomise selection across different historical periods and regions to ensure variety. Do **not** always pick the first question in each section.

### Step 3 — Apply word-count standards

Apply the following default word-count targets (adjust slightly if the user specifies a difficulty level):

| Type | Recommended Length |
|---|---|
| Term Explanation | 150–250 words |
| Source Analysis | 400–600 words |
| Event Commentary | 500–800 words |
| Person Evaluation | 500–800 words |

Always print the word-count requirement **in the question prompt itself**.

### Step 4 — Generate the Word document

Run the bundled script to produce the Word file:

```bash
python <skill_base_dir>/scripts/generate_docx.py topic \
  --questions '<json_array_of_question_objects>' \
  --output ./history_writing_questions.docx
```

Each question object has:
```json
{
  "type": "Term Explanation",
  "type_cn": "名词解释",
  "question": "...",
  "word_count_note": "150–250 words"
}
```

If the script is unavailable, use `jupyter_execute` with `python-docx` directly (see **Appendix: Manual DOCX generation**).

### Step 5 — Deliver

Publish the Word file and briefly describe what was generated (types and number of questions).

---

## Workflow B — Essay Correction (批改)

**Trigger**: User uploads or pastes an English history essay and asks for correction/grading.

### Step 1 — Receive the essay

The user may:
- Upload a `.docx` or `.pdf` file
- Paste text directly into the chat

Extract the full text. If the file cannot be read, ask the user to paste the content as plain text.

### Step 2 — Load the grading rubric

Read `references/grading_rubric.md` carefully before starting any annotation. The rubric defines all criteria and point allocations (total: 100 points).

### Step 3 — Analyse the essay

Work through the essay **paragraph by paragraph**. For each paragraph, note:
- Grammar errors (subject-verb agreement, tense, articles, prepositions, etc.)
- Vocabulary and expression issues (imprecise word choice, register mismatch, redundancy)
- Style and academic register problems (informal tone, unclear academic prose)
- Content and argumentation issues (factual inaccuracies, logical gaps, missing evidence, weak thesis)
- Structure issues (poor transitions, lack of coherence, missing introduction/conclusion elements)

### Step 4 — Produce the annotated version

Create an inline-annotated copy of the essay. For each error or suggestion, insert a comment in this format immediately after the relevant text:

```
[COMMENT: <type> | <original> → <suggestion> | <brief explanation>]
```

Types: `GRAMMAR`, `VOCAB`, `STYLE`, `CONTENT`, `STRUCTURE`

Example:
```
The industrial revolution have[COMMENT: GRAMMAR | have → had | Subject 'revolution' is singular; past perfect required here] transformed...
```

### Step 5 — Score the essay

Apply the rubric from `references/grading_rubric.md` to assign a score out of 100. Break it down by dimension and produce a brief score table:

| Dimension | Max | Score |
|---|---|---|
| Thesis & Argument | 25 | — |
| Evidence & Analysis | 25 | — |
| Historical Knowledge | 20 | — |
| Language & Style | 20 | — |
| Structure & Coherence | 10 | — |
| **Total** | **100** | **—** |

### Step 6 — Write the Chinese commentary

Write **200–300 words in Chinese** summarising:
1. Overall impression and key strengths
2. Main issues identified (3–5 specific points)
3. Targeted advice for improvement
4. Encouraging closing remark

Tone: professional, constructive, native-scholar standard. Avoid vague praise; be specific.

### Step 7 — Generate the output document

Run the bundled script:

```bash
python <skill_base_dir>/scripts/generate_docx.py grade \
  --original '<original_text>' \
  --annotated '<annotated_text>' \
  --score_table '<json_score_table>' \
  --total_score <number> \
  --commentary '<chinese_commentary_text>' \
  --output ./history_essay_graded.docx
```

The document structure must be:
1. **Part 1 — Original Essay** (unmodified)
2. **Part 2 — Annotated Essay** (with inline comments)
3. **Part 3 — Score Breakdown** (table)
4. **Part 4 — Teacher's Commentary** (Chinese, 200–300 words)

If the script is unavailable, use `jupyter_execute` with `python-docx` (see **Appendix: Manual DOCX generation**).

### Step 8 — Deliver

Publish the document. In the chat, give one sentence summary: e.g., "批改完成，总分 XX/100，主要问题集中在 [2–3 key issues]。"

---

## Appendix: Manual DOCX generation

If the bundled script fails, use this fallback in `jupyter_execute`:

```python
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

doc = Document()

# Title
title = doc.add_heading('History Essay — Graded', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Part 1 — Original
doc.add_heading('Part 1: Original Essay', level=1)
doc.add_paragraph(original_text)

# Part 2 — Annotated (inline comments styled in red)
doc.add_heading('Part 2: Annotated Essay', level=1)
# Split on [COMMENT:...] tags and alternate normal / red runs
import re
parts = re.split(r'(\[COMMENT:.*?\])', annotated_text)
para = doc.add_paragraph()
for part in parts:
    run = para.add_run(part)
    if part.startswith('[COMMENT:'):
        run.font.color.rgb = RGBColor(0xCC, 0x00, 0x00)
        run.font.size = Pt(9)

# Part 3 — Score table
doc.add_heading('Part 3: Score Breakdown', level=1)
table = doc.add_table(rows=1, cols=3)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = 'Dimension'; hdr[1].text = 'Max'; hdr[2].text = 'Score'
for row in score_rows:
    cells = table.add_row().cells
    cells[0].text = row['dimension']
    cells[1].text = str(row['max'])
    cells[2].text = str(row['score'])

# Part 4 — Commentary
doc.add_heading('Part 4: Teacher\'s Commentary（教师评语）', level=1)
doc.add_paragraph(chinese_commentary)

doc.save('./history_essay_graded.docx')
print("Document saved.")
```

For topic generation, follow a similar pattern with heading styles per question type.

---

## Notes on academic standard

- This skill grades at **native English-speaker academic level** (equivalent to undergraduate history essays at UK/US universities).
- For grading, prioritise **argument quality and historical reasoning** over surface-level grammar — but both matter.
- When generating questions, draw from **world history broadly**: European, American, Asian, African, and global history are all in scope. Avoid clustering questions around a single region or period.
- The annotated essay format uses plain-text inline comments (not Word's native comment bubbles) so the document is portable and readable without special software.
