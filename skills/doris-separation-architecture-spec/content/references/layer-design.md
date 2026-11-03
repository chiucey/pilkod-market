# 数据仓库分层设计规范

## 1. 数据类型映射表

### 1.1 常见数据库类型映射

| 源数据库 | MySQL | PostgreSQL | Oracle | SQL Server |
|----------|-------|------------|--------|------------|
| **INT** | INT / BIGINT | INTEGER | NUMBER(10) | INT |
| **BIGINT** | BIGINT | BIGINT | NUMBER(19) | BIGINT |
| **DECIMAL** | DECIMAL(p,s) | DECIMAL(p,s) | NUMBER(p,s) | DECIMAL(p,s) |
| **VARCHAR** | VARCHAR(n) | VARCHAR(n) | VARCHAR2(n) | VARCHAR(n) |
| **TEXT** | TEXT / VARCHAR(65535) | TEXT | CLOB | TEXT |
| **DATE** | DATE | DATE | DATE | DATE |
| **DATETIME** | DATETIME | TIMESTAMP | TIMESTAMP | DATETIME2 |
| **TIMESTAMP** | TIMESTAMP | TIMESTAMP | TIMESTAMP | TIMESTAMP |
| **BOOLEAN** | TINYINT(1) | BOOLEAN | NUMBER(1) | BIT |

### 1.2 Doris类型选择建议

| 数据特点 | 推荐类型 | 说明 |
|----------|----------|------|
| 固定长度字符串 | CHAR | 固定长度，性能更优 |
| 可变长度字符串（< 1KB） | VARCHAR | 节省空间 |
| 大文本（> 1KB） | TEXT | 日志、JSON等 |
| 精确金额 | DECIMAL(20,4) | 避免浮点精度问题 |
| 主键/外键 | BIGINT | 比VARCHAR更高效 |
| 日期 | DATE | 日期类型 |
| 时间戳 | DATETIME | 精确到秒 |
| 状态枚举 | TINYINT | 比VARCHAR更节省空间 |

## 2. ODS层设计规范

### 2.1 设计原则
1. **保持原始**: 字段与源表一一映射，不做清洗转换
2. **审计字段**: 必须添加审计字段追溯数据来源
3. **分区策略**: 按数据日期分区，便于增量同步
4. **保留时长**: 根据业务需求设置数据保留策略

### 2.2 必须字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| etl_time | DATETIME | ETL处理时间 |
| source_system | VARCHAR(32) | 源系统标识 |
| source_table | VARCHAR(64) | 源表名 |
| source_pk | VARCHAR(64) | 源表主键值 |

### 2.3 ODS层建表模板

```sql
CREATE TABLE `ods_{源系统}_{源表名}` (
    -- 原始字段（与源表一一映射）
    `{源字段1}` {源类型},
    `{源字段2}` {源类型},

    -- 审计字段
    `etl_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `source_system` VARCHAR(32) NOT NULL,
    `source_table` VARCHAR(64) NOT NULL,
    `source_pk` VARCHAR(64),

    -- 分区字段（生成列）
    `data_date` DATE AS (DATE({时间字段})) STORED
)
UNIQUE KEY(`source_pk`)
PARTITION BY RANGE(`data_date`) ()
DISTRIBUTED BY HASH(`source_pk`) BUCKETS {分桶数}
PROPERTIES (
    "replication_num" = "1",
    "compression" = "{LZ4/ZSTD}",
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "DAY",
    "dynamic_partition.start" = "-{保留天数}",
    "dynamic_partition.end" = "1"
);
```

## 3. DWD层设计规范

### 3.1 设计原则
1. **数据清洗**: 去重、空值处理、异常值处理
2. **格式统一**: 字段类型统一、编码统一、命名统一
3. **维度退化**: 将常用维度退化到事实表
4. **审计追溯**: 保留数据处理过程的审计信息

### 3.2 常用清洗规则

| 清洗类型 | 规则描述 | 实现方式 |
|----------|----------|----------|
| 去重 | 按主键去重，保留最新 | GROUP BY + MAX |
| 空值处理 | 数值型用0或均值填充 | COALESCE() |
| 格式转换 | 日期格式统一、编码统一 | DATE_FORMAT |
| 状态映射 | 数字状态转文字描述 | CASE WHEN |

### 3.3 DWD层建表模板

```sql
CREATE TABLE `dwd_{业务域}_{事实表名}` (
    -- 业务字段（清洗后）
    `{清洗后字段1}` {类型},
    `{清洗后字段2}` {类型},

    -- 审计字段
    `dw_start_date` DATE NOT NULL,
    `dw_end_date` DATE NOT NULL DEFAULT '9999-12-31',
    `is_current` TINYINT NOT NULL DEFAULT 1,

    -- 分区字段
    `{分区字段}` {类型}
)
DUPLICATE KEY(`{主键}`)
PARTITION BY RANGE(`{分区字段}`) ()
DISTRIBUTED BY HASH(`{分桶字段}`) BUCKETS {分桶数}
PROPERTIES (
    "replication_num" = "1",
    "compression" = "{LZ4/ZSTD}"
);

