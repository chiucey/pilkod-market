---
name: paperclaw
description: Production-ready OpenClaw skill library for academic research teams. Use when users need literature management, research synthesis, team collaboration, manuscript output, and research tracking.
---

# PaperClaw - Academic Research Team Skill Library

PaperClaw is a comprehensive skill library designed for academic research teams—labs, collaborative projects, and cross-institution groups—who want a shared AI research layer rather than isolated personal tools.

## Overview

PaperClaw packages 27 production-ready skills across 5 categories:

| Category | Skills | Use Case |
|----------|--------|----------|
| **Literature** | 6 | Literature review, arXiv monitoring, citation graphs, gap detection |
| **Synthesis** | 5 | Contradiction detection, consensus mapping, evidence grading |
| **Collaboration** | 5 | Annotation sharing, expertise mapping, knowledge handoffs |
| **Output** | 6 | Draft generation, grants, rebuttals, presentations |
| **Tracking** | 5 | Hypothesis versioning, preprint watch, citation alerts |

## Key Skills Overview

### Literature Management
- **living-review**: Continuously updated structured literature review
- **arxiv-monitor**: Monitors arXiv for new papers matching research interests
- **citation-graph**: Builds and analyzes citation networks
- **gap-detection**: Identifies research gaps and open questions
- **semantic-scholar**: Queries Semantic Scholar API for 200M+ papers
- **zotero-integration**: Syncs with Zotero library via Web API

### Research Synthesis
- **contradiction-detection**: Finds conflicting claims across papers
- **consensus-mapping**: Maps field consensus vs. contested areas
- **claim-tracker**: Tracks scientific claims over time
- **cross-paper-synthesis**: Synthesizes findings into coherent narratives
- **evidence-grading**: Evaluates evidence strength

### Team Collaboration
- **annotation-sharing**: Share and discuss PDF annotations
- **expertise-mapping**: Maps team expertise distribution
- **lab-knowledge-handoff**: Knowledge transfer for departing members
- **reading-coverage**: Tracks team reading progress
- **team-sync**: Generates meeting agendas from team activity

### Manuscript Output
- **draft-generation**: Generates manuscript sections with citations
- **grant-writing**: NIH, NSF, ERC, Wellcome proposal sections
- **review-response**: Evidence-backed reviewer responses
- **abstract-writing**: Venue-appropriate abstracts
- **rebuttal-writing**: Conference review rebuttals (NeurIPS, ICML, ICLR)
- **presentation-deck**: Conference talk and defense slides

### Research Tracking
- **hypothesis-versioning**: Version-controlled hypothesis registry
- **experiment-log**: Structured experiment documentation
- **reproducibility-check**: Reproducibility evaluation
- **preprint-watch**: Preprint server monitoring
- **citation-alert**: Citation activity monitoring

## Representative Workflows

| Workflow | Skills Chain |
|----------|--------------|
| Start new project | `arxiv-monitor` → `living-review` → `gap-detection` → `hypothesis-versioning` |
| Write paper | `cross-paper-synthesis` → `draft-generation` → `abstract-writing` → `reproducibility-check` |
| Respond to reviewers | `review-response` → `evidence-grading` → `rebuttal-writing` |
| Lab meeting prep | `reading-coverage` → `team-sync` → `annotation-sharing` |
| Onboard new member | `expertise-mapping` → `reading-coverage` → `lab-knowledge-handoff` |
| Write grant | `gap-detection` → `consensus-mapping` → `grant-writing` |

## Installation

```bash
git clone https://github.com/meowscles69/PaperClaw.git
mkdir -p ~/.openclaw/workspace/skills
cp -R PaperClaw/skills/* ~/.openclaw/workspace/skills/
```

## Skill Format

Each skill follows a consistent structure:
- **Overview**: What this skill enables
- **When to Use**: Trigger conditions for activation
- **Key Capabilities**: Tools, APIs, and parameters
- **Usage Examples**: Code and workflow examples
- **Output Format**: Expected return format
- **Notes**: Caveats, integrations, and tips

## Comparison with LabClaw

| | LabClaw | PaperClaw |
|---|---|---|
| Focus | Biomedical tools & databases | Cross-field knowledge workflows |
| Unit | Solo researcher | Research team / lab |
| Emphasis | Execution (run analysis) | Synthesis & collaboration |
| Scope | Bio / pharma / med | Any academic field |

## Notes

- PaperClaw is a skill library that can be installed partially or fully
- Compatible with OpenClaw workspace skill loading
- Language: English (Simplified Chinese coming soon)
- Related: [LabClaw](https://github.com/wu-yc/LabClaw) for biomedical execution toolkit

---

**Source**: [github.com/meowscles69/PaperClaw](https://github.com/meowscles69/PaperClaw)
