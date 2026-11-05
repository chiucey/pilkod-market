# 分层建表模板参考

## 1. 小表模板（< 100万条）

**适用场景**: 配置表、字典表、码表、维度表

```sql
CREATE TABLE `dim_config` (
    `config_key` VARCHAR(64) NOT NULL,
    `config_value` VARCHAR(256),
    `description` VARCHAR(500),
    `update_time` DATETIME
)
UNIQUE KEY(`config_key`)
DISTRIBUTED BY HASH(`config_key`) BUCKETS 1
PROPERTIES (
    "replication_num" = "1",
    "compression" = "LZ4"
);
```

## 2. 中表模板（100万-1000万条）

**适用场景**: 客户信息表、产品表、中小业务表

```sql
CREATE TABLE `dim_customer` (
    `customer_id` BIGINT NOT NULL,
    `customer_name` VARCHAR(100),
    `region` VARCHAR(20),
    `status` TINYINT,
    `create_time` DATETIME
)
UNIQUE KEY(`customer_id`)
DISTRIBUTED BY HASH(`customer_id`) BUCKETS 4
PROPERTIES (
    "replication_num" = "1",
    "compression" = "LZ4"
);

-- 可选：按region查询添加Bitmap索引
INDEX idx_region (`region`) USING BITMAP
```

## 3. 大表模板（1000万-1亿条）

**适用场景**: 订单表、交易流水表

```sql
CREATE TABLE `fact_orders` (
    `order_id` VARCHAR(64) NOT NULL,
    `order_date` DATE NOT NULL,
    `user_id` BIGINT,
    `amount` DECIMAL(20,2),
    `status` TINYINT,
    `region` VARCHAR(20),
    `create_time` DATETIME
)
DUPLICATE KEY(`order_date`, `order_id`)
PARTITION BY RANGE(`order_date`) ()
DISTRIBUTED BY HASH(`order_id`) BUCKETS 16
PROPERTIES (
    "replication_num" = "1",
    "compression" = "ZSTD",
    "file_cache_ttl_seconds" = "3600",
    "bloom_filter_columns" = "user_id",
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "DAY",
    "dynamic_partition.start" = "-90",
    "dynamic_partition.end" = "3"
);

INDEX idx_status (`status`) USING BITMAP,
INDEX idx_region (`region`) USING BITMAP;
```

## 4. 超大表模板（> 1亿条）

**适用场景**: 日志表、埋点表、历史归档表

```sql
CREATE TABLE `fact_logs` (
    `log_date` DATE NOT NULL,
    `log_time` DATETIME NOT NULL,
    `user_id` BIGINT,
    `action` VARCHAR(32),
    `detail` TEXT,
    `ip` VARCHAR(45)
)
DUPLICATE KEY(`log_date`, `log_time`)
PARTITION BY RANGE(`log_date`) ()
DISTRIBUTED BY HASH(`user_id`) BUCKETS 32
PROPERTIES (
    "replication_num" = "1",
    "compression" = "ZSTD",
    "file_cache_ttl_seconds" = "1800",
    "bloom_filter_columns" = "user_id",
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "DAY",
    "dynamic_partition.start" = "-30",
    "dynamic_partition.end" = "1"
);

-- 倒排索引支持全文检索
INDEX idx_detail (`detail`) USING INVERTED PROPERTIES(
    "parser" = "standard",
    "support_phrase" = "true"
);
```

## 5. ODS层实时接入大表

```sql
-- 场景：业务流水表，通过FineDataLink实时同步，年增长5亿+

CREATE TABLE `ods_business_flow` (
    `flow_id` VARCHAR(64) NOT NULL,
    `flow_time` DATETIME NOT NULL,
    `flow_date` DATE AS (DATE(flow_time)) STORED,
    `user_id` BIGINT,
    `business_type` INT,
    `raw_data` TEXT
)
UNIQUE KEY(`flow_id`)
PARTITION BY RANGE(`flow_date`) ()
DISTRIBUTED BY HASH(`flow_id`) BUCKETS 32
PROPERTIES (
    "replication_num" = "1",
    "compression" = "ZSTD",
    "enable_unique_key_merge_on_write" = "false",
    "file_cache_ttl_seconds" = "600",
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "DAY",
    "dynamic_partition.start" = "-7",
    "dynamic_partition.end" = "1"
);
```

## 6. 数据量级速查表

```
┌─────────────────────────────────────────────────────────────────┐
│                    分区分桶设计速查卡                             │
├─────────────────────────────────────────────────────────────────┤
│ 数据量级         │ 分桶  │ 分区    │ 压缩  │ 缓存策略           │
├─────────────────────────────────────────────────────────────────┤
│ 配置表(<10万)    │ 1     │ 无      │ LZ4   │ 默认               │
│ 小表(10万-100万) │ 1-2   │ 无/年   │ LZ4   │ 默认               │
│ 中表(100万-1千万)│ 2-4   │ 月      │ LZ4   │ 可选 cache_ttl     │
│ 大表(1千万-1亿)  │ 8-16  │ 日      │ ZSTD  │ 配置 cache_ttl     │
│ 超大表(>1亿)     │ 16-64 │ 日/小时 │ ZSTD  │ 必须配置 cache_ttl │
├─────────────────────────────────────────────────────────────────┤
│ 强制规则：replication_num = 1（存算分离）                        │
└─────────────────────────────────────────────────────────────────┘
```
