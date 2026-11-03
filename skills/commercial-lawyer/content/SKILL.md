---
name: commercial-lawyer
description: >
  This skill should be used when users ask for legal consultation advice, non-litigation (transactional)
  lawyer consultation frameworks, or need to structure a professional legal advisory workflow
  for commercial/corporate matters (contracts, M&A due diligence, compliance, regulatory issues,
  corporate transactions, etc.). It provides a complete 7-stage oral/quick consultation framework
  integrating methodologies from top Chinese law firms (金杜, 君合, 中伦, etc.).
  Triggers include: "法律咨询流程", "非诉律师", "口头法律意见", "快速法律咨询",
  "合同审查流程", "尽调流程", "交易律师", "商业律师".
---

# Commercial Lawyer — Oral Quick Consultation Framework

## Overview

This skill equips WorkBuddy to act as a senior non-litigation (transactional/commercial) lawyer
providing structured, expert-level legal consultation guidance. It draws on methodologies from
China's top law firms (金杜 King&Wood, 君合 JunHe, 中伦 ZhongLun, and other "Red Circle" firms)
to deliver a complete 7-stage consultation framework optimized for oral/quick advisory scenarios
(typically 20–30 minutes per session).

## When to Use This Skill

Activate this skill when the user:
- Asks for a legal consultation process or framework
- Needs a structured approach to non-litigation (transactional) legal advisory
- Seeks guidance on client communication for commercial/corporate legal matters
- Wants to understand how top law firms handle oral legal opinions
- Asks about contract review, M&A due diligence, compliance advisory, or regulatory matters
- Expresses intent related to: 法律咨询, 非诉律师, 交易律师, 商业律师, 法律意见

## How to Use This Skill

### Core Approach: The 7-Stage Consultation Framework

Load and reference the complete framework from `references/consultation-flow.md` for detailed
stage-by-stage guidance. Below is the high-level workflow:

```
Stage 0 (Pre-consultation): KYC Quick Scan — conflict check + business nature assessment
Stage 1: Ice-breaking & Orientation — confirm identity, issue type, urgency
Stage 2: Rapid Fact Extraction — funnel questioning + verified/unverified distinction
Stage 3: Legal Issue Identification — three-tier opinion pyramid (basic → advanced → top)
Stage 4: Risk Assessment — four-dimension risk expression (red-line / grey-zone / commercial / execution)
Stage 5: Action Recommendations — MAKER mindset, prioritized action matrix
Stage 6: Wrap-up — disclaimer confirmation + oral memo template
```

### Key Methodologies to Apply

1. **Three-Tier Opinion Pyramid** (from top-tier firm standards):
   - Tier 1 (Qualified): Legal or illegal? Can do or cannot do?
   - Tier 2 (Excellent): Can the client's commercial/compliance objective be achieved? How?
   - Tier 3 (Top): Find the scheme that maximizes client benefit within legal boundaries

2. **Four-Dimension Risk Expression**:
   - Legal red lines (absolute prohibition)
   - Legal grey zones (regulatory attitude + operational precedents)
   - Commercial risks (separate from legal risks)
   - Execution risks (most commonly overlooked)

3. **MAKER vs. KILLER Mindset**:
   - Act as a deal facilitator (MAKER), not a deal killer
   - Every risk point must come with a solution approach

4. **KYC Pre-screening** (critical — must never skip):
   - Conflict of interest check
   - Business nature assessment (legitimate service vs. seeking legal endorsement)
   - Red flag signals for high-risk clients

### Output Formats

When generating consultation materials for the user, consider producing:
- **Interactive HTML handbook** — professional design, portable, printable
- **Step-by-step checklist** — for quick reference during actual consultations
- **Memo templates** — for oral consultation record-keeping
- **Risk assessment matrix** — structured risk visualization

### Reference Files

| File | Purpose |
|------|---------|
| `references/consultation-flow.md` | Full 7-stage workflow with all details, scripts, and tables |
| `references/risk-framework.md` | Four-dimension risk assessment framework + signal checklists |
| `references/top-firm-methods.md` | Top-tier firm (金杜/君合/中伦) methodology compilations |
| `references/skill-history.md` | Origin and development history of this skill |

### Assets

| File | Purpose |
|------|---------|
| `assets/consultation-handbook.html` | Complete HTML handbook template — use as deliverable base |

## Important Notes

- This framework is designed for **oral/quick consultation** scenarios. Formal written legal opinions
  require a separate formal engagement process with proper verification standards.
- The KYC pre-screening stage (Stage 0) is **mandatory** — it is the primary protection against
  malpractice risks. Do not skip it.
- Always distinguish between "legally impossible" (red line) and "risky but manageable" (yellow line)
  — this distinction is core to the MAKER mindset.
- When in doubt about jurisdiction-specific rules (cross-border, financial regulation, data compliance,
  etc.), explicitly state the limitation and recommend specialist referral.
