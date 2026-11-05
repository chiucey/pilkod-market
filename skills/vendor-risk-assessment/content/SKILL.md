---
name: vendor-risk-assessment
description: Vendor risk assessment and supplier due diligence skill. Use when users ask to check supplier risks, verify vendor compliance, investigate business risks, screen for bankruptcy, credit violations, state-owned asset procurement violations, or military procurement restrictions. Retrieves information from third-party credit platforms, national enterprise credit information systems, and public announcements.
---

# Vendor Risk Assessment Skill

## Core Functions

This skill conducts comprehensive due diligence on potential suppliers by retrieving and analyzing public information from multiple authoritative sources to identify business risks, compliance issues, and potential red flags.

## Data Sources

### Primary Sources
| Source | Type | Coverage |
|--------|------|----------|
| National Enterprise Credit Information Publicity System | Government | Basic registration, annual reports, administrative penalties |
| China Judgements Online | Government | Enforcement records, dishonesty lists |
| Tianyancha | Third-party | Business registration, shareholders, legal disputes |
| Qichacha | Third-party | Company profiles, risk indicators |
| Credit China | Government | Credit violations, blacklist records |

### Supplementary Sources
| Source | Type | Coverage |
|--------|------|----------|
| China Government Procurement Network | Government | Procurement violations, blacklists |
| Military Procurement Blacklist | Government | Military procurement restrictions |
| Listed Company Announcements (CSRC) | Regulatory | Disciplinary actions, legal violations |
| National Bankruptcy Information | Government | Bankruptcy proceedings, restructuring |

## Risk Categories to Check

### 1. Business Risk Indicators
- [ ] Bankruptcy proceedings or liquidation
- [ ] Business license revocation or cancellation
- [ ] Abnormal business operations
- [ ] Major debt overdue or pending lawsuits
- [ ] Operation suspension or business cessation

### 2. Credit & Compliance Risk
- [ ] Dishonest enforcement subject (Shixin Beizhixing Ren)
- [ ] Restricted high consumption (Xianzhi Gaoxiaofei)
- [ ] Enforcement records (Zhixing Xinxi)
- [ ] Administrative penalties (Xingzheng Chufa)
- [ ] Tax violations (Shuiwu Weigui)

### 3. Government Procurement Risk
- [ ] State-owned asset procurement violations
- [ ] Government procurement blacklist
- [ ] Public resource trading violations
- [ ] Bidding fraud records

### 4. Military Procurement Risk
- [ ] Military procurement blacklist (Jungui Caigou Weigui)
- [ ] Equipment procurement restrictions
- [ ] Defense industry restrictions
- [ ] National defense procurement violations

### 5. Listed Company Risk (if applicable)
- [ ] CSRC disciplinary actions
- [ ] Securities regulatory violations
- [ ] Disclosure violations
- [ ] Insider trading violations

## Execution Flow

### Step 1: Information Collection

Collect basic vendor information:
- Company name (full legal name)
- Unified Social Credit Code
- Registration number
- Key personnel names

### Step 2: Multi-Source Query

Query all relevant databases:
1. National Enterprise Credit System - basic info, annual reports
2. China Judgements Online - enforcement records
3. Tianyancha/QCQC - comprehensive risk screening
4. Credit China - credit violations
5. Government procurement platforms - procurement violations
6. Military procurement database - military restrictions

### Step 3: Risk Analysis

Analyze collected information:
- Categorize risks by type
- Assess severity and impact
- Identify key dates (occurrence, start/end of penalties)
- Verify information currency

### Step 4: Report Generation

Generate structured assessment report with all findings.

## Output Format

### Comprehensive Risk Assessment Report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VENDOR RISK ASSESSMENT REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANY INFORMATION
────────────────────────────────────────────────
Company Name: [Full Legal Name]
Unified Credit Code: [XXXXXXXXXXXXXXXXXX]
Registered Capital: [Amount] [Currency]
Legal Representative: [Name]
Registration Date: [YYYY-MM-DD]
Business Status: [Active/Deregistered/Abnormal/etc.]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RISK FINDINGS SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HIGH RISK (Immediate Attention Required)
────────────────────────────────────────────────
[Risk 1]: [Description]
  - Occurrence Date: [YYYY-MM-DD]
  - Source: [Source Name]
  - Details: [Specific information]

MEDIUM RISK (Review Required)
────────────────────────────────────────────────
[Risk 1]: [Description]
  - Start Date: [YYYY-MM-DD]
  - End Date: [YYYY-MM-DD] or "Ongoing"
  - Issuing Authority: [Authority Name]
  - Details: [Specific information]

INFO ONLY / LOW RISK
────────────────────────────────────────────────
[Item 1]: [Description]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TIMELINE OF KEY EVENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[YYYY-MM-DD] Event description
[YYYY-MM-DD] Event description
[YYYY-MM-DD] Event description

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA SOURCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Source 1: [URL/Platform Name]
- Source 2: [URL/Platform Name]
- Source 3: [URL/Platform Name]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ASSESSMENT CONCLUSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Risk Level: [LOW / MEDIUM / HIGH / CRITICAL]
Recommendation: [Approve / Conditional Approval / Reject / Further Due Diligence]
Remarks: [Additional notes]

Report Generated: [YYYY-MM-DD HH:MM:SS]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### No Risk Found Response

```
VENDOR RISK ASSESSMENT - CLEAR

Company: [Company Name]
Scope: Business risk, compliance, credit, procurement violations, military restrictions

CHECKED ITEMS:
- Business registration status - Active
- Enforcement records - None found
- Credit violations - None found
- Government procurement violations - None found
- Military procurement restrictions - None found
- Administrative penalties - None found

Data Sources Verified:
- National Enterprise Credit Information Publicity System
- China Judgements Online
- Tianyancha/QCQC
- Credit China

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ASSESSMENT RESULT: LOW RISK
No significant risk indicators identified based on available public data.

Report Generated: [YYYY-MM-DD HH:MM:SS]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Key Information Points to Extract

| Field | Description | Example |
|-------|-------------|---------|
| Occurrence Date | When the risk event occurred | 2024-03-15 |
| Start Date | When penalty/restriction began | 2024-03-20 |
| End Date | When penalty/restriction ended (if applicable) | 2025-03-20 |
| Issuing Authority | Organization that imposed the penalty | State Administration for Market Regulation |
| Penalty Content | Specific details of punishment | Fine of 500,000 RMB, business suspension |

## Error Handling

| Scenario | Response |
|----------|----------|
| Company not found | "Unable to locate [Company Name] in public databases. Please verify the company name or provide the Unified Social Credit Code." |
| Partial data available | Provide available information with note on limitations |
| API unavailable | "Temporarily unable to access [Data Source]. Please try again later or proceed with available information." |
| Conflicting information | Present all findings and note discrepancies for user review |

## Usage Examples

**User Input**:
```
Please check the risks for this supplier: Huawei Technologies Co., Ltd.
```

**Execution Flow**:
1. Extract company name: Huawei Technologies Co., Ltd.
2. Query multiple data sources
3. Analyze and categorize risks
4. Generate comprehensive report

**Expected Output**:
Complete risk assessment report (as format above)

## Technical Notes

- **API-First**: Query authoritative government and third-party platforms
- **Multi-Source Verification**: Cross-reference data from multiple sources
- **Freshness Check**: Note the date of last information update
- **Completeness**: Always attempt all risk categories even if no issues found
- **Source Attribution**: Always cite the source for each piece of information
