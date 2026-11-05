---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: e9e0fb8e181a7dad530ffeaa1cdfd287
    PropagateID: e9e0fb8e181a7dad530ffeaa1cdfd287
    ReservedCode1: 30450220306da668c44fecd26b4bc073de9c2b01f5fa372cbd768ad94c034e3c87355e00022100dc4b2327ce835088542e25e8697857c05706b92fd4793a5a4cf36827e14b317b
    ReservedCode2: 3045022100f9703baab1b509044bcce98d964d59e145f0d9c678339950d134e1517f828bfb02203f05ac2796653dd2055f79f1cbcd9d7499b0d2392fca98adb019949fac99f280
---

# Local RAG Search

从本地知识库检索相关信息并回答用户问题。

## 触发
- RAG 搜索
- 知识库查询
- 本地搜索
- 检索

## 配置

### API
- **类型**: HTTP POST
- **地址**: http://localhost:8000/search
- **Headers**: Content-Type: application/json

### 请求参数
```json
{
  "query": "{{user_message}}",
  "top_k": 3,
  "enhance_prompt": true
}
```

### 响应解析
- **answer**: $.answer
- **sources**: $.sources

### 错误处理
- 超时: 30秒
- 重试: 2次
- 错误提示: "抱歉，知识库服务暂时不可用，请稍后再试。"

## 使用示例

**用户**: 请帮我搜索关于 OpenClaw 安装的问题

**Agent**:
```json
{
  "query": "OpenClaw 安装",
  "top_k": 3
}
```

**响应**:
```json
{
  "answer": "OpenClaw 安装步骤...",
  "sources": ["doc1.md", "doc2.md"]
}
```

## 注意事项

1. 确保本地 RAG 服务已启动 (localhost:8000)
2. 知识库文件应放在指定目录
3. 支持中文检索
