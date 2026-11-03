---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022026c608bd645d8c799dbe2e9ec8abbd82984c3bbcaf528aa987314c0fa458e870022100d2ee5427c41c2c799b46d14320d1168a738f34a91577182bdd533d68847c145a
    ReservedCode2: 30460221008b026ddf421a19739c45aa5fa666d8c0b30de7e7f9d9c08367aa8e66f306685f022100f28e9e9a248f50f4c06fd6fbf26acdd9fd52724befe24b11d0fb7b4c34551d76
---

# zshlpay Spring Cloud 项目示例

## 项目结构

```
zshlpay-cloud/
├── pom.xml
├── README.md
├── zshlpay-common/
│   ├── pom.xml
│   └── src/main/java/com/zshlpay/common/
│       ├── common/
│       │   └── result/
│       │       └── Result.java
│       └── config/
│           ├── MyBatisPlusConfig.java
│           └── RedisConfig.java
├── zshlpay-common-util/
│   ├── pom.xml
│   └── src/main/java/com/zshlpay/util/
│       ├── DateUtil.java
│       ├── EncryptUtil.java
│       └── HttpUtil.java
├── zshlpay-api/
│   ├── pom.xml
│   └── src/main/java/com/zshlpay/api/
│       ├── client/
│       │   ├── PayFeignClient.java
│       │   ├── MerchantFeignClient.java
│       │   └── OrderFeignClient.java
│       ├── fallback/
│       │   ├── PayFeignFallback.java
│       │   └── MerchantFeignFallback.java
│       └── dto/
│           ├── PayRequest.java
│           └── PayResponse.java
├── zshlpay-gateway/
│   ├── pom.xml
│   └── src/main/
│       ├── java/com/zshlpay/gateway/
│       │   ├── GatewayApplication.java
│       │   └── filter/
│       │       ├── AuthFilter.java
│       │       └── RateLimitFilter.java
│       └── resources/
│           └── application.yml
├── zshlpay-service/
│   ├── pom.xml
│   └── src/main/
│       ├── java/com/zshlpay/service/
│       │   ├── ServiceApplication.java
│       │   ├── config/
│       │   │   ├── KafkaConfig.java
│       │   │   ├── RabbitMQConfig.java
│       │   │   └── DataSourceConfig.java
│       │   ├── controller/
│       │   │   ├── PayController.java
│       │   │   ├── OrderController.java
│       │   │   └── MerchantController.java
│       │   ├── service/
│       │   │   ├── PayService.java
│       │   │   ├── OrderService.java
│       │   │   └── impl/
│       │   │       ├── PayServiceImpl.java
│       │   │       └── OrderServiceImpl.java
│       │   ├── mapper/
│       │   │   ├── PayOrderMapper.java
│       │   │   └── MerchantMapper.java
│       │   ├── entity/
│       │   │   ├── PayOrder.java
│       │   │   └── Merchant.java
│       │   ├── dto/
│       │   │   └── PayDTO.java
│       │   ├── mq/
│       │   │   ├── kafka/
│       │   │   │   ├── KafkaProducer.java
│       │   │   │   └── KafkaConsumer.java
│       │   │   └── rabbitmq/
│       │   │       ├── RabbitMQProducer.java
│       │   │       └── RabbitMQConsumer.java
│       │   ├── channel/
│       │   │   ├── PayChannel.java
│       │   │   ├── wechat/
│       │   │   │   └── WechatPayChannel.java
│       │   │   ├── alipay/
│       │   │   │   └── AlipayChannel.java
│       │   │   └── union/
│       │   │       └── UnionPayChannel.java
│       │   └── job/
│       │       ├── PayNotifyJob.java
│       │       └── OrderExpireJob.java
│       └── resources/
│           ├── application.yml
│           └── mapper/
│               ├── PayOrderMapper.xml
│               └── MerchantMapper.xml
├── zshlpay-admin/
│   ├── pom.xml
│   └── src/main/
│       ├── java/com/zshlpay/admin/
│       │   ├── AdminApplication.java
│       │   └── controller/
│       │       ├── MerchantManagerController.java
│       │       └── ChannelManagerController.java
│       └── resources/
│           └── application.yml
└── zshlpay-shop/
    ├── pom.xml
    └── src/main/
        ├── java/com/zshlpay/shop/
        │   ├── ShopApplication.java
        │   └── controller/
        │       └── MerchantController.java
        └── resources/
            └── application.yml
```

