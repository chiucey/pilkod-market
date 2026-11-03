# Common IOCs (Indicators of Compromise)

## Suspicious IP Addresses

### Common C2 Servers
- Known Tor exit nodes
- Suspicious mining pools
- Known malicious infrastructure

### Suspicious Countries
- High-risk regions: Eastern Europe, Southeast Asia

## Suspicious Domains
- Typosquatting domains
- Newly registered domains
- DGA (Domain Generation Algorithm) patterns

## File Paths

### High-Risk Paths
- `/tmp/` - Temporary files, often used by malware
- `/dev/shm/` - Shared memory, used for fileless malware
- `/var/tmp/` - Persistent temporary storage
- `/root/` - Root home directory
- Hidden directories starting with `.`

### Suspicious File Extensions
- `.tmp`, `.bak`, `.old`
- `.sh`, `.py`, `.pl` in web directories
- `.so` in unusual locations

## Registry / Configuration
- `/etc/ld.so.preload` - LD_PRELOAD backdoor
- `/etc/cron.d/` - Cron-based persistence
- SSH authorized_keys modifications

## Network Indicators
- High port numbers (40000-65535)
- Unusual protocols (IRC, custom protocols)
- Long-standing connections to external IPs
