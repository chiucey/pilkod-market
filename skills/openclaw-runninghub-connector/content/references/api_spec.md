# RunningHub API 详细规范

## 认证

所有 API 请求都需要在 Header 中包含 API Key：

```
Authorization: Bearer <YOUR_API_KEY>
Content-Type: application/json
```

## 端点详细说明

### 1. 工作流管理

#### 获取工作流列表

```
GET /api/v1/workflows
```

**Query 参数：**
| 参数 | 类型 | 描述 |
|-----|------|------|
| page | int | 页码，默认 1 |
| limit | int | 每页数量，默认 20 |
| status | string | 筛选状态：active, paused, draft |

**响应示例：**
```json
{
  "success": true,
  "data": {
    "workflows": [
      {
        "id": "wf_123456",
        "name": "AI 图像生成",
        "description": "使用 AI 生成高质量图像",
        "status": "active",
        "node_count": 4,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "total_pages": 3
    }
  }
}
```

#### 创建工作流

```
POST /api/v1/workflows
```

**请求体：**
```json
{
  "name": "工作流名称",
  "description": "工作流描述（可选）",
  "nodes": [...],
  "connections": [...]
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "workflow": {
      "id": "wf_789012",
      "name": "工作流名称",
      "status": "draft",
      "created_at": "2024-01-15T10:35:00Z"
    }
  }
}
```

#### 获取工作流详情

```
GET /api/v1/workflows/{workflow_id}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "workflow": {
      "id": "wf_789012",
      "name": "AI 图像生成",
      "description": "使用 AI 生成高质量图像",
      "status": "active",
      "nodes": [...],
      "connections": [...],
      "created_at": "2024-01-15T10:35:00Z",
      "updated_at": "2024-01-15T11:00:00Z"
    }
  }
}
```

#### 更新工作流

```
PUT /api/v1/workflows/{workflow_id}
```

#### 删除工作流

```
DELETE /api/v1/workflows/{workflow_id}
```

### 2. 节点管理

#### 获取可用节点列表

```
GET /api/v1/nodes
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "nodes": [
      {
        "type": "llm",
        "name": "大语言模型",
        "description": "调用大语言模型进行文本处理",
        "icon": "brain",
        "config_schema": {
          "model": {
            "type": "select",
            "options": ["gpt-4", "gpt-3.5-turbo", "claude-3"],
            "required": true
          },
          "temperature": {
            "type": "number",
            "min": 0,
            "max": 2,
            "default": 0.7
          }
        },
        "inputs": ["text"],
        "outputs": ["text"]
      },
      {
        "type": "image",
        "name": "图像生成",
        "description": "使用 AI 模型生成图像",
        "icon": "image",
        "config_schema": {
          "model": {
            "type": "select",
            "options": ["dall-e-3", "stable-diffusion", "midjourney"],
            "required": true
          },
          "size": {
            "type": "select",
            "options": ["1024x1024", "1792x1024", "1024x1792"],
            "default": "1024x1024"
          },
          "quality": {
            "type": "select",
            "options": ["standard", "hd"],
            "default": "standard"
          }
        },
        "inputs": ["prompt"],
        "outputs": ["image_url"]
      }
    ]
  }
}
```

#### 获取节点模板

```
GET /api/v1/nodes/templates
```

返回预定义的工作流模板列表。

### 3. 执行管理

#### 执行工作流

```
POST /api/v1/workflows/{workflow_id}/run
```

**请求体：**
```json
{
  "inputs": {
    "trigger_var_1": "输入值",
    "trigger_var_2": "另一个值"
  },
  "async": false
}
```

**响应示例（同步）：**
```json
{
  "success": true,
  "data": {
    "run_id": "run_456",
    "status": "completed",
    "outputs": {
      "final_output": "结果值"
    },
    "execution_time": 5.2
  }
}
```

**响应示例（异步）：**
```json
{
  "success": true,
  "data": {
    "run_id": "run_456",
    "status": "queued",
    "poll_url": "/api/v1/workflows/wf_123/runs/run_456"
  }
}
```

