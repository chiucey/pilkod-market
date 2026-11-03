# OAuth2 术语表

## 核心术语

### A

**Access Token（访问令牌）**
- 由授权服务器颁发的令牌，代表用户授权客户端访问特定资源
- 通常有过期时间
- 示例：`eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...`

**Authorization Code（授权码）**
- 授权服务器生成的临时码，用于客户端后端交换访问令牌
- 单次使用，通常有效期很短（几分钟）

**Authorization Grant（授权许可）**
- 代表资源所有者授权的凭证，用于获取访问令牌
- 可以是授权码、用户名密码、客户端凭证等

**Authorization Server（授权服务器）**
- 负责验证用户身份并颁发令牌的服务器
- 可能与资源服务器是同一服务

### B

**Bearer Token（持有者令牌）**
- 只要持有令牌就可以使用，无需证明知道其他秘密
- 通过HTTP Header `Authorization: Bearer <token>` 使用

### C

**Client（客户端）**
- 希望访问用户资源的第三方应用程序
- 必须已在授权服务器注册

**Client ID（客户端ID）**
- 授权服务器为客户端应用分配的标识符
- 公开可见

**Client Secret（客户端密钥）**
- 只有客户端和授权服务器知道的秘密
- 用于验证客户端身份
- 必须安全存储，绝不能暴露给用户

**Code Challenge（代码挑战）**
- PKCE中使用的code_verifier的SHA256哈希
- 在授权请求时发送给服务器

**Code Verifier（代码验证器）**
- PKCE中使用的随机字符串
- 用于授权码交换时的验证

### D

**Dynamic Client Registration（动态客户端注册）**
- 允许客户端程序化注册自己到授权服务器
- 标准协议：RFC 7591

### G

**Grant Type（授权类型）**
- 定义的OAuth2流程类型
- 值：`authorization_code`, `client_credentials`, `refresh_token`等

### I

**ID Token（ID令牌）**
- OIDC特有的JWT格式令牌
- 包含用户身份信息（sub, name, email等）
- 可直接用于验证用户身份

### J

**JWT (JSON Web Token)**
- 一种开放标准（RFC 7519），用于安全传输信息
- 结构：`Header.Payload.Signature`
- 常用于OAuth2/OIDC的access_token和id_token

### L

**LDAP (Lightweight Directory Access Protocol)**
- 目录服务访问协议
- OAuth2可以与LDAP集成用于身份验证

### O

**OIDC (OpenID Connect)**
- 构建在OAuth2之上的身份验证协议
- 提供ID Token和用户信息端点
- 版本：1.0

**OAuth 2.0**
- RFC 6749定义的授权框架
- 允许第三方应用获取用户授权访问资源
- 最新版本：RFC 6749

### P

**PKCE (Proof Key for Code Exchange)**
- RFC 7636定义的安全扩展
- 用于防止授权码拦截攻击
- 全称：用于代码交换的证明密钥

**Principal（主体）**
- 通常指当前认证的用户

**Protected Resource（受保护资源）**
- 用户的数据或功能，只有携带有效令牌才能访问

### R

**Refresh Token（刷新令牌）**
- 用于获取新的访问令牌的凭证
- 通常比access_token有效期更长
- 必须安全存储

**Resource Owner（资源所有者）**
- 拥有受保护资源的用户
- 可以授权或拒绝客户端访问

**Resource Server（资源服务器）**
- 托管受保护资源的服务器
- 验证访问令牌并返回资源

**RFC 6749**
- OAuth2.0的官方IETF规范

**RFC 6750**
- OAuth2.0 Bearer Token Usage规范
- 定义如何在HTTP请求中使用Bearer Token

**RFC 7636**
- PKCE（Proof Key for Code Exchange）的规范

**RFC 7519**
- JSON Web Token (JWT)规范

**Scope（权限范围）**
- 指定令牌允许访问的资源类型
- 示例：`openid`, `profile`, `email`, `read`, `write`

**State Parameter（状态参数）**
- 客户端生成的随机字符串
- 用于防止CSRF攻击
- 在授权回调中返回并验证

### T

**Token Endpoint（令牌端点）**
- 用于交换授权码获取令牌的HTTP端点
- 通常：`POST /oauth/token`

**Token Introspection（令牌自省）**
- RFC 7662定义的协议
- 允许客户端查询令牌的有效性和元数据

**Token Revocation（令牌撤销）**
- RFC 7009定义的协议
- 允许客户端撤销不再需要的令牌

### U

**User-Agent**
- 用户的浏览器或应用程序
- 在OAuth2流程中用于重定向用户

### V

**Vulnerabilities（漏洞）**
- 常见OAuth2安全漏洞：
  - CSRF攻击
  - 授权码拦截
  - 重定向URI配置不当
  - Token泄露

---

## 相关RFC文档

| RFC | 主题 |
|-----|------|
| RFC 6749 | OAuth2.0框架 |
| RFC 6750 | Bearer Token使用 |
| RFC 6819 | OAuth2安全注意事项 |
| RFC 7009 | Token撤销 |
| RFC 7519 | JWT |
| RFC 7517 | JWK |
| RFC 7518 | JWA (JWT Algorithms) |
| RFC 7636 | PKCE |
| RFC 7662 | Token自省 |
| RFC 8242 | OAuth2安全性 |
| RFC 8259 | JSON |

## 常见OAuth2服务提供商

- **Google Identity Platform**: `accounts.google.com`
- **Microsoft Identity Platform**: `login.microsoftonline.com`
- **GitHub OAuth**: `github.com/login/oauth`
- **Facebook Login**: `facebook.com/v18.0/dialog/oauth`
- **微信OAuth**: `open.weixin.qq.com`
- **支付宝OAuth**: `openauth.alipay.com`

## OAuth2与OIDC对比

| 方面 | OAuth2 | OIDC |
|------|--------|------|
| 主要目的 | 授权 | 身份验证+授权 |
| Token类型 | Access Token | Access Token + ID Token |
| 用户信息 | 需要额外调用API | ID Token直接包含 |
| 标准Scope | read, write等 | openid, profile, email等 |
| 标准化程度 | RFC 6749 | Core 1.0 + 多个扩展 |
