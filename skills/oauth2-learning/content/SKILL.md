---
name: oauth2-learning
description: Use when users ask about OAuth2 basics, authorization code flow, implicit grant, client credentials, refresh tokens, access tokens, PKCE, OIDC, SSO, third-party login integration, or need OAuth2 implementation examples. 系统学习OAuth2认证授权协议。
---

# OAuth2 Learning Skill

OAuth2学习助手，帮助用户从理论到实践全面掌握OAuth2认证授权协议。

## 核心概念模块

### 1. OAuth2基础理论

**OAuth2是什么？**
- 一种开放标准授权协议，允许第三方应用在用户授权下访问其在其他服务上的资源
- 核心问题解决：如何在不暴露密码的情况下授权第三方应用访问资源

**角色定义**
- **Resource Owner**（资源所有者）：拥有受保护资源的用户
- **Client**（客户端）：想要访问资源的第三方应用
- **Authorization Server**（授权服务器）：验证用户身份并颁发令牌
- **Resource Server**（资源服务器）：托管受保护资源的服务器

**关键概念**
- **Access Token**：访问令牌，用于请求受保护资源
- **Refresh Token**：刷新令牌，用于获取新的访问令牌
- **Scope**：权限范围，定义令牌可以访问的资源类型
- **Client ID/Secret**：客户端标识和密钥，用于识别应用身份

### 2. 授权模式详解

#### 授权码模式（Authorization Code Grant）

**适用场景**：有后端服务器的Web应用（最安全）

**流程**：
1. 用户访问客户端，客户端引导用户到授权服务器
2. 用户登录并授权
3. 授权服务器返回授权码（code）到客户端后端
4. 客户端后端用授权码换取访问令牌
5. 客户端使用访问令牌访问资源服务器

**URL示例**：
```
https://auth.example.com/authorize?
  response_type=code&
  client_id=YOUR_CLIENT_ID&
  redirect_uri=https://your-app.com/callback&
  scope=read write&
  state=RANDOM_STATE
```

**令牌交换**：
```
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=AUTH_CODE&
redirect_uri=https://your-app.com/callback&
client_id=YOUR_CLIENT_ID&
client_secret=YOUR_CLIENT_SECRET
```

#### 隐式模式（Implicit Grant）- 已废弃

**说明**：不推荐使用，简化了流程但安全性降低，现代应用使用授权码+PKCE替代。

#### 客户端凭证模式（Client Credentials Grant）

**适用场景**：机器对机器（M2M）通信，服务间通信

**流程**：
```
POST /token
grant_type=client_credentials&
client_id=YOUR_CLIENT_ID&
client_secret=YOUR_CLIENT_SECRET&
scope=read
```

#### 资源所有者密码凭证模式（Password Grant）

**适用场景**：受信任的第一方应用

**警告**：不推荐用于第三方应用，用户需直接提供用户名密码。

#### 刷新令牌模式（Refresh Token Grant）

**用途**：Access Token过期后获取新令牌

```
POST /token
grant_type=refresh_token&
refresh_token=REFRESH_TOKEN&
client_id=YOUR_CLIENT_ID&
client_secret=YOUR_CLIENT_SECRET
```

### 3. 进阶安全机制

#### PKCE（Proof Key for Code Exchange）

**适用场景**：所有使用授权码模式的客户端（移动App、SPA必须使用）

**流程**：
1. 生成code_verifier（随机字符串，43-128字符）
2. 计算code_challenge = BASE64URL(SHA256(code_verifier))
3. 授权请求时携带code_challenge和code_challenge_method
4. 令牌交换时提供code_verifier，服务器验证

```
# 授权请求
https://auth.example.com/authorize?
  response_type=code&
  client_id=YOUR_CLIENT_ID&
  code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&
  code_challenge_method=S256

# 令牌交换
POST /token
code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk
```

#### OIDC（OpenID Connect）

**是什么**：构建在OAuth2之上的身份层，提供ID Token

**与OAuth2区别**：
- OAuth2：授权（我能访问什么）
- OIDC：身份验证（我是谁）

**ID Token结构**（JWT）：
```json
{
  "iss": "https://auth.example.com",
  "sub": "user123",
  "aud": "YOUR_CLIENT_ID",
  "exp": 1699999999,
  "iat": 1699996399,
  "name": "John Doe",
  "email": "john@example.com"
}
```

### 4. 实战实现指南

#### 常见OAuth2服务提供商

- **Google OAuth2**：支持授权码、PKCE、OIDC
- **GitHub OAuth2**：支持授权码模式
- **Microsoft/Azure AD**：支持授权码、PKCE、OIDC
- **微信OAuth2**：国内常用，支持授权码模式

#### 实现检查清单

**安全要点**：
- [ ] 使用HTTPS
- [ ] 客户端密钥安全存储（环境变量/密钥管理服务）
- [ ] 验证state参数防止CSRF
- [ ] 移动App和SPA必须使用PKCE
- [ ] 令牌存储安全（避免XSS攻击）
- [ ] 正确处理令牌刷新和过期
- [ ] 实现登出和令牌撤销

**错误处理**：
- `invalid_request`：请求参数缺失或无效
- `unauthorized_client`：客户端无权使用此授权类型
- `access_denied`：用户拒绝授权
- `invalid_grant`：授权码或刷新令牌无效/过期

### 5. 参考资源

详细文档位于 `references/` 目录：
- `references/oauth2-flows.md` - OAuth2各流程详解
- `references/security-best-practices.md` - 安全最佳实践
- `references/practical-examples.md` - 实战代码示例
- `references/glossary.md` - OAuth2术语表

## 交互式学习路径

根据用户需求选择学习路径：

1. **入门**：基础概念 → 授权码模式 → 简单实现
2. **进阶**：PKCE → OIDC → 安全加固
3. **实战**：选择服务商 → 阅读文档 → 代码实现
4. **排错**：常见错误 → 问题诊断 → 解决方案

## 输出格式

根据用户问题类型，提供：
- **概念解释**：清晰的定义和类比
- **流程图解**：ASCII或Mermaid流程图
- **代码示例**：Python/Node.js/Java等主流语言
- **安全建议**：最佳实践和常见陷阱
- **故障排除**：常见问题和解决方案
