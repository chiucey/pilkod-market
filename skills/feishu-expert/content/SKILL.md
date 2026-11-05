---
name: feishu-expert
description: 飞书全链路自动化技能，完美复刻ClawHub gog技能交互逻辑。用户通过自然语言即可完成飞书云文档编辑、日历预约会议、会议纪要自动生成、审批流转发起、云文档权限管理、飞书邮箱收发等全链路操作。当用户要求操作飞书文档、管理日历、发起审批、发送邮件、整理会议记录、同步信息时使用。
skill-id: 1928463527
---

# 飞书全链路自动化助手

## 技能概述

本技能完全复刻 ClawHub 的 gog 技能交互逻辑，对接飞书开放平台 API，让用户用自然语言即可完成所有飞书操作。

## 核心能力

### 1. 飞书云文档
- 自动创建 Markdown 格式的飞书文档
- 文档内容整理与格式化
- 云文档权限管理

### 2. 飞书日历
- 自动预约会议日程
- 邀请参会人（支持多人）
- 日历事件管理

### 3. 会议纪要
- 自动整理会议记录为飞书文档
- 一键同步给项目组成员

### 4. 飞书审批
- 自动发起审批流转
- 支持自定义审批表单
- 审批进度追踪

### 5. 飞书邮箱
- 自动发送邮件
- 支持 HTML 格式正文
- 邮件附件支持（扩展功能）

## 使用示例

```
用户: "帮我把这份会议记录整理成飞书文档，同步给项目组"
操作: create_document
参数: title="会议纪要", content="..."

用户: "帮我预约明天下午3点的会议，邀请张三和李四"
操作: create_calendar_event
参数: summary="会议", start_time="2025-03-28T15:00:00+08:00", attendees=["zhangsan", "lisi"]

用户: "帮我给XX发个审批，内容是这个项目的预算"
操作: create_approval
参数: title="预算审批", approver="xxx", form_content={...}

用户: "给李四发邮件，主题是项目进展，正文附上"
操作: send_email
参数: to="lisi@example.com", subject="项目进展", body="..."
```

## 技术架构

- **语言**: Python 3.8+
- **依赖**: requests, pyyaml
- **API**: 飞书开放平台 v1 API
- **认证**: 租户访问凭证 (Tenant Access Token)

## 环境配置

| 环境变量 | 说明 | 必填 |
|---------|------|------|
| FEISHU_APP_ID | 飞书应用 ID | 是 |
| FEISHU_APP_SECRET | 飞书应用密钥 | 是 |
| FEISHU_FOLDER_TOKEN | 默认文档夹 Token | 否 |
| FEISHU_APPROVAL_CODE | 审批模板代码 | 否 |
| FEISHU_CALENDAR_ID | 日历 ID | 否 |

## 飞书权限申请

需要在飞书开放平台为应用开通以下权限：
- `docx:document:create` - 创建文档
- `docx:document:readonly` - 读取文档
- `calendar:event:write` - 写日历事件
- `approval:instance:create` - 创建审批实例
- `mail:message:send` - 发送邮件

## 敏感操作

以下操作需要用户二次确认：
- 发起审批
- 发送邮件

## 错误处理

| 错误类型 | 说明 | 解决方案 |
|---------|------|---------|
| 凭证失败 | APP_ID 或 APP_SECRET 错误 | 检查环境变量配置 |
| 权限不足 | 应用未开通对应权限 | 在飞书开放平台授权 |
| 参数缺失 | 缺少必要参数 | 按提示补充参数 |

## 版本历史

- **1.0.0** 初始版本，支持文档、日历、审批、邮件基础功能
