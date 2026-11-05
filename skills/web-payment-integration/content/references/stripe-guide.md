# Stripe支付集成指南

本文档详细介绍如何在网页中集成Stripe支付功能，支持Checkout、Cards、Subscriptions等多种支付模式。

## 准备工作

### 注册账户

1. 访问Stripe官网（stripe.com）
2. 注册开发者账户
3. 完成邮箱验证

### 获取API密钥

在Dashboard → Developers → API keys中获取：

| 环境 | 密钥类型 | 用途 |
|------|----------|------|
| Test | pk_test_xxx / sk_test_xxx | 测试环境 |
| Live | pk_live_xxx / sk_live_xxx | 生产环境 |

### 安装SDK

**Node.js**：

```bash
npm install stripe
```

**Python**：

```bash
pip install stripe
```

## 支付模式选择

### Stripe Checkout（推荐）

Stripe托管的结账页面，最简单的集成方式。

### Stripe Elements

在你的页面中嵌入Stripe的支付组件，完全自定义UI。

### Stripe.js + PaymentIntents

完全自定义支付流程，适合复杂业务场景。

## Stripe Checkout集成

### 服务器端创建Session

```javascript
const express = require('express');
const stripe = require('stripe')('sk_test_xxx');

const app = express();

app.post('/api/stripe/create-checkout-session', async (req, res) => {
  const { priceId, customerEmail } = req.body;

  try {
    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      payment_method_types: ['card'],
      line_items: [{
        price: priceId,  // 从Stripe Dashboard创建的产品
        quantity: 1
      }],
      customer_email: customerEmail,
      success_url: 'https://yoursite.com/success?session_id={CHECKOUT_SESSION_ID}',
      cancel_url: 'https://yoursite.com/cancel',
      metadata: {
        order_id: 'ORDER-12345'  // 自定义订单标识
      }
    });

    res.json({ sessionId: session.id, url: session.url });
  } catch (error) {
    console.error('创建Checkout Session失败', error);
    res.status(500).json({ error: '创建会话失败' });
  }
});
```

### 前端跳转Checkout

```javascript
async function startCheckout() {
  const response = await fetch('/api/stripe/create-checkout-session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      priceId: 'price_xxx',
      customerEmail: 'customer@example.com'
    })
  });

  const { url } = await response.json();

  // 跳转到Stripe托管的Checkout页面
  window.location.href = url;
}
```

### Stripe Dashboard产品创建

1. 登录Stripe Dashboard
2. 进入Products页面
3. 点击"Add Product"创建产品
4. 获取产品的price ID

## Stripe Elements集成

### 引入Stripe.js

```html
<script src="https://js.stripe.com/v3/"></script>
```

### HTML结构

```html
<form id="payment-form">
  <div id="payment-element">
    <!-- Stripe Elements会在这里渲染 -->
  </div>
  <button id="submit">支付</button>
  <div id="error-message"></div>
</form>
```

### 初始化Stripe

```javascript
const stripe = Stripe('pk_test_xxx');

// 创建Elements实例
const elements = stripe.elements({
  appearance: {
    theme: 'stripe',
    variables: {
      colorPrimary: '#0f5132',
      colorBackground: '#ffffff',
      colorText: '#30313d',
      colorDanger: '#df1b41',
      fontFamily: 'system-ui, sans-serif',
      spacingUnit: '4px',
      borderRadius: '6px'
    }
  }
});

// 创建Payment Element
const paymentElement = elements.create('payment', {
  layout: 'tabs'  // tabs | accordion
});

paymentElement.mount('#payment-element');
```

### 处理支付

```javascript
const form = document.getElementById('payment-form');

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const { error } = await stripe.confirmPayment({
    elements,
    confirmParams: {
      return_url: 'https://yoursite.com/payment-result',
    },
    redirect: 'if_required'
  });

  if (error) {
    // 显示错误
    const errorMessage = document.getElementById('error-message');
    errorMessage.textContent = error.message;
  } else {
    // 支付成功
    // 由于redirect: 'if_required'，成功时不需要跳转
    alert('支付成功！');
  }
});
```

### PaymentIntent后端创建

```javascript
app.post('/api/stripe/create-payment-intent', async (req, res) => {
  const { amount, currency } = req.body;

  try {
    const paymentIntent = await stripe.paymentIntents.create({
      amount: amount,  // 单位：分
      currency: currency || 'cny',
      automatic_payment_methods: {
        enabled: true  // 自动启用Apple Pay、Google Pay等
      },
      metadata: {
        order_id: 'ORDER-12345'
      }
    });

    res.json({
      clientSecret: paymentIntent.client_secret
    });
  } catch (error) {
    console.error('创建PaymentIntent失败', error);
    res.status(500).json({ error: error.message });
  }
});
```

### 获取Client Secret并确认

```javascript
async function initializePayment() {
  // 从后端获取clientSecret
  const response = await fetch('/api/stripe/create-payment-intent', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ amount: 10000, currency: 'cny' })
  });

  const { clientSecret } = await response.json();

  // 使用clientSecret初始化Elements
  const stripe = Stripe('pk_test_xxx');
  const elements = stripe.elements({ clientSecret });

  const paymentElement = elements.create('payment');
  paymentElement.mount('#payment-element');
}
```

## 订阅支付（Subscriptions）

### 创建订阅Session

