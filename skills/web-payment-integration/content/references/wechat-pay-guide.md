# 微信支付集成指南

本文档详细介绍如何在网页中集成微信支付功能，支持JSAPI支付、H5支付、Native支付等多种场景。

## 准备工作

### 商户入驻

1. 访问微信商户平台（pay.weixin.qq.com）
2. 完成商户资质认证
3. 申请微信支付产品
4. 获取商户号（mch_id）

### 必要凭证

| 凭证名称 | 说明 | 用途 |
|----------|------|------|
| mch_id | 商户号 | 接口调用必需 |
| appid | 微信公众号ID | JSAPI支付必需 |
| api_key | API密钥 | 签名验证 |
| cert | SSL证书 | 退款等安全操作 |
| apiv3_key | APIv3密钥 | v3版本接口 |

### 证书申请

1. 登录商户平台
2. 进入账户中心 → API安全
3. 申请证书
4. 下载证书文件（apiclient_cert.p12 或 apiclient_cert.pem）

## 支付场景选择

### JSAPI支付

适用于已绑定微信公众号的网页支付，用户需微信内访问。

### H5支付

适用于手机浏览器网页支付，可唤起微信支付。

### Native支付

适用于PC网站，生成二维码供用户扫码支付。

### 小程序支付

适用于微信小程序内支付。

## 技术集成

### 环境要求

- 服务器端：必须使用HTTPS
- 域名备案：H5支付要求网页域名已备案
- 证书配置：退款等操作需要双向SSL证书

### SDK安装

**Node.js环境**：

```bash
npm install wechat-pay
# 或使用官方SDK
npm install wxpay-sdk
```

**Java环境**：

```xml
<dependency>
    <groupId>com.github.wxpay</groupId>
    <artifactId>wxpay-sdk</artifactId>
    <version>0.0.3</version>
</dependency>
```

### JSAPI支付集成

JSAPI支付需要先获取用户openid。

#### 第一步：获取OpenId

```javascript
// 后端：生成授权URL
function getOpenIdUrl(appId, redirectUri, state) {
  const baseUrl = 'https://open.weixin.qq.com/connect/oauth2/authorize';
  const params = new URLSearchParams({
    appid: appId,
    redirect_uri: redirectUri,
    response_type: 'code',
    scope: 'snsapi_base', // 或 snsapi_userinfo
    state: state || 'STATE'
  });

  return `${baseUrl}?${params.toString()}#wechat_redirect`;
}

// 前端：引导用户访问授权链接
window.location.href = '/api/wechat/get-openid-url';
```

#### 第二步：获取用户OpenId

```javascript
// 后端：交换code获取openid
async function codeToOpenId(code) {
  const appId = 'your_appid';
  const secret = 'your_appsecret';

  const url = `https://api.weixin.qq.com/sns/oauth2/access_token?appid=${appId}&secret=${secret}&code=${code}&grant_type=authorization_code`;

  const response = await fetch(url);
  const data = await response.json();

  return data.openid;
}
```

#### 第三步：统一下单

```javascript
async function unifiedOrder(req, res) {
  const { openid, totalFee, orderId, description } = req.body;

  const params = {
    appid: config.appId,
    mch_id: config.mchId,
    nonce_str: generateNonceStr(),
    body: description,
    out_trade_no: orderId,
    total_fee: totalFee, // 单位：分
    spbill_create_ip: req.ip,
    notify_url: 'https://yoursite.com/api/wechat/notify',
    trade_type: 'JSAPI',
    openid: openid
  };

  // 签名
  params.sign = signParams(params, config.apiKey);

  // 调用统一下单接口
  const result = await postXml('https://api.mch.weixin.qq.com/pay/unifiedorder', params);

  if (result.result_code === 'SUCCESS') {
    // 生成调起支付的参数
    const payParams = {
      appId: config.appId,
      timeStamp: Math.floor(Date.now() / 1000).toString(),
      nonceStr: generateNonceStr(),
      package: `prepay_id=${result.prepay_id}`,
      signType: 'MD5'
    };
    payParams.paySign = signParams(payParams, config.apiKey);

    res.json(payParams);
  } else {
    res.status(400).json({ error: result.err_code_des });
  }
}
```

#### 第四步：前端调起支付

```javascript
function wechatJSPay(payParams) {
  if (typeof WeixinJSBridge === 'undefined') {
    // 微信内置浏览器
    document.addEventListener('WeixinJSBridgeReady', () => {
      callPay(payParams);
    });
  } else {
    callPay(payParams);
  }

  function callPay(params) {
    WeixinJSBridge.invoke('getBrandWCPayRequest', {
      appId: params.appId,
      timeStamp: params.timeStamp,
      nonceStr: params.nonceStr,
      package: params.package,
      signType: params.signType,
      paySign: params.paySign
    }, function(res) {
      if (res.err_msg === 'get_brand_wcpay_request:ok') {
        // 支付成功
        window.location.href = '/order/success?orderId=' + params.out_trade_no;
      } else if (res.err_msg === 'get_brand_wcpay_request:cancel') {
        // 用户取消
        console.log('用户取消支付');
      } else {
        // 支付失败
        alert('支付失败：' + res.err_msg);
      }
    });
  }
}
```

### H5支付集成

H5支付适用于手机浏览器，不依赖微信公众号。

#### 特殊配置

需要在商户平台开通H5支付，并配置支付域名。

#### 统一下单

```javascript
async function h5UnifiedOrder(req, res) {
  const { totalFee, orderId, description, h5Info } = req.body;

  const params = {
    appid: config.appId,
    mch_id: config.mchId,
    nonce_str: generateNonceStr(),
    body: description,
    out_trade_no: orderId,
    total_fee: totalFee,
    spbill_create_ip: req.ip,
    notify_url: 'https://yoursite.com/api/wechat/notify',
    trade_type: 'MWEB',
    scene_info: JSON.stringify({
      h5_info: {
        type: 'Wap',
        app_name: '您的应用名称',
        bundle_id: 'com.yourcompany.app'
      }
    })
  };

  params.sign = signParams(params, config.apiKey);

  const result = await postXml('https://api.mch.weixin.qq.com/pay/unifiedorder', params);

  if (result.result_code === 'SUCCESS') {
    res.json({ mweb_url: result.mweb_url });
  }
}
```

#### 前端跳转

```javascript
function startH5Pay(mwebUrl) {
  // 跳转到微信中间页
  window.location.href = mwebUrl;
}
```

### Native支付集成

Native支付生成二维码，适合PC网站。

#### 统一下单

```javascript
async function nativeUnifiedOrder(req, res) {
  const { totalFee, orderId, description } = req.body;

  const params = {
    appid: config.appId,
    mch_id: config.mchId,
    nonce_str: generateNonceStr(),
    body: description,
    out_trade_no: orderId,
    total_fee: totalFee,
    spbill_create_ip: req.ip,
    notify_url: 'https://yoursite.com/api/wechat/notify',
    trade_type: 'NATIVE',
    product_id: orderId
  };

  params.sign = signParams(params, config.apiKey);

  const result = await postXml('https://api.mch.weixin.qq.com/pay/unifiedorder', params);

  if (result.result_code === 'SUCCESS') {
    res.json({ code_url: result.code_url });
  }
}
```

#### 生成二维码

```html
<div id="qrcode"></div>

