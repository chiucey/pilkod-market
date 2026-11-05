---
name: web-payment-integration
description: 在网页中集成支付功能。当用户要求添加支付功能、集成支付宝/微信支付、接入PayPal/Stripe、开发在线收款页面、实现电商支付系统、或需要多平台支付解决方案时使用。
---

# 网页支付集成技能

本技能提供完整的国内外支付平台集成方案，帮助开发者快速在网页应用中接入支付宝、微信支付、PayPal、Stripe等主流支付渠道。

## 支持的支付平台

### 国内支付

| 平台 | 特点 | 适用场景 |
|------|------|----------|
| 支付宝 | 覆盖率高，用户基数大 | 电商、O2O服务 |
| 微信支付 | 社交支付，便捷快速 | 移动电商、小程序 |

### 国际支付

| 平台 | 特点 | 适用场景 |
|------|------|----------|
| PayPal | 全球普及率高 | 跨境电商、国际服务 |
| Stripe | 开发者友好，API完善 | SaaS、订阅服务 |

## 集成工作流

### 阶段一：支付环境准备

在开始集成前，需要完成以下准备工作：

**商户账户申请**：向各支付平台提交商户入驻申请，获取必要的凭证信息。

**开发资质准备**：根据平台要求准备营业执照、法人身份证等资质文件。

**密钥配置**：获取应用ID（AppID）、商户号、密钥（SecretKey）、证书等安全凭证。

### 阶段二：前端集成

前端负责唤起支付界面和处理支付结果回调。

**支付按钮实现**：创建用户可见的支付入口，支持选择支付方式。

```html
<!-- 支付方式选择示例 -->
<div class="payment-methods">
  <button class="payment-btn" data-method="alipay">
    <img src="/icons/alipay.svg" alt="支付宝"> 支付宝
  </button>
  <button class="payment-btn" data-method="wechat">
    <img src="/icons/wechat.svg" alt="微信支付"> 微信支付
  </button>
  <button class="payment-btn" data-method="paypal">
    <img src="/icons/paypal.svg" alt="PayPal"> PayPal
  </button>
</div>
```

**支付流程处理**：调用后端接口获取支付参数，前端根据不同平台唤起相应支付界面。

### 阶段三：后端集成

后端负责订单创建、支付签名、回调处理等核心逻辑。

**订单创建**：根据前端传来的商品信息生成订单，返回支付所需的签名参数。

**支付签名**：使用平台规定的签名算法对请求参数进行签名，确保请求安全性。

**回调处理**：接收支付平台的异步通知，验证签名后更新订单状态。

## 平台集成详解

### 支付宝集成

支付宝提供多种接入方式，包括电脑网站支付、手机网站支付、APP支付等。

**前端唤起支付**：

```javascript
function alipayPay(orderInfo) {
  // 调用后端获取支付表单
  fetch('/api/payment/alipay/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(orderInfo)
  })
  .then(response => response.json())
  .then(data => {
    // 支付宝PC端跳转
    document.write(data.payForm);
  })
  .catch(error => console.error('支付创建失败', error));
}
```

**后端签名处理**（Node.js示例）：

```javascript
const crypto = require('crypto');

function alipaySign(params, privateKey) {
  const signStr = Object.keys(params)
    .filter(key => params[key] && params[key] !== '')
    .sort()
    .map(key => `${key}=${params[key]}`)
    .join('&');

  const sign = crypto
    .createSign('RSA-SHA256')
    .update(signStr)
    .sign(privateKey, 'base64');

  return sign;
}
```

### 微信支付集成

微信支付分为JSAPI支付（公众号）、H5支付、Native支付等多种模式。

**JSAPI支付前端代码**：

```javascript
async function wechatPay(orderInfo) {
  try {
    // 1. 获取支付参数
    const response = await fetch('/api/payment/wechat/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(orderInfo)
    });
    const data = await response.json();

    // 2. 调起微信支付
    if (typeof WeixinJSBridge !== 'undefined') {
      WeixinJSBridge.invoke('getBrandWCPayRequest', {
        appId: data.appId,
        timeStamp: data.timeStamp,
        nonceStr: data.nonceStr,
        package: data.package,
        signType: data.signType,
        paySign: data.paySign
      }, function(res) {
        if (res.err_msg === 'get_brand_wcpay_request:ok') {
          console.log('支付成功');
          // 跳转成功页面
        } else {
          console.log('支付失败', res.err_msg);
        }
      });
    }
  } catch (error) {
    console.error('微信支付初始化失败', error);
  }
}
```

**H5支付（手机浏览器）**：

```javascript
function wechatH5Pay(orderInfo) {
  fetch('/api/payment/wechat/h5-create', {
    method: 'POST',
    body: JSON.stringify(orderInfo)
  })
  .then(response => response.json())
  .then(data => {
    // 微信H5支付需要跳转至微信中间页
    window.location.href = data.mweb_url;
  });
}
```

### PayPal集成

PayPal提供标准JS SDK，集成简单快捷。

**PayPal按钮集成**：

