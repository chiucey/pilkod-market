# 接口规范文档

## 标准数据格式

所有模块间通信必须使用以下标准格式：

```json
{
    "id": "UUID-v4",
    "type": "数据类型",
    "source_module": "来源模块名称",
    "target_module": "目标模块名称（可选）",
    "version": "1.0.0",
    "timestamp": "ISO8601格式",
    "payload": {}
}
```

## 错误响应格式

```json
{
    "id": "UUID-v4",
    "type": "error",
    "source_module": "来源模块",
    "version": "1.0.0",
    "timestamp": "ISO8601",
    "payload": {
        "code": "ERROR_CODE",
        "message": "错误描述",
        "details": {}
    }
}
```

## 认证接口

### 用户登录

```
POST /api/auth/login
```

**请求：**
```json
{
    "username": "string",
    "password": "string"
}
```

**响应：**
```json
{
    "id": "uuid",
    "type": "auth_response",
    "source_module": "user_auth",
    "version": "1.0.0",
    "timestamp": "2024-01-01T00:00:00Z",
    "payload": {
        "token": "jwt_token",
        "user_id": "string",
        "expires_at": "ISO8601"
    }
}
```

## 内容管理接口

### 获取内容列表

```
GET /api/content/list
```

**响应：**
```json
{
    "id": "uuid",
    "type": "content_list",
    "source_module": "content_management",
    "version": "1.0.0",
    "timestamp": "2024-01-01T00:00:00Z",
    "payload": {
        "items": [],
        "total": 0,
        "page": 1,
        "page_size": 20
    }
}
```

## 日志记录接口

### 记录日志

```
POST /api/log/record
```

**请求：**
```json
{
    "level": "INFO|WARN|ERROR",
    "module": "模块名",
    "message": "日志内容",
    "context": {}
}
```

## 版本兼容性

| 接口版本 | 状态 | 兼容版本 |
|---------|------|---------|
| 1.0.0 | 当前 | - |
