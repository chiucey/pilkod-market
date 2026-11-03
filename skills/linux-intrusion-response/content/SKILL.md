---
name: linux-intrusion-response
description: Linux 系统入侵排查与应急响应指南。用于系统被入侵、发现异常进程、可疑网络连接、WebShell、挖矿程序、后门账户等安全事件时的排查与处置。支持两种方式：(1) 本地执行排查脚本和命令，(2) 通过 SSH 远程登录靶机自动执行排查流程。涵盖日志分析、进程检查、网络连接分析、文件完整性检查、账户审计、持久化威胁清除等全流程。
---

# Linux 入侵排查与应急响应 Skill

本 Skill 提供 Linux 系统入侵事件的全流程排查与应急响应能力。

## 模式选择

首先确定排查模式：

**模式 A: 本地排查** - 在当前系统执行排查（用户手动运行命令/脚本）
**模式 B: SSH 远程排查** - AI 自动登录远程服务器执行排查

### SSH 远程排查前置要求

需要提供以下连接信息：
- 目标 IP 地址
- SSH 端口（默认 22）
- 用户名
- 认证方式：密码 或 私钥路径
- 是否需要 sudo 提权

SSH 远程排查支持两种子模式：
- **全自动模式**: 上传脚本并自动执行全套检查
- **交互模式**: 登录后保持会话，逐条执行用户指定命令

---

## 本地排查流程

### 阶段 0: 前置检查

执行排查前确认：
1. 系统是否已断网隔离？（防止数据外传或攻击者清理痕迹）
2. 是否有磁盘快照/备份？（保留证据）
3. 当前用户权限是否足够？（建议 root 或 sudo）

### 阶段 1: 快速健康检查 (P0 - 易失性证据)

运行快速检查脚本获取系统概览：

```bash
sudo bash quick_check.sh
```

此脚本输出包含：
- 系统基本信息（主机名、内核版本、运行时间）
- CPU/内存占用最高的进程
- 当前网络连接概览
- 最近登录用户
- 在线用户列表

**关键检查点**：
- CPU 占用 >90% 的进程 → 可能是挖矿程序
- 非业务端口的外连 → 可能是 C2 通信
- 异常时间的登录记录 → 可能是非法登录

### 阶段 2: 进程深度分析

如果快速检查发现异常进程，运行深度分析：

```bash
sudo bash process_analyzer.sh
```

检查项：
- 所有进程的二进制路径（检查 /tmp、/dev 等可疑目录）
- 进程启动时间（与攻击时间线对比）
- 进程启动用户
- 无文件进程（memfd 等）
- 隐藏的进程（与 ps 输出对比）

**异常指标**：
- 进程二进制位于 /tmp、/dev/shm、/var/tmp
- 进程名伪装成系统进程但路径不对（如 /tmp/systemd）
- 进程启动时间在凌晨且无计划任务
- 进程使用大量 CPU 但无业务关联

### 阶段 3: 网络连接分析

```bash
sudo bash network_inspector.sh
```

检查项：
- 所有 ESTABLISHED 连接及对应进程
- 所有 LISTEN 端口及对应进程
- 外连 IP 的地理位置（自动标记国外 IP）
- 异常端口（非标准业务端口）

**参考可疑端口**：
- 常见矿池端口：3333、4444、5555、6666、7777、8888、9999
- IRC 端口：6666-6669
- 反向 Shell 常用高位端口

如需查询 IP 信息，参考 `references/common_iocs.md`

### 阶段 4: 账户与登录审计

```bash
sudo bash log_analyzer.sh
```

检查项：
- 最近成功登录（last）
- 登录失败记录（lastb）
- SSH 登录日志（/var/log/auth.log 或 /var/log/secure）
- 用户执行过的命令（~/.bash_history）
- sudo 使用记录

**重点关注**：
- 非工作时间的登录
- 陌生 IP 的登录
- 登录后立即执行敏感命令（下载、修改系统文件）
- 新建的特权用户

### 阶段 5: 持久化机制检查

```bash
sudo bash persistence_scanner.sh
```

