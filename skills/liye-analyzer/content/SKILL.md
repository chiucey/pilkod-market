---
name: liye-analyzer
description: |
  Linux 系统层深度排障分析，专精 sosreport 诊断、宕机/重启/OOM 根因定位、性能瓶颈分析。
  覆盖国产化生态：麒麟（高级服务器 / 桌面）、统信 UOS、openEuler、CentOS、RHEL、Ubuntu；
  国产芯片：鲲鹏（ARM）、海光（x86）、飞腾（ARM）、龙芯；
  虚拟化：KVM 宿主机 / 虚机；
  应用层 system-side：Java/Python/Go 进程 OOM、fd 耗尽、cgroup 限制、网络栈、core dump 解析。

  Use this skill when the user provides a sosreport (or extracted directory) and asks to
  "分析", "排查", "定位", "生成运维报告", or reports symptoms like
  "服务器宕机", "频繁重启", "性能慢", "进程消失", "服务起不来", "桌面卡死",
  "Java 跑一天就挂", "VM 无法启动", "磁盘写满", "CPU 跑满".

  Do NOT use for: 纯业务代码 bug（logic error、单元测试失败）、纯数据库 SQL 调优、
  前端 / 浏览器问题、软件安装 / 服务配置的"怎么做"型操作手册、纯安全合规审计.
---

# liye-analyzer

## Inputs to collect

- **sosreport 路径**：可以是 `.tar.xz` / `.tar.gz` 压缩包，或已解压的目录（默认约定：`sosreport-*/` 或用户给定的目录）。
- **可选：用户主诉症状**（性能？宕机？某个服务？某个时间段？）。未提供时全量分析。
- **可选：环境上下文**（生产/测试、物理机/虚机、业务重要性）。未提供时按生产重要性默认。

如果用户只给了命令输出片段（不是 sosreport），先按症状定位，再用命令补查 —— 不要硬等完整 sosreport。

## Procedure

按以下顺序执行；每步都用 `Read` / `Grep` 工具读 sosreport 内对应文件，不靠记忆。

### 0. 准备：解压与目录定位

- 如果是压缩包：`tar -xJf <file>` 或 `tar -xzf <file>` 到 `/workspace/analysis/` 下
- 摸清 sosreport 根目录（通常含 `sos_commands/`、`var/log/`、`etc/`、`sos_reports/`、`sos.json`）
- 阅读 `sos.json` 的 `version` 和执行的 `cmdline`，确认 sosreport 完整性
- 跨主机时间一致性：读 `sos_commands/date/date` 确认采集时主机时间

### 1. 摸底（Host & Environment）

按顺序读以下文件（不存在的跳过，不阻断）：

| 信息 | 路径（在 sosreport 内） |
|------|------------------------|
| 主机名 | `sos_commands/host/hostname` |
| 内核 / 架构 | `sos_commands/kernel/uname`, `sos_commands/processor/lscpu` |
| 发行版 | `etc/os-release`, `etc/kylin-release`, `etc/lsb-release` |
| 虚拟化角色 | 读 `sos_commands/systemd/systemd-detect-virt` 输出（裸机/kvm/vmware/container） |
| 启动时间 / uptime | `sos_commands/host/uptime`, `sos_commands/proc/uptime` |
| 国产芯片识别 | `/proc/cpuinfo` 的 `model name` 和 `CPU implementer` / `CPU part` |

> 详见 `references/distro-paths.md` 和 `references/chip-checklist.md`。

### 2. 资源使用分析

按维度并行读（不阻塞）：

- **CPU**：`sos_commands/processor/lscpu`, `sos_commands/processor/mpstat`, `sos_commands/host/nproc`, `sos_commands/loadavg`
  - 关注：load average vs nproc，softirq 占比，I/O wait 占比
- **内存**：`sos_commands/memory/free`, `proc/meminfo`, `sos_commands/vmstat/vmstat`
  - 关注：Available vs Used、Swap 使用、Slab、PageTables、HugePages
- **磁盘**：`sos_commands/storage/df`, `sos_commands/storage/lsblk`, `sos_commands/storage/iostat`, `sos_commands/storage/dumpe2fs`
  - 关注：inode 使用率、await、util%、Read/Write 错误计数
