---
name: auto-updater
description: MaxClaw智能体自动更新技能。当用户要求检查更新、定时更新、自动更新MaxClaw或技能、手动触发更新、查询更新记录、禁用或启用自动更新时使用。触发词：自动更新、定时更新、版本检测、技能更新、MaxClaw更新、检查更新、更新汇总、禁用自动更新、重新检测更新。
---

# Auto-Updater 技能

MaxClaw 智能体自动更新管理系统，提供定时版本检测、自动更新、汇总报告和通知推送功能。

## 执行逻辑

### 前置检查 (Pre-Execution)

1. **初始化定时任务规则**
   - 默认每日凌晨4点执行（cron: `0 4 * * *`）
   - 支持自定义执行时间和时区配置
   - 使用 `create_cron_job` 工具创建定时任务

2. **加载版本检测体系**
   - 读取本地 MaxClaw 核心框架版本信息
   - 扫描已挂载技能的版本库
   - 读取上次保存的版本基准

3. **确定更新范围**
   - 仅更新技能
   - 包含 MaxClaw 核心框架
   - 指定特定技能列表
   - 用户可通过参数指定范围

4. **初始化日志与通知**
   - 创建更新日志目录 `logs/auto-updater/`
   - 确定通知接收渠道（会话、webhook等）
   - 记录开始时间戳

5. **权限校验**
   - 验证执行更新的最小权限
   - 确保非 root 权限运行
   - 检查文件写入权限

### 主执行流程 (Main Execution)

1. **版本检测**
   ```
   检测流程:
   ├── 获取本地版本信息
   │   ├── MaxClaw 核心框架版本
   │   └── 已挂载技能列表及版本
   ├── 对比官方最新版本
   │   ├── 核心框架更新信息
   │   └── 技能更新信息
   └── 筛选待更新项
       ├── 版本号差异分析
       ├── 变更类型标注 (bug_fix/feature/b breaking)
       └── 更新优先级评估
   ```

2. **自动更新执行**
   ```
   更新流程:
   ├── 按最小权限执行更新
   ├── 跳过失败的技能并标记原因
   ├── 记录更新进度
   └── 处理依赖关系
   ```

3. **结果校验**
   - 验证更新后技能可用性
   - 检查模块导入是否正常
   - 排除兼容性冲突
   - 兼容性检查依赖 `compatibility_check`

4. **汇总报告生成**
   ```json
   {
     "timestamp": "ISO8601时间戳",
     "scope": "更新范围",
     "summary": {
       "total": "总数量",
       "updated": "已更新数量",
       "skipped": "跳过数量",
       "failed": "失败数量"
     },
     "details": [
       {
         "name": "技能名称",
         "before_version": "旧版本",
         "after_version": "新版本",
         "change_type": "bug_fix|feature|breaking",
         "status": "success|skipped|failed",
         "message": "状态信息"
       }
     ],
     "errors": [
       {
         "name": "失败技能名",
         "reason": "失败原因",
         "suggestion": "建议操作"
       }
     ]
   }
   ```

5. **通知推送**
   - 推送更新汇总报告到指定渠道
   - 支持多种通知方式
   - 失败时发送告警通知

### 后置处理 (Post-Execution)

1. **日志持久化**
   - 保存完整更新日志到本地
   - 路径: `logs/auto-updater/update_{timestamp}.log`
   - 包含时间、范围、结果、失败原因

2. **版本信息保存**
   - 更新技能配置库中的版本基准
   - 为下次检测提供参照点
   - 保存更新历史记录

3. **临时文件清理**
   - 清理更新过程中的缓存
   - 删除临时下载文件
   - 清理失败的任务残留

4. **后续操作支持**
   - `更新记录查询`: 查看历史更新日志
   - `重新检测更新`: 立即执行版本检测
   - `禁用自动更新`: 关闭定时任务
   - `启用自动更新`: 开启定时任务
   - `配置更新时间`: 修改执行时间/时区

## 依赖服务

| 依赖 | 用途 |
|------|------|
| `task_scheduling` | 定时任务管理 |
| `version_detection` | 版本检测与对比 |
| `skill_management` | 技能管理操作 |
| `update_execution` | 执行更新操作 |
| `notification_service` | 通知推送服务 |
| `log_record` | 日志记录管理 |
| `compatibility_check` | 兼容性检查 |

## 安全规则

```yaml
security_rules:
  data_isolation: true          # 数据隔离保护
  no_external_call: true        # 禁止外部敏感调用
  least_privilege: true        # 最小权限原则
  update_log_persistence: true  # 更新日志持久化
  update_confirmation_optional: true  # 更新确认可选
  no_root_permission: true      # 禁止root权限运行
  update_failure_alert: true   # 更新失败告警
```

## 使用示例

### 1. 手动检查更新
```
用户: 检查一下有什么可以更新的
助手: 正在检测版本...
- MaxClaw 核心: v1.2.0 -> v1.3.0 (新功能)
- skill-A: v1.0.0 -> v1.0.1 (bug修复)
- skill-B:已是最新版本

是否执行更新?
```

### 2. 触发自动更新
```
用户: 立即更新所有待更新的技能
助手: 开始执行批量更新...
[更新中...]
汇总报告已生成，正在推送通知...
更新完成: 2个已更新, 0个跳过, 1个失败
```

### 3. 禁用自动更新
```
用户: 关闭自动更新
助手: 已禁用自动更新任务。下次手动检查时可使用"检查更新"命令。
```

### 4. 查看更新记录
```
用户: 查看更新记录
助手: 最近更新记录:
- 2024-01-15 04:00: 更新了 skill-A (v1.0.0 -> v1.0.1)
- 2024-01-14 04:00: 无可用更新
```

### 5. 配置更新时间
```
用户: 将自动更新改到每天早上8点
助手: 已更新定时任务: 每天 08:00 执行
```

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| 版本检测失败 | 记录错误，标记为"检测失败"，继续其他项 |
| 更新执行失败 | 跳过该技能，标记失败原因，发送告警 |
| 兼容性冲突 | 中止更新，提示用户手动处理 |
| 网络异常 | 重试3次，失败则标记并继续 |
| 权限不足 | 提示用户权限问题，建议的操作 |

## 配置文件格式

```yaml
# config/auto-updater.yaml
schedule:
  enabled: true
  cron: "0 4 * * *"        # 默认凌晨4点
  timezone: "Asia/Shanghai"
  scope: "all"             # all | skills_only | core_only | custom

update:
  auto_confirm: false      # 是否自动确认（无确认提示）
  skip_on_failure: true    # 单项失败时跳过继续
  backup_before_update: true

notification:
  channels: ["session"]    # session | webhook | email
  webhook_url: ""          # webhook通知地址

logging:
  level: "info"
  retention_days: 30
  path: "logs/auto-updater/"
```

## 命令接口

| 命令 | 功能 |
|------|------|
| `检查更新` / `检查更新 [技能名]` | 执行版本检测 |
| `立即更新` / `更新所有` | 执行批量更新 |
| `更新记录` | 查看历史更新日志 |
| `禁用自动更新` | 关闭定时更新任务 |
| `启用自动更新` | 开启定时更新任务 |
| `配置更新时间 [时间]` | 修改执行时间 |
| `配置更新范围 [范围]` | 修改更新范围 |
