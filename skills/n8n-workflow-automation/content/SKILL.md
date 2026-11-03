---
name: n8n-workflow-automation
description: 连接 n8n 实现跨平台工作流自动化，支持节点调用、模板管理和自动化执行。
---

# n8n 工作流自动化技能

连接 n8n 实现跨平台工作流自动化，支持节点调用、模板管理和自动化执行。

## 前置要求

确保 n8n 实例正在运行，并获取访问地址和 API Key：
```bash
# 或通过环境变量
export N8N_BASE_URL="https://your-n8n-instance.com"
export N8N_API_KEY="your-api-key"
```

## 核心功能

### 执行工作流
```bash
# 触发指定工作流
n8n execute --workflow-id <id> --payload '{"key":"value"}'

# 按名称执行
n8n execute --workflow-name "数据同步"
```

### 节点操作
```bash
# 触发特定节点
n8n trigger --node "Slack通知节点" --workflow-id <id>

# 查看节点状态
n8n nodes status --workflow-id <id>
```

### 模板管理
```bash
# 列出可用模板
n8n template list

# 从模板创建工作流
n8n workflow create --template "A股数据采集"
```

## 使用场景

- 当用户要求自动化跨平台工作流时
- 当需要触发 n8n 中的特定自动化流程时
- 当需要管理 n8n 工作流和节点时
- 当需要将 AI 输出接入现有自动化流程时

## 与 OpenClaw 集成

可以在定时任务或 AI 对话中触发 n8n 工作流：
```bash
# 在定时任务中调用
n8n execute --workflow-name "每日股市数据汇总"
```

## 常用 n8n 节点

| 节点 | 用途 |
|------|------|
| HTTP Request | 调用外部 API |
| Slack/钉钉 | 消息通知 |
| Google Sheets | 表格数据 |
| Telegram | 消息推送 |
| 代码 | 自定义逻辑 |
