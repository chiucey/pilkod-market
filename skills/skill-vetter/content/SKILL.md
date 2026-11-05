---
name: skill-vetter
description: Security-first skill vetting for AI agents. Use when users ask to check, review, audit, vet, or assess the security of a skill before installing from ClawdHub, GitHub, or other sources. Also triggers when users mention "skill safety", "install check", "security review", "permission audit", "trust rating", or "is this skill safe". Triggers automatically when any skill installation is requested.
---

# Skill Vetter

Security-first vetting workflow for AI agent skills from external sources.

## Workflow

### Phase 1: Source Analysis

1. **Identify the skill source**
   - ClawdHub marketplace
   - GitHub repository
   - Direct file upload
   - Unknown/third-party source

2. **Check source reputation**
   - Author credibility and history
   - Download/installation count
   - Community reviews and issues
   - Last update date

### Phase 2: Permission Scope Analysis

Review the skill's capabilities and permission requests:

1. **File System Access**
   - Read/write to arbitrary paths
   - Access to sensitive directories (`~/.ssh`, `~/.aws`, etc.)
   - Path traversal patterns

2. **Network Access**
   - External API calls
   - Data exfiltration potential
   - Unencrypted communications

3. **Credential Access**
   - API key usage
   - Secret reading patterns
   - Authentication bypass attempts

4. **System Access**
   - Command execution
   - Process manipulation
   - Service management

### Phase 3: Code Pattern Analysis

Scan for security red flags:

**Critical Red Flags (Block Immediately)**
- Base64/Obfuscated code execution
- Credential harvesting patterns
- Reverse shell attempts
- Privilege escalation attempts
- Data exfiltration endpoints

**High Risk Patterns (Require Manual Review)**
- External script downloads
- Unverified dependencies
- Overly broad file access
- Hidden or obfuscated logic
- Dynamic code evaluation

**Medium Risk Patterns (Flag for Awareness)**
- Wide permission scopes
- Complex error handling
- Extensive logging
- Retry mechanisms

**Low Risk (Generally Safe)**
- Pure UI/rendering operations
- Local calculations
- User-facing notifications

### Phase 4: Dependency Audit

1. **External Dependencies**
   - Check for malicious packages
   - Verify package integrity
   - Review transitive dependencies

2. **Tool Dependencies**
   - Required MCP tools
   - System command usage
   - API requirements

### Phase 5: Risk Assessment

Generate a structured risk profile:

```
┌─────────────────────────────────────────────────────────────┐
│ SECURITY VETTING REPORT                                     │
├─────────────────────────────────────────────────────────────┤
│ Skill: [name]                                               │
│ Source: [source type]                                        │
│ Overall Risk Level: [LOW / MEDIUM / HIGH / CRITICAL]         │
├─────────────────────────────────────────────────────────────┤
│ Permission Scope:                                            │
│   File System:     [scope rating]                           │
│   Network:         [scope rating]                             │
│   Credentials:     [scope rating]                            │
│   System:          [scope rating]                            │
├─────────────────────────────────────────────────────────────┤
│ Red Flags Found:                                            │
│   [ ] Critical: [count]                                      │
│   [ ] High: [count]                                          │
│   [ ] Medium: [count]                                        │
│   [ ] Low: [count]                                           │
├─────────────────────────────────────────────────────────────┤
│ Verdict: [APPROVED / CONDITIONAL / REJECTED]                │
│ Recommendation: [brief guidance]                             │
└─────────────────────────────────────────────────────────────┘
```

### Phase 6: Recommendation

Based on findings, provide one of:

- **APPROVED**: Safe to install, no significant concerns
- **CONDITIONAL**: Install with specific precautions listed
- **REJECTED**: Do not install, blocking issues found
- **MANUAL REVIEW**: Requires user judgment on specific concerns

For CONDITIONAL or MANUAL REVIEW, list:
1. Specific concerns
2. Recommended mitigations
3. Questions to ask the skill author

## Output Format

Always provide:

1. **Summary**: One-line verdict
2. **Risk Score**: 0-100 numeric rating
3. **Risk Level**: LOW / MEDIUM / HIGH / CRITICAL
4. **Findings**: Categorized list of all issues
5. **Recommendations**: Actionable next steps

## Special Handling

**For ClawdHub Skills**
- Verify digital signature if present
- Check trust rating and reviews
- Review published permission manifest

**For GitHub Repos**
- Clone and analyze locally
- Check git history for suspicious commits
- Review CI/CD pipeline for data exfiltration

**For Direct Uploads**
- Full sandbox analysis required
- Never execute before vetting complete
- Preserve original file for reference

## When to Escalate to User

Always ask user confirmation before:
- Blocking a skill installation
- Reporting a skill as malicious
- Providing definitive security guarantees

Remember: You are an advisor. The user makes the final decision.
