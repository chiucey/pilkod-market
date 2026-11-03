---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502210080ce42a1082d5e897ed44ca45c5be58ce76fcac9df75e865d4a498f9d2e3fe0302207e70d8e5519f8d504446f4e0587d9be54a83711471506e767f0a79176d6b5525
    ReservedCode2: 304402205e2a7847ee774107879ebbbaa16d4fca998ecd967378b8b9a8a800409a9c5858022010827704caaebf162ad8c045beaa37767007a96795c125dbebeeef2c3bf65d73
---

# zshlpay API 规范文档

## 概述

本文档定义了zshlpay Spring Cloud项目中各服务之间的API接口规范。

## 服务端口映射

| 服务 | 端口 | 上下文路径 | 说明 |
|------|------|-----------|------|
| Gateway | 8080 | / | API网关统一入口 |
| Service | 8081 | / | 支付核心服务 |
| Admin | 8082 | / | 管理后台 |
| Shop | 8083 | / | 商户平台 |

## 网关路由规则

```
/api/service/*  -> zshlpay-service:8081
/api/admin/*     -> zshlpay-admin:8082
/api/shop/*      -> zshlpay-shop:8083
```

## 统一响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {},
  "timestamp": 1704067200000,
  "requestId": "uuid-string"
}
```

### 错误响应
```json
{
  "code": 500,
  "message": "错误描述",
  "data": null,
  "timestamp": 1704067200000,
  "requestId": "uuid-string"
}
```

### 常见状态码
| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## Service 服务 API

### 1. 支付相关

#### 创建支付订单
```
POST /pay/create
Content-Type: application/json

Request:
{
  "orderNo": "ORDER20240101123456",
  "amount": 100.00,
  "subject": "商品名称",
  "body": "商品描述",
  "channelCode": "WECHAT_APP",
  "notifyUrl": "https://example.com/notify",
  "returnUrl": "https://example.com/return"
}

Response:
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "tradeNo": "PAY20240101123456",
    "payUrl": "weixin://wxpay/...",
    "qrCode": "base64..."
  }
}
```

#### 支付回调
```
POST /pay/notify/{channelCode}
Content-Type: application/x-www-form-urlencoded 或 application/json

Request:
{
  "tradeNo": "PAY20240101123456",
  "status": "SUCCESS",
  "amount": 100.00,
  "transactionId": "微信订单号",
  "sign": "签名"
}
```

#### 查询支付状态
```
GET /pay/query/{tradeNo}

Response:
{
  "code": 200,
  "data": {
    "tradeNo": "PAY20240101123456",
    "orderNo": "ORDER20240101123456",
    "status": "SUCCESS",
    "amount": 100.00,
    "channelCode": "WECHAT_APP",
    "payTime": "2024-01-01 12:00:00"
  }
}
```

#### 申请退款
```
POST /pay/refund

Request:
{
  "tradeNo": "PAY20240101123456",
  "refundNo": "REFUND20240101123456",
  "refundAmount": 50.00,
  "reason": "用户申请退款"
}

Response:
{
  "code": 200,
  "data": {
    "refundNo": "REFUND20240101123456",
    "refundAmount": 50.00,
    "status": "PROCESSING"
  }
}
```

### 2. 订单相关

#### 查询订单列表
```
GET /order/list
Query: page=1&size=10&status=PAID

Response:
{
  "code": 200,
  "data": {
    "records": [...],
    "total": 100,
    "page": 1,
    "size": 10
  }
}
```

#### 订单详情
```
GET /order/{orderNo}

Response:
{
  "code": 200,
  "data": {
    "orderNo": "ORDER20240101123456",
    "amount": 100.00,
    "status": "PAID",
    "channelCode": "WECHAT_APP",
    "createTime": "2024-01-01 12:00:00",
    "payTime": "2024-01-01 12:01:00"
  }
}
```

### 3. 商户相关

#### 商户入驻
```
POST /merchant/register

Request:
{
  "merchantName": "商户名称",
  "contactName": "联系人",
  "contactPhone": "13800138000",
  "businessLicense": "营业执照号",
  "settlementType": "T1"
}
```

#### 商户登录
```
POST /merchant/login

Request:
{
  "merchantNo": "M20240101001",
  "password": "encrypted_password"
}

Response:
{
  "code": 200,
  "data": {
    "token": "jwt_token",
    "merchantNo": "M20240101001",
    "merchantName": "商户名称"
  }
}
```

## Admin 服务 API

### 1. 商户管理

#### 商户列表
```
GET /admin/merchant/list
Query: page=1&size=10&status=ENABLE

Response:
{
  "code": 200,
  "data": {
    "records": [
      {
        "merchantNo": "M20240101001",
        "merchantName": "商户名称",
        "status": "ENABLE",
        "balance": 10000.00
      }
    ]
  }
}
```

#### 商户审核
```
POST /admin/merchant/audit

