---
name: evomaster
description: Build evolving autonomous scientific research agents using EvoMaster framework. Use when users want to create AI agents, build scientific research assistants, implement MCP tool integration, develop multi-agent systems, or need autonomous ML/AI research capabilities. Triggers: "create agent", "build scientific agent", "EvoMaster", "autonomous research", "ML-Master", "X-Master", "Browse-Master", "multi-agent system".
---

# EvoMaster - Universal Scientific Research Agent Framework

## Overview

EvoMaster is a lightweight yet powerful framework designed to enable researchers and developers to rapidly build their own scientific agents, free from the engineering burden of tool calling, skill composition, memory storage, and more.

## Key Features

### 1. Universal Compatibility
- Supports MCP tool calling and Skills integration
- Integrates with mainstream technology stacks in the agent landscape
- Single line of configuration for tool integration

### 2. Rapid Development
- Plug-and-play components for quick start
- **~100 lines of code** to spin up a custom agent
- No need to rewrite core logic

### 3. Autonomous Agent Evolution
- Create new agents based on EvoMaster framework
- Orchestrate multiple existing agents through natural language
- Self-iteration and evolution of agent ecosystem

### 4. SciMaster Ecosystem
Pre-built agents available:

| Agent Name | Domain | Status |
|------------|--------|--------|
| ML-Master 2.0 | Autonomous Machine Learning | Available |
| ML-Master | Autonomous Machine Learning | Available |
| X-Master | General Scientific Agent | Available |
| Browse-Master | Web Search Agent | Available |
| PhysMaster | Physics Research & Reasoning | Coming Soon |
| EmboMaster | Embodied Intelligence Training | Coming Soon |

## Project Architecture

```
EvoMaster/
├── evomaster/         # Core library
│   ├── agent/        # Agent components (Agent, Session, Tools)
│   ├── core/         # Workflow (Exp, Playground)
│   ├── env/          # Environment (Docker, Local)
│   ├── interface/    # External interfaces (Feishu, etc.)
│   ├── memory/       # Memory system
│   ├── skills/       # Skill system
│   ├── skills_ts/    # TypeScript skills (OpenClaw bridge)
│   └── utils/        # Utilities (LLM, Types)
├── playground/       # Playground implementations
├── configs/          # Configuration files
└── docs/             # Documentation
```

## Installation

### With pip
```bash
git clone https://github.com/sjtu-sai-agents/EvoMaster.git
cd EvoMaster
pip install -r requirements.txt
```

### With uv (Recommended)
```bash
uv sync
```

## Configuration

### 1. Environment Variables (.env)
```bash
cp .env.template .env
# Edit .env with your API keys:
DEEPSEEK_API_KEY="your-api-key-here"
DEEPSEEK_API_BASE="http://127.0.0.1:18889/v1"
```

### 2. Config File
Edit `configs/[playground name]/[config-file].yaml`:
```yaml
local_sglang:
  provider: "deepseek"
  model: "deepseek-v3.2"
  api_key: "dummy"
  base_url: "http://192.168.2.110:18889/v1"
```

## Basic Usage

### Single Agent (Minimal)
```bash
python run.py --agent minimal --task "Your task description"
```

### With Custom Config
```bash
python run.py --agent minimal --config configs/minimal/config.yaml --task "Your task description"
```

### With Image Input
```bash
python run.py --agent minimal --config configs/minimal/deepseek-v3.2-example.yaml --task "Describe what you see in these images" --images /path/to/image1.png
```

### With TypeScript-format Skill
```bash
python run.py --agent minimal_openclaw_skill --config configs/minimal_openclaw_skill/config.yaml --task "Summarize the content of this Feishu document"
```

## Usage Examples

### Simple Multi-Agent System
```bash
python run.py --agent minimal_multi_agent --config configs/minimal_multi_agent/deepseek-v3.2-example.yaml --task "Write a Python program that implements word count analysis"
```

### Multi-Agent Parallel Execution
```bash
python run.py --agent minimal_multi_agent_parallel --config configs/minimal_multi_agent_parallel/deepseek-v3.2-example.yaml --task "Write a Python program..."
```

### ML-Master (Autonomous Machine Learning)
```bash
pip install -r playground/ml_master/requirements.txt
python run.py --agent ml_master --config configs/ml_master/config.yaml --task /data/exp_data/detecting-insults/prepared/public/description.md
```

### ML-Master 2.0
```bash
pip install -r playground/ml_master_2/requirements.txt
python run.py --agent ml_master_2 --config configs/ml_master_2/deepseek-v3.2-example.yaml --task playground/ml_master_2/data/detecting-insults/prepared/public/description.md
```

### X-Master (General Scientific Agent)
```bash
pip install -r playground/x_master/mcp_sandbox/requirements.txt
python run.py --agent x_master --task "Which condition of Arrhenius's sixth impossibility theorem do critical-level views violate?"
```

### Browse-Master (Web Search Agent)
```bash
pip install -r playground/browse_master/mcp_sandbox/requirements.txt
python run.py --agent browse_master --config configs/browse_master/config.yaml --task "I am searching for the pseudonym of a writer..."
```

### Kaggle Automation
```bash
pip install -r playground/minimal_kaggle/requirements.txt
python run.py --agent minimal_kaggle --config configs/minimal_kaggle/deepseek-v3.2-example.yaml --task playground/minimal_kaggle/data/public/description.md
```

## Creating Custom Agents

### Minimal Agent Example (~100 lines)

```python
from evomaster.agent import Agent
from evomaster.core import Workflow
from evomaster.utils import LLMClient

# 1. Configure LLM
llm = LLMClient(provider="openai", model="gpt-4", api_key="your-key")

# 2. Create Agent
agent = Agent(
    name="my-research-agent",
    llm=llm,
    skills=["web_search", "code_execution"],
    memory_enabled=True
)

# 3. Define Workflow
workflow = Workflow(agent=agent)

# 4. Run Task
result = workflow.run(task="Your research task")
print(result)
```

## Roadmap

| Phase | Version | Content | Status |
|-------|---------|---------|--------|
| Current | v0.0.x | Core framework, basic documentation | Completed |
| Phase 1 | v0.1.x | Open-source SciMaster series agents | Completed |
| Phase 2 | v0.2.x | MagiClaw Feishu intelligent assistant | In Progress |
| Phase 3 | v0.3.x | Bohrium Tool Library (30,000+ scientific tools) | Exploring |

## Resources

- GitHub: https://github.com/sjtu-sai-agents/EvoMaster
- Documentation: https://github.com/sjtu-sai-agents/EvoMaster/blob/main/docs/README.md
- Playground: https://github.com/sjtu-sai-agents/EvoMaster/blob/main/playground/README.md

## License

Apache-2.0