```javascript
app.post('/api/stripe/create-subscription-session', async (req, res) => {
  const { priceId, customerId } = req.body;

  try {
    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      payment_method_types: ['card'],
      line_items: [{
        price: priceId,
        quantity: 1
      }],
      customer: customerId,  // 可选，已有客户
      success_url: 'https://yoursite.com/subscription/success',
      cancel_url: 'https://yoursite.com/subscription/cancel'
    });

    res.json({ url: session.url });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

### 订阅Webhook处理

```javascript
app.post('/api/stripe/webhook', express.raw({ type: 'application/json' }), (req, res) => {
  const sig = req.headers['stripe-signature'];
  const webhookSecret = 'whsec_xxx';

  let event;

  try {
    event = stripe.webhooks.constructEvent(req.body, sig, webhookSecret);
  } catch (err) {
    console.error('Webhook签名验证失败', err.message);
    return res.sendStatus(400);
  }

  // 处理不同事件
  switch (event.type) {
    case 'checkout.session.completed':
      const session = event.data.object;
      handleCheckoutComplete(session);
      break;

    case 'customer.subscription.created':
      const subscription = event.data.object;
      handleSubscriptionCreated(subscription);
      break;

    case 'customer.subscription.updated':
      const updatedSub = event.data.object;
      handleSubscriptionUpdated(updatedSub);
      break;

    case 'customer.subscription.deleted':
      const deletedSub = event.data.object;
      handleSubscriptionDeleted(deletedSub);
      break;

    case 'invoice.payment_succeeded':
      const invoice = event.data.object;
      handleInvoicePaid(invoice);
      break;

    case 'invoice.payment_failed':
      const failedInvoice = event.data.object;
      handleInvoiceFailed(failedInvoice);
      break;
  }

  res.sendStatus(200);
});
```

## 高级功能

### 自定义样式

```javascript
const elements = stripe.elements({
  appearance: {
    theme: 'stripe',  // stripe | night | flat | none
    variables: {
      colorPrimary: '#5578EE',
      fontFamily: 'Open Sans, sans-serif',
      borderRadius: '8px',
      spacingUnit: '4px'
    },
    rules: {
      '.Input': {
        border: '1px solid #e0e0e0',
        boxShadow: 'none'
      },
      '.Input:focus': {
        border: '1px solid #5578EE',
        boxShadow: '0 0 0 2px rgba(85, 120, 238, 0.1)'
      },
      '.Label': {
        fontWeight: '500',
        marginBottom: '8px'
      }
    }
  }
});
```

### 展示多种支付方式

```javascript
const paymentElement = elements.create('payment', {
  layout: {
    type: 'tabs',
    defaultCollapsed: false
  },
  paymentMethodOrder: ['card', 'apple_pay', 'google_pay', 'alipay', 'wechat_pay']
});
```

### 中国特色支付

Stripe支持中国本地支付方式：

```javascript
// 添加支付宝和微信支付
const paymentElement = elements.create('payment', {
  paymentMethodTypes: ['card', 'alipay', 'wechat_pay']
});
```

### 3D Secure验证

Stripe自动处理3D Secure：

```javascript
const { error, paymentIntent } = await stripe.confirmPayment({
  elements,
  confirmParams: {
    return_url: 'https://yoursite.com/3ds-result'
  },
  redirect: 'if_required'
});
```

## 退款处理

### 全额退款

```javascript
app.post('/api/stripe/refund', async (req, res) => {
  const { paymentIntentId } = req.body;

  try {
    const refund = await stripe.refunds.create({
      payment_intent: paymentIntentId
    });

    res.json(refund);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

### 部分退款

```javascript
app.post('/api/stripe/refund-partial', async (req, res) => {
  const { paymentIntentId, amount } = req.body;

  try {
    const refund = await stripe.refunds.create({
      payment_intent: paymentIntentId,
      amount: amount  // 指定退款金额（分）
    });

    res.json(refund);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

## 客户管理

### 创建客户

```javascript
const customer = await stripe.customers.create({
  email: 'customer@example.com',
  name: '张三',
  metadata: {
    user_id: '12345'
  }
});
```

### 附加支付方式

```javascript
// 创建SetupIntent
app.post('/api/stripe/create-setup-intent', async (req, res) => {
  const { customerId } = req.body;

  const setupIntent = await stripe.setupIntents.create({
    customer: customerId,
    payment_method_types: ['card']
  });

  res.json({ clientSecret: setupIntent.client_secret });
});
```

## 沙箱测试

### 测试卡号

| 卡号 | 场景 | 说明 |
|------|------|------|
| 4242424242424242 | 成功 | 标准测试卡 |
| 4000002500003155 | 成功 | 需3D Secure |
| 4000000000000002 | 失败 | 通用失败 |
| 4000000000009995 | 失败 | 资金不足 |

### 测试触发

| 卡号后缀 | 触发场景 |
|----------|----------|
| 0002 | 通用卡片 decline |
| 9995 | 资金不足 decline |
| 0012 | 丢失卡 |
| 0014 | 盗窃卡 |

### 本地支付测试

| 支付方式 | 测试邮箱 |
|----------|----------|
| Alipay | test@alipay.com |
| WeChat Pay | mock_wechat_pay@mock.com |

## 常见问题

### PaymentIntent确认失败

1. 检查clientSecret是否正确
2. 确认金额和货币格式
3. 查看stripe面板的日志

### Webhook不触发

1. 确认webhook端点可公网访问
2. 检查webhook签名验证逻辑
3. 在Dashboard查看webhook历史

### CORS问题

Stripe.js需要确保：

```javascript
// 后端允许Stripe相关域名
app.use(cors({
  origin: ['https://checkout.stripe.com', 'https://js.stripe.com']
}));
```

### 货币支持

Stripe支持135+种货币，包括：

- CNY（人民币）
- USD（美元）
- EUR（欧元）
- GBP（英镑）
- HKD（港币）
- JPY（日元）

### 结算周期

Stripe默认结算周期为：

- 美国账户：2天
- 中国账户：7天

可在Dashboard调整结算设置。
