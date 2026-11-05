---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 30450220545c499f3c7f8013cde894e574a10bf55b28a8974dcc113b20bc1ce2c084c8410221009fc25123eaaff6767c3c1bf87c7b4240e00946d2bec8511027858f9ed7c2d71f
    ReservedCode2: 3046022100a694cd377ff600f45c4a45f687948e8dee4dcb9d7c9a47ff3be9e95f982f18fc022100e9922ff0ee332cb635eec45c7affb208b65bd556f0c756f96ae07b3cb95f3f6a
---

# zshlpay Spring Cloud 工程包结构指南

## 概述

本文档为开发者提供标准的包结构和类创建规范，确保项目代码的一致性和可维护性。

## 完整包结构

```
com.zshlpay
│
├── common/                           # 公共模块
│   ├── result/                       # 统一响应
│   │   ├── Result.java              # 统一响应封装
│   │   └── ResultCode.java          # 响应码枚举
│   ├── exception/                    # 异常处理
│   │   ├── BizException.java        # 业务异常
│   │   └── GlobalExceptionHandler.java # 全局异常处理
│   ├── enums/                        # 枚举类
│   │   ├── PayStatusEnum.java       # 支付状态枚举
│   │   ├── ChannelTypeEnum.java    # 通道类型枚举
│   │   └── MerchantStatusEnum.java # 商户状态枚举
│   ├── constant/                     # 常量
│   │   ├── PayConstant.java        # 支付相关常量
│   │   └── CacheConstant.java      # 缓存Key常量
│   └── config/                       # 配置类
│       ├── MyBatisPlusConfig.java   # MyBatis-Plus配置
│       ├── RedisConfig.java         # Redis配置
│       ├── SwaggerConfig.java       # Swagger配置
│       └── JacksonConfig.java       # Jackson配置
│
├── util/                             # 工具模块
│   ├── date/                         # 日期工具
│   │   └── DateUtil.java
│   ├── encrypt/                      # 加密工具
│   │   ├── AESUtil.java
│   │   ├── RSAUtil.java
│   │   └── MD5Util.java
│   ├── http/                         # HTTP工具
│   │   └── HttpUtil.java
│   ├── string/                       # 字符串工具
│   │   └── StringUtil.java
│   ├── id/                           # ID生成工具
│   │   └── IdGenerator.java
│   └── qrcode/                       # 二维码工具
│       └── QRCodeUtil.java
│
├── api/                              # API模块
│   ├── client/                       # Feign客户端
│   │   ├── PayFeignClient.java
│   │   ├── MerchantFeignClient.java
│   │   └── OrderFeignClient.java
│   ├── fallback/                     # Feign降级
│   │   ├── PayFeignFallback.java
│   │   └── MerchantFeignFallback.java
│   ├── dto/                          # 传输对象
│   │   ├── PayRequest.java
│   │   ├── PayResponse.java
│   │   ├── RefundRequest.java
│   │   └── RefundResponse.java
│   └── config/                       # Feign配置
│       └── FeignConfig.java
│
├── gateway/                          # 网关模块
│   ├── filter/                       # 过滤器
│   │   ├── AuthFilter.java          # 认证过滤器
│   │   ├── RateLimitFilter.java     # 限流过滤器
│   │   └── LogFilter.java           # 日志过滤器
│   ├── handler/                      # 处理器
│   │   └── GlobalErrorHandler.java  # 全局错误处理
│   └── config/                       # 网关配置
│       └── GatewayConfig.java
│
├── service/                          # 服务模块（核心业务）
│   ├── controller/                    # 控制器
│   │   ├── PayController.java
│   │   ├── OrderController.java
│   │   └── MerchantController.java
│   ├── service/                      # 服务接口
│   │   ├── PayService.java
│   │   ├── OrderService.java
│   │   ├── MerchantService.java
│   │   └── impl/                     # 服务实现
│   │       ├── PayServiceImpl.java
│   │       ├── OrderServiceImpl.java
│   │       └── MerchantServiceImpl.java
│   ├── mapper/                        # 数据访问层
│   │   ├── PayOrderMapper.java
│   │   ├── PayRefundMapper.java
│   │   └── MerchantMapper.java
│   ├── entity/                        # 实体类
│   │   ├── PayOrder.java
│   │   ├── PayRefund.java
│   │   └── Merchant.java
│   ├── dto/                           # 数据传输对象
│   │   ├── PayDTO.java
│   │   ├── OrderDTO.java
│   │   └── MerchantDTO.java
│   ├── vo/                            # 视图对象
│   │   ├── PayVO.java
│   │   └── OrderVO.java
│   ├── mq/                            # 消息队列
│   │   ├── kafka/
│   │   │   ├── KafkaProducer.java    # Kafka生产者
│   │   │   └── KafkaConsumer.java    # Kafka消费者
│   │   ├── rabbitmq/
│   │   │   ├── RabbitMQProducer.java
│   │   │   └── RabbitMQConsumer.java
│   │   ├── rocketmq/
│   │   │   ├── RocketMQProducer.java
│   │   │   └── RocketMQConsumer.java
│   │   └── message/                  # 消息体
│   │       ├── PayNotifyMessage.java
│   │       └── OrderMessage.java
│   ├── job/                           # 定时任务
│   │   ├── PayNotifyJob.java        # 支付通知任务
│   │   ├── OrderExpireJob.java      # 订单过期任务
│   │   └── SettlementJob.java        # 结算任务
│   ├── channel/                       # 支付通道
│   │   ├── PayChannel.java          # 通道接口
│   │   ├── ChannelFactory.java      # 通道工厂
│   │   ├── wechat/                  # 微信支付
│   │   │   ├── WechatPayChannel.java
│   │   │   └── WechatConfig.java
│   │   ├── alipay/                   # 支付宝
│   │   │   ├── AlipayChannel.java
│   │   │   └── AlipayConfig.java
│   │   └── union/                    # 银联
│   │       ├── UnionPayChannel.java
│   │       └── UnionConfig.java
│   └── config/                        # 业务配置
│       ├── KafkaConfig.java
│       ├── RabbitMQConfig.java
│       └── DataSourceConfig.java
│
├── admin/                             # 管理后台模块
│   ├── controller/
│   │   ├── MerchantManagerController.java
│   │   ├── ChannelManagerController.java
│   │   ├── TradeManagerController.java
│   │   └── ConfigManagerController.java
│   └── service/
│       └── AdminService.java
│
└── shop/                              # 商户平台模块
    ├── controller/
    │   ├── MerchantController.java
    │   ├── OrderController.java
    │   └── SettlementController.java
    └── service/
        └── ShopService.java
```

