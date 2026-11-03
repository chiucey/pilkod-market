---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 8ba9fab5a6a73c4dfaf5dc44cf3d5e15
    PropagateID: 8ba9fab5a6a73c4dfaf5dc44cf3d5e15
    ReservedCode1: 30440220571d152906ccb4b18219b51b37f2f93d84cf6e28a594a162f7af82d7c1c19ea30220441e24c673eac3167dbdfbfb8db0bde9d84e7de0d77ca67a49047fc203728b4b
    ReservedCode2: 304502202f7c887e20074065d5608a04a968cae2ed688a001f280f63add69e0822305755022100f6da8197ba53fa2fab2d36b6373667c3baea7626c235427abe2df070100302cd
description: Migrate Alibaba HSF framework to Apache Dubbo3 framework. Use when users ask to convert HSF-based microservices to Dubbo3, upgrade from HSF to Dubbo3, or migrate EDAS projects to Dubbo3.
name: hsf-to-dubbo3-migrator
---

# HSF to Dubbo3 Framework Migration Skill

## Overview

本技能用于将阿里云 HSF（High Speed Framework）框架的 Java 代码迁移到 Apache Dubbo3 框架。技能支持批量处理 Java 代码文件，自动识别 HSF 注解、依赖和配置，并转换为 Dubbo3 兼容格式，输出到指定目录。

## 功能特性

- **注解自动转换**：支持 HSFService、HSFReference、HSFProvider、HSFConsumer 等注解转换为 Dubbo3 注解
- **依赖智能替换**：自动分析并替换 Maven pom.xml 中的 HSF 依赖为 Dubbo3 依赖
- **配置迁移**：支持 HSF XML 配置和 properties 配置转换为 Dubbo3 YAML/Properties 配置
- **批量处理**：支持目录输入，递归处理所有 Java 文件
- **增量迁移**：支持部分迁移，保留不需要迁移的代码不变
- **目录隔离**：修改后的文件保存到新的指定目录，不影响原文件

## 使用场景

当用户要求将阿里云 HSF 框架项目迁移到 Dubbo3 框架时使用，包括：
- 微服务框架从 HSF 升级到 Dubbo3
- 阿里云 EDAS 项目迁移到开源 Dubbo3
- HSF 代码库的现代化改造
- 云原生微服务架构迁移

## 注解对照表

### 服务提供者注解

| HSF 注解 | Dubbo3 注解 | 说明 |
|---------|-------------|------|
| `@com.alibaba.boot.hsf.annotation.HSFProvider` | `@org.apache.dubbo.config.annotation.DubboService` | 服务暴露注解 |
| `@com.taobao.hsf.annotation.HSFService` | `@org.apache.dubbo.config.spring.ServiceBean` 或 `@DubboService` | 服务实现类注解 |
| `interfaceClass` | `interfaceClass` | 服务接口类 |
| `group` | `group` | 服务分组 |
| `version` | `version` | 服务版本 |
| `timeout` | `timeout` | 调用超时时间 |
| `retries` | `retries` | 重试次数 |

### 服务消费者注解

| HSF 注解 | Dubbo3 注解 | 说明 |
|---------|-------------|------|
| `@com.alibaba.boot.hsf.annotation.HSFConsumer` | `@org.apache.dubbo.config.annotation.DubboReference` | 服务引用注解 |
| `@com.taobao.hsf.annotation.HSFReference` | `@org.apache.dubbo.config.annotation.DubboReference` | 远程引用注解 |
| `group` | `group` | 服务分组 |
| `version` | `version` | 服务版本 |
| `timeout` | `timeout` | 调用超时时间 |
| `generic` | `generic` | 泛化调用 |
| `check` | `check` | 启动时检查 |

## 依赖对照表

### HSF 依赖

```xml
<!-- HSF Spring Boot 依赖 -->
<dependency>
    <groupId>com.alibaba.boot</groupId>
    <artifactId>hsf-spring-boot-starter</artifactId>
    <version>1.3.0</version>
</dependency>

<!-- HSF 基础依赖 -->
<dependency>
    <groupId>com.taobao.hsf</groupId>
    <artifactId>hsf</artifactId>
    <version>2.2.0</version>
</dependency>

<!-- Pandora 容器（Ali-Tomcat 环境） -->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-pandora</artifactId>
    <version>1.3.0.RELEASE</version>
</dependency>
```

### Dubbo3 依赖