Request:
{
  "merchantNo": "M20240101001",
  "auditStatus": "PASS",
  "auditRemark": "审核通过"
}
```

### 2. 通道管理

#### 通道列表
```
GET /admin/channel/list

Response:
{
  "code": 200,
  "data": [
    {
      "channelCode": "WECHAT_APP",
      "channelName": "微信支付-APP",
      "status": "ENABLE",
      "rate": 0.006
    }
  ]
}
```

#### 配置通道
```
POST /admin/channel/config

Request:
{
  "channelCode": "WECHAT_APP",
  "appId": "wx_configured_appid",
  "mchId": "configured_mchid",
  "apiKey": "configured_apikey",
  "status": "ENABLE"
}
```

### 3. 交易统计

#### 交易报表
```
GET /admin/stat/trade
Query: startDate=2024-01-01&endDate=2024-01-31&merchantNo=M20240101001

Response:
{
  "code": 200,
  "data": {
    "totalAmount": 1000000.00,
    "totalCount": 10000,
    "successAmount": 990000.00,
    "successCount": 9900,
    "refundAmount": 10000.00,
    "refundCount": 100
  }
}
```

## Shop 服务 API

### 1. 商户自服务

#### 商户信息
```
GET /shop/merchant/info

Response:
{
  "code": 200,
  "data": {
    "merchantNo": "M20240101001",
    "merchantName": "商户名称",
    "balance": 10000.00,
    "frozenAmount": 1000.00
  }
}
```

#### 结算记录
```
GET /shop/settlement/list
Query: page=1&size=10

Response:
{
  "code": 200,
  "data": {
    "records": [
      {
        "settlementNo": "SETTLE20240101001",
        "amount": 1000.00,
        "status": "SUCCESS",
        "createTime": "2024-01-01 12:00:00"
      }
    ]
  }
}
```

#### 门店管理
```
POST /shop/store/add

Request:
{
  "storeName": "门店名称",
  "storeAddress": "门店地址",
  "contactPhone": "13800138000"
}
```

## Feign 客户端接口定义

### PayFeignClient
```java
@FeignClient(name = "zshlpay-service", path = "/pay")
public interface PayFeignClient {

    @PostMapping("/create")
    Result<PayResponse> createPay(@RequestBody PayRequest request);

    @GetMapping("/query/{tradeNo}")
    Result<PayQueryResponse> queryPay(@PathVariable("tradeNo") String tradeNo);

    @PostMapping("/refund")
    Result<RefundResponse> refund(@RequestBody RefundRequest request);
}
```

### OrderFeignClient
```java
@FeignClient(name = "zshlpay-service", path = "/order")
public interface OrderFeignClient {

    @GetMapping("/list")
    Result<PageResult<OrderDTO>> listOrders(@RequestParam Map<String, Object> params);

    @GetMapping("/{orderNo}")
    Result<OrderDTO> getOrder(@PathVariable("orderNo") String orderNo);
}
```

### MerchantFeignClient
```java
@FeignClient(name = "zshlpay-service", path = "/merchant")
public interface MerchantFeignClient {

    @GetMapping("/info/{merchantNo}")
    Result<MerchantDTO> getMerchantInfo(@PathVariable("merchantNo") String merchantNo);

    @GetMapping("/balance/{merchantNo}")
    Result<BigDecimal> getBalance(@PathVariable("merchantNo") String merchantNo);
}
```

## 认证与授权

### JWT Token

请求头格式：
```
Authorization: Bearer <jwt_token>
```

Token Payload：
```json
{
  "sub": "user_id",
  "merchantNo": "M20240101001",
  "roles": ["MERCHANT", "ADMIN"],
  "exp": 1704153600
}
```

### 权限控制

| 角色 | 权限范围 |
|------|----------|
| MERCHANT | 商户自服务API |
| ADMIN | 管理后台API |
| SUPER_ADMIN | 系统管理API |

## 错误码定义

| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| PAY_001 | 支付创建失败 | 创建支付订单失败 |
| PAY_002 | 支付超时 | 支付超过有效期 |
| PAY_003 | 支付金额不符 | 实际金额与订单不符 |
| PAY_004 | 通道不可用 | 支付通道未启用或维护中 |
| ORDER_001 | 订单不存在 | 订单号不存在 |
| ORDER_002 | 订单已支付 | 订单已支付，不能重复操作 |
| ORDER_003 | 订单已关闭 | 订单已关闭 |
| MERCHANT_001 | 商户不存在 | 商户号不存在 |
| MERCHANT_002 | 商户未审核 | 商户状态不是已审核 |
| MERCHANT_003 | 商户已禁用 | 商户已被禁用 |

## 版本历史

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| 1.0.0 | 2024-01-01 | 初始版本 |
