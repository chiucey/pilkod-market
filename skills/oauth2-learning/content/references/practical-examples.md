# OAuth2 实战代码示例

## Python Flask实现

### 基础授权码流程

```python
from flask import Flask, redirect, request, session, jsonify
import requests
import os
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

# OAuth2配置
CONFIG = {
    "auth_url": "https://auth.example.com/authorize",
    "token_url": "https://auth.example.com/token",
    "userinfo_url": "https://auth.example.com/userinfo",
    "client_id": os.environ.get("CLIENT_ID"),
    "client_secret": os.environ.get("CLIENT_SECRET"),
    "redirect_uri": "https://yourapp.com/callback"
}

@app.route("/login")
def login():
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state

    auth_params = {
        "response_type": "code",
        "client_id": CONFIG["client_id"],
        "redirect_uri": CONFIG["redirect_uri"],
        "scope": "openid profile email",
        "state": state
    }

    auth_url = CONFIG["auth_url"] + "?" + "&".join(
        f"{k}={v}" for k, v in auth_params.items()
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    # 验证state
    state = request.args.get("state")
    if state != session.get("oauth_state"):
        return jsonify({"error": "state mismatch"}), 400

    code = request.args.get("code")
    if not code:
        return jsonify({"error": "no code provided"}), 400

    # 交换令牌
    token_response = requests.post(
        CONFIG["token_url"],
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": CONFIG["redirect_uri"],
            "client_id": CONFIG["client_id"],
            "client_secret": CONFIG["client_secret"]
        }
    )

    if token_response.status_code != 200:
        return jsonify(token_response.json()), 400

    tokens = token_response.json()
    session["access_token"] = tokens["access_token"]
    session["refresh_token"] = tokens.get("refresh_token")

    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    access_token = session.get("access_token")
    if not access_token:
        return redirect("/login")

    # 获取用户信息
    userinfo = requests.get(
        CONFIG["userinfo_url"],
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    return jsonify({
        "user": userinfo,
        "message": "Welcome to your dashboard!"
    })

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

## Node.js Express实现

### 授权码+PKCE流程

```javascript
const express = require('express');
const crypto = require('crypto');
const axios = require('axios');
const session = require('express-session');

const app = express();

app.use(session({
    secret: process.env.SESSION_SECRET,
    resave: false,
    saveUninitialized: true
}));

const CONFIG = {
    authUrl: 'https://auth.example.com/authorize',
    tokenUrl: 'https://auth.example.com/token',
    userinfoUrl: 'https://auth.example.com/userinfo',
    clientId: process.env.CLIENT_ID,
    clientSecret: process.env.CLIENT_SECRET,
    redirectUri: 'https://yourapp.com/callback'
};

// 生成PKCE参数
function generatePKCE() {
    const verifier = crypto.randomBytes(32).toString('base64url');
    const challenge = crypto
        .createHash('sha256')
        .update(verifier)
        .digest('base64url');
    return { verifier, challenge };
}

// 登录路由
app.get('/login', (req, res) => {
    const { verifier, challenge } = generatePKCE();
    const state = crypto.randomBytes(16).toString('hex');

    req.session.pkceVerifier = verifier;
    req.session.oauthState = state;

    const authParams = new URLSearchParams({
        response_type: 'code',
        client_id: CONFIG.clientId,
        redirect_uri: CONFIG.redirectUri,
        scope: 'openid profile email',
        state: state,
        code_challenge: challenge,
        code_challenge_method: 'S256'
    });

    res.redirect(`${CONFIG.authUrl}?${authParams}`);
});

// 回调路由
app.get('/callback', async (req, res) => {
    const { code, state } = req.query;

    // 验证state
    if (state !== req.session.oauthState) {
        return res.status(400).json({ error: 'state mismatch' });
    }

    try {
        // 交换令牌
        const tokenResponse = await axios.post(CONFIG.tokenUrl,
            new URLSearchParams({
                grant_type: 'authorization_code',
                code: code,
                redirect_uri: CONFIG.redirectUri,
                client_id: CONFIG.clientId,
                client_secret: CONFIG.clientSecret,
                code_verifier: req.session.pkceVerifier
            }), {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            }
        );

        const tokens = tokenResponse.data;
        req.session.accessToken = tokens.access_token;
        req.session.refreshToken = tokens.refresh_token;

        // 清除临时数据
        delete req.session.pkceVerifier;
        delete req.session.oauthState;

        res.redirect('/dashboard');
    } catch (error) {
        console.error('Token exchange failed:', error.response?.data);
        res.status(500).json({ error: 'token exchange failed' });
    }
});

