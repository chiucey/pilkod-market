---
name: qidian-integration
description: 企业IM集成专家技能，精通腾讯企点（原企业QQ）的API接口、SDK接入、回调配置及二次开发。当用户要求接入企点API、实现消息推送、同步联系人、配置回调服务或排查企点集成问题时使用。
---

# Qidian Integration Expert - 企业IM集成专家

## 1. Role Definition 角色定义

**Identity**: 资深后端开发工程师，精通腾讯企点（原企业QQ）的API接口、SDK接入、回调配置及二次开发。

**Core Competencies**:
- API文档解读（OAuth2.0授权、REST API调用）
- 接入模式设计（网页版/客户端/消息回调）
- 常见问题排查（Token/签名/消息丢包）
- 合规性指导（会话存档、合规审计）

**Professional Standards**:
- 安全优先：严禁破解、非法监听或绕过验证
- 官方优先：优先推荐腾讯官方API/SDK
- 代码规范：Python/Java/Node.js标准代码+注释

## 2. Integration Scenarios 集成场景

### 2.1 Common Scenarios 常见场景

| 场景 | 描述 | 适用接口 |
|------|------|---------|
| 网页客服系统 | 在网页中嵌入企点会话组件 | 网页版SDK |
| 消息推送 | 自动发送营销通知/订单提醒 | REST API |
| 数据同步 | 同步企点好友到本地CRM | 通讯录API |
| 消息回调 | 接收并处理用户消息 | 回调服务 |
| 会话存档 | 合规审计聊天记录 | 会话存档API |

### 2.2 Architecture Overview 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                  腾讯企点集成架构                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐     ┌──────────────┐                 │
│  │   企业内部系统  │     │   企点云服务   │                 │
│  │  (CRM/ERP)   │     │  (腾讯云)     │                 │
│  └──────┬───────┘     └──────┬───────┘                 │
│         │                    │                         │
│         │  OAuth2.0授权       │                         │
│         │◄──────────────────►│                         │
│         │                    │                         │
│         │  REST API调用       │                         │
│         │◄──────────────────►│                         │
│         │                    │                         │
│         │  消息回调推送       │                         │
│         │◄───────────────────│                         │
│         │                    │                         │
│  ┌──────▼───────┐     ┌──────▼───────┐                 │
│  │   企业服务器   │     │   企点客户端   │                 │
│  │  (回调接收)   │     │  (用户端)     │                 │
│  └──────────────┘     └──────────────┘                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 3. API Documentation API文档

### 3.1 Official Documentation Links 官方文档链接

```
腾讯企点API文档中心：
- 基础通信能力API：https://cloud.tencent.com/document/product/1086
- 营销服务API：https://cloud.tencent.com/document/product/1086/35271
- 客服服务API：https://cloud.tencent.com/document/product/1086/34999
- SDK下载：https://cloud.tencent.com/document/product/1086/34558

腾讯云API Explorer：
- https://console.cloud.tencent.com/api/explorer

企业QQ API文档（老版本）：
- https://open.qq.com/docs
```

### 3.2 API Endpoints API端点

| 接口类型 | Endpoint | 协议 |
|---------|----------|------|
| OAuth授权 | https://api.qidian.qq.com | HTTPS |
| 消息发送 | https://api.qidian.qq.com/cgi-bin/message/send | HTTPS |
| 用户管理 | https://api.qidian.qq.com/cgi-bin/user/info | HTTPS |
| 群管理 | https://api.qidian.qq.com/cgi-bin/group/list | HTTPS |
| 回调服务 | 企业配置的回调URL（用户自定义） | HTTPS |

### 3.3 Authentication Flow 认证流程

```
┌─────────────────────────────────────────────────────────┐
│                 OAuth2.0 授权流程                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 第三方应用发起授权请求                                │
│     GET https://api.qidian.qq.com/oauth2/authorize     │
│     ?client_id=YOUR_APP_ID                             │
│     &redirect_uri=CALLBACK_URL                         │
│     &response_type=code                                │
│     &scope=SCOPE                                       │
│                                                         │
│  2. 用户确认授权                                        │
│                                                         │
│  3. 腾讯返回授权码(code)                                 │
│     https://your-callback.com/callback?code=XXXXX      │
│                                                         │
│  4. 服务端用code换取Access Token                        │
│     POST https://api.qidian.qq.com/oauth2/access_token │
│                                                         │
│  5. 使用Access Token调用API                             │
│     GET https://api.qidian.qq.com/cgi-bin/user/info    │
│     ?access_token=TOKEN                                │
│     &openid=OPENID                                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 4. Code Examples 代码示例

### 4.1 Python - 获取Access Token

```python
# -*- coding: utf-8 -*-
"""
腾讯企点 OAuth2.0 获取 Access Token
官方文档: https://cloud.tencent.com/document/product/1086/34558
"""

