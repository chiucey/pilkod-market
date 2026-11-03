# Auto-Updater 配置指南

## 配置文件格式

技能使用 YAML 格式的配置文件，默认位置: `config/auto-updater.yaml`

### 完整配置示例

```yaml
# Auto-Updater 配置文件
# 位置: config/auto-updater.yaml

# 定时任务调度配置
schedule:
  enabled: true                    # 是否启用定时更新
  cron: "0 4 * * *"               # Cron 表达式 (默认: 每天凌晨4点)
  timezone: "Asia/Shanghai"       # 时区配置
  scope: "all"                     # 更新范围: all | skills_only | core_only | custom
  custom_skills: []                # 当 scope=custom 时，指定技能列表

# 更新行为配置
update:
  auto_confirm: false              # 是否自动确认更新 (无确认提示)
  skip_on_failure: true           # 单项更新失败时是否跳过继续
  backup_before_update: true      # 更新前是否备份
  max_retries: 3                  # 失败重试次数
  retry_delay_seconds: 5          # 重试间隔

# 通知渠道配置
notification:
  channels: ["session"]           # 通知渠道: session | webhook | email
  webhook_url: ""                # Webhook URL (webhook 渠道时必填)
  webhook_headers: {}            # Webhook 请求头
  email_recipients: []           # 邮件收件人列表

# 日志配置
logging:
  level: "info"                  # 日志级别: debug | info | warning | error
  retention_days: 30             # 日志保留天数
  path: "logs/auto-updater/"    # 日志存储路径
  format: "json"                # 日志格式: json | text

# 安全配置
security:
  verify_checksums: true         # 更新前验证文件校验和
  allow_breaking_changes: false  # 是否允许破坏性更新
  require_confirmation_types:    # 需要确认的更新类型
    - "breaking"                # 破坏性更新
    - "major"                   # 主版本更新
```

## Cron 表达式指南

### 基本格式

```
┌───────────── 分钟 (0-59)
│ ┌───────────── 小时 (0-23)
│ │ ┌───────────── 日期 (1-31)
│ │ │ ┌───────────── 月份 (1-12)
│ │ │ │ ┌───────────── 星期 (0-7, 0和7是周日)
│ │ │ │ │
* * * * *
```

### 常用示例

| 表达式 | 含义 |
|--------|------|
| `0 4 * * *` | 每天凌晨 4:00 |
| `0 8 * * *` | 每天早上 8:00 |
| `0 */6 * * *` | 每 6 小时 |
| `0 4 * * 0` | 每周日凌晨 4:00 |
| `0 4 1 * *` | 每月1日凌晨 4:00 |
| `30 3 * * *` | 每天 3:30 |

### 时区配置

支持的时区示例:
- `Asia/Shanghai` - 中国时区
- `America/New_York` - 纽约时区
- `Europe/London` - 伦敦时区
- `UTC` - 世界协调时间

## 更新范围选项

### `all` - 全部更新
更新 MaxClaw 核心框架和所有已挂载技能。

### `skills_only` - 仅技能
只更新已挂载的技能，不更新核心框架。

### `core_only` - 仅核心
只更新 MaxClaw 核心框架。

### `custom` - 自定义
指定要更新的技能列表:
```yaml
schedule:
  scope: "custom"
  custom_skills:
    - "skill-a"
    - "skill-b"
```

## 通知渠道配置

### 会话通知 (session)
默认渠道，直接在智能体会话中显示更新结果。

### Webhook 通知
```yaml
notification:
  channels: ["webhook"]
  webhook_url: "https://your-webhook-endpoint.com/update"
  webhook_headers:
    Authorization: "Bearer your-token"
```

### 邮件通知
```yaml
notification:
  channels: ["email"]
  email_recipients:
    - "admin@example.com"
    - "ops@example.com"
```

## 日志格式

### JSON 格式日志
```json
{
  "timestamp": "2024-01-15T04:00:00+08:00",
  "level": "info",
  "message": "Update check completed",
  "context": {
    "skill": "auto-updater",
    "action": "check_versions",
    "items_found": 5,
    "items_to_update": 2
  }
}
```

### 文本格式日志
```
2024-01-15 04:00:00 [INFO] Update check completed
  - Skills found: 5
  - Skills to update: 2
  - Core framework: up-to-date
```

## 错误代码

| 代码 | 含义 | 建议操作 |
|------|------|----------|
| `E001` | 版本检测失败 | 检查网络连接 |
| `E002` | 更新下载失败 | 重试或手动下载 |
| `E003` | 权限不足 | 检查文件权限 |
| `E004` | 校验和不匹配 | 重新下载或联系支持 |
| `E005` | 兼容性冲突 | 查看详细错误信息 |
| `E006` | 更新执行失败 | 查看具体技能日志 |
| `E007` | 备份失败 | 检查磁盘空间 |
| `E008` | 通知发送失败 | 检查网络和配置 |
