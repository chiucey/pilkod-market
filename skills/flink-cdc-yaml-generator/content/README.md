# Flink CDC YAML Generator Skill

Flink CDC Pipeline YAML 配置生成与验证专家技能。

## 功能特性

- **自动生成 YAML 配置**：根据用户需求自动生成完整、可执行的 Flink CDC Pipeline YAML 配置文件
- **配置验证**：检查现有 YAML 配置的正确性，识别问题并提供修复建议
- **连接器参数查询**：提供 Source/Sink 连接器的详细参数说明
- **Transform 规则支持**：内置数据转换、列投影、行过滤、UDF、AI 模型等功能
- **Route 路由策略**：支持分库分表合并、表名映射、正则替换等高级路由功能

## 支持的连接器

### Source Connectors
- **MySQL** (5.7, 8.0.x, 8.4+ | RDS MySQL | PolarDB MySQL | Aurora MySQL | MariaDB)
- **PostgreSQL** (9.6+)
- **Oracle** (11g, 12c, 19c)

### Sink Connectors
- **Doris** (1.2.x, 2.x.x, 3.x.x)
- **StarRocks** (2.x, 3.x)
- **Paimon** (0.6 - 1.3)
- **Kafka** (所有常用版本)
- **Elasticsearch** (6.x, 7.x, 8.x)
- **Iceberg** (1.6 - 1.10)
- **Hudi** (最新版本)
- **OceanBase** (3.x, 4.x)
- **MaxCompute** (阿里云)
- **Fluss** (0.7, 0.8, 0.9)

## 使用场景

### 1. 生成新的同步任务配置

```
用户：帮我创建一个 MySQL 到 Doris 的 CDC 同步任务
```

技能会：
1. 读取 MySQL source 和 Doris sink 的连接器文档
2. 询问必要的连接信息（host、port、database、username、password 等）
3. 生成完整的 YAML 配置文件

### 2. 验证现有配置

```
用户：检查一下这个 YAML 配置是否有问题：[用户提供 YAML]
```

技能会：
1. 识别 source 和 sink 类型
2. 读取对应的连接器文档
3. 验证必填字段、格式、参数值等
4. 报告问题并提供修复建议

### 3. 查询连接器参数

```
用户：MySQL CDC source 需要哪些必填参数？
```

技能会返回该连接器的所有必填参数和可选参数说明。

### 4. Transform 转换规则

```
用户：如何在同步过程中添加计算列和过滤条件？
```

技能会提供 transform 配置示例，包括：
- 列投影（projection）
- 行过滤（filter）
- 主键重定义（primary-keys）
- 分区键设置（partition-keys）
- UDF 和 AI 模型调用

### 5. Route 路由策略

```
用户：如何把多个分库分表合并到一个目标表？
```

技能会提供 route 配置示例，包括：
- 一对一路由
- 多对一合并
- 正则捕获组替换
- replace-symbol 占位符

## 版本兼容性

| Flink CDC | Flink Version | Pipeline Source | Pipeline Sink |
|-----------|---------------|-----------------|---------------|
| **3.6.x** | 1.20.*, 2.2.* | MySQL, PostgreSQL, Oracle | StarRocks, Doris, Paimon, Kafka, Elasticsearch, OceanBase, MaxCompute, Iceberg, Fluss, Hudi |
| **3.5.x** | 1.19.*, 1.20.* | MySQL, PostgreSQL | StarRocks, Doris, Paimon, Kafka, Elasticsearch, OceanBase, MaxCompute, Iceberg, Fluss |
| **3.4.x** | 1.19.*, 1.20.* | MySQL | StarRocks, Doris, Paimon, Kafka, Elasticsearch, OceanBase, MaxCompute, Iceberg |
| **3.3.x** | 1.19.*, 1.20.* | MySQL | StarRocks, Doris, Paimon, Kafka, Elasticsearch, OceanBase, MaxCompute |
| **3.2.x** | 1.17.*, 1.18.*, 1.19.* | MySQL | StarRocks, Doris, Paimon, Kafka, Elasticsearch |
| **3.1.x** | 1.17.*, 1.18.*, 1.19.* | MySQL | StarRocks, Doris, Paimon, Kafka |
| **3.0.x** | 1.17.*, 1.18.* | MySQL | StarRocks, Doris |

**注意**：如果用户指定了 Flink CDC 版本，技能会根据此表判断连接器可用性并给出警告或建议。