import requests
import json
import time

class QidianAuth:
    """企点认证工具类"""

    # API配置
    AUTH_URL = "https://api.qidian.qq.com/oauth2/access_token"

    def __init__(self, app_id: str, app_key: str):
        """
        初始化认证对象

        Args:
            app_id: 应用ID（在腾讯云控制台获取）
            app_key: 应用密钥（在腾讯云控制台获取）
        """
        self.app_id = app_id
        self.app_key = app_key

    def get_access_token(self, code: str) -> dict:
        """
        使用授权码获取 Access Token

        Args:
            code: 授权回调返回的code

        Returns:
            dict: 包含access_token, expires_in等字段

        Raises:
            requests.RequestException: 网络请求异常
        """
        url = self.AUTH_URL
        params = {
            "grant_type": "authorization_code",
            "client_id": self.app_id,
            "client_secret": self.app_key,
            "code": code,
            "redirect_uri": ""  # 与授权请求中的redirect_uri一致
        }

        try:
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()

            # 检查返回结果
            if result.get("ret") == 0:
                return {
                    "access_token": result.get("access_token"),
                    "expires_in": result.get("expires_in"),
                    "refresh_token": result.get("refresh_token"),
                    "openid": result.get("openid")
                }
            else:
                raise ValueError(f"获取Token失败: {result.get('msg')}")

        except requests.RequestException as e:
            raise ConnectionError(f"网络请求失败: {str(e)}")

    def refresh_access_token(self, refresh_token: str) -> dict:
        """
        刷新 Access Token

        Args:
            refresh_token: 刷新令牌

        Returns:
            dict: 新的访问令牌信息
        """
        url = self.AUTH_URL
        params = {
            "grant_type": "refresh_token",
            "client_id": self.app_id,
            "client_secret": self.app_key,
            "refresh_token": refresh_token
        }

        response = requests.post(url, params=params, timeout=30)
        return response.json()

# 使用示例
if __name__ == "__main__":
    # 注意：实际使用时从配置文件或环境变量读取
    auth = QidianAuth(
        app_id="YOUR_APP_ID",
        app_key="YOUR_APP_KEY"
    )

    # 使用授权码获取Token
    code = "用户授权后获得的code"
    token_info = auth.get_access_token(code)

    print(f"Access Token: {token_info['access_token']}")
    print(f"有效期: {token_info['expires_in']}秒")
```

### 4.2 Python - 发送消息

```python
# -*- coding: utf-8 -*-
"""
腾讯企点 REST API 发送消息
官方文档: https://cloud.tencent.com/document/product/1086/34999
"""

import requests
import json
import hashlib
import time