```html
<div id="paypal-button-container"></div>

<script src="https://www.paypal.com/sdk/js?client-id=YOUR_CLIENT_ID"></script>
<script>
  paypal.Buttons({
    createOrder: function(data, actions) {
      // 从后端获取订单信息
      return fetch('/api/payment/paypal/create-order', {
        method: 'post',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: document.getElementById('amount').value
        })
      })
      .then(function(res) { return res.json(); })
      .then(function(orderData) { return orderData.orderID; });
    },
    onApprove: function(data, actions) {
      // 支付授权后完成订单
      return fetch('/api/payment/paypal/capture-order', {
        method: 'post',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ orderID: data.orderID })
      })
      .then(function(res) { return res.json(); })
      .then(function(details) {
        alert('交易完成，订单号: ' + details.id);
      });
    }
  }).render('#paypal-button-container');
</script>
```

### Stripe集成

Stripe以开发者体验著称，提供丰富的SDK支持。

**Stripe Checkout集成**：

```javascript
// 后端创建Checkout Session
async function createStripeSession(req, res) {
  const stripe = require('stripe')('sk_test_xxx');

  const session = await stripe.checkout.sessions.create({
    payment_method_types: ['card'],
    line_items: [{
      price_data: {
        currency: 'cny',
        product_data: { name: '商品名称' },
        unit_amount: req.body.amount * 100, // 金额，单位分
      },
      quantity: 1,
    }],
    mode: 'payment',
    success_url: 'https://yoursite.com/success',
    cancel_url: 'https://yoursite.com/cancel',
  });

  res.json({ sessionId: session.id });
}

// 前端跳转至Stripe Checkout
async function stripeCheckout(amount) {
  const response = await fetch('/api/payment/stripe/create-session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ amount })
  });
  const { sessionId } = await response.json();

  const stripe = Stripe('pk_test_xxx');
  stripe.redirectToCheckout({ sessionId });
}
```

## 安全最佳实践

### 敏感信息保护

**密钥管理**：所有支付密钥和商户凭证必须存储在服务端，禁止在前端代码中暴露。

```javascript
// 错误做法
const APP_SECRET = 'your_secret_here'; // 绝对禁止

// 正确做法
// 密钥仅存在于服务端配置文件，环境变量存储
```

**签名验证**：所有支付回调必须验证签名，确保通知来自真实的支付平台。

```javascript
function verifyAlipayCallback(params, alipayPublicKey) {
  const sign = params.sign;
  delete params.sign;
  delete params.sign_type;

  const signStr = Object.keys(params)
    .sort()
    .map(key => `${key}=${params[key]}`)
    .join('&');

  const isValid = crypto
    .createVerify('RSA-SHA256')
    .update(signStr)
    .verify(alipayPublicKey, sign, 'base64');

  return isValid;
}
```

### 支付安全检查清单

- [ ] 使用HTTPS加密传输所有支付相关请求
- [ ] 订单金额在后端计算，禁止信任前端传来的价格
- [ ] 实现订单超时机制，防止重复支付
- [ ] 记录完整的支付日志，便于问题排查
- [ ] 定期轮换支付密钥
- [ ] 启用支付平台的风险监控服务

## 常见问题处理

### 支付回调失败

支付平台的通知可能因网络问题出现延迟或丢失，需要实现以下机制：

1. **幂等性处理**：同一订单号的回调只处理一次
2. **状态检查**：主动查询支付平台确认订单状态
3. **重试队列**：将失败的回调加入重试队列

### 跨域问题

前端调用后端接口时需要正确配置CORS：

```javascript
// 统一网关配置
app.use(cors({
  origin: ['https://yoursite.com'],
  credentials: true
}));
```

### 支付限额

各支付平台有不同的单笔和日累计限额，应在产品层面给予用户提示：

- 支付宝单笔限额：实时到账卡最高50万
- 微信支付单笔限额：银行快捷支付最高5万
- PayPal单笔限额：根据账户类型和地区不同

## 测试环境

在生产环境部署前，必须在测试环境完成完整流程验证：

**沙箱环境**：各平台都提供独立的测试环境，使用测试密钥进行开发调试。

| 平台 | 测试环境地址 |
|------|--------------|
| 支付宝 | https://openhome.alipay.com/develop/sandbox |
| 微信支付 | https://pay.weixin.qq.com/wiki/doc/apiv3_partner/open/pay/chapter6_1.shtml |
| PayPal | https://developer.paypal.com/sandbox |
| Stripe | https://dashboard.stripe.com/test/apikeys |

**测试用例覆盖**：

- 正常支付流程
- 支付取消操作
- 支付超时处理
- 重复回调处理
- 签名验证失败场景

## 相关资源

详细的平台文档和SDK下载地址请参阅 references 目录下的集成指南：

- <filepath>/workspace/temp-skills/web-payment-integration/references/alipay-guide.md</filepath>
- <filepath>/workspace/temp-skills/web-payment-integration/references/wechat-pay-guide.md</filepath>
- <filepath>/workspace/temp-skills/web-payment-integration/references/paypal-guide.md</filepath>
- <filepath>/workspace/temp-skills/web-payment-integration/references/stripe-guide.md</filepath>
