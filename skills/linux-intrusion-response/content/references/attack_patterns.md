# Attack Patterns Reference

## Initial Access

### Brute Force SSH
- Multiple failed logins followed by success
- Login from unusual IP addresses
- Root login attempts

### Web Application Exploits
- SQL Injection
- Remote File Inclusion (RFI)
- Local File Inclusion (LFI)
- Command Injection

## Privilege Escalation

### SUID Binaries
- Find SUID binaries: `find / -perm -4000 2>/dev/null`
- Check GTFOBins for exploitation

### Sudo Misconfigurations
- `sudo -l` to list allowed commands
- Look for NOPASSWD entries

### Kernel Exploits
- Check kernel version against CVE database

## Persistence

### Cron Jobs
- `/etc/crontab`
- `/etc/cron.d/`
- `/var/spool/cron/`
- User crontabs

### Systemd Services
- `/etc/systemd/system/`
- User services

### SSH Keys
- `~/.ssh/authorized_keys`
- `~/.ssh/authorized_keys2`

### Startup Scripts
- `/etc/rc.local`
- `/etc/init.d/`
- `/etc/profile.d/`

## Lateral Movement

### SSH
- Password guessing
- SSH key reuse
- Agent forwarding

### Internal Exploitation
- Network service exploits
- Shared credentials

## Exfiltration

### DNS Tunneling
- Unusual DNS queries
- Long subdomain queries

### HTTP Exfiltration
- Large outbound POST requests
- Unusual data destinations

## Crypto Mining

### Indicators
- High CPU usage
- Connections to known mining pools
- Modified system binaries
