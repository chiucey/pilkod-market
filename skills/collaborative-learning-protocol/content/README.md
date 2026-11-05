# Collaborative Learning Protocol

A protocol for safely sharing non-sensitive experiences between multiple agents or different sessions of the same user.

## Features

- **Experience Recording** - Capture execution experiences in a standardized format
- **Skill Templates** - Share reusable solution patterns
- **Avoidance Guides** - Document lessons learned from failures
- **Multi-instance Sync** - Share knowledge across agent instances
- **Sensitive Info Detection** - Automatic sanitization of sensitive data
- **Experience Integration** - Combine multiple experiences into knowledge graphs

## Quick Start

```python
from collaborative_protocol import create_protocol

# Create protocol instance
protocol = create_protocol(
    instance_id="my-instance",
    knowledge_base_path="./knowledge_base"
)

# Record an experience
with protocol.recorder.session(task_type="code_generation") as session:
    session.record_step("analysis", input_data={...}, output_data={...})
    session.finalize(success=True, metrics={...})

# Extract and publish
experience = session.extract_experience(type="skill_template", title="My Template")
protocol.publisher.publish(experience)

# Search for relevant experiences
results = protocol.retriever.search(query="code optimization")
```

## Experience Types

| Type | Description |
|------|-------------|
| skill_template | Reusable solution patterns |
| avoidance_guide | Pitfalls to avoid |
| lesson_learned | General lessons |
| best_practice | Recommended approaches |

## Privacy Levels

| Level | Description |
|-------|-------------|
| public | Can be shared freely |
| trusted | Requires authentication |
| restricted | Local use only |

## File Structure

```
collaborative-learning-protocol/
├── SKILL.md                  # Skill definition
├── collaborative_protocol.py # Core implementation
├── config.json              # Configuration
├── example_usage.py         # Usage examples
└── README.md                # This file
```

## Author

MiniMax Agent
