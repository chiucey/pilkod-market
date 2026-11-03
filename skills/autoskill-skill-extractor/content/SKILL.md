---
name: autoskill-skill-extractor
description: Experience-driven skill self-evolution and extraction. Use when users want to extract reusable skills from AI conversations, maintain skill libraries, evolve skills through version updates, or implement lifelong learning for AI agents. Triggers: "extract skills from conversation", "create skill from chat", "skill evolution", "maintain skill library", "skill versioning"
---

# AutoSkill: Experience-Driven Skill Self-Evolution

## Overview

AutoSkill is an **experience-driven lifelong learning (ELL)** system that enables AI agents to automatically extract reusable skills from real interaction experiences, continuously evolve them through merge and version updates, and retrieve them for future similar tasks.

## Core Concepts

### What is a Skill?

A **Skill** is a reusable capability artifact defined in `SKILL.md` format with:
- **Metadata**: name, description, trigger phrases
- **Instructions**: detailed implementation steps
- **References**: supporting materials and examples
- **Version history**: evolution through updates

### Skill Lifecycle

1. **Extraction**: Detect durable constraints from interactions, extract/merge skills (v0.1.0)
2. **Update**: Apply user feedback to evolve skills (v0.1.1, v0.1.2...)
3. **Usage**: Retrieve and inject skills for similar future tasks

## Usage Patterns

### 1. Extract Skills from Conversations

When users provide conversation logs or chat data:

```python
from autoskill import AutoSkill, AutoSkillConfig

sdk = AutoSkill(AutoSkillConfig(
    llm={"provider": "dashscope"},  # or openai, anthropic, etc.
    embeddings={"provider": "hashing", "dims": 256},
    store={"provider": "local", "path": "SkillBank"},
))

# Ingest conversation messages
sdk.ingest(user_id="user123", messages=[
    {"role": "user", "content": "Help me review code..."},
    {"role": "assistant", "content": "Here's the code review..."},
])

# AutoSkill automatically extracts durable patterns
```

### 2. Search and Retrieve Skills

```python
# Search for relevant skills based on query
hits = sdk.search("code review best practices", user_id="user123", limit=3)

# Use retrieved skills as context for new tasks
for hit in hits:
    print(f"Skill: {hit.skill.name}, Relevance: {hit.score}")
    print(hit.skill.render())  # Get injectable context
```

### 3. Skill Version Evolution

Skills automatically evolve when:
- New patterns are detected in interactions
- User provides feedback or corrections
- Similar skills can be merged

```python
# Skills maintain version history
skill = sdk.get_skill(skill_id="code-reviewer")
print(f"Current version: {skill.version}")
# Automatic merge/update decisions based on usage patterns
```

### 4. Offline Conversation Extraction

For importing existing conversation logs:

```bash
python -m autoskill.offline.conversation.extract \
    --file ./conversations.jsonl \
    --user-id user123 \
    --llm-provider dashscope
```

### 5. Document-Based Skill Extraction (AutoSkill4Doc)

Extract skills from documentation:

```bash
python -m AutoSkill4Doc llm-extract \
    --file ./docs \
    --domain psychology
```

## SkillBank Storage Structure

```
SkillBank/
├── Users/
│   └── <user_id>/
│       └── <skill_id>/
│           ├── SKILL.md          # Main skill definition
│           ├── scripts/          # Supporting code
│           ├── references/       # Reference materials
│           └── assets/           # Images/attachments
├── Common/
│   └── SKILL.md                  # Shared skills
├── vectors/                      # Embedding vectors
└── index/                        # Search index
```

## LLM Provider Configuration

Supported providers:
- **DashScope**: Alibaba's Qwen models
- **GLM/BigModel**: Zhipu AI
- **OpenAI**: GPT-4, GPT-3.5
- **Anthropic**: Claude
- **InternLM**: Shanghai AI Lab models
- **Generic URL**: Custom API endpoints

```python
config = AutoSkillConfig(
    llm={
        "provider": "dashscope",
        "model": "qwen-max",
        "api_key": os.getenv("DASHSCOPE_API_KEY")
    }
)
```

## Integration Examples

### Web UI Deployment

```bash
python3 -m pip install -e .
export INTERNLM_API_KEY="your-key"
export DASHSCOPE_API_KEY="your-key"
python3 -m examples.web_ui --host 0.0.0.0 --port 8000
```

### OpenAI-Compatible Proxy

```bash
python3 -m examples.openai_proxy --host 0.0.0.0 --port 9000
```

Then use with any OpenAI-compatible client:

```python
import openai
client = openai.OpenAI(base_url="http://localhost:9000/v1")
response = client.chat.completions.create(
    model="autoskill",
    messages=[{"role": "user", "content": "Review my PR..."}]
)
```

### Docker Deployment

```bash
cp .env.example .env
# Edit .env with your API keys
docker compose up --build -d
```

## API Endpoints (Proxy Mode)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/chat/completions` | POST | Chat with skill retrieval |
| `/v1/embeddings` | POST | Generate embeddings |
| `/v1/autoskill/skills` | GET | List all skills |
| `/v1/autoskill/skills/{id}/md` | GET | Get skill as Markdown |
| `/v1/autoskill/conversations/import` | POST | Import conversation logs |
| `/v1/autoskill/extractions` | POST | Trigger skill extraction |

## Best Practices

### When to Extract Skills

Extract skills when:
- User establishes persistent rules/patterns
- Repeated tasks with similar structure
- Valuable domain knowledge demonstrated
- Successful problem-solving approaches

### Skill Granularity

- **Coarse-grained**: Complete workflows (e.g., "Full Stack Web Development")
- **Fine-grained**: Single operations (e.g., "Python List Comprehension")

Balance based on reusability and composability.

### Maintenance

- Monitor skill usage metrics
- Merge similar skills periodically
- Archive unused skills
- Update skills based on feedback

## Architecture Components

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│  (Web UI, CLI, API Proxy, SDK)                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      AutoSkill Core                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Extraction   │  │ Maintenance  │  │ Retrieval    │    │
│  │ Engine       │  │ Manager      │  │ Engine        │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     SkillBank (Storage)                      │
│  Skills │ Vectors │ Index │ Metadata                        │
└─────────────────────────────────────────────────────────────┘
```

## Citation

```bibtex
@software{autoskill_2026,
  author = {Yutao Yang, Junsong Li, Qianjun Pan, et al.},
  title = {AutoSkill: Experience-Driven Lifelong Learning via Skill Self-Evolution},
  year = {2026},
  url = {https://github.com/ECNU-ICALK/AutoSkill}
}
```
