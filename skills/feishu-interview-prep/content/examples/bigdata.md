---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
    PropagateID: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
    ReservedCode1: 30450220712f58e532066532ba823ecca175bc20b7cfa2d968189fdb98dc8f2bd2bc9b55022100f2e0b88490d8ae18e6dbff9288ceb424ca61b13cf84eae56d12941a3d19a4982
    ReservedCode2: 304502201a341a1899871c909b4c6738f70e7cc0ef890b57414e85e8bf2c740d668b2f40022100950d259dc783092e6b1029cde19d9e8a35feb205349a16b8c3338b27878549fb
---

# 大数据开发工程师面试准备示例

## 大数据第一面：基础知识与工具使用

### 面试题示例（30题）

| 题号 | 模块 | 题目 | 考察点 |
|------|------|------|--------|
| 001 | Hadoop | HDFS 的架构？NameNode 和 DataNode 的职责？ | 分布式存储 |
| 002 | Hadoop | HDFS 的读写流程？ | 数据流 |
| 003 | Hadoop | 什么是 Block？默认块大小？为什么这么大？ | 存储机制 |
| 004 | Hadoop | HDFS 的容错机制？副本放置策略？ | 高可用 |
| 005 | Hadoop | SecondNameNode 的作用？Checkpoint 机制？ | 元数据 |
| 006 | Hadoop | MapReduce 的工作流程？Map-Shuffle-Reduce？ | 计算框架 |
| 007 | Hadoop | Combiner 和 Partitioner 的作用？ | 优化 |
| 008 | Hadoop | Shuffle 过程？为什么需要排序？ | 数据处理 |
| 009 | Hadoop | MapReduce 的优化手段？ | 性能优化 |
| 010 | Hadoop | Yarn 的架构？ResourceManager 和 NodeManager？ | 资源管理 |
| 011 | Hive | Hive 的架构？和 HDFS 的关系？ | 数据仓库 |
| 012 | Hive | HiveQL 和 SQL 的区别？ | 查询 |
| 013 | Hive | Hive 的文件存储格式？TextFile、ORC、Parquet？ | 存储格式 |
| 014 | Hive | Hive 的压缩格式？Snappy、LZO、GZIP？ | 压缩 |
| 015 | Hive | Hive 优化手段？数据倾斜如何处理？ | 优化 |
| 016 | Spark | Spark 的架构？Driver 和 Executor？ | 计算框架 |
| 017 | Spark | Spark 和 MapReduce 的区别？为什么 Spark 快？ | 性能 |
| 018 | Spark | RDD 的特性？宽依赖和窄依赖？ | 数据抽象 |
| 019 | Spark | DataFrame 和 DataSet 的区别？ | API |
| 020 | Spark | Spark 的 Shuffle 机制？Hash Shuffle 和 Sort Shuffle？ | Shuffle |
| 021 | Spark | Spark 内存管理？堆内和堆外内存？ | 内存 |
| 022 | Spark | Spark 的广播变量和累加器？ | 共享变量 |
| 023 | Spark | Spark 的 checkpoint 和 cache 的区别？ | 容错 |
| 024 | Kafka | Kafka 的架构？Producer、Broker、Consumer？ | 消息队列 |
| 025 | Kafka | Kafka 的分区和副本机制？ | 分布式 |
| 026 | Kafka | Kafka 如何保证消息不丢失？ | 可靠性 |
| 027 | Kafka | Kafka 的顺序消息？如何保证？ | 顺序性 |
| 028 | Flink | Flink 的架构？JobManager 和 TaskManager？ | 流处理 |
| 029 | Flink | Flink 的 Checkpoint 和 Savepoint？ | 容错 |
| 030 | Flink | Flink 的时间语义？Event Time 和 Processing Time？ | 时间处理 |

---

## 大数据第二面：架构设计与实战

### 设计题示例

**题目：设计一个实时数据仓库**

考察维度：
1. 离线与实时架构融合（Lambda、Kappa）
2. 实时数据采集（Kafka、Flink）
3. 实时 OLAP 引擎（ClickHouse、Doris）
4. 数据一致性保障
5. 故障恢复与监控

---

## 大数据强化训练示例

### 强化训练 001：Spark 数据倾斜

**目标**：从 ⚠️ 模糊 → 💪 熟练

**训练题**：
1. 什么是数据倾斜？数据倾斜有哪些表现？
2. 如何定位数据倾斜的 Key？
3. Map 端数据倾斜的解决方案？
4. Reduce 端数据倾斜的解决方案？
5. Spark SQL 数据倾斜的解决方案？

---

## 大数据晋级评估标准

| 模块 | 精通要求 | 熟练要求 |
|------|---------|---------|
| Hadoop | 内核原理、调优 | HDFS/MapReduce |
| Hive | 原理、高级特性 | SQL优化 |
| Spark | 源码、内存管理 | RDD/DataFrame |
| 实时计算 | Flink watermark | Kafka/Flink |
| 架构设计 | 平台架构 | 数据建模 |
