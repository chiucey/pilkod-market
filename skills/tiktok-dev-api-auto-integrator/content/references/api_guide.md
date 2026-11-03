# TikTok Open API v2 开发者指南

## API 概述

TikTok Open Platform API v2 提供了对 TikTok 小程序生态的完整访问能力，支持：
- OAuth 2.0 授权
- 应用管理
- 游戏包上传
- 审核状态查询
- 广告位管理

## 基础信息

| 项目 | 值 |
|------|-----|
| Base URL | `https://open.tiktokapis.com/v2/` |
| 协议 | HTTPS |
| 数据格式 | JSON |
| 字符编码 | UTF-8 |

## API 端点

### OAuth 端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `/oauth/authorize/` | GET | 获取用户授权 |
| `/oauth/token/` | POST | 获取访问令牌 |
| `/oauth/token/refresh/` | POST | 刷新访问令牌 |

### 应用管理端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `/miniapp/app/create/` | POST | 创建小程序 |
| `/miniapp/app/get/` | GET | 获取应用信息 |
| `/miniapp/app/update/` | POST | 更新应用信息 |
| `/miniapp/app/list/` | GET | 获取应用列表 |
| `/miniapp/app/delete/` | POST | 删除应用 |

### 包管理端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `/miniapp/package/upload/init/` | POST | 初始化上传 |
| `/miniapp/package/upload/chunk/` | POST | 上传分块 |
| `/miniapp/package/upload/complete/` | POST | 完成上传 |
| `/miniapp/package/get/` | GET | 获取包信息 |

### 审核端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `/miniapp/review/submit/` | POST | 提交审核 |
| `/miniapp/review/get/` | GET | 查询审核状态 |

### 广告位端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `/miniapp/ad/slot/create/` | POST | 创建广告位 |
| `/miniapp/ad/slot/get/` | GET | 获取广告位信息 |
| `/miniapp/ad/slot/list/` | GET | 获取广告位列表 |

## 请求格式

### 请求头

```
Authorization: Bearer {access_token}
Content-Type: application/json
```

### 请求体

```json
{
  "app_id": "your_app_id",
  "package_version": "1.0.0",
  "changelog": "Bug fixes and improvements"
}
```

## 响应格式

### 成功响应

```json
{
  "data": {
    "app_id": "123456789",
    "title": "My Game",
    "status": "approved"
  },
  "error": null
}
```

### 错误响应

```json
{
  "data": null,
  "error": {
    "code": "invalid_parameter",
    "message": "Invalid app_id format"
  }
}
```

## 错误码

| 错误码 | 说明 |
|--------|------|
| `invalid_parameter` | 参数无效 |
| `unauthorized` | 未授权 |
| `forbidden` | 权限不足 |
| `not_found` | 资源不存在 |
| `rate_limit` | 请求频率超限 |
| `server_error` | 服务器错误 |

## 限流规则

| 接口类型 | 限制 |
|----------|------|
| 读接口 | 1000次/分钟 |
| 写接口 | 100次/分钟 |
| 上传接口 | 10次/分钟 |

## 最佳实践

1. **实现重试机制**：遇到限流时自动等待重试
2. **使用分块上传**：大文件使用分块上传支持断点续传
3. **Token 刷新**：定期检查 Token 过期时间并刷新
4. **错误处理**：实现完整的错误处理和日志记录
5. **请求签名**：敏感操作使用签名验证
