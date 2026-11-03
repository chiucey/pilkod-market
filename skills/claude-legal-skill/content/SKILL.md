---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 3f8a80dde735a4a48cfc3456a44a493c
    PropagateID: 3f8a80dde735a4a48cfc3456a44a493c
    ReservedCode1: 3045022100b50e66f03fcd5d4d5961e6f21e712dc7e0f7090e40c4c2bd97b581061ec7071b022033d9757d580144a90ba9665f3a4f12040edcf4418ff0c6022f6cad639201477e
    ReservedCode2: 304402202c9d483f9f58a9ba6598e8fa0a6c2238d16c29a6e2b87d81d5423e3bc0204edc0220211ebce6f8edc50f4296dba465d785fc75880eebc7c1caeb684205bb606eb457
argument-hint: '[contract file | text | document path] [--type nda|msa|saas|dpa|ma] [--side customer|vendor|buyer|seller] [--focus specific-clause]'
description: |
    Comprehensive legal assistant skill for contract review, M&A diligence, privacy compliance, IP management, litigation support, and legal research. Use when users ask to review contracts, analyze NDAs, conduct due diligence, check privacy compliance, manage IP matters, prepare litigation documents, or perform legal research. Triggers: "review this contract", "analyze this NDA", "check DPA compliance", "M&A diligence", "IP clearance", "litigation support", "legal research", "contract review", "privacy assessment", "claim chart"
name: claude-legal-skill
---

# Claude Legal Skill

A comprehensive legal assistant for in-house commercial, privacy, product, corporate, employment, litigation, regulatory, AI governance, and IP legal work.

**Important Disclaimer**: Every output is a draft for attorney review — not legal advice, not a legal conclusion, not a substitute for a lawyer. Built with guardrails: source attribution on every citation, conservative defaults on privilege, jurisdiction assumptions surfaced, and explicit gates before filing/sending.

---

## Core Capabilities

### 1. Contract Review & Triage
- **NDA Review**: Fast triage into GREEN/YELLOW/RED based on playbook positions
- **MSA/SaaS Review**: Vendor agreement analysis with SLA, data export, suspension rights
- **DPA Review**: Data Processing Agreement review (processor vs. controller detection)
- **Position-Aware**: Adjusts flags based on side (customer, vendor, buyer, seller)

### 2. M&A & Corporate
- **Diligence Review**: Tabular review with cell-level citations
- **Closing Checklists**: Track closing conditions and contingencies
- **Material Contract Schedule**: Disclosure schedule management
- **Board Minutes**: Draft board minutes and written consents

### 3. Privacy Compliance
- **DPA Review**: Controller/processor detection, transfer mechanism analysis
- **DSAR Response**: Data subject access request acknowledgment and response
- **PIA Generation**: Privacy Impact Assessment triage and generation
- **Use-Case Triage**: PIA vs DPIA routing decisions

### 4. IP Management
- **Trademark Clearance**: Search and clearance analysis
- **FTO Triage**: Freedom-to-operate assessment
- **C&D Drafting**: Cease and desist letter drafting
- **DMCA Takedown**: Copyright takedown procedures

### 5. Litigation Support
- **Claim Chart**: Element-by-element mapping for patents or civil claims
- **Chronology**: Case timeline construction
- **Legal Hold**: Issue/refresh/release holds management
- **Deposition Prep**: Question preparation and topic outlines

### 6. AI Governance
- **Use-Case Triage**: AI impact assessment routing
- **Policy Starter**: AI policy generation
- **Vendor AI Review**: Third-party AI system review
- **Reg Gap Analysis**: Regulatory gap assessment

---

## Workflow

### Step 1: Determine Scope
Identify the type of legal work:
- Contract review → select contract type
- M&A → load deal context
- Privacy → identify controller/processor role
- Litigation → confirm matter and phase

### Step 2: Load Context
1. Identify user's position (customer/vendor/buyer/seller/counsel)
2. Check jurisdiction (US, UK, EU, etc.)
3. Load relevant playbook if configured
4. Identify applicable regulations (GDPR, CCPA, HIPAA, etc.)

### Step 3: Execute Analysis
Follow the appropriate module workflow:
- Contract review: Green/Yellow/Red triage
- M&A: Diligence checklist → issue identification
- Privacy: DPA terms → gap analysis
- IP: Clearance → risk assessment
- Litigation: Elements → evidence mapping → gap detection

### Step 4: Apply Guardrails
- Source attribution on every citation
- Jurisdiction awareness (US vs. non-US)
- Privilege marking where applicable
- Non-lawyer gate for signing decisions

### Step 5: Output
Deliver structured output:
- Risk assessment with severity (Critical/High/Medium/Low)
- Specific redline language where applicable
- Market standard benchmarks
- Missing provisions with suggested language
- Next steps decision tree

---

## Document Type Checklists

### NDA Checklist
- Mutuality (mutual vs. one-way)
- Confidentiality term and survival
- Definition scope (marked-only vs. everything-disclosed)
- Carveouts (5 standard exclusions)
- Residuals clause analysis
- Restrictive covenants (non-solicit, non-compete)
- Governing law and venue

