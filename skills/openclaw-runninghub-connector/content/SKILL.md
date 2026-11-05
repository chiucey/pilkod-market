---
name: openclaw-runninghub-connector
description: OpenClaw 与 RunningHub 自动连接器。当用户要求连接 OpenClaw 和 RunningHub、配置 API key、搭建 AI 工作流、或需要自动创建 RunningHub 工作流时使用。
---

# OpenClaw + RunningHub 自动连接器

## 功能概述

本技能实现 OpenClaw 和 RunningHub 的自动连接，用户只需提供 RunningHub API key 即可一键连接，并可通过自然语言描述自动在 RunningHub 平台搭建 AI 工作流。

## 核心能力

1. **自动连接**：一键连接 OpenClaw 和 RunningHub 平台
2. **API Key 管理**：安全存储和管理 RunningHub API key
3. **工作流自动搭建**：根据自然语言需求自动构建 RunningHub 工作流
4. **插件自动配置**：自动安装和配置所需插件

## 使用流程

### 步骤 1：获取 RunningHub API Key

用户需要从 RunningHub 平台获取 API key：
1. 登录 RunningHub 平台
2. 进入个人设置/API 设置
3. 创建新的 API Key
4. 将 API Key 提供给本技能

### 步骤 2：建立连接

使用 OpenClaw CLI 建立连接：

```bash
# 连接到 RunningHub
openclaw runninghub connect --api-key <USER_API_KEY>

# 验证连接状态
openclaw runninghub status
```

### 步骤 3：自动搭建工作流

用户描述工作流需求，技能将：
1. 解析需求并确定所需节点类型
2. 查询 RunningHub 可用节点库
3. 构建工作流 JSON 配置
4. 通过 API 创建工作流

## 工作流自动搭建指南

### 支持的节点类型

| 节点类型 | 用途 | 典型场景 |
|---------|------|---------|
| Trigger | 工作流触发器 | 定时触发、API 调用触发 |
| LLM | 大语言模型 | 文本生成、对话、总结 |
| Image | 图像处理 | 生成、编辑、风格转换 |
| Audio | 音频处理 | TTS、语音识别 |
| Video | 视频处理 | 生成、剪辑 |
| Webhook | 外部集成 | API 调用、数据同步 |

### 工作流构建规则

1. **入口点**：工作流必须以 Trigger 节点开始
2. **节点连接**：通过节点 ID 建立连接关系
3. **参数配置**：为每个节点配置必要参数
4. **错误处理**：设置适当的错误处理和重试策略

## RunningHub API 参考

### 基础信息

- **API 基础地址**：`https://api.runninghub.com`
- **认证方式**：Bearer Token (API Key)

### 核心 API 端点

```
# 获取工作流列表
GET /api/v1/workflows

# 创建新工作流
POST /api/v1/workflows

# 获取工作流详情
GET /api/v1/workflows/{workflow_id}

# 更新工作流
PUT /api/v1/workflows/{workflow_id}

# 删除工作流
DELETE /api/v1/workflows/{workflow_id}

# 获取可用节点列表
GET /api/v1/nodes

# 执行工作流
POST /api/v1/workflows/{workflow_id}/run

# 获取节点执行结果
GET /api/v1/workflows/{workflow_id}/runs/{run_id}
```

### 工作流创建示例

```json
{
  "name": "AI 图像生成工作流",
  "description": "使用 LLM 生成图像提示词并创建图像",
  "nodes": [
    {
      "id": "trigger_1",
      "type": "trigger",
      "config": {
        "trigger_type": "manual"
      }
    },
    {
      "id": "llm_1",
      "type": "llm",
      "config": {
        "model": "gpt-4",
        "prompt": "为以下主题生成一个图像描述: {{input}}"
      },
      "inputs": ["trigger_1"]
    },
    {
      "id": "image_1",
      "type": "image",
      "config": {
        "model": "dall-e-3",
        "prompt": "{{llm_1.output}}"
      },
      "inputs": ["llm_1"]
    }
  ],
  "connections": [
    {"from": "trigger_1", "to": "llm_1"},
    {"from": "llm_1", "to": "image_1"}
  ]
}
```

## OpenClaw 集成

### 安装 OpenClaw

```bash
# macOS
brew install openclaw/tap/openclaw

# Linux
curl -fsSL https://get.openclaw.io | sh

# 验证安装
openclaw --version
```

### OpenClaw 命令

```bash
# 查看已连接平台
openclaw status

# 连接 RunningHub
openclaw runninghub connect --api-key <KEY>

# 断开连接
openclaw runninghub disconnect

# 查看 RunningHub 状态
openclaw runninghub status

# 列出可用节点
openclaw runninghub nodes list

# 创建工作流
openclaw runninghub workflow create --file workflow.json

# 执行工作流
openclaw runninghub workflow run <workflow_id>
```

## 常见工作流模板

### 1. 文本到图像生成

```
Trigger → LLM(优化提示词) → Image(生成图像) → Output
```

### 2. 批量内容处理

```
Trigger → Loop → LLM(处理) → Output → Loop End
```

### 3. 多模态管道

```
Trigger → LLM → Image → Audio → Webhook → Output
```

### 4. 条件分支工作流

```
Trigger → Condition → [True Path] → LLM → Output
                      → [False Path] → Another LLM → Output
```

## 错误处理

### 连接错误

| 错误码 | 含义 | 解决方案 |
|-------|------|---------|
| AUTH_001 | API Key 无效 | 检查并重新提供有效的 API Key |
| AUTH_002 | API Key 已过期 | 在 RunningHub 更新 API Key |
| CONN_001 | 网络连接失败 | 检查网络连接和代理设置 |
| CONN_002 | 服务不可用 | 等待服务恢复或联系支持 |

### 工作流错误

| 错误码 | 含义 | 解决方案 |
|-------|------|---------|
| WF_001 | 节点配置无效 | 检查节点参数配置 |
| WF_002 | 节点类型不支持 | 确认节点类型可用 |
| WF_003 | 连接关系错误 | 检查节点间的连接 |
| EXEC_001 | 执行超时 | 增加超时时间或简化工作流 |

## 安全注意事项

1. **API Key 安全**：不要在代码中硬编码 API Key，使用环境变量
2. **数据传输**：所有 API 调用使用 HTTPS
3. **日志记录**：避免记录敏感的请求/响应数据
4. **权限控制**：使用最小权限原则

## 参考资源

详细文档和示例请参阅：
- `references/api_spec.md` - RunningHub API 详细规范
- `references/workflow_templates.md` - 工作流模板库
- `scripts/connection_helper.py` - 连接辅助脚本
