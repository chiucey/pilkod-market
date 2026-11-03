---
name: metaclaw-agent
description: MetaClaw AI Agent framework skill. Use when users request creating AI agents, deploying MetaClaw, configuring agent skills, auto RL training, agent scheduling optimization, or building self-evolving intelligent assistants.
---

# MetaClaw Agent Framework Skill

## Overview

MetaClaw is an agent framework that enables meta-learning and continuous evolution in production environments. Inspired by how brains learn, it enables continuous improvement through real-world deployment rather than offline training alone.

## Core Features

### Three Operating Modes

| Mode | Description |
|------|-------------|
| `skills_only` | Proxy LLM API with skills injection. No GPU required. |
| `rl` | Skills + RL training (GRPO). Trains when batch is full. |
| `madmax` | Skills + RL + smart scheduler. RL runs during idle windows. |

### Key Capabilities

- **Skills Injection**: Automatic skill injection at every conversation turn
- **Auto-Summarization**: Automatically summarizes new skills after each session
- **RL Fine-tuning**: Supports GRPO reinforcement learning from live conversations
- **Multi-Claw Support**: OpenClaw, CoPaw, IronClaw, PicoClaw, ZeroClaw, NanoClaw, NemoClaw
- **Asynchronous Design**: Serving, reward modeling, and training are fully decoupled
- **Scheduler**: Meta-learning scheduler with sleep/idle/calendar integration

## Installation

```bash
# Basic installation (skills_only mode - lightweight)
pip install -e .

# With RL training support
pip install -e ".[rl]"

# With skill evolution
pip install -e ".[evolve]"

# With Google Calendar integration
pip install -e ".[scheduler]"

# Full setup
pip install -e ".[rl,evolve,scheduler]"
```

## Quick Start

### Initial Setup

```bash
metaclaw setup  # Interactive configuration wizard
```

### Starting MetaClaw

```bash
metaclaw start              # Default: madmax mode
metaclaw start --mode rl   # RL without scheduler
metaclaw start --mode skills_only  # Skills only
```

### Basic Commands

```bash
metaclaw stop              # Stop running instance
metaclaw status            # Check proxy health and mode
metaclaw config show       # View current configuration
metaclaw config KEY VALUE  # Set config value
```

## Configuration

Configuration file: `~/.metaclaw/config.yaml`

### Key Configuration Options

```yaml
mode: madmax                    # "madmax" | "rl" | "skills_only"
claw_type: openclaw            # agent type
llm:
  provider: kimi               # kimi | qwen | openai | minimax | custom
  model_id: moonshotai/Kimi-K2.5
  api_base: https://api.moonshot.cn/v1
  api_key: sk-...
proxy:
  port: 30000
skills:
  enabled: true
  dir: ~/.metaclaw/skills
  auto_evolve: true
rl:
  enabled: false
  backend: auto                # "auto" | "tinker" | "mint"
  model: moonshotai/Kimi-K2.5
  lora_rank: 32
  batch_size: 4
scheduler:
  enabled: false
  sleep_start: "23:00"
  sleep_end: "07:00"
  idle_threshold_minutes: 30
```

## Architecture

### Component Overview

| Component | Description |
|-----------|-------------|
| `metaclaw` | Main CLI package |
| `proxy` | Transparent proxy intercepting agent interactions |
| `skills` | Skill injection and auto-summarization system |
| `rl` | Reinforcement learning training (GRPO) |
| `scheduler` | Meta-learning scheduler for idle windows |
| `claw_adapter` | Adapter layer supporting multiple claw variants |

### Multi-Claw Support

MetaClaw supports multiple personal agent types:
- **OpenClaw**: Standard open-source agent
- **CoPaw**: Collaborative agent
- **IronClaw**: Heavy-duty agent
- **PicoClaw**: Lightweight agent
- **ZeroClaw**: Zero-configuration agent
- **NanoClaw**: Minimal agent (Anthropic-compatible endpoint)
- **NemoClaw**: Specialized agent

## Use Cases

### Building a Self-Evolving Assistant

1. Install MetaClaw with full dependencies
2. Run `metaclaw setup` to configure LLM provider
3. Start with `metaclaw start --mode skills_only` for initial learning
4. Enable RL training during idle periods
5. Monitor evolution through `metaclaw status`

### Custom Skill Development

Create skills in `~/.metaclaw/skills/` directory:
- Skills are automatically injected at each conversation turn
- New skills are auto-summarized after each session
- Skills can trigger RL training for improvement

### RL Training Setup

1. Configure RL backend (Tinker or MinT)
2. Set training parameters (batch size, LoRA rank)
3. Enable OPD (On-Policy Distillation) for teacher distillation
4. Schedule training during low-usage windows

## Backend Support

### Tinker Backend
[Thinking Machines Tinker](https://www.thinkingmachines.ai/tinker/) for RL training.

### MinT Backend
Install [mindlab-toolkit](https://github.com/MindLab-Research/mindlab-toolkit) for MinT backend support.

### OpenRouter Support
MetaClaw supports OpenRouter LLM platform for flexible model selection.

## Related Projects

- [OpenClaw](https://openclaw.ai/) - Base agent framework
- [SkillRL](https://github.com/aiming-lab/SkillRL) - RL for skills
- [Tinker](https://www.thinkingmachines.ai/tinker/) - RL training backend
- [MinT](https://github.com/MindLab-Research/mindlab-toolkit) - Alternative RL backend

## License

MIT License

## References

- GitHub: https://github.com/aiming-lab/MetaClaw
- Documentation: Available in 12 languages (Chinese, Japanese, Korean, French, German, Spanish, Portuguese, Russian, Italian, Vietnamese, Arabic, Hindi)
