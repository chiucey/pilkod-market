# Security Pattern Reference

Reference guide for identifying security concerns during skill vetting.

## Credential Harvesting Patterns

### API Key Theft
```regex
/(api[_-]?key|secret|token|auth).*(read|get|extract|steal)/i
/(process\.env|os\.environ|getenv).*(key|secret|token)/i
```

### SSH/Cloud Credentials
```regex
/~/.ssh/|~/.aws/|~/.config/gcloud
/.pem|/.key|credentials.json|service_account.json
```

### Authentication Bypass
```regex
/auth.*skip|bypass.*auth|disable.*auth
/selfsigned|verify.*false|ssl.*verify.*false
```

## Data Exfiltration Patterns

### External Network Calls
```regex
/fetch\(|axios\.|requests\.|http\.request/i
/<(img|script|link).*src=["']https?:\/\/[^/]/i
/wget\s|curl\s.*-d\s.*http/i
```

### File Exfiltration
```regex
/fs\.(write|append).*http|stream.*upload/i
/formData|multipart|Content-Disposition.*filename/i
```

### Logging Sensitive Data
```regex
/console\.(log|debug).*(key|token|secret|password)/i
/logger\.(info|debug).*\$\{|log.*\(\$.*(key|secret)/i
```

## Code Execution Patterns

### Command Injection
```regex
/exec\(|spawn\(|eval\(|Function\(/
/child_process|os\.system|subprocess.*shell.*true/i
/\$\{.*\}|\$\(.*\)|`.*\$\{.*\}`/i
```

### Obfuscation
```regex
/atob\(|btoa\(|fromCharCode|charCodeAt/
/base64.*decode|encode.*base64|ZigZag|ROT13/i
/String\.fromCharCode.*eval|eval.*fromCharCode
```

### Dynamic Code Loading
```regex
/new\s+Function|Function.*apply|eval.*script/i
/dynamic.*import|import\(.*\)|require\(.*http/i
```

## Privilege Escalation Patterns

### Sudo/Admin Abuse
```regex
/sudo|chmod\s+[47]777|chown.*root/i
/capability|setuid|setgid/i
```

### Container Escape
```regex
/docker|socket|/proc|/sys/fs|cgroup/i
/mount.*host|nsenter|namespace/i
```

## File System Attacks

### Path Traversal
```regex
/\.\.\/|\.\.\\|%2e%2e|traverse|path.*injection/i
/readFile.*\.\.\/|writeFile.*\.\.\//i
```

### Symlink Attacks
```regex
/ln\s+-s|symlink|readlink.*\.\./i
```

## Social Engineering Patterns

### Phishing
```regex
/click.*here|verify.*account|urgent.*action/i
/login.*now|confirm.*identity|password.*reset/i
```

### Fake Updates
```regex
/update.*now|new.*version|security.*patch/i
/mandatory.*update|critical.*update/i
```

## Risk Scoring Matrix

| Category | Low (1) | Medium (5) | High (10) | Critical (25) |
|----------|---------|------------|-----------|---------------|
| File System | Read only, temp dirs | Read home | Write access | Root/system |
| Network | Localhost only | Internal only | External read | External write |
| Credentials | None | Read public | Read user secrets | Write/steal secrets |
| Code Exec | None | Safe eval | System commands | Shell injection |
| Persistence | None | Session only | Reinstall hook | Backdoor |

**Total Score Calculation:**
- Sum all category scores
- CRITICAL: >= 50
- HIGH: 25-49
- MEDIUM: 10-24
- LOW: < 10

## Permission Manifest Example

```yaml
permissions:
  file_system:
    level: read_only
    allowed_paths:
      - /tmp
      - ~/documents
    denied_paths:
      - ~/.ssh
      - ~/.aws
      - ~/.config

  network:
    level: internal_only
    allowed_domains:
      - api.example.com
    denied_patterns:
      - "*://*.tk
      - "*://*.ml"

  credentials:
    level: none
    read_access: []
    write_access: []

  execution:
    level: sandboxed
    allowed_apis:
      - Math
      - String
      - Array
    denied_apis:
      - eval
      - Function
      - exec
```

## Safe vs Unsafe Patterns Quick Reference

### SAFE - Generally Acceptable
- UI rendering and animations
- Local mathematical calculations
- Text processing and formatting
- User notification APIs
- Read-only data transformations
- File reading in user-designated directories

### CAUTION - Requires Review
- Any network calls
- File write operations
- Environment variable access
- Command-line argument parsing
- JSON/YAML parsing of user files
- Image/media processing

### UNSAFE - Requires Justification
- eval() or similar dynamic code
- External script loading
- Credential storage access
- System command execution
- Base64 encoding/decoding
- Regex patterns on sensitive data