```xml
<!-- Dubbo3 Spring Boot Starter -->
<dependency>
    <groupId>org.apache.dubbo</groupId>
    <artifactId>dubbo-spring-boot-starter</artifactId>
    <version>3.2.0</version>
</dependency>

<!-- Dubbo3 核心依赖 -->
<dependency>
    <groupId>org.apache.dubbo</groupId>
    <artifactId>dubbo</artifactId>
    <version>3.2.0</version>
</dependency>

<!-- 注册中心：Nacos（推荐） -->
<dependency>
    <groupId>com.alibaba.nacos</groupId>
    <artifactId>nacos-client</artifactId>
    <version>2.2.0</version>
</dependency>

<!-- 或使用 Zookeeper -->
<dependency>
    <groupId>org.apache.curator</groupId>
    <artifactId>curator-framework</artifactId>
    <version>5.2.0</version>
</dependency>
```

## 配置对照表

### HSF 配置（application.properties）

```properties
# HSF 配置示例
spring.hsf.version=2.3.5
spring.hsf.group=myGroup
spring.hsf.consumer.timeout=3000
spring.hsf.provider.threadpool.size=200
```

### Dubbo3 配置（application.yml）

```yaml
dubbo:
  application:
    name: my-application
    group: myGroup
  protocol:
    name: dubbo
    port: 20880
  registry:
    address: nacos://localhost:8848
    group: myGroup
  provider:
    timeout: 3000
    threads: 200
  consumer:
    timeout: 3000
    check: false
```

## 迁移步骤

### 1. 准备阶段

1. **代码备份**：确保原始代码已备份
2. **环境检查**：确认 JDK 版本（建议 JDK 8+）
3. **依赖分析**：识别所有 HSF 相关依赖
4. **注解扫描**：统计 HSF 注解使用情况

### 2. 依赖迁移

1. 移除 HSF 相关依赖
2. 添加 Dubbo3 依赖
3. 配置注册中心客户端依赖
4. 更新 Maven/Gradle 构建配置

### 3. 代码迁移

#### 3.1 服务提供者迁移

**HSF 代码示例：**

```java
@HSFProvider(serviceInterface = UserService.class, group = "userGroup", version = "1.0.0")
public class UserServiceImpl implements UserService {
    @Override
    public User getUserById(Long id) {
        return userRepository.findById(id);
    }
}
```

**Dubbo3 迁移后代码：**

```java
@DubboService(
    interfaceClass = UserService.class,
    group = "userGroup",
    version = "1.0.0",
    timeout = 3000,
    retries = 0
)
public class UserServiceImpl implements UserService {
    @Override
    public User getUserById(Long id) {
        return userRepository.findById(id);
    }
}
```

#### 3.2 服务消费者迁移

**HSF 代码示例：**

```java
@HSFConsumer(group = "userGroup", version = "1.0.0", timeout = 5000)
private UserService userService;
```

**Dubbo3 迁移后代码：**

```java
@DubboReference(
    interfaceClass = UserService.class,
    group = "userGroup",
    version = "1.0.0",
    timeout = 5000,
    check = false
)
private UserService userService;
```

#### 3.3 Spring XML 配置迁移

**HSF XML 配置：**

```xml
<bean id="userService" class="com.example.UserServiceImpl"/>
<dubbo:service interface="com.example.UserService" ref="userService" group="userGroup" version="1.0.0"/>
```

**Dubbo3 迁移后：**

```xml
<bean id="userService" class="com.example.UserServiceImpl"/>
<dubbo:service
    interface="com.example.UserService"
    ref="userService"
    group="userGroup"
    version="1.0.0"
    protocol="dubbo"
/>
```

### 4. 配置迁移

1. 创建 `dubbo.properties` 或 `application.yml`
2. 配置注册中心地址
3. 设置协议端口
4. 配置超时、重试等策略

### 5. 测试验证

1. 编译项目
2. 启动服务提供者
3. 验证服务注册
4. 启动服务消费者
5. 测试服务调用

## 常见问题处理

### 1. 服务无法注册

- 检查注册中心配置是否正确
- 确认网络连通性
- 验证注解是否正确添加

### 2. 调用超时

- 检查 Dubbo3 服务端是否正常启动
- 确认注册中心地址是否可达
- 核对 timeout 配置值

### 3. 接口版本冲突

- 确保服务提供者和消费者的 group、version 完全一致
- 使用相同的接口类

### 4. 序列化问题

