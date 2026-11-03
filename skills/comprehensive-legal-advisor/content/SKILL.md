---
name: comprehensive-legal-advisor
description: >
  A comprehensive legal advisor skill that handles a wide range of legal tasks across multiple domains. Use when users ask about legal matters including contract review (NDA, MSA, vendor agreements), litigation management (matter intake, demand letters, legal holds), employment law (termination review, worker classification, investigations), privacy compliance (DSAR responses, DPIA, DPA review), IP protection (cease-desist letters, trademark clearance, infringement triage), corporate governance (board minutes, written consents, M&A diligence), regulatory compliance (NPRM comments, policy drafting, gap analysis), product launches (legal review, marketing claims), law student assistance (case briefs, bar prep, IRAC practice), and legal clinic workflows (client intake, memo drafting, form generation). Trigger phrases include: "legal review", "review this contract", "litigation matter", "employment issue", "privacy compliance", "IP protection", "corporate governance", "regulatory compliance", "product launch legal", "law school help", "legal clinic".
argument-hint: "[domain or legal topic]"
---

# Comprehensive Legal Advisor

## Purpose

A comprehensive legal advisor that handles diverse legal tasks across multiple practice areas. This skill serves as a unified entry point for legal work, routing to appropriate sub-workflows and maintaining consistent quality standards across all domains.

## Core Capabilities

This skill integrates legal expertise across the following domains:

### 1. Commercial Contracts
- **NDA Review:** Fast triage into GREEN/YELLOW/RED based on playbook positions
- **MSA/SaaS Review:** Standard agreement review with escalation flags
- **Vendor Agreement Review:** Third-party contract analysis
- **Renewal Tracking:** Contract lifecycle management

### 2. Litigation Management
- **Matter Intake:** Uniform intake covering identification, conflicts, risk triage, materiality
- **Demand Letters:** Drafting and triage of demand correspondence
- **Legal Hold:** Preservation obligations and notice management
- **Privilege Log Review:** Work product and privilege documentation

### 3. Employment Law
- **Termination Review:** High-risk flag detection, severance, and release analysis
- **Worker Classification:** Exempt/non-exempt determination and FLSA compliance
- **Internal Investigations:** Investigation management and memo drafting
- **Wage & Hour QA:** Back-pay calculations and penalty assessments

### 4. Privacy Compliance
- **DSAR Response:** Complete workflow from identity verification to response drafting
- **DPIA Generation:** Privacy impact assessment for data processing activities
- **DPA Review:** Data processing agreement analysis
- **Policy Monitoring:** Privacy policy review and gap analysis

### 5. Intellectual Property
- **Cease-Desist Letters:** Send and receive modes with enforcement posture calibration
- **Trademark Clearance:** Clearance searches and risk assessment
- **Infringement Triage:** Claims assessment and response options
- **FTO Analysis:** Freedom-to-operate review for products and features

### 6. Corporate Governance
- **Board Minutes:** Meeting minutes in house format with written consents
- **Written Consents:** Corporate written consent drafting
- **Entity Compliance:** State compliance and annual requirements
- **M&A Diligence:** Due diligence grid and issue extraction

### 7. Regulatory Compliance
- **NPRM Comments:** Comment period tracking and decision logging
- **Policy Drafting:** Regulatory policy development and redrafting
- **Gap Analysis:** Compliance gap surfacing and tracking
- **Regulatory Monitoring:** Feed watching for relevant changes

### 8. Product Legal
- **Launch Review:** Full framework review against 8-category standard
- **Feature Risk Assessment:** Deep-dive on complex product features
- **Marketing Claims:** Substantiation review for marketing materials
- **Sector Overlays:** Children, gaming, fintech, health, education compliance

### 9. AI Governance
- **Use Case Triage:** AI feature classification and governance requirements
- **AIA Generation:** AI impact assessment drafting
- **Policy Starter:** AI usage policy development
- **Vendor AI Review:** Third-party AI terms analysis

### 10. Law Student Tools
- **Case Brief:** Scaffolded brief writing with drill-me mode
- **Bar Prep Questions:** MBE-style question practice
- **IRAC Practice:** Legal analysis framework training
- **Outline Builder:** Course outline construction

