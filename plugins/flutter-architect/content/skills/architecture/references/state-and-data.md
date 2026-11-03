# 状态与数据层

## 一、先分类，再选型

问四个问题：这个状态被谁用？来自服务器吗？需要持久化吗？异步有多复杂？

| 方案 | 适用 | 风险 |
|---|---|---|
| setState | 单 Widget 内 UI 状态 | 逻辑稍复杂就难维护 |
| ValueNotifier / ChangeNotifier | 轻量局部、可组合 | 需要手动管理监听生命周期 |
| Provider | 中小项目、依赖+状态 | 复杂派生状态不够用 |
| Riverpod | 需要编译期安全、异步状态、可测试 | 2.x→3.x 迁移成本（部分 API 移入 legacy）、学习曲线 |
| Bloc / Cubit | 事件驱动、状态机、强规范团队 | 样板代码多 |
| GetX | 存量项目 | 全局耦合、可测试性弱，新项目不推荐 |
| Redux / MobX | 已有历史项目 | 生态老化，新项目不默认引入 |

选型必须写明团队熟悉度、测试需求、规范强度，不能只按流行度。

## 二、决策顺序

1. 只在一个 Widget 用 → 局部。
2. 只在一个页面用 → 页面级控制器。
3. 跨页面共享 → 模块级，尽量不全局。
4. 来自服务器 → 先做 Repository + 缓存 + 查询状态，不要直接塞进全局 UI 状态。
5. 需要持久化 → LocalDataSource / SecureStorage。
6. 影响多个模块 → 定义事件来源与订阅关系。
7. 复杂异步（重试、并发、取消、分页）→ 状态机或 AsyncNotifier。
8. 需要严格测试 → 抽 UseCase / Controller 并注入依赖。

## 三、单向数据流

```text
User Event → Controller/Bloc → UseCase → Repository → DataSource → State → UI
```

要避免：UI 直接改全局状态；Widget 内写业务逻辑；多处随意改同一份状态；状态来源不可追踪；副作用分散。

## 四、异步与并发

- 单线程 + event loop：microtask 先于 event queue。
- 阻塞主线程的典型来源：大 JSON 解析、大文件 IO、图片解码、加密、同步 DB 查询。
- 超过当前帧预算一半的计算（60Hz≈8ms / 120Hz≈4ms）必须移出主 isolate：`Isolate.run`、`compute`、独立 isolate + SendPort。
- isolate 之间只传可发送对象（消息复制），不要传含上下文的闭包。
- 取消与超时：Future 不可取消，用 Completer + 令牌或 StreamSubscription 控制生命周期。
- Stream 必须显式释放；页面退出后仍存活的订阅是内存泄漏主因。

## 五、网络层

统一结构：

```text
ApiClient（配置、超时、baseUrl）
Interceptor 链（鉴权、重试、日志、埋点、错误映射）
Authenticator（Token 刷新、并发去重）
ExceptionMapper（HTTP/业务错误码 → 领域异常）
CachePolicy（TTL、ETag、单飞）
Retrier（幂等请求才重试）
```

必须回答：
- 业务错误与系统错误如何区分？（错误码分层：网络 / 协议 / 业务 / 未知）
- Token 过期如何无感刷新？（刷新串行化，等待队列，失败统一登出）
- 重复请求如何取消与去重？（同 key 单飞）
- 哪些请求可重试？（仅幂等 + 网络类错误）
- 超时如何设置？（连接与响应分别设置，不能全局一个值）
- 如何做请求级埋点？（成功率、耗时分位、错误码分布）

安全项：HTTPS、证书固定（评估成本）、签名与防重放（需要时）、日志脱敏（禁止打印 token、手机号、身份证）。

## 六、缓存与离线

- 缓存策略要写清：TTL、容量、淘汰、失效触发（登录切换、版本升级、主动刷新）。
- 列表分页缓存要区分「首屏」「已加载页」「预取」。
- 离线优先需要定义冲突解决：以服务端为准 / 以本地为准 / 合并 + 人工提示。
- 数据迁移：数据库版本升级必须写迁移脚本，禁止直接 drop 重建（会丢用户数据）。
- 敏感数据（token、证件、生物特征）只能进 secure storage / keychain / keystore，不进普通偏好存储与日志。

## 七、本地存储选型

| 需求 | 选择 |
|---|---|
| 简单键值、非敏感 | shared_preferences |
| 敏感小数据 | secure_storage |
| 关系数据、复杂查询、迁移 | sqflite 或 drift（drift 类型安全、迁移完善） |
| 高并发读写、对象存储 | drift 或 objectbox 为主选；isar 3.x、hive 2.x 均已长期停更，仅作存量迁移说明（hive 的社区维护版为 hive_ce） |
| 大文件 | 文件系统 + path_provider |

设计要点：Repository 内组合 Remote 与 Local 数据源；缓存读写要可开关；提供清理入口（退出登录、存储超限、版本升级）。

## 八、可测试性

不可测试通常是设计问题。检查：
- 能否不启动真实网络就测业务逻辑？
- 能否替换数据库实现？
- 能否模拟时间、随机数、设备能力？
- 状态变化能否断言（状态是值对象而非可变字段集合）？
