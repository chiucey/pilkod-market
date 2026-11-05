---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304402203f308658591ba3aad60be2eb12e440ad2cb4823ebf1e619a356d3a5de363a414022078bf8af059b1376f993f6f6b9a1cddfaa446452d59c442b55315e94aeeb69793
    ReservedCode2: 3046022100c71ff19f5aa72f4e978614b762b21b462fc990d569c119112a0adfad72ae778e022100d6a08f6eeaef6d44412b68348697845a5dce6fab59f49fdebae6846f1b032470
---

# zshlpay Spring Cloud 工程生成器 (JDK21增强版)

## 技能描述
基于原始zshlpay支付平台项目（Dubbo架构），自动生成Spring Cloud微服务架构版本的完整项目。
**本版本全面升级至JDK 21，支持多消息队列、 Kafka 及多种国产数据库，并提供标准化的包结构指导。**

## 源项目分析
- **原始架构**: Dubbo + Zookeeper
- **原始模块**:
  - `zshlpay-common`: 公共基类
  - `zshlpay-common-util`: 工具类
  - `zshlpay-dal`: 数据访问层
  - `zshlpay-dubbo-api`: Dubbo接口API
  - `zshlpay-dubbo-service`: 服务提供者（含支付通道）
  - `zshlpay-mgr`: 管理后台
  - `zshlpay-shop`: 商户平台

## 目标架构

### 模块转换对照
| 原模块 | 新模块 | 说明 |
|--------|--------|------|
| zshlpay-common | zshlpay-common | 保留，含Spring Cloud配置 |
| zshlpay-common-util | zshlpay-common-util | 保留，工具类 |
| zshlpay-dal | 合并到zshlpay-service | 数据访问层并入服务 |
| zshlpay-dubbo-api | zshlpay-api | Feign客户端接口 |
| zshlpay-dubbo-service | zshlpay-service | 支付核心服务 |
| zshlpay-mgr | zshlpay-admin | 管理后台 |
| zshlpay-shop | zshlpay-shop | 商户平台 |
| - | zshlpay-gateway | 新增API网关 |

### 技术栈版本 (JDK21增强)
```yaml
Java版本: 21 (LTS)
Spring Boot: 3.2.x
Spring Cloud: 2023.0.x
Spring Cloud Alibaba: 2023.0.x.x
MyBatis-Plus: 3.5.5+
Nacos: 2.3.x
Sentinel: 1.8.8+
Kafka: 3.6.x
```

### 多消息队列支持
| 消息队列 | 版本 | 依赖标识 |
|----------|------|----------|
| Apache Kafka | 3.6.x | kafka |
| RabbitMQ | 3.12.x | rabbitmq |
| RocketMQ | 5.2.x | rocketmq |
| Apache ActiveMQ | 5.18.x | activemq |

### 国产数据库支持
| 数据库 | 驱动版本 | 配置标识 |
|--------|----------|----------|
| 达梦 (DM) | 8.1.2.192 | dm |
| 人大金仓 (Kingbase) | 8.6.0 | kingbase |
| GaussDB | 3.0.x | gaussdb |
| OceanBase | 2.4.x | oceanbase |
| 神通 (ShenTong) | 5.10.x | shentong |
| MySQL | 8.0.x | mysql (默认) |
| PostgreSQL | 42.6.x | postgresql |

## 生成文件清单

### 1. 父POM
- `pom.xml` - 版本管理、依赖管理（所有模块统一版本）

### 2. 模块POM
- `zshlpay-common/pom.xml`
- `zshlpay-common-util/pom.xml`
- `zshlpay-api/pom.xml`
- `zshlpay-gateway/pom.xml`
- `zshlpay-service/pom.xml`
- `zshlpay-admin/pom.xml`
- `zshlpay-shop/pom.xml`

### 3. 启动类
- `GatewayApplication.java`
- `ServiceApplication.java`
- `AdminApplication.java`
- `ShopApplication.java`

### 4. 配置文件
- `application.yml` - 各模块主配置
- `bootstrap.yml` - Nacos配置
- `application-dev.yml` - 开发环境配置
- `application-prod.yml` - 生产环境配置

### 5. 公共配置
- `Result.java` - 统一响应
- `MyBatisPlusConfig.java`
- `RedisConfig.java`
- `SwaggerConfig.java`
- `WebConfig.java`
- `JacksonConfig.java`

### 6. Feign客户端
- `PayFeignClient.java`
- `MerchantFeignClient.java`
- `OrderFeignClient.java`

### 7. 网关配置
- `GlobalGatewayFilter.java`
- `SecurityConfig.java`
- `RateLimiterFilter.java`

### 8. MQ配置（按需启用）
- `KafkaConfig.java`
- `RabbitMQConfig.java`
- `RocketMQConfig.java`
- `ActiveMQConfig.java`

### 9. 数据库配置（按需启用）
- `DynamicDataSourceConfig.java`
- 各数据库专用配置类

