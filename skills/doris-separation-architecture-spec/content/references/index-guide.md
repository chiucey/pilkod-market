# 索引选择完整指南

## 1. 布隆过滤器索引 (Bloom Filter)

### 适用场景
- 查询无法利用前缀索引
- 查询条件为 = 或 IN
- 列基数高（如 user_id、order_id）

### 不适用场景
- 低基数列（如 gender、status）
- 范围查询（>、<、BETWEEN）
- Tinyint、Float、Double 类型

### 存算分离特殊考量
- 布隆过滤器存储在本地 Cache 中
- 建议对高频等值过滤列创建，通过 Cache 预热确保持久命中

### 创建与管理

```sql
-- 建表时指定
CREATE TABLE `orders` (
    `order_id` VARCHAR(64),
    `user_id` BIGINT
)
PROPERTIES (
    "bloom_filter_columns" = "order_id, user_id"
);

-- 已有表添加
ALTER TABLE orders SET ("bloom_filter_columns" = "order_id, user_id");

-- 调整误判率（默认 0.05）
ALTER TABLE orders SET ("bloom_filter_fpp" = "0.001");
```

## 2. 倒排索引 (Inverted Index)

### 适用场景
- 文本全文检索（LIKE '%keyword%'）
- 字符串等值/范围查询
- 日志分析

### 倒排索引 vs 布隆过滤器

| 特性 | 倒排索引 | 布隆过滤器 |
|------|----------|------------|
| 范围查询 | 支持 | 不支持 |
| 文本检索 | 支持 | 不支持 |
| 存储开销 | 较高 | 较低 |
| 适用场景 | 复杂查询 | 简单等值 |

### 创建与管理

```sql
-- 文本全文检索
ALTER TABLE articles ADD INDEX idx_content (content) USING INVERTED;

-- 非主键列等值/范围查询
ALTER TABLE orders ADD INDEX idx_customer (customer_id) USING INVERTED;

-- NGram布隆过滤器（文本模糊匹配）
ALTER TABLE amazon_reviews ADD INDEX review_body_ngram_idx(review_body)
    USING NGRAM_BF PROPERTIES("gram_size"="10", "bf_size"="10240");
```

| 参数建议 | 文本类型 | gram_size | bf_size |
|----------|----------|-----------|---------|
| 短文本 | 2~4 | 较小 |
| 长文本 | 5~10 | 较大 |

## 3. Bitmap 索引

### 原理与特点
- 每个列值映射为位图（0/1数组）
- 位图中每个bit对应一行数据
- 采用 Roaring Bitmap 实现

### 核心优势
- 空间效率高：低基数列压缩后存储极小
- 运算极快：支持 AND、OR、XOR、NOT 位运算
- 实时性：增量数据可实时更新位图

### 限制
- 仅支持等值查询（=、IN）
- 高基数列空间膨胀严重
- 支持类型：TINYINT、SMALLINT、INT、BIGINT、CHAR、VARCHAR、DATE、DATETIME、LARGEINT、DECIMAL

### 适用场景

| 场景 | 基数量级 | 推荐度 |
|------|----------|--------|
| 枚举类型（性别、状态） | 2-10 | ⭐⭐⭐⭐⭐ |
| 维度标签（地区、类目） | 10-1000 | ⭐⭐⭐⭐ |
| 多值列（标签数组） | 动态 | ⭐⭐⭐ |
| ID类字段 | 千万级 | ⭐ |

### 创建与管理

```sql
-- 建表时创建
CREATE TABLE `sales_orders` (
    `order_id` BIGINT,
    `region` VARCHAR(20),
    `status` TINYINT,
    INDEX idx_region (`region`) USING BITMAP,
    INDEX idx_status (`status`) USING BITMAP
);

-- 已有表添加
CREATE INDEX idx_region ON sales_orders (`region`) USING BITMAP;

-- 查看索引
SHOW INDEX FROM sales_orders;

-- 删除索引
DROP INDEX idx_region ON sales_orders;
```

## 4. 索引选择速查表

| 查询模式 | 前缀索引 | 布隆过滤器 | 倒排索引 | Bitmap | 推荐方案 |
|----------|----------|------------|----------|--------|----------|
| 主键点查（=） | ✅ | - | ✅ | - | 前缀索引 |
| 高基数列等值 | ❌ | ✅ 最优 | ✅ | ❌ | 布隆过滤器 |
| 低基数列等值 | ❌ | ❌ | ✅ | ✅ | Bitmap |
| 范围查询（Key列） | ✅ | ❌ | - | ❌ | 前缀索引 |
| 范围查询（非Key列） | ❌ | ❌ | ✅ | ❌ | 倒排索引 |
| 文本 LIKE | ❌ | ❌ | ✅ | ❌ | 倒排索引 |

## 5. 索引选择流程图

```
查询条件是什么？
    │
    ├── 等值过滤（=, IN）
    │   ├── 字段在Key列前36字节内 → 前缀索引（自动）
    │   └── 字段不在Key列
    │       ├── 基数高（如user_id）→ 布隆过滤器
    │       └── 基数低（如status）→ Bitmap索引
    │
    ├── 范围查询（>, <, BETWEEN）
    │   ├── 字段在Key列 → 前缀索引
    │   └── 字段不在Key列 → 倒排索引
    │
    └── 文本模糊匹配（LIKE）
        └── 倒排索引 或 NGram布隆过滤器
```

## 6. 索引使用建议

```sql
-- 查看索引列表
SHOW INDEX FROM your_table;

-- 分析查询是否使用索引
EXPLAIN SELECT COUNT(*) FROM your_table
    WHERE region = '华东' AND status = 1;

-- 查看索引存储大小
SELECT * FROM information_schema.table_indexes
    WHERE table_name = 'your_table';
```
