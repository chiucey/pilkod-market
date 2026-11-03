---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 07f1ae3ff060c37b4353c8560bb37283
    PropagateID: 07f1ae3ff060c37b4353c8560bb37283
    ReservedCode1: 3045022100c77a190ab19d6078fb2047773410ed6c87eeb3f1bc4e779c5de947bd1ca1b2b00220100c825c54ae79cd07f7f9cfb57f2a1add9f3ede8a6e8d7a7e2ca7485e7e286d
    ReservedCode2: 3044022058c87befbde367d7eaff31504101b663b9dbfbd82ee35e82a8eadba97804721402205819f599944ccf0642e0c2827c2caebb40d7dac8fb5697e1fb60ba69dd470922
description: Organize text content into structured Markdown notes. Use when users ask to "整理笔记", "整理制度", "整理规章", "整理办法", "generate summary report", "organize content", or "summary report for [topic]".
name: text-to-markdown
---

# Text-to-Markdown Organizer

Transform disorganized text into clear, logically structured Markdown notes.

## Workflow

### 1. Lead with Core Conclusion
- Summarize the core message in one sentence at the beginning
- Place at the top of the Markdown, no unnecessary preamble

### 2. Extract Key Information
From the source text, identify:
- Core topic and keywords
- Key points/achievements/insights
- Timeline, steps, or classification dimensions

### 3. Organize by Pyramid Principle

**Structural Rules**:
- Core Conclusion → Sub-points → Supporting Details
- Each level heading must summarize its subordinate content
- Follow logical order (importance/time/space/structure)

### 4. Apply List-Based Format

**Symbol Hierarchy**:
```
• Level 1 (Core)
◦ Level 2 (Support)
▪ Level 3 (Detail)
```

**Writing Rules**:
- Each item: noun + verb, concise and powerful
- Avoid complete sentences, use keyword phrases
- Leave blank lines between modules

### 5. MECE Self-Check

Verify output:
- **Mutually Exclusive**: No overlapping sections
- **Collectively Exhaustive**: All key content covered
- No omissions, no duplicates

## Default Content Framework (General Notes)

```
# [Topic] Summary Report

[One-sentence core conclusion]

## Work Achievements
• Key point 1
◦ Supporting detail
• Key point 2

## Personal Growth
• Growth point 1
◦ Specific example

## Challenges & Reflections
• Challenge 1
◦ How it was addressed

## Future Plans
• Goal 1
◦ Specific measures
```

## Company Policy Framework (For Regulations)

When organizing company policies, regulations, or procedures, use this specialized framework:

```
# [Policy Name]

## Metadata
| Item | Value |
|------|-------|
| Version | v1.0 |
| Effective Date | YYYY-MM-DD |
| Issuing Department | [Department] |
| Applicable Scope | [Who must follow] |

## Chapter 1: General Provisions
• Purpose statement
• Scope of application
• Definitions of key terms
• Governing principles

## Chapter 2: Management Specifications
• Subject responsibilities
• Operational procedures
• Prohibited behaviors
• Required approvals

## Chapter 3: Rewards & Penalties
• Reward conditions
• Violation handling
• Dispute resolution

## Chapter 4: Supplementary Provisions
• Interpretation authority
• Amendment procedures
• Effective date
• Superseded documents

## Key Thresholds
• [Numeric/temporal/percentage requirements]

## Compliance Checklist
- [ ] [Check item 1]
- [ ] [Check item 2]
```

## Policy Compliance Checklist

For company regulations, verify:
- [ ] Clear subject responsibilities
- [ ] Quantifiable thresholds defined
- [ ] Approval authority specified
- [ ] Enforcement mechanism stated
- [ ] Appeal process defined
- [ ] Effective date and version noted

## Trigger Examples

- "Please help me organize the summary report for [topic]"
- "Organize this content into notes"
- "Organize company policy [policy name]"
- "整理[制度名称]"
- "整理公司规章"
- "整理管理办法"
- "Generate a structured learning summary"

## Output Requirements

- Output directly in Markdown format
- No additional explanation needed
- Ensure complete structure and standardized format
- For policies: include metadata table and compliance checklist