## 启动类示例

### GatewayApplication.java

```java
package com.zshlpay.gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.openfeign.EnableFeignClients;
import org.springframework.context.annotation.ComponentScan;

@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients(basePackages = "com.zshlpay.api.client")
@ComponentScan(basePackages = {"com.zshlpay"})
public class GatewayApplication {

    public static void main(String[] args) {
        SpringApplication.run(GatewayApplication.class, args);
        System.out.println("===========================================");
        System.out.println("  Gateway 启动成功!");
        System.out.println("===========================================");
    }
}
```

### ServiceApplication.java

```java
package com.zshlpay.service;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.openfeign.EnableFeignClients;
import org.springframework.context.annotation.ComponentScan;

@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients(basePackages = "com.zshlpay.api.client")
@ComponentScan(basePackages = {"com.zshlpay"})
@MapperScan("com.zshlpay.**.mapper")
public class ServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(ServiceApplication.class, args);
        System.out.println("===========================================");
        System.out.println("  Service 启动成功!");
        System.out.println("===========================================");
    }
}
```

## 实体类示例

### PayOrder.java

```java
package com.zshlpay.service.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("pay_order")
public class PayOrder implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.ASSIGN_ID)
    private Long id;

    private String tradeNo;
    private String orderNo;
    private String merchantNo;
    private String channelCode;
    private String channelTradeNo;

    private BigDecimal amount;
    private BigDecimal actualAmount;
    private BigDecimal refundAmount;

    private String subject;
    private String body;
    private String attach;

    private Integer status;
    private LocalDateTime payTime;
    private LocalDateTime expireTime;

    private String notifyUrl;
    private String returnUrl;
    private String clientIp;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT)
    private String createBy;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private String updateBy;

    @TableLogic
    private Integer delFlag;

    private String remark;
}
```

## 服务实现示例

### PayService.java

```java
package com.zshlpay.service.service;

import com.zshlpay.api.dto.*;
import com.zshlpay.common.result.Result;

public interface PayService {

    /**
     * 创建支付订单
     */
    Result<PayResponse> createPayOrder(PayRequest request);

    /**
     * 查询支付订单
     */
    Result<PayDTO> queryPayOrder(String tradeNo);

    /**
     * 支付回调处理
     */
    Result<Void> payNotify(String channelCode, PayNotifyDTO notifyDTO);

    /**
     * 申请退款
     */
    Result<RefundResponse> refund(RefundRequest request);
}
```

### PayServiceImpl.java

