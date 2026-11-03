# 支付宝支付集成指南

本文档详细介绍如何在网页中集成支付宝支付功能，涵盖电脑网站支付、手机网站支付等场景。

## 准备工作

### 商户入驻

1. 访问支付宝开放平台（open.alipay.com）
2. 注册开发者账户
3. 创建应用并选择支付产品
4. 提交资质审核
5. 签约支付产品

### 必要凭证

入驻完成后，你将获得以下凭证：

| 凭证名称 | 说明 | 用途 |
|----------|------|------|
| APPID | 应用唯一标识 | 接口调用必需 |
| 支付宝公钥 | 支付宝提供的RSA公钥 | 验证支付宝签名 |
| 应用私钥 | 自己生成的RSA私钥 | 对请求签名 |
| 支付宝公钥证书 | X.509格式公钥证书 | 证书模式签名验证 |

## 接入方式选择

### 电脑网站支付（Web）

适用于PC端网页支付，用户在电脑上完成支付。

### 手机网站支付（H5）

适用于手机浏览器中的网页支付，支持唤起支付宝APP。

### 当面付

适用于扫码枪、扫码盒等场景。

## 技术集成

### 环境要求

- 服务器端：需要部署签名服务，禁止在前端暴露私钥
- 传输安全：必须使用HTTPS
- 字符编码：统一使用UTF-8

### SDK安装

**Node.js环境**：

```bash
npm install alipay-sdk
```

**Python环境**：

```bash
pip install alipay-sdk-python
```

### 签名机制

支付宝使用RSA或RSA2算法进行签名，推荐使用RSA2。

```javascript
const AlipaySdk = require('alipay-sdk').default;

const alipaySdk = new AlipaySdk({
  appId: 'your_app_id',
  privateKey: 'your_private_key', // 应用私钥
  alipayPublicKey: 'alipay_public_key', // 支付宝公钥
  signType: 'RSA2'
});
```

### 统一收单下单接口

```javascript
async function createAlipayOrder(req, res) {
  const { outTradeNo, totalAmount, subject, body } = req.body;

  const result = await alipaySdk.exec(
    'alipay.trade.page.pay',
    {
      method: 'POST',
      bizContent: {
        outTradeNo,       // 商户订单号
        productCode: 'FAST_INSTANT_TRADE_PAY', // 产品码
        totalAmount,      // 订单金额
        subject,          // 订单标题
        body,             // 订单描述
        goodsDetail: []   // 商品明细
      }
    },
    { returnUrl: 'https://yoursite.com/payment/return' }
  );

  res.json({ payUrl: result });
}
```

### 支付结果通知

```javascript
// POST /api/payment/alipay/notify
async function alipayNotify(req, res) {
  const params = req.body;
  const sign = params.sign;

  // 1. 验签
  const signVerified = alipaySdk.checkNotifySign(params);

  if (!signVerified) {
    return res.send('fail');
  }

  // 2. 处理业务逻辑
  const { outTradeNo, tradeStatus, tradeNo } = params;

  if (tradeStatus === 'TRADE_SUCCESS' || tradeStatus === 'TRADE_FINISHED') {
    // 更新订单状态
    await updateOrderStatus(outTradeNo, 'paid', tradeNo);
  }

  // 3. 响应
  res.send('success');
}
```

### 订单查询

```javascript
async function queryAlipayOrder(outTradeNo) {
  const result = await alipaySdk.exec('alipay.trade.query', {
    bizContent: { outTradeNo }
  });

  return result;
}
```

### 退款接口

```javascript
async function refundOrder(outTradeNo, refundAmount, refundReason) {
  const result = await alipaySdk.exec('alipay.trade.refund', {
    bizContent: {
      outTradeNo,
      refundAmount,
      refundReason,
      outRequestNo: outTradeNo + '_refund'
    }
  });

  return result;
}
```

## 前端实现

### 支付表单提交

```html
<form name="punchout_form" action="<%= payUrl %>" method="post" id="alipayForm">
  <input type="hidden" name="biz_content" value="">
</form>
<script>document.getElementById('alipayForm').submit();</script>
```

### 手机浏览器H5支付

```javascript
// 唤起支付宝APP支付
function h5Pay(payUrl) {
  window.location.href = payUrl;
}
```

### 回调页面处理

```javascript
// 支付完成后跳转回网站的页面
function handleReturn() {
  const urlParams = new URLSearchParams(window.location.search);
  const outTradeNo = urlParams.get('out_trade_no');

  // 查询订单状态确认支付结果
  checkOrderStatus(outTradeNo);
}
```

## 沙箱测试

### 切换沙箱环境

1. 下载沙箱版支付宝APP
2. 获取沙箱版支付宝开放平台密钥
3. 在代码中配置沙箱网关

```javascript
const alipaySdk = new AlipaySdk({
  appId: 'your_sandbox_app_id',
  privateKey: 'your_sandbox_private_key',
  alipayPublicKey: 'sandbox_alipay_public_key',
  signType: 'RSA2',
  gateway: 'https://openapi.alipaydev.com/gateway.do' // 沙箱网关
});
```

### 沙箱工具

- 沙箱钱包APP：用于模拟支付
- 沙箱控制台：查看接口调用日志

## 常见问题

### 提示"订单信息有误"

检查以下内容：

1. 订单金额格式是否正确（最多2位小数）
2. 异步通知地址是否配置正确
3. 签名算法是否与签约算法一致

### 回调验签失败

1. 确认支付宝公钥是否正确（注意是支付宝公钥而非应用公钥）
2. 检查编码格式是否为UTF-8
3. 验签时是否正确处理了sign和sign_type参数

### 支付成功但未收到回调

1. 检查异步通知地址是否公网可达
2. 确认服务器防火墙是否放行80/443端口
3. 检查服务器响应时间是否超过30秒

### RSA2签名失败

1. 确认私钥格式正确（PKCS8格式更稳定）
2. 检查签名参数是否按ASCII码排序
3. 确保不含空值或多余空格