检查所有持久化位置：
- 系统 crontab（/etc/crontab、/etc/cron.d/*）
- 用户 crontab（crontab -l 每个用户）
- 启动脚本（/etc/rc.local、/etc/init.d/*）
- Systemd 服务（/etc/systemd/system/*.service）
- 环境变量劫持（/etc/profile、/etc/bashrc、~/.bashrc）
- LD_PRELOAD 加载器（/etc/ld.so.preload）
- SSH 后门（~/.ssh/authorized_keys）
- PAM 后门（/etc/pam.d/*）

### 阶段 6: WebShell 扫描

如果服务器运行 Web 服务：

```bash
sudo bash webshell_scanner.sh /var/www/html
```

可指定 Web 根目录作为参数，默认检查常见路径：
- /var/www/html
- /usr/share/nginx/html
- /opt/lampp/htdocs

检测特征：
- 常见 WebShell 文件名（shell.php、cmd.php 等）
- 可疑代码特征（eval、base64_decode、system、exec）
- 最近修改的 PHP/JSP/ASP 文件

### 阶段 7: 文件完整性检查

```bash
sudo bash file_integrity.sh
```

检查项：
- SUID/SGID 文件（检查是否有新增）
- 系统二进制文件修改（/bin、/sbin、/usr/bin）
- 最近 7 天内修改的系统文件
- /tmp、/dev/shm 目录下的可执行文件

### 阶段 8: 时间线构建

如需分析特定时间段的事件：

```bash
sudo bash timeline_builder.sh 3  # 分析最近 3 天的文件变更
```

输出：
- 按时间排序的文件修改列表
- 新增的可执行文件
- 修改的配置文件

---

## SSH 远程排查流程

### 全自动模式

执行远程全套检查：

```bash
python3 remote_ir.py --host 192.168.1.100 --user root --password "xxx" --port 22
```

或使用密钥：

```bash
python3 remote_ir.py --host 192.168.1.100 --user root --key ~/.ssh/id_rsa
```

执行流程：
1. 建立 SSH 连接
2. 在远程创建 /tmp/ir-scripts/ 目录
3. 上传所有排查脚本
4. 依次执行 quick_check → process_analyzer → network_inspector → log_analyzer → persistence_scanner
5. 收集所有输出到本地报告
6. 清理远程临时文件

### 交互模式

如需手动控制排查过程：

```bash
python3 ssh_executor.py --host 192.168.1.100 --user root --interactive
```

然后可以逐条执行命令，AI 会实时返回并解读结果。

### 批量扫描

对多台主机执行相同检查：

```bash
python3 batch_scan.py --hostfile hosts.txt --output report.json
```

hosts.txt 格式：
```
192.168.1.10:22:root:password123
192.168.1.11:22:root:/path/to/key
```

---

## 结果分析与决策

### 确认入侵的指标

满足以下任一条件，可高度确认系统已被入侵：
- 发现已知的恶意进程（挖矿、木马）
- 发现 WebShell 文件
- 发现未授权的后门账户
- 发现异常的外连 C2 通信
- 系统二进制文件被篡改

### 应急响应决策树

**系统已失控（攻击者正在活跃）**:
1. 立即断网隔离
2. 内存取证（如果条件允许）
3. 磁盘镜像备份
4. 重装系统（不要直接清理后继续使用）

**系统可控（攻击者已离开）**:
1. 保存所有证据
2. 清理恶意文件和账户
3. 修复漏洞（更新补丁、修改密码、加固配置）
4. 重新上线并持续监控

---

## 参考文档

详细技术参考见 `references/` 目录：

- `common_iocs.md` - 常见 IOC 指标（可疑 IP、域名、文件路径）
- `log_formats.md` - 日志格式说明与关键字段解析
- `attack_patterns.md` - 常见攻击手法特征
- `response_playbooks.md` - 分场景响应流程
- `tools_reference.md` - 常用工具速查手册

---

## 使用示例

**场景1 - 本地快速检查:**
```
User: "帮我检查这台服务器有没有被入侵"
→ 执行 quick_check.sh，根据结果决定深度检查方向
```

**场景2 - 排查挖矿病毒:**
```
User: "CPU 占用 100%，可能是挖矿"
→ 执行 process_analyzer.sh + network_inspector.sh，检查矿池连接
```

**场景3 - SSH 远程自动排查:**
```
User: "远程排查 192.168.1.100，root/xxx"
→ 执行 remote_ir.py 自动全套检查
```

**场景4 - 批量扫描:**
```
User: "批量检查这 10 台服务器"
→ 执行 batch_scan.py 并发检查
```
