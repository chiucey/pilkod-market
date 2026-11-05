# OAuth 2.0 授权教程

## 授权流程概述

```
用户 → 授权页面 → 授权码 → 换取Token → API调用
```

## 授权步骤

### 1. 获取授权 URL

构造授权 URL：

```
https://open.tiktokapis.com/oauth/authorize/
  ?client_id=YOUR_CLIENT_ID
  &redirect_uri=YOUR_REDIRECT_URI
  &scope=miniapp.app.info miniapp.package
  &response_type=code
  &state=RANDOM_STATE
```

### 2. 用户授权

用户访问授权 URL 并同意授权。

### 3. 获取授权码

授权后，TikTok 会重定向到您的回调 URL：

```
https://your-app.com/callback?code=AUTH_CODE&state=RANDOM_STATE
```

### 4. 换取访问令牌

```python
import requests

def exchange_code_for_token(code, client_id, client_secret, redirect_uri):
    url = "https://open.tiktokapis.com/oauth/token/"

    data = {
        "client_key": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }

    response = requests.post(url, data=data)
    return response.json()
```

### 5. 使用访问令牌

```python
headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(
    "https://open.tiktokapis.com/v2/miniapp/app/get/",
    headers=headers,
    params={"app_id": "123456789"}
)
```

## Token 类型

| Token 类型 | 有效期 | 用途 |
|------------|--------|------|
| access_token | 24小时 | API 调用 |
| refresh_token | 30天 | 刷新 access_token |

## Token 刷新

```python
def refresh_token(refresh_token, client_id, client_secret):
    url = "https://open.tiktokapis.com/oauth/token/refresh/"

    data = {
        "client_key": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(url, data=data)
    return response.json()
```

## 权限范围 (Scopes)

| Scope | 说明 |
|-------|------|
| `miniapp.app.info` | 读取应用信息 |
| `miniapp.app.update` | 更新应用信息 |
| `miniapp.package` | 上传游戏包 |
| `miniapp.review` | 提交和查询审核 |
| `miniapp.ad` | 广告位管理 |

## PKCE 扩展 (推荐)

对于客户端应用，推荐使用 PKCE 扩展增强安全性：

```python
import secrets
import hashlib
import base64

def generate_pkce_pair():
    # 生成随机code verifier
    code_verifier = secrets.token_urlsafe(64)

    # 生成code challenge
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip('=')

    return code_verifier, code_challenge

# 授权URL中添加 code_challenge 和 code_challenge_method
# &code_challenge=YOUR_CODE_CHALLENGE&code_challenge_method=S256
```

## 安全建议

1. **保护 client_secret**：不要暴露在客户端代码中
2. **使用 HTTPS**：所有请求必须使用 HTTPS
3. **验证 state 参数**：防止 CSRF 攻击
4. **Token 安全存储**：加密存储刷新令牌
5. **最小权限**：只申请必要的权限范围
