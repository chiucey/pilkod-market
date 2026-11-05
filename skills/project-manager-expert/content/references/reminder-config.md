# Reminder Configuration Guide

## Reminder Types

### 1. Daily Reminder

**Purpose:** Daily task check and progress update

**Configuration:**
```json
{
  "job_title": "Daily Project Check",
  "cron_expression": "0 9 * * *",
  "job_instruction": "Check project task status, generate daily todo list, update milestone progress, identify overdue tasks."
}
```

**Cron Expression Guide:**
- `0 9 * * *` = Every day at 9:00 AM
- `0 8 * * *` = Every day at 8:00 AM
- `0 18 * * *` = Every day at 6:00 PM

### 2. Weekly Reminder

**Purpose:** Weekly report generation and phase review

**Configuration:**
```json
{
  "job_title": "Weekly Project Report",
  "cron_expression": "0 9 * * 1",
  "job_instruction": "Generate weekly project report including: completed tasks, in-progress tasks, milestone status, risk alerts, and next week plans."
}
```

**Cron Expression Guide:**
- `0 9 * * 1` = Every Monday at 9:00 AM
- `0 9 * * 5` = Every Friday at 9:00 AM
- `0 10 * * 1` = Every Monday at 10:00 AM

### 3. Custom Reminder

**Purpose:** Specific milestone or key date reminder

**Configuration:**
```json
{
  "job_title": "Milestone Due Reminder",
  "cron_expression": "0 9 * * *",
  "job_instruction": "Check milestones due in next 3 days and generate reminder report."
}
```

## Reminder Content Templates

### Daily Reminder Template

```markdown
## Daily Project Reminder

**Date:** {date}

### Today's Todo
- [ ] Task 1
- [ ] Task 2

### Due Soon (3 days)
- Task A - Due: {date}

### Overdue Tasks
- Task B - Overdue: {days} days

### Milestone Progress
- Completed: {completed}
- In Progress: {in_progress}

---
Reply "project status" for detailed report.
```

### Weekly Reminder Template

```markdown
## Weekly Project Report

**Period:** {start_date} to {end_date}

### Completed This Week
- Milestone 1.1
- Task A

### In Progress
- Milestone 2.1 (60%)
- Task B (30%)

### Milestone Status
| Milestone | Status | Planned Date | Actual Date |
|-----------|--------|--------------|-------------|
| Phase 1   | Done   | 03/15        | 03/14       |
| Phase 2   | Active | 03/20        | -           |

### Risk Alerts
Task B is 5 days behind schedule

### Next Week Plans
- Start Milestone 2.2
- Complete Task C

---
Reply "adjust reminder settings" to modify.
```

## Reminder Frequency Recommendations

| Project Type | Daily Reminder | Weekly Reminder |
|--------------|----------------|-----------------|
| Event Planning | Yes (2 weeks before event) | Yes |
| Construction | Yes (key phases) | Yes |
| Routine Maintenance | No | Yes |
| Urgent Projects | Yes (full duration) | Yes |

## Reminder Channels

Currently Supported:
- Direct reminders in conversation
- Generated report files (saveable)

Future Extensions:
- Email notifications
- WeChat/DingTalk push
- SMS alerts

## Reminder Configuration Examples

### Example 1: Event Planning Project

```
Daily Reminder: Start 1 month before event, every day at 9 AM
Weekly Reminder: Every Monday at 10 AM for weekly report
Key Reminders: Daily reminders starting 3 days before milestones
```

### Example 2: Construction Project

```
Daily Reminder: During construction period, every day at 8 AM
Weekly Reminder: Every Friday at 3 PM for progress report
Key Reminders: Daily reminders starting 1 week before acceptance
```

## Reminder Termination Conditions

- Project completion
- User-initiated cancellation
- Auto-pause after 90 days of inactivity

## Adjusting Reminder Settings

Users can adjust anytime:
- Reminder time
- Reminder frequency
- Reminder content
- Reminder channel

Simply reply "adjust reminder settings".
