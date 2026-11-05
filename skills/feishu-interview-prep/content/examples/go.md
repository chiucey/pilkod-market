---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: b711a1138ea904e7a0a149246359b9b2
    PropagateID: b711a1138ea904e7a0a149246359b9b2
    ReservedCode1: 3045022100b752ad4f8e4c7ac58768afa484efd0c14c5de2edf4ae3e8489cefc423c48c083022068e7f42fbc5936776407de4cb9b8e7e0073faabd69ed93dc26301b06d7782e6e
    ReservedCode2: 30450221008f58fa6bb2641b050112c5b912d33a8623269655734d342a46af57198980906302202cc3e8b73d3d127cfb4c86ece6d00ba883b93a8b64f26bfd6a1495c667fd0dd3
---

# Go 工程师面试准备示例

## Go 第一面：基础知识与技术深度

### 面试题示例（30题）

| 题号 | 模块 | 题目 | 考察点 |
|------|------|------|--------|
| 001 | 基础语法 | Go 的数据类型有哪些？值类型和引用类型的区别？ | 类型系统 |
| 002 | 基础语法 | make 和 new 的区别？ | 内存分配 |
| 003 | 基础语法 | Go 有没有泛型？Go 1.18 泛型有哪些特性？ | 泛型 |
| 004 | 切片 | 切片底层实现？扩容机制？append 的坑？ | 切片原理 |
| 005 | 切片 | nil 切片和空切片的区别？ | 空值 |
| 006 | Map | Map 底层实现？并发安全吗？ | 散列表 |
| 007 | Map | sync.Map 的原理？什么场景下使用？ | 并发map |
| 008 | Goroutine | 什么是 Goroutine？和线程的区别？ | 并发模型 |
| 009 | Goroutine | GMP 调度模型？P 的数量默认是多少？ | 调度器 |
| 010 | Channel | Channel 有哪些类型？无缓冲和缓冲的区别？ | CSP |
| 011 | Channel | 关闭 Channel 的原则？已关闭的 Channel 读取？ | 通道关闭 |
| 012 | Channel | select 的用法？多个 case 同时就绪？ | 多路复用 |
| 013 | Context | Context 的用途？取消信号如何传递？ | 上下文 |
| 014 | 并发安全 | 什么是竞态条件？如何检测？ | 竞态 |
| 015 | 并发安全 | sync.Mutex、sync.RWMutex 的区别？ | 互斥锁 |
| 016 | 并发安全 | sync.Once 实现单例？ | 原子操作 |
| 017 | 并发安全 | atomic 包的用法？CAS 原理？ | 原子操作 |
| 018 | 内存管理 | Go 的内存分配器？TCMalloc 了解吗？ | 内存分配 |
| 019 | 内存管理 | 什么是逃逸分析？如何避免逃逸？ | 逃逸分析 |
| 020 | GC | Go 使用的是什么垃圾回收算法？三色标记？ | GC |
| 021 | GC | GC 触发条件？STW 时间？如何优化？ | GC调优 |
| 022 | 错误处理 | error 类型如何定义？error wrapping？ | 错误处理 |
| 023 | 错误处理 | panic 和 recover 的用法？哪些场景使用？ | 异常处理 |
| 024 | 接口 | 接口的内部结构？空接口的用途？ | 接口 |
| 025 | 接口 | 类型断言和 type switch？ | 类型断言 |
| 026 | 反射 | reflect 包的使用？反射的优缺点？ | 反射 |
| 027 | 依赖管理 | Go Module 机制？go.mod 文件解析？ | 依赖管理 |
| 028 | HTTP | net/http 包的使用？Server 和 Client？ | 网络编程 |
| 029 | 测试 | 单元测试如何写？table-driven 测试？ | 测试 |
| 030 | 性能 | pprof 如何使用？CPU 和内存 profile？ | 性能分析 |

---

## Go 第二面：系统设计与架构

### 设计题示例

**题目：设计一个配置中心**

考察维度：
1. 配置存储和分发（etcd、Redis）
2. 配置变更推送（长轮询、WebSocket）
3. 配置版本管理
4. 灰度发布和回滚
5. 高可用和容灾

---

## Go 强化训练示例

### 强化训练 001：Goroutine 调度

**目标**：从 ⚠️ 模糊 → 💪 熟练

**训练题**：
1. GMP 模型中 G、M、P 分别是什么？
2. 调度循环的流程？schedtick 的作用？
3. 什么情况会触发 Goroutine 切换？
4. work-stealing 机制？
5. 死锁如何排查？runtime.GOMAXPROCS 的影响？

---

## Go 晋级评估标准

| 模块 | 精通要求 | 熟练要求 |
|------|---------|---------|
| 语法基础 | 深入理解类型系统 | 熟练使用、避开陷阱 |
| 并发模型 | CSP 设计模式 | Goroutine、Channel |
| 运行时 | GC调优、内存管理 | 逃逸分析、分配器 |
| 标准库 | 底层原理 | 常用包熟练使用 |
| 工程能力 | 性能调优 | 测试、profiling |
