---
description: 监控 qBittorrent / Transmission 下载服务器的运行状态，支持自定义阈值、检测间隔和提醒内容。当种子状态、速度、硬盘空间等指标达到阈值时推送提醒。适用于自托管 BT 玩家和 NAS 用户。
name: torrent-monitor
---

# torrent-monitor 下载服务器监控

## 功能概述

通用 BT 下载服务器监控工具，支持 **qBittorrent** 和 **Transmission** 两种后端。检测完成后将结果写入通知队列，达到用户设定的阈值时推送微信消息（或其他已配置渠道）。

## 快速开始

发送消息给 AI，格式如下：

```
安装 torrent-monitor
服务器类型: qbittorrent
地址: https://qb.example.com
用户名: admin
密码: yourpassword
检测间隔: 30分钟
监控项:
- 错误种子数 > 0
- 上传速度 < 1KB/s 持续 10分钟
- 硬盘剩余 < 10GB
提醒: 当 {metric} 异常，值为 {value}
```

## 配置项说明

### 服务器配置

| 字段 | 必填 | 说明 |
|------|------|------|
| `server_type` | ✅ | `qbittorrent` 或 `transmission` |
| `address` | ✅ | 服务器地址，带协议，如 `https://qb.example.com` |
| `username` | ✅ | 登录用户名 |
| `password` | ✅ | 登录密码 |

### 检测间隔

支持两种写法：
- `30分钟` / `30min`
- `1小时` / `1h`
- 最小值：`5分钟`

### 阈值规则（threshold）

格式：`{指标} {比较符} {数值} [{持续条件}]`

| 指标 | 说明 | 单位 |
|------|------|------|
| `error_count` | 错误状态种子数 | 个 |
| `dl_speed` | 下载速度 | B/s, KB/s, MB/s, GB/s |
| `up_speed` | 上传速度 | 同上 |
| `disk_free` | 硬盘剩余空间 | 同上 |
| `active_torrents` | 活跃任务数 | 个 |

比较符：`>`, `<`, `>=`, `<=`, `==`

持续条件（可选）：`持续 N 分钟` / `for N min`

### 提醒内容模板

在 `提醒` 字段中可用以下变量：

| 变量 | 含义 |
|------|------|
| `{name}` | 种子名称 |
| `{metric}` | 指标名 |
| `{value}` | 当前值 |
| `{threshold}` | 阈值 |
| `{server}` | 服务器别名（用户自定义） |
| `{time}` | 检测时间 |

**默认提醒格式**：
```
⚠️ {server} 告警

{metric} = {value}，超过阈值 {threshold}
{result_details}
```

### 示例配置

#### 示例1：只监控错误
```
服务器类型: qbittorrent
地址: https://qb.example.com:8080
用户名: admin
密码: 123456
检测间隔: 30分钟
监控项:
- error_count > 0
提醒: {server} 检测到 {error_count} 个错误种子！
```

#### 示例2：多条件组合
```
服务器类型: transmission
地址: http://192.168.1.100:9091
用户名: pi
密码: raspberry
服务器别名: 卧室NAS
检测间隔: 15分钟
监控项:
- error_count > 0
- disk_free < 5GB
- up_speed < 1KB/s 持续 30分钟
提醒: {server} | {metric}告警：当前{value}，阈值{threshold}
```

## 管理命令

安装后发送以下命令：

- **查看状态** — 查看当前监控服务器列表和最新检测结果
- **暂停监控** — 暂停指定服务器的监控
- **恢复监控** — 恢复被暂停的监控
- **删除监控** — 移除指定服务器的监控任务
- **手动检测** — 立即对指定服务器执行一次检测（不推送）
- **更新配置** — 修改某个监控项的阈值或提醒内容

## 技术说明

- 后台运行脚本：`/workspace/scripts/torrent-monitor.py`
- 命令行包装器：`/workspace/scripts/torrent-monitor-wrapper.sh`
- 配置存储：`/workspace/config/torrent-monitor/{server_id}.json`
- 日志文件：`/workspace/logs/torrent-monitor/{server_id}.log`
- 状态文件：`/workspace/logs/torrent-monitor/{server_id}.state`
- 推送方式：通过 OpenClaw Cron 定时调度，阈值触发时调用 `message` 工具发送提醒
- 同时支持 qBittorrent v4.x / v5.x API 和 Transmission 3.x+ RPC
