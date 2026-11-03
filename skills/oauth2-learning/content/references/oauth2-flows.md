# OAuth2 授权流程详解

## 完整授权码流程时序图

```
+--------+                               +---------------+
|        |--(A)- Authorization Request ->|   Resource    |
|        |                               |     Owner     |
|        |<-(B)-- Authorization Grant ---|               |
|        |                               +---------------+
|        |
|        |                               +---------------+
|        |--(C)-- Authorization Grant -->| Authorization |
| Client |                               |     Server    |
|        |<-(D)----- Access Token -------|               |
|        |                               +---------------+
|        |
|        |                               +---------------+
|        |--(E)----- Access Token ------>|    Resource   |
|        |                               |     Server    |
|        |<-(F)--- Protected Resource ---|               |
+--------+                               +---------------+
```

## 各授权模式对比

| 模式 | 适用场景 | 安全性 | Token位置 |
|------|----------|--------|----------|
| Authorization Code | 有后端的Web应用 | 高 | 服务端交换 |
| Authorization Code + PKCE | SPA、移动App | 高 | 不经过URL |
| Implicit (已废弃) | - | 低 | URL片段 |
| Client Credentials | 服务间通信 | 中 | 请求体 |
| Password Credential | 高度可信的第一方应用 | 低 | 请求体 |

## 授权码模式完整示例

### Step 1: 准备阶段

```python
import secrets
import hashlib
import base64

# 生成state参数（防CSRF）
state = secrets.token_urlsafe(32)

# 如果使用PKCE
code_verifier = secrets.token_urlsafe(64)
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).rstrip(b'=').decode()
```

### Step 2: 构建授权URL

```python
auth_url = (
    f"https://auth.example.com/authorize"
    f"?response_type=code"
    f"&client_id={client_id}"
    f"&redirect_uri={redirect_uri}"
    f"&scope=openid profile email"
    f"&state={state}"
    # PKCE参数
    f"&code_challenge={code_challenge}"
    f"&code_challenge_method=S256"
)
```

### Step 3: 处理回调

```python
# 授权服务器回调后，URL包含code和state
# 例如: https://app.com/callback?code=abc123&state=xyz789

def handle_callback(code, state):
    # 验证state
    if state != saved_state:
        raise ValueError("State mismatch - potential CSRF attack")

    # 交换令牌
    return exchange_code_for_tokens(code)
```

### Step 4: 令牌交换

```python
import requests

def exchange_code_for_tokens(code):
    response = requests.post(
        "https://auth.example.com/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
            # PKCE
            "code_verifier": code_verifier
        }
    )
    return response.json()

# 响应示例
{
    "access_token": "eyJhbGciOiJSUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
    "scope": "openid profile email"
}
```

### Step 5: 使用Access Token

```python
def get_user_profile(access_token):
    response = requests.get(
        "https://api.example.com/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    return response.json()
```

## PKCE深入理解

### 为什么需要PKCE？

在没有后端的客户端（SPA、移动App）中：
- 无法安全存储client_secret
- 授权码可能被截获
- PKCE确保即使授权码被截获，攻击者也无法兑换

### PKCE完整流程

```
1. Client生成code_verifier (随机数)

   code_verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"

2. Client计算code_challenge

   code_challenge = BASE64URL(SHA256(code_verifier))
                  = "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"

3. 授权请求携带code_challenge

   GET /authorize?code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM
                 &code_challenge_method=S256

4. 授权服务器存储code_challenge

5. Client用code换token时，必须提供原始code_verifier

6. 授权服务器重新计算SHA256(code_verifier)，与存储的code_challenge比对
```

## 客户端凭证模式示例

适用于服务间通信：

```python
import requests

def get_service_token():
    response = requests.post(
        "https://auth.example.com/token",
        data={
            "grant_type": "client_credentials",
            "client_id": service_client_id,
            "client_secret": service_client_secret,
            "scope": "api:read api:write"
        }
    )
    return response.json()["access_token"]

# 服务间调用示例
def call_internal_api():
    token = get_service_token()
    response = requests.get(
        "https://api.example.com/internal/data",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()
```

## 令牌刷新流程

```python
def refresh_access_token(refresh_token):
    response = requests.post(
        "https://auth.example.com/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret
        }
    )
    tokens = response.json()

    # 更新存储的令牌
    save_tokens(tokens["access_token"], tokens.get("refresh_token"))
    return tokens
```

## 常见流程错误处理

```python
ERROR_RESPONSES = {
    "invalid_request": {
        "cause": "Missing required parameter or invalid format",
        "solution": "Check request parameters"
    },
    "unauthorized_client": {
        "cause": "Client not authorized for this grant type",
        "solution": "Check app registration"
    },
    "access_denied": {
        "cause": "User denied the authorization request",
        "solution": "Handle user rejection gracefully"
    },
    "invalid_grant": {
        "cause": "Authorization code or refresh token expired/revoked",
        "solution": "Re-initiate authorization flow"
    },
    "invalid_client": {
        "cause": "Client authentication failed",
        "solution": "Verify client_id and client_secret"
    }
}
```
