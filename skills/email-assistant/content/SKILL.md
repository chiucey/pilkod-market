---
name: email-assistant
description: 邮件助手技能。当用户提到收邮件、发邮件、查邮件、读取邮件、发送邮件、邮件管理、email、e-mail等词语时触发此技能。执行邮件读取、发送、搜索等操作。
---

# 邮件助手 (Email Assistant)

## 功能概述

智能处理各种邮件相关请求：
- **读取邮件**：查看收件箱、指定邮件或搜索结果
- **发送邮件**：撰写并发送新邮件
- **搜索邮件**：按关键词、日期、发件人等条件搜索
- **邮件管理**：标记已读、删除、移动等操作

## 工作流程

### 1. 意图识别与解析

分析用户请求，提取关键信息：

| 信息类型 | 示例 | 提取方式 |
|---------|------|---------|
| 收件人 | "发给张三" | 正则匹配邮箱或姓名 |
| 主题 | "主题是项目计划" | 关键字"主题" |
| 内容 | "内容是明天下午开会" | 取关键词后的文本 |
| 附件 | "带上附件xxx.pdf" | 关键字"附件" |
| 时间范围 | "上周的邮件" | 日期解析 |

### 2. 操作类型识别

```
操作类型 = "read" | "send" | "search" | "manage"
```

- **read**：用户想查看邮件
- **send**：用户想发送邮件
- **search**：用户想搜索邮件
- **manage**：用户想管理邮件（删除、标记等）

### 3. 参数收集表单

如果信息不足，使用交互式表单收集：

```xml
<genui-form-wizard title="邮件操作" action-id="email_operation">
  <genui-form-page title="收件人信息">
    <genui-input name="recipient" placeholder="输入收件人邮箱或姓名"></genui-input>
  </genui-form-page>
  <genui-form-page title="邮件详情">
    <genui-input name="subject" placeholder="输入邮件主题"></genui-input>
    <genui-input selection-mode="checkbox" name="hasAttachment" placeholder="是否有附件 (是/否)"></genui-input>
  </genui-form-page>
  <genui-form-page title="邮件内容">
    <genui-input name="body" placeholder="输入邮件正文内容"></genui-input>
  </genui-form-page>
</genui-form-wizard>
```

## 配置要求

### SMTP/IMAP 配置

技能需要以下配置（通过 secrets 获取）：

| 配置项 | 说明 | 示例 |
|-------|------|------|
| `EMAIL_SMTP_HOST` | SMTP服务器地址 | smtp.gmail.com |
| `EMAIL_SMTP_PORT` | SMTP端口 | 587 |
| `EMAIL_IMAP_HOST` | IMAP服务器地址 | imap.gmail.com |
| `EMAIL_IMAP_PORT` | IMAP端口 | 993 |
| `EMAIL_USERNAME` | 邮箱账号 | user@gmail.com |
| `EMAIL_PASSWORD` | 邮箱密码/授权码 | xxxxxxxxxx |

### 安全说明

- 所有凭证通过加密环境变量传递
- 不在日志或响应中暴露敏感信息
- 支持 OAuth2 认证（可选）

## 执行脚本

### 读取邮件 (Python)

```python
import imaplib
import email
from email.header import decode_header

def read_emails(account, folder='INBOX', count=10):
    """读取邮件列表"""
    mail = imaplib.IMAP4_SSL(config['IMAP_HOST'], config['IMAP_PORT'])
    mail.login(config['USERNAME'], config['PASSWORD'])
    mail.select(folder)

    # 获取最新邮件
    _, messages = mail.search(None, 'ALL')
    email_ids = messages[0].split()[-count:]

    results = []
    for eid in email_ids:
        _, data = mail.fetch(eid, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        results.append({
            'from': decode_mime(msg['From']),
            'subject': decode_mime(msg['Subject']),
            'date': msg['Date'],
            'id': eid
        })

    mail.logout()
    return results

def read_email_content(email_id, folder='INBOX'):
    """读取单封邮件完整内容"""
    # 解析邮件正文，处理多部分和附件
    ...
```

### 发送邮件 (Python)

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to, subject, body, attachments=None):
    """发送邮件"""
    msg = MIMEMultipart()
    msg['From'] = config['USERNAME']
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # 添加附件
    if attachments:
        for file in attachments:
            with open(file, 'rb') as f:
                part = MIMEBase()
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{file}"')
                msg.attach(part)

    with smtplib.SMTP(config['SMTP_HOST'], config['SMTP_PORT']) as server:
        server.starttls()
        server.login(config['USERNAME'], config['PASSWORD'])
        server.send_message(msg)

    return {'status': 'success', 'message': '邮件已发送'}
```

### 搜索邮件 (Python)

```python
def search_emails(criteria):
    """搜索邮件

    criteria 支持:
    - from: 发件人
    - to: 收件人
    - subject: 主题关键词
    - body: 正文关键词
    - since: 起始日期
    - before: 结束日期
    """
    search_criteria = []

    if criteria.get('from'):
        search_criteria.append(f'FROM "{criteria["from"]}"')
    if criteria.get('subject'):
        search_criteria.append(f'SUBJECT "{criteria["subject"]}"')
    if criteria.get('since'):
        search_criteria.append(f'SINCE {criteria["since"]}')
    if criteria.get('before'):
        search_criteria.append(f'BEFORE {criteria["before"]}')

    query = ' '.join(search_criteria) or 'ALL'

    _, messages = mail.search(None, query)
    # 返回匹配的邮件列表
    ...
```

## 响应格式

### 成功响应

```json
{
  "status": "success",
  "action": "read|send|search|manage",
  "data": {
    "emails": [...],
    "count": 5
  },
  "message": "操作完成说明"
}
```

### 错误响应

```json
{
  "status": "error",
  "code": "AUTH_FAILED | INVALID_RECIPIENT | NETWORK_ERROR",
  "message": "友好的错误提示"
}
```

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 认证失败 | 提示用户检查邮箱配置 |
| 网络错误 | 重试3次，失败后提示检查网络 |
| 无效收件人 | 要求用户确认收件人地址 |
| 附件过大 | 提示附件大小限制 |

## 示例对话

### 示例1：读取邮件
```
用户：帮我看看最近有什么新邮件
助手：(触发技能) 正在连接邮箱...已找到5封未读邮件:
1. [项目通知] 张三 - 项目进度更新 - 今天 10:30
2. [系统通知] 管理员 - 账户安全提醒 - 今天 09:15
3. [会议邀请] 李四 - 周五产品评审会 - 昨天 17:20
...
```

### 示例2：发送邮件
```
用户：给zhangsan@company.com发一封邮件，主题是项目计划，内容是周三前完成初版
助手：(触发技能) 正在发送邮件...
✅ 邮件已发送成功！
  收件人: zhangsan@company.com
  主题: 项目计划
  内容: 周三前完成初版
```

### 示例3：搜索邮件
```
用户：找一下上周关于预算的邮件
助手：(触发技能) 正在搜索...找到2封相关邮件:
1. [预算审批] 王五 - 2024年Q1预算申请 - 3月8日
2. [Re: 预算] 赵六 - 回复: 预算讨论 - 3月6日
```