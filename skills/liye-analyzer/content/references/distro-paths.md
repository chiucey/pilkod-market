# 各发行版关键路径速查

> sosreport 在不同发行版下的目录结构基本一致（都遵循 `sos_commands/<group>/<cmd>` 规范），但**日志路径**和**发行版信息文件**差异较大。读文件前先确定发行版。

## 发行版识别

| 发行版 | 识别文件（按优先级） |
|--------|---------------------|
| 麒麟高级服务器 V10/V11 | `etc/kylin-release`（含 `[Kylin]` 段）→ `etc/os-release` 的 `ID=kylin` |
| 麒麟桌面 V10 | `etc/kylin-release` + `etc/os-release` 的 `VARIANT_ID=desktop` |
| 统信 UOS | `etc/os-release` 的 `ID=uos` 或 `ID=deepin` |
| openEuler | `etc/os-release` 的 `ID=openEuler` |
| CentOS / RHEL | `etc/redhat-release` 或 `etc/os-release` 的 `ID=centos`/`ID=rhel` |
| Ubuntu | `etc/lsb-release` 或 `etc/os-release` 的 `ID=ubuntu` |
| Debian | `etc/debian_version` 或 `etc/os-release` 的 `ID=debian` |

## 系统日志路径

| 发行版系 | 主系统日志 | 内核日志 | 认证日志 |
|----------|------------|----------|----------|
| RHEL/CentOS/麒麟/openEuler | `var/log/messages` | `var/log/kern.log` 或 `sos_commands/kernel/dmesg` | `var/log/secure` |
| Debian/Ubuntu/UOS（部分） | `var/log/syslog` | `var/log/kern.log` | `var/log/auth.log` |

> 麒麟/UOS 实际都源自 RHEL/Debian，路径继承上游。**双系统日志文件都不存在时**才报缺失。

## 内核与启动

| 用途 | 路径 |
|------|------|
| 内核参数 | `proc/sys/`（运行时） + `etc/sysctl.d/`、`etc/sysctl.conf`（持久化） |
| 当前内核 | `sos_commands/kernel/uname -a` |
| 启动参数 | `sos_commands/proc/cmdline` 或 `etc/default/grub` |
| 已加载模块 | `sos_commands/lsmod/lsmod` |
| 内核 panic 配置 | `proc/sys/kernel/panic`、`proc/sys/kernel/panic_on_oops` |

## systemd 与服务

| 用途 | 路径 |
|------|------|
| 失败的 unit | `sos_commands/systemd/systemctl --failed`（若存在） |
| unit 文件 | `etc/systemd/system/`、`usr/lib/systemd/system/` |
| journal 大小 | `etc/systemd/journald.conf` |
| coredump 配置 | `etc/systemd/coredump.conf` |
| 历史 coredump | `var/lib/systemd/coredump/`（按 hostnamectl 命令索引） |
| cgroup v1 | `sys/fs/cgroup/<subsystem>/<slice>/` |
| cgroup v2（unified） | `sys/fs/cgroup/<slice>/`（含 `memory.max`、`cpu.max` 等） |

> 麒麟高级服务器 V10 默认 cgroup v1；V11/openEuler 20+ 逐渐迁移 v2。**先读 `proc/self/cgroup` 确认是 v1 还是 v2**，再决定读 OOM 时去哪查。

## 网络

| 用途 | 路径 |
|------|------|
| 网卡配置 | `etc/sysconfig/network-scripts/ifcfg-*`（RHEL/麒麟）<br>`etc/network/interfaces`（Debian/Ubuntu）<br>`etc/NetworkManager/system-connections/`（NM 管理） |
| iptables | `sos_commands/networking/iptables-save` 或 `nft` |
| conntrack | `proc/sys/net/netfilter/nf_conntrack_max`、`proc/net/nf_conntrack` |
| DNS | `etc/resolv.conf`、`etc/nsswitch.conf` |
| 主机名 | `etc/hostname`、`etc/hosts` |

## 国产化特有

| 用途 | 路径 |
|------|------|
| 麒麟安全模块 | `etc/kylin-security/`、`var/log/kylin-security.log` |
| 鲲鹏 BMC | `sos_commands/ipmitool/`（IPMI 工具输出） |
| 海光 SVM | `proc/cpuinfo` 检查 `svm` flag |
| 飞腾 PSPA | `dmesg` 里搜 `pspa` |
| 麒麟 UKUI 桌面 | `var/log/lightdm/`、`var/log/Xorg.0.log` |
| UOS DDE 桌面 | `var/log/lightdm/`、`var/log/Xorg.0.log`、DDE 日志在 `~/.log/deepin/`（sosreport 不收集用户态日志） |
