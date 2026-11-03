# OpenClaw Memory System - API 文档

## 基础信息

**基础 URL**: `http://localhost:37778`

---

## API 端点

### 健康检查

**GET** `/api/health`

检查服务状态。

**响应示例**:
```json
{
  "status": "ok",
  "timestamp": "2026-03-30T08:00:00.000Z"
}
```

---

### 统计信息

**GET** `/api/stats`

获取系统统计信息。

**响应示例**:
```json
{
  "sessions": 10,
  "observations": 150,
  "summaries": 10,
  "recentSessions": [
    {
      "session_key": "abc123",
      "started_at": "2026-03-30T07:00:00.000Z",
      "summary": "完成了认证功能开发"
    }
  ]
}
```

---

### 会话列表

**GET** `/api/sessions`

获取所有会话列表（最近 50 条）。

**响应示例**:
```json
[
  {
    "id": 1,
    "session_key": "abc123",
    "started_at": "2026-03-30T07:00:00.000Z",
    "ended_at": "2026-03-30T08:00:00.000Z",
    "summary": "完成了认证功能开发",
    "token_count": 4000
  }
]
```

---

### 会话详情

**GET** `/api/sessions/:id`

获取单个会话详情。

**参数**:
- `id` (路径参数) - 会话 ID

**响应示例**:
```json
{
  "id": 1,
  "session_key": "abc123",
  "started_at": "2026-03-30T07:00:00.000Z",
  "ended_at": "2026-03-30T08:00:00.000Z",
  "summary": "完成了认证功能开发",
  "token_count": 4000
}
```

---

### 观察列表

**GET** `/api/observations`

获取所有观察记录（最近 100 条）。

**响应示例**:
```json
[
  {
    "id": 1,
    "session_id": 1,
    "tool_name": "read",
    "tool_input": "{\"path\": \"/workspace/file.txt\"}",
    "tool_output": "文件内容...",
    "observation_type": "file_read",
    "concept_tags": "file,read,workspace",
    "importance_score": 0.8,
    "created_at": "2026-03-30T07:30:00.000Z"
  }
]
```

---

### 搜索

**POST** `/api/search`

全文搜索观察记录。

**请求体**:
```json
{
  "query": "认证功能",
  "type": "text"
}
```

**响应示例**:
```json
{
  "query": "认证功能",
  "results": [
    {
      "id": 1,
      "session_id": 1,
      "session_key": "abc123",
      "tool_name": "edit",
      "tool_input": "修改 auth.js 添加 JWT 认证",
      "observation_type": "code_change",
      "importance_score": 0.9,
      "created_at": "2026-03-30T07:30:00.000Z"
    }
  ]
}
```

---

## 错误响应

**404 Not Found**:
```json
{
  "error": "Not found"
}
```

**500 Internal Server Error**:
```json
{
  "error": "错误信息"
}
```

---

## 使用示例

### cURL

```bash
# 健康检查
curl http://localhost:37778/api/health

# 获取统计
curl http://localhost:37778/api/stats

# 搜索
curl -X POST http://localhost:37778/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "认证功能"}'
```

### JavaScript

```javascript
// 搜索
const res = await fetch('http://localhost:37778/api/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: '认证功能' })
});
const data = await res.json();
console.log(data.results);
```

---

**版本**: 1.0.0  
**最后更新**: 2026-03-30
