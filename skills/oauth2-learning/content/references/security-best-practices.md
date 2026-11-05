# OAuth2 安全最佳实践

## 核心安全原则

### 1. 传输层安全

**必须使用HTTPS**
- 所有OAuth2通信必须通过HTTPS
- 强制使用TLS 1.2+
- 禁用弱密码套件

### 2. 客户端安全

#### 客户端密钥管理

```python
# 错误示例：硬编码密钥
CLIENT_SECRET = "my_secret_key_123"  # 绝对不要这样做

# 正确做法：环境变量
import os
CLIENT_SECRET = os.environ.get("OAUTH_CLIENT_SECRET")

# 更安全：密钥管理服务
from aws_secrets_manager import get_secret
CLIENT_SECRET = get_secret("oauth-client-secret")
```

#### 令牌存储安全

| 应用类型 | 推荐存储 | 注意事项 |
|----------|----------|----------|
| 后端Web应用 | 服务器内存/Session | 不暴露给客户端 |
| SPA | HttpOnly Cookie | 配合CSRF保护 |
| 移动App | Keychain(iOS)/Keystore(Android) | 使用系统安全存储 |

```javascript
// SPA安全存储示例（使用httpOnly cookie）
// 服务端设置Cookie
res.cookie('access_token', token, {
  httpOnly: true,    // 防止XSS访问
  secure: true,      // 仅HTTPS
  sameSite: 'lax',   // CSRF保护
  maxAge: 3600000    // 1小时
});
```

### 3. CSRF防护

**State参数必须使用**

```python
import secrets

def initiate_auth():
    state = secrets.token_urlsafe(32)
    # 存储state到session
    session['oauth_state'] = state

    return redirect(
        f"https://auth.example.com/authorize"
        f"?state={state}"
        # ... 其他参数
    )

def callback(code, state):
    # 验证state
    if state != session.get('oauth_state'):
        abort(400, "Invalid state parameter")

    # 清除state
    session.pop('oauth_state', None)

    # 继续处理...
```

### 4. PKCE强制使用

**以下情况必须使用PKCE：**
- 单页应用（SPA）
- 原生移动应用
- 桌面应用
- 任何没有安全后端的客户端

```python
# PKCE实现
import hashlib
import base64
import secrets

def generate_pkce_pair():
    code_verifier = secrets.token_urlsafe(64)  # 43-128字符
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b'=').decode()
    return code_verifier, code_challenge

# 使用
verifier, challenge = generate_pkce_pair()
# 保存verifier，用于后续令牌交换
session['pkce_verifier'] = verifier
```

### 5. 令牌安全

#### Access Token最佳实践

```python
# 令牌请求示例
response = requests.post(
    "https://auth.example.com/token",
    data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
        # 最小化scope请求
        "scope": "read"  # 只请求需要的权限
    }
)

# 验证令牌
def validate_token(token):
    response = requests.get(
        "https://auth.example.com/userinfo",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.status_code == 200
```

#### 刷新令牌安全

```python
# 刷新令牌最佳实践
class TokenManager:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def refresh_if_needed(self, token_info):
        # 检查是否即将过期（提前5分钟刷新）
        if self._is_expiring_soon(token_info):
            return self._refresh_token(token_info['refresh_token'])
        return token_info

    def _refresh_token(self, refresh_token):
        response = requests.post(
            "https://auth.example.com/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                # 可选：限制scope
                "scope": "read"
            }
        )
        return response.json()
```

### 6. Redirect URI安全

#### 严格配置白名单

```python
# 服务端验证redirect_uri
ALLOWED_REDIRECT_URIS = [
    "https://app.example.com/callback",
    "https://staging.example.com/callback"
]

def validate_redirect_uri(uri):
    if uri not in ALLOWED_REDIRECT_URIS:
        raise ValueError(f"Invalid redirect_uri: {uri}")
    return True
```

#### 防止重定向攻击

```python
# 不允许的情况
# ❌ http://localhost/callback (在生产环境)
# ❌ https://evil.com/callback
# ❌ https://app.example.com.corp.evil.com/callback

# 允许的情况
# ✅ https://app.example.com/callback
# ✅ https://app.example.com/api/oauth/callback
```

### 7. Scope控制

#### 最小权限原则

```python
# 过度授权 - 不推荐
scope = "read write delete admin"  # 请求所有权限

# 最小权限 - 推荐
scope = "read"  # 只请求需要的权限

# 动态scope请求
def get_required_scopes(action):
    scopes = {
        "view_profile": "openid profile",
        "send_email": "openid profile email",
        "access_calendar": "openid profile calendar"
    }
    return scopes.get(action, "openid profile")
```

### 8. 令牌撤销

```python
# 实现登出功能
def revoke_tokens(access_token, refresh_token):
    # 撤销access token
    requests.post(
        "https://auth.example.com/revoke",
        data={"token": access_token}
    )

    # 撤销refresh token
    if refresh_token:
        requests.post(
            "https://auth.example.com/revoke",
            data={"token": refresh_token}
        )

    # 清除本地存储
    clear_local_tokens()
```

### 9. 日志与监控

```python
import logging

logger = logging.getLogger("oauth2")

# 记录关键事件
logger.info("OAuth2 authorization initiated", extra={
    "client_id": client_id,
    "scope": requested_scope
})

logger.warning("OAuth2 authorization denied", extra={
    "reason": error,
    "client_id": client_id
})

logger.error("Token exchange failed", extra={
    "error": error_description,
    "client_id": client_id
})
```

### 10. 安全检查清单

**部署前检查：**
- [ ] 使用HTTPS
- [ ] 客户端密钥在环境变量或密钥服务
- [ ] redirect_uri为精确白名单
- [ ] 实现state参数验证
- [ ] SPA和移动App使用PKCE
- [ ] 令牌存储安全（HttpOnly Cookie或系统Keychain）
- [ ] 实现CSRF保护
- [ ] 令牌过期前主动刷新
- [ ] 实现登出和令牌撤销
- [ ] 记录安全日志
- [ ] 定期更新依赖库
