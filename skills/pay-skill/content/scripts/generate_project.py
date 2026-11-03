#!/usr/bin/env python3
"""
zshlpay Spring Cloud 项目生成器
基于JDK21，支持多MQ和国产数据库
"""
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import json

# 颜色定义
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log_info(msg: str):
    print(f"{Colors.OKBLUE}[INFO]{Colors.ENDC} {msg}")

def log_success(msg: str):
    print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} {msg}")

def log_warning(msg: str):
    print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} {msg}")

def log_error(msg: str):
    print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {msg}")

class ProjectGenerator:
    """项目生成器类"""

    # Java版本配置
    JAVA_VERSION = "21"
    SPRING_BOOT_VERSION = "3.2.5"
    SPRING_CLOUD_VERSION = "2023.0.1"
    SPRING_CLOUD_ALIBABA_VERSION = "2023.0.1.2"

    # 支持的MQ类型
    MQ_TYPES = ["kafka", "rabbitmq", "rocketmq", "activemq"]

    # 支持的数据库类型
    DB_TYPES = ["mysql", "dm", "kingbase", "gaussdb", "oceanbase", "shentong", "postgresql"]

    def __init__(self, output_dir: str, project_name: str = "zshlpay-cloud"):
        self.output_dir = Path(output_dir)
        self.project_name = project_name
        self.project_path = self.output_dir / project_name

    def create_parent_pom(self) -> str:
        """生成父POM文件内容"""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.zshlpay</groupId>
    <artifactId>{self.project_name}</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>
    <name>zshlpay Spring Cloud</name>
    <description>zshlpay支付平台 - Spring Cloud微服务架构</description>

    <properties>
        <java.version>{self.JAVA_VERSION}</java.version>
        <maven.compiler.source>{self.JAVA_VERSION}</maven.compiler.source>
        <maven.compiler.target>{self.JAVA_VERSION}</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>

        <spring-boot.version>{self.SPRING_BOOT_VERSION}</spring-boot.version>
        <spring-cloud.version>{self.SPRING_CLOUD_VERSION}</spring-cloud.version>
        <spring-cloud-alibaba.version>{self.SPRING_CLOUD_ALIBABA_VERSION}</spring-cloud-alibaba.version>

        <mybatis-plus.version>3.5.6</mybatis-plus.version>
        <druid.version>1.2.21</druid.version>
        <fastjson2.version>2.0.46</fastjson2.version>
        <jwt.version>0.12.5</jwt.version>
        <hutool.version>5.8.26</hutool.version>
        <lombok.version>1.18.30</lombok.version>
        <swagger.version>2.2.22</swagger.version>
        <sentinel.version>1.8.8</sentinel.version>

        <!-- MQ版本 -->
        <kafka.version>3.7.0</kafka.version>
        <rabbitmq.version>5.21.0</rabbitmq.version>
        <rocketmq.version>2.2.3</rocketmq.version>
        <activemq.version>5.18.4</activemq.version>

        <!-- 国产数据库驱动版本 -->
        <dm.version>8.1.2.192</dm.version>
        <kingbase.version>8.6.0</kingbase.version>
        <oceanbase.version>2.4.12</oceanbase.version>
        <postgresql.version>42.7.3</postgresql.version>
    </properties>

    <dependencyManagement>
        <dependencies>
            <!-- Spring Boot Dependencies -->
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-dependencies</artifactId>
                <version>${{spring-boot.version}}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>

            <!-- Spring Cloud Dependencies -->
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${{spring-cloud.version}}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>

            <!-- Spring Cloud Alibaba Dependencies -->
            <dependency>
                <groupId>com.alibaba.cloud</groupId>
                <artifactId>spring-cloud-alibaba-dependencies</artifactId>
                <version>${{spring-cloud-alibaba.version}}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>

            <!-- MyBatis-Plus -->
            <dependency>
                <groupId>com.baomidou</groupId>
                <artifactId>mybatis-plus-boot-starter</artifactId>
                <version>${{mybatis-plus.version}}</version>
            </dependency>

            <!-- JWT -->
            <dependency>
                <groupId>io.jsonwebtoken</groupId>
                <artifactId>jjwt-api</artifactId>
                <version>${{jwt.version}}</version>
            </dependency>
            <dependency>
                <groupId>io.jsonwebtoken</groupId>
                <artifactId>jjwt-impl</artifactId>
                <version>${{jwt.version}}</version>
            </dependency>
            <dependency>
                <groupId>io.jsonwebtoken</groupId>
                <artifactId>jjwt-jackson</artifactId>
                <version>${{jwt.version}}</version>
            </dependency>

            <!-- Swagger -->
            <dependency>
                <groupId>com.github.xiaoymin</groupId>
                <artifactId>knife4j-openapi3-jakarta-spring-boot-starter</artifactId>
                <version>${{swagger.version}}</version>
            </dependency>

            <!-- Sentinel -->
            <dependency>
                <groupId>com.alibaba.csp</groupId>
                <artifactId>sentinel-core</artifactId>
                <version>${{sentinel.version}}</version>
            </dependency>

            <!-- Kafka -->
            <dependency>
                <groupId>org.apache.kafka</groupId>
                <artifactId>kafka-clients</artifactId>
                <version>${{kafka.version}}</version>
            </dependency>

            <!-- RabbitMQ -->
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-starter-amqp</artifactId>
                <version>${{rabbitmq.version}}</version>
            </dependency>

            <!-- RocketMQ -->
            <dependency>
                <groupId>org.apache.rocketmq</groupId>
                <artifactId>rocketmq-spring-boot-starter</artifactId>
                <version>${{rocketmq.version}}</version>
            </dependency>

            <!-- ActiveMQ -->
            <dependency>
                <groupId>org.apache.activemq</groupId>
                <artifactId>activemq-client</artifactId>
                <version>${{activemq.version}}</version>
            </dependency>

            <!-- 国产数据库驱动 -->
            <dependency>
                <groupId>com.dameng</groupId>
                <artifactId>DmJdbcDriver18</artifactId>
                <version>${{dm.version}}</version>
            </dependency>
            <dependency>
                <groupId>com.kingbase8</groupId>
                <artifactId>kingbase8</artifactId>
                <version>${{kingbase.version}}</version>
            </dependency>
            <dependency>
                <groupId>com.oceanbase</groupId>
                <artifactId>oceanbase-client</artifactId>
                <version>${{oceanbase.version}}</version>
            </dependency>
            <dependency>
                <groupId>org.postgresql</groupId>
                <artifactId>postgresql</artifactId>
                <version>${{postgresql.version}}</version>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <modules>
        <module>zshlpay-common</module>
        <module>zshlpay-common-util</module>
        <module>zshlpay-api</module>
        <module>zshlpay-gateway</module>
        <module>zshlpay-service</module>
        <module>zshlpay-admin</module>
        <module>zshlpay-shop</module>
    </modules>

    <build>
        <pluginManagement>
            <plugins>
                <plugin>
                    <groupId>org.springframework.boot</groupId>
                    <artifactId>spring-boot-maven-plugin</artifactId>
                    <version>${{spring-boot.version}}</version>
                    <configuration>
                        <excludes>
                            <exclude>
                                <groupId>org.projectlombok</groupId>
                                <artifactId>lombok</artifactId>
                            </exclude>
                        </excludes>
                    </configuration>
                </plugin>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-compiler-plugin</artifactId>
                    <version>3.12.1</version>
                    <configuration>
                        <source>{self.JAVA_VERSION}</source>
                        <target>{self.JAVA_VERSION}</target>
                    </configuration>
                </plugin>
            </plugins>
        </pluginManagement>
    </build>