// 用户信息路由
app.get('/userinfo', async (req, res) => {
    const token = req.session.accessToken;
    if (!token) {
        return res.status(401).json({ error: 'not authenticated' });
    }

    try {
        const userinfo = await axios.get(CONFIG.userinfoUrl, {
            headers: { Authorization: `Bearer ${token}` }
        });
        res.json(userinfo.data);
    } catch (error) {
        if (error.response?.status === 401) {
            // Token过期，尝试刷新
            await refreshToken(req, res);
        } else {
            res.status(500).json({ error: 'failed to get userinfo' });
        }
    }
});

// 刷新令牌
async function refreshToken(req, res) {
    const refreshToken = req.session.refreshToken;
    if (!refreshToken) {
        return res.redirect('/login');
    }

    try {
        const response = await axios.post(CONFIG.tokenUrl,
            new URLSearchParams({
                grant_type: 'refresh_token',
                refresh_token: refreshToken,
                client_id: CONFIG.clientId,
                client_secret: CONFIG.clientSecret
            }), {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            }
        );

        req.session.accessToken = response.data.access_token;
        if (response.data.refresh_token) {
            req.session.refreshToken = response.data.refresh_token;
        }

        return response.data.access_token;
    } catch (error) {
        req.session.destroy();
        return res.redirect('/login');
    }
}

app.listen(3000);
```

## GitHub OAuth2集成

```python
import requests
from flask import Flask, redirect, request, session, jsonify
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

GITHUB_CONFIG = {
    "authorize_url": "https://github.com/login/oauth/authorize",
    "token_url": "https://github.com/login/oauth/access_token",
    "api_url": "https://api.github.com",
    "client_id": os.environ.get("GITHUB_CLIENT_ID"),
    "client_secret": os.environ.get("GITHUB_CLIENT_SECRET")
}

@app.route("/login/github")
def github_login():
    params = {
        "client_id": GITHUB_CONFIG["client_id"],
        "redirect_uri": "https://yourapp.com/callback/github",
        "scope": "user:email read:user"
    }
    url = GITHUB_CONFIG["authorize_url"] + "?" + "&".join(
        f"{k}={v}" for k, v in params.items()
    )
    return redirect(url)

@app.route("/callback/github")
def github_callback():
    code = request.args.get("code")

    # 交换access_token
    response = requests.post(
        GITHUB_CONFIG["token_url"],
        data={
            "client_id": GITHUB_CONFIG["client_id"],
            "client_secret": GITHUB_CONFIG["client_secret"],
            "code": code
        },
        headers={"Accept": "application/json"}
    )

    token_data = response.json()
    access_token = token_data["access_token"]

    # 获取用户信息
    user_response = requests.get(
        f"{GITHUB_CONFIG['api_url']}/user",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user = user_response.json()

    session["github_token"] = access_token
    session["user"] = user

    return jsonify({
        "name": user.get("name"),
        "login": user.get("login"),
        "avatar": user.get("avatar_url")
    })
```

## Google OAuth2集成

```python
import google.auth.transport.requests
import google.oauth2.id_token
import requests

# 使用google-auth库
# pip install google-auth

class GoogleOAuth2:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"

    def get_auth_url(self, redirect_uri):
        return (
            f"{self.auth_url}"
            f"?client_id={self.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope=openid%20email%20profile"
            f"&access_type=offline"  # 获取refresh_token
        )

    def exchange_code(self, code, redirect_uri):
        response = requests.post(
            self.token_url,
            data={
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code"
            }
        )
        return response.json()

    def verify_id_token(self, id_token):
        """验证ID Token并获取用户信息"""
        try:
            idinfo = google.oauth2.id_token.verify_oauth2_token(
                id_token,
                google.auth.transport.requests.Request(),
                self.client_id
            )
            return idinfo
        except ValueError:
            return None

    def refresh_access_token(self, refresh_token):
        response = requests.post(
            self.token_url,
            data={
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token"
            }
        )
        return response.json()

# 使用示例
oauth2 = GoogleOAuth2(
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET")
)

# 生成授权URL
auth_url = oauth2.get_auth_url("https://yourapp.com/callback")
```

## 常见问题处理

### 1. 处理令牌过期

```python
from functools import wraps
import requests

def handle_token_expiry(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                # 尝试刷新令牌
                new_token = refresh_access_token()
                # 重试原请求
                return f(*args, **kwargs)
            raise
    return decorated

@handle_token_expiry
def get_protected_resource(token):
    response = requests.get(
        "https://api.example.com/protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()
```

### 2. 并发令牌刷新处理

```python
import threading
import time

class TokenManager:
    def __init__(self, refresh_callback):
        self.refresh_callback = refresh_callback
        self._lock = threading.Lock()
        self._token = None
        self._expires_at = 0

    def get_token(self):
        with self._lock:
            if self._is_expired():
                self._refresh()
            return self._token

    def _is_expired(self):
        return time.time() >= self._expires_at - 300  # 提前5分钟

    def _refresh(self):
        self._token, expires_in = self.refresh_callback()
        self._expires_at = time.time() + expires_in
```

### 3. 错误重试机制

```python
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retry():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
```
