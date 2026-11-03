---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100c1c8447aff83920eca8467b0e626f4e126b6ff2028a51dd42fff301f4ee6049f02203ae8a7eef835edb143955db64ea661c86b3d24fd6317d3b19e3235ab1192cc5d
    ReservedCode2: 304502202b11db540ed2590ba2162ec1c9719b38efce81b7ac596f3b7119379c02394323022100d54843d3dba17ba60aa716e9a1dff4a48a6ee156d63d19815d375070d58595a6
---

# zshlpay 配置模板

## 环境配置模板

### 开发环境 application-dev.yml

```yaml
spring:
  application:
    name: zshlpay-service

  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://127.0.0.1:3306/zshlpay?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai
    username: root
    password: root123456

  data:
    redis:
      host: 127.0.0.1
      port: 6379
      password:
      database: 0

  # Kafka配置
  kafka:
    bootstrap-servers: 127.0.0.1:9092

  # RabbitMQ配置
  rabbitmq:
    host: 127.0.0.1
    port: 5672
    username: guest
    password: guest

# Nacos配置
nacos:
  server-addr: 127.0.0.1:8848
  namespace: dev

# 日志级别
logging:
  level:
    com.zshlpay: DEBUG
    org.springframework: INFO
```

### 生产环境 application-prod.yml

```yaml
spring:
  application:
    name: zshlpay-service

  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://${DB_HOST}:${DB_PORT}/${DB_NAME}?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&useSSL=true
    username: ${DB_USER}
    password: ${DB_PASSWORD}

  data:
    redis:
      host: ${REDIS_HOST}
      port: ${REDIS_PORT}
      password: ${REDIS_PASSWORD}
      database: 0
      ssl: true

# Nacos配置
nacos:
  server-addr: ${NACOS_SERVER}
  namespace: ${NACOS_NAMESPACE}

# 日志级别
logging:
  level:
    com.zshlpay: INFO
    org.springframework: WARN
  file:
    name: /var/log/zshlpay/${spring.application.name}.log
```

## 支付通道配置模板

### 微信支付配置 wechat-pay.yml

```yaml
wechat:
  pay:
    # 公众号支付
    official-account:
      app-id: ${WX_OFFICIAL_APP_ID}
      mch-id: ${WX_MCH_ID}
      api-key: ${WX_API_KEY}
      cert-path: ${WX_CERT_PATH}
      notify-url: ${WX_NOTIFY_URL}

    # APP支付
    app:
      app-id: ${WX_APP_ID}
      mch-id: ${WX_MCH_ID}
      api-key: ${WX_API_KEY}
      cert-path: ${WX_CERT_PATH}
      notify-url: ${WX_NOTIFY_URL}

    # 小程序支付
    mini-program:
      app-id: ${WX_MINI_APP_ID}
      mch-id: ${WX_MCH_ID}
      api-key: ${WX_API_KEY}
      notify-url: ${WX_NOTIFY_URL}

    # H5支付
    h5:
      app-id: ${WX_H5_APP_ID}
      mch-id: ${WX_MCH_ID}
      api-key: ${WX_API_KEY}
      notify-url: ${WX_NOTIFY_URL}
      h5-domain: ${WX_H5_DOMAIN}
```

### 支付宝配置 alipay.yml

```yaml
alipay:
  pay:
    # 应用ID
    app-id: ${ALI_APP_ID}

    # 商户私钥
    private-key: ${ALI_PRIVATE_KEY}

    # 支付宝公钥
    alipay-public-key: ${ALI_PUBLIC_KEY}

    # 签名类型
    sign-type: RSA2

    # 编码格式
    charset: UTF-8

    # 网关地址
    gateway-url: https://openapi.alipay.com/gateway.do

    # 异步通知地址
    notify-url: ${ALI_NOTIFY_URL}

    # 同步跳转地址
    return-url: ${ALI_RETURN_URL}

    # 格式
    format: json
```

### 银联支付配置 union-pay.yml

```yaml
union:
  pay:
    # 商户ID
    merchant-id: ${UNION_MERCHANT_ID}

    # 签名密钥
    sign-key: ${UNION_SIGN_KEY}

    # 银联公钥
    union-public-key: ${UNION_PUBLIC_KEY}

    # 报文加密密钥
    encrypt-key: ${UNION_ENCRYPT_KEY}

    # 异步通知地址
    notify-url: ${UNION_NOTIFY_URL}

    # 前端跳转地址
    front-url: ${UNION_FRONT_URL}

    # 网关地址
    gateway-url: https://gateway.95516.com
```

