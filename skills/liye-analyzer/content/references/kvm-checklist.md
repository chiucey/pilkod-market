# KVM 排障检查清单

> 先用 `systemd-detect-virt` 确认角色：
> - 输出 `kvm` → 当前是虚机
> - 命令不存在或输出 `none` → 裸机
> - 需读 `sos_commands/systemd/systemd-detect-virt` 进一步判断

## 一、宿主机角色（Host）的排障

### 1. libvirt 状态
- `sos_commands/libvirt/virsh_list_all` → 虚机列表
- `sos_commands/libvirt/virsh_net_list_all` → 虚拟网络
- `var/log/libvirt/` 下的日志（`qemu/<vm-name>.log`、`libvirtd.log`）

### 2. qemu-kvm 进程
- `sos_commands/process/ps_auxww` 或 `ps auxww`（grep `qemu-kvm`）→ 资源占用
- **qemu core dump**：`var/lib/libvirt/qemu/dump/<vm-name>-*.elf` 或 `*.core`
- **qemu monitor**：`sos_commands/libvirt/virsh_qemu_monitor_command`（如果存在）

### 3. 资源与隔离
- **cgroup 限制**：`sys/fs/cgroup/.../machine.slice/` → libvirt 管理的虚机是否被 cgroup 限制
- **NUMA binding**：`virsh dumpxml <vm>` 看 `<numatune>` 配置
- **大页（HugePage）**：
  - `proc/sys/vm/nr_hugepages` → 系统预留大页数
  - `proc/meminfo` 的 `HugePages_Total` / `HugePages_Free`
  - 大页不足 → qemu 启动失败或 OOM

### 4. 设备直通（VFIO / vhost）
- **VFIO**：`sys/kernel/iommu_groups/`、`sys/bus/pci/devices/*/driver_override`
- **vhost-net**：`sys/module/vhost_net/parameters/` 
- **vhost-user**（如 DPDK）：socket 文件在 `/var/run/openvswitch/` 或自定义路径

### 5. 存储后端
- **镜像路径**：`/var/lib/libvirt/images/` 或自定义
- **存储池**：`virsh pool-list`（sos 不一定采集到）
- **qcow2 / raw** 性能差异：sosreport 通常不直接采集，需让用户提供 `qemu-img info` 输出

### 6. 桥接网络
- `sos_commands/networking/ip_link` → 看 `virbr0`、bridge、bond、vlan
- **MTU 不一致**：桥接 1500 vs 物理网卡 9000 → 性能下降
- **桥接泛洪**：bridge nf_call_iptables 是否启用

### 7. 宿主机 OOM 影响
- 宿主机 OOM → qemu 进程被杀 → 虚机异常掉电
- 检查：`sos_commands/kernel/dmesg` 搜 `oom` + `qemu`

---

## 二、虚机角色（Guest）的排障

### 1. 虚机内部视角
- 虚机内部的 sosreport 用同样 procedure 分析（系统层）
- 重点关注：**虚机看到的"硬件"是 virtio 模拟的**，硬件错误可能是 host 透传问题

### 2. virtio 驱动
- `lspci` 或 `lshw` → 看 `Virtio` 设备是否都识别
- `dmesg | grep virtio` → 驱动加载是否成功
- 常见：`virtio_net` / `virtio_blk` / `virtio_scsi` / `virtio_gpu`

### 3. 时间同步
- **kvm-clock**：`dmesg | grep -i kvm-clock`
- **chrony / ntpd 配置**：`etc/chrony.conf` 或 `etc/ntp.conf`
- 虚机时间漂移 → 业务日志时间戳错乱，**跨主机关联时极易误判**

### 4. balloon 内存
- `sos_commands/qemu_guest_agent/` 或 `virsh dommemstat <vm>` → balloon 状态
- balloon 回收后 OOM → 检查 `vm.swappiness`、应用内存使用

### 5. 巨页透传
- `/proc/meminfo` 的 `AnonHugePages` vs `HugePages_Total`
- 数据库类应用（Oracle、Redis、MongoDB）必须配大页

---

## 三、跨角色关联

当虚机故障时，**必须同时看宿主和虚机两边**：

1. 时间对齐：所有事件用相对时间（"采集时刻 -N 分钟"）
2. 虚机内部 OOM 时，先看宿主是否有同时刻 cgroup 限制
3. 虚机网卡丢包时，**先看宿主** `vhost_net` 日志、桥接丢包统计
4. 虚机磁盘慢时，**先看宿主**镜像所在物理盘的 `iostat`

## 四、典型故障模式

| 现象 | 优先排查 |
|------|----------|
| 虚机启动失败 | 大页不足、镜像损坏、NUMA 配置、CPU model 不支持 |
| 虚机卡顿但 CPU 显示正常 | 宿主 cgroup 限制、IO 透传问题、NUMA 跨节点 |
| 虚机网络慢/丢包 | vhost-net 异常、桥接 MTU、宿主网络栈压力 |
| 虚机磁盘 I/O 慢 | 镜像所在物理盘压力、qcow2 碎片、virtio-blk vs virtio-scsi |
| 虚机时间漂移 | kvm-clock 未启用、chrony/ntpd 异常 |
| 虚机掉电 | 宿主 OOM 杀进程、宿主内核 panic、libvirtd 崩溃 |
| 虚机内部随机 reboot | 宿主 BUG、qemu monitor 异常、CPU 热添加问题 |