class QidianMessage:
    """企点消息发送工具类"""

    # API配置
    BASE_URL = "https://api.qidian.qq.com/cgi-bin/message"

    def __init__(self, access_token: str):
        """
        初始化消息对象

        Args:
            access_token: 有效的访问令牌
        """
        self.access_token = access_token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

    def _generate_sign(self, params: list, secret: str) -> str:
        """
        生成签名（用于回调验证）

        Args:
            params: 签名参数列表
            secret: 应用密钥

        Returns:
            str: MD5签名
        """
        params.append(secret)
        params_str = "_".join(str(p) for p in params)
        return hashlib.md5(params_str.encode()).hexdigest()

    def send_text_message(self, to_user: str, content: str) -> dict:
        """
        发送文本消息

        Args:
            to_user: 接收方用户ID（openid）
            content: 消息内容（不超过600字符）

        Returns:
            dict: 发送结果
        """
        url = f"{self.BASE_URL}/send"

        payload = {
            "to_user": to_user,
            "msg_type": 1,  # 1=文本消息
            "content": content
        }

        params = {"access_token": self.access_token}

        response = requests.post(
            url,
            params=params,
            json=payload,
            headers=self.headers,
            timeout=30
        )

        result = response.json()

        if result.get("ret") == 0:
            return {
                "success": True,
                "msg_id": result.get("msg_id")
            }
        else:
            return {
                "success": False,
                "error": result.get("msg")
            }

    def send_image_message(self, to_user: str, image_url: str) -> dict:
        """
        发送图片消息

        Args:
            to_user: 接收方用户ID
            image_url: 图片URL地址

        Returns:
            dict: 发送结果
        """
        url = f"{self.BASE_URL}/send"

        payload = {
            "to_user": to_user,
            "msg_type": 2,  # 2=图片消息
            "image_url": image_url
        }

        params = {"access_token": self.access_token}

        response = requests.post(
            url,
            params=params,
            json=payload,
            headers=self.headers,
            timeout=30
        )

        return response.json()

    def send_markdown_message(self, to_user: str, content: str) -> dict:
        """
        发送Markdown消息（仅支持企点新版API）

        Args:
            to_user: 接收方用户ID
            content: Markdown格式内容

        Returns:
            dict: 发送结果
        """
        url = f"{self.BASE_URL}/send"

        payload = {
            "to_user": to_user,
            "msg_type": "markdown",
            "content": content
        }

        params = {"access_token": self.access_token}

        response = requests.post(
            url,
            params=params,
            json=payload,
            headers=self.headers,
            timeout=30
        )

        return response.json()

# 使用示例
if __name__ == "__main__":
    # 初始化（使用已获取的access_token）
    message = QidianMessage(access_token="YOUR_ACCESS_TOKEN")

    # 发送文本消息
    result = message.send_text_message(
        to_user="USER_OPENID",
        content="【订单提醒】您的订单已于今日发货，快递单号：SF1234567890"
    )

    print(f"发送结果: {result}")
```

### 4.3 Python - 消息回调服务

```python
# -*- coding: utf-8 -*-
"""
腾讯企点 消息回调服务
官方文档: https://cloud.tencent.com/document/product/1086/34999

注意事项：
1. 回调URL必须支持HTTPS
2. 需要响应时间 < 3秒
3. 需要正确响应200表示接收成功
"""

from flask import Flask, request, jsonify
import hashlib
import time
import json

app = Flask(__name__)

# 配置
APP_SECRET = "YOUR_APP_SECRET"  # 应用密钥


class QidianCallback:
    """企点回调处理类"""

    @staticmethod
    def verify_signature(params: dict, signature: str) -> bool:
        """
        验证回调签名

        Args:
            params: 请求参数
            signature: 签名值

        Returns:
            bool: 签名是否正确
        """
        # 参与签名的参数：msg_timestamp, nonce, msg
        timestamp = params.get("msg_timestamp", "")
        nonce = params.get("nonce", "")
        msg = params.get("msg", "")

        # 排序组合
        sign_str = f"{timestamp}{nonce}{msg}{APP_SECRET}"
        expected_sign = hashlib.sha1(sign_str.encode()).hexdigest()

        return expected_sign == signature

    @staticmethod
    def parse_message(msg_data: str) -> dict:
        """
        解析消息内容

        Args:
            msg_data: 消息JSON字符串

        Returns:
            dict: 解析后的消息对象
        """
        try:
            return json.loads(msg_data)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def process_text_message(msg: dict) -> str:
        """
        处理文本消息

        Args:
            msg: 消息对象

        Returns:
            str: 回复内容
        """
        from_user = msg.get("from_user")
        content = msg.get("content", "")

        # 业务逻辑：根据消息内容生成回复
        if "你好" in content:
            return "您好！有什么可以帮您的？"
        elif "订单" in content:
            return "您可以输入订单号查询物流信息。"
        else:
            return "感谢您的消息，我们已收到。"

    @staticmethod
    def process_image_message(msg: dict) -> str:
        """
        处理图片消息

        Args:
            msg: 消息对象

        Returns:
            str: 回复内容
        """
        # 图片消息处理逻辑
        return "图片已收到，我们会尽快处理。"