- **网络**：`sos_commands/networking/ss_-s`, `sos_commands/networking/netstat_-s`, `sos_commands/networking/ip_-s_-s`
  - 关注：TCP 重传、丢包、socket 状态、conntrack 表使用

sar 系列（`sos_commands/sar/`）如果存在，优先用 —— 含历史趋势。

### 3. 异常事件时间线

按时间顺序聚合以下来源（用 Grep 配合时间戳正则）：

- **重启记录**：`sos_commands/general/last` 里的 `reboot` / `shutdown` / `crash`
- **dmesg / 内核日志**：`sos_commands/kernel/dmesg` 或 `var/log/kern.log`
- **系统日志**：`var/log/messages`（RHEL/CentOS/麒麟系）或 `var/log/syslog`（Debian/Ubuntu）
- **审计 / 登录**：`var/log/secure`, `var/log/auth.log`, `sos_commands/auditd/ausearch_-m`
- **coredump**：`sos_commands/systemd/coredumpctl_list` 或 `var/lib/systemd/coredump/`
- **服务失败**：`sos_commands/systemd/systemctl_--failed` 或 `journalctl -p err` 片段

**重点模式识别**（用 Grep 关键词）：

| 模式 | 含义 | 优先级 |
|------|------|--------|
| `Out of memory: Killed process` | 系统 OOM killer 触发 | P0 |
| `invoked oom-killer` + `cgroup` | cgroup 限制触发的 OOM（应用层） | P1 |
| `Kernel panic - not syncing` | 内核 panic | P0 |
| `Oops:.*Call Trace` | 内核 bug / 驱动错误 | P0 |
| `mce:.*Hardware error` | Machine Check Exception（CPU/内存硬件错） | P0 |
| `I/O error.*dev` | 磁盘 / 控制器 I/O 错误 | P0 |
| `segfault.*ip` | 进程段错误 | P1 |
| `TCP: out of memory` | 网络栈内存不足 | P1 |
| `connection reset by peer` 突发 | 网络抖动 / 服务异常退出 | P2 |
| `Failed to start` + unit 名 | systemd 服务启动失败 | P1 |

> 把每条事件按时间戳排序，输出成时间线。跨主机时把 UTC/本地时区标注清楚。

### 4. 分层根因定位

按以下优先级逐层排查，**每一层都给出"是否触发"的明确结论**：

1. **硬件层** — MCE、I/O error、ECC 内存错误、CPU 过热（`sos_commands/hardware/sensors`）、电源（IPMI/BMC 事件）
2. **内核层** — kernel panic、驱动 bug、cgroup v1/v2 配置、`/proc/sys/` 关键参数
3. **虚拟化层**（KVM 宿主） — qemu-kvm crash、libvirt 错误、VFIO 直通、vhost-net 异常 —— 详见 `references/kvm-checklist.md`
4. **系统服务层** — systemd unit 失败、关键服务 OOM、依赖循环
5. **用户态 / 桌面层** — display manager、GPU 驱动、音频、Wayland 协议 —— 详见 `references/desktop-checklist.md`
6. **应用层 system-side** — 应用崩溃的**系统层**根因：
   - Java：检查 `/var/log/java*.log`、`-XX:+HeapDumpOnOutOfMemoryError` 输出、cgroup 内存限制（`/sys/fs/cgroup/memory/<slice>/memory.limit_in_bytes` 或 v2 的 `memory.max`）
   - Python/Go：core dump（`coredumpctl list` + `coredumpctl dump`）、`/proc/PID/status` 的 VmRSS/VmPeak、fd 数量（`/proc/PID/fd | wc -l` vs `ulimit -n`）
   - 通用：`prlimit` 进程资源限制、cgroup CPU share、cgroup blkio 限制

### 5. 国产芯片特殊检查（如适用）

按 `references/chip-checklist.md` 走；先识别芯片再走对应 checklist：
- **鲲鹏**（`CPU implementer: 0x48`） — NUMA 拓扑、HPKI 性能计数器、BMC IPMI 事件、鲲鹏使能的内核选项
- **海光**（`CPU vendor_id: HygonGenuine`） — SVM 状态、CPUID 0x80000001、安全加密引擎
- **飞腾**（`CPU implementer: 0x70`） — PSPA 安全架构、大页配置、主板固件日志
- **龙芯**（`CPU implementer: 0x14` 或 `Loongson`） — loongarch 架构、PMON 固件日志

