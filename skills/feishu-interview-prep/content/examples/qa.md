---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 9e35311d499431f50c610cf9e42c7610
    PropagateID: 9e35311d499431f50c610cf9e42c7610
    ReservedCode1: 30450220712f58e532066532ba823ecca175bc20b7cfa2d968189fdb98dc8f2bd2bc9b55022100f2e0b88490d8ae18e6dbff9288ceb424ca61b13cf84eae56d12941a3d19a4982
    ReservedCode2: 304502201a341a1899871c909b4c6738f70e7cc0ef890b57414e85e8bf2c740d668b2f40022100950d259dc783092e6b1029cde19d9e8a35feb205349a16b8c3338b27878549fb
---

# 测试开发工程师面试准备示例

## 测试开发第一面：测试基础与自动化

### 面试题示例（30题）

| 题号 | 模块 | 题目 | 考察点 |
|------|------|------|--------|
| 001 | 测试基础 | 测试金字塔？单元测试、集成测试、E2E？ | 测试分层 |
| 002 | 测试基础 | 黑盒测试和白盒测试的区别？ | 测试方法 |
| 003 | 测试基础 | 等价类划分、边界值分析、判定表？ | 测试用例设计 |
| 004 | 测试基础 | 什么是测试左移和测试右移？ | 测试策略 |
| 005 | 测试基础 | 测试用例编写原则？ | 测试用例 |
| 006 | Java测试 | JUnit 5 注解？@BeforeEach、@Disabled？ | 单元测试 |
| 007 | Java测试 | Mockito 使用？stub 和 mock 的区别？ |  mocking |
| 008 | Java测试 | JUnit 5 断言？assertThrows、assertAll？ | 断言 |
| 009 | Java测试 | @Nested 嵌套测试？@ParameterizedTests？ | 高级特性 |
| 010 | Java测试 | Spring Boot 测试？@SpringBootTest、@MockBean？ | 集成测试 |
| 011 | Python测试 | pytest  fixtures？scope 和 autouse？ | pytest |
| 012 | Python测试 | pytest parametrize？markers？ | 参数化 |
| 013 | Python测试 | unittest vs pytest？ | 测试框架 |
| 014 | Python测试 | pytest 插件？pytest-cov、pytest-html？ | 生态 |
| 015 | 前端测试 | Jest 用法？describe、it、expect？ | 前端测试 |
| 016 | 前端测试 | Vue Test Utils / React Testing Library？ | 组件测试 |
| 017 | 前端测试 | Enzyme vs Testing Library？ | 测试库 |
| 018 | 前端测试 | Jest 模拟（Mock）？jest.fn()、jest.spyOn()？ | Mock |
| 019 | 前端测试 | 快照测试（Snapshot Testing）？ | 快照 |
| 020 | E2E测试 | Selenium 架构？WebDriver 协议？ | E2E |
| 021 | E2E测试 | Playwright vs Cypress？ | E2E框架 |
| 022 | E2E测试 | 页面对象模式（Page Object）？ | 设计模式 |
| 023 | 接口测试 | Postman / Apifox 使用？ | 接口测试 |
| 024 | 接口测试 | HTTP 状态码？RESTful API 设计？ | API |
| 025 | 接口测试 | 接口测试用例设计？ | 用例设计 |
| 026 | 性能测试 | JMeter / Locust 使用？ | 性能测试 |
| 027 | 性能测试 | 性能指标？TPS、RT、并发数？ | 性能指标 |
| 028 | 性能测试 | JMeter 关联和参数化？ | 高级特性 |
| 029 | 安全测试 | SQL 注入、XSS、CSRF 原理？ | 安全 |
| 030 | 安全测试 | 安全测试工具？Burp Suite？ | 安全工具 |

---

## 测试开发第二面：测试平台与质量保障

### 设计题示例

**题目：设计一个企业级测试平台**

考察维度：
1. 测试用例管理（版本管理、评审流程）
2. 自动化测试平台（任务调度、执行集群）
3. 测试报告与度量平台
4. 缺陷管理与流程集成
5. CI/CD 测试集成（门禁）

---

## 测试开发强化训练示例

### 强化训练 001：测试策略与实践

**目标**：从 ⚠️ 模糊 → 💪 熟练

**训练题**：
1. 如何为遗留代码编写单元测试？
2. 测试覆盖率越高越好吗？如何权衡？
3. 如何处理不稳定的测试（Flaky Tests）？
4. TDD 和 BDD 的区别？各自适用场景？
5. 如何评估自动化测试的 ROI？

---

## 测试开发晋级评估标准

| 模块 | 精通要求 | 熟练要求 |
|------|---------|---------|
| 测试理论 | 测试策略、用例设计 | 测试方法 |
| 单元测试 | 测试隔离、Mocks | JUnit/Pytest |
| 自动化测试 | 框架设计、平台建设 | Selenium/Playwright |
| 性能测试 | 场景设计、瓶颈分析 | JMeter/Locust |
| 质量保障 | 质量度量和改进 | DevOps/CI集成 |