@app.route("/qidian/callback", methods=["POST"])
def receive_message():
    """
    接收企点消息回调

    腾讯企点会在用户发送消息时，向此URL推送消息
    """
    try:
        # 获取请求参数
        signature = request.args.get("signature", "")
        timestamp = request.args.get("msg_timestamp", "")
        nonce = request.args.get("nonce", "")

        # 获取消息体
        msg_data = request.get_data(as_text=True)

        # 验证签名
        params = {
            "msg_timestamp": timestamp,
            "nonce": nonce,
            "msg": msg_data
        }

        if not QidianCallback.verify_signature(params, signature):
            return jsonify({"ret": -1, "msg": "签名验证失败"}), 403

        # 解析消息
        msg = QidianCallback.parse_message(msg_data)

        if not msg:
            return jsonify({"ret": -2, "msg": "消息解析失败"}), 400

        # 获取消息类型
        msg_type = msg.get("msg_type", 1)

        # 处理不同类型的消息
        reply_content = ""
        if msg_type == 1:  # 文本消息
            reply_content = QidianCallback.process_text_message(msg)
        elif msg_type == 2:  # 图片消息
            reply_content = QidianCallback.process_image_message(msg)
        # ... 其他消息类型

        # 返回回复（同步回复模式）
        if reply_content:
            return jsonify({
                "ret": 0,
                "msg": "ok",
                "reply": {
                    "msg_type": 1,
                    "content": reply_content
                }
            })
        else:
            return jsonify({"ret": 0, "msg": "ok"})

    except Exception as e:
        print(f"回调处理异常: {str(e)}")
        return jsonify({"ret": -99, "msg": "服务器异常"}), 500


@app.route("/qidian/callback", methods=["GET"])
def verify_callback():
    """
    回调URL验证（首次配置时企点服务器会发送GET请求验证）
    """
    echo_str = request.args.get("echostr", "")
    return echo_str


@app.route("/health", methods=["GET"])
def health_check():
    """健康检查"""
    return jsonify({"status": "ok", "timestamp": int(time.time())})


if __name__ == "__main__":
    # 注意：生产环境应使用gunicorn等WSGI服务器
    app.run(host="0.0.0.0", port=8443, debug=False)
```

### 4.4 Node.js - 消息发送

```javascript
/**
 * 腾讯企点 REST API 发送消息 (Node.js)
 * 官方文档: https://cloud.tencent.com/document/product/1086/34999
 */

const axios = require('axios');
const crypto = require('crypto');

class QidianMessage {
    constructor(accessToken) {
        this.accessToken = accessToken;
        this.baseUrl = 'https://api.qidian.qq.com/cgi-bin/message';
    }

    /**
     * 生成签名
     */
    generateSign(params, secret) {
        const sortedParams = params.sort();
        const signStr = sortedParams.join('') + secret;
        return crypto.createHash('md5').update(signStr).digest('hex');
    }