```java
package com.zshlpay.service.service.impl;

import com.zshlpay.api.dto.*;
import com.zshlpay.common.result.Result;
import com.zshlpay.service.channel.PayChannel;
import com.zshlpay.service.entity.PayOrder;
import com.zshlpay.service.mapper.PayOrderMapper;
import com.zshlpay.service.service.PayService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

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

        // 获取支付通道
        PayChannel channel = payChannelMap.get(request.getChannelCode());
        if (channel == null) {
            return Result.fail(500, "支付通道不存在");
        }

        // 创建本地订单
        PayOrder order = createLocalOrder(request);

        // 调用通道支付
        return channel.pay(order);
    }

    @Override
    public Result<PayDTO> queryPayOrder(String tradeNo) {
        PayOrder order = payOrderMapper.selectByTradeNo(tradeNo);
        if (order == null) {
            return Result.fail(404, "订单不存在");
        }
        return Result.success(convertToDTO(order));
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Result<Void> payNotify(String channelCode, PayNotifyDTO notifyDTO) {
        log.info("支付回调, channelCode={}, tradeNo={}", channelCode, notifyDTO.getTradeNo());

        // 获取通道处理回调
        PayChannel channel = payChannelMap.get(channelCode);
        if (channel == null) {
            return Result.fail(500, "支付通道不存在");
        }

        return channel.handleNotify(notifyDTO);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Result<RefundResponse> refund(RefundRequest request) {
        log.info("申请退款, tradeNo={}, refundAmount={}", request.getTradeNo(), request.getRefundAmount());

        PayOrder order = payOrderMapper.selectByTradeNo(request.getTradeNo());
        if (order == null) {
            return Result.fail(404, "订单不存在");
        }

        PayChannel channel = payChannelMap.get(order.getChannelCode());
        if (channel == null) {
            return Result.fail(500, "支付通道不存在");
        }

        return channel.refund(order, request);
    }

    private PayOrder createLocalOrder(PayRequest request) {
        PayOrder order = new PayOrder();
        order.setTradeNo(generateTradeNo());
        order.setOrderNo(request.getOrderNo());
        order.setMerchantNo(request.getMerchantNo());
        order.setChannelCode(request.getChannelCode());
        order.setAmount(request.getAmount());
        order.setActualAmount(request.getAmount());
        order.setSubject(request.getSubject());
        order.setBody(request.getBody());
        order.setAttach(request.getAttach());
        order.setNotifyUrl(request.getNotifyUrl());
        order.setReturnUrl(request.getReturnUrl());
        order.setClientIp(request.getClientIp());
        order.setStatus(0);
        order.setExpireTime(LocalDateTime.now().plusMinutes(30));
        payOrderMapper.insert(order);
        return order;
    }

    private String generateTradeNo() {
        return "PAY" + DateUtil.format(new Date(), "yyyyMMddHHmmss") +
               String.format("%04d", new Random().nextInt(10000));
    }

    private PayDTO convertToDTO(PayOrder order) {
        PayDTO dto = new PayDTO();
        dto.setTradeNo(order.getTradeNo());
        dto.setOrderNo(order.getOrderNo());
        dto.setAmount(order.getAmount());
        dto.setStatus(order.getStatus());
        // ... 其他字段转换
        return dto;
    }
}
```

## MQ生产者/消费者示例

### KafkaProducer.java

```java
package com.zshlpay.service.mq.kafka;

import com.alibaba.fastjson2.JSON;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;
import org.springframework.stereotype.Component;

import java.util.concurrent.CompletableFuture;

@Slf4j
@Component
@RequiredArgsConstructor
public class KafkaProducer {

    private final KafkaTemplate<String, String> kafkaTemplate;

    private static final String TOPIC_PAY_NOTIFY = "pay-notify-topic";
    private static final String TOPIC_ORDER = "order-topic";

    /**
     * 发送支付通知消息
     */
    public void sendPayNotify(String key, Object message) {
        String json = JSON.toJSONString(message);
        CompletableFuture<SendResult<String, String>> future =
            kafkaTemplate.send(TOPIC_PAY_NOTIFY, key, json);

        future.whenComplete((result, ex) -> {
            if (ex != null) {
                log.error("发送支付通知消息失败, key={}, error={}", key, ex.getMessage());
            } else {
                log.info("发送支付通知消息成功, key={}, partition={}, offset={}",
                    key,
                    result.getRecordMetadata().partition(),
                    result.getRecordMetadata().offset());
            }
        });
    }

    /**
     * 发送订单消息
     */
    public void sendOrderMessage(String key, Object message) {
        String json = JSON.toJSONString(message);
        kafkaTemplate.send(TOPIC_ORDER, key, json);
    }
}
```

### KafkaConsumer.java

