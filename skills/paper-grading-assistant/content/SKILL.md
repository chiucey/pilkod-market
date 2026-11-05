---
name: paper-grading-assistant
description: A grading assistant for university course assignments and papers. Use when users request paper grading, homework review, course report evaluation, academic writing quality checks, or Word document feedback with comments. Supports annotations, scoring, revision suggestions, and detailed improvement feedback.
---

# Paper Grading Assistant

## Core Functions

This skill is used for intelligent grading of Word-format course papers and assignments submitted by university students, outputting Word documents with detailed annotation feedback.

## Trigger Scenarios

This skill should be activated when users send the following requests:
- "Grade this paper"
- "Help me review this assignment"
- "Evaluate this course report"
- "Score this essay and provide revision suggestions"
- "Check the writing quality of this paper"
- "Academic paper polishing and annotation"
- Upload a .docx file and request grading

## Workflow

### Stage 1: Document Reception and Parsing

1. **Receive Word Document**
   - Supports .docx format course papers, assignments, reports, etc.
   - If user provides file path, read directly
   - If user provides text content, guide user to upload Word file

2. **Parse Document Structure**
   - Use minimax-docx skill to read document content
   - Identify document heading hierarchy
   - Extract body paragraphs, tables, image descriptions, etc.
   - Record basic document information (word count, paragraph count, etc.)

3. **Content Classification Analysis**
   - Distinguish sections like introduction, methods, results, discussion, conclusion
   - Identify core arguments and supporting evidence
   - Mark citations and references

### Stage 2: Multi-dimensional Grading Assessment

Evaluate papers on the following dimensions:

#### 2.1 Structure Completeness (20 points)
- [ ] Whether containing complete paper structure
- [ ] Whether heading levels are clear and reasonable
- [ ] Whether chapter logic is coherent
- [ ] Whether introduction-body-conclusion flow is smooth

#### 2.2 Content Quality (30 points)
- [ ] Whether arguments are clear and novel
- [ ] Whether evidence is sufficient and persuasive
- [ ] Whether analysis is in-depth and insightful
- [ ] Whether conclusions are well-supported and reasonable

#### 2.3 Writing Standards (25 points)
- [ ] Whether language expression is accurate and fluent
- [ ] Whether terminology usage is standard
- [ ] Whether paragraph transitions are natural
- [ ] Whether grammar/punctuation errors exist

#### 2.4 Format Standards (15 points)
- [ ] Whether citation format meets requirements
- [ ] Whether reference format is standard
- [ ] Whether figure/table numbering and captions are complete
- [ ] Whether overall layout is neat

#### 2.5 Innovation and Thinking (10 points)
- [ ] Whether showing independent thinking
- [ ] Whether viewpoints have innovation
- [ ] How critical thinking performance is

### Stage 3: Generate Annotation Feedback

Based on evaluation results, generate the following types of annotations:

1. **Overall Evaluation**
   - Summary comments (strengths + weaknesses)
   - Suggested total score and grade
   - Overall improvement direction

2. **Detailed Annotations**
   - Add specific annotations at various document positions
   - Use different colors to distinguish annotation types:
     - Red: Serious issues (needs immediate revision)
     - Yellow: General issues (optimization suggested)
     - Green: Excellent parts (keep it up)
   - Each annotation includes: problem description + revision suggestion

3. **Itemized Scoring Table**
   - Score breakdown by dimension
   - Reason for point deductions

### Stage 4: Output Word Grading Document

Use minimax-docx skill to generate graded Word document:

```
Output Document Structure:
├── Cover Page
│   ├── Grading Date
│   ├── Document Title
│   └── Overall Score
├── Overall Evaluation
│   ├── Score Summary Table
│   ├── Strengths Summary
│   └── Weaknesses and Suggestions
├── Detailed Annotations
│   ├── Chapter-by-chapter annotations
│   └── Specific Revision Suggestions
└── Appendix: Annotation Reference Table
```

## Annotation Format Standards

### Annotation Type Markers

| Marker | Type | Color | Description |
|--------|------|-------|-------------|
| [Issue] | Error | Red | Factual errors or serious problems |
| [Suggestion] | Improvement | Yellow | Optimization suggestions |
| [Strength] | Praise | Green | Excellent performance |
| [Question] | Discussion | Blue | Needs further explanation |
| [Reference] | Supplement | Gray | Extended reading materials |

### Annotation Template

```
[Annotation Type] Location: Specific paragraph/page
- Problem Description: ...
- Revision Suggestion: ...
- Reference Example: ... (optional)
```

## Output Requirements

### Word Document Format
- Use Word's built-in comment feature for annotations
- Preserve original document structure, don't directly modify original text
- Use table format for scoring
- Support printing and electronic review

### File Naming
- Input file: Original file name
- Output file: `[Original filename]_Graded.docx`

## Typical Work Example

**Input**: Course paper "XXX Research" submitted by a student

**Processing Flow**:
1. Parse paper structure and content
2. Evaluate on five dimensions
3. Generate itemized scoring table
4. Add annotations at key positions
5. Output complete graded document

**Output**: Word document containing overall evaluation, detailed scoring, and specific annotations

## Notes

1. **Maintain Objectivity**: Evaluate based on paper content without personal bias
2. **Focus on Constructiveness**: Balance criticism and praise, emphasize improvement plans
3. **Consider Subject Differences**: Different subjects may have different writing standards
4. **Respect Students**: Annotation tone should be friendly and encouraging, avoid hurting student motivation
5. **Confidentiality Principle**: Handle student assignment content properly without disclosure