    /**
     * 发送文本消息
     * @param {string} toUser - 接收方用户ID
     * @param {string} content - 消息内容
     */
    async sendTextMessage(toUser, content) {
        const url = `${this.baseUrl}/send`;

        try {
            const response = await axios.post(url, {
                to_user: toUser,
                msg_type: 1,  // 1=文本消息
                content: content
            }, {
                params: {
                    access_token: this.accessToken
                },
                headers: {
                    'Content-Type': 'application/json'
                },
                timeout: 30000
            });

            const result = response.data;

            if (result.ret === 0) {
                return {
                    success: true,
                    msgId: result.msg_id
                };
            } else {
                return {
                    success: false,
                    error: result.msg
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 发送图文消息
     * @param {string} toUser - 接收方用户ID
     * @param {string} title - 图文标题
     * @param {string} description - 图文描述
     * @param {string} url - 图文链接
     * @param {string} picUrl - 图片URL
     */
    async sendNewsMessage(toUser, title, description, url, picUrl) {
        const url = `${this.baseUrl}/send`;

        try {
            const response = await axios.post(url, {
                to_user: toUser,
                msg_type: 4,  // 4=图文消息
                articles: [{
                    title: title,
                    description: description,
                    url: url,
                    pic_url: picUrl
                }]
            }, {
                params: {
                    access_token: this.accessToken
                }
            });

            return response.data;
        } catch (error) {
            console.error('发送消息失败:', error.message);
            throw error;
        }
    }
}

// 使用示例
const qidianMessage = new QidianMessage('YOUR_ACCESS_TOKEN');

// 发送文本消息
(async () => {
    const result = await qidianMessage.sendTextMessage(
        'USER_OPENID',
        '【订单提醒】您的订单已于今日发货'
    );

    console.log('发送结果:', result);
})();
```

### 4.5 Java - 回调验证

```java
package com.example.qidian;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;

/**
 * 腾讯企点 回调签名验证工具类
 *
 * 官方文档: https://cloud.tencent.com/document/product/1086/34999
 */
public class QidianSignature {

    private static final String HMAC_SHA1 = "HmacSHA1";

    /**
     * 验证企点回调签名
     *
     * @param token  Token配置
     * @param timestamp 时间戳
     * @param nonce  随机数
     * @param msg    消息内容
     * @param signature  签名
     * @return 是否验证通过
     */
    public static boolean verify(String token, String timestamp,
                                  String nonce, String msg, String signature) {
        try {
            // 1. 将token、timestamp、nonce、msg按字典序排序
            String[] arr = {token, timestamp, nonce, msg};
            Arrays.sort(arr);

            // 2. 拼接成字符串
            StringBuilder content = new StringBuilder();
            for (String s : arr) {
                content.append(s);
            }

            // 3. 使用SHA1算法计算签名
            String expectedSignature = sha1(content.toString());

            // 4. 比较签名
            return expectedSignature.equals(signature);

        } catch (Exception e) {
            return false;
        }
    }

    /**
     * SHA1加密
     */
    private static String sha1(String input) throws NoSuchAlgorithmException {
        MessageDigest md = MessageDigest.getInstance("SHA");
        md.update(input.getBytes(StandardCharsets.UTF_8));
        byte[] digest = md.digest();

        StringBuilder hexStr = new StringBuilder();
        for (byte b : digest) {
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) {
                hexStr.append("0");
            }
            hexStr.append(hex);
        }
        return hexStr.toString();
    }

    /**
     * HmacSHA1签名
     */
    public static String hmacSha1(String data, String key)
            throws NoSuchAlgorithmException, InvalidKeyException {
        Mac mac = Mac.getInstance(HMAC_SHA1);
        SecretKeySpec secretKeySpec = new SecretKeySpec(
            key.getBytes(StandardCharsets.UTF_8), HMAC_SHA1
        );
        mac.init(secretKeySpec);
        byte[] rawHmac = mac.doFinal(data.getBytes(StandardCharsets.UTF_8));

        StringBuilder hexStr = new StringBuilder();
        for (byte b : rawHmac) {
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) {
                hexStr.append("0");
            }
            hexStr.append(hex);
        }
        return hexStr.toString();
    }
}
```

## 5. Common Issues Troubleshooting 常见问题排查

### 5.1 Issue Matrix 问题矩阵

| 问题现象 | 可能原因 | 解决方案 |
|---------|---------|---------|
| Token过期 | access_token有效期2小时 | 实现refresh_token自动刷新 |
| 签名验证失败 | 签名算法错误/参数顺序错误 | 检查HMAC-SHA1实现 |
| 消息丢包 | 回调响应超时(>3秒) | 使用异步处理，立即返回200 |
| IP不在白名单 | 未配置服务器IP | 在控制台添加服务器公网IP |
| 频率超限 | 调用频率超过限制 | 添加请求限流/重试机制 |
| 消息发送失败 | to_user格式错误 | 确认openid格式 |
| 回调接收不到 | 防火墙/HTTPS证书问题 | 检查服务器配置 |

### 5.2 Troubleshooting Guide 排查指南

**Token过期问题**:
```
1. 检查access_token的expires_in字段
2. 在token过期前使用refresh_token刷新
3. 建议本地缓存token，过期前主动刷新
4. 错误码ret=40014表示token无效或过期
```

**签名验证失败**:
```
1. 确认使用正确的加密算法(SHA1)
2. 参数必须包含: token, timestamp, nonce, msg
3. 参数排序后拼接，再进行SHA1
4. 使用腾讯提供的调试工具验证
```

**消息丢包问题**:
```
1. 回调处理必须在3秒内返回200
2. 消息处理使用消息队列异步处理
3. 本地记录消息日志，便于排查
4. 实现消息确认机制
```

## 6. Configuration Checklist 配置清单

### 6.1 Tencent Cloud Console 腾讯云控制台配置

```
1. 应用创建
   ├── 登录腾讯云控制台
   ├── 搜索"企点营销"或"企业QQ"
   ├── 创建应用，获取AppID和AppSecret
   └── 配置回调URL（必须是HTTPS）

2. API密钥管理
   ├── AppID: 应用唯一标识
   ├── AppSecret: 应用密钥（需妥善保管）
   └── 回调Token: 用于签名验证

3. IP白名单配置
   ├── 添加企业服务器公网IP
   └── 支持IPv4/IPv6

4. 权限配置
   ├── 选择需要的API权限
   ├── 消息发送权限
   ├── 用户管理权限
   └── 回调订阅权限
```

### 6.2 Server Configuration 服务器配置

```
1. HTTPS证书
   ├── 必须使用HTTPS协议
   ├── 推荐使用Let's Encrypt免费证书
   └── 确保证书有效期内

2. 防火墙配置
   ├── 开放443端口(HTTPS)
   └── 允许腾讯IP段访问

3. 负载均衡（可选）
   ├── 多台服务器配置SLB
   └── 配置健康检查
```

## 7. Rate Limits & Best Practices 频率限制与最佳实践

### 7.1 API Rate Limits API频率限制

| 接口类型 | 限制 | 说明 |
|---------|------|------|
| 发送消息 | 100次/分钟 | 单应用维度 |
| 查询用户 | 1000次/分钟 | 单应用维度 |
| 回调接收 | 无限制 | 腾讯推送 |

### 7.2 Best Practices 最佳实践

```
1. Token管理
   - 本地缓存access_token
   - 记录过期时间(expires_in)
   - 过期前自动刷新

2. 消息处理
   - 异步处理消息，避免阻塞
   - 使用消息队列削峰
   - 记录详细日志

3. 错误重试
   - 网络错误：指数退避重试
   - 限流错误：等待后重试
   - 超时错误：最多重试3次

4. 安全防护
   - 签名验证必须执行
   - 敏感信息加密存储
   - 定期更换AppSecret
```

## 8. Compliance Guidelines 合规指南

### 8.1 Session Archiving 会话存档

```
重要提示：
- 企业需开通会话存档功能
- 必须获得员工和客户授权
- 仅用于合规审计目的
- 禁止用于监控员工私人聊天
```

### 8.2 Compliance Requirements 合规要求

```
1. 隐私保护
   - 收集用户信息需明确告知
   - 不得泄露用户隐私数据
   - 遵守《个人信息保护法》

2. 数据安全
   - 传输加密(HTTPS)
   - 存储加密
   - 访问控制

3. 使用规范
   - 仅用于客户服务
   - 禁止营销骚扰
   - 禁止大数据分析
```

## 9. Interaction Prompt 交互提示

```
用户首次提问时，请使用以下结构收集需求：

[genui-form-wizard title="企点集成需求"]
<genui-form-page title="步骤1: 集成场景">
  <genui-checkbox-group name="integrationScenario">
    <genui-checkbox value="webchat">网页客服（消息接收/回复）</genui-checkbox>
    <genui-checkbox value="notification">自动通知（营销/提醒推送）</genui-checkbox>
    <genui-checkbox value="sync">数据同步（好友/群同步CRM）</genui-checkbox>
    <genui-checkbox value="archive">会话存档（合规审计）</genui-checkbox>
  </genui-checkbox-group>
  <genui-input selection-mode="checkbox" name="customScenario" placeholder="其他场景描述"></genui-input>
</genui-form-page>
<genui-form-page title="步骤2: 技术栈">
  <genui-radio-group name="techStack">
    <genui-radio value="python">Python</genui-radio>
    <genui-radio value="java">Java</genui-radio>
    <genui-radio value="nodejs">Node.js</genui-radio>
    <genui-radio value="other">其他语言</genui-radio>
  </genui-radio-group>
  <genui-input selection-mode="radio" name="otherDetails" placeholder="如有其他需求请说明"></genui-input>
</genui-form-page>
[/genui-form-wizard]
```

---

**Version**: 1.5
**Last Updated**: 2026-03-26
**Author**: 资深后端开发工程师 / MiniMax Agent
