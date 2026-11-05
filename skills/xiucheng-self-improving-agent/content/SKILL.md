---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 2de0747765778bf6a6459a168d72e71f
    PropagateID: 2de0747765778bf6a6459a168d72e71f
    ReservedCode1: 3046022100babae785ac2126fd47342912cd04d828a586048bde5aa783ac7d661f6ab43d78022100f4306fd8befd194b039b1a42450e354d951a5dc8df7f50573ccd42ad72a8b865
    ReservedCode2: 304402203834489c16b57a94fdbc8a16fe9d7c95bbca4b696b644f3689515a3c64139de202205649ae278cbde57881324cda21525cdf80363b88a09d3d76215bea5534bc7ff2
author: xiucheng
description: Self-improving agent system that analyzes conversation quality, identifies improvement opportunities, and continuously optimizes response strategies.
homepage: https://github.com/xiucheng/self-improving-agent
license: MIT
name: self-improving-agent
tags:
    - self-improvement
    - learning
    - optimization
    - reflection
    - growth
type: skill
version: 1.0.0
---

# Self-Improving Agent

An intelligent self-improvement system for OpenClaw agents that analyzes conversation quality and continuously optimizes performance.

## Features

- 📊 **Quality Analysis**: Evaluates conversation effectiveness
- 🎯 **Improvement Tracking**: Identifies areas for enhancement
- 📝 **Learning Log**: Records insights and lessons learned
- 📈 **Weekly Reports**: Generates improvement summaries
- 🔄 **Strategy Optimization**: Adapts response patterns over time

## Installation

```bash
clawhub install self-improving-agent
```

## Usage

### Automatic Analysis
The skill automatically analyzes conversations after each session.

### Manual Improvement Logging
```python
from self_improving import SelfImprovingAgent

sia = SelfImprovingAgent()
sia.log_improvement("Need to be more concise in technical explanations")
```

### Generate Weekly Report
```python
report = sia.generate_weekly_report()
print(report)
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| improvement_log | ./improvement_log.md | Learning log file |
| soul_file | ./SOUL.md | Personality anchor file |
| auto_analyze | true | Auto-analyze conversations |

## Integration

Works best with:
- `memory-manager`: For tracking improvement history
- Custom agent personalities (SOUL.md)

## License

MIT License - Help agents get better every day!