```java
package com.zshlpay.service.mq.kafka;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class KafkaConsumer {

    private final PayNotifyService payNotifyService;
    private final OrderService orderService;

    @KafkaListener(
        topics = "pay-notify-topic",
        groupId = "${spring.kafka.consumer.group-id}",
        containerFactory = "kafkaListenerContainerFactory"
    )
    public void handlePayNotify(ConsumerRecord<String, String> record, Acknowledgment ack) {
        try {
            log.info("收到支付通知消息, key={}, partition={}, offset={}",
                record.key(), record.partition(), record.offset());

            // 幂等性检查
            if (isDuplicateMessage(record.key())) {
                log.warn("消息已处理, key={}", record.key());
                ack.acknowledge();
                return;
            }

            // 处理消息
            payNotifyService.processNotify(record.value());

            // 标记已处理
            markMessageProcessed(record.key());

            ack.acknowledge();
        } catch (Exception e) {
            log.error("处理支付通知消息异常", e);
            // 业务处理失败，不确认消息，等待重试
        }
    }

    @KafkaListener(
        topics = "order-topic",
        groupId = "${spring.kafka.consumer.group-id}",
        containerFactory = "kafkaListenerContainerFactory"
    )
    public void handleOrderMessage(ConsumerRecord<String, String> record, Acknowledgment ack) {
        try {
            log.info("收到订单消息, key={}", record.key());
            orderService.processMessage(record.value());
            ack.acknowledge();
        } catch (Exception e) {
            log.error("处理订单消息异常", e);
        }
    }

    private boolean isDuplicateMessage(String key) {
        // 实现幂等性检查逻辑
        return false;
    }

    private void markMessageProcessed(String key) {
        // 标记消息已处理
    }
}
```

## RabbitMQ生产者/消费者示例

### RabbitMQProducer.java

```java
package com.zshlpay.service.mq.rabbitmq;

import com.zshlpay.service.config.RabbitMQConfig;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class RabbitMQProducer {

    private final RabbitTemplate rabbitTemplate;

    /**
     * 发送支付通知
     */
    public void sendPayNotify(Object message) {
        rabbitTemplate.convertAndSend(
            RabbitMQConfig.PAY_EXCHANGE,
            RabbitMQConfig.PAY_ROUTING_KEY,
            message
        );
        log.info("发送支付通知消息成功");
    }

    /**
     * 发送订单消息
     */
    public void sendOrderMessage(Object message) {
        rabbitTemplate.convertAndSend(
            RabbitMQConfig.ORDER_EXCHANGE,
            RabbitMQConfig.ORDER_ROUTING_KEY,
            message
        );
        log.info("发送订单消息成功");
    }
}
```

### RabbitMQConsumer.java

```java
package com.zshlpay.service.mq.rabbitmq;

import com.zshlpay.service.config.RabbitMQConfig;
import com.zshlpay.service.service.PayNotifyService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.amqp.support.AmqpHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.stereotype.Component;
import com.rabbitmq.client.Channel;

@Slf4j
@Component
@RequiredArgsConstructor
public class RabbitMQConsumer {

    private final PayNotifyService payNotifyService;

    @RabbitListener(queues = RabbitMQConfig.PAY_QUEUE)
    public void handlePayNotify(
            Object message,
            Channel channel,
            @Header(AmqpHeaders.DELIVERY_TAG) long deliveryTag) {
        try {
            log.info("收到支付通知消息: {}", message);
            payNotifyService.processNotify(message);
            channel.basicAck(deliveryTag, false);
        } catch (Exception e) {
            log.error("处理支付通知消息异常", e);
            try {
                channel.basicNack(deliveryTag, false, true);
            } catch (Exception ex) {
                log.error("消息确认失败", ex);
            }
        }
    }

    @RabbitListener(queues = RabbitMQConfig.ORDER_QUEUE)
    public void handleOrderMessage(
            Object message,
            Channel channel,
            @Header(AmqpHeaders.DELIVERY_TAG) long deliveryTag) {
        try {
            log.info("收到订单消息: {}", message);
            // 处理订单逻辑
            channel.basicAck(deliveryTag, false);
        } catch (Exception e) {
            log.error("处理订单消息异常", e);
            try {
                channel.basicNack(deliveryTag, false, true);
            } catch (Exception ex) {
                log.error("消息确认失败", ex);
            }
        }
    }
}
```