## 类创建规范

### 1. 创建实体类

```java
package com.zshlpay.service.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 支付订单实体
 *
 * @author zshlpay
 */
@Data
@TableName("pay_order")
public class PayOrder implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.ASSIGN_ID)
    private Long id;

    /** 支付单号 */
    private String tradeNo;

    /** 商户订单号 */
    private String orderNo;

    /** 商户号 */
    private String merchantNo;

    /** 通道编码 */
    private String channelCode;

    // ... 其他字段

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;

    @TableLogic
    private Integer delFlag;
}
```

### 2. 创建Mapper接口

```java
package com.zshlpay.service.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.zshlpay.service.entity.PayOrder;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * 支付订单Mapper
 */
@Mapper
public interface PayOrderMapper extends BaseMapper<PayOrder> {

    /**
     * 根据支付单号查询
     */
    PayOrder selectByTradeNo(@Param("tradeNo") String tradeNo);

    /**
     * 查询待通知订单
     */
    List<PayOrder> selectUnnotifiedOrders();

    /**
     * 关闭过期订单
     */
    int closeExpiredOrders(@Param("expireTime") LocalDateTime expireTime);
}
```

### 3. 创建Mapper XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
    "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.zshlpay.service.mapper.PayOrderMapper">

    <resultMap id="BaseResultMap" type="com.zshlpay.service.entity.PayOrder">
        <id column="id" property="id"/>
        <result column="trade_no" property="tradeNo"/>
        <result column="order_no" property="orderNo"/>
        <!-- 其他字段映射 -->
    </resultMap>

    <select id="selectByTradeNo" resultMap="BaseResultMap">
        SELECT * FROM pay_order
        WHERE trade_no = #{tradeNo}
        AND del_flag = 0
    </select>

    <select id="selectUnnotifiedOrders" resultMap="BaseResultMap">
        SELECT * FROM pay_order
        WHERE status = 2
        AND notify_status = 0
        AND del_flag = 0
        LIMIT 100
    </select>

    <update id="closeExpiredOrders">
        UPDATE pay_order
        SET status = 4, update_time = NOW()
        WHERE status = 0
        AND expire_time &lt; #{expireTime}
        AND del_flag = 0
    </update>

