# Log Formats Reference

## SSH Logs (`/var/log/auth.log` or `/var/log/secure`)

### Format
```
Month Day HH:MM:SS hostname sshd[pid]: Failed password for user from IP port ssh2
Month Day HH:MM:SS hostname sshd[pid]: Accepted password for user from IP port ssh2
```

### Key Fields
- `Failed password` - Failed authentication attempts
- `Accepted password` - Successful login
- `reverse mapping checking` - DNS PTR check
- `Publickey` - SSH key authentication

## Cron Logs

### Format
```
CRON[pid]: (user) CMD (/path/to/command)
```

## Systemd Logs

```bash
journalctl -u service-name
journalctl --since "2024-01-01" --until "2024-01-02"
```

## Web Server Access Logs

### Apache
```
127.0.0.1 - - [01/Jan/2024:00:00:00 +0000] "GET /path HTTP/1.1" 200 1234
```

### Nginx
```
127.0.0.1 - - [01/Jan/2024:00:00:00 +0000] "GET /path HTTP/1.1" 200 1234 "-" "User-Agent"
```

## Bash History

### Format
```
# timestamp
command
# timestamp
command
```

## Last/Lastb

### Format
```
username pts/X IP address :timestamp still logged in
username pts/X IP address :timestamp - :timestamp (duration)
```

## dmesg / Syslog

```bash
dmesg | grep -i "malware"
dmesg | tail -50
```