## 支付通道实现示例

### PayChannel.java (接口)

```java
package com.zshlpay.service.channel;

/**
 * 支付通道接口
 */
public interface PayChannel {

    /**
     * 获取通道编码
     */
    String getChannelCode();

    /**
     * 通道是否可用
     */
    boolean isAvailable();

    /**
     * 发起支付
     */
    Result<PayResponse> pay(PayOrder order);

    /**
     * 支付回调处理
     */
    Result<Void> handleNotify(PayNotifyDTO notifyDTO);

    /**
     * 申请退款
     */
    Result<RefundResponse> refund(PayOrder order, RefundRequest request);

    /**
     * 查询支付状态
     */
    Result<PayDTO> queryPay(String tradeNo);
}
```

### WechatPayChannel.java (实现)

```java
package com.zshlpay.service.channel.wechat;

import com.github.binarywang.wxpay.bean.order.WxPayMwebOrderResult;
import com.github.binarywang.wxpay.bean.request.WxPayUnifiedOrderRequest;
import com.github.binarywang.wxpay.bean.result.WxPayUnifiedOrderResult;
import com.github.binarywang.wxpay.config.WxPayConfig;
import com.github.binarywang.wxpay.service.WxPayService;
import com.github.binarywang.wxpay.service.impl.WxPayServiceImpl;
import com.zshlpay.api.dto.*;
import com.zshlpay.common.result.Result;
import com.zshlpay.service.channel.PayChannel;
import com.zshlpay.service.entity.PayOrder;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class WechatPayChannel implements PayChannel {

    @Value("${wechat.pay.app.app-id}")
    private String appId;

    @Value("${wechat.pay.app.mch-id}")
    private String mchId;

    @Value("${wechat.pay.app.api-key}")
    private String apiKey;

    @Override
    public String getChannelCode() {
        return "WECHAT_APP";
    }

    @Override
    public boolean isAvailable() {
        return true;
    }

    @Override
    public Result<PayResponse> pay(PayOrder order) {
        try {
            WxPayService wxPayService = createWxPayService();

            WxPayUnifiedOrderRequest request = new WxPayUnifiedOrderRequest();
            request.setOutTradeNo(order.getTradeNo());
            request.setTotalFee((int)(order.getAmount().doubleValue() * 100));
            request.setBody(order.getSubject());
            request.setSpbillCreateIp(order.getClientIp());
            request.setNotifyUrl(order.getNotifyUrl());
            request.setTradeType("APP");

            WxPayUnifiedOrderResult result = wxPayService.unifiedOrder(request);

            PayResponse response = new PayResponse();
            response.setTradeNo(order.getTradeNo());
            response.setPayInfo(result.getMwebUrl());

            return Result.success(response);
        } catch (Exception e) {
            log.error("微信支付创建失败", e);
            return Result.fail(500, "微信支付创建失败: " + e.getMessage());
        }
    }

    @Override
    public Result<Void> handleNotify(PayNotifyDTO notifyDTO) {
        // 处理微信支付回调
        return Result.success();
    }

    @Override
    public Result<RefundResponse> refund(PayOrder order, RefundRequest request) {
        // 发起微信退款
        return Result.success();
    }

    @Override
    public Result<PayDTO> queryPay(String tradeNo) {
        // 查询微信支付状态
        return Result.success();
    }

    private WxPayService createWxPayService() {
        WxPayConfig config = new WxPayConfig();
        config.setAppId(appId);
        config.setMchId(mchId);
        config.setMchKey(apiKey);

        WxPayService service = new WxPayServiceImpl();
        service.setConfig(config);
        return service;
    }
}
```

