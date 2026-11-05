# 异常排查与诊断参考

## 1. 诊断命令速查

| 症状 | 诊断命令 | 说明 |
|------|----------|------|
| **查询超时** | `EXPLAIN {sql}` | 分析执行计划 |
| **查询超时** | `SHOW PROCESSLIST` | 查看当前连接和查询 |
| **写入失败** | `SHOW LOAD WARNINGS` | 查看导入警告 |
| **写入失败** | `SHOW LOAD ERRORS` | 查看导入错误 |
| **节点异常** | `SHOW BACKENDS` | 查看BE状态 |
| **节点异常** | `SHOW FRONTENDS` | 查看FE状态 |
| **磁盘告警** | `SHOW PROC '/statistic'` | 查看磁盘使用 |
| **Tablet异常** | `SHOW TABLET FROM {table}` | 查看Tablet状态 |

## 2. 错误码速查

| 错误码 | 错误信息 | 含义 | 解决方案 |
|--------|----------|------|----------|
| **E-1001** | Connect failed | 连接失败 | 检查FE/BE网络连通性 |
| **E-1003** | Tablet write failed | Tablet写入失败 | 检查BE磁盘空间 |
| **E-2001** | Insert timeout | 写入超时 | 增加批次大小或攒批时间 |
| **E-2035** | Stream load error | Stream Load失败 | 检查数据格式和字段映射 |
| **E-235** | Too many tablet versions | 版本数过多 | 执行COMPACT或降低写入频率 |
| **E-245** | Memory limit exceeded | 内存超限 | 减少批次大小或关闭写时合并 |
| **E-1007** | Publish timeout | 发布超时 | 检查BE状态和磁盘IO |

## 3. 性能类问题诊断

### 3.1 查询慢诊断流程

**步骤1：获取执行计划**
```sql
EXPLAIN {慢查询SQL};
EXPLAIN ANALYZE {慢查询SQL};
```

**步骤2：检查关键指标**
- 扫描类型（OlapScan / Empty Set）
- 扫描行数预估
- 是否命中分区裁剪
- 是否有排序/聚合操作

**步骤3：检查资源状态**
```sql
SHOW PROCESSLIST;
SHOW BACKENDS;
SELECT * FROM information_schema.table_cache_statistics;
```

**步骤4：定位根因并优化**

### 3.2 常见慢查询避坑

```sql
-- 避免SELECT *
SELECT order_id, customer_id, amount
FROM orders WHERE order_date = '2026-03-31';

-- 避免隐式类型转换
SELECT * FROM orders WHERE order_id = '12345';  -- 类型匹配

-- 避免函数运算在索引列上
SELECT * FROM orders
WHERE order_date >= '2026-03-31' AND order_date < '2026-04-01';

-- 合理使用LIMIT（利用TOP-N优化）
SELECT * FROM orders ORDER BY order_date DESC LIMIT 10;
```

## 4. 写入类问题诊断

### 4.1 导入失败诊断

**步骤1：获取导入错误信息**
```sql
SHOW LOAD WHERE Label = '{label}';
SHOW LOAD WARNINGS WHERE Label = '{label}';
```

**步骤2：根据错误类型处理**

| 错误类型 | 原因 | 解决方案 |
|----------|------|----------|
| 字段不匹配 | 源数据和目标表字段不一致 | 检查字段映射 |
| 数据格式错误 | 数据类型转换失败 | 清洗数据 |
| 超时 | 批次过大或网络问题 | 减小批次或增加超时 |
| 唯一键冲突 | UNIQUE KEY模型重复数据 | 检查数据或关闭写时合并 |

### 4.2 小文件问题诊断

```sql
-- 检查小文件问题
SHOW TABLET FROM your_table;

-- 查看版本数
SELECT TABLET_ID, VERSION, ROW_COUNT
FROM information_schema.partitions
WHERE TABLE_NAME = 'your_table';

-- 版本数过多（> 100），执行合并
ALTER TABLE your_table COMPACT;

-- 设置自动合并策略
ALTER TABLE your_table SET ("compaction_policy" = "time_series");
```

