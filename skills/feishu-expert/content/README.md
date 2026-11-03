# 飞书全链路自动化技能

> 对标 ClawHub gog 技能的自然语言飞书操作助手

## 简介

这是一个纯 Python 实现的飞书全链路自动化技能，完全复刻 ClawHub 的 gog 技能交互逻辑。用户通过自然语言即可完成所有飞书操作，无需记忆复杂的 API 调用方式。

## 核心能力

| 功能 | 说明 |
|------|------|
| **飞书云文档** | 自动创建、编辑、读取、权限管理 |
| **飞书日历** | 自动预约会议、邀请参会人、设置提醒 |
| **会议纪要** | 自动整理会议记录为结构化文档 |
| **飞书审批** | 快速发起各类审批流程 |
| **飞书邮箱** | 支持 HTML 格式邮件发送 |
| **权限管理** | 文档分享、成员权限控制 |

## 快速开始

### 1. 安装依赖

```bash
pip install requests pyyaml
```

### 2. 配置飞书应用

1. 前往 [飞书开放平台](https://open.feishu.cn/app) 创建应用
2. 获取 **APP_ID** 和 **APP_SECRET**
3. 开通以下权限：

| 权限名称 | 权限标识 | 说明 |
|---------|---------|------|
| 创建云文档 | `docx:document:create` | 创建飞书文档 |
| 读取云文档 | `docx:document:readonly` | 读取文档内容 |
| 日历事件写入 | `calendar:event:write` | 创建日历事件 |
| 审批实例创建 | `approval:instance:create` | 发起审批 |
| 邮件消息发送 | `mail:message:send` | 发送邮件 |

### 3. 配置环境变量

```bash
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"

# 可选配置
export FEISHU_FOLDER_TOKEN="default_folder_token"    # 默认文档夹
export FEISHU_APPROVAL_CODE="your_approval_code"      # 审批模板代码
export FEISHU_CALENDAR_ID="primary"                   # 日历ID
```

### 4. 使用技能

在 MiniMax Agent 中，通过以下关键词触发技能：

- 飞书、feishu
- 文档、日历、审批、邮箱
- 会议纪要、整理

## 使用示例

### 创建飞书文档

**用户输入**:
```
帮我把这份会议记录整理成飞书文档
```

**处理结果**:
```
文档已创建成功！
📄 标题: 会议纪要
🔗 链接: https://bytedance.feishu.cn/docx/xxx
```

### 预约会议

**用户输入**:
```
帮我预约明天下午3点的会议，邀请张三和李四
```

**处理结果**:
```
日历事件已创建！
📅 主题: 会议
🕐 时间: 2025-03-28 15:00 - 16:00
🔗 链接: https://calendar.feishu.cn/event/xxx
```

### 发起审批

**用户输入**:
```
帮我发起一个项目预算审批，审批人是李经理
```

**系统确认**:
```
请确认执行以下操作:
- 操作类型: create_approval
- 审批标题: 项目预算审批
- 审批人: 李经理

如确认，请回复"确认发送"。
```

### 发送邮件

**用户输入**:
```
给 zhangsan@example.com 发邮件，主题是项目进展报告
```

**系统确认**:
```
请确认发送邮件:
- 收件人: zhangsan@example.com
- 主题: 项目进展报告

回复"确认"执行发送。
```

### 生成会议纪要

**用户输入**:
```
帮我把这份会议记录整理成规范的会议纪要
```

**处理结果**:
```
会议纪要已生成并创建为飞书文档！
📄 标题: 会议纪要
🔗 链接: https://bytedance.feishu.cn/docx/xxx
```

## API 文档

### 支持的操作类型

| Action | 说明 | 敏感操作 |
|--------|------|---------|
| `create_document` | 创建云文档 | 否 |
| `update_document` | 更新文档内容 | 否 |
| `get_document` | 获取文档信息 | 否 |
| `share_document` | 分享文档权限 | 否 |
| `create_calendar_event` | 创建日历事件 | 否 |
| `create_approval` | 发起审批 | **是** |
| `send_email` | 发送邮件 | **是** |
| `generate_meeting_summary` | 生成会议纪要 | 否 |

### 参数格式

#### 时间格式（ISO 8601）

```
2025-03-28T15:00:00+08:00
```

#### 用户ID类型

- `openid`: 用户的 Open ID
- `userid`: 用户的 User ID
- `email`: 用户邮箱
- `unionid`: 用户的 Union ID

## 项目结构

```
feishu-expert/
├── SKILL.md                      # 技能元数据
├── README.md                     # 说明文档
├── src/
│   └── main.py                   # 主逻辑入口
├── instructions/
│   └── system_prompt.md           # 系统提示词
├── config/
│   └── settings.yaml             # 配置文件
├── tests/
│   └── test_main.py              # 测试用例
└── assets/
    └── .gitkeep                  # 资源目录
```

## 测试

```bash
cd feishu
python -m pytest tests/test_main.py -v
```

## 故障排查

### 凭证获取失败

**错误**: `获取飞书访问凭证失败`

**解决方案**:
1. 检查 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 是否正确
2. 确认应用已在飞书开放平台启用
3. 检查应用是否在租户内发布

### 权限不足

**错误**: `权限不足`

**解决方案**:
1. 在飞书开放平台检查应用权限
2. 重新发布应用以应用新权限
3. 确认已开通所需的具体权限

### 文档创建失败

**错误**: `创建文档失败`

**解决方案**:
1. 检查 `folder_token` 是否有效
2. 确认文件夹访问权限
3. 检查文档内容格式

### 日历事件创建失败

**错误**: `日历事件创建失败`

**解决方案**:
1. 检查时间格式是否为 ISO 8601
2. 确认 `calendar_id` 存在
3. 验证参会人 ID 是否正确

## 已知限制

1. 文档创建目前仅支持基础 Markdown 格式
2. 日历事件仅支持主日历
3. 邮件附件功能暂未实现
4. 审批表单需符合模板要求

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 版本历史

- **1.0.0** (2025-03-27)
  - 初始版本发布
  - 支持文档、日历、审批、邮件基础功能
  - 完整复刻 ClawHub gog 技能交互逻辑

---

**对标技能**: ClawHub gog
**作者**: MiniMax Agent
**版本**: 1.0.0
