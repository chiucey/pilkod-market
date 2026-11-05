# Tools Reference

## Process Analysis

### ps
```bash
ps aux --forest          # Tree view
ps -eo pid,user,cmd      # Custom format
ps aux | grep suspicious
```

### top/htop
```bash
top -c                  # Command line
htop                    # Interactive
```

### lsof
```bash
lsof -i                 # Network connections
lsof -p PID             # Files by process
lsof /path/to/file      # Process using file
```

## Network Analysis

### netstat/ss
```bash
netstat -tulpn          # Listening ports
ss -tulpn              # Alternative
netstat -anp            # All connections
```

### iftop/nethogs
```bash
iftop                   # Bandwidth per connection
nethogs                 # Traffic per process
```

### tcpdump
```bash
tcpdump -i eth0 -w capture.pcap
tcpdump -r capture.pcap -n
```

## File Analysis

### find
```bash
find / -perm -4000 2>/dev/null          # SUID files
find / -mtime -7 -type f 2>/dev/null    # Recent files
find /tmp -type f 2>/dev/null           # Temp files
```

### stat
```bash
stat /path/to/file                      # Full file metadata
```

## Log Analysis

### grep/egrep
```bash
grep -E "failed|error" /var/log/auth.log
grep -i "eval\|base64" /var/www/*.php
```

### ausearch (auditd)
```bash
ausearch -k auth
ausearch -ts recent
```

## Memory Analysis

### memdump
```bash
memdump -p PID
```

## Rootkit Detection

### chkrootkit
```bash
chkrootkit
```

### rkhunter
```bash
rkhunter --check
```

## System State

### who/w/last
```bash
who                       # Current users
w                         # Detailed current users
last                      # Recent logins
lastb                     # Failed logins
```

### history
```bash
cat ~/.bash_history
```
