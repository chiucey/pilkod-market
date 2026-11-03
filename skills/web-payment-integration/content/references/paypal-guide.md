# PayPal支付集成指南

本文档详细介绍如何在网页中集成PayPal支付功能，支持Checkout、Subscriptions等多种支付模式。

## 准备工作

### 开发者账户

1. 访问PayPal开发者平台（developer.paypal.com）
2. 使用PayPal账户登录
3. 进入Dashboard创建应用

### 必要凭证

| 环境 | 客户端ID | 说明 |
|------|----------|------|
| Sandbox | 自动生成 | 测试环境使用 |
| Live | 需申请 | 生产环境使用 |

### 沙箱账户

在Developer Dashboard可以创建测试用的Buyer和Seller账户：

- Buyer账户：用于模拟付款的用户
- Seller账户：用于接收付款的商户

## 支付模式选择

### Checkout

适合一次性付款场景，如商品购买。

### Subscriptions

适合订阅制服务，按周期自动扣费。

### Invoicing

适合开具发票场景。

## 技术集成

### Checkout JS SDK

最推荐的集成方式，通过PayPal官方JS SDK实现。

```html
<!-- 引入PayPal SDK -->
<script src="https://www.paypal.com/sdk/js?client-id=YOUR_CLIENT_ID&currency=USD"></script>
```

### 环境切换

```html
<!-- Sandbox环境 -->
<script src="https://www.paypal.com/sdk/js?client-id=sb&currency=USD"></script>

<!-- Live环境 -->
<script src="https://www.paypal.com/sdk/js?client-id=YOUR_LIVE_CLIENT_ID&currency=USD"></script>
```

### 基础Checkout集成

#### HTML结构

```html
<div id="paypal-button-container"></div>
<div id="card-button-container"></div>
```

#### JavaScript实现

```javascript
// 渲染PayPal按钮
paypal.Buttons({
  // 创建订单
  createOrder: function(data, actions) {
    return fetch('/api/paypal/create-order', {
      method: 'post',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        amount: document.getElementById('amount').value
      })
    })
    .then(function(res) {
      return res.json();
    })
    .then(function(orderData) {
      // 返回订单ID
      return orderData.orderID;
    });
  },

  // 支付授权
  onApprove: function(data, actions) {
    return fetch('/api/paypal/capture-order', {
      method: 'post',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        orderID: data.orderID
      })
    })
    .then(function(res) {
      return res.json();
    })
    .then(function(details) {
      // 支付成功，显示确认
      alert('交易完成！订单号: ' + details.purchase_units[0].payments.captures[0].id);
    });
  },

  // 支付失败
  onError: function(err) {
    console.error('支付错误:', err);
    alert('支付过程中出现错误，请重试');
  }
}).render('#paypal-button-container');
```

### 服务器端实现

#### Node.js + Express

```javascript
const paypal = require('@paypal/checkout-server-sdk');

// 配置环境
let environment = new paypal.core.SandboxEnvironment(
  'YOUR_SANDBOX_CLIENT_ID',
  'YOUR_SANDBOX_CLIENT_SECRET'
);

if (process.env.NODE_ENV === 'production') {
  environment = new paypal.core.LiveEnvironment(
    'YOUR_LIVE_CLIENT_ID',
    'YOUR_LIVE_CLIENT_SECRET'
  );
}

const client = new paypal.core.PayPalHttpClient(environment);

// 创建订单
app.post('/api/paypal/create-order', async (req, res) => {
  const { amount } = req.body;

  const request = new paypal.orders.OrdersCreateRequest();
  request.requestBody({
    intent: 'CAPTURE',
    purchase_units: [{
      amount: {
        currency_code: 'USD',
        value: amount
      }
    }]
  });

  try {
    const order = await client.execute(request);
    res.json({ orderID: order.result.id });
  } catch (error) {
    console.error('创建订单失败', error);
    res.status(500).json({ error: '订单创建失败' });
  }
});

// 捕获订单（完成支付）
app.post('/api/paypal/capture-order', async (req, res) => {
  const { orderID } = req.body;

  const request = new paypal.orders.OrdersCaptureRequest(orderID);
  request.requestBody({});

  try {
    const capture = await client.execute(request);
    // 支付成功，更新订单状态
    await updateOrderStatus(capture.result.purchase_units[0].reference_id);
    res.json(capture.result);
  } catch (error) {
    console.error('捕获订单失败', error);
    res.status(500).json({ error: '支付确认失败' });
  }
});
```

### 订阅支付集成

适用于SaaS类产品的定期订阅。

```javascript
// 创建订阅
paypal.Buttons({
  createSubscription: function(data, actions) {
    return actions.subscription.create({
      plan_id: 'P-XXXXXXXXXXXXXXXXXXX', // 订阅计划ID
      quantity: 1
    });
  },
  onApprove: function(data, actions) {
    // 订阅创建成功
    alert('订阅创建成功，订阅ID: ' + data.subscriptionID);
  }
}).render('#paypal-subscribe-button');
```

### 信用卡支付

启用信用卡支付需要额外配置：

