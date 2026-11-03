---
name: academic-writing
description: |
  Academic paper writing assistant with 30 Prompt templates covering the full workflow of paper writing.
  Use when users mention: paper writing, polishing, translation, literature review, abstract, introduction, methods chapter, reviewer response, grant application, research proposal, academic presentation PPT, LaTeX editing, academic figures, experimental result analysis, manuscript review simulation, removing AI flavor, literature comparison, finding research gaps, paper outline.
license: MIT
metadata:
  author: MiniMax Agent
  version: "1.0.0"
---

# Academic Writing Skill

> **Version**: 1.0 | **Prompt Templates**: 30

## Skill Overview

This Skill provides 30 Prompt templates covering the full workflow of academic paper writing: **Literature Research → Outline → Drafting → Polishing → Figures → Submission → Grant Application**.

**Applicable Scenarios**:
- Chinese/English paper translation and polishing
- LaTeX/Word document editing
- Academic figure generation and captions
- Experimental result analysis
- Pre-submission review and peer review simulation
- Literature review writing
- Reviewer response letters
- Research proposals and grant applications

**Usage**: Copy the corresponding Prompt directly to chat, or use AI coding tools like Cursor/Claude Code/openclaw/opencode.

---

## Quick Index

| Stage | Prompts | Purpose |
|-------|---------|---------|
| Translation | #1-2 | Chinese to English, English to Chinese |
| Polishing | #3-7 | Chinese polishing, English condensing/expanding/polishing |
| AI Removal | #8-10 | Remove AI flavor, logic checking |
| Figures | #11-14 | Architecture diagrams, chart recommendations, figure/table captions |
| Analysis | #15 | Experimental result writing |
| Review | #16-17 | Peer review simulation, logic checking |
| Research | #18-20 | Literature summary, comparison, finding research gaps |
| Outline | #21-22 | Paper outline, section expansion |
| Drafting | #23-25 | Abstract, Introduction, Methods writing |
| Submission | #26-27 | Reviewer response, cover letter |
| Funding | #28-30 | Grant proposal, research plan, academic PPT |

---

## Workflow

### Scenario Selection

Select the corresponding Prompt based on your current writing stage:

1. **New to research area** → Use #18-20 (Literature Research)
2. **Preparing to write** → Use #21-25 (Outline + Draft)
3. **Polishing phase** → Use #1-10 (Translation + Polishing + AI Removal)
4. **Preparing submission** → Use #11-17 (Figures + Review Simulation)
5. **Responding to reviewers** → Use #26-27 (Rebuttal)
6. **Applying for grants** → Use #28-30 (Grant + Presentation)

### Best Practices

1. **Combine**: Multiple Prompts can be chained, e.g., use #21 for outline, then #22-25 for section expansion
2. **Iterate**: Polish AI-generated content using #3-10 for multiple rounds
3. **Stay critical**: Use #16 to simulate reviewer perspective and identify issues early
4. **Data integrity**: All experimental data and conclusions must be based on real research; AI assists only with expression

---

## Prompt Template References

Detailed Prompt templates are available in the `references/` directory:

- `references/translation.md` - Translation (#1-2)
- `references/polishing.md` - Polishing (#3-10)
- `references/figures.md` - Figures (#11-14)
- `references/analysis.md` - Analysis (#15-17)
- `references/research.md` - Research (#18-20)
- `references/drafting.md` - Drafting (#21-25)
- `references/submission.md` - Submission (#26-27)
- `references/funding.md` - Funding (#28-30)
