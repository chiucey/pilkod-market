# 网络设备安全审计清单

## 账户与访问控制审计

### 用户账户管理

- [ ] 审计所有设备账户，确认无多余账户
- [ ] 验证默认账户（admin/adminroot）已修改或禁用
- [ ] 检查是否存在共享账户
- [ ] 确认服务账户用途明确、最小权限
- [ ] 验证账户密码复杂度策略
- [ ] 检查账户锁定策略配置
- [ ] 确认超时不活动自动登出配置

**检查命令：**

```bash
# 思科 - 用户账户
show running-config | include username
show users

# 华为 - 用户信息
display local-user
display aaa

# 华三 - 账户审计
display user-group
display local-user
```

### 认证授权审计

- [ ] 验证AAA服务器连接状态
- [ ] 检查本地认证 fallback 配置
- [ ] 审计权限级别分配合理性
- [ ] 确认RADIUS/TACACS+密钥一致性
- [ ] 验证特权模式密码与普通密码差异

### 远程访问审计

- [ ] 确认Telnet已禁用，仅允许SSH
- [ ] 检查SSH版本（应使用SSHv2）
- [ ] 验证ACL限制管理IP范围
- [ ] 检查VPN/端口转发配置
- [ ] 确认无后门账户或隐藏配置

---

## 网络服务安全审计

### 协议服务审计

| 服务 | 风险等级 | 检查要点 |
|------|----------|----------|
| Telnet | 高 | 确认已禁用 |
| HTTP | 中 | 建议禁用或限制 |
| CDP/LLDP | 中 | 建议在不可信端口禁用 |
| Finger | 高 | 建议禁用 |
| BootP | 低 | 根据需求评估 |
| Echo | 中 | 建议禁用 |

**检查命令：**

```bash
# 思科 - 服务状态
show running-config | include service
show tcp all status

# 华为 - 服务配置
display info-center
display snmp-agent
display telnet server status
```

### SNMP安全审计

- [ ] 确认SNMPv3已启用（避免SNMPv1/v2c）
- [ ] 检查SNMP社区字符串复杂度
- [ ] 验证SNMP读写权限限制
- [ ] 确认SNMP访问ACL配置
- [ ] 检查SNMP Trap目标地址

```bash
# 思科 - SNMP配置
show snmp group
show snmp user
show snmp community

# 华为 - SNMP审计
display snmp-agent
display snmp-agent mib-view
```

---

## 访问控制列表审计

### ACL规则审查

- [ ] 审计所有ACL规则必要性
- [ ] 确认隐含deny语句生效
- [ ] 检查规则顺序优化
- [ ] 验证ACL应用到正确接口
- [ ] 确认过期ACL已清理
- [ ] 检查日志记录配置

### 安全基线检查

```bash
# 思科 - ACL分析
show access-lists
show ip access-lists
show interface | include access-group

# 华为 - ACL配置
display acl all
display traffic-filter
display traffic-filter interface
```

### 建议的最小安全ACL

```
! 边缘设备入站过滤示例
access-list EXT_IN deny ip host 0.0.0.0 any
access-list EXT_IN deny ip 10.0.0.0 0.255.255.255 any
access-list EXT_IN deny ip 172.16.0.0 0.15.255.255 any
access-list EXT_IN deny ip 192.168.0.0 0.0.255.255 any
access-list EXT_IN deny ip 127.0.0.0 0.255.255.255 any
access-list EXT_IN permit ip any any
```

---

## 网络协议安全审计

### STP安全

- [ ] 确认启用BPDU Guard
- [ ] 检查Root Guard配置
- [ ] 验证PortFast仅用于接入端口
- [ ] 确认环路保护启用

```bash
# 思科 - STP保护
show spanning-tree detail | include Guard
show spanning-tree blockedports
```

### ARP安全

- [ ] 启用动态ARP检测（DAI）
- [ ] 配置ARP速率限制
- [ ] 检查ARP欺骗防护
- [ ] 验证ARP表项学习限制

### DHCP安全

- [ ] 启用DHCP Snooping
- [ ] 配置可信端口
- [ ] 检查DHCP限速设置
- [ ] 验证IP地址分配记录

---

## 日志与审计配置

### 日志配置检查

- [ ] 确认日志记录级别合理（建议Info或Warning）
- [ ] 验证日志同步到Syslog服务器
- [ ] 检查本地日志缓冲大小
- [ ] 确认日志时间戳准确（NTP同步）
- [ ] 验证日志归档策略

```bash
# 思科 - 日志配置
show logging
show logging | include timestamps
show running-config | include ntp

# 华为 - 日志审计
display info-center
display logbuffer
```

### 审计日志保留

- [ ] 确认Syslog服务器可用
- [ ] 验证日志保留周期（建议至少6个月）
- [ ] 检查日志完整性保护
- [ ] 确认日志备份机制

---

## 系统安全基线配置

### 密码策略

```bash
# 思科 - 密码策略
service password-encryption
security passwords min-length 12
enable secret [强密码]
```

### 服务加固

```bash
# 禁用不必要的服务（思科）
no service pad
no service tcp-keepalives-in
no service tcp-keepalives-out
no ip finger
no ip bootp server
no ip http server
no ip http secure-server

# 启用安全特性
service timestamps debug datetime msec
service timestamps log datetime msec
service sequence-numbers
```

### 控制平面保护

- [ ] 配置控制平面限速
- [ ] 启用Control Plane Protection
- [ ] 验证管理流量分类
- [ ] 检查CPPr策略应用

```bash
# 思科 - 控制平面保护
show policy-map control-plane
```

---

## 固件与漏洞管理

### 固件版本审计

- [ ] 记录所有设备当前固件版本
- [ ] 确认使用支持版本（非EOL）
- [ ] 检查安全公告涉及版本
- [ ] 评估升级必要性

### 漏洞扫描

- [ ] 定期执行漏洞扫描
- [ ] 验证已知漏洞修复状态
- [ ] 评估风险等级和修复优先级
- [ ] 建立漏洞修复流程

### 补丁管理策略

| 补丁类型 | 响应时间 | 测试要求 |
|----------|----------|----------|
| Critical | 72小时内 | 必须测试 |
| High | 2周内 | 建议测试 |
| Medium | 1个月内 | 按需测试 |
| Low | 下次维护窗口 | 可选测试 |

---

## 合规性检查

### 等保合规要点

| 检查项 | 要求 | 检查方法 |
|--------|------|----------|
| 身份鉴别 | 三权分立 | 审计账户 |
| 访问控制 | 最小权限 | 审查ACL |
| 安全审计 | 日志留存6月+ | 检查日志 |
| 剩余信息保护 | 配置清除 | 检查配置 |
| 入侵防范 | 异常检测 | 检查IDS |

### 审计报告模板

```markdown
## 安全审计报告

### 审计基本信息
- **审计时间**: YYYY-MM-DD
- **审计范围**: [设备清单]
- **审计人员**: [人员]
- **审计依据**: [合规标准]

### 总体评估
- **合规项数量**: XX
- **不合规项数量**: XX
- **风险等级**: [高/中/低]

### 详细发现

| 编号 | 检查项 | 状态 | 说明 | 建议 |
|------|--------|------|------|------|
| 1 | ... | 通过/不通过 | ... | ... |

### 高风险项
[列出高风险项及修复建议]

### 后续行动计划
| 序号 | 修复项 | 责任人 | 完成时间 |
|------|--------|--------|----------|
| 1 | ... | ... | ... |
```