## MQ配置模板

### Kafka配置 kafka.yml

```yaml
spring:
  kafka:
    bootstrap-servers: ${KAFKA_BOOTSTRAP_SERVERS:127.0.0.1:9092}

    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.apache.kafka.common.serialization.StringSerializer
      acks: all
      retries: 3
      batch-size: 16384
      linger-ms: 1
      buffer-memory: 33554432
      properties:
        enable.idempotence: true
        max.in.flight.requests.per.connection: 5

    consumer:
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      group-id: ${KAFKA_GROUP_ID:zshlpay-group}
      auto-offset-reset: earliest
      enable-auto-commit: false
      max-poll-records: 500
      properties:
        session.timeout.ms: 30000
        heartbeat.interval.ms: 10000

    listener:
      ack-mode: manual
      concurrency: 3
```

### RabbitMQ配置 rabbitmq.yml

```yaml
spring:
  rabbitmq:
    host: ${RABBITMQ_HOST:127.0.0.1}
    port: ${RABBITMQ_PORT:5672}
    username: ${RABBITMQ_USERNAME:guest}
    password: ${RABBITMQ_PASSWORD:guest}
    virtual-host: /

    listener:
      simple:
        acknowledge-mode: manual
        prefetch: 10
        concurrency: 3
        max-concurrency: 10
        retry:
          enabled: true
          initial-interval: 1000
          max-attempts: 3
          max-interval: 10000
          multiplier: 2.0

    template:
      mandatory: true
      retry:
        enabled: true
        initial-interval: 1000
        max-attempts: 3
```

## 国产数据库配置模板

### 达梦数据库 DM

```yaml
spring:
  datasource:
    driver-class-name: dm.jdbc.driver.DmDriver
    url: jdbc:dm://${DB_HOST}:${DB_PORT}/${DB_NAME}?schema=${DB_NAME}&zeroDateTimeBehavior=convertToNull&escape=true
    username: ${DB_USER}
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
```

### 人大金仓 Kingbase

```yaml
spring:
  datasource:
    driver-class-name: com.kingbase8.Driver
    url: jdbc:kingbase8://${DB_HOST}:${DB_PORT}/${DB_NAME}
    username: ${DB_USER}
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
```

### OceanBase

```yaml
spring:
  datasource:
    driver-class-name: com.oceanbase.jdbc.Driver
    url: jdbc:oceanbase://${DB_HOST}:${DB_PORT}/${DB_NAME}?useUnicode=true&characterEncoding=utf8
    username: ${DB_USER}
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
```

## Sentinel配置模板

```yaml
sentinel:
  eager: true
  transport:
    dashboard: ${SENTINEL_DASHBOARD:127.0.0.1:8858}
    port: 8719

  # 规则配置
  rule:
    # 流控规则
    flow:
      - resource: /api/pay/create
        limit-app: default
        grade: 1
        count: 100
        strategy: 0
        control-behavior: 0

    # 熔断规则
    degrade:
      - resource: /api/pay/create
        grade: 3
        count: 5
        time-window: 10

    # 热点规则
    param:
      - resource: /api/pay/query
        index: 0
        count: 100
        grade: 1
```

## 网关路由配置模板

```yaml
spring:
  cloud:
    gateway:
      discovery:
        locator:
          enabled: true
          lower-case-service-id: true

      routes:
        - id: service-route
          uri: lb://zshlpay-service
          predicates:
            - Path=/api/service/**
          filters:
            - StripPrefix=1
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 100
                redis-rate-limiter.burstCapacity: 200

        - id: admin-route
          uri: lb://zshlpay-admin
          predicates:
            - Path=/api/admin/**
          filters:
            - StripPrefix=1

        - id: shop-route
          uri: lb://zshlpay-shop
          predicates:
            - Path=/api/shop/**
          filters:
            - StripPrefix=1

      globalcors:
        cors-configurations:
          '[/**]':
            allowed-origin-patterns: "*"
            allowed-methods:
              - GET
              - POST
              - PUT
              - DELETE
            allowed-headers: "*"
            allow-credentials: true
            max-age: 3600
```
