# 微服务测试金字塔详解

基于 Martin Fowler "Testing Strategies in a Microservice Architecture"

## 测试金字塔层级

```
                    /\
                   /  \
                  / E2E \         ← 少量 (1-5%)
                 /        \
                / Component \     ← 中等 (10-20%)
               /  Integration \
              /________________\
             /                  \
            /     Unit Tests     \  ← 大量 (70-80%)
           /______________________\
```

## 各层详细说明

### Level 1: Unit Tests（单元测试）

**执行频率**：每次代码提交
**执行速度**：毫秒级
**维护成本**：低
**隔离程度**：完全隔离

#### 适用场景

| 场景 | 策略 | 示例 |
|------|------|------|
| 领域逻辑 | 使用真实对象 | 价格计算、库存扣减 |
| 管道代码 | 使用测试替身 | HTTP客户端、文件IO |
| 协调逻辑 | 验证消息传递 | 事件发布、命令分发 |

#### 代码示例（Python + pytest）

```python
# 领域逻辑测试 - 使用真实对象
class TestPriceCalculator:
    def test_apply_discount(self):
        calculator = PriceCalculator()
        result = calculator.apply_discount(100, 0.2)
        assert result == 80

# 管道代码测试 - 使用测试替身
class TestOrderService:
    def test_calls_payment_gateway(self, mock_payment_gateway):
        service = OrderService(payment_gateway=mock_payment_gateway)
        service.process_payment(100)
        mock_payment_gateway.charge.assert_called_once_with(100)

# 协调逻辑测试 - 验证消息
class TestEventPublisher:
    def test_publishes_order_created_event(self, mock_message_bus):
        publisher = EventPublisher(mock_message_bus)
        publisher.publish_order_created(Order(id=1))
        mock_message_bus.publish.assert_called_with(
            "order.created",
            {"order_id": 1}
        )
```

---

### Level 2: Integration Tests（集成测试）

**执行频率**：每次PR/每日构建
**执行速度**：秒级
**维护成本**：中
**隔离程度**：部分隔离（真实依赖）

#### 适用场景

| 组件 | 测试内容 | 风险 |
|------|----------|------|
| 数据库 | Schema映射、查询性能 | 数据隔离 |
| 缓存 | 读写一致、过期策略 | 数据污染 |
| 消息队列 | 消息格式、消费确认 | 服务依赖 |
| 外部API | 协议兼容、错误处理 | 网络不稳定 |

#### 代码示例

```python
# 数据库集成测试
class TestOrderRepository:
    @pytest.fixture
    def db_connection(self):
        conn = create_test_db()
        yield conn
        cleanup_db(conn)

    def test_save_and_retrieve_order(self, db_connection):
        repo = OrderRepository(db_connection)
        order = Order(id=1, amount=100)
        repo.save(order)

        retrieved = repo.find_by_id(1)
        assert retrieved.amount == 100
        assert retrieved.id == 1

# 外部API集成测试
class TestPaymentGatewayIntegration:
    def test_handles_timeout_gracefully(self, mock_external_api):
        mock_external_api.set_delay(30)  # 超时
        gateway = PaymentGateway(api=mock_external_api)

        with pytest.raises(PaymentTimeoutError):
            gateway.charge(100)
```

---

### Level 3: Component Tests（组件测试）

**执行频率**：每日构建/CI
**执行速度**：秒到分钟级
**维护成本**：中高
**隔离程度**：组件边界

#### 进程内 vs 进程外

```
┌─────────────────────────────────────────────────────┐
│                 Component Test                       │
├──────────────────────┬──────────────────────────────┤
│     In-Process       │       Out-of-Process          │
├──────────────────────┼──────────────────────────────┤
│  速度快 (ms-s)       │  速度慢 (s-min)               │
│  完全内存隔离        │  需要真实网络                 │
│  难以测试真实依赖    │  更接近生产环境               │
│  无需部署包特殊逻辑  │  测试夹具更复杂               │
└──────────────────────┴──────────────────────────────┘
```

#### 代码示例

```python
# 进程内组件测试
class TestOrderServiceComponent:
    """使用内存数据库和Mock测试完整服务"""

    def test_complete_order_workflow(self):
        # Setup - 内存依赖
        in_memory_db = InMemoryDatabase()
        mock_notification = MockNotificationService()
        fake_payment = FakePaymentGateway()

        # 注入依赖
        service = OrderService(
            db=in_memory_db,
            notifier=mock_notification,
            payment=fake_payment
        )

        # Execute
        order = service.create_order(items=[Item(sku="A", qty=1)])
        service.process_payment(order.id, 100)
        service.confirm_order(order.id)

        # Verify
        assert service.get_order(order.id).status == "confirmed"
        mock_notification.sent_messages[-1].should_contain("confirmed")

# 进程外组件测试
class TestOrderServiceOutOfProcess:
    """针对真实部署服务的测试"""

    def test_order_creation_via_http(self, deployed_service_url):
        response = requests.post(
            f"{deployed_service_url}/api/orders",
            json={"items": [{"sku": "A", "qty": 1}]}
        )
        assert response.status_code == 201
        assert "order_id" in response.json()
```

---

### Level 4: Contract Tests（契约测试）