### MSA/SaaS Checklist
- SLA metrics and remedies
- Data export and portability
- Suspension rights
- Price caps and auto-renewal
- Liability limitations
- Indemnification scope

### DPA Checklist (Processor)
- Subprocessor approval mechanism
- Audit rights and notice
- Breach notification timeline
- Security measures annex
- Deletion/return timeline
- Data residency commitments

### DPA Checklist (Controller)
- Subprocessor list disclosure
- Security standards reference
- Breach notification obligation
- International transfer mechanism
- Audit rights (report vs. on-site)
- Deletion certification

---

## Market Standard Benchmarks

| Provision | Standard | Yellow | Red |
|-----------|----------|--------|-----|
| Liability cap | 12 months fees | 6-11 mo | <6 mo or uncapped |
| Auto-renewal notice | 90+ days | 60-89 days | <60 days |
| Non-compete (US) | 1-2 years | 3-4 years | 5+ years |
| NDA term | 2-3 years | 4-5 years | Perpetual |
| Rep survival (M&A) | 12-18 months | 24-30 months | 36+ months |

---

## Red Flags Quick Scan

Automatically flag:
- Liability cap < 6 months
- Uncapped indemnification
- Unilateral amendment rights
- Perpetual confidentiality obligations
- Offshore jurisdiction (BVI, Cayman)
- Missing transfer mechanism (international DPA)
- Non-compete in CA/ND/OK/MN (unenforceable)

---

## Jurisdiction Awareness

Recognize and flag jurisdiction-specific rules:

**US:**
- Non-competes: void in CA, limited in ND/OK/MN
- Work product doctrine (FRCP 26(b)(3))
- State consumer privacy laws (CCPA, VCDPA, etc.)

**UK:**
- Litigation privilege requires reasonable contemplation
- UK Addendum / IDTA for transfers
- GDPR as retained law post-Brexit

**EU:**
- No general work-product protection
- Art. 58(1) GDPR gives DPAs broad investigative powers
- SCC Decision 2021/914 for transfers

---

## Output Format

```markdown
[WORK-PRODUCT HEADER]
PRIVILEGED & CONFIDENTIAL — ATTORNEY WORK PRODUCT

## [Document Type] Review: [Counterparty]

**Position:** [Customer/Vendor/Buyer/Seller]
**Jurisdiction:** [Governing law]
**Reviewed:** [Date]

---

### Bottom Line
[Two sentences. Can we proceed? What must change?]

**Issues:** [N] Critical [N] High [N] Medium [N] Low

---

### Key Findings

| Provision | Status | Risk | Recommendation |
|-----------|--------|------|-----------------|
| [Term] | [OK/Flag] | [Level] | [Action] |

---

### Red Flags
1. **[Issue]** — Section [X]
   - What: [one line]
   - Risk: [level]
   - Recommended: [specific language]

---

### Missing Provisions
- [Provision] — suggested language to add

---

### Next Steps
1. **Draft redline** — I'll produce specific replacement language
2. **Escalate** — Draft note to [GC/counsel] for decision
3. **Get more facts** — [open questions]
4. **Watch and wait** — Add to tracker with revisit date

**One question I'd ask:** [the thing a thoughtful reviewer would notice]
```

---

## Gate: Signing Decisions

Before any signing decision (NDA, DPA, contract):
> This is a legal act that binds the company to specific obligations.
> Have you reviewed this with an attorney? If yes, proceed. If no,
> here's a brief to bring to them:
>
> [1-page summary: counterparty, key terms, what's acceptable, three questions for counsel]

---

## Source Attribution Tags

Always tag citations:
- `[settled]` — stable statutory/regulatory references (verify before filing)
- `[verify]` — model knowledge that should be confirmed
- `[CourtListener/Westlaw/Lexis]` — tool-retrieved citations
- `[user provided]` — user-supplied documents
- `[web search — verify]` — web results requiring primary source check

---

## Limitations

- **Not legal advice** — always have material terms reviewed by qualified counsel
- **US law focus** — analysis defaults to US; provisions vary by jurisdiction
- **Context window** — very long documents may need section-by-section review
- **Jurisdiction gaps** — flag when non-US law may apply differently

---

## Examples

```
# Review an NDA
/review nda.pdf --side receiving-party

# Check a DPA (we're the processor)
/dpa-review customer-dpa.docx

# M&A diligence
/tabular-review acquisition-agreement.pdf --deal-type ma

# IP clearance
/clearance --mark "CloudSync" --class 9

# Litigation claim chart
/claim-chart --patent --infringement --claim 1 --target accused-product.pdf

# Privacy assessment
/pia-generation --activity "AI hiring tool"
```

---

## Integration Points

This skill coordinates with:
- Document review (PDF, DOCX, text extraction)
- Legal research (CourtListener, Westlaw via MCP)
- Contract management (Ironclad, DocuSign via MCP)
- Matter management (iManage, Everlaw via MCP)
- Communication (Slack via MCP)

---

*Last updated: 2026-05-15*
*Source: Anthropic Claude for Legal (https://github.com/anthropics/claude-for-legal)*