### 6. KVM 特殊检查（如果是宿主机/虚机）

读 `references/kvm-checklist.md`，按"宿主机角色"或"虚机角色"分支处理：
- 宿主机：libvirt 日志、qemu 进程 coredump、vcpu/内存配置、NUMA binding、大页
- 虚机：内部 sosreport 与宿主机时间线对齐、virtio 驱动、巨页、I/O 透传

### 7. 风险评级

每条发现必须挂等级：

- **P0（紧急）**：数据丢失风险、服务不可用、硬件故障 —— 24 小时内处理
- **P1（高）**：性能严重下降、频繁故障、潜在 OOM —— 1 周内处理
- **P2（中）**：潜在风险、配置不合理 —— 1 个月内处理
- **P3（低）**：优化建议、最佳实践 —— 下个版本迭代

### 8. 输出

按 `references/output-template.md` 章节结构，先写 **`findings.md`**（结构化中间产物，方便复用），再用 `minimax-docx` skill 生成正式 **`report.docx`**。

## Output contract

**中间产物**：`findings.md`，结构化（YAML frontmatter + 章节），含每条发现的：
- `level`: P0/P1/P2/P3
- `category`: hardware/kernel/virtualization/service/desktop/app-system
- `evidence`: 文件路径 + 关键行 + 行号
- `root_cause`: 一句话根因
- `fix`: 可执行命令或配置

**最终产物**：`report.docx`，章节固定（详见 `references/output-template.md`）：
1. 报告概览（系统信息 + 严重程度 + 时间范围）
2. 系统信息（主机/内核/架构/虚拟化角色/芯片）
3. 资源使用分析（CPU/内存/磁盘/网络，含趋势）
4. 异常事件时间线（按时间倒序）
5. 根因结论与风险等级（按 P0→P3 排序）
6. 优化建议与解决方案（按优先级）
7. 附录（关键命令清单 / 相关日志片段 / 引用文件路径）

**报告必须含**：证据链（每个结论都引用 sosreport 具体文件路径）、可执行方案（不只是说"建议优化")、麒麟/国产化特有的注意事项（如涉及）。

## Failure handling

- **sosreport 解压失败** → 报用户并请重传；不要强行读部分文件
- **关键目录缺失**（如 `var/log/messages` 为空）→ 在 `findings.md` 标注"该维度数据缺失"，继续分析其他维度
- **跨主机时间不一致** → 全部改用相对时间（"采集时刻 -N 分钟"）标注，避免误导
- **信息不足以给根因** → 明确说"无法定位到唯一根因"，列出剩余假设和仍需采集的数据（如 `perf record`、`strace`、完整 `journalctl`）
- **应用层崩溃但无 core dump** → 建议用户开启 `kernel.core_pattern` 和 systemd-coredump，下次复现后再分析；本次给排查方向
- **误报 OOM** → 区分"系统 OOM"和"cgroup OOM"（前者全局内存耗尽，后者 cgroup 局部限制），解决方案不同

## Examples

**Example 1：sosreport + 宕机主诉**
- Input: 用户上传 `sosreport-host01-20260803.tar.xz`，说"昨晚 3 点服务器重启了，帮我看看"
- 流程：解压 → 摸底（识别为鲲鹏 920 + 麒麟高级服务器 V10）→ 资源分析（内存 Available 接近 0）→ 异常时间线（03:12 出现 OOM killed java）→ 根因：cgroup 内存限制 4G 触发的应用层 OOM（不是系统 OOM）→ P1 风险
- Output: `findings.md` + `report.docx`，含 cgroup 限制调大、Java 堆参数调优、监控告警补充等可执行方案

**Example 2：Java 应用跑一天就挂，无完整 sosreport**
- Input: "我们的 Java 服务每天凌晨挂掉，重启就好，已知 JDK 11"
- 流程：无 sosreport → 让用户提供 `coredumpctl list` 输出 + `/var/log/messages` 中 java 相关段 + 应用启动参数；如已提供直接分析 → 重点查 GC 日志、cgroup 限制、`-Xmx` 与 cgroup 关系 → 根因：cgroup 4G vs `-Xmx` 6G 不匹配，物理内存未耗尽但 cgroup 触发 OOM
- Output: 报告含调优方案（`-Xmx` ≤ cgroup limit * 0.75）+ cgroup 配置建议 + 监控指标
