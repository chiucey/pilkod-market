---
name: work-summary-compiler
description: Compile weekly work summaries into monthly or annual work summary documents. Use when users provide weekly work summary documents and ask to organize them into monthly or annual summaries. Trigger: compile monthly summary, compile annual summary, weekly summary aggregation.
---

# Work Summary Compiler Skill

Core workflow for compiling multiple weekly work summaries into structured monthly or annual work summary Word documents.

## Core Principles

1. **Preserve Original Meaning**: Do not alter original work content, ensure no deviation from source
2. **Filter Duplicates**: Merge repetitive and routine work, highlight key achievements
3. **Clear Structure**: Organize by business modules, concise and professional language
4. **Standard Format**: Output standard Word documents for easy download

## Workflow

### Step 1: Read Source Documents

Use LibreOffice to convert `.doc` files to `.docx` format, then read content:

```bash
# 1. Convert format using soffice
soffice --headless --convert-to docx --outdir tmp input.doc

# 2. Read content using python-docx
python3 << 'EOF'
from docx import Document
doc = Document(output.docx)
for para in doc.paragraphs:
    if para.text.strip():
        print(para.text)
EOF
```

### Step 2: Content Analysis

**Monthly Summary Logic**:
- Merge similar items: Combine same category work from 4 weeks
- Filter duplicates: Remove weekly routine work (e.g., "complete daily attendance" keep once)
- Highlight key points: Preserve important achievements, changes, optimizations
- Supplement details: Aggregate specific names, dates, data from all weeks

**Annual Summary Logic**:
- Aggregate by month: Summarize 12 months work separately
- Extract highlights: Core achievements, major projects, key results each month
- Horizontal merge: Combine same category work across 12 months
- Deduplicate: Remove monthly routine work

### Step 3: Categorize and Organize

Classify work summary content into following modules:
- Attendance Management (attendance stats, exception handling, leave management)
- Salary & Social Security (salary calculation, social insurance/housing fund)
- Recruitment & Personnel (resume screening, interviews, onboarding/offboarding)
- Performance Management (assessment framework, KPI optimization)
- Administrative Affairs (office environment, logistics)
- Cross-department Coordination (finance liaison, project communication)
- Policy & Process (policy updates, process optimization)
- Other (special matters)

### Step 4: Generate Document

Use python-docx to generate Word document with format requirements:
- Page margins: top/bottom 2.54cm, left/right 3.17cm
- Title: Heiti 22pt centered
- Heading 1: Heiti 16pt
- Body: Songti 12pt bullet list

```python
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()
# Set margins
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.17)
    section.right_margin = Cm(3.17)

# Add title
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title_run = title.add_run('2026 Year January Work Summary')
title_run.font.name = 'Heiti'
title_run.font.size = Pt(22)
```

## Automation Scripts

### read_docs.py - Read Documents

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert and read work summary documents using LibreOffice"""

import subprocess
import os
from docx import Document

def convert_doc_to_docx(input_file):
    """Convert .doc to .docx format"""
    os.makedirs("tmp", exist_ok=True)
    output_file = f"tmp/{os.path.basename(input_file).replace('.doc', '.docx')}"
    cmd = ["soffice", "--headless", "--convert-to", "docx", "--outdir", "tmp", input_file]
    subprocess.run(cmd, check=True, capture_output=True, timeout=30)
    return output_file

def read_docx_content(docx_file):
    """Read .docx file content"""
    doc = Document(docx_file)
    contents = []
    for para in doc.paragraphs:
        if para.text.strip():
            contents.append(para.text)
    return contents

def read_all_docs(input_files):
    """Batch convert and read multiple documents"""
    results = {}
    for f in input_files:
        try:
            converted = convert_doc_to_docx(f)
            results[f] = read_docx_content(converted)
        except Exception as e:
            print(f"[Failed] {f}: {e}")
    return results
```

### create_summary.py - Generate Document

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate monthly/annual work summary Word document"""

import os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_heading(doc, text, level=1):
    """Add styled heading"""
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.name = 'Heiti'
        run.font.bold = True
        run.font.size = Pt(16 if level == 1 else 14)
    return heading

def add_bullet(doc, text):
    """Add bullet point"""
    para = doc.add_paragraph()
    para.style = 'List Bullet'
    run = para.add_run(text)
    run.font.name = 'Songti'
    run.font.size = Pt(12)
    return para

def create_summary(title_text, sections, output_dir='outputs'):
    """Generate work summary document

    Args:
        title_text: Document title, e.g., "2026 Year January Work Summary"
        sections: Dict, key=module name, value=list of work items
        output_dir: Output directory
    """
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.17)
        section.right_margin = Cm(3.17)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.add_run(title_text)
    title_run.font.name = 'Heiti'
    title_run.font.size = Pt(22)
    title_run.font.bold = True

    for section_name, items in sections.items():
        add_heading(doc, section_name, 1)
        for item in items:
            add_bullet(doc, item)

    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{title_text}.docx"
    doc.save(output_path)
    return output_path
```

## Usage Instructions

1. User says "compile monthly summary" and provides weekly work summary documents
2. Skill automatically reads all documents
3. Analyzes content, deduplicates, integrates
4. Generates monthly/annual work summary Word document
5. Returns download link

## Examples

**Input**: User provides 4 weekly work summaries for January
**Output**: Generate "Work Summary -- 2026 January.docx"

**Input**: User provides 12 monthly work summaries for the year
**Output**: Generate "Annual Work Summary -- 2026.docx"