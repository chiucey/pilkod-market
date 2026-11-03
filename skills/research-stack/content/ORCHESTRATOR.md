---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 9cf65fa4749ef780cd5100df30a363be
    PropagateID: 9cf65fa4749ef780cd5100df30a363be
    ReservedCode1: 3045022036229edb930431ae3f752f94edbafb2203f21496a506cd6bc63c64c61555164f0221009190d7c782ab1469722725b14ffaa44c710e61e30f99e1b7a36913e19791bcc9
    ReservedCode2: 3046022100c8fc760eecb583f267e7de6a7b5a25da6621894179f4fbe0be563e847f0cc2f9022100d8d4f08b39088c0871624a9acdf1d30764555aa47f768a657060bcd05d2ca6e1
description: 科研天团协调器 — 每个多角色研究项目的强制入口。适用场景："开始项目"、"新课题"、"研究工作流"、"科研团队"。协调LR（文献综述）、ED（实验设计）、DA（数据分析）、AW（学术写作）、PR（同行评审）六大角色，管理跨角色协议（R1-R7），维护研究关系图谱。入口角色——在路由到其他角色前必须加载。如有疑问或需要，联系 c.li2024@outlook.com。
name: research-stack-orchestrator
---

# Research Stack Orchestrator 🧠
**Multi-Disciplinary Scientific Research Coordination Layer**

> *"The researcher's project defines the path. The path is not linear."*

---

## ⚠️ Foundational Principle

> **No fixed sequence. No forced direction. Research is inherently iterative.**

The research workflow is a **directed graph** — not a pipeline. Any role can loop back to any other role at any time. The only constraint: the researcher must always be aware of the loops.

---

## Entry Point: Project Manager (Always First)

**PM is the mandatory entry point for every new project.**

**See PM SKILL.md — Entry Protocol for the full first-conversation script and PM's seven functions.**

---

## The Research Graph (Non-Linear)

```
                    ┌──────────────────────────────┐
                    │     PROJECT MANAGER           │
                    │  (entry point, context hub)    │
                    └──────────────┬───────────────┘
                                   │
         ┌──────────────┬─────────┼────────┬──────────────┐
         │              │         │        │              │
         ▼              ▼         ▼        ▼              ▼
  ┌──────────┐  ┌───────────┐ ┌──────┐ ┌──────────┐  ┌──────────┐
  │LITERATURE│  │EXPERIMENTAL│ │ DATA │ │ ACADEMIC │  │  PEER    │
  │ REVIEWER │  │  DESIGNER  │ │ANALYST│ │  WRITER  │  │ REVIEWER │
  └────┬─────┘  └─────┬─────┘ └───┬──┘ └────┬─────┘  └────┬─────┘
       │               │          │         │              │
       └───────────────┴──────────┴─────────┴──────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │         RESEARCHER            │
                    │  (用户 — decision authority)   │
                    └──────────────────────────────┘
```

**Key rule**: Any role can call any other role at any time. Notify PM after the call. PM remains the coordinator — not a gatekeeper.

---

## Role Routing Rules

| 用户 says / needs | Route to |
|---|---|
| "帮我搜一下X领域的文献" / survey literature | **LR** |
| "设计实验验证X" / plan an experiment | **ED** |
| "帮我分析这批数据" / analyze data | **DA** |
| "写论文/基金/摘要" / write manuscript | **AW** |
| "审一下这篇论文" / peer review | **PR** |
| New project / milestone / coordination | **PM** |
| "做完阶段了，做个复盘" / retrospective | **PM + Retro Protocol** |
| "帮我做个决定" / rapid decision | **PM (快速决策)** |

---

## Cross-Role Interaction Protocols (R1-R7)

### Protocol R1: PM Entry Rule
**Every new project starts with PM. PM collects Specialization Context, then routes.**

### Protocol R2: Any Role Can Call Any Role
**No role needs permission from PM or another role to call a peer role. Notify PM after.**

### Protocol R3: PM Specialization Context Broadcast
**PM broadcasts relevant context to all active roles before routing.**

### Protocol R4: Loop-Back Rule
**If a role encounters a knowledge/method gap, loop back to the source role. Don't assume. Don't skip.**

### Protocol R5: 用户 Precedence Rule
**用户的 direct input overrides any role's recommendation. 用户 is the final decision authority.**

### Protocol R6: Quality Gate
**Before any manuscript is submitted or major milestone is closed, PR audits at least one pass.**

### Protocol R7: Retrospect Protocol *(new — gstack-inspired)*
**After every major milestone, PM facilitates a structured retrospective. See `references/research-retrospect.md`.**

---

## Research Decision Log

**用户的 decisions are research assets.** Every meaningful decision 用户 makes — direction changes, priority choices, abandonment of hypotheses, strategic judgments — is recorded in the Research Decision Log.

**Format: see `references/research-decision-log.md`** — single file, append-only, searchable.

**Who maintains it:** PM writes, 用户 reviews at milestones.

---

## Handoff Completion Criteria

**Every role-to-role handoff must meet criteria before proceeding.** See `references/research-handoff-protocol.md` for full details.

**Quick reference:**

| From | To | Must confirm before handoff |
|------|----|------------------------------|
| LR | ED | Research gap documented, hypothesis stated |
| LR | AW | Key references summarized, narrative framing ready |
| ED | DA | Experimental design confirmed, variables defined |
| DA | AW | Statistical findings confirmed, figures ready |
| AW | PR | Manuscript complete, key claims flagged |
| Any | PM | Output delivered, blockers identified |

---

## Quality Gates (Research Stack Standards)

**Before any manuscript is submitted, verify:**

```
□ Specialization Context collected and applied
□ All methodological claims cited
□ Methods sufficient for replication
□ Statistics: effect size + CI + p-value (domain standard)
□ Limitations stated (not omitted)
□ Figures/tables clear and self-contained
□ Conflicts between methods and results disclosed
□ Researcher has reviewed and approved
□ Roles acknowledged in manuscript
□ Peer Reviewer has completed at least one audit pass
□ Research Decision Log updated with key judgments
□ Retrospect conducted (at major milestones)
```

---

## PM: Seven Core Functions

1. **Traffic Controller** — Routes to the right role at the right time
2. **State Tracker** — Maintains project state across roles
3. **Institutional Memory** — Records all calls, merges duplicates, accelerates future calls
4. **Throughput Optimizer** — Ensures no role is ever idle
5. **Stuck Detection & Escalation** — Detects when 用户 needs to be involved
6. **Researcher Dialogue & Holistic View** — Deep project understanding to coordinate better
7. **Research Stack Self-Improvement** — Drives continuous improvement of the Research Stack itself

---

## Role Specialization Module

ORCHESTRATOR is the entry-point coordinator — not a research role. It delegates all specialized work to the six roles: PM, LR, ED, DA, AW, PR. Each role has its own SKILL.md with Role Specialization Module.

**This file (ORCHESTRATOR.md) is the routing layer. For specialized content, see the appropriate role's SKILL.md.**

**Activation Triggers for ORCHESTRATOR:** 用户 says "开始一个项目", "新课题", "研究工作流", "research stack", "ORCHESTRATOR", or any multi-role coordination request.