**执行频率**：每次代码提交（双方）
**执行速度**：秒级
**维护成本**：中
**隔离程度**：完全解耦

#### 消费者驱动契约流程

```
┌──────────────┐         ┌──────────────┐
│   Consumer   │         │   Producer   │
│   (Order)    │         │   (Payment)   │
└──────┬───────┘         └──────┬───────┘
       │                        │
       │  1. 编写期望契约        │
       │────────────────────────>
       │                        │
       │  2. 验证Producer        │
       │<────────────────────────│
       │                        │
       │  3. 独立部署Consumer    │
       │                        │
```

#### Pact 契约测试示例

```python
# Consumer 端 - 定义期望
provider_state("an order with id 1 exists")

given("an order with id 1 exists")
    .upon_receiving("a request for order details")
    .with_request(
        method="GET",
        path="/orders/1"
    )
    .will_respond_with(
        status=200,
        headers={"Content-Type": "application/json"},
        body={
            "id": 1,
            "status": "pending",
            "total": 100.00
        }
    )

# Producer 端 - 验证实现
@pytest.fixture
def pactVerification(producer):
    return producer.verify_contract()

def test_order_endpoint_matches_contract(pactVerification):
    # Pact Broker 自动获取消费者期望
    # 验证实现是否满足所有消费者契约
    assert pactVerification.passed
```

---

### Level 5: End-to-End Tests（端到端测试）

**执行频率**：发布前/关键路径
**执行速度**：分钟级
**维护成本**：高
**隔离程度**：无（真实系统）

#### 测试策略

| 策略 | 说明 | 风险 |
|------|------|------|
| 用户画像 | 模拟真实用户角色 | 覆盖不完整 |
| 用户旅程 | 覆盖关键操作路径 | 可能过时 |
| 关键路径 | 只测核心功能 | 风险遗漏 |

#### 代码示例

```python
# Selenium E2E 测试
class TestUserCheckoutJourney:
    def test_complete_checkout_flow(self, browser, base_url):
        # Login
        browser.visit(f"{base_url}/login")
        browser.fill("username", "testuser")
        browser.fill("password", "testpass")
        browser.click_button("Login")

        # Add to cart
        browser.visit(f"{base_url}/product/1")
        browser.click_button("Add to Cart")

        # Checkout
        browser.visit(f"{base_url}/cart")
        browser.click_button("Checkout")

        # Payment
        browser.fill("card_number", "4242424242424242")
        browser.fill("expiry", "12/25")
        browser.fill("cvv", "123")
        browser.click_button("Pay")

        # Verify
        assert "Order confirmed" in browser.html
        assert browser.is_text_present("Order #")

# Headless HTTP E2E 测试
class TestOrderLifecycleE2E:
    def test_order_lifecycle_through_api(self):
        # Create order
        order_resp = requests.post(
            f"{BASE_URL}/orders",
            json={"customer_id": 1, "items": [...]}
        )
        order_id = order_resp.json()["order_id"]

        # Process payment
        payment_resp = requests.post(
            f"{BASE_URL}/orders/{order_id}/pay",
            json={"method": "credit_card", "amount": 100}
        )
        assert payment_resp.status_code == 200

        # Verify fulfillment
        fulfillment_resp = requests.get(
            f"{BASE_URL}/orders/{order_id}"
        )
        assert fulfillment_resp.json()["status"] == "paid"
```

---

## 测试数据管理策略

```
┌─────────────────────────────────────────────────────────┐
│                    Testing Data Pyramid                   │
├─────────────────────────────────────────────────────────┤
│  E2E Tests    │  使用干净的种子数据，每次测试后清理     │
├───────────────┼─────────────────────────────────────────┤
│  Contract     │  Mock数据，隔离消费者/生产者            │
├───────────────┼─────────────────────────────────────────┤
│  Component    │  内存数据库，固定测试数据集             │
├───────────────┼─────────────────────────────────────────┤
│  Integration  │  专用测试数据库，支持事务回滚           │
├───────────────┼─────────────────────────────────────────┤
│  Unit         │  无需外部数据，工厂方法生成             │
└───────────────┴─────────────────────────────────────────┘
```

---

## 测试工具推荐

| 层级 | Java/Kotlin | Python | Go |
|------|-------------|--------|-----|
| Unit | JUnit, Spock | pytest, unittest | testing package |
| Integration | Testcontainers | pytest-django, testcontainers | testcontainers-go |
| Component | Arquillian, Hoverfly | pytest, vcrpy | go-testcontainers |
| Contract | Pact-JVM | Pact-Python | Pact-Go |
| E2E | Selenium, Cypress | Playwright, Selenium | Playwright-Go |

---

## 执行时间预算

建议测试套件执行时间分配：

```
Unit Tests:        70% → 1-2 分钟
Integration Tests: 15% → 5-10 分钟
Component Tests:   10% → 10-15 分钟
Contract Tests:    3%  → 2-3 分钟
E2E Tests:         2%  → 15-30 分钟
```

---

## 参考链接

- 原文：[Testing Strategies in a Microservice Architecture](https://martinfowler.com/articles/microservice-testing/)
- Pact 契约测试：[pact.io](https://pact.io)
- Testcontainers：[testcontainers.com](https://testcontainers.com)