## 定时任务示例

### PayNotifyJob.java

```java
package com.zshlpay.service.job;

import com.zshlpay.service.entity.PayOrder;
import com.zshlpay.service.mapper.PayOrderMapper;
import com.zshlpay.service.mq.kafka.KafkaProducer;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.List;

@Slf4j
@Component
@RequiredArgsConstructor
public class PayNotifyJob {

    private final PayOrderMapper payOrderMapper;
    private final KafkaProducer kafkaProducer;

    /**
     * 处理支付成功但未通知的消息
     * 每分钟执行一次
     */
    @Scheduled(cron = "0 * * * * ?")
    public void processPayNotify() {
        log.info("开始处理支付通知任务");

        // 查询待通知的订单
        List<PayOrder> orders = payOrderMapper.selectUnnotifiedOrders();

        for (PayOrder order : orders) {
            try {
                // 发送通知消息
                kafkaProducer.sendPayNotify(order.getTradeNo(), order);
                log.info("发送支付通知成功, tradeNo={}", order.getTradeNo());
            } catch (Exception e) {
                log.error("发送支付通知失败, tradeNo={}", order.getTradeNo(), e);
            }
        }

        log.info("支付通知任务处理完成, 处理数量={}", orders.size());
    }

    /**
     * 关闭超时未支付订单
     * 每5分钟执行一次
     */
    @Scheduled(cron = "0 */5 * * * ?")
    public void closeExpiredOrders() {
        log.info("开始关闭超时订单任务");

        LocalDateTime expireTime = LocalDateTime.now();
        int count = payOrderMapper.closeExpiredOrders(expireTime);

        log.info("关闭超时订单完成, 关闭数量={}", count);
    }
}
```

## 数据库配置示例

### DataSourceConfig.java (支持多数据库)

```java
package com.zshlpay.service.config;

import com.alibaba.druid.pool.DruidDataSource;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.sql.DataSource;

@Configuration
public class DataSourceConfig {

    @Value("${db.type:mysql}")
    private String dbType;

    @Value("${db.host:127.0.0.1}")
    private String host;

    @Value("${db.port:3306}")
    private int port;

    @Value("${db.name:zshlpay}")
    private String database;

    @Value("${db.username:root}")
    private String username;

    @Value("${db.password:}")
    private String password;

    @Bean
    public DataSource dataSource() {
        DruidDataSource dataSource = new DruidDataSource();
        dataSource.setUrl(buildJdbcUrl());
        dataSource.setUsername(username);
        dataSource.setPassword(password);
        dataSource.setDriverClassName(getDriverClassName());
        dataSource.setInitialSize(5);
        dataSource.setMinIdle(5);
        dataSource.setMaxActive(20);
        dataSource.setMaxWait(60000);
        return dataSource;
    }

    private String buildJdbcUrl() {
        return switch (dbType) {
            case "dm" -> String.format(
                "jdbc:dm://%s:%d/%s", host, port, database);
            case "kingbase" -> String.format(
                "jdbc:kingbase8://%s:%d/%s", host, port, database);
            case "oceanbase" -> String.format(
                "jdbc:oceanbase://%s:%d/%s", host, port, database);
            case "postgresql" -> String.format(
                "jdbc:postgresql://%s:%d/%s", host, port, database);
            default -> String.format(
                "jdbc:mysql://%s:%d/%s?useUnicode=true&characterEncoding=utf8",
                host, port, database);
        };
    }

    private String getDriverClassName() {
        return switch (dbType) {
            case "dm" -> "dm.jdbc.driver.DmDriver";
            case "kingbase" -> "com.kingbase8.Driver";
            case "oceanbase" -> "com.oceanbase.jdbc.Driver";
            case "postgresql" -> "org.postgresql.Driver";
            default -> "com.mysql.cj.jdbc.Driver";
        };
    }
}
```
