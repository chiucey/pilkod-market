# Vendor Risk Assessment - Comprehensive Risk Checklist

## 1. Business Operation Risks

### 1.1 Bankruptcy & Liquidation
| Item | Description | Data Source |
|------|-------------|-------------|
| Bankruptcy proceedings | Active or completed bankruptcy cases | Court records, Enterprise Credit System |
| Liquidation status | Whether company is under liquidation | Enterprise Credit System |
| Reorganization | Corporate restructuring records | Court announcements |
| Debt restructuring | Financial restructuring cases | Court records |

### 1.2 Business Status
| Item | Description | Data Source |
|------|-------------|-------------|
| Abnormal operations | Business license abnormalities | Enterprise Credit System |
| Revoked license | Business license revocation | Enterprise Credit System |
| Suspension of business | Business suspension records | Enterprise Credit System |
| Deregistration | Company deregistration | Enterprise Credit System |

### 1.3 Financial Risks
| Item | Description | Data Source |
|------|-------------|-------------|
| Major debt overdue | Significant outstanding debts | Court records, Media reports |
| Guarantee risks | Guarantee obligations | Tianyancha/QCQC |
| Loan defaults | Bank loan defaults | Court records, Credit China |

## 2. Credit & Compliance Risks

### 2.1 Enforcement Records
| Item | Term (CN) | Description |
|------|-----------|-------------|
| Dishonest execution | Shixin Beizhixing Ren | Refused to comply with legal obligations |
| Consumption restrictions | Xianzhi Gaoxiaofei | Restricted from high consumption |
| Enforcement cases | Beizhixing Ren | Pending enforcement cases |

### 2.2 Administrative Penalties
| Category | Examples | Issuing Authority |
|----------|----------|-------------------|
| Market regulation | Product quality, unfair competition | SAMR |
| Tax violations | Tax evasion, invoice fraud | SAT |
| Environmental | Pollution, waste disposal violations | MEE |
| Customs | Import/export violations | GAC |
| Food safety | Food safety violations | NMPA |
| Production safety | Workplace safety violations | MEM |

### 2.3 Credit Violations
| Violation Type | Description | Source |
|----------------|-------------|--------|
| Tax A/B grade | Poor tax credit rating | SAT |
| Invoice irregularities | VAT invoice fraud | SAT |
| Customs violations | Import/export rule violations | GAC |

## 3. Government Procurement Risks

### 3.1 Procurement Violations
| Violation Type | Description | Consequence |
|----------------|-------------|-------------|
| Bidding fraud | Collusion, bid rigging | Blacklisting |
| Contract violation | Failure to fulfill contracts | Penalties |
| Quality issues | Substandard products/services | Suspension |
| False statements | Fabricated qualifications | Disqualification |

### 3.2 Blacklists
| List Type | Scope | Duration |
|-----------|-------|----------|
| Government procurement blacklist | National/provincial | 1-5 years |
| State-owned asset procurement | SOE suppliers | Varies |
| Public resource trading | Public projects | 1-3 years |

### 3.3 Regulatory Actions
| Action | Description |
|--------|-------------|
| Warning | Verbal/written warning |
| Fine | Monetary penalty |
| Suspension | Temporary exclusion |
| Blacklisting | Permanent exclusion |

## 4. Military Procurement Risks

### 4.1 Military Blacklists
| Category | Description | Authority |
|----------|-------------|-----------|
| Procurement blacklist | Violations in military procurement (Jungui Caigou Weigui) | PLA Logistics Department |
| Equipment restrictions | Restricted from equipment supply | Defense Ministry |
| Defense industry ban | Prohibited from defense work | Military Commission |

### 4.2 Violation Types
| Type | Description |
|------|-------------|
| Quality violations | Substandard military equipment |
| Security violations | Information security breaches |
| Integrity violations | Corruption, kickbacks |
| Compliance violations | Regulations violations |

### 4.3 Consequences
| Consequence | Duration | Scope |
|-------------|----------|-------|
| Warning | N/A | Limited |
| Suspension | 1-3 years | All military procurement |
| Blacklisting | 3-5 years or permanent | Military sector |
| Criminal referral | N/A | Judicial prosecution |

## 5. Listed Company Risks (if applicable)

