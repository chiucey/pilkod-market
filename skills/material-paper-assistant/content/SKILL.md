---
name: material-paper-assistant
description: Academic paper writing assistant for materials science. Use when users need to write, revise, or polish academic papers in materials science, including providing standardized paper formats, structural suggestions, Chinese-English translation, content simplification or expansion. Trigger phrases: "write paper", "revise paper", "polish paper", "translate to English", "write abstract", "materials paper structure", "academic paper format"
---

# Materials Science Academic Paper Writing Assistant

## Core Capabilities

1. **Paper Structure Standardization** - Provide standard IMRAD structure with materials science-specific sections
2. **Format Templates** - ACS, Elsevier, Springer, and other major journal formats
3. **Content Revision** - Rewrite content following standardized academic writing patterns
4. **Chinese-English Translation** - Accurate translation of materials science terminology
5. **Simplification/Expansion** - Adjust content detail level based on requirements

## Workflow

### Step 1: Understand Requirements

Confirm the following:
- Target journal (ACS Materials / ACS Applied Materials / Nature Materials / Science / Other)
- Paper type (Research Article / Review / Letter / Perspective)
- Language requirement (Chinese / English)
- Specific task type

### Step 2: Structure Suggestions

Provide standard structure based on journal requirements:

```
Standard IMRAD Structure:
├── Title
├── Abstract - 200-300 words, including background/methods/results/conclusions
├── Keywords - 5-7 terms
├── Introduction - Research background -> Research gap -> Research objective
├── Experimental/Methods
├── Results and Discussion
├── Conclusions
├── Supporting Information
└── References
```

### Step 3: Content Generation/Revision

**When generating new content:**
- Use standardized academic expressions
- Follow journal style guidelines
- Standardize materials science terminology

**When revising existing content:**
- Preserve original meaning
- Follow high-quality paper writing patterns
- Improve academic expression standardization

### Step 4: Language Processing

**Key points for Chinese to English translation:**
- Use materials science standard terminology
- Pay attention to tense (past tense for experiments, present tense for conclusions)
- Standardize passive voice usage
- Standardize figure and table descriptions

## Common Sentence Templates

### Introduction
```
[Research field] has attracted significant attention due to [research significance]
However, [existing problem/gap] remains a challenge
Herein, we report [research content] for the first time
We demonstrate that [main finding]
```

### Methods
```
The [material name] was synthesized via [method]
[Characterization technique] was performed using [equipment model]
The crystal structure was confirmed by [technique name]
```

### Results
```
As shown in Figure 1, [observation result]
The diffraction peaks at [angle] correspond to [crystallographic plane]
The morphology exhibits [characteristic description]
```

### Conclusions
```
In summary, we have developed [system] with [performance]
The [mechanism] was revealed through [analysis]
This work provides insights into [application field]
```

## Journal Format References

Different journals have different requirements. Refer to format specification files in the `references/` directory:
- `acs_format.md` - ACS journal format guide
- `elsevier_format.md` - Elsevier journal format guide
- `materials_terms.md` - Materials science terminology glossary

## Important Notes

1. **Data Consistency** - All data, figures, and citations must be consistent throughout the paper
2. **Logical Coherence** - Clear logic and smooth transitions between sections
3. **Terminology Consistency** - Use the same terminology consistently throughout
4. **Plagiarism Control** - Pay attention to originality and citation standards
