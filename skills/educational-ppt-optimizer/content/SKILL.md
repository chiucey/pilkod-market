---
name: educational-ppt-optimizer
description: 教学PPT设计优化助手。当用户需要将HTML转换为PPT、分析教学设计PPT质量、优化PPT结构布局、改进视觉设计、提升教学效果时使用。支持HTML到PPTX转换、PPT内容分析、设计原则诊断和优化建议。
---

# Educational PPT Optimizer

教学PPT设计优化助手，支持HTML转PPT、PPT内容分析和设计优化。

## Core Capabilities

### 1. HTML to PPT Conversion

Convert HTML files to PowerPoint presentations while preserving:
- Document structure (headings, paragraphs, lists)
- Basic formatting (bold, italic, lists)
- Tables and basic styling
- Images (referenced by URL or local path)

### 2. PPT Analysis & Evaluation

Analyze educational PPTs against design principles:
- **MagicSeven Principle**: 5-9 concepts per slide
- **KISS Principle**: Keep content simple and stupid
- **10/20/30 Rule**: Max 10 slides, 20 min, 30pt font
- **Three-No Principle**: Max 3 fonts, 3 color schemes, 3 animations
- **Visual Design**: Layout, color scheme, typography
- **Educational Effectiveness**: Learning objectives, interactivity

### 3. PPT Optimization

Provide optimization suggestions for:
- Content simplification and key point extraction
- Layout improvement and visual hierarchy
- Color scheme optimization
- Interactive element suggestions
- Animation refinement

## Usage Examples

```markdown
用户: 将这个HTML文件转换为PPT
操作: 使用 html_to_ppt.py 转换HTML到PPTX

用户: 分析这个教学PPT的设计质量
操作: 使用 ppt_analyzer.py 进行全面分析

用户: 优化这个PPT使其更适合教学
操作: 使用 ppt_optimizer.py 提供优化建议
```

## Quick Start

### HTML to PPT Conversion

```bash
python3 /workspace/temp-skills/educational-ppt-optimizer/scripts/html_to_ppt.py \
  --input example.html \
  --output presentation.pptx \
  --theme education
```

### PPT Analysis

```bash
python3 /workspace/temp-skills/educational-ppt-optimizer/scripts/ppt_analyzer.py \
  --input presentation.pptx \
  --output analysis_report.md
```

### PPT Optimization

```bash
python3 /workspace/temp-skills/educational-ppt-optimizer/scripts/ppt_optimizer.py \
  --input presentation.pptx \
  --output optimized.pptx \
  --mode comprehensive
```

## Design Principles Reference

See `references/design_principles.md` for detailed educational PPT design guidelines.

## Technical Requirements

- Python 3.8+
- python-pptx library
- BeautifulSoup4 for HTML parsing
- lxml for XML processing

## Output Formats

- **PPTX**: Standard PowerPoint format
- **Analysis Report**: Markdown format with scoring
- **Optimization Suggestions**: JSON or Markdown format

## Workflow

```
HTML File → Parse Structure → Create Slides → Apply Theme → PPTX Output
    ↓
Existing PPT → Analyze Content → Evaluate Design → Generate Report → Optimization Suggestions
```

## Integration

This skill works with:
- HTML files (web content, course materials)
- Existing PPTX files (for analysis and optimization)
- Design reference documents (for principle-based evaluation)

## Best Practices

1. **Content First**: Ensure content quality before design optimization
2. **Simple is Better**: Follow KISS principle for educational content
3. **Visual Consistency**: Maintain uniform style throughout
4. **Student-Centered**: Design from learner's perspective
5. **Interactive Elements**: Include engagement mechanisms
