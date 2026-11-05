# 有道云笔记 API 参考

## 认证方式

### 1. Token 认证

适用于已登录用户，需要获取有道云开放 API Token。

**获取方式**：
1. 登录有道云笔记网页版
2. 打开开发者工具 (F12)
3. 在 Network 面板中找到任意 API 请求
4. 查看 Authorization header 获取 token

### 2. 分享链接认证

适用于访问他人分享的笔记内容。

**分享链接格式**：
```
https://note.youdao.com/sharing/embed?id={share_id}
https://note.youdao.com/share/?id={share_id}
```

## API 端点

### 获取分享信息

```
GET https://note.youdao.com/yws/api/v1/share/{share_id}
```

**响应示例**：
```json
{
  "shareId": "abc123",
  "title": "分享的笔记",
  "creator": "username",
  "createdAt": "2024-01-01T00:00:00Z",
  "fileCount": 10
}
```

### 获取分享文件列表

```
GET https://note.youdao.com/yws/api/v1/share/{share_id}/files
```

**响应示例**：
```json
{
  "files": [
    {
      "id": "file001",
      "name": "文档.md",
      "path": "/工作",
      "size": 1024,
      "modified": "2024-01-10T12:00:00Z",
      "dir": false
    },
    {
      "id": "folder001",
      "name": "项目文件夹",
      "path": "/",
      "size": 0,
      "modified": "2024-01-15T10:00:00Z",
      "dir": true
    }
  ]
}
```

### 获取文件列表 (Token 方式)

```
GET https://note.youdao.com/yws/api/v1/files
Authorization: Bearer {token}
```

### 下载文件

```
GET https://note.youdao.com/yws/api/v1/file/{file_id}
Authorization: Bearer {token}  (Token 方式需要)
```

## 错误码

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 401 | Token 过期或无效 | 重新获取 Token |
| 403 | 无权限访问 | 检查分享链接是否有效 |
| 404 | 文件或分享不存在 | 检查 ID 是否正确 |
| 429 | 请求频率限制 | 降低请求频率，等待后重试 |
| 500 | 服务器错误 | 稍后重试 |

## 速率限制

- 普通请求：每秒 10 次
- 文件下载：每秒 5 次
- 建议在批量操作时添加延迟

## 注意事项

1. **Token 有效期**：有道云 Token 通常有效期较长，但建议实现自动刷新机制
2. **分享链接有效期**：分享者可以随时取消分享
3. **文件大小限制**：单文件建议不超过 100MB
4. **网络超时**：建议设置 60 秒超时并实现重试
