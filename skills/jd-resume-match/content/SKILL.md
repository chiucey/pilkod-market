---
name: jd-resume-match
description: 分析简历与职位描述的匹配程度。支持多种输入格式：JD可来自URL链接、图片截图、PDF/Word文档；简历可上传PDF、Word、Markdown或图片格式。当用户要求匹配简历和JD、分析简历与职位匹配度、对比简历和职位要求、进行简历JD匹配分析时使用。
---

# JD-Resume Matching Analysis Skill

## Core Features

Intelligent analysis of job description (JD) and resume matching degree, extracting key information for multi-dimensional comparison, outputting structured matching reports and improvement suggestions.

## Supported Input Formats

### JD Sources

| Source Type | Processing Method | Tool Support |
|-------------|------------------|--------------|
| URL Link | Web scraping + content extraction | extract_content_from_websites |
| Image Screenshot | OCR text recognition | images_understand |
| PDF Document | Text extraction | extract_pdfs_full_content |
| Word Document | Text extraction | extract_pdfs_full_content (convert to PDF) |
| Plain Text | Direct parsing | Text processing |

### Resume Sources

| File Type | Processing Method | Tool Support |
|-----------|-------------------|--------------|
| PDF Resume | Text extraction | extract_pdfs_full_content |
| Word Document | Text extraction | extract_pdfs_full_content (convert to PDF) |
| Markdown | Direct parsing | Text processing |
| Plain Text | Direct parsing | Text processing |
| Image Resume | OCR recognition | images_understand |

### Processing Flow

```
Input Recognition → Format Detection → Content Extraction → Text Standardization → Structured Parsing
```

## Workflow

### Step 1: Content Parsing

**Parsing Content**:

**JD Parsing Items**:

- Must-Have Skills
- Nice-to-Have Skills
- Years of Experience
- Education Requirements
- Industry Background
- Certifications
- Soft Skills

**Resume Parsing Items**:

- Work Experience
- Projects
- Technical Skills
- Education
- Industry Experience
- Certifications
- Soft Skills

### Step 2: Information Extraction

Extract key information using structured format:

```json
{
  "jd": {
    "must_have_skills": ["Python", "SQL", "Machine Learning"],
    "nice_to_have_skills": ["AWS", "Docker"],
    "min_experience_years": 3,
    "education": "本科",
    "industry": "互联网/科技",
    "certifications": [],
    "soft_skills": ["沟通能力", "团队协作"]
  },
  "resume": {
    "skills": ["Python", "SQL", "Tableau", "Excel"],
    "experience_years": 5,
    "education": "硕士",
    "industries": ["金融", "互联网"],
    "certifications": ["PMP"],
    "soft_skills": ["项目管理", "数据分析"]
  }
}
```

### Step 3: Multi-dimensional Matching Analysis

| Matching Dimension | Weight | Calculation Method | Scoring Criteria |
|-------------------|--------|-------------------|------------------|
| Must-Have Skills | 35% | Matched count / Required count | 100%/80%/60%/40%/0% |
| Nice-to-Have Skills | 15% | Matched count / Provided count | 100%/80%/60%/40%/0% |
| Experience Years | 20% | Satisfaction level | Exceed(100%)/Meet(100%)/Close(80%)/Insufficient(50%)/Major gap(20%) |
| Education | 10% | Satisfaction level | Exceed(100%)/Meet(100%)/Close(80%)/Insufficient(50%) |
| Industry Background | 10% | Industry overlap | Perfect match(100%)/Related(70%)/Cross-industry(40%)/Unrelated(0%) |
| Certifications | 10% | Match degree | Perfect match(100%)/Partial match(60%)/None(0%) |

### Step 4: Gap Analysis

Identify the following types of gaps:

- Gap Type A - Critical Gap (Must-Have)
- Gap Type B - Minor Gap (Nice-to-Have)
- Gap Type C - Strengths (Resume exceeds JD requirements)

### Step 5: Report Generation

## Output Format

### Matching Overview

```
+------------------------------------------+
|         JD-Resume Matching Report         |
+------------------------------------------+
|  Overall Match Rate: ████████░░ 78%     |
|                                          |
|  Match Level: [Good]                     |
|  Suggestion: Meets requirements,        |
|              targeted improvement needed |
+------------------------------------------+
```

### Detailed Dimension Analysis

```
## 1. Must-Have Skills (35%)
Required: Python, SQL, Machine Learning, Deep Learning, NLP
Matched: Python ✓, SQL ✓, Machine Learning ✓
Unmatched: Deep Learning ✗, NLP ✗
Match Rate: 60% (3/5)
Contribution Score: 21/35

## 2. Nice-to-Have Skills (15%)
Required: AWS, Docker, Kubernetes
Resume skills: Python, SQL, Tableau, Excel
Matched: None
Match Rate: 0% (0/3)
Contribution Score: 0/15

[Other dimensions...]
```

### Improvement Suggestions

```
## Targeted Improvement Suggestions

### Immediate Action (Critical)
1. Deep learning Deep Learning theory, master CNN/RNN core models
2. Complete NLP-related projects, accumulate text processing experience

### Recommended Learning (Bonus)
3. Understand AWS cloud services basics for cloud deployment
4. Learn Docker basic containerization technology

### Highlight Strengths (Emphasize in Resume)
5. Emphasize 5 years of data analysis experience, exceeding requirements
6. Highlight Machine Learning application achievements in finance
```

## Usage Scenarios

### Scenario 1: URL-based JD Analysis
```
User Input: "Analyze this resume against the JD from https://example.com/job/123"
Trigger: URL content extraction + matching analysis
```

### Scenario 2: Image-based JD Analysis
```
User Input: "Compare my resume with this job posting [screenshot attached]"
Trigger: OCR + matching analysis
```

### Scenario 3: Document-based Resume Analysis
```
User Input: "Upload my resume (PDF) and analyze against this JD"
Trigger: Document parsing + matching analysis
```

### Scenario 4: Mixed Format Analysis
```
User Input: "Analyze my Word resume against the JD screenshot I uploaded"
Trigger: Multi-format processing + matching analysis
```

### Scenario 5: Interview Preparation
```
User Input: "What skills do I need to add before applying for this position?"
Trigger: Gap analysis + priority recommendations
```

### Scenario 6: Batch Screening
```
User Input: "Which of these three candidates best matches the position?"
Trigger: Multi-candidate comparison mode
```

## Best Practices

1. **Input Quality**: Ensure JD and resume content is complete and accurate
2. **Format Selection**: Use the most appropriate format for your materials
3. **Context Supplement**: Provide additional notes if special requirements exist
4. **Iterative Optimization**: Re-analyze after targeted adjustments
5. **Multi-round Comparison**: Compare horizontally when applying to multiple positions

## Notes

- Analysis is based on text content recognition and may be affected by formatting
- Recommend combining with human judgment and actual circumstances
- Weights of certifications and experience can be adjusted based on industry characteristics
