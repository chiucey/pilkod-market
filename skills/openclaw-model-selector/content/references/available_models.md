# OpenClaw Available Models Reference

## Model List

### Anthropic Claude Series

| Model | Name | Context Window | Speed | Best For |
|-------|------|----------------|-------|----------|
| opus | Claude Opus | 200K tokens | Slow | Deep research, complex reasoning, system design |
| sonnet | Claude Sonnet | 200K tokens | Medium | Balanced tasks, code, analysis |
| haiku | Claude Haiku | 200K tokens | Fast | Quick Q&A, daily tasks |
| claude-code | Claude Code | 200K tokens | Medium | Programming tasks, code debugging |

### OpenAI GPT Series

| Model | Name | Context Window | Speed | Best For |
|-------|------|----------------|-------|----------|
| gpt-4 | GPT-4 | 128K tokens | Slow | Complex reasoning, creative writing, math |
| gpt-4-turbo | GPT-4 Turbo | 128K tokens | Medium | Balanced tasks, high-quality output |
| gpt-3.5-turbo | GPT-3.5 Turbo | 16K tokens | Fast | Simple tasks, quick response |

## Selection Guide

### By Speed

- **Need instant response**: Haiku / GPT-3.5-Turbo
- **Balance speed and quality**: Sonnet / GPT-4-Turbo
- **Quality priority**: Opus / GPT-4

### By Task

| Task Type | Recommended Model | Reason |
|-----------|------------------|--------|
| Code generation/debugging | Claude Code / Sonnet | Strong code understanding |
| Creative writing | GPT-4 / Opus | High creativity and fluency |
| Technical analysis | Opus / Sonnet | Strong reasoning ability |
| Quick Q&A | Haiku / GPT-3.5 | Low latency, cost-effective |
| Long document processing | Opus / Sonnet | Large context window |
| Math computation | GPT-4 / Opus | High accuracy |
| Translation | GPT-4 / Sonnet | Strong multilingual ability |

### By Complexity

- **Simple tasks** (one-line Q&A, simple queries):
  - Primary: Haiku / GPT-3.5-Turbo
  - Backup: Sonnet

- **Medium tasks** (code snippets, short writing, explanations):
  - Primary: Sonnet / GPT-4-Turbo
  - Backup: Opus

- **Complex tasks** (complete projects, system design, long documents):
  - Primary: Opus / GPT-4
  - Backup: Sonnet

## Cost Considerations

- **Free/Low cost**: Haiku, GPT-3.5-Turbo
- **Medium cost**: Sonnet, GPT-4-Turbo
- **High cost**: Opus, GPT-4

It is recommended to select the appropriate model based on task complexity to optimize costs.
