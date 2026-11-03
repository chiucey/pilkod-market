---
name: serial-monitor
description: "Monitor serial output from BK7252N / RT-Thread devices: picocom, log capture, finsh shell."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [embedded, serial, uart, monitor, log, finsh, debug]
    related_skills: [bk7252n-flash, rtthread-debug, bk7252n-rtthread-kb]
---

# 串口监控与日志

## Overview

监控 BK7252N 芯片的 UART 串口输出，包括 RT-Thread 启动日志、finsh shell 交互、运行日志捕获与保存。

## 工具选择

| 工具 | 优点 | 适用场景 |
|------|------|----------|
| `picocom` | 轻量、可靠、纯命令行 | 日常调试首选 |
| `minicom` | 功能丰富、有菜单 | 需要配置保存的场景 |
| `screen` | 可后台 detach | 长时间运行/远程 |
| `tio` | 现代化、自动重连 | 需要自动重连 |

---

## Step 1: 安装工具

```bash
sudo apt install -y picocom minicom screen
# 可选 tio
sudo snap install tio
```

## Step 2: 连接串口

### picocom（推荐）

```bash
picocom -b 115200 /dev/ttyUSB0
```

退出：`Ctrl+A` 然后 `Ctrl+X`

常用选项：

```bash
picocom -b 115200 /dev/ttyUSB0 --omap crcrlf   # CR→CR+LF 转换
picocom -b 115200 /dev/ttyUSB0 --flow none       # 禁用流控
picocom -b 115200 /dev/ttyUSB0 -l                # 无锁模式（允许多实例）
picocom -b 115200 /dev/ttyUSB0 --logfile serial.log  # 记录到文件
```

### minicom

```bash
# 首次配置
sudo minicom -s
# 设置 Serial port setup → /dev/ttyUSB0, 115200 8N1, 无流控
# 保存为 dfl

# 直接连接
minicom -D /dev/ttyUSB0 -b 115200
```

退出：`Ctrl+A` 然后 `X`

### screen

```bash
screen /dev/ttyUSB0 115200
```

退出：`Ctrl+A` 然后 `K` 然后 `Y`

---

## Step 3: 捕获日志

### 实时保存到文件

```bash
# picocom 自带日志
picocom -b 115200 /dev/ttyUSB0 --logfile "$(date +%Y%m%d_%H%M%S).log"

# 或用 tee 管道
picocom -b 115200 /dev/ttyUSB0 2>&1 | tee serial.log
```

### 使用 cat 读取原始数据

```bash
# 只读取不交互（适合快速抓取启动日志）
stty -F /dev/ttyUSB0 115200 raw -echo
cat /dev/ttyUSB0 > boot_log.txt &
# 复位芯片产生输出...
kill %1
```

---

## Step 4: finsh Shell 交互

RT-Thread 内置 finsh shell，通过串口交互：

```
msh >
```

### 常用 finsh 命令

```
help              # 列出所有命令
ps                # 查看线程列表
list_thread       # 同上
list_timer        # 查看定时器
list_device       # 查看设备列表
list_sem          # 查看信号量
list_mutex        # 查看互斥锁
list_event        # 查看事件
list_mailbox      # 查看邮箱
list_msgqueue     # 查看消息队列
free              # 查看内存使用
memcheck          # 内存泄漏检查
version           # RT-Thread 版本
date              # 系统时间

# 网络相关（Wi-Fi 开启后）
wifi scan         # 扫描 Wi-Fi
wifi join <ssid> <password>   # 连接 Wi-Fi
ifconfig          # 查看 IP
ping <host>       # ping 测试
```

### 启用/禁用 finsh

在 `rtconfig.h` 或 `menuconfig` 中：

```
RT-Thread Kernel → Kernel Device Object → Using finsh
```

---

## Step 5: RT-Thread 日志风格

### 默认启动日志

```
 \ | /
- RT -     Thread Operating System
 / | \     5.1.0 build May  1 2026 15:30:00
 2006 - 2024 Copyright by RT-Thread team
msh >
```

### 组件初始化日志

```
[I/sal.skt] Socket Abstraction Layer initialize success.
[I/at.clnt] AT client(V1.3.1) on device uart2 initialize success.
[I/wlan] WLAN driver initialized
[D/main] Application started
```

日志级别标记：
- `[A/xxx]` — Assert
- `[E/xxx]` — Error
- `[W/xxx]` — Warning  
- `[I/xxx]` — Info
- `[D/xxx]` — Debug

---

## 远程串口（开发板不在本地）

### 通过 ser2net 共享串口

```bash
# 在连接开发板的机器上
sudo apt install ser2net
echo "2000:raw:600:/dev/ttyUSB0:115200 8DATABITS NONE 1STOPBIT" | sudo tee -a /etc/ser2net.yaml
sudo systemctl restart ser2net

# 在远程机器上
telnet <host> 2000
```

---

## 一键监控脚本

```bash
#!/bin/bash
# monitor.sh — 自动查找串口并连接
PORT=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -1)
if [ -z "$PORT" ]; then
    echo "No serial device found!"
    exit 1
fi
echo "Connecting to $PORT at 115200..."
echo "Press Ctrl+A then Ctrl+X to exit"
sleep 1
picocom -b 115200 "$PORT" --logfile serial_$(date +%Y%m%d_%H%M%S).log
```

## Pitfalls

1. **端口忙：** `Device or resource busy` — 检查是否有其他终端占用了串口（`lsof /dev/ttyUSB0`）
2. **乱码：** 波特率不匹配，尝试 115200/921600/2000000
3. **无输出：** 检查 TX/RX 是否接反，芯片 UART 引脚是否正确初始化
4. **finsh 不响应：** 确认 `RT_USING_FINSH` 已启用，检查串口设备是否注册成功

---

## 知识库参考

详见 `bk7252n-rtthread-kb` skill 的参考文件，覆盖 RT-Thread 内核、驱动、网络、组件、调试、软件包全部 API 文档。
