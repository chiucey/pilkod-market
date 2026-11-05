---
name: career-planning-filler
description: "Fill in career planning Excel templates for returning overseas students based on their resumes. Use for: extracting resume information to populate red-font cells in the 归国求职学生规划课教参 Excel template, generating industry-specific career advice, recommending target companies and positions, and providing skill improvement suggestions tailored to specific job directions (algorithm/ML, quantitative finance, data science, etc.)."
---

# Career Planning Filler

Fill the red-font cells in the career planning Excel template (归国求职学生规划课教参) using information extracted from a student's resume, combined with industry-specific career guidance.

## Workflow

1. Parse the resume
2. Detect red cells in the Excel template
3. Determine career direction
4. Fill each red cell
5. Save and deliver

## Step 1: Parse the Resume

Read the uploaded resume (`.docx` or `.pdf`) using `python-docx` or `pdfplumber`. Extract all fields listed in `references/resume_parsing_guide.md`.

Save extracted info to a working note for reference during filling.

## Step 2: Detect Red Cells

Run the detection script:

```bash
python /home/ubuntu/skills/career-planning-filler/scripts/detect_red_cells.py <excel_path>
```

This identifies all red-font cells that need filling. The standard template has these red cells: B3, B4, B5, B6, D12, D13, D14, D15, D16, D17, D18.

## Step 3: Determine Career Direction

Based on resume signals (see `references/resume_parsing_guide.md`), identify the student's primary career direction. If the user specifies a direction (e.g., "算法岗"), use that.

## Step 4: Fill Each Red Cell

Use `openpyxl` to write content. For each cell:

```python
from openpyxl.styles import Font, Alignment

black_font = Font(name='微软雅黑', size=10, color='FF000000')
wrap_align = Alignment(wrap_text=True, vertical='top')

ws[cell_ref] = content
ws[cell_ref].font = black_font
ws[cell_ref].alignment = wrap_align
```

Consult `references/cell_filling_guide.md` for what to fill in each cell. Key principles:

- **B3 (背景挖掘)**: Comprehensive student profile — location, education (school/major/GPA/courses), internships with key achievements, skills, language scores, career intent
- **B4 (归国时间)**: Graduation date, return timeline, applicable recruitment seasons with primary season highlighted
- **B5 (就业方向)**: 4-5 recommended industries with reasoning tied to student's background
- **B6 (求职方向)**: Specific companies and position titles per direction (5 categories)
- **D12 (实习留用)**: Intern availability and conversion rates at target companies
- **D13 (校招社招)**: Campus recruitment scale and social recruitment availability
- **D14 (技能提升)**: 5-6 specific skill gaps with actionable improvement steps
- **D15 (项目科研)**: Existing resources + 3-4 recommended additions (competitions, open-source, research)
- **D16 (实习建议)**: Timeline, target companies, channels, preparation checklist
- **D17 (证书考试)**: Recommended certifications with priority ranking (direction-specific)
- **D18 (其他注意)**: GitHub, blog, interview prep categories, networking, visa planning, resume versioning

For direction-specific company lists and skill recommendations, read the relevant section in `references/cell_filling_guide.md`.

## Step 5: Save and Deliver

Save with a descriptive filename:

```python
wb.save(f'归国求职学生规划课教参-{student_name}-已填写.xlsx')
```

Deliver the file with a summary table showing each filled cell and a content preview.