</mapper>
```

### 4. 创建Service接口

```java
package com.zshlpay.service.service;

import com.zshlpay.api.dto.*;
import com.zshlpay.common.result.Result;

/**
 * 支付服务接口
 */
public interface PayService {

    /**
     * 创建支付订单
     *
     * @param request 支付请求
     * @return 支付响应
     */
    Result<PayResponse> createPayOrder(PayRequest request);

    /**
     * 查询支付订单
     *
     * @param tradeNo 支付单号
     * @return 支付信息
     */
    Result<PayDTO> queryPayOrder(String tradeNo);

    /**
     * 支付回调
     */
    Result<Void> payNotify(String channelCode, PayNotifyDTO notifyDTO);

    /**
     * 申请退款
     */
    Result<RefundResponse> refund(RefundRequest request);
}
```

### 5. 创建Service实现

```java
package com.zshlpay.service.service.impl;

import com.zshlpay.api.dto.*;
import com.zshlpay.common.exception.BizException;
import com.zshlpay.common.result.Result;
import com.zshlpay.service.channel.PayChannel;
import com.zshlpay.service.entity.PayOrder;
import com.zshlpay.service.mapper.PayOrderMapper;
import com.zshlpay.service.service.PayService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

/**
 * 支付服务实现
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class PayServiceImpl implements PayService {

    private final PayOrderMapper payOrderMapper;
    private final Map<String, PayChannel> payChannelMap;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Result<PayResponse> createPayOrder(PayRequest request) {
        log.info("创建支付订单, orderNo={}", request.getOrderNo());

        // 1. 参数校验
        validatePayRequest(request);

        // 2. 获取支付通道
        PayChannel channel = payChannelMap.get(request.getChannelCode());
        if (channel == null || !channel.isAvailable()) {
            return Result.fail(500, "支付通道不可用");
        }

        // 3. 创建本地订单
        PayOrder order = createLocalOrder(request);

        // 4. 调用通道支付
        return channel.pay(order);
    }

    // ... 其他方法

    private void validatePayRequest(PayRequest request) {
        if (request.getAmount() == null || request.getAmount().compareTo(java.math.BigDecimal.ZERO) <= 0) {
            throw new BizException("支付金额必须大于0");
        }
        // 其他校验...
    }

    private PayOrder createLocalOrder(PayRequest request) {
        PayOrder order = new PayOrder();
        order.setTradeNo(generateTradeNo());
        // ... 设置其他字段
        payOrderMapper.insert(order);
        return order;
    }

    private String generateTradeNo() {
        return "PAY" + System.currentTimeMillis();
    }
}
```

### 6. 创建Controller

```java
package com.zshlpay.service.controller;

import com.zshlpay.api.dto.*;
import com.zshlpay.common.result.Result;
import com.zshlpay.service.service.PayService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

/**
 * 支付控制器
 */
@Slf4j
@RestController
@RequestMapping("/pay")
@RequiredArgsConstructor
@Tag(name = "支付管理", description = "支付相关接口")
public class PayController {

    private final PayService payService;

    @PostMapping("/create")
    @Operation(summary = "创建支付订单")
    public Result<PayResponse> createPay(@Validated @RequestBody PayRequest request) {
        return payService.createPayOrder(request);
    }

    @GetMapping("/query/{tradeNo}")
    @Operation(summary = "查询支付订单")
    public Result<PayDTO> queryPay(@PathVariable String tradeNo) {
        return payService.queryPayOrder(tradeNo);
    }

    @PostMapping("/notify/{channelCode}")
    @Operation(summary = "支付回调")
    public Result<Void> payNotify(
            @PathVariable String channelCode,
            @RequestBody PayNotifyDTO notifyDTO) {
        return payService.payNotify(channelCode, notifyDTO);
    }

