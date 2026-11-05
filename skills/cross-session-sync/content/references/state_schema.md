# 状态模式参考

## 会话状态完整结构

```json
{
  "session_id": "session_WEB_20260404_103622_a1b2c3",
  "created_at": "2026-04-04T10:36:22.123456",
  "channel": "web",
  "status": "in_progress",

  "task": {
    "type": "代码开发|数据分析|文档撰写|...|",
    "description": "详细的任务描述",
    "priority": "high|medium|low"
  },

  "progress": {
    "completed_steps": [
      "步骤1描述",
      "步骤2描述"
    ],
    "current_step": "当前正在进行的步骤",
    "next_steps": [
      "下一步计划1",
      "下一步计划2"
    ],
    "progress_percent": 60
  },

  "context": {
    "summary": "上下文摘要段落",
    "key_constraints": ["约束1", "约束2"],
    "user_preferences": {
      "format": "...",
      "style": "..."
    }
  },

  "artifacts": [
    {
      "id": "art_abc123",
      "path": "/workspace/output/file.ext",
      "description": "文件用途描述",
      "type": "code|data|document|image|...|",
      "size": "123KB",
      "created_at": "2026-04-04T10:40:00"
    }
  ],

  "pending": {
    "questions": ["待决问题1", "待决问题2"],
    "approvals_needed": ["需要用户确认的事项"],
    "blocked_by": ["阻塞原因"]
  },

  "metadata": {
    "agent_id": "MiniMax Agent",
    "version": "1.0.0",
    "tags": ["tag1", "tag2"]
  }
}
```

## 任务类型枚举

| 类型 | 描述 | 典型步骤 |
|------|------|----------|
| `code_development` | 代码开发 | 需求分析 → 设计 → 实现 → 测试 → 部署 |
| `data_analysis` | 数据分析 | 数据获取 → 清洗 → 分析 → 可视化 → 报告 |
| `document_writing` | 文档撰写 | 构思 → 大纲 → 撰写 → 审核 → 定稿 |
| `research` | 研究调研 | 资料搜集 → 整理分析 → 总结报告 |
| `design` | 设计工作 | 需求沟通 → 方案设计 → 评审 → 交付 |
| `troubleshooting` | 问题排查 | 问题定位 → 原因分析 → 方案制定 → 实施 |
| `general` | 通用任务 | 用户自定义 |

## 渠道标识

| 渠道 | 代码 | 描述 |
|------|------|------|
| 网页版 | `web` | Web端界面 |
| 飞书 | `feishu` | 飞书集成 |
| Slack | `slack` | Slack集成 |
| 微信 | `wechat` | 微信集成 |
| 移动端 | `mobile` | 移动App |
| API | `api` | API调用 |
| 未知 | `unknown` | 未识别渠道 |

## 状态生命周期

```
┌─────────┐     ┌─────────────┐     ┌──────────┐     ┌──────────┐
│ created │ ──▶ │ in_progress │ ──▶ │ paused   │ ──▶ │ completed│
└─────────┘     └─────────────┘     └──────────┘     └──────────┘
     │                │                  │                │
     │                │                  │                │
     ▼                ▼                  ▼                ▼
┌─────────┐     ┌─────────────┐     ┌──────────┐     ┌──────────┐
│ expired │     │ interrupted │     │ resumed  │     │ archived │
└─────────┘     └─────────────┘     └──────────┘     └──────────┘
```

## 自动保存触发点

### 关键交互节点 (每5次触发)

系统自动计数器追踪对话轮次，每达到5次关键交互时触发保存：
- 用户提问后
- 助手完成重要步骤后
- 生成文件后

### 明确任务边界

- 完成一个子任务
- 生成确认的文件
- 用户说"暂停"、"先到这里"、"够了"

### 主动健康检查

- 检测会话可能中断的信号
- 会话即将超时
- 用户切换渠道

## 恢复流程状态机

```
检查状态
    │
    ▼
┌───────────┐
│ 有状态?   │──否──▶ 引导新会话
└───────────┘
    │
    是
    │
    ▼
┌───────────────┐
│ 已过期(>7天)?│──是──▶ 询问是否仍要恢复
└───────────────┘
    │
    否
    │
    ▼
┌───────────────┐
│ 多状态冲突?  │──是──▶ 让用户选择
└───────────────┘
    │
    否
    │
    ▼
显示恢复摘要
    │
    ▼
用户确认 ──是──▶ 加载上下文
    │
    否
    │
    ▼
开始新会话
```

## 产物类型枚举

| 类型 | 描述 | 文件扩展名 |
|------|------|-----------|
| `code` | 源代码 | .py, .js, .ts, .go, .java, ... |
| `data` | 数据文件 | .csv, .json, .xlsx, .db, ... |
| `document` | 文档 | .md, .docx, .pdf, .txt, ... |
| `image` | 图片 | .png, .jpg, .svg, .gif, ... |
| `config` | 配置文件 | .yaml, .toml, .ini, .env, ... |
| `archive` | 归档 | .zip, .tar, .gz, ... |
| `other` | 其他 | * |
