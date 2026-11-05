---
name: token-cost-controller
description: OpenClaw Token Cost Controller - Smart caching, dynamic routing, real-time monitoring. Automatically optimizes at runtime, reducing costs by 70%. Use when users ask about cost optimization, token savings, caching strategies, model routing, or cost monitoring.
---

# Token Cost Controller v2.1.1

> Your AI Cost Management Assistant - Every Token Spent Wisely

## Core Features

- **Smart Cache**: Semantic similarity hits cache directly, saving 30-50% costs
- **Dynamic Routing**: Simple tasks route to cheap models, complex tasks use flagship models
- **Real-time Monitoring**: Detect abnormal consumption within 5 seconds, auto alert
- **One-click Control**: Disable skills, set budget limits, pause plans

## Performance Optimization (v2.1.1)

- Async CLI calls - Non-blocking main thread
- Ring Buffer fixed memory - No more memory leaks
- Dynamic anomaly detection - Intelligent threshold based on coefficient of variation
- Safe cache keys - Object key sorting improves hit rate

## Quick Usage

```bash
openclaw cost report      # View today's cost report
openclaw cost top-skills  # View top consuming skills
openclaw cost disable-skill <skill-name>  # Disable high-cost skill
```

## Savings

| Before | After | Savings |
|--------|-------|---------|
| $156/month | $47/month | 70% |
| 125K Tokens/day | 45K Tokens/day | 64% |

## Tech Stack

- Node.js 18+
- Async execAsync calls
- Ring Buffer data structure
- Dynamic threshold anomaly detection