- 确保服务接口和实体类可序列化
- 统一序列化方式（Hessian2/Protobuf）

## 技术原理

### Dubbo3 核心优势

1. **应用级注册发现**：相比接口级注册，节点数大幅减少，内存占用降低 50%+
2. **Triple 协议**：基于 HTTP/2 的 Triple 协议，网关友好，支持多语言互通
3. **云原生友好**：与 Kubernetes、Service Mesh 深度集成
4. **高性能**：基于 Netty 的异步通信，序列化性能优异

### 迁移兼容性

- Dubbo3 完全兼容 Dubbo2.x 协议
- 支持与遗留 HSF 系统混合部署
- 提供平滑迁移路径

## 输入输出说明

### 输入要求

- 支持单个 Java 文件或包含 Java 文件的目录
- 支持 pom.xml 依赖配置文件
- 支持 Spring XML 配置文件

### 输出说明

- 迁移后的文件将保存到指定的输出目录
- 保持原有目录结构不变
- 生成三类迁移报告供研发审核

## 变更记录报告（供研发审核）

迁移工具会生成三种格式的变更记录报告，便于研发团队进行代码审核：

### 1. JSON 报告 (migration_report.json)

完整的结构化数据报告，包含：
- 迁移元信息（时间、源框架、目标框架）
- 统计概要（处理文件数、变更数、变更类型分布）
- 每个文件的变更详情
- 未变更文件清单

### 2. Markdown 审核报告 (migration_report.md)

人类可读的详细审核报告，包含：

#### 变更概要
| 指标 | 数量 |
|:-----|-----:|
| 处理文件总数 | N |
| 变更文件数 | N |
| 注解转换数 | N |
| 导入语句转换数 | N |
| 依赖更新数 | N |

#### 变更明细
按文件分组的详细变更记录：
- 文件路径和类型
- 行号
- 变更类型（annotation/import/dependency）
- 变更前代码
- 变更后代码
- 变更描述

#### 审核检查项
供审核人员勾选的检查清单：
- 代码完整性检查
- 配置检查
- 测试建议

### 3. CSV 变更汇总 (change_summary.csv)

可用于数据分析的表格格式：
```
文件路径,变更类型,行号,变更前,变更后,描述
```

### 使用方式

```bash
# 执行迁移
python migrate.py --input ./hsf-project --output ./dubbo3-project

# 查看报告
cat ./dubbo3-project/migration_report.md    # 审核报告
cat ./dubbo3-project/migration_report.json   # 完整数据
cat ./dubbo3-project/change_summary.csv     # 变更汇总
```

### 报告预览示例

```markdown
## 变更概要

### 统计概览

| 指标 | 数量 |
|:-----|-----:|
| 处理文件总数 | 15 |
| 变更文件数 | 8 |
| 变更记录总数 | 23 |
| 注解转换数 | 12 |
| 导入语句转换数 | 6 |
| 依赖更新数 | 5 |

### 变更类型分布

- **annotation**: 12 处变更
- **import**: 6 处变更
- **dependency**: 5 处变更

---

## 变更明细

### 2.1 src/main/java/com/example/UserServiceImpl.java

**文件类型**: `.java`
**变更数量**: 3 处

#### 变更详情

| 行号 | 类型 | 变更前 | 变更后 |
|:----:|:-----|:-------|:-------|
| 15 | annotation | @HSFProvider(...) | @DubboService(...) |
| 22 | import | com.alibaba.boot.hsf... | org.apache.dubbo.config... |

#### 变更描述

- 服务提供者注解: @HSFProvider -> @DubboService
- 导入语句转换: com.alibaba.boot.hsf.annotation.HSFProvider -> org.apache.dubbo.config.annotation.DubboService

---

## 审核检查项

### 4.1 代码完整性检查

- [ ] 所有 HSF 注解是否已正确转换为 Dubbo3 注解
- [ ] 导入语句是否完整，无遗漏
- [ ] 依赖配置是否正确添加

### 4.2 配置检查

- [ ] 注册中心地址是否配置（推荐使用 Nacos）
- [ ] 协议端口是否正确（默认 20880）
- [ ] 服务分组和版本是否一致

### 4.3 测试建议

1. **编译测试**: 执行 `mvn clean compile` 验证代码无误
2. **单元测试**: 运行项目单元测试确保功能正常
3. **集成测试**: 启动服务验证注册发现正常
4. **调用测试**: 测试服务间调用是否正常
```
