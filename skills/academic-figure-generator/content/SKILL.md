---
name: academic-figure-generator
description: Professional skill for generating academic figures for research papers. Use when users request architecture diagrams, flowcharts, model schematics, data flow diagrams, or experimental visualizations for papers. Trigger phrases include: generate academic figures for paper, paper illustrations, academic images, architecture diagram, model schematic, algorithm flowchart, research framework, paper figure creation.
---

# Academic Figure Generator

## Core Capabilities

Generate high-quality academic figures for research papers, not only displaying surface information but deeply presenting principle-level academic content.

## Workflow

### Phase 1: Information Gathering and Requirements Analysis

1. **Collect Paper Information**
   - Paper topic and research domain
   - Core methods and innovations
   - Key technical architecture
   - Target audience (conference/journal)

2. **Determine Figure Type**
   - Model Architecture Diagram
   - Algorithm Pipeline Flowchart
   - Data Flow Diagram
   - Network Structure Diagram
   - Comparison Results Chart
   - System Framework Diagram
   - Mathematical Formula Visualization

### Phase 2: Literature Search and Principle Research

1. **Search for Relevant Academic Architecture Diagrams**
   - Use `batch_web_search` to search for architecture diagrams from top conferences in the field
   - Search for classic paper illustration styles in the domain
   - Find reference diagrams from similar research

2. **Extract Key Visual Elements**
   - Standard graphical symbols and notations
   - Color coding conventions
   - Layout and hierarchical structure patterns
   - Labeling and annotation styles

### Phase 3: Figure Design and Generation

1. **Principle-Level Design**
   - Ensure graphics accurately reflect technical principles
   - Use standard academic notations
   - Clearly show data flow and processing steps
   - Accurately label key parameters and variables

2. **Generate Using image_synthesize**
   - Build precise prompts based on figure type
   - Include style requirements (academic, minimalist, high contrast)
   - Specify output format and dimensions
   - Add necessary detail descriptions

### Phase 4: Quality Optimization and Delivery

1. **Check Figure Quality**
   - Clarity: text and graphic edges are sharp
   - Accuracy: principle expression is correct
   - Readability: clear hierarchy, emphasis on key points
   - Academic standards: conforms to domain conventions

2. **Save and Output**
   - Save as high-resolution PNG/SVG format
   - Provide paper-ready dimension versions
   - Ensure complete academic citation annotations

## Output Specifications

### Required Outputs
- Primary figure file (PNG format, resolution >= 300 DPI)
- Optional SVG vector version (for easy editing)
- Usage recommendations and format instructions

### Figure Style Requirements
- Academic style: clean, professional, high contrast
- Color scheme: blue-gray primary, adjustable per domain
- Typography: clear and readable, primarily English
- Layout: clear visual hierarchy

## Prompt Construction Guide

### Model Architecture Diagram Prompt Template
```
[Style] Professional academic paper figure, [Subject] architecture diagram of [Model Name],
showing [main components: encoder, decoder, attention layers],
data flow from [input] to [output] with [specific mechanisms],
clean layout with labeled boxes, arrows indicating information flow,
minimalist academic style, high contrast, [specific color scheme],
white background, publication-quality, [dimensions if specified]
```

### Algorithm Flowchart Prompt Template
```
[Style] Academic flowchart for [Algorithm Name],
showing step-by-step process from [start] to [end],
with [decision points], [loops], [parallel processes],
clean geometric shapes, numbered steps,
professional academic diagram style, [specific color scheme],
white background, publication-quality
```

### System Framework Diagram Prompt Template
```
[Style] System architecture diagram for [Application Domain],
showing [main modules], [data sources], [outputs],
with [interactions] and [dependencies] clearly indicated,
professional academic illustration style,
clean layout, labeled components, [specific color scheme],
white background, publication-quality
```

## Quality Checklist

- [ ] Figure clarity: 300 DPI or higher
- [ ] Principle accuracy: technical details correct
- [ ] Visual hierarchy: primary information highlighted
- [ ] Label completeness: all elements labeled
- [ ] Academic standards: conforms to domain conventions
- [ ] Copyright compliance: original or properly cited

## Applicable Domains

- Deep Learning and Machine Learning
- Computer Vision
- Natural Language Processing
- Biomedical Engineering
- Reinforcement Learning
- Graph Neural Networks
- Multimodal Learning
- Other AI/ML Research Domains
