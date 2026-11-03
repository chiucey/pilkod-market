---
name: study-reminder
description: Study reminder skill. Use when inputting next day's study plan including location, content, and time. The agent will remind you on time the next day. Trigger phrases: "add study plan", "what to study tomorrow", "remind me to study", "set study reminder".
---

# 学习备忘录

帮助 Python 初学者规划每日学习计划，并在第二天准时提醒。

## 核心功能

- 添加第二天的学习计划
- 存储学习地点、内容、时间
- 第二天自动提醒学习任务

## 使用流程

### 1. 添加学习计划

当你告诉 Agent 明天的学习计划时，Agent 会提取并存储以下信息：

| 字段 | 说明 | 示例 |
|------|------|------|
| study_location | 学习地点 | 图书馆三楼自习室 |
| study_content | 学习内容 | Python 基础语法 |
| study_time | 学习时间 | 09:00 |

### 2. 数据存储

学习计划保存在 `~/.study_plans.json` 文件中，格式如下：

```json
{
  "plans": [
    {
      "date": "2026-04-23",
      "study_location": "图书馆三楼自习室",
      "study_content": "Python 基础语法",
      "study_time": "09:00",
      "reminded": false
    }
  ]
}
```

### 3. 提醒机制

- 每天早上 8:00 自动检查当天计划
- 若有计划，Agent 会主动提醒你
- 提醒内容包括：时间、地点、学习内容

## 示例对话

**用户**: 明天我要在图书馆二楼学 Python 基础语法，9点开始

**Agent**: 好的！我已经记录了你的学习计划：
- 日期：2026-04-23
- 时间：09:00
- 地点：图书馆二楼
- 内容：Python 基础语法

明天早上我会准时提醒你！

## 注意事项

- 学习计划针对"明天"，系统会自动计算实际日期
- 支持修改和删除已添加的计划
- 提醒时间固定为当天 08:00

## 技术实现

- 数据存储：JSON 文件
- 提醒系统：定时任务 + Agent 主动推送
- 依赖：Python 3.x, 无需额外库
