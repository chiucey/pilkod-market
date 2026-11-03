# Bangyang-Claude Style Mimicry Skill - Usage Guide

## Overview

Bangyang-Claude is a style mimicry skill that enables LLM output to imitate conversational patterns from reference datasets.

## Contents Included

- **System Prompt Template**: Role definitions, behavioral rules, language style guidelines, content organization templates
- **Few-shot Examples**: Representative conversation examples selected from datasets
- **Style Profile**: Structured style atom configuration (85 total patterns/atoms)

## Data Sources

- claude_opus (Quality Weight: 1.0)
- opus46 (Quality Weight: 0.8)
- distilled_stage2 (Quality Weight: 0.7)
- distilled_cot (Quality Weight: 0.6)

## Usage Methods

### 1. System Prompt Injection

Use the contents of `bangyang_system_prompt_template.md` as the system prompt.

### 2. Few-shot Examples

When conversing, inject examples from `bangyang_few_shot_examples.jsonl` as few-shot examples.

### 3. Style Profile

`bangyang_style_profile.json` contains the complete style atom configuration for programmatic processing.

## Style Dimensions Coverage

| Dimension | Pattern Count |
|-----------|--------------|
| System Prompt Role Definition | 17 |
| Dialogue Structure Patterns | 20 |
| Language Expression Style | 22 |
| Content Organization | 26 |

## Extension Guide

To add new reference datasets:

1. Use `scripts/analyze_dataset.py` to analyze new datasets
2. Use `scripts/sample_dataset.py` to sample representative data
3. Use Agent to analyze patterns in new datasets
4. Use `scripts/unify_patterns.py` to fuse new patterns
5. Use `scripts/generate_skill.py` to regenerate the Skill