INDEX idx_{索引名} ({列}) USING {BITMAP/BLOOMFILTER};
```

## 4. DWS层设计规范

### 4.1 设计原则
1. **按主题汇总**: 订单主题、用户主题、商品主题等
2. **时间粒度**: 支持日、周、月等多时间粒度
3. **去重计数**: 使用BITMAP或COUNT(DISTINCT)
4. **预计算**: 将常用聚合结果预计算存储

### 4.2 DWS层建表模板

```sql
CREATE TABLE `dws_{业务域}_{主题}_{时间粒度}` (
    -- 统计维度
    `{维度1}` {类型},
    `{维度2}` {类型},

    -- 时间维度
    `stat_date` DATE NOT NULL,

    -- 汇总指标
    `cnt` BIGINT DEFAULT 0,
    `sum_amount` DECIMAL(20,2) DEFAULT 0,
    `uv` BITMAP_UNION,

    -- 审计字段
    `etl_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
)
AGGREGATE KEY(`{维度1}`, `{维度2}`, `stat_date`)
PARTITION BY RANGE(`stat_date`) ()
DISTRIBUTED BY HASH(`{分桶字段}`) BUCKETS {分桶数}
PROPERTIES (
    "replication_num" = "1",
    "compression" = "LZ4"
);
```

## 5. ADS层设计规范

### 5.1 设计原则
1. **查询优先**: 优化查询性能，减少Join
2. **指标预计算**: 将复杂计算结果预计算存储
3. **灵活字段**: 支持动态列扩展
4. **低延迟**: 优先使用DUPLICATE KEY模型

### 5.2 ADS层建表模板

```sql
CREATE TABLE `ads_{应用主题}_{用途}` (
    -- 维度字段
    `{维度1}` {类型},
    `{维度2}` {类型},

    -- 指标字段
    `{指标1}` {类型},
    `{指标2}` {类型},

    -- 时间字段
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
)
DUPLICATE KEY(`{唯一标识}`)
DISTRIBUTED BY HASH(`{分桶字段}`) BUCKETS {分桶数}
PROPERTIES (
    "replication_num" = "1",
    "compression" = "LZ4"
);
```

## 6. DIM层设计规范

### 6.1 设计原则
1. **缓慢变化维**: 支持历史数据追踪（SCD Type 1/2）
2. **维度退化**: 将小维度退化到事实表
3. **一致性**: 统一维度口径
4. **低基数**: 维度表通常数据量较小

### 6.2 拉链表模板

```sql
CREATE TABLE `dim_{维度名}` (
    `{维度主键}` {类型} NOT NULL,

    -- 维度属性
    `{属性1}` {类型},
    `{属性2}` {类型},

    -- 拉链字段
    `start_date` DATE NOT NULL,
    `end_date` DATE NOT NULL DEFAULT '9999-12-31',
    `is_current` TINYINT NOT NULL DEFAULT 1,

    -- 审计字段
    `etl_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
)
UNIQUE KEY(`{维度主键}`, `start_date`)
DISTRIBUTED BY HASH(`{维度主键}`) BUCKETS {分桶数}
PROPERTIES (
    "replication_num" = "1",
    "compression" = "LZ4"
);
```

## 7. 分层同步配置汇总

| 层级 | 数据来源 | 同步方式 | 同步频率 | 保留策略 |
|------|----------|----------|----------|----------|
| ODS | 源系统 | FDL实时 / Kettle批量 | 实时/日级 | 7-90天 |
| DWD | ODS | 调度任务 | 日级 | 永久 |
| DWS | DWD | 调度任务 | 日级/小时级 | 1-3年 |
| ADS | DWD/DWS | 调度任务 | 小时级/实时 | 按需 |
| DIM | 源系统 | 全量覆盖 / 拉链 | 日级 | 永久 |

## 8. 分层设计速查

```
┌─────────────────────────────────────────────────────────────────┐
│                    数据仓库分层速查                               │
├─────────────────────────────────────────────────────────────────┤
│ 层级 │ 作用           │ 表模型       │ 同步方式                 │
├─────────────────────────────────────────────────────────────────┤
│ ODS  │ 原始数据保留    │ UNIQUE KEY   │ FDL实时 / Kettle批量     │
│ DWD  │ 数据清洗标准化  │ DUPLICATE    │ 调度任务                 │
│ DWS  │ 轻度汇总        │ AGGREGATE    │ 调度任务                 │
│ ADS  │ 应用指标        │ DUPLICATE    │ 调度任务 / 实时          │
│ DIM  │ 维度表          │ UNIQUE KEY   │ 全量覆盖 / 拉链         │
├─────────────────────────────────────────────────────────────────┤
│ 审计字段（必须）：etl_time, source_system, source_table           │
│ 拉链字段（维度表）：start_date, end_date, is_current              │
└─────────────────────────────────────────────────────────────────┘
```
