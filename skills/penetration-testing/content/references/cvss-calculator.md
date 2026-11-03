# CVSS Scoring Guide

Common Vulnerability Scoring System (CVSS) v3.1 reference for standardized vulnerability severity assessment.

## CVSS Score Ranges

| Severity Level | Score Range | Description |
|----------------|-------------|-------------|
| None | 0.0 | No vulnerability |
| Low | 0.1 - 3.9 | Minimal impact, easily exploitable or low impact |
| Medium | 4.0 - 6.9 | Moderate impact, requires some conditions |
| High | 7.0 - 8.9 | Significant impact, straightforward exploitation |
| Critical | 9.0 - 10.0 | Extreme impact, trivial exploitation |

## Metric Groups

### 1. Base Metrics

#### Attack Vector (AV)
| Metric | Score | Description |
|--------|-------|-------------|
| Network (N) | 0.85 | Remotely exploitable over network |
| Adjacent (A) | 0.62 | Requires local network access |
| Local (L) | 0.55 | Requires local access to system |
| Physical (P) | 0.20 | Requires physical access |

#### Attack Complexity (AC)
| Metric | Score | Description |
|--------|-------|-------------|
| Low (L) | 0.77 | No specialized conditions |
| High (H) | 0.44 | Specialized conditions required |

#### Privileges Required (PR)
| Metric | Score | Description |
|--------|-------|-------------|
| None (N) | 0.85 | No privileges needed |
| Low (L) | 0.62 | Basic user privileges |
| High (H) | 0.27 | Administrative privileges |

#### User Interaction (UI)
| Metric | Score | Description |
|--------|-------|-------------|
| None (N) | 0.85 | No user interaction required |
| Required (R) | 0.62 | User must perform action |

#### Scope (S)
| Metric | Score | Description |
|--------|-------|-------------|
| Unchanged (U) | - | Does not affect other components |
| Changed (C) | - | Affects other components |

#### Confidentiality Impact (C)
| Metric | Score | Description |
|--------|-------|-------------|
| High (H) | 0.56 | Total confidentiality loss |
| Low (L) | 0.22 | Partial confidentiality loss |
| None (N) | 0.00 | No confidentiality impact |

#### Integrity Impact (I)
| Metric | Score | Description |
|--------|-------|-------------|
| High (H) | 0.56 | Total integrity loss |
| Low (L) | 0.22 | Partial integrity loss |
| None (N) | 0.00 | No integrity impact |

#### Availability Impact (A)
| Metric | Score | Description |
|--------|-------|-------------|
| High (H) | 0.56 | Total availability loss |
| Low (L) | 0.22 | Partial availability loss |
| None (N) | 0.00 | No availability impact |

---

## CVSS Calculation Examples

### Example 1: SQL Injection (Critical)

```
Attack Vector: Network (N) = 0.85
Attack Complexity: Low (L) = 0.77
Privileges Required: None (N) = 0.85
User Interaction: None (N) = 0.85
Scope: Unchanged (U)
Confidentiality: High (H) = 0.56
Integrity: High (H) = 0.56
Availability: Low (L) = 0.22

CVSS Base Score: 9.8 (Critical)
```

### Example 2: Reflected XSS (Medium)

```
Attack Vector: Network (N) = 0.85
Attack Complexity: Low (L) = 0.77
Privileges Required: None (N) = 0.85
User Interaction: Required (R) = 0.62
Scope: Unchanged (U)
Confidentiality: Low (L) = 0.22
Integrity: Low (L) = 0.22
Availability: None (N) = 0.00

CVSS Base Score: 6.1 (Medium)
```

### Example 3: Information Disclosure (Low)

```
Attack Vector: Network (N) = 0.85
Attack Complexity: Low (L) = 0.77
Privileges Required: Low (L) = 0.62
User Interaction: None (N) = 0.85
Scope: Unchanged (U)
Confidentiality: Low (L) = 0.22
Integrity: None (N) = 0.00
Availability: None (N) = 0.00

CVSS Base Score: 4.3 (Medium/Low)
```

---

## Temporal Metrics (Optional)

Adjust base score based on current threat landscape.

| Metric | Options | Impact |
|--------|---------|--------|
| Exploit Code Maturity (E) | Not Defined, High, Functional, Proof-of-Concept, Unproven | +/- |
| Remediation Level (RL) | Not Defined, Unavailable, Workaround, Temporary Fix, Official Fix | +/- |
| Report Confidence (RC) | Not Defined, Confirmed, Reasonable, Unknown | +/- |

---

## Environmental Metrics (Optional)

Modify score based on organizational environment.

### Modified Base Metrics

- MAV (Modified Attack Vector)
- MAC (Modified Attack Complexity)
- MR (Modified Privileges Required)
- MUI (Modified User Interaction)
- MS (Modified Scope)
- MC (Modified Confidentiality)
- MI (Modified Integrity)
- MA (Modified Availability)

---

## Quick Reference Table

| Vulnerability Type | Typical AV | Typical AC | Typical PR | Typical UI | Typical C/I/A | Typical Score |
|-------------------|------------|------------|------------|------------|---------------|---------------|
| SQL Injection | Network | Low | None | None | High/High/High | 9.8 |
| RCE | Network | Low | None | None | High/High/High | 9.8 |
| CSRF | Network | Low | None | Required | None/Low/None | 4.3 |
| Open Redirect | Network | Low | None | None | None/Low/None | 6.1 |
| Stored XSS | Network | Low | None | Required | Low/Low/None | 6.1 |
| SSRF | Network | Low | None | None | High/Low/Low | 8.6 |
| IDOR | Network | Low | Low | None | Low/Low/None | 6.5 |
| Information Disclosure | Network | Low | Low | None | Low/None/None | 4.3 |
| DoS | Network | Low | None | None | None/None/High | 7.5 |

---

## Score Interpretation Guidelines

### Critical (9.0 - 10.0)
- Immediate action required
- Remote code execution possible
- Complete system compromise likely
- No authentication required

### High (7.0 - 8.9)
- Urgent attention needed
- Significant data exposure risk
- Authentication bypass possible
- Lateral movement likely

### Medium (4.0 - 6.9)
- Schedule remediation
- Partial data/access exposure
- Requires specific conditions
- Limited impact scope

### Low (0.1 - 3.9)
- Routine remediation
- Minimal direct impact
- Difficult exploitation
- Limited scope