#### 获取执行状态

```
GET /api/v1/workflows/{workflow_id}/runs/{run_id}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "run": {
      "id": "run_456",
      "status": "completed",
      "started_at": "2024-01-15T10:40:00Z",
      "completed_at": "2024-01-15T10:45:00Z",
      "execution_time": 5.2,
      "node_results": {
        "trigger_1": {
          "status": "completed",
          "output": {}
        },
        "llm_1": {
          "status": "completed",
          "output": {
            "text": "生成的文本"
          }
        }
      },
      "final_output": {}
    }
  }
}
```

#### 取消执行

```
DELETE /api/v1/workflows/{workflow_id}/runs/{run_id}
```

### 4. 变量管理

#### 获取工作流变量

```
GET /api/v1/workflows/{workflow_id}/variables
```

#### 创建/更新变量

```
POST /api/v1/workflows/{workflow_id}/variables
PUT /api/v1/workflows/{workflow_id}/variables/{variable_id}
```

### 5. Webhook 配置

#### 获取 Webhook 配置

```
GET /api/v1/workflows/{workflow_id}/webhooks
```

#### 创建 Webhook

```
POST /api/v1/workflows/{workflow_id}/webhooks
```

**请求体：**
```json
{
  "trigger_type": "webhook",
  "secret": "webhook_secret_key",
  "events": ["workflow.started", "workflow.completed", "workflow.failed"]
}
```

## 错误响应格式

所有错误响应遵循以下格式：

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```

### 错误码说明

| 错误码 | HTTP 状态码 | 描述 |
|-------|------------|------|
| AUTH_001 | 401 | API Key 无效 |
| AUTH_002 | 401 | API Key 已过期 |
| AUTH_003 | 403 | 权限不足 |
| RESOURCE_001 | 404 | 工作流不存在 |
| RESOURCE_002 | 404 | 节点不存在 |
| VALIDATION_001 | 400 | 请求参数验证失败 |
| VALIDATION_002 | 400 | 工作流结构无效 |
| EXECUTION_001 | 500 | 执行失败 |
| EXECUTION_002 | 408 | 执行超时 |
| RATE_LIMIT | 429 | 请求频率超限 |

## 速率限制

- 默认限制：100 请求/分钟
- 工作流执行：10 并发执行
- 超出限制返回 `429 Too Many Requests`

## SDK 示例

### Python

```python
import requests

class RunningHubClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.runninghub.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def create_workflow(self, name: str, description: str,
                        nodes: list, connections: list) -> dict:
        url = f"{self.base_url}/api/v1/workflows"
        payload = {
            "name": name,
            "description": description,
            "nodes": nodes,
            "connections": connections
        }
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    def run_workflow(self, workflow_id: str, inputs: dict) -> dict:
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}/run"
        payload = {"inputs": inputs, "async": True}
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    def get_nodes(self) -> list:
        url = f"{self.base_url}/api/v1/nodes"
        response = requests.get(url, headers=self.headers)
        return response.json().get("data", {}).get("nodes", [])
```

### JavaScript/TypeScript

```typescript
class RunningHubClient {
  private apiKey: string;
  private baseUrl = "https://api.runninghub.com";

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  private getHeaders(): HeadersInit {
    return {
      "Authorization": `Bearer ${this.apiKey}`,
      "Content-Type": "application/json"
    };
  }

  async createWorkflow(
    name: string,
    description: string,
    nodes: any[],
    connections: any[]
  ): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/workflows`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ name, description, nodes, connections })
    });
    return response.json();
  }

  async runWorkflow(workflowId: string, inputs: object): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/workflows/${workflowId}/run`,
      {
        method: "POST",
        headers: this.getHeaders(),
        body: JSON.stringify({ inputs, async: true })
      }
    );
    return response.json();
  }

  async getNodes(): Promise<any[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/nodes`, {
      headers: this.getHeaders()
    });
    const data = await response.json();
    return data.data?.nodes || [];
  }
}
```
