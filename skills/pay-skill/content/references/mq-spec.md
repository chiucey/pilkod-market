---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304402206efed6aca54d05949c0dbfcc7f79a4e24885d4359274f3b2a97a7a08c3a5a6cd02201ddae94778bc9f8d43db11a236b84b2c709ccc2bf776ec7a82932c2262aa39e1
    ReservedCode2: 30450221008e229231f5505c10f2fd5befcc8f64d793728e23efd99a64cf5d5edec107e48002207a1e0d62f7fbc2c2d450512a410d175f60ec0d80a4a4d2a382131e32aa760973
---

# zshlpay MQ 消息格式规范

## 概述

本文档定义了zshlpay项目中各消息队列的消息格式规范，支持Kafka、RabbitMQ、RocketMQ和ActiveMQ。

## Kafka 消息规范

### 消息结构

```json
{
  "messageId": "uuid-string",
  "topic": "topic-name",
  "tag": "tag-name",
  "key": "business-key",
  "body": {},
  "timestamp": 1704067200000,
  "headers": {
    "source": "zshlpay-service",
    "version": "1.0.0"
  }
}
```

### 预定义Topic

| Topic | 说明 | 分区数 | 保留时间 |
|-------|------|--------|----------|
| pay-notify-topic | 支付通知 | 3 | 7天 |
| order-topic | 订单消息 | 3 | 7天 |
| refund-topic | 退款消息 | 3 | 7天 |
| settlement-topic | 结算消息 | 3 | 7天 |

### 生产者配置

```yaml
spring:
  kafka:
    bootstrap-servers: 127.0.0.1:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.apache.kafka.common.serialization.StringSerializer
      acks: all
      retries: 3
      batch-size: 16384
      linger-ms: 1
      properties:
        enable.idempotence: true
        max.in.flight.requests.per.connection: 5
```

### 消费者配置

```yaml
spring:
  kafka:
    consumer:
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      group-id: zshlpay-group
      auto-offset-reset: earliest
      enable-auto-commit: false
      properties:
        max.poll.records: 500
        max.poll.interval.ms: 300000
```

### 支付通知消息示例

```json
{
  "messageId": "msg-20240101123456789",
  "topic": "pay-notify-topic",
  "tag": "pay-success",
  "key": "PAY20240101123456",
  "body": {
    "tradeNo": "PAY20240101123456",
    "orderNo": "ORDER20240101123456",
    "merchantNo": "M20240101001",
    "channelCode": "WECHAT_APP",
    "amount": 100.00,
    "status": "SUCCESS",
    "transactionId": "微信订单号",
    "payTime": "2024-01-01 12:00:00"
  },
  "timestamp": 1704067200000,
  "headers": {
    "source": "zshlpay-service",
    "version": "1.0.0"
  }
}
```

## RabbitMQ 消息规范

### 交换机和队列定义

| 交换机 | 类型 | 队列 | 路由键 |
|--------|------|------|--------|
| pay.exchange | Direct | pay.queue | pay.notify |
| order.exchange | Direct | order.queue | order.create |
| refund.exchange | Direct | refund.queue | refund.process |
| settlement.exchange | Direct | settlement.queue | settlement.create |

### 消息属性

```yaml
spring:
  rabbitmq:
    host: 127.0.0.1
    port: 5672
    username: guest
    password: guest
    virtual-host: /
    listener:
      simple:
        acknowledge-mode: manual
        prefetch: 10
        concurrency: 3
        max-concurrency: 10
    template:
      mandatory: true
      exchange: ""
      routing-key: ""
```

### 支付通知消息示例

```json
{
  "exchange": "pay.exchange",
  "routingKey": "pay.notify",
  "messageId": "msg-20240101123456789",
  "timestamp": 1704067200000,
  "deliveryMode": 2,
  "contentType": "application/json",
  "headers": {
    "source": "zshlpay-service",
    "version": "1.0.0"
  },
  "body": {
    "tradeNo": "PAY20240101123456",
    "orderNo": "ORDER20240101123456",
    "merchantNo": "M20240101001",
    "channelCode": "WECHAT_APP",
    "amount": 100.00,
    "status": "SUCCESS"
  }
}
```

## RocketMQ 消息规范

### Topic和Tag定义