### 11. Legal Clinic
- **Client Intake:** Uniform client intake process
- **Memo Drafting:** Legal memo creation for clinic matters
- **Form Generation:** Legal form templates
- **Supervisor Review Queue:** Review tracking and status management

## Workflow

### Step 1: Identify the Domain

Ask the user to specify or infer from context which legal domain applies:

```
What type of legal matter is this?

1. Commercial Contracts (NDA, MSA, vendor agreements)
2. Litigation (disputes, demands, litigation holds)
3. Employment (terminations, classifications, investigations)
4. Privacy (data requests, compliance, policies)
5. IP (trademarks, copyrights, cease-desist)
6. Corporate (governance, M&A, compliance)
7. Regulatory (agency rules, comments, policy)
8. Product (launches, claims, features)
9. AI Governance (AI usage, impact assessments)
10. Law Student (case briefs, bar prep, study)
11. Legal Clinic (client matters, memos, forms)
12. General Legal Question
```

### Step 2: Route to Appropriate Skill

Based on domain selection:

- **Commercial Contracts:** Apply playbook-based triage, use GREEN/YELLOW/RED framework
- **Litigation:** Create matter workspace, run conflict checks, establish timeline
- **Employment:** Run high-risk flags, check jurisdiction requirements, document decisions
- **Privacy:** Classify request type, verify identity, walk systems, assess exemptions
- **IP:** Identify rights, assess conduct, calibrate to enforcement posture
- **Corporate:** Confirm format, verify quorum, draft in house style
- **Regulatory:** Check comment periods, log decisions, track deadlines
- **Product:** Run 8-category framework, calibrate to house risk table
- **AI Governance:** Classify use case, determine assessment requirements
- **Law Student:** Apply scaffolded approach, match preferred format
- **Legal Clinic:** Follow intake process, maintain supervisor review queue

### Step 3: Execute Skill-Specific Workflow

Follow the detailed workflow for the selected domain. Reference domain-specific guidance and templates.

### Step 4: Quality Gates

Apply standard quality gates:

1. **Source Attribution:** Tag all citations with source (Westlaw, CourtListener, web search, model knowledge)
2. **Unverified Flags:** Mark uncertain items with [verify] or [SME VERIFY]
3. **Privilege Check:** Verify output destination before applying work-product headers
4. **Non-Lawyer Gate:** For consequential actions, confirm attorney review before proceeding
5. **Citation Verification:** Verify all legal citations against primary sources before reliance

### Step 5: Output and Handoffs

- Provide structured output matching domain-specific format
- Flag escalations and automatic handoffs
- Close with decision tree for next steps
- Log matter and decisions per house process

## Universal Guardrails

### Destination Check
Before producing output, verify where it will go. Public channels, company-wide lists, and counterparties waive privilege. Offer privileged vs. sanitized versions.

### Source Attribution Tiering
- `[settled]` — Stable, well-known references unlikely to have changed
- `[verify]` — Real citations that should be verified against primary source
- `[verify-pinpoint]` — High fabrication risk; always verify against primary source

### No Silent Supplement
If research returns insufficient results, report and stop. Do not fill gaps from web search or model knowledge without asking. Present options: broaden search, try different tool, accept web search with tags, or stop and flag.

### Consequential Action Gate
For actions with legal consequences (signing documents, filing, sending letters, clearing launches), confirm with non-lawyer users that attorney review has occurred.

## Matter Workspace Integration

Check `## Matter workspaces` in the applicable practice-level CLAUDE.md:
- If enabled and no active matter: prompt for matter selection or creation
- Load matter-specific context and overrides
- Write outputs to matter folder
- Never read another matter's files unless `Cross-matter context` is `on`

## Output Structure

Standard output structure varies by domain but always includes:
- Work-product header (if applicable)
- Domain-specific content
- Source attribution for all citations
- Action items with owners and deadlines
- Escalation flags if applicable
- Decision tree for next steps

## What This Skill Does

- Provides unified entry point for diverse legal tasks
- Routes to appropriate domain-specific workflows
- Maintains consistent quality standards across all domains
- Applies universal guardrails (destination check, source attribution, no silent supplement)
- Flags escalations and handles routine matters

## What This Skill Does Not Do

- Replace attorney judgment on close cases
- Guarantee legal sufficiency of output
- Make final decisions on consequential actions without human review
- Bypass quality gates or escalation requirements