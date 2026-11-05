---
name: cron-task-check
description: 定时任务检查与修复 Skill。每次定时任务执行后自动检查结果，若推送失败立即修复并重试。触发条件：定时任务执行后检查、任务疑似失败时诊断。适用于所有使用 cron 设置的定时任务。
---

# Cron 任务检查与修复 Skill

## 触发场景

1. 定时任务执行后，**自动检查任务是否成功**
2. 用户反馈"没收到推送"时，**立即诊断并修复**
3. 任何 cron 任务设置后，**验证能否正常运行**

## 核心原则

> ⚠️ **定时任务发出后不检查 = 任务没完成**
> 每次 cron 触发后，必须验证消息是否成功送达用户手中

## 检查流程

### Step 1：读取任务配置
```bash
openclaw cron list --json 2>&1
```
找到任务名，确认 `state.nextRunAtMs`（下次运行时间）和 `state.lastRunAtMs`（上次运行时间）。

### Step 2：检查任务执行日志
```bash
openclaw cron runs <job-id> --json 2>&1 | head -50
```
查看是否成功执行、是否有错误。

### Step 3：验证输出文件
检查脚本输出文件是否存在（如 `/workspace/reports/daily_briefing.md`）：
```bash
ls -la /workspace/reports/ && head -5 /workspace/reports/daily_briefing.md
```

### Step 4：验证飞书推送
检查飞书日志是否有发送记录，或直接用飞书测试：
```bash
openclaw status 2>&1 | grep -i "feishu\|channel\|online"
```

## 自动修复方案

### 常见失败原因及修复方法

**❌ 原因 1：脚本执行失败**
- 表现：cron runs 显示 error 或 timeout
- 修复：直接运行脚本，查看报错
```bash
python3 /workspace/skills/news-daily-briefing/briefing.py
```

**❌ 原因 2：飞书推送失败（channel 不可用）**
- 表现：脚本运行成功，但飞书未收到消息
- 修复：重新发布飞书频道配置
```bash
openclaw channels enable feishu 2>&1
# 或使用 gateway tool 重新配置
```

**❌ 原因 3：定时任务被禁用**
- 表现：任务 state 为 "disabled"
- 修复：重新启用
```bash
openclaw cron enable <job-id> 2>&1
```

**❌ 原因 4：Gateway 重启后任务丢失**
- 表现：cron list 中找不到任务
- 修复：重新添加 cron 任务

**❌ 原因 5：数据源 mcporter 无响应**
- 表现：briefing.py 输出为空或超时
- 修复：直接通过 HTTP 调用
```bash
npx mcporter call zaker.list_flash --args '{"cursor": ""}' 2>&1
# 如果失败，手动从新浪/Reuters 抓取新闻
```

## 快速诊断命令清单

```bash
# 1. 查看所有定时任务状态
openclaw cron list 2>&1

# 2. 查看最近执行结果
openclaw cron runs <job-id> 2>&1 | tail -20

# 3. 测试脚本是否正常
python3 /workspace/skills/news-daily-briefing/briefing.py 2>&1

# 4. 测试 MCP 连接
npx mcporter list 2>&1

# 5. 测试飞书连通性
openclaw channels status feishu 2>&1

# 6. 查看 Gateway 状态
openclaw gateway status 2>&1

# 7. 检查飞书配对状态
openclaw pairing list feishu 2>&1
```

## 每日定时任务清单（当前已配置）

| 任务名 | 时间 | 功能 | 状态 |
|--------|------|------|------|
| Max 早间要闻简报 | 08:30 UTC | 调用 briefing.py，生成并飞书推送 | 已配置 |
| Max 晚间要闻简报 | 19:00 UTC | 调用 briefing.py，生成并飞书推送 | 已配置 |
| Max 每日问候 | 08:00 UTC | 早安问候 | 已配置 |

## 预防性维护

每次添加新的 cron 任务时，同步更新本 skill 的"每日定时任务清单"。

格式要求：
- 任务名、时间、功能、状态、脚本路径（如果有）
- 关联飞书 sender ID（用于推送验证）

## 故障响应优先级

1. **立即**：确认用户是否收到任务消息（飞书是否有推送）
2. **5分钟内**：诊断失败原因（看 cron runs 日志）
3. **修复**：根据"常见失败原因"对症处理
4. **验证**：重新运行脚本，确认输出正常后再重新触发 cron
5. **记录**：将故障原因和修复步骤写入 MEMORY.md