### 5.1 CSRC Disciplinary Actions
| Action | Description |
|--------|-------------|
| Public criticism | Formal reprimand |
| Warning | Administrative warning |
| Fine | Monetary penalty |
| License revocation | Business license removed |
| Market ban | Trading restrictions |

### 5.2 Regulatory Violations
| Violation Type | Severity | Common Penalties |
|----------------|----------|------------------|
| Disclosure violations | Medium | Fines, warnings |
| Fraud | High | Fines, criminal referral |
| Insider trading | High | Fines, trading ban |
| Market manipulation | High | Fines, prosecution |

### 5.3 Stock Exchange Actions
| Exchange | Actions Available |
|----------|-------------------|
| SSE | Public condemnation, listing suspension |
| SZSE | Criticism, delisting risk warnings |
| ChiNext | Risk disclosure requirements |

## 6. Personnel & Shareholder Risks

### 6.1 Legal Representative
| Check Item | Risk Indicator |
|------------|----------------|
| Other companies | Multiple legal representative roles |
| Enforcement records | Personal enforcement cases |
| Industry bans | Prohibited from certain industries |

### 6.2 Major Shareholders
| Check Item | Risk Indicator |
|------------|----------------|
| Enforcement records | Shareholder dishonesty records |
| Industry restrictions | Prohibited from regulated industries |
| Cross-border issues | Foreign sanctions, restrictions |

### 6.3 Key Personnel
| Role | Risk Check |
|------|------------|
| Directors | Disqualification records |
| Supervisors | Enforcement history |
| Senior executives | Personal litigation |

## 7. Industry-Specific Risks

### 7.1 Regulated Industries
| Industry | Key Checks |
|----------|------------|
| Financial services | Financial licenses, regulatory status |
| Healthcare | Medical licenses, drug approval status |
| Education | Education permits, qualification status |
| Construction | Construction permits, safety records |
| Food & beverage | Food licenses, hygiene permits |

### 7.2 Qualifications & Licenses
| License Type | Check Point |
|--------------|-------------|
| Business license | Validity, scope |
| Industry licenses | Specific sector permits |
| Operating permits | Operational authorization |
| Quality certifications | ISO, other standards |

## 8. Risk Assessment Matrix

### Severity Levels

| Level | Score | Description | Action Required |
|-------|-------|-------------|------------------|
| Critical | 9-10 | Major violations, blacklisted | Immediate rejection |
| High | 7-8 | Significant risks, multiple issues | Strong caution, senior review |
| Medium | 4-6 | Moderate concerns, single issues | Conditional approval |
| Low | 1-3 | Minor issues, clean record | Standard approval |
| None | 0 | No risk indicators | Fast track approval |

### Risk Category Weights

| Category | Weight | Notes |
|----------|--------|-------|
| Military procurement blacklist | 30% | Absolute disqualifier if active |
| Government procurement blacklist | 25% | Depends on duration |
| Dishonest execution | 20% | Major red flag |
| Bankruptcy/liquidation | 15% | Business viability concern |
| Administrative penalties | 10% | Depends on severity |

## 9. Information Fields to Extract

For each risk finding, collect:

```json
{
  "risk_type": "Type of risk",
  "severity": "Severity level",
  "occurrence_date": "YYYY-MM-DD",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD or null",
  "issuing_authority": "Issuing Authority",
  "penalty_content": "Penalty Content",
  "source": "Data Source",
  "source_url": "URL",
  "query_date": "YYYY-MM-DD",
  "verification_status": "Verified/Pending"
}
```

### Field Descriptions

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| risk_type | Yes | Category of risk identified | "Dishonest execution" |
| severity | Yes | Impact level (Critical/High/Medium/Low) | "High" |
| occurrence_date | Recommended | When risk event first occurred | "2024-03-15" |
| start_date | For penalties | When restriction/penalty began | "2024-03-20" |
| end_date | Optional | When restriction ends (null if ongoing) | "2025-03-20" |
| issuing_authority | For penalties | Agency that issued the penalty | "SAMR" |
| penalty_content | For penalties | Details of punishment | "Fine of 500,000 RMB" |
| source | Yes | Where information was obtained | "China Judgements Online" |
| source_url | Recommended | Direct link to source | "https://..." |
| query_date | Yes | When data was retrieved | "2026-04-10" |
| verification_status | Yes | Confidence level | "Verified" |
