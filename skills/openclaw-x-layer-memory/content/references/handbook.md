# OpenClaw X-Layer Memory System Handbook

> **Version:** 1.0.0
> **Last Updated:** 2026-03-26
> **Status:** Production Ready

This handbook provides a complete guide to implementing and managing multi-layer memory systems in OpenClaw, based on research from Hindsight, Mem0, and OpenClaw's native capabilities.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Layer Specifications](#layer-specifications)
4. [Research Foundations](#research-foundations)
5. [Implementation Guide](#implementation-guide)
6. [Troubleshooting](#troubleshooting)
7. [Reference](#reference)

---

## Quick Start

### One-Command Setup

```bash
# Initialize 3-layer memory (recommended for beginners)
node scripts/init_x_layer_memory.js --workspace . --layers 3

# Initialize 5-layer memory (full production)
node scripts/init_x_layer_memory.js --workspace . --layers 5
```

### One-Command Audit

```bash
# Check memory health
node scripts/audit_openclaw_memory.js --workspace .

# Get JSON output for automation
node scripts/audit_openclaw_memory.js --workspace . --json
```

---

## Architecture Overview

### Five-Layer Memory Model

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 5: Retrieval                       │
│  High-recall index, hybrid search, temporal decay            │
├─────────────────────────────────────────────────────────────┤
│                    Layer 4: Reflection                      │
│  Consolidation, conflict detection, pattern extraction       │
├─────────────────────────────────────────────────────────────┤
│                    Layer 3: Semantic                         │
│  bank/world.md, bank/experience.md, bank/opinions.md         │
│  bank/entities/*.md - Entity summaries & relationships      │
├─────────────────────────────────────────────────────────────┤
│                    Layer 2: Episodic                         │
│  memory/YYYY-MM-DD.md - Daily events, decisions, follow-ups │
├─────────────────────────────────────────────────────────────┤
│                    Layer 1: Core                             │
│  MEMORY.md - Stable preferences, rules, durable facts        │
└─────────────────────────────────────────────────────────────┘
```

### Three Operational Axes

| Axis | Description | Operations |
|------|-------------|------------|
| **Representation** | Where memory lives | Working → Episodic → Semantic → Procedural → Retrieval |
| **Processing** | How memory changes | Capture → Retain → Recall → Reflect → Reconsolidate → Forget |
| **Value** | Why memory matters | Goal impact, behavior change, reuse frequency, confidence |

---

## Layer Specifications

### Layer 1: Core Memory (`MEMORY.md`)

**Purpose:** Permanent storage for stable, high-value information.

**Content Guidelines:**
- User preferences (communication style, formatting preferences)
- Stable facts (timezone, main projects, key technologies)
- Rules and constraints (coding standards, workflow requirements)
- Lessons learned (important discoveries, avoided mistakes)

**Size Target:** < 3,000 tokens (~12KB)

**Anti-Patterns:**
- ❌ Chat transcripts or conversation history
- ❌ Raw project documentation
- ❌ Large code snippets
- ❌ Time-sensitive information
- ❌ Unverified assumptions

**Good Pattern:**
```markdown
## Communication Preferences
- Keep responses concise unless detail is requested
- Use code blocks with language tags for code samples

## Stable Facts
- Timezone: UTC+8
- Primary language: TypeScript
- Main workspace: /workspace/project

## Rules
- Always run tests before pushing
- Document API changes in CHANGELOG.md
```

---

### Layer 2: Episodic Memory (`memory/YYYY-MM-DD.md`)

**Purpose:** Daily event logging with structured retention markers.

**Required Sections:**
```markdown
## Events        # What happened today
## Decisions     # Key decisions made
## Follow-ups    # Outstanding items
## Retain        # Facts to promote to higher layers
```

**Retention Marker Syntax:**
```markdown
## Retain
- W @project: Important world fact
- B @task: Behavioral/experience note
- O(c=0.80) @user: Opinion with confidence
```

**Marker Types:**
| Marker | Meaning | Example |
|--------|---------|---------|
| `W` | World fact (objective) | `W @project: Project X uses PostgreSQL` |
| `B` | Behavioral note | `B @debug: This error usually means Y` |
| `O(c=x)` | Opinion with confidence | `O(c=0.70) @design: Prefer composition over inheritance` |

---

### Layer 3: Semantic/Entity Memory (`bank/`)

**Purpose:** Structured organization of facts, experiences, and opinions.

**File Structure:**
```
bank/
├── world.md           # Objective world facts
├── experience.md      # Past actions, experiments, fixes
├── opinions.md        # Subjective preferences with confidence
├── reflections.md     # Consolidation results (L4)
├── procedures.md      # Repeatable workflows (L5)
└── entities/
    ├── project-x.md   # Project-specific entity
    ├── alice.md       # Person entity
    └── system-y.md    # System entity
```

**Entity Page Template:**
```markdown
# Entity Name

## Current State
- Status: Active/Archived/Unknown
- Last Updated: YYYY-MM-DD

## Durable Facts
-

## Recent Changes
-

## Relationships
-

## Evidence
<!-- memory/YYYY-MM-DD.md#Lx -->
```

---

### Layer 4: Reflection Memory (`bank/reflections.md`)

**Purpose:** Periodic consolidation and knowledge synthesis.

**Activities:**
1. Conflict detection (contradicting facts across layers)
2. Pattern recognition (repeated observations)
3. Promotion decisions (what moves to MEMORY.md)
4. Deprecation marking (superseded information)

**Consolidation Frequency:** Recommended weekly or bi-weekly

---

### Layer 5: Retrieval/Index Memory (`.memory/`)

**Purpose:** High-performance recall infrastructure.

**Components:**
- `.memory/index.sqlite` - Derived search index
- Hybrid search - BM25 + vector combination
- Temporal decay - Recency weighting
- MMR reranking - Diversity enhancement

**Implementation Priority:**
```
P0: Hybrid Search (BM25 + vector)     ← Start here
P1: MMR Diversity Reranking            ← Add when seeing duplicates
P2: Temporal Decay                     ← Add for time-sensitive tasks
P3: QMD Backend                        ← Only for large-scale deployments
```

---

## Research Foundations

### Hindsight: Building Agent Memory (arXiv:2512.12818)

**Key Contributions:**
- Explicit retain/recall/reflect operations
- World facts, agent experiences, entity summaries distinction
- LongMemEval and LoCoMo benchmark improvements

**Direct Applications:**
- `memory/YYYY-MM-DD.md` → retain input only
- `bank/world.md`, `bank/experience.md` → sustainable structure
- Reflection layer → consolidation loop

### Mem0: Production-Ready AI Memory (arXiv:2504.19413)

**Key Contributions:**
- Selective memory extraction (not everything goes to prompt)
- Graph-based memory variant for complex relationships
- LoCoMo benchmark comparison

**Direct Applications:**
- Dynamic extraction over static context
- Entity relationships when complexity increases
- Production-focused optimization

### OpenClaw Memory Research

**Current State (2026-03-26):**
- 2-layer default (MEMORY.md + memory/YYYY-MM-DD.md)
- memory_search and memory_get tools available
- SQLite FTS and vector embedding support
- QMD sidecar backend option

**Memory v2 Direction:**
- bank/ as typed memory pages
- .memory/index.sqlite as derived store
- Retain/Recall/Reflect workflow
- Entity, temporal, opinion confidence support

---

## Implementation Guide

### Decision Tree: How Many Layers?

```
Start here
    │
    ▼
Do you need persistent recall across sessions?
    │
    ├── No → 2 layers (OpenClaw default)
    │
    └── Yes
            │
            ▼
        Do you have recurring entities (people/projects/systems)?
            │
            ├── No → 3 layers (L1+L2+L3 minimal)
            │
            └── Yes
                    │
                    ▼
                Do preferences change frequently?
                    │
                    ├── No → 3 layers + manual consolidation
                    │
                    └── Yes
                            │
                            ▼
                        4 layers (L1+L2+L3+L4)

        Add Layer 5 if:
        - Vector search is slow with many chunks
        - Need semantic similarity matching
        - Hybrid search becomes necessary
```

### Migration Path from OpenClaw Default

**Before (2 layers):**
```
workspace/
├── MEMORY.md          # May be bloated
└── memory/
    └── 2026-03-26.md
```

**After (3 layers):**
```
workspace/
├── MEMORY.md          # Trimmed, focused
├── memory/
│   └── 2026-03-26.md  # With ## Retain section
└── bank/
    ├── world.md       # Extracted facts
    ├── experience.md  # Extracted learnings
    ├── opinions.md    # Extracted preferences
    └── entities/      # Project/person pages
```

### Writing Protocol

**Always Include:**
- Source citations (file and line reference)
- Confidence scores for opinions
- Context for facts that may change
- Date stamps for time-sensitive information

**Never:**
- Copy-paste entire chat logs
- Include unverified assumptions as facts
- Mix observation with inference without labeling
- Store information only in memory, not on disk

---

## Troubleshooting

### Symptom: "Said it before, forgot now"

**Causes:**
- Statement only in chat, not written to disk
- Written to daily log but not promoted to core/entity

**Fix:**
1. Verify MEMORY.md or memory/YYYY-MM-DD.md was updated
2. For stable preferences, write to MEMORY.md
3. For entity-related info, write to bank/entities/*.md

### Symptom: MEMORY.md growing, effectiveness declining

**Causes:**
- Core layer mixing short-term and long-term content
- Chat history pollution
- Redundant facts

**Fix:**
1. Delete expired, duplicated, superseded content
2. Move time-sensitive content to daily logs
3. Keep only high-stability, high-reuse, high-impact info

### Symptom: Know facts but can't express relationships

**Causes:**
- Only flat logs, no entity layer

**Fix:**
1. Create bank/entities/ directory
2. Create pages for key entities
3. Include current state, changes, evidence pointers

### Symptom: Search returns old/duplicate information

**Causes:**
- Basic vector search without hybrid/MMR/temporal decay

**Fix:**
1. Enable hybrid search (BM25 + vector)
2. Add MMR reranking
3. Implement temporal decay for recency weighting

### Symptom: Conflicting facts across layers

**Causes:**
- Missing reflection/consolidation
- New facts added without marking old as superseded

**Fix:**
1. Add bank/reflections.md for regular consolidation
2. Mark superseded information: `~~old~~ [superseded by YYYY-MM-DD]`
3. Let latest valid fact win, preserve evidence chain

---

## Reference

### Recommended Layer Bundles

| Use Case | Layers | Components |
|----------|--------|------------|
| Personal assistant | 3 | L1 + L2 + L3 |
| Production workspace | 4 | L1 + L2 + L3 + L4 |
| Complex project | 5 | L1 + L2 + L3 + L4 + L5 |

### File Size Guidelines

| Layer | Target Size | Warning | Critical |
|-------|-------------|---------|----------|
| MEMORY.md | < 3,000 tokens | > 3,000 | > 6,000 |
| Daily log | < 1,500 tokens | > 1,500 | > 3,000 |
| Entity page | < 1,000 tokens | > 1,000 | > 2,000 |

### Promotion Rules

**L2 → L1 (Daily → Core):**
- [ ] Long-term validity confirmed
- [ ] Cross-session utility demonstrated
- [ ] Behavior/style impact identified

**L2 → L3 (Daily → Entity):**
- [ ] Entity mentioned multiple times
- [ ] Relationships span multiple sessions
- [ ] Daily log insufficient for clarity

**L3 → L1 (Entity → Core):**
- [ ] Fact verified multiple times
- [ ] Conflicts resolved
- [ ] Must be visible every session

### Sources

- Hindsight: https://arxiv.org/abs/2512.12818
- Mem0: https://arxiv.org/abs/2504.19413
- SuCo: https://arxiv.org/abs/2411.14754
- OpenClaw Memory Research: https://docs.openclaw.ai/experiments/research/memory
- OpenClaw Permanent Memory Guide: https://www.getopenclaw.ai/en/blog/openclaw-permanent-memory

---

*This handbook is part of the OpenClaw X-Layer Memory System skill. For automation scripts, see `scripts/audit_openclaw_memory.js` and `scripts/init_x_layer_memory.js`.*