| Topic | Tag | 说明 |
|-------|-----|------|
| PAY_TOPIC | pay-success | 支付成功 |
| PAY_TOPIC | pay-fail | 支付失败 |
| ORDER_TOPIC | order-create | 订单创建 |
| ORDER_TOPIC | order-cancel | 订单取消 |
| REFUND_TOPIC | refund-process | 退款处理 |

### 消息结构

```json
{
  "messageId": "msg-20240101123456789",
  "topic": "PAY_TOPIC",
  "tag": "pay-success",
  "keys": "PAY20240101123456",
  "body": {},
  "flag": 0,
  "waitStoreMsgOk": true,
  "timestamp": 1704067200000
}
```

### 配置示例

```yaml
rocketmq:
  name-server: 127.0.0.1:9876
  producer:
    group: zshlpay-producer-group
    send-msg-timeout: 3000
    retry-times-when-send-failed: 2
    max-message-size: 4194304
  consumer:
    group: zshlpay-consumer-group
    message-model: CLUSTERING
    subscribe:
      PAY_TOPIC: "pay-success||pay-fail"
      ORDER_TOPIC: "order-create||order-cancel"
```

### 支付通知消息示例

```json
{
  "messageId": "msg-20240101123456789",
  "topic": "PAY_TOPIC",
  "tag": "pay-success",
  "keys": "PAY20240101123456",
  "body": {
    "tradeNo": "PAY20240101123456",
    "orderNo": "ORDER20240101123456",
    "merchantNo": "M20240101001",
    "channelCode": "WECHAT_APP",
    "amount": 100.00,
    "status": "SUCCESS",
    "transactionId": "微信订单号",
    "payTime": "2024-01-01 12:00:00"
  },
  "flag": 0,
  "timestamp": 1704067200000
}
```

## ActiveMQ 消息规范

### 队列定义

| 队列名称 | 说明 | 持久化 |
|----------|------|--------|
| pay.notify.queue | 支付通知队列 | 是 |
| order.create.queue | 订单创建队列 | 是 |
| refund.process.queue | 退款处理队列 | 是 |

### 配置示例

```yaml
spring:
  activemq:
    broker-url: tcp://127.0.0.1:61616
    user: admin
    password: admin
    packages:
      trust-all: true
    pool:
      enabled: true
      max-connections: 10
      idle-timeout: 30000
```

### 消息示例

```json
{
  "messageId": "msg-20240101123456789",
  "timestamp": 1704067200000,
  "deliveryMode": 2,
  "priority": 4,
  "headers": {
    "source": "zshlpay-service",
    "version": "1.0.0"
  },
  "body": {
    "tradeNo": "PAY20240101123456",
    "orderNo": "ORDER20240101123456",
    "merchantNo": "M20240101001",
    "channelCode": "WECHAT_APP",
    "amount": 100.00,
    "status": "SUCCESS"
  }
}
```

## 通用消息处理规范

### 消息幂等性

```java
// 使用消息ID进行幂等处理
@KafkaListener(topics = "pay-notify-topic", groupId = "zshlpay-group")
public void handlePayNotify(ConsumerRecord<String, String> record) {
    String messageId = record.key();
    if (idempotentService.isProcessed(messageId)) {
        log.info("消息已处理，跳过: {}", messageId);
        return;
    }
    // 处理业务逻辑
    idempotentService.markProcessed(messageId);
}
```

### 消息重试机制

```java
// 配置重试策略
@RetryableTopic(
    attempts = "3",
    backoff = @Backoff(delay = 1000, multiplier = 2),
    exclude = {BizException.class}
)
@KafkaListener(topics = "pay-notify-topic")
public void handlePayNotify(String message) {
    // 业务处理
}
```

### 消息监控

```java
// 消息监控指标
@Component
public class MQMetrics {
    private final MeterRegistry meterRegistry;

    public void recordMessage(String topic, String action, long costTime) {
        meterRegistry.counter("mq.message", "topic", topic, "action", action).increment();
        meterRegistry.timer("mq.process.time", "topic", topic, "action", action)
            .record(costTime, TimeUnit.MILLISECONDS);
    }
}
```

## 最佳实践

1. **消息压缩**：对于大于1KB的消息，建议启用压缩
2. **批量处理**：消费者应批量处理消息以提高吞吐量
3. **死信队列**：为每个队列配置死信队列处理失败消息
4. **消息监控**：定期监控消息积压和消费延迟
5. **版本兼容**：消息格式变更应保持向后兼容
6. **日志追踪**：在消息头中携带traceId便于链路追踪
