# 配置文件参数表

## 配置文件结构

```json
{
  "environment": "production",
  "oauth": {},
  "api": {},
  "upload": {},
  "log_level": "INFO",
  "cache_dir": "~/.tiktok_config/cache"
}
```

## OAuth 配置

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `client_id` | string | 是 | - | 应用 Client Key |
| `client_secret` | string | 是 | - | 应用 Client Secret |
| `redirect_uri` | string | 是 | - | 回调地址 |
| `auth_url` | string | 否 | 见下方 | 授权 URL |
| `token_url` | string | 否 | 见下方 | Token URL |
| `scopes` | array | 否 | 默认列表 | 权限范围 |

### 默认 URLs

```python
auth_url = "https://open.tiktokapis.com/oauth/authorize/"
token_url = "https://open.tiktokapis.com/oauth/token/"
refresh_url = "https://open.tiktokapis.com/oauth/token/refresh/"
```

### 权限范围

| Scope | 说明 |
|-------|------|
| `miniapp.app.info` | 应用信息读取 |
| `miniapp.app.update` | 应用信息更新 |
| `miniapp.package` | 包管理 |
| `miniapp.review` | 审核管理 |
| `miniapp.ad` | 广告位管理 |

## API 配置

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `base_url` | string | 否 | 见下方 | API Base URL |
| `timeout` | int | 否 | 30 | 请求超时（秒） |
| `max_retries` | int | 否 | 3 | 最大重试次数 |
| `retry_delay` | int | 否 | 5 | 重试间隔（秒） |

### 默认值

```python
base_url = "https://open.tiktokapis.com/v2/"
timeout = 30
max_retries = 3
retry_delay = 5
```

## 上传配置

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `chunk_size` | int | 否 | 5242880 | 分块大小（字节） |
| `max_retries` | int | 否 | 3 | 最大重试次数 |
| `max_file_size` | int | 否 | 524288000 | 最大文件大小（字节） |

### 默认值

```python
chunk_size = 5 * 1024 * 1024  # 5MB
max_retries = 3
max_file_size = 500 * 1024 * 1024  # 500MB
```

### 推荐配置

| 文件大小 | 推荐 chunk_size |
|----------|-----------------|
| < 10MB | 1MB |
| 10-100MB | 5MB |
| > 100MB | 10MB |

## 环境配置

| 值 | 说明 |
|----|------|
| `development` | 开发环境 |
| `production` | 生产环境 |

## 日志配置

| 值 | 说明 |
|----|------|
| `DEBUG` | 详细日志 |
| `INFO` | 一般信息 |
| `WARNING` | 警告 |
| `ERROR` | 错误 |

## 环境变量覆盖

| 变量名 | 对应配置 |
|--------|----------|
| `TIKTOK_CLIENT_ID` | oauth.client_id |
| `TIKTOK_CLIENT_SECRET` | oauth.client_secret |
| `TIKTOK_REDIRECT_URI` | oauth.redirect_uri |
| `TIKTOK_ENVIRONMENT` | environment |
| `TIKTOK_BASE_URL` | api.base_url |
| `TIKTOK_LOG_LEVEL` | log_level |

## 完整示例配置

```json
{
  "environment": "production",
  "oauth": {
    "client_id": "your_client_id_here",
    "client_secret": "your_client_secret_here",
    "redirect_uri": "https://your-app.com/callback",
    "auth_url": "https://open.tiktokapis.com/oauth/authorize/",
    "token_url": "https://open.tiktokapis.com/oauth/token/",
    "scopes": [
      "miniapp.app.info",
      "miniapp.app.update",
      "miniapp.package",
      "miniapp.review",
      "miniapp.ad"
    ]
  },
  "api": {
    "base_url": "https://open.tiktokapis.com/v2/",
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 5
  },
  "upload": {
    "chunk_size": 5242880,
    "max_retries": 3,
    "max_file_size": 524288000
  },
  "log_level": "INFO",
  "cache_dir": "~/.tiktok_config/cache"
}
```

## 配置文件位置

| 平台 | 路径 |
|------|------|
| Windows | `C:\Users\{username}\.tiktok_config\` |
| macOS/Linux | `~/.tiktok_config/` |
| 自定义 | 传入 `config_dir` 参数 |

## 配置优先级

1. 环境变量（最高）
2. 传入的配置参数
3. 配置文件
4. 默认值（最低）
