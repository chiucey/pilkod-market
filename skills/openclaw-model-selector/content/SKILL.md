---
name: openclaw-model-selector
description: Automatically selects the optimal AI model for OpenClaw based on task type. Use when users need to handle different types of tasks such as code writing, creative writing, data analysis, technical debugging, etc. This skill analyzes task characteristics and switches to the most suitable model for the current work.
---

# OpenClaw Model Auto-Selector

This skill helps OpenClaw automatically select the optimal AI model based on input tasks, improving task processing efficiency and quality.

## Workflow

### 1. Task Analysis

Analyze user input to extract key characteristics:

- **Task Type Recognition**: code, writing, analysis, creative, translation, etc.
- **Complexity Assessment**: simple query vs. complex multi-step task
- **Domain Judgment**: technical, finance, creative, legal, etc.
- **Time Requirements**: fast response needed vs. can wait for high-quality results

### 2. Model Matching

Match optimal model based on task characteristics:

| Task Type | Recommended Models | Reason |
|-----------|-------------------|--------|
| Code Writing/Debugging | Claude Code / GPT-4 | Strong coding capability, long context support |
| Creative Writing | GPT-4 / Claude | High creativity and fluency |
| Quick Q&A | GPT-3.5 / Haiku | Low latency, cost-effective |
| Complex Analysis | Claude / GPT-4 | Strong reasoning ability |
| Technical Documentation | Claude | Precise and structured |
| Math Computation | GPT-4 / Claude | High accuracy |

### 3. Model Switching

Use OpenClaw configuration command to switch models:

```
/set model <model-name>
```

## Execution Script

Call `scripts/select_model.py` for automated selection:

```bash
python scripts/select_model.py --task "<user task description>"
```

The script will:
1. Parse task characteristics
2. Query available model list
3. Output optimal model recommendation
4. Execute model switching command

## Available Models Reference

Refer to `references/available_models.md` for the complete model list and specifications.

## Example Usage

- User: "Help me write a Python quicksort function"
  → Select: Claude Code (strong code capability)

- User: "Explain the basic principles of quantum computing"
  → Select: Claude (strong explanation ability)

- User: "What's the weather like today"
  → Select: Haiku (quick response sufficient)
