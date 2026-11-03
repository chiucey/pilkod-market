# 百度网盘 OAuth2.0 授权配置指南

## 第一步：创建百度开发者应用

1. 访问 [百度网盘开放平台](https://pan.baidu.com/union/) → 登录百度账号
2. 进入「控制台」→「创建应用」
3. 选择应用类型（选择「网盘应用」或「电商工具」等）
4. 填写应用名称、描述
5. 创建后记录：**API Key** 和 **Secret Key**

## 第二步：生成授权 URL

使用 Python 脚本生成授权 URL：

```python
import urllib.parse

api_key = "YOUR_API_KEY"
redirect_uri = "oob"  # 借用页面模式，无需回调
scope = "netdisk"     # 申请网盘权限

params = {
    "client_id": api_key,
    "response_type": "code",
    "redirect_uri": redirect_uri,
    "scope": scope,
}
url = "https://openapi.baidu.com/oauth/2.0/authorize?" + urllib.parse.urlencode(params)
print(url)
```

访问输出的 URL，扫码或登录百度账号，授权后获得一个字母数字组合的 **Authorization Code**（形如：`c9a1d7f2e3f4b8d9c0e1f2a3b4c5d6e`）

## 第三步：交换 Access Token

用 Authorization Code 换取 Access Token：

```bash
curl -X POST "https://openapi.baidu.com/oauth/2.0/token" \
  -d "grant_type=authorization_code" \
  -d "code={AUTHORIZATION_CODE}" \
  -d "client_id={API_KEY}" \
  -d "client_secret={SECRET_KEY}" \
  -d "redirect_uri=oob"
```

返回示例：
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "expires_in": 2592000,
  "session_secret": "",
  "session_key": "",
  "scope": "netdisk"
}
```

## 第四步：保存配置

将 Token 写入配置（自动管理，无需手动刷新）：

```json
// ~/.openclaw/config/baidu-netdisk-auth.json
{
  "api_key": "YOUR_API_KEY",
  "secret_key": "YOUR_SECRET_KEY",
  "access_token": "...",
  "refresh_token": "...",
  "expires_at": 1735000000
}
```

## Token 自动刷新

百度网盘 Access Token 有效期约 30 天（2592000 秒）。Skill 会在 Token 过期前自动用 Refresh Token 刷新：

```bash
curl -X POST "https://openapi.baidu.com/oauth/2.0/token" \
  -d "grant_type=refresh_token" \
  -d "refresh_token={REFRESH_TOKEN}" \
  -d "client_id={API_KEY}" \
  -d "client_secret={SECRET_KEY}"
```

## 所需权限清单

在开放平台申请以下权限：
- `netdisk` — 读取用户网盘文件
- `netdisk:file` — 上传文件到用户网盘