<script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>
<script>
  function showQRCode(codeUrl) {
    new QRCode(document.getElementById('qrcode'), {
      text: codeUrl,
      width: 200,
      height: 200
    });
  }
</script>
```

### 支付结果通知

```javascript
async function wechatNotify(req, res) {
  // 解析XML通知
  const xmlData = req.body;
  const params = parseXml(xmlData);

  // 验证签名
  const sign = params.sign;
  delete params.sign;

  const calculatedSign = signParams(params, config.apiKey);

  if (calculatedSign !== sign) {
    return res.send('<xml><return_code><![CDATA[FAIL]]></return_code></xml>');
  }

  // 处理支付结果
  if (params.return_code === 'SUCCESS' && params.result_code === 'SUCCESS') {
    const { out_trade_no, transaction_id } = params;

    // 更新订单状态
    await updateOrderStatus(out_trade_no, 'paid', transaction_id);
  }

  // 回复微信
  res.send('<xml><return_code><![CDATA[SUCCESS]]></return_code></xml>');
}
```

### 签名函数

```javascript
function signParams(params, apiKey) {
  const sortedKeys = Object.keys(params).sort();
  const signStr = sortedKeys
    .filter(key => params[key] !== '' && params[key] !== undefined)
    .map(key => `${key}=${params[key]}`)
    .join('&');

  return crypto
    .createHash('md5')
    .update(signStr + '&key=' + apiKey)
    .digest('hex')
    .toUpperCase();
}

function generateNonceStr() {
  return crypto.randomBytes(16).toString('hex');
}
```

## 沙箱测试

### 切换沙箱环境

微信支付提供沙箱环境用于测试。

```javascript
// 获取沙箱API密钥
async function getSandboxKey() {
  const params = {
    mch_id: config.mchId,
    nonce_str: generateNonceStr()
  };
  params.sign = signParams(params, config.apiKey);

  const result = await postXml(
    'https://api.mch.weixin.qq.com/sandboxnew/pay/getsignkey',
    params
  );

  return result.sandbox_signkey;
}
```

### 测试用例

| 场景 | 预期结果 |
|------|----------|
| 正常支付 | 支付成功，收到回调 |
| 用户取消 | 返回取消状态 |
| 超时未支付 | 订单自动关闭 |
| 金额错误 | 签名校验失败 |

## 常见问题

### JSAPI提示"支付验证签名失败"

1. 检查调起支付时的签名是否正确
2. 确保timeStamp为字符串类型
3. 确认package参数格式为prepay_id=xxx

### H5支付提示"商户需配置授权域名"

1. 在商户平台H5支付配置中添加授权域名
2. 确保域名已ICP备案
3. 检查referer是否正确

### Native支付code_url为空

1. 检查product_id是否传递
2. 确认交易类型配置正确
3. 查看商户平台是否开通Native支付

### 回调通知失败

1. 确认notify_url公网可达
2. 检查SSL证书配置
3. 确保服务器能在5秒内返回SUCCESS

### 退款失败

1. 确认证书路径正确
2. 检查退款金额是否超过可退金额
3. 验证证书权限