    @PostMapping("/refund")
    @Operation(summary = "申请退款")
    public Result<RefundResponse> refund(@Validated @RequestBody RefundRequest request) {
        return payService.refund(request);
    }
}
```

### 7. 创建支付通道

```java
package com.zshlpay.service.channel.wechat;

import com.zshlpay.api.dto.*;
import com.zshlpay.common.result.Result;
import com.zshlpay.service.channel.PayChannel;
import com.zshlpay.service.entity.PayOrder;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * 微信支付通道
 */
@Slf4j
@Component
public class WechatPayChannel implements PayChannel {

    @Value("${wechat.pay.app.app-id}")
    private String appId;

    @Value("${wechat.pay.app.mch-id}")
    private String mchId;

    @Override
    public String getChannelCode() {
        return "WECHAT_APP";
    }

    @Override
    public boolean isAvailable() {
        return appId != null && mchId != null;
    }

    @Override
    public Result<PayResponse> pay(PayOrder order) {
        // 实现微信支付逻辑
        return Result.success();
    }

    @Override
    public Result<Void> handleNotify(PayNotifyDTO notifyDTO) {
        // 处理回调
        return Result.success();
    }

    @Override
    public Result<RefundResponse> refund(PayOrder order, RefundRequest request) {
        // 退款逻辑
        return Result.success();
    }

    @Override
    public Result<PayDTO> queryPay(String tradeNo) {
        // 查询逻辑
        return Result.success();
    }
}
```

### 8. 创建MQ消费者

```java
package com.zshlpay.service.mq.kafka;

import com.alibaba.fastjson2.JSON;
import com.zshlpay.service.mq.message.PayNotifyMessage;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.stereotype.Component;

/**
 * Kafka支付通知消费者
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class KafkaPayConsumer {

    private final PayNotifyService payNotifyService;

    @KafkaListener(
        topics = "pay-notify-topic",
        groupId = "${spring.kafka.consumer.group-id:zshlpay-group}",
        containerFactory = "kafkaListenerContainerFactory"
    )
    public void handlePayNotify(ConsumerRecord<String, String> record, Acknowledgment ack) {
        try {
            log.info("收到支付通知消息, key={}, partition={}, offset={}",
                record.key(), record.partition(), record.offset());

            PayNotifyMessage message = JSON.parseObject(record.value(), PayNotifyMessage.class);
            payNotifyService.processNotify(message);

            ack.acknowledge();
        } catch (Exception e) {
            log.error("处理支付通知消息异常", e);
            // 可选择不确认，等待重试
        }
    }
}
```

## 命名规范

### 类命名
| 类型 | 规范 | 示例 |
|------|------|------|
| 实体类 | Entity后缀 | PayOrderEntity |
| 数据传输对象 | DTO后缀 | PayRequestDTO |
| 视图对象 | VOP后缀 | PayVO |
| Mapper接口 | Mapper后缀 | PayOrderMapper |
| 服务接口 | Service后缀 | PayService |
| 服务实现 | ServiceImpl后缀 | PayServiceImpl |
| 控制器 | Controller后缀 | PayController |

### 方法命名
| 操作 | 命名规范 | 示例 |
|------|----------|------|
| 新增 | create/save | createPayOrder |
| 修改 | update | updatePayOrder |
| 删除 | delete/remove | deletePayOrder |
| 查询单个 | get/find | getPayOrder |
| 查询列表 | list | listPayOrders |
| 分页查询 | page | pagePayOrders |

### 变量命名
| 类型 | 规范 | 示例 |
|------|------|------|
| 普通变量 | 驼峰命名 | orderNo, tradeAmount |
| 常量 | 全大写下划线 | MAX_RETRY_COUNT |
| 集合 | 复数或List后缀 | orders, orderList |
| 布尔 | is/has/can前缀 | isSuccess, hasPermission |

## 代码注释规范

### 类注释
```java
/**
 * 支付服务
 *
 * @author zshlpay
 * @since 1.0.0
 */
```

### 方法注释
```java
/**
 * 创建支付订单
 *
 * @param request 支付请求参数
 * @return 支付响应
 * @throws BizException 业务异常
 */
```

### 复杂逻辑注释
```java
// 1. 校验订单金额
// 2. 计算手续费
// 3. 创建支付记录
```
