# Auto-Updater API 参考

## 命令接口

### 1. 检查更新

**命令**: `检查更新` / `check-updates` / `检查更新 [技能名]`

**参数**:
- `skill_name` (可选): 指定要检查的技能名称

**响应示例**:
```json
{
  "status": "success",
  "timestamp": "2024-01-15T04:00:00+08:00",
  "core_framework": {
    "name": "MaxClaw Core",
    "current_version": "1.2.0",
    "latest_version": "1.3.0",
    "update_available": true,
    "change_type": "feature"
  },
  "skills": [
    {
      "name": "skill-A",
      "current_version": "1.0.0",
      "latest_version": "1.0.1",
      "update_available": true,
      "change_type": "bug_fix"
    },
    {
      "name": "skill-B",
      "current_version": "2.1.0",
      "latest_version": "2.1.0",
      "update_available": false
    }
  ],
  "summary": {
    "total_skills": 2,
    "skills_to_update": 1,
    "core_to_update": true
  }
}
```

### 2. 执行更新

**命令**: `立即更新` / `update-now` / `更新所有`

**参数**:
- `scope` (可选): `all` | `skills_only` | `core_only` | `skills:[name1,name2]`
- `force` (可选): 是否强制更新

**响应示例**:
```json
{
  "status": "completed",
  "timestamp": "2024-01-15T04:05:00+08:00",
  "summary": {
    "total": 3,
    "updated": 2,
    "skipped": 0,
    "failed": 1
  },
  "details": [
    {
      "name": "MaxClaw Core",
      "before_version": "1.2.0",
      "after_version": "1.3.0",
      "status": "success"
    },
    {
      "name": "skill-A",
      "before_version": "1.0.0",
      "after_version": "1.0.1",
      "status": "success"
    },
    {
      "name": "skill-B",
      "before_version": "2.1.0",
      "after_version": null,
      "status": "failed",
      "error": "Compatibility check failed",
      "error_code": "E005"
    }
  ],
  "notification_sent": true
}
```

### 3. 查看更新记录

**命令**: `更新记录` / `update-history`

**参数**:
- `limit` (可选): 返回记录数量，默认 10
- `offset` (可选): 分页偏移量

**响应示例**:
```json
{
  "status": "success",
  "records": [
    {
      "id": "update_20240115040000",
      "timestamp": "2024-01-15T04:00:00+08:00",
      "scope": "all",
      "result": {
        "updated": 2,
        "failed": 1
      },
      "duration_seconds": 45
    },
    {
      "id": "update_20240114040000",
      "timestamp": "2024-01-14T04:00:00+08:00",
      "scope": "all",
      "result": {
        "updated": 0,
        "failed": 0
      },
      "duration_seconds": 3
    }
  ],
  "pagination": {
    "total": 30,
    "limit": 10,
    "offset": 0
  }
}
```

### 4. 定时任务管理

#### 启用自动更新
**命令**: `启用自动更新` / `enable-auto-update`

#### 禁用自动更新
**命令**: `禁用自动更新` / `disable-auto-update`

#### 配置执行时间
**命令**: `配置更新时间 [时间]` / `set-update-time [time]`

**参数示例**:
- `每天早上8点`
- `每周日凌晨3点`
- `cron:0 8 * * *`

### 5. 配置更新范围

**命令**: `配置更新范围 [范围]` / `set-update-scope [scope]`

**可用范围**:
- `全部` / `all` - 更新所有
- `仅技能` / `skills_only` - 只更新技能
- `仅核心` / `core_only` - 只更新核心框架
- `[技能1],[技能2]` - 指定技能列表

## 版本变更类型

| 类型 | 描述 | 示例 |
|------|------|------|
| `bug_fix` | Bug 修复 | v1.0.0 → v1.0.1 |
| `feature` | 新功能 | v1.0.0 → v1.1.0 |
| `breaking` | 破坏性变更 | v1.0.0 → v2.0.0 |
| `security` | 安全更新 | v1.0.0 → v1.0.1 |
| `minor` | 小改进 | v1.0.0 → v1.0.2 |

## 状态码

| 状态码 | 含义 |
|--------|------|
| `200` | 操作成功 |
| `400` | 参数错误 |
| `401` | 权限不足 |
| `404` | 技能不存在 |
| `500` | 服务器错误 |
| `503` | 服务不可用 (正在更新) |

## Webhook 事件

当配置 webhook 通知时，会推送以下事件:

### 事件类型

#### `update.check.completed`
版本检测完成
```json
{
  "event": "update.check.completed",
  "timestamp": "2024-01-15T04:00:00+08:00",
  "data": {
    "items_to_update": 3
  }
}
```

#### `update.execution.started`
更新开始
```json
{
  "event": "update.execution.started",
  "timestamp": "2024-01-15T04:05:00+08:00",
  "data": {
    "scope": "all",
    "total_items": 3
  }
}
```

#### `update.execution.completed`
更新完成
```json
{
  "event": "update.execution.completed",
  "timestamp": "2024-01-15T04:10:00+08:00",
  "data": {
    "scope": "all",
    "result": {
      "updated": 2,
      "failed": 1
    }
  }
}
```

#### `update.item.failed`
单个更新项失败
```json
{
  "event": "update.item.failed",
  "timestamp": "2024-01-15T04:07:00+08:00",
  "data": {
    "item_name": "skill-B",
    "error_code": "E005",
    "error_message": "Compatibility check failed"
  }
}
```
