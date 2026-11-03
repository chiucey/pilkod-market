# HEARTBEAT.md - 每日进度提醒配置

## 每天中午12:00 - 活动进度提醒

**任务说明**：
检查所有启用了每日提醒的活动项目，推送当日进度报告。

**执行步骤**：
1. 扫描 `~/.openclaw/workspace/events/` 目录下的所有活动文件
2. 对于每个 `enable_daily_reminder` 为 true 的活动：
   - 运行：`python ~/.openclaw/workspace/skills/event-project-manager/scripts/task_scheduler.py daily <活动名称>`
   - 将输出发送给用户

**提醒内容包含**：
- 今日待完成任务
- 已逾期任务（红色警告）
- 即将到期任务（3天内，黄色提醒）
- 整体进度百分比

---

## 配置示例

当用户确认创建活动后，活动数据文件会自动包含以下配置：

```json
{
  "event_name": "活动名称",
  "enable_daily_reminder": true,
  "reminder_time": "12:00",
  ...
}
```

如需关闭某活动的每日提醒，可手动修改对应JSON文件，将 `enable_daily_reminder` 设为 `false`。