```javascript
paypal.Buttons({
  createOrder: function(data, actions) {
    // ...
  },
  onApprove: function(data, actions) {
    // ...
  },
  style: {
    layout: 'vertical',
    color: 'gold',
    shape: 'rect',
    label: 'paypal'
  }
}).render('#paypal-button-container');

// 渲染信用卡按钮
paypal.Buttons({
  style: {
    layout: 'vertical',
    color: 'black',
    shape: 'rect',
    label: 'card'
  }
}).render('#card-button-container');
```

## 高级功能

### 自定义按钮样式

```javascript
paypal.Buttons({
  style: {
    layout: 'horizontal',  // horizontal | vertical
    size: 'responsive',    // small | medium | large | responsive
    color: 'gold',         // gold | blue | silver | black
    shape: 'rect',         // rect | pill
    label: 'pay',          // pay | checkout | buy now | paypal
    tagline: true          // true | false
  }
}).render('#paypal-button-container');
```

### 运费和税费计算

```javascript
createOrder: function(data, actions) {
  return fetch('/api/paypal/create-order', {
    method: 'post',
    body: JSON.stringify({
      amount: '100.00',
      shipping: '10.00',
      tax: '8.00'
    })
  })
  .then(res => res.json())
  .then(order => order.orderID);
}
```

### 折扣和优惠券

```javascript
createOrder: function(data, actions) {
  return fetch('/api/paypal/create-order', {
    method: 'post',
    body: JSON.stringify({
      amount: '100.00',
      discount: '20.00'  // 折扣金额
    })
  })
  .then(res => res.json())
  .then(order => order.orderID);
}
```

### 订单详情传递

```javascript
createOrder: function(data, actions) {
  return fetch('/api/paypal/create-order', {
    method: 'post',
    body: JSON.stringify({
      amount: '100.00',
      custom_id: 'ORDER-12345',  // 自定义订单号
      invoice_id: 'INV-001',      // 发票号
      description: '商品描述'
    })
  })
  .then(res => res.json())
  .then(order => order.orderID);
}
```

## 退款处理

### 部分退款

```javascript
app.post('/api/paypal/refund', async (req, res) => {
  const { captureId, amount } = req.body;

  const request = new paypal.payments.CapturesRefundRequest(captureId);
  request.requestBody({
    amount: {
      value: amount,
      currency_code: 'USD'
    }
  });

  try {
    const refund = await client.execute(request);
    res.json(refund.result);
  } catch (error) {
    console.error('退款失败', error);
    res.status(500).json({ error: '退款失败' });
  }
});
```

### 全额退款

```javascript
app.post('/api/paypal/refund-full', async (req, res) => {
  const { captureId } = req.body;

  const request = new paypal.payments.CapturesRefundRequest(captureId);
  request.requestBody({});

  try {
    const refund = await client.execute(request);
    res.json(refund.result);
  } catch (error) {
    console.error('退款失败', error);
    res.status(500).json({ error: '退款失败' });
  }
});
```

## 沙箱测试

### 测试场景

| 测试卡号 | 场景 | CVV | 过期日期 |
|----------|------|-----|----------|
| 4032031111111111 | 成功 | 任何3位 | 任何未来日期 |
| 4000000000000002 | 失败-通用 | 任何3位 | 任何未来日期 |
| 4000000000009995 | 失败-不足 | 任何3位 | 任何未来日期 |

### 测试账户

在Developer Dashboard可以：

1. 创建测试用Buyer账户
2. 创建测试用Business账户
3. 模拟各种支付场景

### IPN测试

PayPal IPN（即时付款通知）测试：

1. 启用沙箱IPN模拟器
2. 在订单中配置IPN通知URL
3. 查看IPN历史记录

## Webhook集成

### 设置Webhook

```javascript
app.post('/api/paypal/webhook', (req, res) => {
  const webhookId = 'YOUR_WEBHOOK_ID';

  // 验证webhook签名
  const verified = verifyWebhookSignature(req, webhookId);

  if (verified) {
    const event = req.body;

    switch (event.event_type) {
      case 'PAYMENT.CAPTURE.COMPLETED':
        // 处理支付成功
        handlePaymentComplete(event);
        break;
      case 'PAYMENT.CAPTURE.DENIED':
        // 处理支付被拒
        handlePaymentDenied(event);
        break;
      case 'CHECKOUT.ORDER.APPROVED':
        // 处理订单授权
        handleOrderApproved(event);
        break;
    }

    res.sendStatus(200);
  } else {
    res.sendStatus(400);
  }
});
```

## 常见问题

### SDK加载失败

1. 检查网络连接
2. 确认client-id正确
3. 检查浏览器是否阻止了PayPal域名

### 按钮不显示

1. 确认SDK加载成功
2. 检查DOM元素是否存在
3. 查看控制台错误信息

### 支付后无法回调

1. 确认onApprove函数正常执行
2. 检查网络请求是否被阻止
3. 验证服务器端点可访问

### 货币问题

```javascript
// 在SDK中指定货币
<script src="https://www.paypal.com/sdk/js?client-id=YOUR_ID&currency=EUR"></script>

// 支持的货币
// USD, EUR, GBP, CAD, AUD, JPY, CNY, etc.
```

### 跨境收款

1. 确保账户已完成跨境收款资质认证
2. 在Dashboard配置收款账户
3. 了解目标国家的支付法规