## 5. 资源类问题诊断

### 5.1 OOM问题诊断

```sql
-- 检查BE内存使用
SHOW BACKENDS\G

-- 检查查询内存使用
SHOW PROCESSLIST;

-- 诊断大表内存问题
-- 原因：Unique表主键索引内存占用过大
-- 解决：
-- 1. 改用DUPLICATE KEY模型
ALTER TABLE your_table SET ("storage_type" = "column");
-- 2. 使用更短的主键
-- 3. 关闭写时合并
ALTER TABLE your_table SET ("enable_unique_key_merge_on_write" = "false");
```

### 5.2 磁盘空间问题诊断

```sql
-- 检查磁盘使用
SHOW PROC '/statistic';

-- 检查各表磁盘占用
SELECT TABLE_NAME, ROUND(DATA_LENGTH / 1024 / 1024, 2) as MB
FROM information_schema.tables
WHERE TABLE_SCHEMA = '{database}'
ORDER BY DATA_LENGTH DESC;
```

## 6. 监控与运维

### 6.1 缓存命中率监控

```sql
SELECT
    TableName,
    TotalBytesRead,
    CacheHitBytes,
    CacheHitBytes / TotalBytesRead as HitRate
FROM information_schema.table_cache_statistics
WHERE TotalBytesRead > 0
ORDER BY HitRate ASC;
```

### 6.2 数据量监控

```sql
-- 查看表数据量
SHOW DATA FROM your_table;

-- 查看各分区大小
SHOW PARTITIONS FROM your_table;

-- 查看各桶数据量分布
SHOW TABLET DISTRIBUTION your_table;

-- 查看数据倾斜
ADMIN SHOW REPLICA DISTRIBUTION FROM your_table;
```

### 6.3 小文件合并

```sql
-- 查看表版本数
SHOW TABLET FROM your_table;

-- 手动触发合并
ALTER TABLE your_table COMPACT;

-- 自动合并策略
ALTER TABLE your_table SET ("compaction_policy" = "time_series");
```

## 7. 常见问题与避坑指南

### Q1: 为什么我的查询很慢？
**排查步骤**:
1. 检查表数据量是否超出预期
2. 检查是否命中分区裁剪：`EXPLAIN` + 查询SQL
3. 检查缓存命中率：`SHOW TABLET CACHE STATS your_table;`
4. 检查是否使用索引

### Q2: 小文件问题如何解决？
**解决**:
- 增加FDL/Kettle批次大小
- 定期执行 `ALTER TABLE table_name COMPACT;`
- 降低同步频率（如从1分钟改为5分钟）

### Q3: Bitmap索引空间过大怎么办？
**解决**: 若基数 > 10000，删除Bitmap索引改用布隆过滤器

### Q4: 布隆过滤器误判率高？
**解决**: `ALTER TABLE orders SET ("bloom_filter_fpp" = "0.001");`

### Q5: 存算分离下写入报错 [E-235]？
**解决**: 增加FDL任务的攒批窗口（5秒或1万条）

### Q6: MinIO连接数被打满？
**解决**: `s3_max_connections = 30`

### Q7: 数十亿级大表内存不足（OOM）？
**解决**:
```sql
-- 1. 关闭Unique表的写时合并
ALTER TABLE ods_business_flow SET ("enable_unique_key_merge_on_write" = "false");
-- 2. 改用DUPLICATE KEY模型
-- 3. 降低缓存占比
-- 4. 使用更短的主键
```

### Q8: 分桶数设置不合理如何调整？
**解决**:
```sql
-- 方式1：使用临时表重建
CREATE TABLE your_table_new LIKE your_table
DISTRIBUTED BY HASH(`key`) BUCKETS 32;
INSERT INTO your_table_new SELECT * FROM your_table;
DROP TABLE your_table;
ALTER TABLE your_table_new RENAME your_table;

-- 方式2：使用ALTER TABLE（Doris 4.0.3+）
ALTER TABLE your_table DISTRIBUTED BY HASH(`key`) BUCKETS 32;
```