### 10. 包结构模板
```
com.zshlpay
├── common/                    # 公共模块
│   ├── config/               # 配置类
│   ├── result/               # 统一响应
│   ├── exception/            # 异常处理
│   ├── enums/                # 枚举类
│   └── constant/             # 常量
├── util/                     # 工具模块
│   ├── date/                 # 日期工具
│   ├── encrypt/             # 加密工具
│   ├── http/                 # HTTP工具
│   └── string/               # 字符串工具
├── api/                      # API模块
│   ├── client/               # Feign客户端
│   ├── fallback/            # 降级处理
│   └── dto/                  # 传输对象
├── gateway/                  # 网关模块
│   ├── filter/              # 过滤器
│   └── handler/              # 处理器
├── service/                  # 服务模块（核心）
│   ├── controller/           # 控制器
│   ├── service/              # 服务接口
│   │   ├── impl/             # 服务实现
│   │   └── inner/            # 内部服务
│   ├── mapper/               # 数据访问
│   ├── entity/               # 实体类
│   ├── dto/                  # 数据传输对象
│   ├── vo/                   # 视图对象
│   ├── mq/                   # 消息队列
│   │   ├── kafka/            # Kafka生产者/消费者
│   │   ├── rabbitmq/        # RabbitMQ配置
│   │   ├── rocketmq/        # RocketMQ配置
│   │   └── activemq/        # ActiveMQ配置
│   ├── job/                  # 定时任务
│   └── channel/              # 支付通道
│       ├── wechat/          # 微信支付
│       ├── alipay/          # 支付宝
│       ├── union/           # 银联
│       └── channel/         # 通道基类
├── admin/                    # 管理后台模块
│   └── controller/
├── shop/                     # 商户平台模块
│   └── controller/
└── xxx-channel/             # 自定义支付通道
```

## 服务端口分配
| 服务 | 端口 |
|------|------|
| Gateway | 8080 |
| Service | 8081 |
| Admin | 8082 |
| Shop | 8083 |
| Nacos | 8848 |
| Sentinel | 8858 |

## 环境变量
```bash
# Nacos配置
NACOS_SERVER=127.0.0.1:8848
NACOS_NAMESPACE=public

# 数据库配置（根据实际数据库选择）
DB_TYPE=mysql          # mysql/dm/kingbase/gaussdb/oceanbase/shentong/postgresql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=zshlpay
DB_USER=root
DB_PASSWORD=

# Redis配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# Kafka配置
KAFKA_BOOTSTRAP_SERVERS=127.0.0.1:9092

# RabbitMQ配置
RABBITMQ_HOST=127.0.0.1
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=guest
RABBITMQ_PASSWORD=guest

# RocketMQ配置
ROCKETMQ_NAMESRV_ADDR=127.0.0.1:9876

# Sentinel配置
SENTINEL_DASHBOARD=127.0.0.1:8858
```

## 启动顺序
1. Nacos Server
2. MySQL/国产数据库
3. Redis
4. Kafka/RabbitMQ/RocketMQ（按需）
5. Sentinel Dashboard
6. zshlpay-gateway
7. zshlpay-service
8. zshlpay-admin
9. zshlpay-shop

## 业务保留
- 微信支付通道
- 支付宝支付通道
- 银联支付通道
- 订单管理
- 商户管理
- 定时任务
- 数据库实体

## MQ消息格式规范

### Kafka消息格式
```json
{
  "messageId": "uuid",
  "topic": "topic-name",
  "tag": "tag-name",
  "key": "business-key",
  "body": {},
  "timestamp": 1234567890,
  "headers": {}
}
```

### RabbitMQ消息格式
```json
{
  "exchange": "exchange-name",
  "routingKey": "routing-key",
  "message": {},
  "properties": {
    "deliveryMode": 2,
    "contentType": "application/json"
  }
}
```

## 数据库连接池配置
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
```

## 输出目录
生成的Spring Cloud项目将输出到用户指定目录，结构如下：
```
指定目录/
├── zshlpay-cloud/
│   ├── pom.xml
│   ├── README.md
│   ├── zshlpay-common/
│   ├── zshlpay-common-util/
│   ├── zshlpay-api/
│   ├── zshlpay-gateway/
│   ├── zshlpay-service/
│   ├── zshlpay-admin/
│   └── zshlpay-shop/
```

## 开发指南

### 创建新支付通道
1. 在 `zshlpay-service/src/main/java/com/zshlpay/service/channel/` 下创建通道包
2. 实现 `PayChannel` 接口
3. 在配置类中注册通道Bean
4. 添加通道配置到 `application.yml`

### 创建新MQ消费者
1. 在对应MQ包下创建消费者类
2. 使用 `@KafkaListener`、`@RabbitListener`、`@RocketMQListener` 或 `@JMSListener`
3. 实现消息处理逻辑

### 创建新数据库实体
1. 在 `entity` 包下创建实体类
2. 使用JPA注解或MyBatis-Plus注解
3. 在对应 `mapper` 包下创建Mapper接口
4. 注册Mapper到MyBatisPlusConfig

## 注意事项
1. JDK 21 需要使用 Spring Boot 3.x，不再支持 javax.*，需使用 jakarta.*
2. 部分国产数据库驱动需要商业授权，请确认使用许可
3. Kafka 消息顺序性保证需要配置 partition 和 key
4. 国产数据库连接请确保驱动兼容性
