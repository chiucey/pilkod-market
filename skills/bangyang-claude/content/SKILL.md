---
name: bangyang-claude
description: Use when user asks to write in a specific style, imitate a role model, generate a system prompt, create few-shot examples, or analyze conversational patterns from datasets.
---

# Bangyang-Claude Style Mimicry Skill

## Purpose

This skill enables style mimicry - generating content that matches the conversational patterns, language style, and behavioral characteristics found in reference datasets.

## When to Activate

Activate when user asks for:
- "Write in the style of..." or "imitate..."
- "Generate a system prompt based on..."
- "Create few-shot examples from..."
- "Analyze patterns from dataset"
- `/bangyang` command invoked

## How to Use This Skill

### Step 1: Load Style Profile

Read the style profile to understand the reference patterns:

```
references/bangyang_style_profile.json
```

The profile contains 85 style atoms across 4 dimensions:
- **System Prompt Patterns** (17): Role definitions, behavioral constraints
- **Dialogue Structure Patterns** (20): Turn-taking, CoT patterns
- **Language Style Atoms** (22): Tone, formality, expressions
- **Content Organization Atoms** (26): Opening, closing, structure

### Step 2: Load System Prompt Template

```
references/bangyang_system_prompt_template.md
```

This template provides:
- Role definition guidelines
- Behavioral rules extracted from dataset
- Language style guidelines
- Content organization templates

### Step 3: Generate Style-Specific Output

When generating content in the Bangyang-Claude style:

1. **Role Setting**: Start with minimal role definition ("You are a helpful AI assistant")
2. **Language Tone**: Use formal academic tone with guiding opening ("Let me analyze...", "Let me work through...")
3. **Structure**: Use Step 1/2/3 markers, Markdown formatting, tables
4. **Content Organization**: Answer-first, then explain, with verification marks
5. **CoT Pattern**: Include `<thinking>` tags for reasoning when appropriate

### Quick Reference

| Style Element | Bangyang-Claude Pattern |
|---------------|------------------------|
| Role | Minimal ("helpful AI assistant") |
| Opening | Answer-first, then explain |
| Tone | Formal, academic, guiding |
| Structure | Step-by-step with markers |
| Verification | Check marks, "Verification:" labels |
| Math | LaTeX format, equation embedding |
| Closing | Summary repetition |

## Data Sources

| Dataset | Quality Weight | Sample Count | Characteristics |
|---------|---------------|--------------|----------------|
| claude_opus | 1.0 | 50 | Multi-domain expert consultant style |
| distilled_cot | 0.6 | 80 | Chain-of-Thought reasoning style |
| distilled_stage2 | 0.7 | 70 | Academic problem-solving style |
| opus46 | 0.8 | 200 | Concise general assistant style |

**Total fused atoms: 85**

## File Locations

- Style atoms: `references/bangyang_style_profile.json`
- System prompt template: `references/bangyang_system_prompt_template.md`
- Usage guide: `references/bangyang_usage_guide.md`
- Few-shot examples: `references/bangyang_few_shot_examples.jsonl`

## Adding New Reference Datasets

To extend the style profile:

1. Analyze new dataset with `analyze_dataset.py`
2. Sample representative records with `sample_dataset.py`
3. Use Agent to extract patterns
4. Fuse patterns with `unify_patterns.py`
5. Regenerate skill with `generate_skill.py`
