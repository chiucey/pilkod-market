# 国产芯片检查清单

> 先识别芯片再走 checklist。识别方式：`/proc/cpuinfo` + `lscpu` 联合判断。

## 芯片识别速查

| 芯片 | 架构 | 关键识别特征 | 关键 flag |
|------|------|--------------|-----------|
| 鲲鹏 920/970 | aarch64 | `CPU implementer: 0x48`，`model name: HiSilicon...Kunpeng...` 或 `PHYTIUM` 之外的 ARM | `asimd`, `crc32`, `lse` |
| 海光 7000/5000 | x86_64 | `vendor_id: HygonGenuine`，`cpu family: 25`（Zen 衍生） | `svm`, `avx2` |
| 飞腾 2000+/S2500 | aarch64 | `CPU implementer: 0x70`，`model name: Phytium...` | `asimd`, `evtstrm` |
| 龙芯 3A5000/3A6000 | loongarch64 | `Architecture: loongarch64`，`vendor_id: Loongson` | `lsx`, `lasx` |
| 海光（部分旧版） | x86_64 | `vendor_id: AuthenticAMD` 但 `cpu family: 24`（Zen 之前），需结合 DMI 确认 | `svm` |

> 海光部分早期型号 CPUID 伪装成 AMD，需要看 DMI：`sos_commands/dmidecode/dmidecode -t 2` 或 `sos_commands/dmidecode/dmidecode -t processor`。

---

## 鲲鹏 ARM（Kunpeng）

### 性能与 NUMA
- **NUMA 拓扑**：`lscpu | grep NUMA` → 节点数；正常 920 是 2-4 节点，970 最多 8 节点
- **跨节点访问**：sar 看到的 `%sys` 高 + `numastat` 显示跨节点访问 > 30% → 亲和性配置问题
- **HPKI 性能分析**：`perf stat -e hpki/*` 或鲲鹏专属 PMU 事件，需 `perf` 工具链支持

### 内存与透明大页
- 鲲鹏默认 THP 配置：`/sys/kernel/mm/transparent_hugepage/enabled` → `madvise` 比 `always` 更安全
- 内存预留：检查 `/sys/devices/system/cpu/cpu*/cpufreq/` 是否有策略限制导致 freq 拉不上去

### 散热与电源
- **BMC 事件**：`sos_commands/ipmitool/ipmitool sel list`（IPMI SEL 系统事件日志）
- **CPU 温度**：`sos_commands/hardware/sensors` 或 `sos_commands/lmsensors/sensors`
- 散热异常 → CPU 降频 → 性能下降但 load 不高

### 内核选项
- `CONFIG_ARM64_16K_PAGES`：部分场景 16K 页性能更好，但与某些数据库冲突
- 鲲鹏使能的内核配置：`config-$(uname -r)` 文件（在 `/boot/` 或 `/usr/src/`）

### 常见坑
- 跨 NUMA 性能损失严重
- 巨页 + 鲲鹏组合性能更优
- 第三方二进制（如旧版 Java）需 ARM 原生版本

---

## 海光 x86（Hygon）

### CPUID 与虚拟化
- **SVM（Secure Virtual Machine）状态**：`grep -E '^flags' /proc/cpuinfo | head -1 | tr ' ' '\n' | grep svm` → 必须存在才能跑 KVM
- **CPUID 0x80000001**：ECX 包含 `HygonGenuine` 标识
- **嵌套虚拟化**：`/sys/module/kvm_amd/parameters/nested` → 设为 1 才能跑 KVM-in-KVM

### 性能
- 与 AMD Zen 类似：`perf stat -e amd_l3/...` 事件
- **IBRS/IBPB 缓解**：`/sys/devices/system/cpu/vulnerabilities/` 检查 Spectre/Meltdown 状态
- **SMT 调度**：检查 `thread_siblings_list` 是否合理

### 安全加密
- **国密算法支持**：`/proc/cpuinfo` 检查 `sm3` / `sm4` flag
- **加密引擎**：`lsmod | grep hygon` 是否有 `hygon_crypto` 等模块加载

### 常见坑
- 旧内核对海光 CPUID 识别不全 → 升级内核
- 海光与某些 AMD 专属工具不兼容 → 用海光专用工具

---

## 飞腾 ARM（Phytium）

### PSPA 安全架构
- **PSPA 状态**：`dmesg | grep -i pspa` → 应有 `PSPA: ... initialized`
- 关闭 PSPA：`pspadev=disable` 内核参数（不推荐，影响安全特性）
- PSPA 异常会触发内核错误

### 大页配置
- 飞腾对 2M/1G 大页支持有差异：`/sys/kernel/mm/hugepages/` 检查可用大页
- 数据库场景务必配 HugePage

### 主板固件
- **固件日志**：可能不在传统 IPMI 位置，看 `var/log/messages` 中 `PSCI`、`SCMI` 关键词
- **DMI 信息**：`dmidecode -t bios` 看固件版本

### 常见坑
- PSPA 异常导致随机进程被 kill
- 飞腾部分型号 NUMA 配置异常（单节点也显示为多节点）
- 兼容性矩阵必须查官方手册

---

## 龙芯 LoongArch

### 架构
- **指令集扩展**：`lsx`（128-bit SIMD）、`lasx`（256-bit SIMD）
- **二进制翻译**：`/proc/sys/abi/` 下 `lsx`/`lasx` 控制允许状态

### 性能监控
- 龙芯 PMU 与 x86 完全不同：`perf list` 看到的 `loongarch_*` 事件
- **HT 拓扑**：`lscpu` 的 Thread 字段

### 固件
- **PMON 固件日志**：不在 `/var/log/`，需在固件串口或专用工具读
- 启动问题：参考 PMON 手册而非 GRUB

### 常见坑
- 生态工具链相对落后，第三方二进制不兼容
- 性能监控工具需要专门适配
