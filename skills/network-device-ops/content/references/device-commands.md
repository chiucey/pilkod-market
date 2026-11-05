# 主流网络设备厂商命令速查表

## 思科 IOS 命令

### 系统信息

```bash
# 查看设备基本信息
show version
show inventory
show license

# 查看CPU和内存使用
show processes cpu
show memory

# 查看系统时钟
show clock
```

### 接口管理

```bash
# 查看所有接口状态
show ip interface brief
show interfaces status

# 查看特定接口详情
show interfaces GigabitEthernet0/0

# 查看接口统计信息
show interfaces counters
show interfaces trunk

# 重置接口统计
clear counters
```

### 路由协议

```bash
# 查看路由表
show ip route
show ip route static
show ip route ospf
show ip route bgp

# OSPF配置查看
show ip ospf neighbor
show ip ospf database
show ip ospf interface

# BGP配置查看
show ip bgp summary
show ip bgp neighbors
show ip bgp routes
```

### VLAN与交换

```bash
# 查看VLAN信息
show vlan
show vlan brief

# 生成树协议
show spanning-tree
show spanning-tree summary

# 端口通道
show etherchannel summary
show port-channel
```

### 安全功能

```bash
# 查看访问控制列表
show access-lists
show ip access-lists

# 查看端口安全
show port-security address
show port-security interface

# 查看SSH/Telnet状态
show ssh
show line
```

---

## 华为 VRP 命令

### 系统信息

```bash
# 查看设备信息
display version
display device
display esn

# 查看CPU和内存
display cpu-usage
display memory-usage

# 查看运行时间
display startup
```

### 接口管理

```bash
# 查看接口概要
display ip interface brief
display interface brief

# 查看接口详情
display interface GigabitEthernet0/0/0

# 查看接口统计
display interface statistics

# 查看光模块信息
display transceiver
```

### 路由协议

```bash
# 查看路由表
display ip routing-table
display ip routing-table protocol static
display ip routing-table protocol ospf
display ip routing-table protocol bgp

# OSPF配置
display ospf peer
display ospf lsdb
display ospf interface

# ISIS配置
display isis peer
display isis route
```

### VLAN与交换

```bash
# 查看VLAN
display vlan
display vlan summary

# 查看MAC地址表
display mac-address

# 查看STP状态
display stp
display stp region-configuration

# 查看链路聚合
display eth-trunk
```

### 安全配置

```bash
# 查看ACL
display acl all
display traffic-filter

# 查看攻击防范
display auto-defend configuration
display arp anti-attack
```

---

## 华三 Comware 命令

### 系统信息

```bash
# 查看版本信息
display version
display device-manufacture-info

# 查看系统资源
display cpu-usage
display memory
```

### 接口配置

```bash
# 查看接口状态
display interface brief
display ip interface brief

# 查看接口详细信息
display interface GigabitEthernet1/0/1

# 查看端口隔离
display port-isolate group
```

### 路由配置

```bash
# 查看路由表
display ip routing-table
display bgp peer
display ospf peer

# 查看策略路由
display policy-based-route
```

### 交换功能

```bash
# 查看VLAN
display vlan all

# 查看MAC地址
display mac-address all

# 查看STP
display stp
```

---

## Juniper JunOS 命令

### 系统操作

```bash
# 查看版本和硬件信息
show version
show chassis hardware
show system uptime

# 查看资源使用
show system processes extensive
show system memory
```

### 接口配置

```bash
# 查看接口状态
show interfaces terse
show interfaces

# 查看接口统计
show interfaces statistics

# 查看IP别名
show interfaces terse | match inet
```

### 路由协议

```bash
# 查看路由表
show route
show route protocol static
show route protocol ospf
show route protocol bgp

# OSPF邻接关系
show ospf neighbor
show ospf interface

# BGP配置
show bgp summary
show bgp neighbor
```

### 安全策略

```bash
# 查看安全策略
show security policies
show security zones

# 查看NAT规则
show security nat source
show security nat destination
```

### 交换功能

```bash
# 查看VLAN
show vlans

# 查看MAC地址表
show ethernet-switching table

# 查看生成树
show spanning-tree
```

---

## 命令对照速查表

| 操作类型 | 思科 IOS | 华为 VRP | 华三 Comware | Juniper JunOS |
|----------|----------|----------|--------------|---------------|
| 进入特权模式 | `enable` | `system-view` | `system-view` | `cli` |
| 进入配置模式 | `configure terminal` | `system-view` | `system-view` | `configure` |
| 保存配置 | `write memory` | `save` | `save` | `commit` |
| 查看当前配置 | `show running-config` | `display current-configuration` | `display current-configuration` | `show configuration` |
| 查看启动配置 | `show startup-config` | `display saved-configuration` | `display saved-configuration` | `show configuration` |
| 重启设备 | `reload` | `reboot` | `reboot` | `request system reboot` |
| 查看接口IP | `show ip interface brief` | `display ip interface brief` | `display ip interface brief` | `show interfaces terse` |
| 配置IP地址 | `interface` + `ip address` | `interface` + `ip address` | `interface` + `ip address` | `set interfaces` |
| 查看路由表 | `show ip route` | `display ip routing-table` | `display ip routing-table` | `show route` |
| 查看邻居 | `show cdp neighbors` | `display lldp neighbor` | `display lldp neighbor` | `show lldp neighbors` |
| 查看ACL | `show access-lists` | `display acl all` | `display acl all` | `show firewall` |
| 清空统计 | `clear counters` | `reset counters interface` | `reset counters interface` | `clear interfaces statistics` |
