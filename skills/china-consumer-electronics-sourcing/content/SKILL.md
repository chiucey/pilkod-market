---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 743637557a90084e65cbea4d408ed5d5
    PropagateID: 743637557a90084e65cbea4d408ed5d5
    ReservedCode1: 304402201e0fea6c503ec9034983caa95b417b1baff9c1b9c3d0b7653ecf15632476137b02206f44a5f323457cd3fd59055d7e1f7b46b85527f9f1d81cf450b5f437631c71ad
    ReservedCode2: 304502207c78915963b1a3abed09edc828bc22abc9b35f2986d6c714a678e50a0c904242022100e83e6686cc6ba9685317013e5dd09a06a77e32e5b35bd371b7f91c33a038f948
author: sourcing-china
description: Comprehensive consumer electronics industry sourcing guide for international buyers – provides detailed information about China's smartphone, wearable, audio, smart home, and AR/VR manufacturing clusters, supply chain structure, regional specializations, and industry trends (2026 updated).
invocable: true
name: china-consumer-electronics-sourcing
tags:
    - consumer-electronics
    - smartphones
    - wearables
    - audio-devices
    - smart-home
    - AR-VR
    - TWS
    - electronics-manufacturing
    - sourcing
    - supply-chain
version: 1.0.0
---

# China Consumer Electronics Sourcing Skill

## Description
This skill helps international buyers navigate China's consumer electronics manufacturing landscape, which is projected to exceed **¥15.2 trillion in revenue by 2026**. It provides data-backed intelligence on regional clusters, supply chain structure, and industry trends based on the latest government policies and industry reports. Coverage includes smartphones, wearables, audio devices, smart home products, AR/VR headsets, and accessories.

## Key Capabilities
- **Industry Overview**: Get a summary of China's consumer electronics industry scale, development targets, and key policy initiatives (Digital China, 5G, AI).
- **Supply Chain Structure**: Understand the complete industry chain from core components (chips, displays, batteries) to assembly and global sales channels.
- **Regional Clusters**: Identify specialized manufacturing hubs for different product categories (smartphones in Pearl River Delta, laptops in Yangtze River Delta, AR/VR in Beijing).
- **Subsector Insights**: Access detailed information on key subsectors (smartphones, wearables, audio devices, smart home, AR/VR).
- **Sourcing Recommendations**: Get practical guidance on evaluating and selecting suppliers, including verification methods, communication best practices, typical lead times, and payment terms.

## How to Use
You can interact with this skill using natural language. For example:
- "What's the overall status of China's consumer electronics industry in 2026?"
- "Show me the supply chain structure for smartphones"
- "Which regions are best for sourcing TWS earbuds?"
- "Tell me about smart watch manufacturing clusters"
- "How do I evaluate suppliers of smart home devices?"
- "What certifications should I look for in consumer electronics?"

## Data Sources
This skill aggregates data from:
- Ministry of Industry and Information Technology (MIIT)
- China Electronic Information Industry Development Institute
- National Bureau of Statistics of China
- China Audio Industry Association
- Industry research publications (updated Q1 2026)

## Implementation
The skill logic is implemented in `do.py`, which reads structured data from `data.json`. All data is cluster-level intelligence without individual factory contacts.

## API Reference

The following Python functions are available in `do.py` for programmatic access:

### `get_industry_overview() -> Dict`
Returns overview of China's consumer electronics industry scale, targets, and key policy initiatives.

**Example:**
```python
from do import get_industry_overview
result = get_industry_overview()
# Returns: industry scale, 2026 targets, key drivers, export value, etc.