## 安装方法

将本 skill包目录复制到钉钉 AI Agent 的技能目录，或通过技能管理界面导入。

```bash
# 假设钉钉技能目录为 ~/.dingtalk/skills/
cp -r flink-cdc-yaml-generator ~/.dingtalk/skills/
```

## 文件结构

```
flink-cdc-yaml-generator/
├── SKILL.md                    # 技能主文档（包含路由逻辑、工作流程、规则）
├── manifest.json               # 技能元数据
├── README.md                   # 使用说明（本文件）
├── connectors/
│   ├── source/
│   │   ├── mysql.md           # MySQL source 参数文档
│   │   ├── oracle.md          # Oracle source 参数文档
│   │   └── postgres.md        # PostgreSQL source 参数文档
│   └── sink/
│       ├── doris.md           # Doris sink 参数文档
│       ├── starrocks.md       # StarRocks sink 参数文档
│       ├── paimon.md          # Paimon sink 参数文档
│       ├── kafka.md           # Kafka sink 参数文档
│       ├── elasticsearch.md   # Elasticsearch sink 参数文档
│       ├── iceberg.md         # Iceberg sink 参数文档
│       ├── hudi.md            # Hudi sink 参数文档
│       ├── oceanbase.md       # OceanBase sink 参数文档
│       ├── maxcompute.md      # MaxCompute sink 参数文档
│       └── fluss.md           # Fluss sink 参数文档
└── modules/
    ├── transform.md            # Transform 模块文档（函数、UDF、AI 模型）
    └── route.md                # Route 模块文档（路由规则、替换符号）
```

## 示例 YAML

### MySQL → Doris 基础同步

```yaml
source:
  type: mysql
  hostname: 127.0.0.1
  port: 3306
  username: flinkuser
  password: "flinkpw"
  tables: mydb.orders, mydb.products
  server-id: 5400-5404
  server-time-zone: Asia/Shanghai

sink:
  type: doris
  fenodes: 127.0.0.1:8030
  username: root
  password: ""
  sink.label-prefix: mysql_doris_cdc
  sink.enable-delete: true
  sink.properties.format: json
  sink.properties.read_json_by_line: true

pipeline:
  name: MySQL to Doris CDC Pipeline
  parallelism: 4
  local-time-zone: Asia/Shanghai
```

### MySQL → StarRocks 带 Transform 和 Route

```yaml
source:
  type: mysql
  hostname: 127.0.0.1
  port: 3306
  username: flinkuser
  password: "flinkpw"
  tables: mydb.order_2023, mydb.order_2024
  server-id: 5400-5404

transform:
  - source-table: mydb\\.order_.*
    projection: id, order_id, UPPER(status) AS status, NOW() AS updated_at
    filter: amount > 0
    primary-keys: id

route:
  - source-table: mydb\\.order_2023
    sink-table: dw.orders_history
    description: "archive 2023 orders"
  - source-table: mydb\\.order_2024
    sink-table: dw.orders_current
    description: "sync 2024 orders"

sink:
  type: starrocks
  jdbc-url: jdbc:mysql://starrocks-fe:9030
  load-url: starrocks-fe:8030
  username: root
  password: ""
  sink.label-prefix: mysql_sr_cdc

pipeline:
  name: MySQL to StarRocks with Transform and Route
  parallelism: 2
```

## 常见问题

### Q: 如何启用增量快照？
A: 在 source 中添加 `scan.incremental.snapshot.enabled: true`（默认已启用）。

### Q: 如何处理没有主键的表？
A: 在 transform 中使用 `primary-keys` 指定替代键，或在 source 中设置 `scan.incremental.snapshot.chunk.key-column`。

### Q: 如何实现软删除（Soft Delete）？
A: 使用 transform 的 `converter-after-transform: SOFT_DELETE` 配合 `__data_event_type__` 元数据字段。

### Q: 如何自定义 UDF？
A: 在 pipeline.user-defined-function 中注册 UDF 类，JAR 文件需放入 Flink `/lib` 目录或通过 `--jar` 参数传递。

### Q: 如何使用 AI 模型进行 Embedding 或 Chat？
A: 在 pipeline.model 中注册模型配置，然后在 transform projection 中调用模型函数。需要下载内置模型 JAR 并通过 `--jar` 参数传递。

## 贡献者

- Original concept: `.claude/skills/flink-cdc-yaml`
- Standard Skill package: Thorne

## 许可证

MIT License
