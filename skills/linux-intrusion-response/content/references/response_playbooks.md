# Response Playbooks

## Scenario 1: Confirmed Crypto Miner

### Symptoms
- High CPU usage (>90%)
- Unknown processes
- Connections to mining pools

### Response Steps
1. Isolate the system (if active threat)
2. Kill malicious processes
3. Identify persistence mechanisms
4. Block mining pool domains/IPs at firewall
5. Remove all persistence vectors
6. Verify cleanup
7. Monitor for recurrence

## Scenario 2: WebShell Detected

### Symptoms
- Suspicious files in web directory
- Unusual web server logs
- Abnormal outbound connections

### Response Steps
1. Isolate the system
2. Identify all web shells
3. Analyze web shell capabilities
4. Check for additional compromised files
5. Determine initial access vector
6. Clean and rebuild affected web application
7. Patch vulnerability used for initial access
8. Implement WAF rules

## Scenario 3: Unauthorized Access

### Symptoms
- Unexpected user logins
- New user accounts
- Modified SSH keys

### Response Steps
1. Determine scope of compromise
2. Review access logs
3. Identify affected accounts
4. Lock compromised accounts
5. Remove unauthorized accounts
6. Reset all passwords
7. Revoke and regenerate SSH keys
8. Enable enhanced monitoring

## Scenario 4: Data Exfiltration

### Symptoms
- Large outbound data transfers
- Unusual network traffic patterns
- Modified log files

### Response Steps
1. Block exfiltration channel
2. Preserve evidence
3. Identify data scope
4. Notify stakeholders
5. Contain affected systems
6. Eradicate persistence
7. Recover and rebuild

## Containment Strategy

### Network Isolation
- Disconnect network cable
- Disable network interface
- Firewall rules to block all outbound

### Evidence Preservation
- Create disk image
- Preserve memory if possible
- Document system state
