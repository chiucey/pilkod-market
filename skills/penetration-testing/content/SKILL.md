---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 21a95bf36de337b68e5e9bb64f12b45b
    PropagateID: 21a95bf36de337b68e5e9bb64f12b45b
    ReservedCode1: 304502202f8de7bd6b276c9d6403bb63172bb6231d5d0d6098007c2c32c04a8d2237f8c6022100f7e95aaedeada789bcda0af2cf5b9e2172a02a567430d98815cf8d6f23384ffa
    ReservedCode2: 30450220067b1c69242d498a4a118df886596be2675e24a945cf86c091e9b2794cadf3370221008b454840c7f5f83a2deaa1d6b06dc19cf60f0e32dadf205ef84766b0a0af0047
description: Use when users ask for penetration testing, security assessment, vulnerability scanning, ethical hacking, PTES methodology, security audit, red team operation, or network security testing. Covers full penetration testing lifecycle including reconnaissance, vulnerability scanning, exploitation, privilege escalation, and reporting.
name: penetration-testing
---

# Penetration Testing Professional Skill

A comprehensive skill for executing full-spectrum penetration testing engagements following industry-standard methodologies.

## Core Workflow

### Phase 1: Reconnaissance (Information Gathering)

**Objective**: Gather maximum intelligence about the target while maintaining operational security.

**Activities**:
1. **OSINT Collection**
   - Domain/IP registration details (WHOIS, DNS records)
   - Email addresses and employee information
   - Public documents, S3 buckets, Git repositories
   - Social media intelligence

2. **Passive Reconnaissance**
   - Shodan, Censys, BuiltWith enumeration
   - Certificate transparency logs
   - Wayback Machine archival data

3. **Active Reconnaissance**
   - DNS zone transfers
   - Subdomain enumeration (brute force + dictionary)
   - Network mapping

**Deliverable**: Reconnaissance report with attack surface inventory

---

### Phase 2: Scanning & Enumeration

**Objective**: Identify live hosts, open ports, services, and potential vulnerabilities.

**Network Scanning**:
```bash
# TCP SYN scan
nmap -sS -sV -sC -p- -T4 -oA full_scan <target>

# UDP scan (top 100 ports)
nmap -sU --top-ports 100 -oA udp_scan <target>

# Service version detection
nmap -sV --version-intensity 5 <target>
```

**Vulnerability Assessment**:
- Port-specific vulnerability checks
- CVE enumeration for identified services
- Configuration weakness identification

**Enumeration Focus Areas**:
| Target Type | Enumeration Focus |
|-------------|-------------------|
| Web Apps | Directories, parameters, technologies, APIs |
| Networks | Shares, protocols, authentication |
| APIs | Endpoints, methods, authentication, rate limits |
| Cloud | IAM, S3 buckets, metadata services |

---

### Phase 3: Exploitation

**Objective**: Safely demonstrate vulnerabilities with authorization.

**Pre-Exploitation Checklist**:
- [ ] Scope verification completed
- [ ] Safety margins established (rollback plans)
- [ ] Impact assessment documented
- [ ] Client notified of active testing

**Exploitation Techniques by Category**:

#### Web Application Exploits
- SQL Injection (Union, Boolean, Time-based)
- Cross-Site Scripting (Reflected, Stored, DOM)
- Authentication bypasses
- IDOR vulnerabilities
- SSRF exploitation
- Command Injection

#### Network Exploits
- SMB/Windows exploits (EternalBlue, etc.)
- SSH brute force / key exchange attacks
- FTP exploits
- SMTP relaying

#### Cloud Exploits
- IAM privilege escalation
- SSRF for metadata access
- S3 bucket misconfiguration
- Overpermissive IAM roles

**Post-Exploitation**:
- Local enumeration
- Privilege escalation attempts
- Lateral movement planning
- Data exfiltration simulation
- Persistence establishment (documentation only)

---

### Phase 4: Reporting

**Deliverable Structure**:

```markdown
# Penetration Test Report

## Executive Summary
- Scope overview
- Key findings summary
- Risk rating
- Recommendations priority

## Methodology
- Framework used (PTES/OWASP/NIST)
- Testing phases executed
- Tools employed

## Findings Detail
For each finding:
- Vulnerability title
- CVSS score and rating
- Description
- Proof of concept / Steps to reproduce
- Impact assessment
- Remediation recommendations
- References

## Appendices
- Raw tool outputs
- Traffic captures
- Screenshots
```

**CVSS Scoring**:
| Rating | Score Range |
|--------|-------------|
| Critical | 9.0 - 10.0 |
| High | 7.0 - 8.9 |
| Medium | 4.0 - 6.9 |
| Low | 0.1 - 3.9 |
| None | 0.0 |

---

## Methodology Frameworks

### PTES (Penetration Testing Execution Standard)

1. Pre-Engagement Interactions
2. Intelligence Gathering
3. Threat Modeling
4. Vulnerability Analysis
5. Exploitation
6. Post-Exploitation
7. Reporting

### OWASP Testing Guide Focus Areas

- Configuration & Deployment Management
- Identity Management
- Authentication
- Authorization
- Session Management
- Input Validation
- Error Handling
- Cryptography
- Business Logic
- Client-Side Testing

---

## Common Tools Reference

| Phase | Tools |
|-------|-------|
| Recon | Amass, Sublist3r, theHarvester, Maltego, Recon-ng |
| Scanning | Nmap, Masscan, OpenVAS, Nessus |
| Web Testing | Burp Suite, OWASP ZAP, sqlmap, XSStrike |
| Exploitation | Metasploit, Cobalt Strike, PowerSploit |
| Password | Hashcat, John the Ripper, Hydra |
| Post-Exploit | BloodHound, Mimikatz, Empire |
| Reporting | Dradis, Faraday, custom templates |

---

## Operational Security Guidelines

**DO**:
- Always verify scope before testing
- Use safe/development environments when possible
- Implement rate limiting in scripts
- Document everything
- Report immediately if critical vulnerabilities found

**NEVER**:
- Test without authorization
- Exfiltrate real sensitive data
- Leave persistence mechanisms active
- Test production during business hours without consent
- Share client data outside engagement scope

---

## Escalation Triggers

Immediately escalate to client if:

- **Critical Findings**: RCE, SQLi with data exposure, authentication bypass
- **Data Breach Indicators**: Real PII/financial data exposure
- **Safety Concerns**: Potential for service disruption
- **Out-of-Scope Discovery**: Sensitive systems inadvertently discovered

---

## References

See `references/` directory for:
- `pentest-checklist.md` - Detailed phase-by-phase checklist
- `cvss-calculator.md` - CVSS scoring guide
- `report-template.md` - Report template with examples
- `tools-usage.md` - Common tool command references