</project>
'''

    def create_module_pom(self, module_name: str, dependencies: List[str]) -> str:
        """生成模块POM文件"""
        dep_xml = ""
        for dep in dependencies:
            dep_xml += f"        <dependency>\n            <groupId>{dep['group']}</groupId>\n            <artifactId>{dep['artifact']}</artifactId>\n        </dependency>\n"

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.zshlpay</groupId>
        <artifactId>{self.project_name}</artifactId>
        <version>1.0.0</version>
    </parent>

    <artifactId>{module_name}</artifactId>
    <packaging>jar</packaging>
    <name>{module_name}</name>

    <dependencies>
{dep_xml}    </dependencies>
</project>
'''

    def create_application_main(self, module_name: str, class_name: str) -> str:
        """生成启动类"""
        return f'''package com.zshlpay.{module_name};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.openfeign.EnableFeignClients;
import org.springframework.context.annotation.ComponentScan;

/**
 * {module_name} 启动类
 *
 * @author zshlpay
 * @version 1.0.0
 */
@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients(basePackages = "com.zshlpay.api.client")
@ComponentScan(basePackages = {{"com.zshlpay"}})
public class {class_name} {{

    public static void main(String[] args) {{
        SpringApplication.run({class_name}.class, args);
        System.out.println("===========================================");
        System.out.println("  {module_name} 启动成功!");
        System.out.println("===========================================");
    }}
}}
'''

    def create_application_yml(self, port: int, service_name: str) -> str:
        """生成application.yml"""
        return f'''server:
  port: {port}
  servlet:
    context-path: /

spring:
  application:
    name: {service_name}
  profiles:
    active: @spring.profiles.active@
  cloud:
    nacos:
      discovery:
        server-addr: ${{NACOS_SERVER:127.0.0.1:8848}}
        namespace: ${{NACOS_NAMESPACE:public}}
        group: ${{NACOS_GROUP:DEFAULT_GROUP}}
      config:
        server-addr: ${{NACOS_SERVER:127.0.0.1:8848}}
        namespace: ${{NACOS_NAMESPACE:public}}
        file-extension: yml
        shared-configs:
          - data-id: common-config.yml
            group: ${{NACOS_GROUP:DEFAULT_GROUP}}
            refresh: true

  # 数据源配置
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://${{DB_HOST:127.0.0.1}}:${{DB_PORT:3306}}/${{DB_NAME:zshlpay}}?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&useSSL=false
    username: ${{DB_USER:root}}
    password: ${{DB_PASSWORD:}}
    type: com.alibaba.druid.pool.DruidDataSource
    druid:
      initial-size: 5
      min-idle: 5
      max-active: 20
      max-wait: 60000
      test-while-idle: true
      test-on-borrow: false
      test-on-return: false
      validation-query: SELECT 1
      time-between-eviction-runs-millis: 60000
      min-evictable-idle-time-millis: 300000

  # Redis配置
  data:
    redis:
      host: ${{REDIS_HOST:127.0.0.1}}
      port: ${{REDIS_PORT:6379}}
      password: ${{REDIS_PASSWORD:}}
      database: 0
      timeout: 5000
      lettuce:
        pool:
          max-active: 8
          max-idle: 8
          min-idle: 2
          max-wait: 2000

  # Jackson配置
  jackson:
    date-format: yyyy-MM-dd HH:mm:ss
    time-zone: GMT+8
    serialization:
      write-dates-as-timestamps: false
      fail-on-empty-beans: false
    deserialization:
      fail-on-unknown-properties: false

# Feign配置
feign:
  client:
    config:
      default:
        connect-timeout: 10000
        read-timeout: 30000
        logger-level: basic
  httpclient:
    enabled: true
    max-connections: 200
    max-connections-per-route: 50
  compression:
    request:
      enabled: true
    response:
      enabled: true

# Sentinel配置
sentinel:
  eager: true
  transport:
    dashboard: ${{SENTINEL_DASHBOARD:127.0.0.1:8858}}
    port: 8719

# Actuator配置
management:
  endpoints:
    web:
      exposure:
        include: "*"
  endpoint:
    health:
      show-details: always
  metrics:
    export:
      prometheus:
        enabled: true

# 日志配置
logging:
  level:
    com.zshlpay: ${{LOG_LEVEL:INFO}}
    org.springframework: WARN
  pattern:
    console: "%d{{yyyy-MM-dd HH:mm:ss.SSS}} [%thread] %-5level %logger{{20}} - %msg%n"
'''

    def create_gateway_pom(self) -> str:
        """生成网关模块POM"""
        return self.create_module_pom("zshlpay-gateway", [
            {"group": "org.springframework.boot", "artifactId": "spring-boot-starter-webflux"},
            {"group": "org.springframework.cloud", "artifactId": "spring-cloud-starter-gateway"},
            {"group": "org.springframework.cloud", "artifactId": "spring-cloud-starter-loadbalancer"},
            {"group": "org.springframework.cloud", "artifactId": "spring-cloud-starter-openfeign"},
            {"group": "com.alibaba.cloud", "artifactId": "spring-cloud-starter-alibaba-nacos-discovery"},
            {"group": "com.alibaba.cloud", "artifactId": "spring-cloud-starter-alibaba-nacos-config"},
            {"group": "com.alibaba.csp", "artifactId": "sentinel-spring-cloud-gateway-adapter"},
            {"group": "io.jsonwebtoken", "artifactId": "jjwt-api"},
            {"group": "io.jsonwebtoken", "artifactId": "jjwt-impl"},
            {"group": "io.jsonwebtoken", "artifactId": "jjwt-jackson"},
            {"group": "org.projectlombok", "artifactId": "lombok"},
            {"group": "com.github.xiaoymin", "artifactId": "knife4j-openapi3-jakarta-spring-boot-starter"},
        ])

    def create_gateway_application(self) -> str:
        """生成网关启动类"""
        return f'''package com.zshlpay.gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.openfeign.EnableFeignClients;

/**
 * 网关服务启动类
 */
@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients(basePackages = "com.zshlpay.api.client")
public class GatewayApplication {{

    public static void main(String[] args) {{
        SpringApplication.run(GatewayApplication.class, args);
        System.out.println("===========================================");
        System.out.println("  Gateway 启动成功!");
        System.out.println("===========================================");
    }}
}}
'''

    def create_gateway_yml(self) -> str:
        """生成网关配置"""
        return f'''server:
  port: 8080

spring:
  application:
    name: zshlpay-gateway
  cloud:
    nacos:
      discovery:
        server-addr: ${{NACOS_SERVER:127.0.0.1:8848}}
        namespace: ${{NACOS_NAMESPACE:public}}
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
            allowed-methods: "*"
            allowed-headers: "*"
            allow-credentials: true
            max-age: 3600

  # Redis配置 (用于Token存储)
  data:
    redis:
      host: ${{REDIS_HOST:127.0.0.1}}
      port: ${{REDIS_PORT:6379}}
      password: ${{REDIS_PASSWORD:}}
      database: 0

# Sentinel配置
sentinel:
  eager: true
  transport:
    dashboard: ${{SENTINEL_DASHBOARD:127.0.0.1:8858}}

# JWT配置
jwt:
  secret: ${{JWT_SECRET:zshlpay-secret-key-change-in-production}}
  expiration: 86400000

# 日志
logging:
  level:
    org.springframework.cloud.gateway: DEBUG
'''

    def create_common_result(self) -> str:
        """生成统一响应类"""
        return '''package com.zshlpay.common.result;

import lombok.Data;
import java.io.Serializable;

/**
 * 统一响应结果
 *
 * @author zshlpay
 */
@Data
public class Result<T> implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 状态码 */
    private Integer code;

    /** 消息 */
    private String message;

    /** 数据 */
    private T data;

    /** 时间戳 */
    private Long timestamp;

    /** 请求ID */
    private String requestId;

    public Result() {
        this.timestamp = System.currentTimeMillis();
    }

    public Result(Integer code, String message, T data) {
        this.code = code;
        this.message = message;
        this.data = data;
        this.timestamp = System.currentTimeMillis();
    }

    public static <T> Result<T> success() {
        return new Result<>(200, "操作成功", null);
    }

    public static <T> Result<T> success(T data) {
        return new Result<>(200, "操作成功", data);
    }

    public static <T> Result<T> success(String message, T data) {
        return new Result<>(200, message, data);
    }

    public static <T> Result<T> fail() {
        return new Result<>(500, "操作失败", null);
    }

    public static <T> Result<T> fail(String message) {
        return new Result<>(500, message, null);
    }

    public static <T> Result<T> fail(Integer code, String message) {
        return new Result<>(code, message, null);
    }

    public static <T> Result<T> fail(Integer code, String message, T data) {
        return new Result<>(code, message, data);
    }

    public boolean isSuccess() {
        return this.code != null && this.code == 200;
    }
}
'''

    def create_mybatis_plus_config(self) -> str:
        """生成MyBatis-Plus配置"""
        return '''package com.zshlpay.common.config;

import com.baomidou.mybatisplus.annotation.DbType;
import com.baomidou.mybatisplus.core.handlers.MetaObjectHandler;
import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;
import org.apache.ibatis.reflection.MetaObject;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.LocalDateTime;

/**
 * MyBatis-Plus 配置
 *
 * @author zshlpay
 */
@Configuration
public class MyBatisPlusConfig {

    /**
     * 分页插件
     */
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
        return interceptor;
    }

    /**
     * 自动填充处理
     */
    @Bean
    public MetaObjectHandler metaObjectHandler() {
        return new MetaObjectHandler() {
            @Override
            public void insertFill(MetaObject metaObject) {
                this.strictInsertFill(metaObject, "createTime", LocalDateTime.class, LocalDateTime.now());
                this.strictInsertFill(metaObject, "updateTime", LocalDateTime.class, LocalDateTime.now());
            }

            @Override
            public void updateFill(MetaObject metaObject) {
                this.strictUpdateFill(metaObject, "updateTime", LocalDateTime.class, LocalDateTime.now());
            }
        };
    }
}
'''

    def create_kafka_config(self) -> str:
        """生成Kafka配置"""
        return '''package com.zshlpay.service.config;

import org.apache.kafka.clients.admin.AdminClientConfig;
import org.apache.kafka.clients.admin.NewTopic;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.config.TopicBuilder;
import org.springframework.kafka.core.*;

import java.util.HashMap;
import java.util.Map;

/**
 * Kafka 配置
 *
 * @author zshlpay
 */
@Configuration
@EnableKafka
public class KafkaConfig {

    @Value("${{spring.kafka.bootstrap-servers:127.0.0.1:9092}}")
    private String bootstrapServers;

    @Value("${{spring.kafka.consumer.group-id:zshlpay-group}}")
    private String groupId;

    // ==================== Admin配置 ====================

    @Bean
    public KafkaAdmin kafkaAdmin() {
        Map<String, Object> configs = new HashMap<>();
        configs.put(AdminClientConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        return new KafkaAdmin(configs);
    }

    // ==================== Topic配置 ====================

    @Bean
    public NewTopic payTopic() {
        return TopicBuilder.name("pay-notify-topic")
                .partitions(3)
                .replicas(1)
                .build();
    }

    @Bean
    public NewTopic orderTopic() {
        return TopicBuilder.name("order-topic")
                .partitions(3)
                .replicas(1)
                .build();
    }

    // ==================== Producer配置 ====================

    @Bean
    public ProducerFactory<String, String> producerFactory() {
        Map<String, Object> configs = new HashMap<>();
        configs.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        configs.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        configs.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        configs.put(ProducerConfig.ACKS_CONFIG, "all");
        configs.put(ProducerConfig.RETRIES_CONFIG, 3);
        configs.put(ProducerConfig.BATCH_SIZE_CONFIG, 16384);
        configs.put(ProducerConfig.LINGER_MS_CONFIG, 1);
        return new DefaultKafkaProducerFactory<>(configs);
    }

    @Bean
    public KafkaTemplate<String, String> kafkaTemplate() {
        return new KafkaTemplate<>(producerFactory());
    }

    // ==================== Consumer配置 ====================

    @Bean
    public ConsumerFactory<String, String> consumerFactory() {
        Map<String, Object> configs = new HashMap<>();
        configs.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        configs.put(ConsumerConfig.GROUP_ID_CONFIG, groupId);
        configs.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        configs.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        configs.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        configs.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        return new DefaultKafkaConsumerFactory<>(configs);
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> kafkaListenerContainerFactory() {
        ConcurrentKafkaListenerContainerFactory<String, String> factory =
                new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory());
        factory.setConcurrency(3);
        factory.getContainerProperties().setAckMode(
                org.springframework.kafka.listener.ContainerProperties.AckMode.MANUAL_IMMEDIATE);
        return factory;
    }
}
'''

    def create_rabbitmq_config(self) -> str:
        """生成RabbitMQ配置"""
        return '''package com.zshlpay.service.config;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.config.SimpleRabbitListenerContainerFactory;
import org.springframework.amqp.rabbit.connection.CachingConnectionFactory;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * RabbitMQ 配置
 *
 * @author zshlpay
 */
@Configuration
public class RabbitMQConfig {

    @Value("${{spring.rabbitmq.host:127.0.0.1}}")
    private String host;

    @Value("${{spring.rabbitmq.port:5672}}")
    private int port;

    @Value("${{spring.rabbitmq.username:guest}}")
    private String username;

    @Value("${{spring.rabbitmq.password:guest}}")
    private String password;

    public static final String PAY_EXCHANGE = "pay.exchange";
    public static final String PAY_QUEUE = "pay.queue";
    public static final String PAY_ROUTING_KEY = "pay.notify";

    public static final String ORDER_EXCHANGE = "order.exchange";
    public static final String ORDER_QUEUE = "order.queue";
    public static final String ORDER_ROUTING_KEY = "order.create";

    @Bean
    public ConnectionFactory connectionFactory() {
        CachingConnectionFactory connectionFactory = new CachingConnectionFactory();
        connectionFactory.setHost(host);
        connectionFactory.setPort(port);
        connectionFactory.setUsername(username);
        connectionFactory.setPassword(password);
        return connectionFactory;
    }

    @Bean
    public MessageConverter messageConverter() {
        return new Jackson2JsonMessageConverter();
    }

    @Bean
    public RabbitTemplate rabbitTemplate() {
        RabbitTemplate rabbitTemplate = new RabbitTemplate(connectionFactory());
        rabbitTemplate.setMessageConverter(messageConverter());
        return rabbitTemplate;
    }

    @Bean
    public SimpleRabbitListenerContainerFactory rabbitListenerContainerFactory() {
        SimpleRabbitListenerContainerFactory factory = new SimpleRabbitListenerContainerFactory();
        factory.setConnectionFactory(connectionFactory());
        factory.setMessageConverter(messageConverter());
        factory.setConcurrentConsumers(3);
        factory.setMaxConcurrentConsumers(10);
        factory.setAcknowledgeMode(AcknowledgeMode.MANUAL);
        return factory;
    }

    // ==================== Queue/Exchange/Binding配置 ====================

    @Bean
    public Queue payQueue() {
        return QueueBuilder.durable(PAY_QUEUE).build();
    }

    @Bean
    public DirectExchange payExchange() {
        return new DirectExchange(PAY_EXCHANGE);
    }

    @Bean
    public Binding payBinding() {
        return BindingBuilder.bind(payQueue()).to(payExchange()).with(PAY_ROUTING_KEY);
    }

    @Bean
    public Queue orderQueue() {
        return QueueBuilder.durable(ORDER_QUEUE).build();
    }

    @Bean
    public DirectExchange orderExchange() {
        return new DirectExchange(ORDER_EXCHANGE);
    }

    @Bean
    public Binding orderBinding() {
        return BindingBuilder.bind(orderQueue()).to(orderExchange()).with(ORDER_ROUTING_KEY);
    }
}
'''

    def create_rocketmq_config(self) -> str:
        """生成RocketMQ配置"""
        return '''package com.zshlpay.service.config;

import org.apache.rocketmq.spring.autoconfigure.RocketMQProperties;
import org.apache.rocketmq.spring.config.RocketMQConfigUtils;
import org.apache.rocketmq.spring.config.RocketMQProperties;
import org.apache.rocketmq.spring.core.RocketMQTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/**
 * RocketMQ 配置
 *
 * @author zshlpay
 */
@Configuration
@ConditionalOnProperty(prefix = "rocketmq", name = "name-server")
public class RocketMQConfig {

    @Value("${{rocketmq.name-server:127.0.0.1:9876}}")
    private String nameServer;

    @Value("${{rocketmq.consumer.group:zshlpay-consumer-group}}")
    private String consumerGroup;

    @Bean
    public RocketMQProperties rocketMQProperties() {
        RocketMQProperties properties = new RocketMQProperties();
        properties.setNameServer(nameServer);
        return properties;
    }

    @Bean
    public RocketMQTemplate rocketMQTemplate() {
        RocketMQTemplate template = new RocketMQTemplate();
        return template;
    }
}
'''

    def create_dynamic_datasource_config(self, db_type: str) -> str:
        """生成动态数据源配置"""
        return f'''package com.zshlpay.common.config;

import com.alibaba.druid.pool.DruidDataSource;
import com.baomidou.mybatisplus.extension.spring.MybatisPlusSqlSessionFactoryBean;
import org.apache.ibatis.session.SqlSessionFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;

import javax.sql.DataSource;

/**
 * 数据源配置 - {db_type}
 *
 * @author zshlpay
 */
@Configuration
public class DataSourceConfig {{

    @Value("${{DB_HOST:127.0.0.1}}")
    private String host;

    @Value("${{DB_PORT:3306}}")
    private int port;

    @Value("${{DB_NAME:zshlpay}}")
    private String database;

    @Value("${{DB_USER:root}}")
    private String username;

    @Value("${{DB_PASSWORD:}}")
    private String password;

    @Bean
    public DataSource dataSource() {{
        DruidDataSource dataSource = new DruidDataSource();
        dataSource.setUrl(buildJdbcUrl());
        dataSource.setUsername(username);
        dataSource.setPassword(password);
        dataSource.setDriverClassName(getDriverClassName());
        dataSource.setInitialSize(5);
        dataSource.setMinIdle(5);
        dataSource.setMaxActive(20);
        dataSource.setMaxWait(60000);
        dataSource.setTestWhileIdle(true);
        dataSource.setTestOnBorrow(false);
        dataSource.setTestOnReturn(false);
        dataSource.setValidationQuery("SELECT 1");
        return dataSource;
    }}

    private String buildJdbcUrl() {{
        return switch (db_type) {{
            case "dm" -> String.format(
                "jdbc:dm://%s:%d/%s?schema=%s&zeroDateTimeBehavior=convertToNull",
                host, port, database, database
            );
            case "kingbase" -> String.format(
                "jdbc:kingbase8://%s:%d/%s",
                host, port, database
            );
            case "oceanbase" -> String.format(
                "jdbc:oceanbase://%s:%d/%s",
                host, port, database
            );
            case "postgresql" -> String.format(
                "jdbc:postgresql://%s:%d/%s",
                host, port, database
            );
            default -> String.format(
                "jdbc:mysql://%s:%d/%s?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&useSSL=false",
                host, port, database
            );
        }};
    }}

    private String getDriverClassName() {{
        return switch (db_type) {{
            case "dm" -> "dm.jdbc.driver.DmDriver";
            case "kingbase" -> "com.kingbase8.Driver";
            case "oceanbase" -> "com.oceanbase.jdbc.Driver";
            case "postgresql" -> "org.postgresql.Driver";
            default -> "com.mysql.cj.jdbc.Driver";
        }};
    }}

    @Bean
    public SqlSessionFactory sqlSessionFactory(DataSource dataSource) throws Exception {{
        MybatisPlusSqlSessionFactoryBean sqlSessionFactory = new MybatisPlusSqlSessionFactoryBean();
        sqlSessionFactory.setDataSource(dataSource);
        sqlSessionFactory.setMapperLocations(
            new PathMatchingResourcePatternResolver().getResources("classpath*:/mapper/**/*.xml")
        );
        sqlSessionFactory.setTypeAliasesPackage("com.zshlpay.**.entity");
        return sqlSessionFactory.getObject();
    }}

    @Bean
    public DataSourceTransactionManager transactionManager(DataSource dataSource) {{
        return new DataSourceTransactionManager(dataSource);
    }}
}}
'''

    def create_service_application(self) -> str:
        """生成service模块启动类"""
        return self.create_application_main("service", "ServiceApplication")

    def create_admin_application(self) -> str:
        """生成admin模块启动类"""
        return self.create_application_main("admin", "AdminApplication")

    def create_shop_application(self) -> str:
        """生成shop模块启动类"""
        return self.create_application_main("shop", "ShopApplication")

    def create_service_pom(self, mq_list: List[str], db_type: str) -> str:
        """生成service模块POM"""
        deps = [
            {"group": "org.springframework.boot", "artifactId": "spring-boot-starter-web"},
            {"group": "org.springframework.boot", "artifactId": "spring-boot-starter-validation"},
            {"group": "com.alibaba.cloud", "artifactId": "spring-cloud-starter-alibaba-nacos-discovery"},
            {"group": "com.alibaba.cloud", "artifactId": "spring-cloud-starter-alibaba-nacos-config"},
            {"group": "com.alibaba.cloud", "artifactId": "spring-cloud-starter-alibaba-sentinel"},
            {"group": "com.baomidou", "artifactId": "mybatis-plus-boot-starter"},
            {"group": "org.springframework.boot", "artifactId": "spring-boot-starter-data-redis"},
            {"group": "com.github.xiaoymin", "artifactId": "knife4j-openapi3-jakarta-spring-boot-starter"},
            {"group": "org.projectlombok", "artifactId": "lombok"},
        ]

        # MQ依赖
        if "kafka" in mq_list:
            deps.append({"group": "org.springframework.kafka", "artifactId": "spring-kafka"})
        if "rabbitmq" in mq_list:
            deps.append({"group": "org.springframework.boot", "artifactId": "spring-boot-starter-amqp"})
        if "rocketmq" in mq_list:
            deps.append({"group": "org.apache.rocketmq", "artifactId": "rocketmq-spring-boot-starter"})
        if "activemq" in mq_list:
            deps.append({"group": "org.apache.activemq", "artifactId": "activemq-client"})

        # 数据库驱动
        if db_type == "dm":
            deps.append({"group": "com.dameng", "artifactId": "DmJdbcDriver18"})
        elif db_type == "kingbase":
            deps.append({"group": "com.kingbase8", "artifactId": "kingbase8"})
        elif db_type == "oceanbase":
            deps.append({"group": "com.oceanbase", "artifactId": "oceanbase-client"})
        elif db_type == "postgresql":
            deps.append({"group": "org.postgresql", "artifactId": "postgresql"})
        else:
            deps.append({"group": "com.mysql", "artifactId": "mysql-connector-j"})

        return self.create_module_pom("zshlpay-service", deps)

    def generate(self, mq_types: List[str], db_type: str):
        """生成项目结构"""
        log_info(f"开始生成项目: {self.project_name}")
        log_info(f"支持的MQ: {', '.join(mq_types)}")
        log_info(f"数据库类型: {db_type}")

        # 创建目录结构
        modules = ["zshlpay-common", "zshlpay-common-util", "zshlpay-api",
                   "zshlpay-gateway", "zshlpay-service", "zshlpay-admin", "zshlpay-shop"]

        for module in modules:
            module_path = self.project_path / module / "src" / "main" / "java" / "com" / "zshlpay"
            module_parts = module.replace("zshlpay-", "").split("-")
            for part in module_parts:
                module_path = module_path / part
            module_path.mkdir(parents=True, exist_ok=True)

            resources_path = self.project_path / module / "src" / "main" / "resources"
            resources_path.mkdir(parents=True, exist_ok=True)

        log_success(f"目录结构创建完成")

        # 写入父POM
        parent_pom = self.project_path / "pom.xml"
        parent_pom.write_text(self.create_parent_pom(), encoding='utf-8')
        log_success(f"父POM创建完成")

        # 写入各模块POM
        self.project_path.joinpath("zshlpay-common", "pom.xml").write_text(
            self.create_module_pom("zshlpay-common", [
                {"group": "org.springframework.boot", "artifactId": "spring-boot-starter-web"},
                {"group": "org.springframework.boot", "artifactId": "spring-boot-starter-validation"},
                {"group": "org.projectlombok", "artifactId": "lombok"},
            ]), encoding='utf-8'
        )

        self.project_path.joinpath("zshlpay-common-util", "pom.xml").write_text(
            self.create_module_pom("zshlpay-common-util", [
                {"group": "org.projectlombok", "artifactId": "lombok"},
                {"group": "cn.hutool", "artifactId": "hutool-all"},
            ]), encoding='utf-8'
        )

        self.project_path.joinpath("zshlpay-api", "pom.xml").write_text(
            self.create_module_pom("zshlpay-api", [
                {"group": "org.springframework.cloud", "artifactId": "spring-cloud-starter-openfeign"},
                {"group": "org.projectlombok", "artifactId": "lombok"},
            ]), encoding='utf-8'
        )

        self.project_path.joinpath("zshlpay-gateway", "pom.xml").write_text(
            self.create_gateway_pom(), encoding='utf-8'
        )

        self.project_path.joinpath("zshlpay-service", "pom.xml").write_text(
            self.create_service_pom(mq_types, db_type), encoding='utf-8'
        )

        self.project_path.joinpath("zshlpay-admin", "pom.xml").write_text(
            self.create_module_pom("zshlpay-admin", [
                {"group": "org.springframework.boot", "artifactId": "spring-boot-starter-web"},
                {"group": "com.alibaba.cloud", "artifactId": "spring-cloud-starter-alibaba-nacos-discovery"},
                {"group": "com.alibaba.cloud", "artifactId": "spring-cloud-starter-alibaba-nacos-config"},
                {"group": "com.zshlpay", "artifactId": "zshlpay-api"},
                {"group": "org.projectlombok", "artifactId": "lombok"},
            ]), encoding='utf-8'
        )

        self.project_path.joinpath("zshlpay-shop", "pom.xml").write_text(
            self.create_module_pom("zshlpay-shop", [
                {"group": "org.springframework.boot", "artifactId": "spring-boot-starter-web"},
                {"group": "com.alibaba.cloud", "artifactId": "spring-cloud-starter-alibaba-nacos-discovery"},
                {"group": "com.alibaba.cloud", "artifactId": "spring-cloud-starter-alibaba-nacos-config"},
                {"group": "com.zshlpay", "artifactId": "zshlpay-api"},
                {"group": "org.projectlombok", "artifactId": "lombok"},
            ]), encoding='utf-8'
        )

        log_success(f"模块POM创建完成")

        # 写入启动类
        gateway_app_path = self.project_path / "zshlpay-gateway" / "src" / "main" / "java" / "com" / "zshlpay" / "gateway" / "GatewayApplication.java"
        gateway_app_path.parent.mkdir(parents=True, exist_ok=True)
        gateway_app_path.write_text(self.create_gateway_application(), encoding='utf-8')

        service_app_path = self.project_path / "zshlpay-service" / "src" / "main" / "java" / "com" / "zshlpay" / "service" / "ServiceApplication.java"
        service_app_path.parent.mkdir(parents=True, exist_ok=True)
        service_app_path.write_text(self.create_service_application(), encoding='utf-8')

        admin_app_path = self.project_path / "zshlpay-admin" / "src" / "main" / "java" / "com" / "zshlpay" / "admin" / "AdminApplication.java"
        admin_app_path.parent.mkdir(parents=True, exist_ok=True)
        admin_app_path.write_text(self.create_admin_application(), encoding='utf-8')

        shop_app_path = self.project_path / "zshlpay-shop" / "src" / "main" / "java" / "com" / "zshlpay" / "shop" / "ShopApplication.java"
        shop_app_path.parent.mkdir(parents=True, exist_ok=True)
        shop_app_path.write_text(self.create_shop_application(), encoding='utf-8')

        log_success(f"启动类创建完成")

        # 写入配置文件
        service_yml = self.project_path / "zshlpay-service" / "src" / "main" / "resources" / "application.yml"
        service_yml.write_text(self.create_application_yml(8081, "zshlpay-service"), encoding='utf-8')

        admin_yml = self.project_path / "zshlpay-admin" / "src" / "main" / "resources" / "application.yml"
        admin_yml.write_text(self.create_application_yml(8082, "zshlpay-admin"), encoding='utf-8')

        shop_yml = self.project_path / "zshlpay-shop" / "src" / "main" / "resources" / "application.yml"
        shop_yml.write_text(self.create_application_yml(8083, "zshlpay-shop"), encoding='utf-8')

        gateway_yml = self.project_path / "zshlpay-gateway" / "src" / "main" / "resources" / "application.yml"
        gateway_yml.write_text(self.create_gateway_yml(), encoding='utf-8')

        log_success(f"配置文件创建完成")

        # 写入公共类
        common_path = self.project_path / "zshlpay-common" / "src" / "main" / "java" / "com" / "zshlpay" / "common"
        result_path = common_path / "result"
        config_path = common_path / "config"
        result_path.mkdir(parents=True, exist_ok=True)
        config_path.mkdir(parents=True, exist_ok=True)

        result_path.joinpath("Result.java").write_text(self.create_common_result(), encoding='utf-8')
        config_path.joinpath("MyBatisPlusConfig.java").write_text(self.create_mybatis_plus_config(), encoding='utf-8')

        log_success(f"公共类创建完成")

        # 写入MQ配置
        if "kafka" in mq_types:
            service_config_path = self.project_path / "zshlpay-service" / "src" / "main" / "java" / "com" / "zshlpay" / "service" / "config"
            service_config_path.mkdir(parents=True, exist_ok=True)
            service_config_path.joinpath("KafkaConfig.java").write_text(self.create_kafka_config(), encoding='utf-8')
            log_success(f"Kafka配置创建完成")

        if "rabbitmq" in mq_types:
            service_config_path = self.project_path / "zshlpay-service" / "src" / "main" / "java" / "com" / "zshlpay" / "service" / "config"
            service_config_path.mkdir(parents=True, exist_ok=True)
            service_config_path.joinpath("RabbitMQConfig.java").write_text(self.create_rabbitmq_config(), encoding='utf-8')
            log_success(f"RabbitMQ配置创建完成")

        if "rocketmq" in mq_types:
            service_config_path = self.project_path / "zshlpay-service" / "src" / "main" / "java" / "com" / "zshlpay" / "service" / "config"
            service_config_path.mkdir(parents=True, exist_ok=True)
            service_config_path.joinpath("RocketMQConfig.java").write_text(self.create_rocketmq_config(), encoding='utf-8')
            log_success(f"RocketMQ配置创建完成")

        # 数据源配置
        service_config_path = self.project_path / "zshlpay-service" / "src" / "main" / "java" / "com" / "zshlpay" / "service" / "config"
        service_config_path.mkdir(parents=True, exist_ok=True)
        service_config_path.joinpath("DataSourceConfig.java").write_text(
            self.create_dynamic_datasource_config(db_type), encoding='utf-8'
        )
        log_success(f"数据源配置创建完成")

        # 创建README
        readme = f'''# {self.project_name}

## 项目说明

基于zshlpay支付平台的Spring Cloud微服务架构重构版本，采用JDK 21。

## 技术栈

- JDK 21
- Spring Boot 3.2.5
- Spring Cloud 2023.0.1
- Spring Cloud Alibaba 2023.0.1.2
- MyBatis-Plus 3.5.6
- Nacos 2.3.x
- Sentinel 1.8.8

## MQ支持

- Kafka 3.7.x
- RabbitMQ 5.21.x
- RocketMQ 2.2.3
- ActiveMQ 5.18.4

## 数据库支持

- MySQL 8.x (默认)
- 达梦 DM 8.x
- 人大金仓 Kingbase 8.x
- GaussDB 3.x
- OceanBase 2.x
- PostgreSQL 42.x

## 模块说明

| 模块 | 端口 | 说明 |
|------|------|------|
| zshlpay-gateway | 8080 | API网关 |
| zshlpay-service | 8081 | 业务服务 |
| zshlpay-admin | 8082 | 管理后台 |
| zshlpay-shop | 8083 | 商户平台 |

## 快速开始

### 1. 环境要求

- JDK 21+
- Maven 3.9+
- MySQL 5.7+/8.0+
- Redis 5.0+
- Nacos Server 2.x

### 2. 编译项目

```bash
mvn clean install -DskipTests
```

### 3. 启动服务

按顺序启动：
1. Nacos Server
2. Redis
3. MySQL
4. zshlpay-gateway
5. zshlpay-service
6. zshlpay-admin
7. zshlpay-shop

### 4. 访问地址

- 网关: http://localhost:8080
- Swagger: http://localhost:8081/doc.html
- Admin Swagger: http://localhost:8082/doc.html
- Shop Swagger: http://localhost:8083/doc.html

## 环境变量

```bash
export NACOS_SERVER=127.0.0.1:8848
export DB_HOST=127.0.0.1
export DB_PORT=3306
export DB_NAME=zshlpay
export DB_USER=root
export DB_PASSWORD=
export REDIS_HOST=127.0.0.1
export REDIS_PORT=6379
```

## 开发指南

详见 [SKILL.md](./SKILL.md)
'''
        self.project_path.joinpath("README.md").write_text(readme, encoding='utf-8')

        log_success(f"项目生成完成: {self.project_path}")
        return str(self.project_path)


def main():
    parser = argparse.ArgumentParser(description='zshlpay Spring Cloud 项目生成器')
    parser.add_argument('-o', '--output', default='.', help='输出目录')
    parser.add_argument('-n', '--name', default='zshlpay-cloud', help='项目名称')
    parser.add_argument('--mq', nargs='+', default=['kafka'],
                        choices=['kafka', 'rabbitmq', 'rocketmq', 'activemq'],
                        help='启用的MQ类型')
    parser.add_argument('--db', default='mysql',
                        choices=['mysql', 'dm', 'kingbase', 'gaussdb', 'oceanbase', 'shentong', 'postgresql'],
                        help='数据库类型')

    args = parser.parse_args()

    generator = ProjectGenerator(args.output, args.name)
    result_path = generator.generate(args.mq, args.db)
    print(f"\n项目已生成到: {result_path}")


if __name__ == '__main__':
    main()
